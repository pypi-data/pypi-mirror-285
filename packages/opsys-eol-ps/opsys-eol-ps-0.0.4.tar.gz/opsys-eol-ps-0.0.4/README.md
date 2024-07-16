# eol ps Repository README

This README provides an overview of the eol ps repository, including its purpose, setup instructions, unit testing guidelines, reference links, and a usage example.

### What is this repository for? ###

- This repository is a part of the Opsys automation infrastructure.
- It serves as the control interface for an eol ps.

### How do I get set up? ###

To set up the eol ps control interface, follow these steps:

1. Install the `opsys-eol-ps` package using pip:
    ```
    pip install opsys-eol-ps
    ```

### Unit Testing ###

To run unit tests for the eol ps interface, execute the following command:
python -m unittest -v
.

### Usage Example ###

Here's an example demonstrating the usage of the eol ps control interface:

```python
from opsys_eol_ps.eol_ps import EolPs

# Initialize the ps instance with the comm num 
ps = EolPs()
cabinet.init_modbus_conn(4)

voltage = ps.get_volt()

