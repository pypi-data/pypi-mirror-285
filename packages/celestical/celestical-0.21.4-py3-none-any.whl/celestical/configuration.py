"""
Managing the configuration for the Celestical services
"""
import json
import os
import logging
import importlib.metadata
import datetime
from pathlib import Path

import typer
from prettytable import PrettyTable, ALL

import celestical.api as api

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
API_HOST = "moon.celestical.net"
API_URL = "https://" + API_HOST

current_celestical_version = importlib.metadata.version('celestical')

# LOGGING_LEVEL = logging.DEBUG
# logging.basicConfig(encoding='utf-8', level=LOGGING_LEVEL)

HOTLINE = "starship@celestical.net"
PRODUCTION = True
BATCH_MODE = False


def api_configuration():
    conf_for_api = api.Configuration(host=API_URL)
    conf_for_api.verify_ssl = True
    #conf_for_api.assert_hostname = True
    conf_for_api.tls_server_name = API_HOST

    return conf_for_api


def get_batch_mode():
    return BATCH_MODE


def celestical_date() -> str:
    return str(datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%S'))


def get_login_status() -> str:
    login_status = ""
    # [{wcol}]colored text[/{wcol}]
    wcol = "purple"

    udata = load_config()
    if not (udata is None or udata == {}):
        # else message that config cannot be loaded will be shown.
        tok = udata["access_token"]
        uname = udata["username"]
        if uname != "":
            login_status += f"\n\t* Current user: [{wcol}]{uname}[/{wcol}]"
        else:
            login_status += f"\n\t* No current user [{wcol}]logged in[/{wcol}]"
        if tok != "":
            # TODO checked the created date field to announce
            # if relogging is necessary.
            login_status += f"\n\t* [{wcol}]Already logged in[/{wcol}] once"

    return login_status


def welcome(verbose:int=2) -> str:
    """ Return a global welcome message

        verbose from 0 (short) to 2 (long)
    """
    wcol = "purple"
    welcome_message:str = f"[{wcol}]Direct deployment of containers or compose" \
                          +" files to an independent green cloud made by space" \
                          +f" engineers[/{wcol}] " \
                          +f"(version: {current_celestical_version})\n"

    if verbose > 0:
        welcome_message += get_login_status()


    if verbose > 1:
        welcome_message += "\n [underline]Usual workflow steps[/underline]" \
                        +"\n\t [1] (only once) Register with command " \
                        +f"[{wcol}]celestical register[/{wcol}]" \
                        +"\n\t [2] Login with command " \
                        +f"[{wcol}]celestical login[/{wcol}]" \
                        +"\n\t [3] Deploy with command " \
                        +f"[{wcol}]celestical deploy[/{wcol}]"

    return welcome_message


# Service types definitions
def get_default_config_dir() -> Path:
    path = Path.home() / ".config" / "celestical"
    return path


def get_default_config_path() -> Path:
    """Return the default config path for this application

    Returns:
        Path typed path to the config json file
    """
    path = get_default_config_dir() / "config.json"
    return path


def get_default_log_path() -> Path:
    """Return the default log file path for this application

    Returns:
        Path typed path to the log file
    """
    path = get_default_config_dir() / "celestical.log"
    return path


def _get_default_config_data() -> dict:
    data = {
        "created": celestical_date(),
        "username": "",
        "access_token": "",
        "token_type": "",
        "batch": False
    }
    return data


def reset_config():
    """ Reset config is used to logout and start login protocol from scratch
    """
    # Similar to a logout: forgetting token
    data = {
        "created": celestical_date(),
        "username": "",
        "access_token": "",
        "token_type": "",
        "batch": False
    }
    return save_config(data)


def load_config(config_path: str = "") -> dict:
    """Load config file from config_path.

    Params:
        config_path(str): non-default absolute path of the configuration.
    Returns:
        (dict): configuration content
    """
    path = get_default_config_path()
    if config_path is not None and config_path != "":
        path = Path(config_path)

    user_data = {}
    if path.exists():
        try:
            with open(path, 'r') as f_desc:
                user_data = json.load(f_desc)
        except:
            # Use only standard print function
            print(" *** could not read the celestical configuration file.")
            user_data = {}

    default_data = _get_default_config_data()
    for key in default_data:
        if key not in user_data:
            user_data[key] = default_data[key]

    return user_data


def save_config(config:dict) -> bool:
    """Save config file to the default_config_path.

    Params:
        config(dict): configuration.
    Returns:
        (bool): True if saving process went fine
    """
    cpath = get_default_config_path()

    try:
        if not cpath.parent.exists():
            os.makedirs(cpath.parent, exist_ok=True)
    except Exception as oops:
        cli_logger.debug("save_config: directory couldn't be created.")
        cli_logger.debug(oops)
        return False

    # Check if all fields are saved for uniformization
    if "created" not in config:
        config["created"] = celestical_date()
    if "username" not in config:
        config["username"] = ""
    if "access_token" not in config:
        config["access_token"] = ""
    if "token_type" not in config:
        config["token_type"] = ""
    if "batch" not in config:
        config["batch"] = False

    try: 
        with cpath.open(mode='w') as fdescr:
            json.dump(config, fdescr, indent=4)
    except Exception as oops:
        cli_logger.debug("save_config: config file couldn't be written.")
        cli_logger.debug(oops)
        return False

    return True


def cli_setup() -> bool:
    """ Setup necessary directories.
    """
    config_path = get_default_config_dir()
    try:
        config_path.mkdir(parents=True, exist_ok=True)
    except Exception as oops:
        return False
    return True


def create_logger(production: bool=False) -> logging.Logger :
    """A function to create and configure the logger for the Celestical CLI
    Params:
        production(bool): if False, set log level to debug
    Returns:
        (logger): the logger object
    """
    log_format = "%(asctime)s --%(levelname)s: %(message)s"
    log_location = get_default_log_path()

    logging.basicConfig(
        encoding='utf-8',
        filename=log_location,
        format=log_format,
        filemode="a",
        level=logging.WARNING if production else logging.DEBUG,
    )
    logger = logging.getLogger(name="Celestical CLI")
    if production is False:
        logger.debug(f"Starting Logger in DEBUG Mode: {log_location}")
    else:
        logger.warning(f"Starting Logger in WARNING Mode: {log_location}")
    return logger

cli_setup()
# Creation of the CLI-wide logger -> celestical.log
cli_logger = create_logger(production=PRODUCTION)
