"""
    QuaO Project qapp_braket_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from braket.devices import LocalSimulator

from qapp_common.config.logging_config import logger
from qapp_common.enum.provider_tag import ProviderTag
from qapp_common.model.provider.provider import Provider


class QappBraketProvider(Provider):

    def __init__(self, ):
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('[QappBraketProvider] get_backend()')

        provider = self.collect_provider()

        device_names = provider.registered_backends()

        if device_names.__contains__(device_specification):
            return LocalSimulator(device_specification)

        raise Exception('Unsupported device')

    def collect_provider(self):
        logger.debug('[QappBraketProvider] collect_provider()')

        return LocalSimulator()
