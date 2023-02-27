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

This repo was created with python 3.10.
The circuit is created as a qiskit circuit library component.
Tests proving the intended functionality are written with pytest.

```sh
python3.10 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -U -r requirements.txt
pytest
```
