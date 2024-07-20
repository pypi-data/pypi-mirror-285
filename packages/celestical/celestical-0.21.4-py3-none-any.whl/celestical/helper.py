"""Helper functions for the celestical app"""
import string
import json
import yaml
from pathlib import Path
import typer


from prettytable import PrettyTable, ALL
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from celestical.configuration import get_batch_mode,cli_logger

console = Console()


# For each service type there is a list of keywords to detect them
SERVICE_TYPES = {
    "FRONTEND": ["web", "www", "frontend", "traefik", "haproxy", "apache", "nginx"],
    "API": ["api", "backend", "service", "node"],
    "DB": ["database", "redis", "mongo", "mariadb", "postgre"],
    "BATCH": ["process", "hidden", "compute"],
    "OTHER": []
}


# Building a table in the terminal
def create_empty_table(columns_labels):
    """Create an empty table with specified columns."""
    pt = PrettyTable()

    # Set the field names (columns)
    pt.field_names = columns_labels

    return pt


def add_row_to_table(table, row_dict):
    """Add a row to the table based on a dictionary."""
    if set(row_dict.keys()) != set(table.field_names):
        raise ValueError("Row dictionary keys do not match table columns.")
    table.add_row([row_dict[col] for col in table.field_names])


def cli_create_table(data: dict) -> Table:
    """Create a table from a dictionary.
    Params:
        data(dict): dictionary to be displayed
    Returns:
        (Table): table object
    """
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Key", style="dim")
    table.add_column("Value")

    for key, value in data.items():
        table.add_row(str(key), str(value))

    return table


def cli_panel(message: str, _type="info", _title:str="Celestical Message", batch:bool=get_batch_mode()) -> None:
    """Display a message in a panel.
    Params:
        message(str): message to be displayed
    Returns:
        None
    """

    if batch:
        return

    # Note: here is hwo to join *args
    # buffer = "\n".join(str(arg) for arg in args)

    if _type == "info":
        title = _title
        panel = Panel(message, title=f"[bold purple]{title}[/bold purple]",
                    border_style="purple",
                    expand=True,
                    title_align='left')
    elif _type == "error":
        title = "Celestical CLI Error"
        panel = Panel(message, title=f"[bold red]{title}[/bold red]",
            border_style="red",
            expand=True,
            title_align='left')


    console.print(panel)


def save_json(data: dict, batch:bool=get_batch_mode()) -> bool:
    """Helper function to save the complete stack info.
    Params:
        data(dict): complete info about the stack (name, compose ..)
    Returns:

    """
    if "name" not in data:
        return False

    json_file = f'stack_{data["name"]}.json'
    try:
        with open(json_file, 'w') as jfile:
            json.dump(data, jfile, indent=4)
    except Exception as oops:
        if not batch:
            print_text(f"Error: JSON file could not be saved f'stack_{data['name']}.json'")
        cli_logger.debug(oops)
        return False

    return True


def save_yaml(data: dict, yml_file:Path = None, batch:bool=get_batch_mode()) -> Path|None:
    """Helper function to save the complete stack info.
    Params:
        data(dict): complete info about the stack (name, compose ..)
        yml_file(Path):  Path where to save the file
    Returns:

    """
    #yml_file = "docker-compose.yml"
    if yml_file is None:
        yml_file = Path("./.docker-compose-enriched.yml")

    try:
        with yml_file.open(mode='w') as yfile:
            yaml.dump(data, yfile, default_flow_style=False)
        if not batch:
            print_text(f"YAML file created successfully: [green]{yml_file}[/green]")

    except Exception as eoops:
        msg = f'Error: Unable to save data to {yml_file}'
        cli_logger.error(msg)
        cli_logger.error(eoops)
        return None

    # return the Path object of the saved file
    return Path(yml_file)


def print_nested_dict(dictionary: dict, batch:bool=get_batch_mode()):
    """Print a nested dictionary in a readable format."""
    if batch:
        return
    for key, value in dictionary.items():
        if isinstance(value, dict):
            print_nested_dict(value)
        else:
            print(f"{key}: {value}")


def print_feedback(used_input:str, batch:bool=get_batch_mode()):
    """ Show users what they have input """
    if batch:
        return
    console.print(f" :heavy_check_mark: - {used_input}")


def print_help(help_text: str, batch:bool=get_batch_mode()):
    """ Show users a help text """
    if batch:
        return
    console.print(" [dodger_blue3]<:information:>[/dodger_blue3] "
                +f"[gray30]{help_text}[/gray30]")


def prompt_user(prompt: str,
                default:str=None,
                helptxt:str="",
                batch:bool=get_batch_mode()) -> str:
    """Prompt the user for input.
    Params:
        prompt(str): the prompt text invitation
    Returns:
        str: the user input

    """
    if batch:
        return default

    more_help = ""
    if helptxt != "":
        if len(helptxt) <= 20:
            more_help = f" [gray30]({helptxt})[/gray30]"
        else:
            more_help = " [gray30](type ? for more help)[/gray30]"
    resp = Prompt.ask(f"\n [green_yellow]===[/green_yellow] {prompt}{more_help}", default=default)

    if resp is None:
        resp = ""

    if resp == "?":
        print_help(helptxt)
        return prompt_user(prompt, default, helptxt)

    return resp


def confirm_user(prompt: str, default:bool = True, batch:bool=get_batch_mode()) -> bool:
    """Prompt the user for yes no answer.
    Params:
        prompt(str): the prompt text invitation
    Returns:
        bool: the user confirmation
    """
    if batch:
        return default

    confirmation:bool = Confirm.ask(f"\n === {prompt} ", default=default)
    if confirmation is None:
        confirmation = False
    return confirmation


def print_text(text: str, worry_level="chill", batch:bool=get_batch_mode()):
    """Print text to the CLI.
        Params:
            text(str): the text to print
            worry_level(str): a level of worries that would change the color; chill, oops, ohno
        Returns:
            str: the text to print
    """
    if batch:
        return

    msg = f"{text}"
    if worry_level == "oops":
        msg = f"[orange]{text}[/orange]"
    elif worry_level == "ohno":
        msg = f"[red]{text}[/red]"

    # add prefix
    msg = " --- " + msg

    return console.print(msg)


def guess_service_type_by_name(service_name: str, img_name:str=""):
    """ Quick guess of service type
    """

    if len(service_name) == 0:
        return ""

    service_name = service_name.lower()

    for stype in SERVICE_TYPES:
        for guesser in SERVICE_TYPES[stype]:
            if guesser in service_name:
                return stype

    if img_name != "":
        img_name = img_name.lower()
        for stype in SERVICE_TYPES:
            for guesser in SERVICE_TYPES[stype]:
                if guesser in img_name:
                    return stype

    # if nothing found
    return "OTHER"


def get_most_recent_file(file1:Path,
                         file2:Path) -> Path:
    """ Will compare modification time between file1 and file2
        and return most recent one.
        If no file exist

    Params:
        - file1(str): file Path
        - file2(str): file Path
    """
    # --- cover cases if one or both are null
    if file1 is None:
        if file2 is None:
            return None
        else:
            return file2
    elif file2 is None:
        return file1
        # else keep going

    # --- select last modified or file1
    selected_path = file1
    ftime1 = 1.0
    if file1.is_file():
        ftime1 = file1.stat().st_mtime

    ftime2 = 0.0
    if file2.is_file():
        ftime2 = file2.stat().st_mtime

    if ftime2 > ftime1:
        selected_path = file2

    return selected_path


def dict_to_list_env(d_in:dict) -> list:
    env_list = []
    for key in d_in:
        env_list.append(key+"="+str(d_in[key]))
    return env_list


def extract_all_dollars(str_in:str) -> dict:
    """ Extract all dollar variables names from the string

    Returns:
        A dictionary that has  pure variable names as keys
        as they would be found defined in an shell env or .env file
        and they representation in strings as $variables or ${variables}.

    """
    # - split the strings and manage where to start
    splits = str_in.strip() # we dont need whitespaces

    if len(splits) <= 1:
        # we need at least 2 characters to work out at least one $variable
        return {}

    s_idx = 1
    if splits[0] == '$':
        # use first split, so start at index 0
        s_idx = 0

    splits = str_in.split("$")
    if len(splits) <= 1:
        return {}

    used_vars = {}
    accepted_chars = string.ascii_letters + string.digits + "_"
    # - each split start with a variable or '{'
    for spp in splits[s_idx:]:
        var = ""
        if len(spp) > 1:
            if spp[0] == '{':
                # get all up to next first '}'
                idx = spp.find('}')
                if idx > 1:
                    var = spp[1:idx]
                    used_vars[var] = "${"+var+"}"
                # else not adding the var.
            else:
                for char in spp:
                    if char in accepted_chars:
                        var += char
                    else:
                        # stop at first unaccepted char
                        break
                if len(var) >= 1:
                    used_vars[var] = "$"+var

    return used_vars
