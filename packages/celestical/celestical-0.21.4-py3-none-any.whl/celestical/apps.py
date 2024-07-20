""" Apps related actions
"""
from celestical.configuration import (
    API_URL, api_configuration, cli_logger)
from celestical.helper import cli_panel
from celestical import api
from celestical.api.exceptions import UnauthorizedException
from celestical.user import load_user_creds

# logging.basicConfig(encoding='utf-8', level=LOGGING_LEVEL)


def list_creator_apps() -> bool:
    """ List /app/ the latest created apps """
 
    apiconf = api_configuration()
    setcred, msg = load_user_creds(apiconf)
    if setcred is False:
        cli_panel(msg)
        return False

    api_response = None
    with api.ApiClient(apiconf) as api_client:
        app_api = api.AppApi(api_client)

        try:
            api_response = app_api.get_user_apps_app_get()

        except UnauthorizedException as oops:
            cli_panel("You might have to login again, Your token expired.")
            return False
        except Exception as oops:
            cli_logger.debug(oops)
            cli_panel("Could not connect; check your connection.")
            return False

    show_res = api_response
    if isinstance(api_response, api.models.app.App):
        show_res = [api_response]

    msg = "\n"
    deployed_wip = False
    for app in show_res:
        dcolor = "red"
        if deployed_wip is True:
            dcolor = "blue"
        msg += f" - [{dcolor}][underline]{app.get('url','[no url]')}[/underline][/{dcolor}]"
        msg += f" [yellow]{app['id']}[/yellow]"
        msg += f" created on {app['created_date']}\n"

    cli_panel(msg, _title="Celestical - Your apps")
    return True
