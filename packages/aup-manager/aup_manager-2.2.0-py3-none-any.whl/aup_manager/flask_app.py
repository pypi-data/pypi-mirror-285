from connexion import FlaskApp
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from perun.connector import Logger
from swagger_ui_bundle import swagger_ui_3_path

from aup_manager.app_properties import AppProperties
from aup_manager.gui import construct_gui_blueprint

logger = Logger.get_logger(__name__)


def exception_handler(error):
    return {
        "detail": str(error),
        "status": 500,
        "title": "Internal Server Error",
    }, 500


def get_flask_app():
    properties = AppProperties.get_application_properties()
    hostname = properties.hostname
    app_prefix = properties.app_prefix

    flask_app = FlaskApp(__name__)

    flask_app.app.config.update(
        OIDC_REDIRECT_URI=f"{hostname}{app_prefix}/oidc_callback",
        SECRET_KEY=properties.cookie_secret,
        post_logout_redirect_uris=[f"{hostname}{app_prefix}/logout", app_prefix],
    )

    client_metadata = ClientMetadata(
        client_id=properties.client_id, client_secret=properties.client_secret
    )
    provider_config = ProviderConfiguration(
        issuer=properties.issuer, client_metadata=client_metadata
    )
    auth = OIDCAuthentication({"default": provider_config}, flask_app.app)

    flask_app.app.register_blueprint(construct_gui_blueprint(auth))
    auth.init_app(flask_app.app)
    flask_app.add_api(
        "openapi-specification.yaml",
        base_path=properties.app_prefix,
        strict_validation=True,
        validate_responses=True,
        arguments={
            "authorizationUrl": properties.authorization_url,
            "tokenUrl": properties.token_url,
        },
        options={
            "swagger_ui": True,
            "swagger_path": swagger_ui_3_path,
            "swagger_ui_config": {
                "oauth2RedirectUrl": f"{hostname}{app_prefix}/ui/oauth2-redirect.html",
                "persistAuthorization": True,
            },
        },
    )
    # flask_app.add_error_handler(Exception, exception_handler)
    return flask_app


def get_app(*args):
    app = get_flask_app()
    return app(*args)


if __name__ == "__main__":
    get_flask_app().run(port=3034)
