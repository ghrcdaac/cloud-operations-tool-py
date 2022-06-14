import unittest
from os import path
from pylot.cumulus_api.cumulus_token import CumulusToken
from moto import mock_s3, mock_secretsmanager
import boto3
import pytest


class TestCumulusToken(unittest.TestCase):
    bucket_name = "test_bucket"
    certificate_s3_key = "temp/certificate.pfx"
    expected_body = "NoThingToS33HereExceptS@meRandoMText\n"
    certificate_path = path.join(path.dirname(__file__), "fixtures/certificate.pfx")
    secret_name = "fake_secretmanager"
    secret_string = "supersecretstring"

    def setUp(self) -> None:
        self.cml_token = CumulusToken(config={})

    @pytest.fixture
    def s3_resource(self):
        """Pytest fixture that creates the recipes bucket in
        the fake moto AWS account

        Yields a fake boto3 s3 resource
        """

        with mock_s3():
            mocked_s3_resource = boto3.resource("s3")
            mocked_s3_resource.create_bucket(Bucket=self.bucket_name)
            s3_client = boto3.client('s3')
            s3_client.upload_file(self.certificate_path, self.bucket_name, self.certificate_s3_key)
            yield mocked_s3_resource

    @pytest.fixture
    def secretmanager_client(self):
        """Pytest fixture that creates a secretmanager to a
        the fake moto AWS account

        Yields a fake secret manager client
        """
        with mock_secretsmanager():

            mocked_secretmanger_client = boto3.client('secretsmanager', region_name="us-west-2")
            mocked_secretmanger_client.create_secret(
                Name=self.secret_name,
                SecretString=self.secret_string
            )
            yield mocked_secretmanger_client

    def test__get_launchpad_certificate_body_raise(self):
        s3_certificate_path = "/fake/path/launchpad.pfx"

        with self.assertRaises(Exception) as context:
            self.cml_token._CumulusToken__get_launchpad_certificate_body_s3(s3_certificate_path=s3_certificate_path)
        self.assertEqual(f'{s3_certificate_path} is not of the format s3://<bucket_name>/path', str(context.exception))

    # Either we can use this or we can define @pytest.fixture(autouse=True) to be used automatically
    @pytest.mark.usefixtures("s3_resource")
    def test__get_launchpad_certificate_body_s3(self):
        s3_certificate_path = f"s3://{self.bucket_name}/{self.certificate_s3_key}"
        body = self.cml_token._CumulusToken__get_launchpad_certificate_body_s3(s3_certificate_path=s3_certificate_path)
        self.assertEqual(body, self.expected_body.encode("utf-8"))

    def test__get_launchpad_certificate_body_file_system(self):
        body = self.cml_token._CumulusToken__get_launchpad_certificate_body_file_system(certificate_path=
                                                                                        self.certificate_path)
        self.assertEqual(body, self.expected_body.encode("utf-8"))

    @pytest.mark.usefixtures("secretmanager_client")
    def test__get_launchpad_pass_phrase_secret_manager(self):
        secret = self.cml_token._CumulusToken__get_launchpad_pass_phrase_secret_manager(secret_manager_id=
                                                                                        "fake_secretmanager")
        self.assertEqual("supersecretstring", secret)
