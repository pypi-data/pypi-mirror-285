""" File to manage docker compose file and their enrichment """
import sys
import os
import threading
import time
from pathlib import Path
from typing import Tuple

import uuid
import yaml
import typer
import docker

import celestical.api as api
from celestical.api.exceptions import UnauthorizedException
from celestical.api import (
    App,
    Compose)

from celestical.user import (
    user_login,
    user_register,
    load_user_creds)

from celestical.docker_local import \
    compress_image

from celestical.helper import (
    cli_panel,
    prompt_user,
    confirm_user,
    print_text,
    print_feedback,
    guess_service_type_by_name,
    save_yaml,
    get_most_recent_file,
    extract_all_dollars,
    dict_to_list_env,
    SERVICE_TYPES)

from celestical.configuration import (
    HOTLINE,
    API_URL,
    cli_logger,
    api_configuration,
    load_config)

from celestical.utils import Spinner
#class ComposeEnricher():
#    def __init__():
#
#        # Keep a dictionary of missing variables with their
#        # name as key and $REF_IN_ENV as value.
#        missing_variables = {}

def _get_api_with_auth():
    apiconf = api_configuration()
    setcred, mesg = load_user_creds(apiconf)
    if setcred is False:
        cli_panel(mesg)
        return None
    return apiconf


def richformat_services(services:dict) -> str:
    """Create a rich formatted string to display a bullet list for services
    """
    s_info = ""
    for serv in services:
        image = services[serv].get("image", "-undefined-")
        s_info += f"\t- [yellow]{serv}[/yellow] (image)--> {image}\n"
    return s_info


def load_dot_env(env_dir:Path) -> dict:
    """ Read the .env file and extract all variables

    Returns:
        a dictionary of key value of these env variables.
    """
    env_file = env_dir / ".env"
    return load_env_file(env_file)


def load_env_file(env_file:Path) -> dict:
    """ Read the env_file and extract all variables name and value

    Returns:
        a dictionary of key value of these env variables.
    """
    loaded_env = {}

    # - load the content of .env
    if not env_file.is_file():
        return loaded_env

    with env_file.open(mode="r") as fdesc:
        for line in fdesc:
            line = line.strip()
            if not line:
                continue

            if line[0] == '#':
                continue

            split_line = line.split('=', 1)
            if len(split_line) == 2:
                k, v = split_line
                loaded_env[k] = v
            # else line is ignored
            # .env file is supposed to define stuffs
    return loaded_env


def _apply_os_env_or_one(denv:dict) -> dict:
    """ For key value dictionary where value is empty (None)
     - set the potential value from key as variable in the the OS/Shell environment
     OR
     - set it to "1" as required in the docker reference.

     None must be set prior to processing here as an empty string might be what
     a user exactly wants. None or empty value are the same when read by
     yaml.safe_load.

     Requirement all output values must be strings

    """
    for key in denv:
        if denv[key] is None:
            if key in os.environ:
                denv[key] = os.environ[key]
            else:
                denv[key] = "1"
    return denv


def _separate_kvpairs(env:list) -> dict:
    """ For an input list of "KEY=VALUE" separate everything in a dictionary
    for accessing KEY: VALUE easily
     - if no value is found just set a the value of a KEY as an empty string

    """
    compose_env = {}

    for vardef in env:
        vardef = vardef.strip()
        varsplit = vardef.split('=', 1)
        if len(varsplit) == 2:
            compose_env[varsplit[0]] = str(varsplit[1])
        elif len(varsplit) == 1:
            compose_env[varsplit[0]] = None

    compose_env = _apply_os_env_or_one(compose_env)

    return compose_env


def _apply_variables(env:list|dict, loaded_env:dict) -> list:
    """ Read the .env file and replace all variables in the env list with their
    compose_env = {}

    Params:
        env(list): is the list of strings from environment field in
        the docker-compose file
        loaded_env: should be the content of the .env file or any default env

    Returns:
        a dictionary with all variables with their found values 
        and a missing_replace parameter to tell how many variables where missed.
    """
    # - loading the content of env list of strings
    compose_env = {}

    if isinstance(env, list):
        compose_env = _separate_kvpairs(env)
    elif isinstance(env, dict):
        # to replace names by their value in env if exist
        # else set them to one
        compose_env = _apply_os_env_or_one(env)

    # - now applying .env (loaded_env) to compose_env
    missing_replace = 0
    for k in compose_env:
        var_str = str(compose_env[k])
        if "$" in var_str:
            # v2d var to dollars
            v2d = extract_all_dollars(var_str)
            for v in v2d:
                missing_replace += 1
                if v in loaded_env:
                    missing_replace -= 1
                    # replace the dollar variable
                    # with loaded_env corresponding value
                    compose_env[k] = var_str.replace(
                                        v2d[v],
                                        loaded_env[v])
                elif v in os.environ:
                    missing_replace -= 1
                    compose_env[k] = var_str.replace(
                                        v2d[v],
                                        os.environ[v])

    # - join both env and return, update loaded with modified compose_env
    #loaded_env.update(compose_env)

    return compose_env, missing_replace


def integrate_all_env(comp:dict, env_dir:Path) -> dict:
    """Read all files from docker-compose environment and env_files
       and loads their content to re-express it in the compose environment list
       of each services.

    Returns:
        the fully integrated compose dictionary
    """
    dot_env = load_dot_env(env_dir)

    for key in comp.get("services", {}):
        # Variables to develop by getting them from .env and os.env
        env = comp["services"][key].get("environment", None)
        if env is not None:
            comp["services"][key]["environment"], MR = _apply_variables(
                env,
                dot_env)

            print_text(f"{MR} undefined env variables in service {key}",
                worry_level="oops")

        # environt from envfiles to add
        env_files = comp["services"][key].get("env_files", [])
        key_env = {}
        for efile in [Path(x) for x in env_files]:
            if efile.is_absolute():
                key_env.update(load_env_file(efile))
            else:
                key_env.update(load_env_file(env_dir / efile))

        if env is None: 
            comp["services"][key]["environment"] = {}
        comp["services"][key]["environment"].update(key_env)

    return comp


def use_built_image_names(compose: dict, compose_path: Path) -> dict:
    """Add the generated image name for images built in the compose file and
    remove the build definition.
    """
    base_name = compose_path.resolve().parent.name

    if "services" not in compose:
        return compose

    for service_name, service in compose["services"].items():
        if "image" not in service and "build" in service:
            service["image"] = f"{base_name}-{service_name}:latest"
            del service["build"]

    return compose


def read_docker_compose(compose_path: Path, integrate_env_files: bool=True) -> dict:
    """ Read a docker-compose.yml file.
        and integrates environment variables from files.

    Params:
        compose_path(Path): path to the docker-compose.yml file
    Returns:
        (dict): docker-compose.yml file content
                or empty dictionary
    """

    compose = dict()

    if not isinstance(compose_path, Path):
        compose_path = Path(str(compose_path))

    compose_path = compose_path.resolve()

    def logerror(message:str):
        print_text(message)
        cli_logger.error(message)

    if compose_path.is_dir():
        logerror(f"Path is not a file: {compose_path}")
        return {}

    if compose_path.is_file():
        try:
            with compose_path.open(mode='r') as f:
                # Here all fields have native type
                # integers are integers
                compose = yaml.safe_load(f)
                if compose is None:
                    compose = {}
        except FileNotFoundError:
            logerror(f"No file found at given path: {compose_path}")
            return {}
    else:
        logerror(f"No file found at given path: {compose_path}")
        return {}

    # return even if compose == {}
    return compose


def enrich_compose(
    compose: dict,
    prev_comp:dict = {},
    ecomp_path:Path = None) -> Path:
    """Enrich a stack with additional information about the services.
    Params:
        compose(dict): docker-compose.yml file content
    Returns:
        (dict): enriched docker-compose.yml file content
    """
    enriched_compose: dict = compose
    services: list = compose.get('services', {})

    # init an empty enrichment metadata
    enriched_compose["celestical"] = {}

    # extracting default values that could be set here
    def_app_name:str|None = None
    def_base_domain:str|None = None
    if prev_comp is not None and isinstance(prev_comp, dict):
        if "celestical" in prev_comp:
            def_app_name = prev_comp["celestical"].get(
                "name",
                None)
            def_base_domain = prev_comp["celestical"].get(
                "base_domain",
                None)


    # metadata: Appplication name
    # app_name: str = prompt_user(
    #     "Name for your App",
    #     default=def_app_name)
    # app_name = app_name.strip()

    # # TODO clean name of whitespaces
    # enriched_compose["celestical"]["name"] = app_name
    # print_feedback(enriched_compose["celestical"]["name"])

    # metadata: base domain
    base_domain: str = prompt_user(
         "Indicate the base domain for your app?\n"
        +"     (e.g.  myapp.parametry.ai or parametry.ai)",
        default=def_base_domain,
        helptxt="If the base domain is a subdomain, it would constitute "
            +"your base domain, e.g.: app2.celestical.net\n")
    base_domain = base_domain.strip()
    base_domain = base_domain.lower()
    if "http://" in base_domain or "https://" in base_domain:
        base_domain = base_domain.split("://")[-1]
    enriched_compose["celestical"]["base_domain"] = base_domain
    enriched_compose["celestical"]["name"] = base_domain
    print_feedback(enriched_compose["celestical"]["base_domain"])

    # summarizing current services in docker compose file
    msg = "[underline]Here is a quick recap[/underline]\n\n"
    msg += f"Your App: [green]{enriched_compose['celestical']['name']}[/green]\n"
    msg += f"Website: [green]https://{enriched_compose['celestical']['base_domain']}[/green]\n"
    msg += "runs the following services:\n"
    msg += richformat_services(services)
    msg += "\n\n[yellow]We will tag services by usage tag[/yellow]:\n"

    serveme_types = [serv for serv in SERVICE_TYPES]
    help_on_types = "Type the type number or name\n"
    for n in range(len(serveme_types)):
        help_on_types += f"\t{n+1} --> {serveme_types[n]}\n"

    cli_panel(msg+help_on_types)

    counter: int = 1
    for service_name in services:
        # --- display current service name and guessed type
        msg = f"Choose a type for service #{counter} of {len(services)}: "
        msg += f"[yellow]{service_name}[/yellow] --> "

        img_name = services[service_name].get("image", "")
        stype = guess_service_type_by_name(service_name, img_name)
        msg += f" detected type: [purple]{stype}[/purple]"

        # --- ask for a better categorization
        prompt_done = False
        while prompt_done is False:
            type_nbr:str = prompt_user(msg, default=stype, helptxt=help_on_types)
            type_nbr = type_nbr.strip()
            type_nbr = type_nbr.upper()
            prompt_done = True
            match type_nbr:
                case "1":
                    stype = serveme_types[0]
                case "2":
                    stype = serveme_types[1]
                case "3":
                    stype = serveme_types[2]
                case "4":
                    stype = serveme_types[3]
                case "5":
                    stype = serveme_types[4]
                case _:
                    # type_nbr might be something else
                    if type_nbr == "":
                        #stype is already set
                        prompt_done = True
                    elif type_nbr in SERVICE_TYPES:
                        stype = type_nbr
                        prompt_done = True
                    else:
                        prompt_done = False

        enriched_compose["services"][service_name]["celestical_type"] = stype
        print_feedback(
            enriched_compose["services"][service_name]["celestical_type"])

        msg = f"[underline]Public URL[/underline] for service [yellow]{service_name}[/yellow] "
        service_url: str = prompt_user(msg, default="", helptxt="Leave empty if none")

        if service_url != "":
            enriched_compose["services"][service_name]["celestical_url"] = service_url
            print_feedback(
                enriched_compose["services"][service_name]["celestical_url"])

        # TODO get image hash or not
        # enriched_compose["services"][service_name]["celestical_image_hash"] = service_name["image"]
        counter += 1

    save_path: Path = save_yaml(data=enriched_compose, yml_file=ecomp_path)
    return save_path


def define_compose_path(input_path:str) -> Tuple[Path, Path]:
    """ Form the paths to docker-compose file and its enrichment
        according to the type of the input_path

        returns (compose_filepath, enriched_filepath)
    """
    # use current directory if nothing provided
    docker_compose_path = Path.cwd()
    file_dir = Path.cwd()

    if input_path is not None:
        if input_path != "":
            docker_compose_path = Path(input_path)

    # if we get a directory, complete full path
    selected_path = None
    # if input is directory we have to find the file
    if docker_compose_path.is_dir():
        file_dir = docker_compose_path
        # default most used path
        docker_compose_path = file_dir / "docker-compose.yml"

        # Order in these lists is priority, first found first selected
        base_names = ["docker-compose", "compose"]
        extension_names = [".yml", ".yaml"]
        for filename in \
            [base+ext for base in base_names for ext in extension_names]:
            yml_path = file_dir / filename
            if yml_path.is_file():
                docker_compose_path = yml_path
                break

    elif docker_compose_path.is_file():
        # we consider docker_compose_path a valid file set from user
        # We will set the enriched file accordingly
        file_dir = docker_compose_path.parent

    else:
        # provided path does not exist
        return (None, None)

    docker_ecompose_path = file_dir / '.docker-compose-enriched.yml'
    return (docker_compose_path, docker_ecompose_path)


def check_for_enrichment(compose_path:str) -> Tuple[Path, dict, dict]:
    """ Find the compose file in the given folder if it is a folder and decide
    where the enriched compose file will be. Check with the user if enrichment
    is necessary when already present

        Returns: three elements:
         - the path to the found most recent docker-compose or enriched
        file
         - the python dictionary of that most recent compose file content with
           first metadata containing info if user wants to enrich or not.
           From confirmation ask thanks to timestamp comparison.
         - the python dictionary of the enriched file anyway found, so it can be
           used for default values while enrichiing to fasten and ease the
           process.
    """
    compose_path, ecompose_path = define_compose_path(compose_path)

    # in case file name could not be defined
    # (different from file does not exist)
    if compose_path is None or ecompose_path is None or \
        not compose_path.is_file():
        cli_panel("docker-compose.yml or compose.yml files are not valid files:\n"
                 +"Give another docker-compose path on command line: \n"
                 +"\t=> [yellow]celestical deploy "
                 +"/path/to/docker-compose.yml[/yellow]")
        cli_logger.debug("exiting as provided docker compose path is wrong")
        raise typer.Abort()

    # --- selecting most recent valid path
    selected_path = get_most_recent_file(compose_path, ecompose_path)
    prev_compose = read_docker_compose(ecompose_path)

    # --- selected process compose file
    if selected_path.is_file():
        c_dict = read_docker_compose(selected_path)

        # - loading potential environment variables and files
        c_dict = integrate_all_env(c_dict, selected_path.parent)

        # - use the generated image name for images built in the compose file
        c_dict = use_built_image_names(c_dict, selected_path)


        s_info = "\n* Services found in detected docker-compose file: \n"
        s_info += f"\t[green]{selected_path}[/green]\n\n"

        if "services" in c_dict:
            s_info += richformat_services(c_dict["services"])

        if "celestical" in c_dict:
            # s_info += f"\n* [underline]App name[/underline]: " \
            #          +f"[green]{c_dict['celestical']['name']}[/green]\n"
            s_info += f"* [underline]App URL[/underline]: " \
                     +f"[blue]{c_dict['celestical']['base_domain']}[/blue]\n\n"

        cli_panel(s_info)

        # - case where we are on an enriched file
        if "celestical" in c_dict:
            msg = "(Yes) To deploy now | (No) To reset info"
            answer = confirm_user(msg, default=True)

            if answer:
                # Skip enrichment
                c_dict["celestical"]["skip_enrich"] = True
                return ecompose_path, c_dict, prev_compose
            # else will lead to enrichment (reset)
            c_dict["celestical"]["skip_enrich"] = False
            return ecompose_path, c_dict, prev_compose

        # - case where we are on an user compose file
        answer = confirm_user("Continue with this file", default=True)
        if answer:
            return ecompose_path, c_dict, prev_compose

        # - case where we exit for another file
        cli_panel("Give another path on command line: \n"
                 +"\t=> celestical deploy /path/to/docker-compose.yml")
        raise typer.Abort()

    else:
        cli_panel("No docker-compose.yml file was found at:\n"
                 +f"{selected_path}\n\n"
                 +"Give another docker-compose path on command line: \n"
                 +"\t=> [yellow]celestical deploy /path/to/docker-compose.yml[/yellow]")
        cli_logger.debug("exiting as no docker compose file found")
        raise typer.Abort()

    return None, None, {}


def upload_images(app_uuid:uuid.UUID, compose_path:Path|None=None, e_compose:dict|None=None) -> bool:
    """Upload the enriched compose file to the Celestical Cloud."""

    cli_panel("Now uploading your App's images to Celestical")

    if compose_path is not None:
        e_compose = read_docker_compose(compose_path)
    elif e_compose is None:
        return False

    # Build the compressed tar file for services images
    image_names = [
        e_compose["services"][service_name]["image"]
        for service_name in e_compose["services"]
    ]

    image_paths = compress_image(images=image_names, project_name=e_compose["celestical"]["name"])

    api_ires = None
    apiconf = _get_api_with_auth()
    if apiconf is None:
        return False

    with api.ApiClient(apiconf) as api_client:
        app_api = api.AppApi(api_client)
        for ipath in image_paths:
            try:
                with ipath.open(mode="rb") as ipath_desc:
                    # This form won't work:
                    # upfile = {"upload_file": (ipath.name, ipath_desc.read())}
                    upfile = (ipath.name, ipath_desc.read())
                    cli_logger.debug("Making image upload request")
                    # with_http_info returns an HTTP response with status code

                    #start the loading spinner
                    loading_msg = f"your image {str(ipath.name)} is uploading"
                    spinner = Spinner()
                    spinner.start(loading_msg)

                    api_ires = app_api.upload_image_compressed_file_app_app_uuid_upload_image_post_with_http_info(
                        app_uuid=app_uuid,
                        image_file=upfile)

                    #stop the loading spinner
                    spinner.stop()

                    # Print feedback to user
                    if api_ires is not None:
                        msg = " uploaded" \
                              if (api_ires.status_code == 200) \
                              else " not uploaded"
                        msg = str(ipath.name)+msg
                        print_feedback(msg)

            except Exception as oops:
                cli_logger.debug(f"Exception in uploading image {ipath}")
                cli_logger.debug(type(oops))
                print_text(f"Could not upload file {ipath.name}")
                continue

    return True


def upload_compose(compose_path:str, call_nbr:int = 1) -> dict|None:
    """ This function find the compose file and ask the user for enrichment
        unless an enriched file is already present in case user is asked
        if they want to reset the enrichment.

        - compose_path:str: string of the folder to deploy, it should contain
          a docker compose file. It is where the enriched file will be saved
        - call_nbr:str: in case we are missing authentication we are trying to
          login again to get a new token. If that does not work something else
          is going on.
    """
    # --- Find file and verify path and previous enrichment
    ecomp_path, comp_dict, prev_comp = check_for_enrichment(compose_path)

    do_enrich:bool = True
    if "celestical" in comp_dict:
        if "skip_enrich" in comp_dict["celestical"]:
            if comp_dict["celestical"]["skip_enrich"] is True:
                do_enrich = False

    # --- Get info from user to enrich context
    enriched_compose = {}
    if do_enrich:
        enriched_compose_path = enrich_compose(comp_dict, prev_comp, ecomp_path)
        # we reread the compose so that we can audit what is posted
        enriched_compose = read_docker_compose(enriched_compose_path)
    else:
        enriched_compose = comp_dict

    # --- Posting the body package for Compose file
    compose_pack = {}
    compose_pack["enriched_compose"] = enriched_compose
    # optional in case we want to upload compose for later deployment
    compose_pack["deploy"] = True

    apiconf = _get_api_with_auth()
    if apiconf is None:
        return None

    api_response = None
    with api.ApiClient(apiconf) as api_client:
        app_api = api.AppApi(api_client)

        try:
            # App creation with compose (possibly empty) upload
            cli_logger.debug("Preparing compose info to post")
            compose_to_post = Compose.from_dict(compose_pack)

            cli_logger.debug("Making compose info push request")
            api_response = app_api.upload_compose_file_app_compose_post( \
                compose_to_post)

        except UnauthorizedException as oops:
            # Let's try to relog again and relaunch that function
            if call_nbr > 1:
                msg = "[red]Access not authorized for now[/red]\n\n"
                msg += "Make sure a payment method is installed\n"
                msg += f"If problem persists please contact us: {HOTLINE}"
                cli_panel(msg)
                return None
            # else
            cli_panel("Unauthorized access, your token may have expired." \
                      +" (signing out automatically)")
            if not user_login(force_relog=True):
                if not user_login(force_relog=True):
                    print_text("Please start over again checking your credentials carefully.",
                        worry_level="ohno")
                    return None
            call_nbr += 1
            cli_logger.debug(oops)
            return upload_compose(compose_path, call_nbr)
        except Exception as oops:
            print_text("No connection yet possible to deploy your app.")
            cli_logger.error("Error during posting of the enriched compose file")
            cli_logger.error(oops)
            return None

    if (not isinstance(api_response, App)):
        cli_logger.error("API response is not an App.")
        msg = "Try to login again, your token might have expired.\n"
        msg += "--> [underline]celestical login[/underline]"
        cli_panel(msg)
        return None

    # at this point api_response is an App
    if "celestical" in enriched_compose:
        enriched_compose["celestical"]["app_id"] = str(api_response.id)
        save_path: Path = save_yaml(data=enriched_compose, yml_file=ecomp_path)

    return enriched_compose
