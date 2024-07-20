# Gamewire Python SDK

A Python SDK for interacting with the Gamewire API.

## Installation

You can install the Gamewire SDK using pip:

```
pip install gamewire
```

## Usage

Here's a quick example of how to use the Gamewire SDK:

```python
from gamewire import GamewireClient

# Initialize the client
client = GamewireClient("your_email@example.com", "your_password")

# Get user balance
balance = client.get_balance()
print(f"Your balance is: {balance['balance']}")

# Create an instance
instance = client.create_instance("eu-1", "RTX 3070", "Linux", 100)
print("Instance created:", instance)

# Get instance details
instance_details = client.get_instance()
print("Instance details:", instance_details)
```

## Available Methods

The GamewireClient provides the following methods:

- `get_balance()`: Retrieve the user's balance
- `get_instance()`: Get details of the current instance
- `start_instance()`: Start an instance
- `stop_instance()`: Stop an instance
- `get_regions()`: Get available regions
- `get_region(region)`: Get details of a specific region
- `create_instance(region, instance_type, os, storage)`: Create a new instance
- `delete_instance()`: Delete the current instance

## Authentication

The SDK handles authentication automatically. Simply provide your email and password when initializing the GamewireClient:

```python
client = GamewireClient("your_email@example.com", "your_password")
```

The client will manage the authentication token for you.

## Error Handling

The SDK uses requests' built-in exception handling. If an API request fails, it will raise an HTTPError exception. You can catch and handle these exceptions in your code:

```python
from requests.exceptions import HTTPError

try:
    balance = client.get_balance()
except HTTPError as e:
    print(f"An error occurred: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```