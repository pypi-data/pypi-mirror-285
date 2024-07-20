import os
import pathlib
import datetime


def get_version_number():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")


def upload_docker_image(image_name, version_number, destination, hostname):
    image_name = image_name.replace("_", "-")
    # Save the built image file to a tar archive for compression and uploading.
    os.system(
        "docker save {image_name}:{version_number} > {image_name}.tar".format(
            version_number=version_number,
            image_name=image_name,
        )
    )
    # Archive the image file using xzip.
    os.system("xz -9 {image_name}.tar".format(image_name=image_name))
    # Upload the saved image archive into the SSH host.
    os.system(
        "scp {image_name}.tar.xz {hostname}:{destination}/{image_name}.tar.xz".format(
            image_name=image_name,
            destination=destination,
            hostname=hostname,
        )
    )
    # Load the uploaded image archive into the docker image list.
    os.system(
        "ssh {hostname} 'docker load < {destination}/{image_name}.tar.xz'".format(
            image_name=image_name,
            destination=destination,
            hostname=hostname,
        )
    )


def run_docker_container(
    container_name,
    version_number,
    mount=True,
    mount_source="/home/mraUser/online_experiments_data",
    mount_folder="",
    mount_destination="/online_experiments_data",
    restart_policy="always",
    port_mappings=None,
    network_mode=None,
    ssh=False,
    hostname=None,
):
    if ssh and not hostname:
        raise RuntimeError("SSH mode enabled on docker run, but no hostname provided!")

    commands = [
        "docker stop {0}".format(container_name),
        "docker rm {0}".format(container_name),
    ]

    run_args = [
        "docker",
        "run",
        "-d",
        "--restart {0}".format(restart_policy),
        "--name {0}".format(container_name),
        "{1}:{0}".format(version_number, container_name.replace("_", "-")),
    ]

    if mount:
        run_args.insert(
            2,
            '--mount type=bind,source="{0}",target={1}'.format(
                pathlib.Path(mount_source, mount_folder), mount_destination
            ),
        )

    if network_mode:
        run_args.insert(3, "--network {0}".format(network_mode))

    if port_mappings:
        mapping = " ".join(
            [
                "{0}:{1}".format(source_port, destination_port)
                for (source_port, destination_port) in port_mappings.items()
            ]
        )
        run_args.insert(3, "-p {0}".format(mapping))

    print("docker run command:")
    print(run_args)

    commands.append(" ".join(run_args))

    if ssh:
        os.system("ssh {hostname} '{command_string}'".format(hostname=hostname, command_string="; ".join(commands)))
    else:
        for command in commands:
            os.system(command)


def build_docker_container(image_name, version_number):
    os.system("docker build -t {1}:{0} .".format(version_number, image_name.replace("_", "-")))
