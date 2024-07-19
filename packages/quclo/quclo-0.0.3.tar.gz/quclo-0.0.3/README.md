# QuClo CLI

QuClo CLI is a command-line interface tool designed to simplify the execution and management of quantum circuits across multiple backend providers. This tool leverages the QuClo platform to offer a seamless experience for researchers, educators, and hobbyists in quantum computing.

## Features

- **Execute Quantum Circuits:** Run your quantum circuits on various backend providers.
- **Intelligent Backend Selection:** Choose the best backend based on criteria like cost, speed, fidelity, and queue time.
- **Result Visualization:** Generate comprehensive and easy-to-understand visualizations of your quantum circuit results.
- **Open-Source SDK Integration:** Easily integrate and submit circuits created with other SDKs.

## Installation

To install the QuClo CLI, ensure you have Python installed, then use pip:

```bash
pip install quclo
```

## Usage

CLI:

```bash
quclo --help
```

UI:

```bash
pip install pdoc
pdoc quclo --logo https://quclo.com/assets/quclo-Cg4oDc2h.svg
```

1. Create a new user account:

   ```bash
   quclo create user --email <email> --password <password>
   ```

2. Authenticate with your user account:

   ```bash
   quclo create apikey --email <email> --password <password>
   ```

3. List available backends:

   ```bash
   quclo list backends
   ```

4. Display details of a specific backend:

   ```bash
   quclo get backend ibm.condor
   ```

5. Execute a quantum circuit:

   **Using priority:**

   ```bash
   quclo create circuit --file <file> --priority <priority>
   ```

6. Get the status or results of a quantum circuit:

   ```bash
   quclo get circuit <circuit_id>
   ```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## Contact

For any questions or feedback, please contact us at [support@quclo.com](mailto:support@quclo.com).
