"""
    QApp Platform Project circuit_convert_utils.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from braket.circuits import Circuit
from qiskit import QuantumCircuit
from qiskit.qasm2 import loads
from pytket.qasm import circuit_to_qasm_str
from pytket.extensions.braket import braket_to_tk

from qapp_common.config.logging_config import logger


class CircuitConvertUtils:

    @staticmethod
    def braket_to_qasm2_str(circuit: Circuit) -> str:
        logger.debug("[CircuitConvertUtils] braket_to_qasm2_str()")

        return circuit_to_qasm_str(braket_to_tk(circuit))

    @staticmethod
    def qasm2_str_to_qiskit(qasm_str: str) -> QuantumCircuit:
        logger.debug("[CircuitConvertUtils] qasm2_str_to_qiskit()")

        return loads(qasm_str)

    @staticmethod
    def braket_to_qiskit(circuit: Circuit) -> QuantumCircuit:
        logger.debug("[CircuitConvertUtils] braket_to_qiskit()")

        qasm_str = CircuitConvertUtils.braket_to_qasm2_str(circuit)
        return CircuitConvertUtils.qasm2_str_to_qiskit(qasm_str)
