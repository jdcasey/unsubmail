import os
from ruamel.yaml import YAML
import subprocess

HOME_CONFIG_FILE=os.path.join(os.environ.get('HOME'), '.config/unsubmail/config.yaml')
SERVER = 'server'
USER = 'user'
PASSWORD = 'password'
MAILBOXES= 'mailboxes'

def depass(password):
    if password and password.startswith('pass:'):
        key = password[5:]
        
        print(f"Reading password from key: {key}")
        result = subprocess.run(['pass', key], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    
    return password


def load(config_file=None):
    config_path = config_file or HOME_CONFIG_FILE

    if os.path.exists(config_path) is not True:
    	raise Exception(f"No configuration defined in {config_file} or {HOME_CONFIG_FILE}")
    	
    data = {}

    print(f"Loading config from: {config_path}")
    with open(config_path) as f:
        data = YAML().load(f)

    errors = []
    for key in (SERVER, USER, PASSWORD):
        if data.get(key) is None:
            errors.append(key)

    if len(errors) > 0:
        raise Exception(f"You must provide configuration for {errors} in {config_path}")

    data[PASSWORD] = depass(data[PASSWORD])

    return Config(data)

class Config:
    def __init__(self, data):
        self.server = data.get(SERVER)
        self.user = data.get(USER)
        self.password = data.get(PASSWORD)
        self.mailboxes = data.get(MAILBOXES)