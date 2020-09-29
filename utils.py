import json
import os

import requests

import logger
from constants import GITHUB_USER_ENV_VAR, GITHUB_ACCESS_TOKEN_ENV_VAR, DEBUG_MODE_ENV_VAR, REPO_NAME
from resources import load_resource

log = logger.get_logger()


class GitApiData:

    def __init__(self, user, token):
        self.user = user
        self.token = token


def get_options(list_value):
    dict_list = []
    for i in list_value:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def get_options_from_list(field_list):
    dict_list = []
    for data in field_list:
        dict_list.append({'label': str(load_resource(data)), 'value': str(data)})

    return dict_list


def get_environment_variable(env_var_name):
    env_var = os.getenv(env_var_name)
    log.info(f"Loading Environment Variable '{env_var_name}'")
    if env_var is None:
        log.info(f"Environment variable {env_var_name} was not found. Returning empty string")
        return ""
    return str(env_var)


def load_git_environment_variables():
    user = get_environment_variable(GITHUB_USER_ENV_VAR)
    token = get_environment_variable(GITHUB_ACCESS_TOKEN_ENV_VAR)
    return user, token


def is_debug_mode_enabled():
    debug_mode = get_environment_variable(DEBUG_MODE_ENV_VAR)
    if debug_mode.lower() == 'true':
        log.info(f"{DEBUG_MODE_ENV_VAR} is enabled. Never do this in production")
        return True
    elif debug_mode.lower() == 'false':
        return False
    elif debug_mode == "":
        log.info(f"{DEBUG_MODE_ENV_VAR} is not set in your Environment Configuration. Setting False as default")
        return False
    else:
        log.error(f"{DEBUG_MODE_ENV_VAR} was not set correctly, it expect True or False as value. Setting False as default")
        return False


git_user_data = GitApiData(*load_git_environment_variables())


# TODO Remember to set the environment variables for the GitHub user and token in your IDE to get access to the Git API locally
# TODO Remember to set these also in Heroku Config Vars
def get_version():
    resp = requests.get(f'https://api.github.com/repos/{git_user_data.user}/{REPO_NAME}/tags',
                        auth=(git_user_data.user, git_user_data.token))

    if resp.status_code == 401:
        log.info("Unauthorized access to GitHub API, check your credentials")
        return ""
    elif resp.status_code != 200:
        log.info("It was not possible to access GitHub API, retry later")
        return ""

    data = json.loads(resp.text)
    version = data[0]['name']
    log.info(f"Application version: {version}")

    return version
