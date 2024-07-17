import importlib

import yaml
from jwcrypto import jwk

from aup_manager.db import MongodbDatabase


class AppProperties:
    __application_properties = None

    @staticmethod
    def get_application_properties():
        if AppProperties.__application_properties is None:
            AppProperties.__application_properties = AppProperties()
        return AppProperties.__application_properties

    def __init__(self):
        with open("/etc/aup-manager.yaml", "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
        self.database = MongodbDatabase(config["mongodb"])

        connector_module, _, connector_class_name = config[
            "connector_class"
        ].rpartition(".")
        connector_class = getattr(
            importlib.import_module(connector_module), connector_class_name
        )
        self.connector = connector_class(config["connectors"][connector_class_name])
        self.ext_source_name = config["connectors"][connector_class_name].get(
            "ext_source_name"
        )

        self.hostname = config["hostname"]
        self.issuer = config["OIDC"]["issuer"]
        self.introspect_url = config["OAuth2"]["introspect_url"]
        self.authorization_url = config["OAuth2"]["authorization_url"]
        self.token_url = config["OAuth2"]["token_url"]
        self.client_id = config["OAuth2"]["client_id"]
        self.client_secret = config["OAuth2"]["client_secret"]
        self.cookie_secret = config["secret"]

        key_id = config["jwks"]["key_id"]
        keystore = config["jwks"]["keystore"]
        jwk_set = jwk.JWKSet()
        with open(keystore, "r") as file:
            jwk_set.import_keyset(file.read())
        self.json_web_key = jwk_set.get_key(key_id)

        self.accept_aups_message = config.get(
            "accept_aups_message",
            "Before proceeding to service, you have to accept following acceptable use "
            "policies. These policies restrict the ways in which the service may be used "
            "and set guidelines as to how it should be used.",
        )

        self.responses_success = config["responses"]["success"]
        self.responses_failure = config["responses"]["failure"]
        self.responses_invalid = config["responses"]["invalid-request"]

        self.app_prefix = config.get("app_prefix", "")
