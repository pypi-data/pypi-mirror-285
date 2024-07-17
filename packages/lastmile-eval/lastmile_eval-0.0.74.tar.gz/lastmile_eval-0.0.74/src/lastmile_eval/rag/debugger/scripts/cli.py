from lastmile_eval.rag.debugger.scripts.util import validate_ui_dependencies

# This is a hack to make sure that the UI dependencies are installed.
# Keep this import and function call at the top of the file.
validate_ui_dependencies()

import logging
import sys

import lastmile_utils.lib.core.api as core_utils
import result
from lastmile_eval.rag.debugger.common.utils import load_dotenv_from_cwd

from result import Err, Ok, Result

from lastmile_eval.rag.debugger.app_utils import LaunchConfig
from lastmile_eval.rag.debugger.server import serve

logging.basicConfig(format=core_utils.LOGGER_FMT)
LOGGER = logging.getLogger()


class CLIConfig(core_utils.Record):
    log_level: str | int = "WARNING"
    # TODO:
    # ragdebugrc_path: str = os.path.join(os.path.expanduser("~"), ".ragdebugrc")


def main() -> int:
    argv = sys.argv
    return main_with_args(argv)


def main_with_args(argv: list[str]) -> int:
    final_result = run_subcommand(argv)
    match final_result:
        case Ok(msg):
            LOGGER.info("Final result: Ok:\n%s", msg)
            return 0
        case Err(e):
            LOGGER.critical("Final result err: %s", e)
            return core_utils.result_to_exitcode(Err(e))


def run_subcommand(argv: list[str]) -> Result[str, str]:
    LOGGER.info("Running subcommand")
    subparser_record_types = {
        "launch": LaunchConfig,
    }
    main_parser = core_utils.argparsify(
        CLIConfig, subparser_record_types=subparser_record_types
    )

    # Try to parse the CLI args into a config.
    cli_config: Result[CLIConfig, str] = core_utils.parse_args(
        main_parser, argv[1:], CLIConfig
    )

    # If cli_config is Ok(), pass its contents to _get_cli_process_result_from_config().
    # Otherwise, short circuit and assign process_result to the Err.
    # Nothing gets mutated except for log level (see inside _get_cli_process_result_from_config()
    process_result = cli_config.and_then(_set_script_state)
    LOGGER.info(f"{process_result=}")

    subparser_name = core_utils.get_subparser_name(main_parser, argv[1:])
    LOGGER.info(f"Running subcommand: {subparser_name}")

    subcommand_config = core_utils.parse_args(
        main_parser, argv[1:], subparser_record_types[subparser_name]
    )
    LOGGER.debug(f"{subcommand_config.is_ok()=}")
    out = result.do(
        _run_servers_with_configs(subcommand_config_ok, cli_config_ok)
        for subcommand_config_ok in subcommand_config
        for cli_config_ok in cli_config
    )
    return out


def _run_servers_with_configs(
    subcommand_config: LaunchConfig, cli_config: CLIConfig
) -> Result[str, str]:
    return serve(subcommand_config)


def _set_script_state(
    cli_config: CLIConfig,
) -> Result[bool, str]:
    """
    1. Set the log level
    2. TODO: Write the default aiconfigrc if it doesn't exist.

    It returns Ok(True) if everything went well. Currently, it never returns Ok(False).
    As usual, we return an error with a message if something went wrong.
    """
    LOGGER.setLevel(cli_config.log_level)

    is_load_dotenv = load_dotenv_from_cwd()
    return Ok(is_load_dotenv)


if __name__ == "__main__":
    retcode: int = main()
    sys.exit(retcode)
