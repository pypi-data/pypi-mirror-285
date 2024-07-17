import json
import time
from urllib.parse import urlparse, urlencode

from flask import Blueprint
from flask import Response, render_template, redirect, session, url_for, request
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.user_session import UserSession
from jwcrypto import jwt, jws
from markdown2 import markdown

from aup_manager.app_properties import AppProperties
from aup_manager.models import Status, Aup, Admin, Request, Acceptance


def verify_jwt(token, key):
    return jwt.JWT(jwt=token, key=key).claims


def _get_admin(connector, ext_src_name):
    sub = UserSession(session).userinfo["sub"]
    admin = session.get("admin")
    if admin:
        admin = Admin(**json.loads(admin))
    if not admin or admin.ext_login != sub:
        admin = connector.get_admin(sub, ext_src_name)
        if not admin:
            return render_template("unauthorized.html", login=sub)
        session["admin"] = admin.to_json()
    return admin


def save_acceptances_to_db(user_id, aup_ids, database):
    acceptances_list = []
    for aup_id in aup_ids:
        acceptance = Acceptance(
            aup_id,
            str(user_id),
            time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
        )
        acceptances_list.append(acceptance)
    if acceptances_list:
        database.insert_acceptances(acceptances_list)


def construct_gui_blueprint(auth: OIDCAuthentication):
    app_properties = AppProperties.get_application_properties()
    json_web_key = app_properties.json_web_key
    database = app_properties.database
    connector = app_properties.connector
    ext_src_name = app_properties.ext_source_name

    gui = Blueprint(
        "gui",
        __name__,
        template_folder="templates",
        url_prefix=app_properties.app_prefix,
        static_folder="static",
    )

    @gui.route("/accept_aups/<message>")
    def accept_aups(message):
        try:
            message = json.loads(verify_jwt(message, json_web_key))
        except jws.InvalidJWSSignature:
            return Response(json.dumps({"fail": "Invalid signature"}), 400)
        user_id = message.get("user_id")
        entity_type_id = message.get("entity_type_id")
        callback_url = message.get("callback_url")
        nonce = message.get("nonce")
        accept_aups_message = message.get(
            "accept_aups_message", app_properties.accept_aups_message
        )

        if database.get_request_by_nonce(nonce):
            return Response(json.dumps({"fail": "Replay attack."}), 403)

        if not user_id or not entity_type_id or not callback_url or not nonce:
            return Response(json.dumps({"fail": "Missing request parameter."}), 400)
        entity_type_ids = connector.get_relevant_entity_id_types(
            entity_type_id, user_id
        )
        aups = database.get_user_not_accepted_aups_by_condition(
            user_id, entity_type_ids
        )
        if len(aups) == 0:
            database.save_request(Request(nonce, user_id, status=Status.SUCCESS))
            callback_url += ("&" if urlparse(callback_url).query else "?") + urlencode(
                {"nonce": nonce}
            )
            return redirect(callback_url)
        aups_as_dict = [aup.__dict__ for aup in aups]

        session["accept_user_id"] = user_id
        session["callback_url"] = callback_url
        session["aup_ids"] = [aup["_id"] for aup in aups_as_dict]
        session["nonce"] = nonce

        database.save_request(Request(nonce, user_id))

        return render_template(
            "accept_aups.html",
            aups=aups_as_dict,
            accept_aups_message=accept_aups_message,
        )

    @gui.route("/save_acceptances")
    def save_acceptances():
        user_id = session.pop("accept_user_id", None)
        nonce = session.pop("nonce", None)
        callback_url = session.pop("callback_url", None)
        aup_ids = session.pop("aup_ids", None)
        if not user_id or not nonce or not callback_url or not aup_ids:
            return Response(json.dumps({"fail": "Missing attribute in session."}), 400)

        internal_request = database.get_request_by_nonce(nonce)
        if (
            not internal_request
            or internal_request.status != internal_request.status.FAILURE
        ):
            return Response(json.dumps({"fail": "Invalid nonce."}), 403)
        save_acceptances_to_db(user_id, aup_ids, database)
        database.make_request_success(internal_request.get_id())
        callback_url += ("&" if urlparse(callback_url).query else "?") + urlencode(
            {"nonce": nonce}
        )
        return redirect(callback_url)

    @gui.route("/get_accept_result/<message>")
    def get_accept_result(message):
        try:
            message = json.loads(verify_jwt(message, json_web_key))
        except jws.InvalidJWSSignature:
            return Response(json.dumps({"fail": "Invalid signature"}), 400)
        nonce = message.get("nonce")
        user_id = message.get("user_id")
        if not nonce or not user_id:
            return Response(json.dumps({"fail": "Missing request parameter."}), 400)
        internal_request = database.get_request_by_nonce(nonce)
        if (
            not internal_request
            or internal_request.user_id != user_id
            or internal_request.status == Status.FAILURE
        ):
            response = app_properties.responses_failure
        elif internal_request.status == Status.SUCCESS:
            database.make_request_invalid(internal_request.get_id())
            response = app_properties.responses_success
        elif internal_request.status == Status.INVALID:
            response = app_properties.responses_invalid
        else:
            response = "error"
        response_dict = {
            "result": response,
            "nonce": internal_request.nonce,
        }
        return Response(json.dumps(response_dict), 200)

    @gui.route("/")
    def admin_login():
        user_session = UserSession(session, "default")
        if user_session.is_authenticated():
            return redirect(url_for("gui.aup_overview"))
        return render_template("login.html")

    @gui.route("/logout")
    @auth.oidc_logout
    def logout():
        session.clear()
        return render_template(
            "text_message.html", text_msg="You were successfully logged out."
        )

    def gui_conditions_to_type_id(gui_conditions):
        result = []
        for outer in range(len(gui_conditions)):
            result.append([])
            for condition in gui_conditions[outer]:
                result[outer].append(condition["type_id"])
        return result

    @gui.route("/save_aup", methods=["POST"])
    @auth.oidc_auth("default")
    def save_aup():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return Response(
                json.dumps(
                    {
                        "error": "unauthorized",
                        "error_description": "you do not have rights to update this AUP",
                    }
                ),
                403,
            )
        body = request.get_json()
        aup = Aup(
            body["name"],
            body["content"],
            markdown(body["content"]),
            gui_conditions_to_type_id(body["conditions"]),
            body.get("entitlement"),
            additional_data=body.get("additional_data"),
        )
        if database.insert_aup(aup):
            return Response(
                json.dumps({"redirect_url": url_for("gui.aup_overview")}), 200
            )
        return Response(json.dumps({"status": "error occurred"}), 500)

    @gui.route("/update_aup_name", methods=["POST"])
    @auth.oidc_auth("default")
    def update_aup_name():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return Response(
                json.dumps(
                    {
                        "error": "unauthorized",
                        "error_description": "you do not have rights to update this AUP",
                    }
                ),
                403,
            )
        body = request.get_json()
        database.set_aup_name(body["_id"], body["new_name"])
        return Response(json.dumps({"status": "ok"}), 200)

    @gui.route("/update_aup_content", methods=["POST"])
    @auth.oidc_auth("default")
    def update_aup_content():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return Response(
                json.dumps(
                    {
                        "error": "unauthorized",
                        "error_description": "you do not have rights to update this AUP",
                    }
                ),
                403,
            )
        body = request.get_json()
        inserted_id = database.update_aup_text(
            body["_id"], body["content"], markdown(body["content"])
        )
        aup = database.get_aup_by_id(str(inserted_id))
        if aup:
            return Response(json.dumps(aup.to_dict()), 200)
        return Response(json.dumps({"status": "error occurred"}), 500)

    @gui.route("/update_aup_conditions", methods=["POST"])
    @auth.oidc_auth("default")
    def update_aup_conditions():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return Response(
                json.dumps(
                    {
                        "error": "unauthorized",
                        "error_description": "you do not have rights to update this AUP",
                    }
                ),
                403,
            )
        body = request.get_json()
        database.set_aup_conditions(
            body["_id"], gui_conditions_to_type_id(body["conditions"])
        )
        return Response(json.dumps({"status": "ok"}), 200)

    @gui.route("/delete_aup", methods=["POST"])
    @auth.oidc_auth("default")
    def delete_aup():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return Response(
                json.dumps(
                    {
                        "error": "unauthorized",
                        "error_description": "you do not have rights to update this AUP",
                    }
                ),
                403,
            )
        body = request.get_json()
        new_actual_aup_id = database.delete_aup_by_id(body["_id"])
        return Response(json.dumps({"new_actual_aup_id": str(new_actual_aup_id)}), 200)

    @gui.route("/aup_overview")
    @auth.oidc_auth("default")
    def aup_overview():
        aups = database.get_all_aups()
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return result
        admin = result
        return render_template("aup_overview.html", aups=aups, login=admin.ext_login)

    @gui.route("/create_aup")
    @auth.oidc_auth("default")
    def create_aup():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return result
        admin = result
        entities = connector.get_entities_for_admin(admin.get_id())
        entities_as_dict = {}
        for key, value in entities.items():
            new_value = []
            for entity in value:
                new_value.append(entity.__dict__)
            entities_as_dict[key] = new_value

        return render_template(
            "create_aup.html",
            entities=entities_as_dict,
            entity_types=list(entities.keys()),
        )

    def find_entity_in_admin_entities_dict(type_id, entities_dict):
        ent_type, ent_id = type_id.split(":", 1)
        entity_list = entities_dict.get(ent_type)
        if not entity_list:
            return None
        for entity in entity_list:
            if entity.type_id == type_id:
                return entity
        return None

    @gui.route("/manage_aups")
    @auth.oidc_auth("default")
    def manage_aups():
        result = _get_admin(connector, ext_src_name)
        if not isinstance(result, Admin):
            return result
        admin = result
        admin_entities = connector.get_entities_for_admin(admin.get_id())

        entities_as_dict = {}
        for key, value in admin_entities.items():
            new_value = []
            for entity in value:
                entity_as_dict = entity.__dict__
                entity_as_dict["type"] = entity.get_entity_type()
                new_value.append(entity_as_dict)
            entities_as_dict[key] = new_value

        aups_dict = {"enabled": [], "disabled": []}
        all_aups = database.get_all_aups()
        for aup in all_aups:
            aup_as_dict = aup.to_dict()
            enabled = True
            for outer_ind in range(len(aup.conditions)):
                if not enabled:
                    break
                for inner_ind in range(len(aup.conditions[outer_ind])):
                    entity = find_entity_in_admin_entities_dict(
                        aup.conditions[outer_ind][inner_ind], admin_entities
                    )
                    if entity:
                        entity_as_dict = entity.__dict__
                        entity_as_dict["type"] = entity.get_entity_type()
                        aup_as_dict["conditions"][outer_ind][inner_ind] = entity_as_dict
                    else:
                        enabled = False
                        aups_dict["disabled"].append(aup.to_dict())
                        break
            if enabled:
                aups_dict["enabled"].append(aup_as_dict)
        return render_template(
            "manage_aups.html",
            aups_dict=aups_dict,
            entities=entities_as_dict,
            entity_types=list(admin_entities.keys()),
        )

    return gui
