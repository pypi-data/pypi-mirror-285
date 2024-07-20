import json5
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import EVMVerifier.certoraContext as Ctx
import EVMVerifier.certoraContextAttribute as Attr
from EVMVerifier.certoraContextClass import CertoraContext
from Shared import certoraUtils as Util

"""
This file is responsible for reading and writing configuration files.
"""

# logger for issues regarding the general run flow.
# Also serves as the default logger for errors originating from unexpected places.
run_logger = logging.getLogger("run")


def current_conf_to_file(context: CertoraContext) -> Dict[str, Any]:
    """
    Saves current command line options to a configuration file
    @param context: context object
    @:return the data that was written to the file (in json/dictionary form)

    We are not saving options if they were not provided (and have a simple default that cannot change between runs).
    Why?
    1. The .conf file is shorter
    2. The .conf file is much easier to read, easy to find relevant arguments when debugging
    3. Reading the .conf file is quicker
    4. Parsing the .conf file is simpler, as we can ignore the null case
    """
    def input_arg_with_value(k: Any, v: Any) -> Any:
        return v is not None and v is not False and k in Attr.all_context_keys()
    context_to_save = {k: v for k, v in vars(context).items() if input_arg_with_value(k, v)}
    all_keys = Attr.all_context_keys()

    context_to_save = dict(sorted(context_to_save.items(), key=lambda x: all_keys.index(x[0])))
    context_to_save.pop('build_dir', None)  # build dir should not be saved, each run should define its own build_dir

    out_file_path = Util.get_last_conf_file()
    run_logger.debug(f"Saving last configuration file to {out_file_path}")
    Ctx.write_output_conf_to_path(context_to_save, out_file_path)

    return context_to_save


def read_from_conf_file(context: CertoraContext, conf_file_path: Optional[Path] = None) -> None:
    """
    Reads data from the configuration file given in the command line and adds each key to the context namespace if the
    key is undefined there. For more details, see the invoked method read_from_conf.
    @param context: A namespace containing options from the command line, if any (context.files[0] should always be a
        .conf file when we call this method)
        :param conf_file_path: Path to the conf file
    """
    if not conf_file_path:
        conf_file_path = Path(context.files[0])
    assert conf_file_path.suffix == ".conf", f"conf file must be of type .conf, instead got {conf_file_path}"

    with conf_file_path.open() as conf_file:
        configuration = json5.load(conf_file, allow_duplicate_keys=False)
        try:
            check_conf_content(configuration, context)
        except Util.CertoraUserInputError as e:
            raise Util.CertoraUserInputError(f"Error when reading {conf_file_path}", e) from None
        context.conf_file = str(conf_file_path)


def check_conf_content(configuration: Dict[str, Any], context: CertoraContext) -> None:
    """
    validating content read from the conf file
    Note: a command line definition trumps the definition in the file.
    If in the .conf file solc is 4.25 and in the command line --solc solc6.10 was given, sol6.10 will be used
    @param configuration: A json object in the conf file format
    @param context: A namespace containing options from the command line, if any
    """
    for option in configuration:
        if hasattr(context, option):
            val = getattr(context, option)
            if val is None or val is False:
                setattr(context, option, configuration[option])
        else:
            raise Util.CertoraUserInputError(f"{option} appears in the conf file but is not a known attribute. ")
    if 'files' not in configuration:
        raise Util.CertoraUserInputError("Mandatory 'files' attribute is missing from the configuration")
    context.files = configuration['files']  # Override the current .conf file
