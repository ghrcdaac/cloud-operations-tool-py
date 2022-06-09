
import re
import logging
from configparser import SectionProxy
import requests
from typing import Union
from types import ModuleType
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.backends import default_backend
from requests_toolbelt.adapters.x509 import X509Adapter


class CumulusToken:
    def __init__(self, boto3_session: ModuleType, config: Union[SectionProxy, dict]):
        """

        :param boto3_session: Boto3 session to be used
        :type boto3_session: boto3 class
        """
        self.boto3_session = boto3_session
        self.config = config

    def __get_launchpad_certificate_body_s3(self, s3_certificate_path: str) -> bytes:
        """
        :param s3_certificate_path: S3 path of launchpad certificate
        :type s3_certificate_path: string
        :return:
        :rtype:
        """
        groups = re.match(r"s3://(((?!/).)+)/(.*)", s3_certificate_path)
        if not groups:
            logging.error("S3 path should be of a format s3://<bucket_name>/path")
            raise Exception(f"{s3_certificate_path} is not of the format s3://<bucket_name>/path")
        s3 = self.boto3_session.resource('s3')
        bucket_name, certificate_path = groups[1], groups[3]
        obj = s3.Object(bucket_name=bucket_name, key=certificate_path)
        return obj.get()['Body'].read()

    @staticmethod
    def __get_launchpad_certificate_body_file_system(certificate_path: str):
        """
        :param certificate_path:
        :type certificate_path:
        :return:
        :rtype:
        """
        with open(certificate_path, "rb") as pkcs12_file:
            pkcs12_data = pkcs12_file.read()
        return pkcs12_data

    def __get_launchpad_pass_phrase_secret_manager(self, secret_manager_id):
        """
        :param secret_manager_id:
        :type secret_manager_id:
        :return:
        :rtype:
        """
        client = self.boto3_session.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_manager_id)
        return response['SecretString']

    def __get_token_launchpad(self):
        """
        Get token using launchpad authentication
        return: cumulus token
        """
        error_str = "Getting the token (Launchpad)"
        config = self.config
        try:
            backend = default_backend()
            pkcs12_data = ""
            pkcs12_password_bytes = b""
            if config.get("FS_LAUNCHPAD_CERT"):
                pkcs12_data = self.__get_launchpad_certificate_body_file_system(config.get("FS_LAUNCHPAD_CERT"))
            if config.get("S3URI_LAUNCHPAD_CERT"):
                pkcs12_data = self.__get_launchpad_certificate_body_s3(config.get("S3URI_LAUNCHPAD_CERT"))
            pass_phrase_secret_manager_id = config.get("LAUNCHPAD_PASSPHRASE_SECRET_NAME")
            if pass_phrase_secret_manager_id:
                pkcs12_password_bytes = self.__get_launchpad_pass_phrase_secret_manager(
                    pass_phrase_secret_manager_id).encode()
            elif config.get("LAUNCHPAD_PASSPHRASE"):
                pkcs12_password_bytes = config.get("LAUNCHPAD_PASSPHRASE").encode()

            pycaP12 = load_key_and_certificates(
                pkcs12_data, pkcs12_password_bytes, backend
            )

            cert_bytes = pycaP12[1].public_bytes(Encoding.DER)
            pk_bytes = pycaP12[0].private_bytes(
                Encoding.DER, PrivateFormat.PKCS8, NoEncryption()
            )

            adapter = X509Adapter(
                max_retries=3,
                cert_bytes=cert_bytes,
                pk_bytes=pk_bytes,
                encoding=Encoding.DER,
            )
            session = requests.Session()
            session.mount("https://", adapter)

            r = session.get(config.get("LAUNCHPAD_URL"))
            response = r.json()
            token = response["sm_token"]
            return token
        except Exception as ex:
            error_str = f"{error_str} {str(ex)}"
            logging.error(error_str)
            raise Exception(error_str)

    def get_token(self):
        """
        Get Earth Data Token
        :return: Token otherwise raise exception
        """
        return self.__get_token_launchpad()


