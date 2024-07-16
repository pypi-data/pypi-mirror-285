import argparse
import json
import os
import boto3
from typing import Optional
from sws_api_client.auth import AuthClientCredentials
from sws_api_client.discover import Discover
from sws_api_client.token import Token
import logging

logger = logging.getLogger(__name__)

DEFAULT_CREDENTIALS_SECRET_NAME = "SWS_USER_CREDENTIALS_SECRET_NAME"

class SwsApiClient:

    def __init__(self,
                 sws_endpoint: str,
                 sws_token: str,
                 authclient: AuthClientCredentials,
                 current_task_id:Optional[str],
                 current_execution_id:Optional[str]
        ) -> None:
        
        logger.info("Initializing SwsApiClient")

        self.sws_endpoint = sws_endpoint
        self.sws_token = sws_token
        self.authclient = authclient
        self.current_task_id = current_task_id
        self.current_execution_id = current_execution_id
        self.token = Token(authclient)
        self.is_debug = self.check_debug()
        self.discoverable = Discover(sws_endpoint=sws_endpoint, sws_token=sws_token, token=self.token)
        logger.debug(f"SwsApiClient initialized with endpoint {sws_endpoint} and token {sws_token}")

    @classmethod
    def __get_authclient_credentials_from_secret(cls, env_name="SWS_USER_CREDENTIALS_SECRET_NAME") -> AuthClientCredentials:
        logger.debug(f"Fetching auth client credentials from secret: {env_name}")
        secret_name = os.getenv(env_name)
        if not secret_name:
            raise ValueError(f"Secret name not found in environment variable: {env_name}")
        cls.session = getattr(cls, 'session', boto3.Session())
        cls.secret_manager = getattr(cls, 'secret_manager', cls.session.client('secretsmanager'))
        response = cls.secret_manager.get_secret_value(SecretId=secret_name)
        secretContent = json.loads(response['SecretString'])
        logger.debug(f"Secret fetched successfully: {secretContent}")
        return AuthClientCredentials(
            clientId=secretContent["ID"],
            clientSecret=secretContent["SECRET"],
            scope=secretContent["SCOPE"],
            tokenEndpoint=secretContent["TOKEN_ENDPOINT"]
        )

    @classmethod
    def from_env(cls, sws_endpoint_env="SWS_ENDPOINT", authclient_secret_name=DEFAULT_CREDENTIALS_SECRET_NAME):
        logger.debug(f"Creating SwsApiClient from environment variables: {sws_endpoint_env}, {authclient_secret_name}")
        authclient:AuthClientCredentials = cls.__get_authclient_credentials_from_secret( env_name=authclient_secret_name)
        
        sws_token = os.getenv("SWS_TOKEN")
        if not sws_token:
            raise ValueError("SWS_TOKEN environment variable must be set")
        
        sws_endpoint = os.getenv(sws_endpoint_env)
        if not sws_endpoint:
            raise ValueError(f"{sws_endpoint_env} environment variable must be set")
        

        return cls(
            sws_token=os.getenv("SWS_TOKEN"),
            sws_endpoint=os.getenv(sws_endpoint_env),
            current_task_id=os.getenv("TASK_ID"),
            current_execution_id=os.getenv("EXECUTION_ID"),
            authclient=authclient
        )

    @classmethod
    def from_conf(cls, conf_file="conf_sws_api_client.json"):
        logger.debug(f"Creating SwsApiClient from config file: {conf_file}")
        with open(conf_file) as f:
            kwargs = json.load(f)
            logger.debug(f"Config loaded: {kwargs}")
            return cls(
                sws_endpoint=kwargs["sws_endpoint"],
                sws_token=kwargs["sws_token"],
                current_task_id=kwargs.get("current_task_id"),
                current_execution_id=kwargs.get("current_execution_id"),
                authclient=AuthClientCredentials(**kwargs["authclient"])
            )

    @classmethod
    def from_args(cls):
        logger.debug("Creating SwsApiClient from command line arguments")
        parser = argparse.ArgumentParser(description="Instantiate SwsApiClient from args")
        parser.add_argument("--sws_endpoint", type=str, required=True, help="The sws endpoint")
        parser.add_argument("--sws_token", type=str, required=True, help="The SWS access token")
        parser.add_argument("--authclient_id", type=str, required=True, help="The authclient ID")
        parser.add_argument("--authclient_secret", type=str, required=True, help="The authclient secret")
        parser.add_argument("--authclient_scope", type=str, required=True, help="The authclient scope")
        parser.add_argument("--authclient_endpoint", type=str, required=True, help="The authclient endpoint URI")
        parser.add_argument("--current_task_id", type=str, required=False, help="The current task ID")
        parser.add_argument("--current_execution_id", type=str, required=False, help="The current execution ID")
        args, _ = parser.parse_known_args()
        props = vars(args)
        logger.debug(f"Arguments parsed: {props}")
        return cls(
            sws_endpoint=props.get("sws_endpoint"),
            current_task_id=props.get("current_task_id"),
            current_execution_id=props.get("current_execution_id"),
            authclient={
                "client_id": props.get("authclient_id"),
                "client_secret": props.get("authclient_secret"),
                "scope": props.get("authclient_scope"),
                "endpoint": props.get("authclient_endpoint")
            }
        )
    
    @classmethod
    def check_debug(cls):
        debug = os.getenv("DEBUG_MODE") == "TRUE" or os.getenv("DEBUG_MODE") is None
        logger.debug(f"Debug mode is {'on' if debug else 'off'}")
        return debug
    
    @classmethod
    def auto(cls):
        debug = cls.check_debug()
        logger.debug(f"Auto-detecting client creation method, debug mode: {debug}")
        if debug:
            return cls.from_conf()
        else:
            return cls.from_env()
