import json
import os

import requests

import logger
from constants import load_resource

REPO_NAME = "covid-data-analysis"
GITHUB_ACCESS_TOKEN_ENV_VAR = "GITHUB_ACCESS_TOKEN"
GITHUB_USER_ENV_VAR = "GITHUB_USER"

log = logger.get_logger()


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


def new_positive_regions(df_regional_data):
    df = df_regional_data.tail(21)
    df = df.sort_values(by=['nuovi_positivi']).tail(3)
    return df['denominazione_regione'].tolist()


def get_environment_variable(env_var_name):
    env_var = os.getenv(env_var_name)
    log.info(f"Loading Environment Variable '{env_var_name}'")
    if env_var is None:
        log.info(f"Environment variable {env_var_name} was not found. Returning empty string")
        return ""
    return str(env_var)


# Remember to set the environment variables for the GitHub user and token in your IDE to get access to the Git API locally
# Remember to set these also in Heroku Config Vars
def get_version():
    user = get_environment_variable(GITHUB_USER_ENV_VAR)
    token = get_environment_variable(GITHUB_ACCESS_TOKEN_ENV_VAR)

    resp = requests.get(f'https://api.github.com/repos/{user}/{REPO_NAME}/tags', auth=(user, token))

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
