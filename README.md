# Postman Toolkit

Application used to define properties that can be later used in Postman. While Postman itself allows defining
variables, it doesn't support using multiple environments at the same time (with overriding of variables). 

## Installation

Requirements:
* Python 3.7 or newer
* NodeJS (development only)

Installation: 

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```
1. Go to `install` directory and execute install script in PowerShell:
   ```
   .\install.ps1
   ``` 
1. Run created archive:
   ```
   python .\postman-toolkit.zip
   ```
1. Go to `http://localhost:8881/app`. 


## Development

1. Set the following environment variables:
    ```
    PYTHONUNBUFFERED=1
    FLASK_ENV=development
    DEBUG=true
    ```