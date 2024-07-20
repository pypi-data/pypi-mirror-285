import time
import socket
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
import webbrowser
import json
import pyntcli.log.log as log

from pyntcli.commands.static_file_extensions import STATIC_FILE_EXTENSIONS
from pyntcli.pynt_docker import pynt_container
from pyntcli.ui import report
from pyntcli.transport import pynt_requests

logger = log.get_logger()


def is_http_handler(url):
    path = url.split("/")[-1]
    for ext in STATIC_FILE_EXTENSIONS:
        if ext in path:
            return False

    return True


def find_open_port() -> int:
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]


HEALTHCHECK_TIMEOUT = 60
HEALTHCHECK_INTERVAL = 0.1
GOT_INITIAL_HEALTHCHECK_MESSAGE = "Got initial pynt server health check"


def wait_for_healthcheck(address):
    start = time.time()
    while start + HEALTHCHECK_TIMEOUT > time.time():
        try:
            res = pynt_requests.get(address + "/healthcheck")

            logger.debug("Health check response: {}".format(res.status_code))
            if res.status_code == 418:
                return
        except:
            time.sleep(HEALTHCHECK_INTERVAL)

    logger.debug("Health check timed out!")
    raise TimeoutError()


def get_user_report_path(path, file_type):
    path = Path(path)
    if path.is_dir():
        return os.path.join(path, "pynt_results_{}.{}".format(int(time.time()), file_type))

    return os.path.join(str(path.parent), path.stem + ".{}".format(file_type))


class HtmlReportNotCreatedException(Exception):
    pass


class SomeFindingsOrWarningsException(Exception):
    pass


@contextmanager
def create_default_file_mounts(args):
    html_report_path = os.path.join(tempfile.gettempdir(), "results.html")
    json_report_path = os.path.join(tempfile.gettempdir(), "results.json")

    if "reporters" in args and args.reporters:
        html_report_path = os.path.join(os.getcwd(), "pynt_results.html")
        json_report_path = os.path.join(os.getcwd(), "pynt_results.json")

    mounts = []
    with open(html_report_path, "w", encoding="utf-8"), open(json_report_path, "w", encoding="utf-8"):
        mounts.append(pynt_container.create_mount(json_report_path, "/etc/pynt/results/results.json"))
        mounts.append(pynt_container.create_mount(html_report_path, "/etc/pynt/results/results.html"))

    yield mounts

    if os.stat(html_report_path).st_size == 0:
        raise HtmlReportNotCreatedException()

    webbrowser.open("file://{}".format(html_report_path))

    if os.stat(html_report_path).st_size > 0:
        report.PyntReporter(json_report_path).print_summary()

    check_for_findings_or_warnings(args, json.load(open(json_report_path)))


def check_for_findings_or_warnings(args, json_report):
    security_tests = json_report.get("securityTests", {})
    findings = security_tests.get("Findings", 0)
    warnings = security_tests.get("Warnings", 0)

    if "return_error" in args and args.return_error != "never" and findings != 0:
        raise SomeFindingsOrWarningsException()

    if "return_error" in args and args.return_error == "all-findings" and warnings != 0:
        raise SomeFindingsOrWarningsException()
