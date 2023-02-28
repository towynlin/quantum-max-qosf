"""Implements a quantum integer maximum function on qiskit."""

from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.circuit import Operation
from qiskit.circuit.library import BlueprintCircuit, CDKMRippleCarryAdder
from qiskit.circuit.library.arithmetic.adders.adder import Adder
from typing import List, Optional


class QiskitMax(BlueprintCircuit, Operation):
    """Uses a quantum circuit to calculate the maximum of a list of signed integers.

    Example usage:

        Create a QiskitMax circuit, specifying the integer precision.

            `qmax = QiskitMax(4)`

        Set the two values to compare.

            `qmax.values = [5, -6]`

        Create a circuit with at least 2**num_state_qubits + 3 qubits.

            `circuit = QuantumCircuit(11, 1)`

        Turn the resulting circuit into a gate.

            `qmax_gate = qmax.to_gate()`

        Append the gate the the circuit.

            `circuit.append(qmax_gate, range(circuit.num_qubits))`

        Measure the last qubit of the gate.
        If the result is 0, then the first value is greater.
        If the result is 1, then the second value is greater.

            `circuit.measure(10, 0)`

        This example should give 0, since 5 > -6.
    """

    def __init__(
        self, num_state_qubits: int, adder: Optional[Adder] = None, name: str = "max"
    ) -> None:
        """Creates a new qiskit circuit to calculate the maximum of a list of integers.

        The number of qubits needed for this circuit is 2 * num_state_qubits + 3 ancillas.

        Args:
            num_state_qubits: The number of qubits in one input register.
                The two input registers must have the same number of qubits.
            adder: Untested. Substitute a different adder than the default,
                which is a ``CDKMRippleCarryAdder`` in half-adder mode.
            name: The name of the circuit object.
        """
        super().__init__(name=name)
        self._num_state_qubits = num_state_qubits
        self._values = []
        self.name = name
        if adder == None:
            self._adder = CDKMRippleCarryAdder(num_state_qubits, "half")
        else:
            self._adder = adder

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def num_state_qubits(self) -> int:
        return self._num_state_qubits

    @property
    def values(self) -> List[int]:
        return self._values

    @values.setter
    def values(self, vals: List[int]):
        self._values = vals

    def _check_configuration(self, raise_on_failure: bool = True) -> bool:
        """Check if the current configuration allows the circuit to be built.
        Args:
            raise_on_failure: If True, raise if the configuration is invalid. If False, return
                False if the configuration is invalid.
        Returns:
            True, if the configuration is valid. Otherwise, depending on the value of
            ``raise_on_failure`` an error is raised or False is returned.
        """
        valid = True

        if len(self._values) < 2:
            valid = False
            if raise_on_failure:
                raise AttributeError("Not enough values have been set for comparison.")

        return valid

    def _encode(
        self, value: int, register: QuantumRegister, circuit: QuantumCircuit
    ) -> None:
        """Encode the given signed integer value into the given QuantumRegister
        and QuantumCircuit with X gates for each bit with value 1."""
        v = value
        if v < 0:
            v += 2**self.num_state_qubits
        for idx, bit in enumerate(reversed("{0:b}".format(v))):
            if bit == "1":
                circuit.x(register[idx])

    def _build(self, should_draw: bool = False) -> None:
        """If not already built, build the circuit."""
        if self._is_built:
            return

        self._check_configuration()

        qr_a = QuantumRegister(self.num_state_qubits)
        qr_b = QuantumRegister(self.num_state_qubits)
        anc = AncillaRegister(3)
        circuit = QuantumCircuit(qr_a, qr_b, anc)

        # Encode the input values using X gates
        self._encode(self.values[0], qr_a, circuit)
        self._encode(self.values[1], qr_b, circuit)

        # TODO: Add more than the first 2 values

        # Save the sign of register B in the third ancilla qubit before we modify B
        circuit.cx(qr_b[-1], anc[2])

        # The adder becomes a subtractor when we bit-flip the first operand before adding,
        # and then bit-flip both the sum and the first operand after adding.
        # The carry qubit gives info about which operand is greater.
        circuit.x(qr_a)
        adder_gate = self._adder.to_gate()
        circuit.append(adder_gate, range(adder_gate.num_qubits))
        circuit.x(qr_a)
        circuit.x(qr_b)
        self.add_register(qr_a, qr_b, anc)

        # Calculate the parity of carry and sign a and sign b in anc[2]
        circuit.cx(qr_a[-1], anc[2])
        circuit.cx(anc[0], anc[2])
        # After this, measuring anc[2] will give 0 if a is the max, or 1 if b is the max

        if should_draw:
            print(circuit.draw("text"))

        # Calling `self.append` triggers a call to `_build`, so
        # we set `_is_built` to `True` first, to prevent stack overflow.
        self._is_built = True
        self.append(circuit.to_gate(), self.qubits)
