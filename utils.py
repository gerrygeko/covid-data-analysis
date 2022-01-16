import csv
import json
import os
from urllib.request import urlopen

import datetime
import requests
import pandas as pd
import json as js
import logger
from constants import GITHUB_USER_ENV_VAR, GITHUB_ACCESS_TOKEN_ENV_VAR, DEBUG_MODE_ENV_VAR, REPO_NAME, CURRENT_LOCALE_ENV_VAR
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


def is_macos_mode_enabled():
    macos_mode = get_environment_variable(CURRENT_LOCALE_ENV_VAR)
    if macos_mode.lower() == 'true':
        log.info(f"{CURRENT_LOCALE_ENV_VAR} is enabled. Never do this in production")
        return True
    elif macos_mode.lower() == 'false':
        return False
    elif macos_mode == "":
        log.info(f"{CURRENT_LOCALE_ENV_VAR} is not set in your Environment Configuration. Setting False as default")
        return False
    else:
        log.error(f"{CURRENT_LOCALE_ENV_VAR} was not set correctly, it expect True or False as value. Setting False "
                  f"as default")
        return False


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
        log.error(f"{DEBUG_MODE_ENV_VAR} was not set correctly, it expect True or False as value. Setting False as "
                  f"default")
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


def load_csv_from_file(path):
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
        k, v = row
        d[k] = v
    return d


def load_csv(url, data_string=None):
    if data_string is not None:
        data_loaded = pd.read_csv(url, parse_dates=[data_string])
    else:
        data_loaded = pd.read_csv(url)
    log.info(f"Data loaded at {datetime.datetime.now().time()}")
    return data_loaded


def load_geojson(url):
    with urlopen(url) as response:
        json = js.load(response)
    return json


#component style
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    mapbox=dict(
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)


style_vaccines_italy_tab = {
    'background-image': 'url("/assets/logo_vax.png")',
    'background-position': 'right top',
    'background-size': '40px 40px',
    'background-repeat': 'no-repeat',
    'color': 'crimson'
}

style_vaccines_italy_herd_immunity = {
    'background-image': 'url("/assets/logo_vax.png")',
    'background-position': 'right center',
    'background-size': '20px 20px',
    'background-repeat': 'no-repeat',
    'color': 'crimson'
}
