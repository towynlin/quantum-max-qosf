# Quantum Integer Max

In February 2023, I applied to the
[QOSF mentorship program](https://www.qosf.org/qc_mentorship/).
Applicants are given a screening task, and I chose to
"find the largest of two signed integers".

One way to accomplish this is mentioned near the end of
["A new quantum ripple-carry addition circuit" by
Cuccaro, Draper, Kutin, and Moulton](https://arxiv.org/abs/quant-ph/0410184).

They describe an adder circuit, and then mention that it
"can easily be turned into a subtractor...
by adding two time slices: complement _a_ at the start,
and complement _a_ and _s_ at the end."

They say that the carry bit of the resulting subtractor "is 1 if and only if a < b."
I found in developing this that their definition of "less than" requires
viewing the encoded bit strings as *unsigned* integers, so that, for example,
when using 4-bit registers, the carry bit will be 1 when `a = 1` and `b = -1`.
That's because -1 is encoded to 4 bits as 1111, which may also be read as 15.

Thus, I had to determine the maximum using the parity of 3 values:
- the carry bit
- the MSB (sign bit) of _a_
- the MSB (sign bit) of _b_

Even parity means that _a_ is the greater signed value,
whereas odd parity means that _b_ is the greater signed value.

## Usage

This repo was developed and tested with python 3.10.10,
qiskit 0.41.1, qiskit-terra 0.23.2, and qiskit-aer 0.11.2.
The circuit is created as a qiskit circuit library component.
Code is formatted by black.

Tests proving the intended functionality are written with pytest,
including tests of randomly generated input values from 3-bit and
4-bit precision, all the way up to 10-bit precision.

As long as one has a quantum computer or simulator with enough qubits,
this solution will work for any size integer. See the test
[`test_any_precision`](https://github.com/towynlin/quantum-max-qosf/blob/7835f97904dd9f42692bd5299fc11902faf4ee45/tests/test_quantum_max/test_qiskitmax.py#L114-L130)
for an example showing the constraints.

The `statevector_simulator` allows up to 24 qubits, so 10-bit integers
are the largest ones we can compare without a bigger quantum computer.
Running all the tests takes about 105 seconds on my laptop;
most of that time is taken by the one and only 10-bit circuit execution.

```sh
python3.10 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -U -r requirements.txt
pytest -s
python example.py
```

Running example.py will print the following:

```
Finding the largest number among the choices 5 and -6...
The answer is: 5
      ┌───┐┌───┐┌───────────────────────┐┌───┐          
q6_0: ┤ X ├┤ X ├┤0                      ├┤ X ├──────────
      ├───┤└───┘│                       │├───┤          
q6_1: ┤ X ├─────┤1                      ├┤ X ├──────────
      ├───┤┌───┐│                       │├───┤          
q6_2: ┤ X ├┤ X ├┤2                      ├┤ X ├──────────
      ├───┤└───┘│                       │├───┤          
q6_3: ┤ X ├─────┤3                      ├┤ X ├──■───────
      └───┘     │                       │├───┤  │       
q7_0: ──────────┤4                      ├┤ X ├──┼───────
      ┌───┐     │  CDKMRippleCarryAdder │├───┤  │       
q7_1: ┤ X ├─────┤5                      ├┤ X ├──┼───────
      └───┘     │                       │├───┤  │       
q7_2: ──────────┤6                      ├┤ X ├──┼───────
      ┌───┐     │                       │├───┤  │       
q7_3: ┤ X ├──■──┤7                      ├┤ X ├──┼───────
      └───┘  │  │                       │└───┘  │       
a1_0: ───────┼──┤8                      ├───────┼────■──
             │  │                       │       │    │  
a1_1: ───────┼──┤9                      ├───────┼────┼──
           ┌─┴─┐└───────────────────────┘     ┌─┴─┐┌─┴─┐
a1_2: ─────┤ X ├──────────────────────────────┤ X ├┤ X ├
           └───┘                              └───┘└───┘
```
