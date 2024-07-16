import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from functools import partial

import lastmile_utils.lib.core.api as core_utils
from result import Err, Ok, Result

LOGGER = logging.getLogger(__name__)


# TODO unhardcode level and format
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")


@dataclass(frozen=True)
class RunUserLLMScriptconfig:
    executable: str
    timeout_s: int


def _run_subprocess_print_and_capture_output(
    cmd: list[str], stdin: str, timeout_s: int
) -> tuple[list[str], list[str], int | None, bool]:
    """
    Run the subprocess and capture both stdout and stderr
    as they are output line by line.
    If process times out, returncode will be None.
    Out: (stdout, stderr, returncode, is_timeout)"""

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # os.set_blocking(proc.stdin.fileno(), False)  # type: ignore

    proc.stdin.write(stdin.encode())  # type: ignore
    proc.stdin.close()  # type: ignore

    os.set_blocking(proc.stdout.fileno(), False)  # type: ignore
    os.set_blocking(proc.stderr.fileno(), False)  # type: ignore

    start = time.time()
    timeout_ts = start + timeout_s

    now = start

    lines_stdout: list[str] = []
    lines_stderr: list[str] = []

    while now < timeout_ts:
        poll = proc.poll()
        line_out = proc.stdout.readline()  # type: ignore
        line_err = proc.stderr.readline()  # type: ignore
        if line_out:
            print(line_out.decode().strip())
            lines_stdout.append(line_out.decode())

        if line_err:
            sys.stderr.write(line_err.decode().strip())
            lines_stderr.append(line_err.decode())

        if poll is not None:
            print(f"{poll=}")
            break

        now = time.time()

    poll = proc.poll()

    is_timeout = poll is None

    return lines_stdout, lines_stderr, poll, is_timeout


# TODO: we can return None and just print any errors/timeouts,
# or we can return debug info. TBD (@ryan)
def run_user_llm_script(
    config: RunUserLLMScriptconfig, prompt: str
) -> Result[str, str]:
    try:
        (
            stdout,
            stderr,
            exitcode,
            is_timeout,
        ) = _run_subprocess_print_and_capture_output(
            [config.executable, prompt],
            prompt,
            config.timeout_s,
        )
        LOGGER.debug(f"{stdout=}, {stderr=}, {exitcode=}, {is_timeout=}")
        if is_timeout or exitcode is None or exitcode != 0:
            error_msg = (
                f"Error: {is_timeout=}, {exitcode=}, {stdout=}, {stderr=}"
            )
            LOGGER.error(error_msg)
            return Err(error_msg)
        else:
            return Ok("\n".join(stdout))
    except Exception as e:
        return core_utils.ErrWithTraceback(e)


# Example usage
if __name__ == "__main__":
    config = RunUserLLMScriptconfig(
        executable="../../examples/rag_debugger/run_llm.py",
        timeout_s=2,
    )

    runner = partial(run_user_llm_script, config)
    prompts = [
        "The sky is blue.",
        "The sky is red.",
    ]

    for prompt in prompts:
        llm_response = runner(prompt)
        if llm_response.is_ok():
            print(f"Response: {llm_response.ok()}")
        else:
            print(f"Error info: {llm_response.err()}")
        print("\n\n")
