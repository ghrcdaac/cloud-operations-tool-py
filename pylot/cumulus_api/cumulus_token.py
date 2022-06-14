
import re
import logging
from configparser import SectionProxy
from typing import Union, Dict
from .aws_services import AWS_Services
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.backends import default_backend
import requests
from requests_toolbelt.adapters.x509 import X509Adapter


class CumulusToken:
    def __init__(self, config: Union[SectionProxy, dict]):
        """

        :param config: PyLOT Configuration

        """
        self.config = config
        aws_profile: Union[str, None] = self.config.get('AWS_PROFILE')
        aws_region: str = self.config.get('AWS_REGION', 'us-west-2')
        aws_services = AWS_Services(aws_profile=aws_profile, aws_region=aws_region)
        self.s3_resource = aws_services.get_s3_resource()
        self.secretmanager_client = aws_services.get_secretmanager_client()

    def get_s3_object_body(self, bucket_name, prefix):
        """

        :return:
        :rtype:
        """
        obj = self.s3_resource.Object(bucket_name=bucket_name, key=prefix)
        return obj.get()['Body'].read()


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
        bucket_name, certificate_path = groups[1], groups[3]

        return self.get_s3_object_body(bucket_name=bucket_name, prefix=certificate_path)



    @staticmethod
    def __get_launchpad_certificate_body_file_system(certificate_path: str) -> bytes:
        """
        :param certificate_path:
        :type certificate_path:
        :return:
        :rtype:
        """
        with open(certificate_path, "rb") as pkcs12_file:
            pkcs12_data = pkcs12_file.read()
        return pkcs12_data

    def __get_launchpad_pass_phrase_secret_manager(self, secret_manager_id: str):
        """
        :param secret_manager_id:
        :type secret_manager_id:
        :return:
        :rtype:
        """
        response = self.secretmanager_client.get_secret_value(SecretId=secret_manager_id)
        return response['SecretString']

    def __get_launchpad_certificate_body(self, config: Dict[str, str]) -> bytes:
        """

        :param config:
        :type config:
        :return:
        :rtype:
        """
        pkcs12_data: bytes = b""
        if config.get("FS_LAUNCHPAD_CERT"):
            pkcs12_data = self.__get_launchpad_certificate_body_file_system(config["FS_LAUNCHPAD_CERT"])
        if config.get("S3URI_LAUNCHPAD_CERT"):
            pkcs12_data = self.__get_launchpad_certificate_body_s3(config["S3URI_LAUNCHPAD_CERT"])
        return pkcs12_data

    def __get_launchpad_secret_phrase(self, config: dict) -> bytes:
        """

        :param config:
        :type config:
        :return:
        :rtype:
        """
        pass_phrase_secret_manager_id = config.get("LAUNCHPAD_PASSPHRASE_SECRET_NAME")
        if pass_phrase_secret_manager_id:
            pkcs12_password_bytes = self.__get_launchpad_pass_phrase_secret_manager(
                pass_phrase_secret_manager_id).encode()
            return pkcs12_password_bytes
        return config.get("LAUNCHPAD_PASSPHRASE", "").encode()

    def __get_launchpad_adapter(self):
        """
        Get launchpad adopter
        return: cumulus token
        """
        error_str = "Getting launchpad adapter"
        try:
            backend = default_backend()
            pkcs12_data = self.__get_launchpad_certificate_body(self.config)
            pkcs12_password_bytes = self.__get_launchpad_secret_phrase(self.config)
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
            return adapter
        except Exception as ex:
            error_str = f"{error_str} {str(ex)}"
            logging.error(error_str)
            raise Exception(error_str)

    def get_token(self):
        """
        Get token using launchpad authentication
        :return: Token otherwise raise exception
        """
        error_str = "Getting launchpad token"
        try:
            adapter = self.__get_launchpad_adapter()
            session = requests.Session()
            session.mount("https://", adapter)
            r = session.get(self.config.get("LAUNCHPAD_URL"))
            response = r.json()
            return response["sm_token"]
        except Exception as exp:
            error_str = f"{error_str} {str(exp)}"
            logging.error(error_str)
            raise Exception(error_str)
