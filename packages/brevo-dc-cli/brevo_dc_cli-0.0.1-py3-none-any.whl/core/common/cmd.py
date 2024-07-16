import subprocess

from core.common import log


def _run_with_result(cmd: str, quiet: bool) -> None:
    if not quiet:
        log.cmd(cmd)

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output and not quiet:
            log.info(output.strip().decode("utf-8"))

    returncode = process.poll()
    if returncode:
        raise Exception()


def _run_without_result(cmd: str, quiet: bool) -> any:
    if not quiet:
        log.cmd(cmd)

    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if not quiet:
        log.info(result.stdout.strip())  # Strip to get rid of trailing newlines

    return result


def run_without_result(cmd: str) -> any:
    return _run_without_result(cmd, False)


def run_without_result_quiet(cmd: str) -> any:
    return _run_without_result(cmd, True)


def run_with_result(cmd: str) -> any:
    return _run_with_result(cmd, False)


def run_with_result_quiet(cmd: str) -> any:
    return _run_with_result(cmd, True)
