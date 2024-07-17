import base64
import json

import requests
from flask import Response
from werkzeug.exceptions import Unauthorized

from aup_manager.app_properties import AppProperties
from aup_manager.gui import save_acceptances_to_db


def token_info(token):
    properties = AppProperties.get_application_properties()

    b64_client_id_secret = base64.urlsafe_b64encode(
        f"{properties.client_id}:" f"{properties.client_secret}".encode()
    ).decode()
    response = requests.get(
        properties.introspect_url,
        params={"token": token},
        headers={"Authorization": f"Basic {b64_client_id_secret}"},
    )
    if response.status_code != 200:
        raise Unauthorized
    return response.json()


def exception_handler(error):
    return {
        "detail": str(error),
        "status": 500,
        "title": "Internal Server Error",
    }, 500


def get_user_accepted_aups(user_id, entity_type_id):
    properties = AppProperties.get_application_properties()

    entity_type_ids = properties.connector.get_relevant_entity_id_types(
        entity_type_id, user_id
    )
    aups = properties.database.get_user_accepted_aups_by_condition(
        user_id, entity_type_ids
    )
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def get_all_user_accepted_aups(user_id):
    properties = AppProperties.get_application_properties()

    aups = properties.database.get_all_user_accepted_aups(user_id)
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def get_user_not_accepted_aups(user_id, entity_type_id):
    properties = AppProperties.get_application_properties()

    entity_type_ids = properties.connector.get_relevant_entity_id_types(
        entity_type_id, user_id
    )
    aups = properties.database.get_user_not_accepted_aups_by_condition(
        user_id, entity_type_ids
    )
    return Response(json.dumps([aup.to_response_dict() for aup in aups]), 200)


def user_accepted_aups(body):
    properties = AppProperties.get_application_properties()

    save_acceptances_to_db(body["user_id"], list(body["aup_ids"]), properties.database)
    return Response("Success", 200)
