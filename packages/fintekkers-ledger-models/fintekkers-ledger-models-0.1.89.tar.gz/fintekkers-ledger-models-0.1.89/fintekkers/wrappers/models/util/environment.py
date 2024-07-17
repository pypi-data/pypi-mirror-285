import grpc
from typing import Dict
from pathlib import Path

SERVICE_MAP: Dict[str, str] = {
    "SecurityService": "34.205.69.2",
    "LedgerService": "34.205.69.2",
    "TransactionService": "34.205.69.2",
    "PortfolioService": "34.205.69.2",
    "ValuationService": "54.165.101.211"
}

PORT_MAP: Dict[str, str] = {
    "SecurityService": "8082",
    "LedgerService": "8082",
    "TransactionService": "8082",
    "PortfolioService": "8082",
    "ValuationService": "8080"
}

LEDGER_SERVICE = "LedgerService"
VALUATION_SERVICE = "ValuationService"
SECURITY_SERVICE = "SecurityService"
TRANSACTION_SERVICE = "TransactionService"
PORTFOLIO_SERVICE = "PortfolioService"

class Environment(object):
    IS_RUNNING_LOCALLY = True

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Environment, cls).__new__(cls)
        return cls.instance

    def __get_base_url(self, service: str) -> str:
        if Environment().IS_RUNNING_LOCALLY:
            return "host.docker.internal" if Path("/.dockerenv").exists() else "127.0.0.1"

        if service in SERVICE_MAP:
            return SERVICE_MAP[service]
        else:
            raise ValueError("Could not get location of service")

    def get_endpoint(self, service: str) -> str:
        # base_url = "http://" + __get_base_url(service)
        base_url = self.__get_base_url(service)

        port = PORT_MAP.get(service, None)
        if port is None:
            raise ValueError("Could not get port")

        return base_url + ":" + port

    def get_service_insecure_channel(self, service_name:str) -> grpc.Channel:
        '''
            Creates a HTTP channel for sending/receiving GRPC requests

                Parameters:
                        The name of the services. Note, these are currently defined in language by language
                        implementations and are manually kept in sync.

                Returns:
                        channel (grpc.Channel): Returns an insecure/HTTP channel for GRPC comms. 
        '''
        return grpc.insecure_channel(self.get_endpoint(service_name))
    

    def get_service_secure_channel(self, service_name:str) -> grpc.Channel:
        '''
            Creates a HTTPS channel for sending/receiving GRPC requests, using default locations to search for
            private keys

                Parameters:
                        The name of the services. Note, these are currently defined in language by language
                        implementations and are manually kept in sync.

                Returns:
                        channel (grpc.Channel): Returns a one-way secure/HTTPS channel for GRPC comms. Two way SSL 
                        not currently implemented.
        '''
        return grpc.secure_channel(self.get_endpoint(service_name), grpc.ssl_channel_credentials())