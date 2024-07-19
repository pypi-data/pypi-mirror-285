"""
    QApp Platform Project braket_invocation.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from braket.circuits import Circuit

from qapp_common.component.backend.invocation import Invocation
from qapp_common.data.async_task.circuit_export.backend_holder import BackendDataHolder
from qapp_common.data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from qapp_common.data.request.invocation_request import InvocationRequest
from qapp_common.model.provider.provider import Provider
from qapp_common.config.logging_config import logger
from qapp_common.config.thread_config import circuit_exporting_pool

from ...factory.braket_provider_factory import BraketProviderFactory
from ...factory.braket_device_factory import BraketDeviceFactory
from ...async_tasks.braket_circuit_export_task import BraketCircuitExportTask


class BraketInvocation(Invocation):

    def __init__(self, request_data: InvocationRequest):
        super().__init__(request_data)

    def _export_circuit(self, circuit):
        logger.info("[BraketInvocation] _export_circuit()")

        circuit_export_task = BraketCircuitExportTask(
            circuit_data_holder=CircuitDataHolder(circuit, self.circuit_export_url),
            backend_data_holder=BackendDataHolder(
                self.backend_information, self.authentication.user_token
            ),
        )

        circuit_exporting_pool.submit(circuit_export_task.do)

    def _create_provider(self):
        logger.info("[BraketInvocation] _create_provider()")

        return BraketProviderFactory.create_provider(
            provider_type=self.backend_information.provider_tag,
            sdk=self.sdk,
            authentication=self.backend_information.authentication,
        )

    def _create_device(self, provider: Provider):
        logger.info("[BraketInvocation] _create_device()")

        return BraketDeviceFactory.create_device(
            provider=provider,
            device_specification=self.backend_information.device_name,
            authentication=self.backend_information.authentication,
            sdk=self.sdk,
        )

    def _get_qubit_amount(self, circuit):
        logger.info("[BraketInvocation] _get_qubit_amount()")

        if isinstance(circuit, Circuit):
            return circuit.qubit_count

        raise Exception("Invalid circuit type!")
