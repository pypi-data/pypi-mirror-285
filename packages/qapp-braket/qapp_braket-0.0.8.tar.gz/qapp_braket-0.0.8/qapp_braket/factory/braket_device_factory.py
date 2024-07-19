"""
    QApp Platform Project braket_device_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from qapp_common.enum.provider_tag import ProviderTag
from qapp_common.enum.sdk import Sdk
from qapp_common.factory.device_factory import DeviceFactory
from qapp_common.model.provider.provider import Provider
from qapp_common.config.logging_config import logger

from qapp_braket.model.device.aws_braket_device import AwsBraketDevice
from qapp_braket.model.device.oqc_cloud_device import OqcCloudDevice
from qapp_braket.model.device.qapp_braket_device import QappBraketDevice


class BraketDeviceFactory(DeviceFactory):

    @staticmethod
    def create_device(provider: Provider, device_specification: str, authentication: dict, sdk: Sdk):
        logger.info("[BraketDeviceFactory] create_device()")

        provider_type = ProviderTag.resolve(provider.get_provider_type().value)

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type) and Sdk.BRAKET.__eq__(sdk):
            logger.debug("[BraketDeviceFactory] Create QappBraketDevice")

            return QappBraketDevice(provider, device_specification)

        if ProviderTag.AWS_BRAKET.__eq__(provider_type):
            logger.debug("[BraketDeviceFactory] Create QappBraketDevice")

            return AwsBraketDevice(
                provider,
                device_specification,
                authentication.get("bucketName"),
                authentication.get("prefix"),
            )

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            return OqcCloudDevice(provider, device_specification)

        raise Exception("Unsupported device!")
