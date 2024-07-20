import platform
import subprocess
import docker
from docker.errors import DockerException, APIError, ImageNotFound
from docker.types import Mount
import os
import json
import argparse
from typing import List
import base64

from . import container_utils

from pyntcli.ui import ui_thread
from pyntcli.analytics import send as analytics
from pyntcli.store import CredStore
from pyntcli.auth.login import PYNT_ID, PYNT_SAAS, PYNT_BUCKET_NAME, PYNT_PARAM1, PYNT_PARAM2

PYNT_DOCKER_IMAGE = "ghcr.io/pynt-io/pynt"


def create_mount(src, destination, mount_type="bind"):
    return Mount(target=destination, source=src, type=mount_type)


class DockerNotAvailableException(Exception):
    pass


class DockerNativeUnavailableException(Exception):
    pass


class ImageUnavailableException(Exception):
    pass


class PortInUseException(Exception):
    def __init__(self, port=""):
        self.message = ui_thread.print(ui_thread.PrinterText("Port: {} already in use, please use a different one".format(port), ui_thread.PrinterText.WARNING))
        super().__init__(self.message)


def get_docker_type_native():
    try:
        version_data = json.loads(subprocess.check_output(["docker", "version", "--format", "{{json .}}"], text=True))
        platform = version_data.get("Client", {}).get("Platform", {})
        analytics.deferred_emit(analytics.DOCKER_PLATFORM, platform)
        return platform.get("Name", "")
    except Exception:
        raise DockerNotAvailableException()


def get_docker_type():
    try:
        c = docker.from_env()
        version_data = c.version()
        platform = version_data.get("Platform")
        analytics.deferred_emit(analytics.DOCKER_PLATFORM, platform)
        if platform and platform.get("Name"):
            return platform.get("Name")

        return ""

    except DockerException:
        raise DockerNotAvailableException()
    except Exception:  # TODO: This is since windows is not behaving nice
        raise DockerNotAvailableException()


class PyntBaseContainer():
    def __init__(self, docker_type, docker_arguments, mounts, environment={}) -> None:
        self.docker_type = docker_type
        self.docker_arguments = docker_arguments
        self.mounts = mounts
        self.environment = environment


class PyntDockerPort:
    def __init__(self, src, dest, name) -> None:
        self.src = src
        self.dest = dest
        self.name = name


def get_container_with_arguments(args: argparse.Namespace, *port_args: PyntDockerPort) -> PyntBaseContainer:
    docker_arguments = []
    ports = {}
    for p in port_args:
        if container_utils.is_port_in_use(p.dest):
            raise PortInUseException(p.dest)
        if "desktop" in get_docker_type().lower():
            ports[str(p.src)] = int(p.dest)
        else:
            docker_arguments.append(p.name)
            docker_arguments.append(str(p.dest))

    if "desktop" in get_docker_type().lower():
        docker_type = PyntDockerDesktopContainer(ports=ports)
    else:
        docker_type = PyntNativeContainer(network="host")

    if "insecure" in args and args.insecure:
        docker_arguments.append("--insecure")

    if "application_id" in args and args.application_id:
        docker_arguments += ["--application-id", args.application_id]

    if "proxy" in args and args.proxy:
        docker_arguments += ["--proxy", args.proxy]

    if "dev_flags" in args:
        docker_arguments += args.dev_flags.split(" ")

    mounts = []
    if "host_ca" in args and args.host_ca:
        ca_name = os.path.basename(args.host_ca)
        docker_arguments += ["--host-ca", ca_name]
        mounts.append(create_mount(os.path.abspath(args.host_ca), "/etc/pynt/{}".format(ca_name)))

    if "transport_config" in args and args.transport_config:
        tc_name = os.path.basename(args.transport_config)
        docker_arguments += ["--transport-config", tc_name]
        mounts.append(create_mount(os.path.abspath(args.transport_config), "/etc/pynt/{}".format(tc_name)))

    if "verbose" in args and args.verbose:
        docker_arguments.append("--verbose")

    creds_path = os.path.dirname(CredStore().file_location)
    mitm_cert_path = os.path.join(creds_path, "cert")
    os.makedirs(mitm_cert_path, exist_ok=True)
    mounts.append(create_mount(mitm_cert_path, "/root/.mitmproxy"))

    env = {PYNT_ID: CredStore().get_tokens(), "PYNT_SAAS_URL": PYNT_SAAS}
    if user_set_all_variables():
        add_env_variables(env)
    return PyntBaseContainer(docker_type, docker_arguments, mounts, env)


def _container_image_from_tag(tag: str) -> str:
    if ":" in tag:
        return tag.split(":")[0]

    return tag


def user_set_all_variables():
    return all([PYNT_BUCKET_NAME, PYNT_PARAM1, PYNT_PARAM2])


def add_env_variables(env: dict):
    env["PYNT_BUCKET_NAME"] = PYNT_BUCKET_NAME
    env["PYNT_PARAM1"] = base64.b64encode(PYNT_PARAM1.encode('utf-8'))
    env["PYNT_PARAM2"] = base64.b64encode(PYNT_PARAM2.encode('utf-8'))


def value_from_environment_variable(key, fallback=""):
    e = os.environ.get(key)

    if e:
        ui_thread.print_verbose(f"Using environment variable {key}={e}")
        return e
    if fallback != "":
        ui_thread.print_verbose(f"Using variable {key}={fallback}")
    return fallback


class PyntContainerNative:
    def __init__(self, image_name, tag, base_container, is_detach=True):
        self.image_name = value_from_environment_variable("IMAGE", image_name)
        self.tag = value_from_environment_variable("TAG", tag)
        self.is_detach = is_detach
        self.mounts = base_container.mounts
        self.env_vars = base_container.environment
        self.base_container = base_container
        self.container_name = ""
        self.system = platform.system().lower()

        self.stdout = None
        self.running = False

    def is_alive(self):
        command = ["docker", "ps", "--filter", f"name={self.container_name}", "--filter", "status=running"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return len(result.stdout.splitlines()) > 1

    def run(self):
        self.running = True
        self.kill_other_instances()

        self.get_image()
        args = self.base_container.docker_arguments if self.base_container.docker_arguments else None
        docker_command = ["docker", "run"]

        if self.is_detach:
            docker_command.append("-d")

        mounts = []
        for mount in self.base_container.mounts:
            mounts.extend(["-v", f"{mount['Source']}:{mount['Target']}"])

        env_vars = []
        for key, value in self.base_container.environment.items():
            env_vars.extend(self.adapt_environment_variable_partial(key, value))

        docker_type_options = []
        for key, value in self.base_container.docker_type.get_arguments().items():
            if key == "ports":
                if isinstance(value, dict):
                    for s, d in value.items():
                        # --publish source:destination for each port
                        docker_type_options.extend([f"-p", f"{s}:{d}"])
            else:
                docker_type_options.extend([f"--{key}={value}"])

        docker_command += mounts
        docker_command += env_vars
        docker_command += docker_type_options
        docker_command += [f"{self.image_name}:{self.tag}"]
        docker_command += args

        command = self.adapt_run_command(docker_command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if stderr:
            print(stderr)

        container_id = stdout.strip()

        if process.returncode and process.returncode != 0:
            raise DockerNativeUnavailableException(f"Unable to perform docker run command, return code: {process.returncode}")

        logs_process = subprocess.Popen(
            ['docker', 'logs', container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        logs_stdout, logs_stderr = logs_process.communicate()

        self.stdout = logs_stdout

    def kill_other_instances(self):
        try:
            ui_thread.print_verbose("Killing other pynt containers if such exist")
            command = ["docker", "ps", "-q", "-f", f"ancestor={self.image_name}:{self.tag}"]
            containers_output = subprocess.check_output(command, text=True)
            if not containers_output:
                return

            container_ids = containers_output.splitlines()
            for container_id in container_ids:
                command = ["docker", "kill", container_id]
                subprocess.run(command)

        except subprocess.CalledProcessError:
            analytics.emit(analytics.ERROR, {"error": "Unable to kill other pynt containers"})
            ui_thread.print(ui_thread.PrinterText("Error: Unable to kill other pynt containers", ui_thread.PrinterText.WARNING))

    def pull_image(self):
        try:
            command = ["docker", "pull", f"{self.image_name}:{self.tag}"]
            subprocess.run(command, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            analytics.emit(analytics.ERROR, {"error": "Unable to pull image from ghcr"})
            ui_thread.print(ui_thread.PrinterText("Error: Docker unable to pull latest Pynt image due to VPN/proxy. If using a mirror for Docker images, visit docs.pynt.io for help.", ui_thread.PrinterText.WARNING))
            return None

    def get_image(self):
        try:
            ui_thread.print(ui_thread.PrinterText("Pulling latest docker image", ui_thread.PrinterText.INFO))
            command = ['docker', 'pull', f'{self.image_name}:{self.tag}']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise ImageUnavailableException(f"Failed to pull image: {stderr.decode().strip()}")

            command = ['docker', 'images', '-q', f'{self.image_name}']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

            if stderr:
                ui_thread.print(ui_thread.PrinterText(f"Error: {stderr}", ui_thread.PrinterText.WARNING))
                raise ImageUnavailableException("Failed to pull image")

            if process.returncode != 0:
                raise ImageUnavailableException("Failed to pull image")

            image_id = stdout.strip()
            return image_id
        except Exception as e:
            raise ImageUnavailableException(f"An error occurred: {str(e)}")

    def stop(self):
        if not self.running:
            return
        self.kill_other_instances()
        self.running = False

    def adapt_run_command(self, docker_command=[]):
        if self.system == "windows":
            return ' '.join(docker_command)
        return docker_command

    def adapt_environment_variable_partial(self, key, value):
        if self.system == "windows":
            return ["-e", f"{key}={json.dumps(value)}"]
        return ["-e", f"{key}={value}"]


class PyntContainerSDK:
    def __init__(self, image_name, tag, base_container, is_detach=True) -> None:
        self.image_name = value_from_environment_variable("IMAGE", image_name)
        self.tag = value_from_environment_variable("TAG", tag)
        self.base_container = base_container
        self.is_detach = is_detach

        self.mounts = base_container.mounts
        self.env_vars = base_container.environment

        self.docker_client: docker.DockerClient = None
        self.container_name = ""
        self.stdout = None
        self.running = False

    def _initialize(self):
        self.docker_client = docker.from_env()
        docker_password = value_from_environment_variable("DOCKER_PASSWORD")
        docker_username = value_from_environment_variable("DOCKER_USERNAME")
        docker_registry = value_from_environment_variable("DOCKER_REGISTRY")
        if docker_password and docker_username and docker_registry:
            self.docker_client.login(username=docker_username, password=docker_password, registry=docker_registry)

    def is_alive(self):
        if not self.docker_client or not self.container_name:
            return False

        l = self.docker_client.containers.list(filters={"name": self.container_name})
        if len(l) != 1:
            return False

        return l[0].status == "running"

    def run(self):
        if not self.docker_client:
            self._initialize()

        self.running = True

        ui_thread.print_verbose("Killing other pynt containers if such exist")
        self.kill_other_instances()

        image = self.get_image()
        ui_thread.print(ui_thread.PrinterText("Docker pull done", ui_thread.PrinterText.INFO))

        args = self.base_container.docker_arguments if self.base_container.docker_arguments else None

        run_arguments = {
            "image": image,
            "detach": self.is_detach,
            "mounts": self.base_container.mounts,
            "environment": self.base_container.environment,
            "stream": True,
            "remove": True,
            "command": args
        }

        run_arguments.update(self.base_container.docker_type.get_arguments())

        ui_thread.print_verbose("Running pynt docker with arguments:\n {}".format(" ".join(args)))
        c = self.docker_client.containers.run(**run_arguments)
        self.container_name = c.name
        self.stdout = c.logs(stream=True)

    def kill_other_instances(self):
        for c in self.docker_client.containers.list():
            if len(c.image.tags) and _container_image_from_tag(c.image.tags[0]) == self.image_name:
                c.kill()

    def pull_image(self):
        try:
            return self.docker_client.images.pull(self.image_name, tag=self.tag)
        except APIError as e:
            analytics.emit(analytics.ERROR, {"error": "Unable to pull image from ghcr: {}".format(e)})
            ui_thread.print(ui_thread.PrinterText("Error: Docker unable to pull latest Pynt image due to VPN/proxy. Visit docs.pynt.io for help using a mirror for Docker images.", ui_thread.PrinterText.WARNING))
            return None

    def get_image(self):
        ui_thread.print(ui_thread.PrinterText("Pulling latest docker image", ui_thread.PrinterText.INFO))
        try:
            image = self.pull_image()
            if not image:
                ui_thread.print(ui_thread.PrinterText("Trying to get pynt local image", ui_thread.PrinterText.INFO))
                image = self.docker_client.images.get(f"{self.image_name}:{self.tag}")
            return image
        except ImageNotFound:
            raise ImageUnavailableException()

    def stop(self):
        if not self.running:
            return
        self.kill_other_instances()
        self.docker_client.close()
        self.docker_client = None
        self.running = False


class PyntContainer:
    def __init__(self, image_name, tag, detach, base_container: PyntBaseContainer, use_native=False) -> None:
        self.use_native = use_native

        if use_native:
            self.client_implementation = PyntContainerNative(image_name=image_name, tag=tag, base_container=base_container, is_detach=detach)
        else:
            self.client_implementation = PyntContainerSDK(image_name=image_name, tag=tag, base_container=base_container, is_detach=detach)

        self.image = image_name
        self.tag = tag
        self.detach = detach
        self.container_name = ""
        self.base_container = base_container
        self.stdout = None

    def kill_other_instances(self):
        self.client_implementation.kill_other_instances()

    def stop(self):
        self.client_implementation.stop()

    def is_alive(self):
        return self.client_implementation.is_alive()

    def pull_image(self):
        return self.client_implementation.pull_image()

    def get_image(self):
        return self.client_implementation.get_image()

    def run(self):
        self.client_implementation.run()
        self.stdout = self.client_implementation.stdout
        PyntContainerRegistry.instance().register_container(self)

    def running(self):
        return self.client_implementation.running


class PyntDockerDesktopContainer:
    def __init__(self, ports) -> None:
        self.ports = ports

    def get_arguments(self):
        return {"ports": self.ports} if self.ports else {}


class PyntNativeContainer:
    def __init__(self, network) -> None:
        self.network = network

    def get_arguments(self):
        return {"network": self.network} if self.network else {}


class PyntContainerRegistry:
    _instance = None

    def __init__(self) -> None:
        self.containers: List[PyntContainer] = []

    @staticmethod
    def instance():
        if not PyntContainerRegistry._instance:
            PyntContainerRegistry._instance = PyntContainerRegistry()

        return PyntContainerRegistry._instance

    def register_container(self, c: PyntContainer):
        self.containers.append(c)

    def stop_all_containers(self):
        for c in self.containers:
            c.stop()
