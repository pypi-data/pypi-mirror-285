
# Positron Networks

This package facilitates interacting with the Positron Supercompute infrastructure.

## Installation

Install the package from PyPi:

```bash
pip install positron_networks
```

## Positron CLI Usage
Generate a local auth configuration.
```
python -m positron_networks login
```
This will prompt you to open your browser, verify a code, and log in to the Positron Networks application using your username and password. Upon successful completion, a configuration file will be generated with your API key.

## Python Decorator Usage
A Python decorator to handle deploying your code into the Positron Cloud.

### Command Line Arguments

- `-l, --local`: Run the script on your local machine. Overwrites `--positron-deploy`.
- `--positron-deploy`: Deploy your script into Positron Cloud.
- `--stream-stdout`: Stream the stdout from Positron Cloud back to your CLI.
- `--debug`: Get more detailed error messages.

### Example

1. Define your function and apply the `@positron_sync` decorator with the necessary parameters:

```python
from positron-networks import positron_sync

@positron_sync(
    funding_group='your_funding_group_id',
    image_name='your_image_name',
    environment_id='your_environment_id',
    workspace_dir='your_workspace_dir',
    entry_point='your_entry_point_script'
)
def my_function():
    print("Running my function")

if __name__ == "__main__":
    my_function()
```

2. Run your script with the desired arguments:

```bash
python your_script.py --positron-deploy --stream-stdout
```

## Configuration

Ensure you have a configuration file located at `~/.positron/config.ini` with the following structure:

```ini
[DEFAULT]
UserAuthToken=your_user_auth_token
```

## Detailed Error Messages

To enable detailed error messages, run your script with the `--debug` flag:

```bash
python your_script.py --positron-deploy --debug
```

## Handling Interruptions

The script handles `SIGINT` (Ctrl+C) gracefully, allowing for proper cleanup and exit.

## License

This project is licensed under the Apache 2 License. See the [LICENSE](LICENSE) file for details.
