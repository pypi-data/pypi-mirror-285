"""
    QuaO Project aws_braket_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import boto3
from braket.aws import AwsSession, AwsDevice

from qapp_common.enum.provider_tag import ProviderTag
from qapp_common.model.provider.provider import Provider
from qapp_common.config.logging_config import logger


class AwsBraketProvider(Provider):

    def __init__(self, aws_access_key, aws_secret_access_key, region_name):
        super().__init__(ProviderTag.AWS_BRAKET)
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

    def get_backend(self, device_specification: str):
        logger.debug('[AwsBraketProvider] get_backend()')

        session = self.collect_provider()

        return AwsDevice(
            arn=device_specification,
            aws_session=session)

    def collect_provider(self):
        logger.debug('[AwsBraketProvider] collect_provider()')

        session = boto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name)

        return AwsSession(boto_session=session)
