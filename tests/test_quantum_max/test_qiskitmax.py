import pytest

from quantum_max import QiskitMax
from qiskit import QuantumCircuit, BasicAer, transpile
from random import randrange
from typing import List


def test_num_state_qubits():
    qmax = QiskitMax(4)
    assert qmax.num_state_qubits == 4
    qmax = QiskitMax(5)
    assert qmax.num_state_qubits == 5


def test_values():
    qmax = QiskitMax(3)
    assert qmax.values == []
    with pytest.raises(AttributeError):
        qmax._check_configuration()
    assert qmax._check_configuration(raise_on_failure=False) == False
    qmax.values = [5, 8, 13]
    assert qmax._check_configuration() == True


def test_circuit_append():
    qmax1 = QiskitMax(4)
    qmax1.values.append(2)
    qmax1.values.append(-5)
    assert qmax1.num_qubits == 0
    qmax1_gate = qmax1.to_gate()
    expected_num_qubits = 11
    assert qmax1_gate.num_qubits == expected_num_qubits
    qc = QuantumCircuit(expected_num_qubits)
    assert qc.num_qubits == expected_num_qubits
    qc.append(qmax1_gate, range(qc.num_qubits))
    d1 = qc.depth()
    assert d1 > 0

    qmax2 = QiskitMax(4)
    qmax2.values = [6, 7]
    qc.append(qmax2.to_gate(), range(qc.num_qubits))
    d2 = qc.depth()
    assert d2 > d1


def test_3bit_results():
    """Tests 20 random 3-bit signed integers"""
    for _ in range(20):
        qmax = QiskitMax(3)
        qmax.values = [randrange(-4, 4), randrange(-4, 4)]
        circuit = QuantumCircuit(9, 1)
        circuit.append(qmax.to_gate(), range(circuit.num_qubits))
        circuit.measure(8, 0)
        max_a0_b1 = simulate_and_get_answer(circuit)
        assert_correct_max(max_a0_b1, qmax.values)


def test_4bit_results():
    """Tests 20 random 4-bit signed integers"""
    for _ in range(20):
        qmax = QiskitMax(4)
        qmax.values = [randrange(-8, 8), randrange(-8, 8)]
        circuit = QuantumCircuit(11, 1)
        circuit.append(qmax.to_gate(), range(circuit.num_qubits))
        circuit.measure(10, 0)
        max_a0_b1 = simulate_and_get_answer(circuit)
        assert_correct_max(max_a0_b1, qmax.values)


def test_5bit_results():
    """Tests 20 random 5-bit signed integers"""
    for _ in range(20):
        qmax = QiskitMax(5)
        qmax.values = [randrange(-16, 16), randrange(-16, 16)]
        circuit = QuantumCircuit(13, 1)
        circuit.append(qmax.to_gate(), range(circuit.num_qubits))
        circuit.measure(12, 0)
        max_a0_b1 = simulate_and_get_answer(circuit)
        assert_correct_max(max_a0_b1, qmax.values)


def simulate_and_get_answer(circuit: QuantumCircuit) -> str:
    sim = BasicAer.get_backend("statevector_simulator")
    compiled_circuit = transpile(circuit, sim)
    job = sim.run(compiled_circuit)
    result = job.result()
    counts = result.get_counts(circuit)
    return counts.popitem()[0]


def assert_correct_max(max_a0_b1: str, input_vals: List[int]) -> None:
    if max(input_vals[0], input_vals[1]) == input_vals[0]:
        assert max_a0_b1 == "0"
    else:
        assert max_a0_b1 == "1"
