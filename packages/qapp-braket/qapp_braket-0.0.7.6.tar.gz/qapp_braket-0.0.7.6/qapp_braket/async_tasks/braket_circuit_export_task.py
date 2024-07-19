"""
    QApp Platform Project braket_circuit_export_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from braket.circuits import Circuit

from qapp_common.async_tasks.export_circuit_task import CircuitExportTask
from qapp_common.config.logging_config import logger

from qapp_braket.util.circuit_convert_utils import CircuitConvertUtils


class BraketCircuitExportTask(CircuitExportTask):

    def _transpile_circuit(self):
        logger.debug("[BraketCircuitExportTask] _transpile_circuit()")

        circuit = self.circuit_data_holder.circuit

        if isinstance(circuit, Circuit):
            return CircuitConvertUtils.braket_to_qiskit(circuit)

        raise Exception("Invalid circuit type!")
