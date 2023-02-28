"""Just in case anyone feels pedantic about the
specific phrasing of the screening task,
here's a solution phrased almost exactly as given."""

from qiskit import BasicAer, QuantumCircuit, transpile
from quantum_max import QiskitMax


def find_the_largest_number(number_1: int, number_2: int) -> int:
    """
    number_1: Integer value that is the first parameter to the function.
    number_2: Integer value that is the second parameter to the function.
    """
    circuit = build_the_circuit(number_1, number_2)
    result = simulate_and_get_result(circuit)
    if result == "0":
        return number_1
    else:
        return number_2


def build_the_circuit(number_1: int, number_2: int) -> QuantumCircuit:
    qmax = QiskitMax(4)
    qmax.values = [number_1, number_2]
    circuit = QuantumCircuit(11, 1)
    circuit.append(qmax.to_gate(), range(circuit.num_qubits))
    circuit.measure(10, 0)
    return circuit


def simulate_and_get_result(circuit: QuantumCircuit) -> str:
    sim = BasicAer.get_backend("statevector_simulator")
    compiled_circuit = transpile(circuit, sim)
    job = sim.run(compiled_circuit)
    result = job.result()
    counts = result.get_counts(circuit)
    return counts.popitem()[0]


if __name__ == "__main__":
    print(f"Finding the largest number among the choices 5 and -6...")
    largest = find_the_largest_number(5, -6)
    print(f"The answer is: {largest}")

    # Draw the circuit.
    # See the paper or the qiskit docs for the internals of the adder.
    # https://qiskit.org/documentation/stubs/qiskit.circuit.library.CDKMRippleCarryAdder.html
    # It's a cascade of "majority" gates followed by a reverse cascade of
    # "unmajority and add" gates. Those in turn are constructed mostly
    # from CNOT and Toffoli gates.
    qmax = QiskitMax(4)
    qmax.values = [5, -6]
    qmax._build(should_draw=True)
