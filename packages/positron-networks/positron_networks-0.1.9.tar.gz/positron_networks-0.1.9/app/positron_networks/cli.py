import typer
import configparser
import requests
import time
import os
import webbrowser

app = typer.Typer()

AUTH0_DOMAIN = 'positron-beta.us.auth0.com'
AUTH0_CLIENT_ID = 'ZW0vio95rYfbHrN7kE3PoUXwmPloBw7e'
AUTH0_AUDIENCE = 'https://beta/positron/api'
ALGORITHMS = ['RS256']

POSITRON_API_BASE = 'https://beta.positronsupercompute.com/backend/api'
LOCAL_API_BASE = 'http://localhost:3000/api'

@app.command()
def hello():
    print('Hello, I am the Positron CLI')
    print('Here is a list of thing I can help you with:')
    print('- Logging you in to your Positron account and create your configuration file that will help you run jobs easily in the cloud')

@app.command()
def login(local: bool = False):
    if local:
        global POSITRON_API_BASE; POSITRON_API_BASE = LOCAL_API_BASE

    # Get device code
    print('Requesting device code')
    device_code_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'scope': 'openid profile',
        'audience': AUTH0_AUDIENCE
    }
    device_code_response = requests.post(f'https://{AUTH0_DOMAIN}/oauth/device/code', data=device_code_payload)
    if device_code_response.status_code != 200:
        print('Error generating device code')
        raise typer.Exit(code=1)
    
    device_code_data = device_code_response.json()
    
    # Redirect to login
    print('1. On your computer or mobile device navigate to: ', device_code_data['verification_uri_complete'])
    print('2. Enter the following code: ', device_code_data['user_code'])
    print('3. Complete the login process')
    print('')
    webbrowser.open(url=device_code_data['verification_uri_complete'], new=2, autoraise=True)

    # Wait for authentication
    access_token = wait_for_access_token(device_code_data)
    
    # Get user token
    print('Requesting User Auth Token')
    auth_header = {
        'Authorization': f'Bearer {access_token}'
    }
    user_token_response = requests.get(f'{POSITRON_API_BASE}/get-user-auth-token', headers=auth_header)

    if user_token_response.status_code != 200:
        print(user_token_response.json())
        print('Error getting User Auth Token')
        raise typer.Exit(code=1)
    user_token_response_data = user_token_response.json()

    # Save user token
    print(f'Creating positron configuration at: {os.path.expanduser("~/.positron")}')
    save_user_token(user_token_response_data['userAuthToken'])


def wait_for_access_token(device_code_data):
    token_payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code_data['device_code'],
        'client_id': AUTH0_CLIENT_ID
    }
    authenticated = False
    while not authenticated:
        print('Checking if the user completed the flow...')
        token_response = requests.post(f'https://{AUTH0_DOMAIN}/oauth/token', data=token_payload)

        token_data = token_response.json()
        if token_response.status_code == 200:
            print('Authenticated!')
            authenticated = True
            return token_data['access_token']
        elif token_data['error'] not in ('authorization_pending', 'slow_down'):
            print(token_data['error_description'])
            raise typer.Exit(code=1)
        else:
            time.sleep(device_code_data['interval'])

def save_user_token(user_token):
    try:
        config_folder = os.path.expanduser('~/.positron')
        if not os.path.exists(config_folder):
            os.mkdir(config_folder)
        config_path = os.path.expanduser('~/.positron/config.ini')
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'UserAuthToken': user_token}
        with open(config_path, 'w') as config_file:
            config.write(config_file)
    except:
        print('Could not create configuration file')
        typer.Exit(code=1)

if __name__ == "__main__":
    app()


    