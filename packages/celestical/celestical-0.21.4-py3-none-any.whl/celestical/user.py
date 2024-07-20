""" user related functions

    This file holds the routines to login, register
    and manage user data and configuration.
"""
import getpass
from typing import Tuple

from celestical import api
from celestical.api import ApiClient, ApiException, AuthApi, UserCreate
from celestical.configuration import (API_URL, api_configuration,
                                      celestical_date, cli_logger, load_config,
                                      reset_config, save_config)
from celestical.helper import cli_panel, confirm_user, print_text, prompt_user, confirm_user


def register_form(ask:str = "Register with or without a [b]special code[/b]",
    default_code:str = ""
    ) -> str:
    if ask != "":
        print_text(ask)
    user_code = prompt_user("[b]special code[/b] (optional)", default=default_code)
    return user_code


def login_form(ask:str = "Please enter your [i]celestical[/i] credentials",
               default_email:str = None
              ) -> Tuple[str, str]:
    """ The username/password form to login and register """

    if ask != "":
        print_text(ask)

    # -------------- username
    user_mail = prompt_user("work email", default=default_email)
    if "@" not in user_mail:
        cli_logger.error("Entered email address is missing a '@'")
        cli_panel(message="Email is incorrect: no @ sign found.", _type="error")
        return login_form(ask)

    # -------------- password
    password = getpass.getpass(" *** password: ")
    cli_logger.info("Password succesfully created.")

    if len(password) == 0:
        cli_logger.error("Password was empty")
        cli_panel(message="Password was empty!", _type="error")
        return login_form(ask="Please re-enter your [i]celestical[/i] credentials")

    if len(password) <= 7:
        cli_logger.error("Password is too short - less than 8 chars")
        cli_panel(message="Password too short - less than 8 chars!", _type="error")
        return login_form(ask="Please re-enter your [i]celestical[/i] credentials")

    return (user_mail, password)


def user_login(default_email:str = None,
               force_relog:bool = False,
               ) -> bool:
    """Login to Parametry's Celestical Cloud Services via the CLI.

    Returns:
        bool
    """
    cli_logger.info("Entering user login function in user.py")
    user_data = load_config()
    if default_email is not None:
        user_data['username'] = default_email

    prask = ""

    if force_relog:
        if not reset_config():
            return False

        # user_data was loaded before the reset
        if "username" in user_data:
            if user_data['username'] is None or user_data['username'] == "":
                return user_login(default_email=None)
            # else we've got a previous email info
            return user_login(default_email=user_data['username'])
        return user_login()
    elif len(user_data["access_token"]) > 10 and  len(user_data["username"]) > 3:
        use_user = confirm_user("Do you want to continue with logged " \
            + f"in user: [yellow]{user_data['username']}[/yellow]")
        if use_user:
            default_email = user_data["username"]
            prask = f"Ok login again with [i]{default_email}[/i]" 

    if prask != "":
        (username, password) = login_form(ask=prask, default_email=default_email)
    else:
        (username, password) = login_form(default_email=default_email)

    apiconf = api_configuration()
    with ApiClient(apiconf) as api_client:
        # Create an instance of the API class
        api_instance = AuthApi(api_client)

        save_ok = False
        try:
            # Auth:Jwt.Login
            api_response = api_instance.auth_jwt_login_auth_jwt_login_post(username, password)
            cli_logger.debug("We did get a login api response")
            if api_response.token_type != "bearer":
                cli_logger.debug("This client does not handle non bearer type token")
                return False

            if len(api_response.access_token) < 10:
                cli_logger.debug("Received token seems invalid")
                return False

            # Collect all user data and save it
            cli_logger.debug("Creating and saving user data/conf.")
            data = {
                "created": celestical_date(),
                "username": username,
                "access_token": api_response.access_token,
                "token_type": api_response.token_type
            }
            save_ok = save_config(data)
        except ApiException as api_exp:
            cli_logger.error("Code Enceladus: ApiException when logging in. Assuming wrong user,password tuple.")
            cli_logger.debug(api_exp)
            print_text("Sorry user/password are not matching. Not logged in",
                       worry_level="ohno")
            return False
        except Exception as oops:
            cli_logger.error("Code Mars: could not connect, try again after checking your connection.")
            cli_logger.debug(oops)
            print_text("Sorry we could not log you in, please try again.",
                       worry_level="ohno")
            return False

    cli_panel("\t --> You are now logged in as user: "
              +f"[yellow]{username}[/yellow]"
              +"\n\n\t     You use other celestical commands"
              +"\n\t     as long as your login token is valid.")
    return True


def user_register() -> int:
    """Register as a user for Parametry Cloud Services via the CLI."""

    user_code = register_form()

    (user_mail, password) = login_form("")
    repassword = getpass.getpass(" *** re-enter password: ")
    flag = 0

    if repassword != password:
        msg = "Re-entered password does not match. "
        msg += 'Please run [blue]celestical register[/blue] again to register'
        print_text(text=msg, worry_level="ohno")
        flag += 2
        return flag
    
    apiconf = api_configuration()

    
    with ApiClient(apiconf) as api_client:
        auth = AuthApi(api_client=api_client)

        apires = None
        try:
            apires = auth.register_register_auth_register_post(
                    user_create=UserCreate(
                        email=user_mail,
                        password=password,
                        code=user_code
                        )
                    )
        except ApiException as api_err:
            msg = f"---- Registration error ({api_err.status})"
            cli_logger.error(msg)
            cli_logger.debug(apires)
            if api_err.body:
                cli_logger.debug(api_err.body)
            else:
                cli_logger.debug(api_err.reason)
            return flag
        except Exception as oops:
            cli_logger.error(oops)
            return flag
    config = load_config()
    current_user = "" if config['username'] == '' else f"from [yellow]{config['username']}[/yellow]"
    msg = 'Do you want to switch your default user '
    msg += f"{current_user} to [yellow]{user_mail}[/yellow]"
    flag += 1
    cli_panel('You have successfully registered')
    if config["username"] == '' or confirm_user(msg):
        config["username"] = user_mail
        flag += 1
        if save_config(config):
            flag += 1

    return flag


def load_user_creds(_apiconf) -> Tuple[bool, str]:
    """ Reads user creds from config and set access token

        _apiconf from api.Configuration() in api_configuration()
        is set with latest access token.
    """
    user_data = load_config()

    if user_data is not None and isinstance(user_data, dict):
        # cover the case of an apiKey type security
        _apiconf.api_key['Authorization'] = \
          user_data.get("access_token", "")
        _apiconf.api_key_prefix['Authorization'] = \
          user_data.get("token_type", "bearer")
        # cover the case of an http+bearer type security
        # (this is current default on celestical's API side
        _apiconf.access_token = user_data.get("access_token", "")
        return True, "Loaded creds for API request"

    msg = "[red] You need to login or relogin before proceeding[/red]\n"
    msg += ">>> [underline]celestical login[/underline]"
    return False, msg
