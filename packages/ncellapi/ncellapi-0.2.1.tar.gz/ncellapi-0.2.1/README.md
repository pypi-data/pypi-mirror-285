# NcellAPI (Unofficial)

NcellAPI is am unofficial Python wrapper for the Ncell API, providing a convenient way to interact with Ncell's services such as checking balance, usage details, free SMS quota, and sending SMS. This library aims to simplify the process of making authenticated requests and handling responses from the Ncell API.

## Disclaimer

This library is not affiliated with, endorsed by, or supported by Ncell. Use it at your own risk. The developers of this library are not responsible for any misuse, damage, or issues that may arise from using this software. Always comply with Ncell's terms of service and policies.

## Features

- Login and session management
- Query account balance
- Get usage details
- Check free SMS quota
- Send SMS
- Validate SMS before sending
- Pydantic model support for response validation
- Conversion of responses to dictionary format

## Installation

### Installing from PyPI:

```sh
pip install ncellapi
```

### Installing from the source

1. **Clone the Repository:**

```sh
git clone https://github.com/ashishkandu/ncellapi.git
```

2.**Install Poetry:**
If you don't have Poetry installed, you can install it using the following command:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install Dependencies and the Package:**
Navigate to the project directory and install the dependencies and the package using Poetry:

```sh
cd ncellapi
poetry install
```

4. **Activate the Virtual Environment:**
Poetry creates a virtual environment for the project. You can activate it using the following command:

```sh
poetry shell
```

5. Run Your Code:

Once the virtual environment is activated, you can run your code or scripts that use the ncellapi package.

## Usage

Here's an example of how to use the NcellAPI library:

```python
from ncellapi import Ncell

# Initialize the API with your credentials
ncell = Ncell(msisdn=1234567890, password='your_password')

# Login to the Ncell system
login_response = ncell.login()
print(login_response.to_dict())

# Check balance
balance_response = ncell.balance()
print(balance_response.to_dict())

# Get usage details
usage_detail_response = ncell.usage_details()
print(usage_detail_response.to_dict())

# Check free SMS quota
sms_count_response = ncell.free_sms_count()
print(sms_count_response.to_dict())

# Send SMS
send_sms_response = ncell.send_sms(recipient_mssidn=9876543210, message='Hello, this is a test message.')
print(send_sms_response.to_dict())
```

## Documentation

### Initialization

```python
from ncellapi import Ncell, InvalidCredentialsError

try:
    ncell = Ncell(msisdn, password)
except InvalidCredentialsError as e:
    print(f"Invalid credentials: {e}")

```

* `msisdn`: Your Ncell mobile number.
* `password`: Your Ncell account password.

### Login

```python
from ncellapi import NetworkError

try:
    login_response = ncell.login()
    print(login_response.to_dict())
except NetworkError as e:
    print(f"Network error: {e}")
```

### Check Balance

```python
balance_response = ncell.balance()
```

### Get Usage Details

```python
usage_detail_response = ncell.usage_details()
```

### Check Free SMS Quota

```python
sms_count_response = ncell.free_sms_count()
```

### Send SMS

```python
send_sms_response = ncell.send_sms(recipient_mssidn, message, send_time)
```

* `recipient_mssidn`: The recipient's mobile number.
* `message`: The message to be sent.
* `send_time`: (Optional) The time to send the message.

## Handling Errors

The library raises `InvalidCredentialsError` for invalid credentials and `NetworkError` for network-related issues. Other errors are logged and handled within the response objects.

```python
from ncellapi import NetworkError

try:
    balance_response = ncell.balance()
    print(balance_response.to_dict())
except NetworkError as e:
    print(f"Network error: {e}")
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any issues or questions, please open an issue on GitHub.

