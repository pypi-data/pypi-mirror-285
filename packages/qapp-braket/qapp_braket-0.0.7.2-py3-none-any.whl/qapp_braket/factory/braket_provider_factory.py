"""
    QApp Platform Project braket_provider_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qapp_common.enum.provider_tag import ProviderTag
from qapp_common.enum.sdk import Sdk
from qapp_common.factory.provider_factory import ProviderFactory
from qapp_common.config.logging_config import logger

from ..model.provider.aws_braket_provider import AwsBraketProvider
from ..model.provider.oqc_cloud_provider import OqcCloudProvider
from ..model.provider.qapp_braket_provider import QappBraketProvider


class BraketProviderFactory(ProviderFactory):

    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk, authentication: dict):
        logger.info("[BraketProviderFactory] create_provider()")

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type) and Sdk.BRAKET.__eq__(sdk):
            logger.debug("[BraketProviderFactory] Create QappBraketProvider")

            return QappBraketProvider()

        if ProviderTag.AWS_BRAKET.__eq__(provider_type):
            logger.debug("[BraketProviderFactory] Create AwsBraketProvider")

            return AwsBraketProvider(
                authentication.get("accessKey"),
                authentication.get("secretKey"),
                authentication.get("regionName"),
            )

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            return OqcCloudProvider(
                authentication.get("url"),
                authentication.get("accessToken")
            )

        raise Exception("Unsupported provider!")
