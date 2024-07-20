""" Handling all the local docker functionalities
"""
import os
from pathlib import Path
import shutil
from typing import Tuple

import docker
import gzip
from tqdm import tqdm
from prettytable import PrettyTable, ALL
import typer
from celestical.configuration import cli_logger
from celestical.helper import print_text, confirm_user


def _build_unix_socket(socket_path: Path) -> str:
    return 'unix://' + str(socket_path.resolve())


def _connect_docker_colima() -> docker.DockerClient:
    """ Try to establish client connection with colima
    """
    current_ctx = docker.context.Context.load_context(
        docker.context.api.get_current_context_name())
    if current_ctx is None:
        return None
    url = current_ctx.endpoints["docker"]["Host"]
    return docker.DockerClient(base_url=url)


def get_docker_client():
    """ Returns a docker client taken from local environment """
    client = None
    try:
        cli_logger.debug(f"Searching docker API client from_env()")
        client = docker.from_env()
    except Exception as oops:
        err_msg = "Could not connect to the docker service. Is it really running?"
        cli_logger.debug(err_msg)
        cli_logger.error(oops)
        client = None

    # alternative to finding docker 
    if client is None:
        try:
            cli_logger.debug(f"Searching docker API from system socket.")
            client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        except Exception as oops:
            cli_logger.error(oops)
            client = None

    if client is None:
        try:
            cli_logger.debug(f"Searching docker API from userspace socket.")
            user_tilde = Path("~")
            user_home = user_tilde.expanduser()
            socket_path = user_home / ".docker/run/docker.sock"
            client = docker.DockerClient(base_url=_build_unix_socket(socket_path))
        except Exception as oops:
            cli_logger.error(oops)
            client = None

    # alternative to finding docker on Mac or Linux running Colima
    if client is None:
        try:
            cli_logger.debug(f"Searching docker API client via context (Colima)")
            client = _connect_docker_colima()
        except Exception as oops:
            cli_logger.error(oops)
            client = None

    return client


def get_image_hash(image_name_tag:str) -> str|None:
    """ Get the hash for a certain docker image name and tag.

        Params:
            image_name_tag(str): docker tag of the image to extract hash from
        Returns:
    """
    client = get_docker_client()
    if client is None:
        # Something weird happened with Docker connection
        return None
    image = client.images.get(image_name_tag)
    if image is None:
        return None
    return image.id


def get_ports(image_id:str,
              docker_client:any=None,
              proto:str="tcp") -> str:
    """ Get ports from containers created from the specified image.
        else get the ExposedPorts info from the image itself.

        Params:
            image_id(str): should the string hash of the image
            docker_clienti(any): a docker client
            proto(str): ports for a that specific protocol, by default 'tcp'

        Returns:
            a string for a joint list of ports
    """
    if docker_client is None:
        docker_client = get_docker_client()
        if docker_client is None:
            return ""
        # else continue

    ports = set()

    # Checking from containers
    for container in docker_client.containers.list(all=True):
        if container.image.id == image_id:
            port_data = container.attrs['HostConfig']['PortBindings']
            if port_data:
                for port, bindings in port_data.items():
                    # get only the port number, not the protocol
                    ports.add(str(port.split('/')[0]))

    # Checking from listed images
    if len(ports) == 0:
        try:
            img = docker_client.images.get(image_id)
            for tcpport in [str(attr).split("/")[0]
                            for attr in
                            img.attrs["Config"]["ExposedPorts"]
                            if "tcp" in attr]:
                ports.add(tcpport)
        except Exception as oops:
            # The image_id is not found
            # The ports set remains empty and that's all ok.
            cli_logger.debug(oops)

    return ",".join(sorted(ports))


def list_local_images() -> PrettyTable:
    """List all docker images locally available with port information.

    Returns:
        PrettyTable of formatted table of docker images
    """
    docker_client = get_docker_client()
    if docker_client == None:
        return None

    table = PrettyTable()
    table.field_names = ["Image ID", "Image Name", "Tags", "Ports"]
    table.hrules = ALL  # Add horizontal rules between rows

    images = []
    terminal_width = 100
    try:
        terminal_width, _ = shutil.get_terminal_size()
        images = docker_client.images.list()
    except Exception as whathappened:
        cli_logger.error(whathappened)
        return table

    # Adjust column widths based on the terminal width
    # divide by 2 for two lines
    id_width = max(len(image.id) for image in images) // 2 + 1
    name_width = max(len(image.tags[0].split(':')[0])
                     if image.tags
                     else 0 for image in images)
    # divide by 2 to leave space for the Ports column
    tags_width = (terminal_width - id_width - name_width - 7) // 2
    ports_width = tags_width
    table.align["Image ID"] = "l"
    table.align["Image Name"] = "l"
    table.align["Tags"] = "l"
    table.align["Ports"] = "l"
    table._max_width = {
        "Image ID": id_width,
        "Image Name": name_width,
        "Tags": tags_width,
        "Ports": ports_width}

    for image in images:
        # Split the Image ID into two lines
        half_length = len(image.id) # // 2
        formatted_id = f'{image.id[:half_length]}\n{image.id[half_length:]}'
        # Extract image name from the tags
        image_name = image.tags[0].split(':')[0] if image.tags else 'N/A'
        # Get ports
        ports = get_ports(image.id, docker_client)
        table.add_row([formatted_id, image_name, ', '.join(image.tags), ports])

    return table


def compress_image(images: str|list[str], project_name: str) -> list[Path]:
    """Compress a Docker image.

    Params:
        images: string or list of strings of image full tag names
                as they should appear in the "image" field of each service
        project_name: a string given to name the project, usually the base
                domain name
    Returns:
        A list of path to gzipped images to be uploaded
    """

    image_names = []
    gz_paths = []

    # --- Getting docker client
    client = get_docker_client()
    if client is None:
        cli_logger.debug(f"Docker client could not be found.")
        return gz_paths

    # --- preparing save directory
    save_path = Path(f"/tmp/celestical/{project_name}/")
    # Create the save_path directory and any necessary parent directories
    save_path.mkdir(parents=True, exist_ok=True)

    # --- preparing list of images, or of 1 image
    if isinstance(images, str):
        image_names = [images]
    else:
        image_names = images

    # --- Compressing all images in different gzips
    for image_name in image_names:
        escaped_image_name = image_name.replace('/', '__')
        escaped_image_name = escaped_image_name.replace(':', '_-_')
        gz_filename = save_path / f'{escaped_image_name}.tar.gz'
        gz_filename_local = Path(f'{escaped_image_name}.tar.gz')

        # Step 0: Prompt user for confirmation before proceeding with
        # a new compression
        if not gz_filename.is_file():
            if gz_filename_local.is_file():
                gz_filename = gz_filename_local

        if gz_filename.is_file():
            if not confirm_user(f"[yellow]{image_name}[/yellow] already prepared,"
                                +f"\n\trenew and overwrite {gz_filename} ?",
                                default=False):
                print_text(f" * Ok, using ready file: {gz_filename}\n")
                gz_paths.append(gz_filename)
                continue

        # Step 1: Calculate the total size of the image
        # for chunk in client.images.get(image).save(named=True):
        #     tar_file.write(chunk)
        print_text(f"Working on {image_name}...")
        img = None
        try:
            cli_logger.debug(f"Using docker client to image.get: {image_name}")
            img = client.images.get(image_name)
        except Exception as oops:
            cli_logger.debug(oops)
            img = None

        if img is None:
            msg = (
                f"Image {image_name} not found for project: {project_name}. If "
                "this image is built in the compose file, please run "
                "'docker compose build' first."
            )
            print_text(msg,
                       worry_level="ohno")
            cli_logger.debug(msg)
            continue

        cli_logger.debug(f"Checking Image Size: {img}")
        image_data = img.save(named=True)
        total_size = sum(len(chunk) for chunk in image_data)
        total_size_mb = total_size / (1024 * 1024)

        print_text(f"Image Tag Found: {image_name}"
                   +f"\n\timage size: {total_size_mb:.2f} MB"
                   +f"\n\tsaving in: {save_path}"
                   +f"\n\tas file name: {gz_filename}")

        # Reset the image data iterator
        image_data = img.save(named=True)

        # Save the Docker image to a gzip file with a progress bar
        print_text(f"Exporting compressed image (gzip) to {gz_filename} ...")
        with gzip.open(gz_filename, 'wb') as gz_file:
            with tqdm(total=total_size,
                      unit='B',
                      unit_scale=True,
                      desc="exporting") as pbar:
                # Read, compress, and write data in chunks
                for chunk in image_data:
                    gz_file.write(chunk)
                    pbar.update(len(chunk))

        gz_paths.append(gz_filename)
        print_text(f"[green]succesfully prepared[/green]: {gz_filename}")

    return gz_paths
