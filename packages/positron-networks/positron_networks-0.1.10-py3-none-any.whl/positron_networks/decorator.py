from functools import wraps
import os
import requests
import tarfile
import asyncio
import socketio
from colorama import init, Fore
import time
import configparser
import argparse
import signal
import json
import yaml
import sys

# Initialize colorama
init(autoreset=True)

# Init configuration
config = configparser.ConfigParser()

# Parse command line arguments
parser = argparse.ArgumentParser(description = "A decorator to handle deploying your code into the cloud")
parser.add_argument('--positron-deploy', action='store_true', help='Deploy your script into Positron Cloud', dest='deploy')
parser.add_argument('--stream-stdout', action='store_true', help='Stream the stdout from Positron Cloud back to your cli', dest='stream_stdout')
parser.add_argument('--debug', action='store_true', help='Get more detailed error messages', dest='debug')
positron_args, job_args = parser.parse_known_args()

# Cross component enums
log_types = dict(
    stdout="INFO",
    stderr="ERROR",
    debug="DEBUG"
)

# Decorator definition
def positron_sync(**positron_parameters):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if positron_args.deploy:
                positron_deploy(positron_parameters)
            else:
                parser.print_help()
                func(*args, **kwargs)

        return wrapper
    return decorator

# Cloud deployment definition
def positron_deploy(positron_parameters):
    signal.signal(signal.SIGINT, handle_sigint)
    global API_BASE
    global API_CREATE_JOB
    global API_GET_PRESIGNED
    global API_START_JOB
    global SOCKET_IO_DOMAIN, SOCKET_IO_PATH
    global COMPRESSED_WS_NAME

    API_BASE = positron_parameters.get('dev_api', 'https://beta.positronsupercompute.com/backend/api')
    SOCKET_IO_DOMAIN = positron_parameters.get('dev_ws', 'wss://beta.positronsupercompute.com')
    SOCKET_IO_PATH = '/backend/api/ws/socket.io' # '/api/ws/socket.io' # 
    API_CREATE_JOB = f'{API_BASE}/create-job'
    API_GET_PRESIGNED = f'{API_BASE}/generate-presigned-url'
    API_START_JOB = f'{API_BASE}/start-job'
    COMPRESSED_WS_NAME = 'workspace.tar.gz'

    try:
        print('Loading Configuration')
        load_config()
        load_job_config(positron_parameters)

        print('Validating sync parameters')
        validate_sync_parameters(parameters=positron_parameters)

        global auth_token, funding_group, image_name, environment_id, workspace_dir, entry_point
        auth_token = config['DEFAULT']['UserAuthToken']
        funding_group = positron_parameters.get('funding_group')
        image_name = positron_parameters.get('image_name')
        environment_id = positron_parameters.get('environment_id')
        workspace_dir = positron_parameters.get('workspace_dir')
        entry_point = positron_parameters.get('entry_point')

        print('Creating workspace tar file')
        create_workspace_tar()

        print('Creating new job')
        job = create_job()

        print('Fetching presigned url for upload')
        resp = get_presigned_url(job_id=job['id'])

        print('Uploading compressed workspace to Positron storage')
        upload_file(resp.get('url'), resp.get('fields'))

        print('Starting Job')
        start_job(job_id=job['id'])

        print(f"Your workspace has been uploaded and the job is in a processing queue. Please check your dashboard to follow your jobs {job['name']} status!")

        start_stdout_stream(job['id'])
        
    except PositronException as e:
        print(e)
    except Exception as e:
        print('An exception occured. Please use --debug flag to get details')
        debug(e)


def load_config():
    env_token = os.getenv('PositronUserAuthToken', False)
    config_path = os.path.expanduser('~/.positron/config.ini')
    if env_token:
        config['DEFAULT'] = {'UserAuthToken': env_token}
    elif os.path.exists(config_path):
        config.read(config_path)    
    else:
        raise PositronException('Missing UserAuthToken, please init configuration')


def load_job_config(parameters):
    script_dir = os.path.dirname(sys.argv[0])
    config_path = os.path.join(script_dir, "job_config.yaml")
    if not os.path.exists(config_path):
        return
    try:
        with open(config_path, 'r') as job_config_file:
            job_config = yaml.safe_load(job_config_file)
            keys = [
                'funding_group',
                'environment_id',
                'image_name'
            ]
            for key in keys:
                config = job_config['python_job'][key]
                if not parameters.get(key, False) and config is not None:
                    parameters[key] = config
    except Exception as e:
        debug(f'Error loading job configuration! {str(e)}')


def validate_sync_parameters(parameters):
    valid = True
    if not parameters.get('funding_group', False):
        print('Missing decorator parameter: funding_group')
        valid = False
    if not parameters.get('image_name', False):
        print('Missing decorator parameter: image_name')
        valid = False
    if not parameters.get('environment_id', False):
        print('Missing decorator parameter: environment_id')
        valid = False
    if not parameters.get('workspace_dir', False):
        print('Missing decorator parameter: workspace_dir')
        valid = False
    if not parameters.get('entry_point', False):
        print('Missing decorator parameter: entry_point')
        valid = False

    if not valid:
        raise PositronException(
            'Validation failed! Please check your decorator parameters!')


def create_workspace_tar():
    # Use the context manager to handle opening and closing the tar file
    with tarfile.open(COMPRESSED_WS_NAME, 'w:gz') as tar:
        for root, dirs, files in os.walk(workspace_dir):
            for exclude_dir in ['.venv', '.git', '__pycache__']:
                try:
                    dirs.remove(exclude_dir)
                except ValueError:
                    # Ignore if the directory is not in the list
                    pass
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=workspace_dir)
                tar.add(full_path, arcname=arcname)


def create_job():
    debug(f'Calling: {API_CREATE_JOB}')
    data = {"imageName": image_name, "fundingGroupId": funding_group, "environmentId": environment_id, "entryPoint": entry_point, "jobArguments": job_args}
    debug(data)
    Headers = {"PositronAuthToken": auth_token}
    response = requests.post(API_CREATE_JOB, headers=Headers, json=data)
    debug(response)
    if response.status_code != 200:
        raise PositronException(
            f'Job creation failed with http code: {response.status_code} \n {response.text}')
    else:
        debug(response.json())
        return response.json()


def get_presigned_url(job_id):
    Headers = {"PositronAuthToken": auth_token, "PositronJobId": job_id}
    url = API_GET_PRESIGNED + '?filename=' + COMPRESSED_WS_NAME
    debug(f'Calling: {url}')
    response = requests.get(url, headers=Headers)
    debug(response)
    if response.status_code != 200:
        raise PositronException(
            f'Presigned url fetching failed with http code: {response.status_code} \n {response.text}')
    else:
        debug(response.json())
        return response.json()


def upload_file(url, data):
    with open(COMPRESSED_WS_NAME, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, data=data, files=files)
        if response.status_code != 204:
            raise PositronException(
                f'Upload failed with http code: {response.status_code} \n {response.text}')


def start_job(job_id):
    Headers = {"PositronAuthToken": auth_token, "PositronJobId": job_id}
    debug(f'Calling: {API_START_JOB}')
    response = requests.get(API_START_JOB, headers=Headers)
    debug(response)
    if response.status_code != 200:
        raise PositronException(
            f'Failed to start job with http code: {response.status_code} \n {response.text}')
    else:
        debug(response.json())
        return response.json()


def start_stdout_stream(job_id):
    if positron_args.stream_stdout:
        try:
            asyncio.get_event_loop().run_until_complete(start_stream(job_id))
        except Exception as e:
            print (e)


sio = socketio.AsyncClient()


@sio.event(namespace='/stdout-stream')
async def connect():
    print('Connected to stdout stream')


@sio.event(namespace='/stdout-stream')
async def message(message):
    try:
        log = json.loads(message)
        if log['log_level'] == log_types['stdout']:
            print(Fore.GREEN + log['message'])
        elif log['log_level'] == log_types['stderr']:
            print(Fore.RED + log['message'])
        elif log['log_level'] == log_types['debug']:
            print(Fore.BLUE + log['message'])            
    except:
        print(message)


@sio.event(namespace='/stdout-stream')
async def disconnect():
    print('Disconnected from stdout stream')


@sio.event(namespace='/stdout-stream')
async def error(err):
    print('An error occured in the streaming process')
    debug(err)


async def start_stream(job_id):
    custom_headers = {
        "PositronAuthToken": auth_token,
        "PositronJobId": job_id
    }
    await sio.connect(SOCKET_IO_DOMAIN, headers=custom_headers, socketio_path=SOCKET_IO_PATH)
    await sio.wait()


def handle_sigint(signum, frame):
    print('Terminating gracefully...')
    time.sleep(5)
    exit(0)

class PositronException(Exception):
    "Raised when decorator related errors are happening"
    pass


def debug(log):
    if positron_args.debug:
        print(log)
