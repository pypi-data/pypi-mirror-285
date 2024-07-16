import logging
import sys
import re
from functools import lru_cache
from dataclasses import dataclass
from enum import unique
from pathlib import Path
from typing import Optional, List
from Shared import certoraAttrUtil as AttrUtil

from Shared import certoraValidateFuncs as Vf
from Shared import certoraUtils as Util


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

# logger for issues regarding context
context_logger = logging.getLogger("context")


def validate_prover_args(value: str) -> str:

    strings = value.split()
    for arg in ContextAttribute:
        if arg.value.jar_flag is None:
            continue
        for string in strings:

            if string == arg.value.jar_flag:
                # globalTimeout will get a special treatment, because the actual arg is the wrong one
                if arg.value.jar_flag == ContextAttribute.CLOUD_GLOBAL_TIMEOUT.value.jar_flag:
                    actual_arg = ContextAttribute.GLOBAL_TIMEOUT
                else:
                    actual_arg = arg

                flag_name = actual_arg.get_flag()
                if not arg.value.temporary_jar_invocation_allowed:
                    raise Util.CertoraUserInputError(
                        f"Use CLI flag '{flag_name}' instead of 'prover_args' with {string} as value")
    return value


def validate_typechecker_args(value: str) -> str:
    strings = value.split()
    for arg in ContextAttribute:
        if arg.value.typechecker_flag is None:
            continue
        for string in strings:
            if string == arg.value.typechecker_flag:
                raise Util.CertoraUserInputError(f"Use CLI flag '{arg.get_flag()}' "
                                                 f"instead of 'typechecker_args' with {string} as value")
    return value


def parse_struct_link(link: str) -> str:
    search_res = re.search(r'^\w+:([^:=]+)=\w+$', link)
    # We do not require firm form of slot number so we can give more informative warnings
    if search_res is None:
        raise Util.CertoraUserInputError(f"Struct link argument {link} must be of the form contractA:<field>=contractB")
    if search_res[1].isidentifier():
        return link
    try:
        parsed_int = int(search_res[1], 0)  # an integer or a hexadecimal
        if parsed_int < 0:
            raise Util.CertoraUserInputError(f"struct link slot number negative at {link}")
    except ValueError:
        raise Util.CertoraUserInputError(f"Struct link argument {link} must be of the form contractA:number=contractB"
                                         f" or contractA:fieldName=contractB")
    return link


@dataclass
class CertoraArgument(AttrUtil.BaseArgument):
    deprecation_msg: Optional[str] = None
    jar_flag: Optional[str] = None  # the flag that is sent to the jar (if attr is sent to the jar)
    jar_no_value: Optional[bool] = False  # if true, flag is sent with no value
    temporary_jar_invocation_allowed: bool = False  # If true we can call the jar flag without raising an error
    typechecker_flag: Optional[
        str] = None  # the flag that is sent to the typechecker jar (if attr is sent to the typechecker jar)

    def get_dest(self) -> Optional[str]:
        return self.argparse_args.get('dest')


@unique
class ContextAttribute(AttrUtil.BaseAttribute):
    """
    This enum class must be unique. If 2 args have the same value we add the 'flag' attribute to make sure the hash
    value is not going to be the same

    The order of the attributes is the order we want to show the attributes in argParse's help

    """
    FILES = CertoraArgument(
        attr_validation_func=Vf.validate_input_file,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="contract files for analysis, a conf file or SOLANA_FILE.so",
        default_desc="",
        flag='files',
        argparse_args={
            'nargs': AttrUtil.MULTIPLE_OCCURRENCES
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    VERIFY = CertoraArgument(
        attr_validation_func=Vf.validate_verify_attr,
        arg_type=AttrUtil.AttrArgType.STRING,
        help_msg="Path to The Certora CVL formal specifications file. \n\nFormat: "
                 "\n  <contract>:<spec file>\n"
                 "Example: \n  Bank:specs/Bank.spec\n\n"
                 "spec files suffix must be .spec",
        default_desc="",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MSG = CertoraArgument(
        attr_validation_func=Vf.validate_msg,
        help_msg="Add a message description to your run",
        default_desc="No message",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    RULE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=Vf.validate_rule_name,
        jar_flag='-rule',
        help_msg="Verify only the given list of rules/invariants. Asterisks are interpreted as wildcards",
        default_desc="Verifies all rules and invariants",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    EXCLUDE_RULE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=Vf.validate_rule_name,
        jar_flag='-excludeRule',
        help_msg="Filter out the list of rules/invariants to verify. Asterisks are interpreted as wildcards",
        default_desc="Verifies all rules and invariants",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    PROTOCOL_NAME = CertoraArgument(
        help_msg="Add the protocol's name for easy filtering in the dashboard",
        default_desc="The `package.json` file's `name` field if found",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    PROTOCOL_AUTHOR = CertoraArgument(
        help_msg="Add the protocol's author for easy filtering in the dashboard",
        default_desc="The `package.json` file's `author` field if found",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    BUILD_CACHE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        help_msg="Enable caching of the contract compilation process",
        default_desc="Compiles contract source files from scratch each time",
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MULTI_ASSERT_CHECK = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=True,
        jar_flag='-multiAssertCheck',
        help_msg="Check each assertion statement that occurs in a rule, separately",
        default_desc="Stops after a single violation of any assertion is found",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    INDEPENDENT_SATISFY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=False,
        jar_flag='-independentSatisfies',
        help_msg="Check each `satisfy` statement that occurs in a rule while ignoring previous ones",
        default_desc="For each `satisfy` statement, assumes that all previous `satisfy` statements were fulfilled",
        argparse_args={
            'action': AttrUtil.STORE_TRUE,
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SAVE_VERIFIER_RESULTS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=True,
        jar_flag='-saveVerifierResults',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    INCLUDE_EMPTY_FALLBACK = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-includeEmptyFallback',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    RULE_SANITY = CertoraArgument(
        attr_validation_func=Vf.validate_sanity_value,
        help_msg="Select the type of sanity check that will be performed during execution",
        jar_flag='-ruleSanityChecks',
        default_desc="No sanity checks",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --rule_sanity given
            'const': Vf.RuleSanityValue.BASIC.name.lower()  # 'default': when empty --rule_sanity is given
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MULTI_EXAMPLE = CertoraArgument(
        attr_validation_func=Vf.validate_multi_example_value,
        help_msg="Show several counter examples for failed `assert` statements "
                 "and several witnesses for verified `satisfy` statements",
        jar_flag='-multipleCEX',
        default_desc="Shows a single example",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --multi_example given
            'const': Vf.MultiExampleValue.BASIC.name.lower()
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    FUNCTION_FINDER_MODE = CertoraArgument(
        attr_validation_func=Vf.validate_function_finder_mode,
        help_msg="Use `relaxed` mode to increase internal function finders precision, "
                 "but may cause `stack too deep` errors unless using `via-ir`",
        default_desc="Takes less stack space but internal functions may be missed",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SHORT_OUTPUT = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-ciMode',
        help_msg="Reduce verbosity",
        default_desc="",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    NO_CALLTRACE_STORAGE_INFORMATION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-noCalltraceStorageInformation',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    CALLTRACE_REMOVE_EMPTY_LABELS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-calltraceRemoveEmptyLabels',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SEND_ONLY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="'send_only' is deprecated and is now the default. In CI, use 'wait_for_results none' instead",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    WAIT_FOR_RESULTS = CertoraArgument(
        attr_validation_func=Vf.validate_wait_for_results,
        help_msg="Wait for verification results before terminating the run",
        default_desc="Sends request and does not wait for results",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when --wait_for_results was not used
            'const': str(Vf.WaitForResultOptions.ALL)  # when --wait_for_results was used without an argument
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    COMPILATION_STEPS_ONLY = CertoraArgument(
        flag='--compilation_steps_only',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Compile the spec and the code without sending a verification request to the cloud",
        default_desc="Sends a request after source compilation and spec syntax checking",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SOLC = CertoraArgument(
        attr_validation_func=Vf.validate_exec_file,
        help_msg="Path to the Solidity compiler executable file",
        default_desc="Calling `solc`",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    VYPER = CertoraArgument(
        attr_validation_func=Vf.validate_exec_file,
        help_msg="Path to the Vyper compiler executable file",
        default_desc="Calling `vyper`",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_VIA_IR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Pass the `--via-ir` flag to the Solidity compiler",
        default_desc="",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_EXPERIMENTAL_VIA_IR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Pass the `--experimental-via-ir` flag to the Solidity compiler",
        default_desc="",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_EVM_VERSION = CertoraArgument(
        help_msg="Instruct the Solidity compiler to use a specific EVM version",
        default_desc="Uses the Solidity compiler's default EVM version",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_MAP = CertoraArgument(
        attr_validation_func=Vf.validate_solc_map,
        arg_type=AttrUtil.AttrArgType.MAP,
        help_msg='Map contracts to the appropriate Solidity compiler in case not all contract files are compiled '
                 'with the same Solidity compiler version. \n\nCLI Example: '
                 '\n  --solc_map A=solc8.11,B=solc8.9,C=solc7.5\n\nJSON Example: '
                 '\n  "solc_map: {"'
                 '\n    "A": "solc8.11",'
                 '\n    "B": "solc8.9",'
                 '\n    "C": "solc7.5"'
                 '\n  }',
        default_desc="Uses the same Solidity compiler version for all contracts",
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'type': lambda value: Vf.parse_dict('solc_map', value)
            },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    COMPILER_MAP = CertoraArgument(
        attr_validation_func=Vf.validate_solc_map,
        arg_type=AttrUtil.AttrArgType.MAP,
        help_msg='Map contracts to the appropriate compiler in case not all contract files are compiled '
                 'with the same compiler version. \n\nCLI Example: '
                 '\n  --compiler_map A=solc8.11,B=solc8.9,C=solc7.5\n\nJSON Example: '
                 '\n  "compiler_map": {'
                 '\n    "A": "solc8.11", '
                 '\n    "B": "solc8.9", '
                 '\n    "C": "solc7.5"'
                 '\n  }',
        default_desc="Uses the same compiler version for all contracts",
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'type': lambda value: Vf.parse_dict('compiler_map', value)
            },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_ALLOW_PATH = CertoraArgument(
        attr_validation_func=Vf.validate_dir,
        help_msg="Set the base path for loading Solidity files",
        default_desc="Only the Solidity compiler's default paths are allowed",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_OPTIMIZE = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer_or_minus_1,
        help_msg="Tell the Solidity compiler to optimize the gas costs of the contract for a given number of runs",
        default_desc="Uses the Solidity compiler's default optimization settings",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'const': '-1'
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_OPTIMIZE_MAP = CertoraArgument(
        attr_validation_func=Vf.validate_solc_optimize_map,
        arg_type=AttrUtil.AttrArgType.MAP,
        help_msg='Map contracts to their optimized number of runs in case not all contract files are compiled '
                 'with the same number of runs. \n\nCLI Example:'
                 '\n  --solc_optimize_map A=200,B=300,C=200\n\nJSON Example:'
                 '\n  "solc_optimize_map": {'
                 '\n    "A": "200",'
                 '\n    "B": "300",'
                 '\n    "C": "200"'
                 '\n  }',
        default_desc="Compiles all contracts with the same optimization settings",
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'type': lambda value: Vf.parse_dict('solc_optimize_map', value)
            },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    SOLC_ARGS = CertoraArgument(
        attr_validation_func=Vf.validate_solc_args,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    PACKAGES_PATH = CertoraArgument(
        attr_validation_func=Vf.validate_dir,
        help_msg="Look for Solidity packages in the given directory",
        default_desc="Looks for the packages in $NODE_PATH",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    PACKAGES = CertoraArgument(
        attr_validation_func=Vf.validate_packages,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Map packages to their location in the file system",
        default_desc="Takes packages mappings from `package.json` `remappings.txt` if exist, conflicting mappings"
                     " cause the script abnormal termination",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    # once we decide to make this default, add a deprecation message and add the inverse option
    USE_MEMORY_SAFE_AUTOFINDERS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`use_memory_safe_autofinders` is deprecated and is turned on by default. To disable it"
                        " use `no_memory_safe_autofinders`",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    NO_MEMORY_SAFE_AUTOFINDERS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        # This is a hidden flag, the following two attributes are left intentionally as comments to help devs
        # help_msg="Don't instrument internal function finders using memory-safe assembly",
        # default_desc="Uses memory-safe bytecode annotations to identify internal functions",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    DO_NOT_USE_MEMORY_SAFE_AUTOFINDERS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`do_not_use_memory_safe_autofinders` is deprecated, use `no_memory_safe_autofinders` instead",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    FINDER_FRIENDLY_OPTIMIZER = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`finder_friendly_optimizer` is deprecated and is turned on by default. To disable it"
                        " use `strict_solc_optimizer`",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    DISABLE_FINDER_FRIENDLY_OPTIMIZER = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`disable_finder_friendly_optimizer` is deprecated, use `strict_solc_optimizer` instead",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    STRICT_SOLC_OPTIMIZER = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Allow Solidity compiler optimizations that can interfere with internal function finders",
        default_desc="Disables optimizations that may invalidate the bytecode annotations that identify "
                     "internal functions",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    DISABLE_SOLC_OPTIMIZERS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    YUL_ABI = CertoraArgument(
        attr_validation_func=Vf.validate_json_file,
        help_msg="An auxiliary ABI file for yul contracts",
        default_desc="",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=True
    )

    OPTIMISTIC_LOOP = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-assumeUnwindCond',
        jar_no_value=True,
        help_msg="Assume the loop halt conditions hold, after unrolling loops",
        default_desc="May produce a counter example showing a case where loop halt conditions don't hold after "
                     "unrolling",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    LOOP_ITER = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-b',
        help_msg="Set the maximum number of loop iterations",
        default_desc="A single iteration for variable iterations loops, all iterations for fixed iterations loops",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    OPTIMISTIC_HASHING = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Bound the length of data (with potentially unbounded length) to the value given in "
                 "`hashing_length_bound`",
        jar_flag='-optimisticUnboundedHashing',
        default_desc="May show counter examples with hashing applied to data with unbounded length",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    OPTIMISTIC_SUMMARY_RECURSION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Assume the recursion limit of Solidity functions within a summary is never reached",
        default_desc="Can show counter examples where the recursion limit was reached",
        jar_flag='-optimisticSummaryRecursion',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    OPTIMISTIC_FALLBACK = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-optimisticFallback',
        help_msg="Prevent unresolved external calls with an empty input buffer from affecting storage states",
        default_desc="Unresolved external calls with an empty input buffer cause havocs "
                     "that can lead to non-useful counter examples",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SUMMARY_RECURSION_LIMIT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        help_msg="Determine the number of recursive calls we verify "
                 "in case of recursion of Solidity functions within a summary",
        jar_flag='-summaryRecursionLimit',
        default_desc="0 - no recursion is allowed",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    OPTIMISTIC_CONTRACT_RECURSION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Assume the recursion limit is never reached in cases of "
                 "recursion of Solidity functions due to inlining",
        jar_flag='-optimisticContractRecursion',
        default_desc="May show counter examples where the recursion limit is reached",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    CONTRACT_RECURSION_LIMIT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        help_msg="Specify the maximum depth of recursive calls verified for Solidity functions due to inlining",
        jar_flag='-contractRecursionLimit',
        default_desc="0 - no recursion is allowed",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    HASHING_LENGTH_BOUND = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-hashingLengthBound',
        help_msg="Set the maximum length of otherwise unbounded data chunks that are being hashed",
        default_desc="224 bytes (7 EVM words)",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    METHOD = CertoraArgument(
        jar_flag='-method',
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Filter methods to be verified by their signature",
        default_desc="Verifies all public or external methods. In invariants pure and view functions are ignored",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    CACHE = CertoraArgument(
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SMT_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_positive_integer,
        jar_flag='-t',
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    LINK = CertoraArgument(
        attr_validation_func=Vf.validate_link_attr,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Link a slot in a contract with another contract. \n\nFormat: "
                 "\n  <Contract>:<field>=<Contract>\n\n"
                 "Example: \n  Pool:asset=Asset\n\n"
                 "The field asset in contract Pool is a contract of type Asset",
        default_desc="The slot can be any address, often resulting in unresolved calls and havocs that lead to "
                     "non-useful counter examples",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,  # not sure, better be careful
        disables_build_cache=False
    )

    ADDRESS = CertoraArgument(
        attr_validation_func=Vf.validate_address,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Set the address of a contract to a given address",
        default_desc="Assigns addresses arbitrarily",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    STRUCT_LINK = CertoraArgument(
        attr_validation_func=Vf.validate_struct_link,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Link a slot in a struct with another contract. \n\nFormat: "
                 "\n  <Contract>:<slot#>=<Contract>\n"
                 "Example: \n  Bank:0=BankToken Bank:1=LoanToken\n\n"
                 "The first field in contract Bank is a contract of type BankToken and the second of type LoanToken ",
        default_desc="The slot can be any address, often resulting in unresolved calls and havocs that lead to "
                     "non-useful counter examples",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,  # carefulness
        disables_build_cache=False
    )

    PROTOTYPE = CertoraArgument(
        attr_validation_func=Vf.validate_prototype_attr,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Set the address of the contract's create code. \n\nFormat: "
                 "\n  <hex address>=<Contract>\n\n"
                 "Example: \n  0x3d602...73\n\n"
                 "Contract Foo will be created from the code in address 0x3d602...73",
        default_desc="Calls to the created contract will be unresolved, causing havocs that may lead to "
                     "non-useful counter examples",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    DYNAMIC_BOUND = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-dynamicCreationBound',
        help_msg="Set the maximum amount of times a contract can be cloned",
        default_desc="0 - calling create/create2/new causes havocs that can lead to non-useful counter examples",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DYNAMIC_DISPATCH = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-dispatchOnCreated',
        help_msg="Automatically apply the DISPATCHER summary on newly created instances",
        default_desc="Contract method invocations on newly created instances "
                     "causes havocs that can lead to non-useful counter examples",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    AUTO_NONDET_DIFFICULT_INTERNAL_FUNCS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`auto_nondet_difficult_internal_funcs` is deprecated, use `nondet_difficult_funcs` instead",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    NONDET_DIFFICULT_FUNCS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-autoNondetDifficultInternalFuncs',
        help_msg="Summarize as NONDET all value-type returning difficult internal functions which are view or pure",
        default_desc="Tries to prove the unsimplified code",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    AUTO_NONDET_MINIMAL_DIFFICULTY = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        deprecation_msg="`auto_nondet_minimal_difficulty` is deprecated, use `nondet_minimal_difficulty` instead",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    NONDET_MINIMAL_DIFFICULTY = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-autoNondetMinimalDifficulty',
        help_msg="Set the minimal `difficulty` threshold for summarization by `nondet_difficult_funcs`",
        default_desc="50",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DEBUG = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--debug',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SHOW_DEBUG_TOPICS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--show_debug_topics',  # added to prevent dup with DEBUG
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DEBUG_TOPICS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    VERSION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Show the Prover version",
        default_desc="",
        argparse_args={
            'action': AttrUtil.VERSION,
            'version': 'This message should never be reached'
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    JAR = CertoraArgument(
        attr_validation_func=Vf.validate_jar,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    JAVA_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'action': AttrUtil.APPEND,
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    BUILD_ONLY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--build_only',  # added to prevent dup with NO_COMPARE
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    BUILD_DIR = CertoraArgument(
        attr_validation_func=Vf.validate_build_dir,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DISABLE_LOCAL_TYPECHECKING = CertoraArgument(
        flag='--disable_local_typechecking',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    NO_COMPARE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--no_compare',  # added to prevent dup with BUILD_ONLY
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    EXPECTED_FILE = CertoraArgument(
        attr_validation_func=Vf.validate_optional_readable_file,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    QUEUE_WAIT_MINUTES = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--queue_wait_minutes',  # added to prevent dup with MAX_POLL_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MAX_POLL_MINUTES = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--max_poll_minutes',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    LOG_QUERY_FREQUENCY_SECONDS = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--log_query_frequency_seconds',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MAX_ATTEMPTS_TO_FETCH_OUTPUT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--max_attempts_to_fetch_output',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DELAY_FETCH_OUTPUT_SECONDS = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--delay_fetch_output_seconds',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    PROCESS = CertoraArgument(
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'default': 'emv'
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    """
    The content of prover_args is added as is to the jar command without any flag. If jar_flag was set to None, this
    attribute would have been skipped altogether. setting jar_flag to empty string ensures that the value will be added
    to the jar as is
    """
    PROVER_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=validate_prover_args,
        help_msg="Send flags directly to the Prover",
        default_desc="",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    TYPECHECKER_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=validate_typechecker_args,
        help_msg="Send flags directly to the CVL typechecker",
        default_desc="",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    COMMIT_SHA1 = CertoraArgument(
        attr_validation_func=Vf.validate_git_hash,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DISABLE_AUTO_CACHE_KEY_GEN = CertoraArgument(
        flag='--disable_auto_cache_key_gen',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    USE_PER_RULE_CACHE = CertoraArgument(
        attr_validation_func=Vf.validate_false,
        jar_flag='-usePerRuleCache',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    UNUSED_SUMMARY_HARD_FAIL = CertoraArgument(
        attr_validation_func=Vf.validate_on_off,
        jar_flag='-unusedSummaryHardFail',
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MAX_GRAPH_DEPTH = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-graphDrawLimit',
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    TOOL_OUTPUT = CertoraArgument(
        attr_validation_func=Vf.validate_tool_output_path,
        jar_flag='-json',
        argparse_args={
            'action': AttrUtil.UniqueStore,
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    CLOUD_GLOBAL_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_cloud_global_timeout,
        jar_flag='-globalTimeout',
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    GLOBAL_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-userGlobalTimeout',
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    INTERNAL_FUNCS = CertoraArgument(
        attr_validation_func=Vf.validate_json_file,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=True  # prefer to be extra careful with this rare option
    )

    COINBASE_MODE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-coinbaseFeaturesMode',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    RUN_SOURCE = CertoraArgument(
        attr_validation_func=Vf.validate_run_source,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    ASSERT_AUTOFINDER_SUCCESS = CertoraArgument(
        flag="--assert_autofinder_success",
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    CONTRACT_COMPILER_SKIP_SEVERE_WARNING_AS_ERROR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="`contract_compiler_skip_severe_warning_as_error` is deprecated. "
                        "Use `ignore_solidity_warnings` instead",
        affects_build_cache_key=True,
        disables_build_cache=False,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    IGNORE_SOLIDITY_WARNINGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Ignore all Solidity compiler warnings",
        default_desc="Treats certain severe Solidity compiler warnings as errors",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    PROVER_VERSION = CertoraArgument(
        attr_validation_func=Vf.validate_prover_version,
        help_msg="Use a specific Prover revision",
        default_desc="Uses the latest public Prover version",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    SERVER = CertoraArgument(
        attr_validation_func=Vf.validate_server_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    # resource files are string of the form <label>:<path> the client will add the file to .certora_sources
    # and will change the path from relative/absolute path to
    PROVER_RESOURCE_FILES = CertoraArgument(
        attr_validation_func=Vf.validate_resource_files,
        jar_flag='-resourceFiles',
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    TEST = CertoraArgument(
        attr_validation_func=Vf.validate_test_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=False
    )

    COVERAGE_INFO = CertoraArgument(
        attr_validation_func=Vf.validate_coverage_info,
        jar_flag='-coverageInfo',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --coverage_info given
            'const': Vf.CoverageInfoValue.BASIC.name.lower()  # 'default': when empty --coverage_info is given
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    FE_VERSION = CertoraArgument(
        attr_validation_func=Vf.validate_fe_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    JOB_DEFINITION = CertoraArgument(
        attr_validation_func=Vf.validate_job_definition,
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    MUTATION_TEST_ID = CertoraArgument(
        flag='--mutation_test_id',  # added to prevent dup with CONF_OUTPUT_FILE
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    ALLOW_SOLIDITY_CALLS_IN_QUANTIFIERS = CertoraArgument(
        flag='--allow_solidity_calls_in_quantifiers',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    PARAMETRIC_CONTRACTS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=Vf.validate_contract_name,
        jar_flag='-contract',
        help_msg="Filter the set of contracts whose functions will be verified in parametric rules/invariants",
        default_desc="Verifies all functions in all contracts in the file list",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    # something is definitely under-tested here, because I changed this to take
    # a string instead of list of strings and everything just passed!
    ASSERT_CONTRACTS = CertoraArgument(
        attr_validation_func=Vf.validate_assert_contracts,
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND,
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    BYTECODE_JSONS = CertoraArgument(
        attr_validation_func=Vf.validate_json_file,
        arg_type=AttrUtil.AttrArgType.LIST,
        jar_flag='-bytecode',
        help_msg="List of EVM bytecode JSON descriptors",
        default_desc="",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        },
        affects_build_cache_key=True,
        disables_build_cache=True
    )

    BYTECODE_SPEC = CertoraArgument(
        attr_validation_func=Vf.validate_spec_file,
        jar_flag='-spec',
        help_msg="Spec to use for the provided bytecodes",
        default_desc="",
        argparse_args={
            'action': AttrUtil.UniqueStore
        },
        affects_build_cache_key=True,
        disables_build_cache=True
    )

    # used by certoraMutate, ignored by certoraRun
    MUTATIONS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.MAP,
        flag='--mutations',  # added to prevent dup with GAMBIT
        argparse_args={
            'action': AttrUtil.NotAllowed
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    PRECISE_BITWISE_OPS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Show precise bitwise operation counter examples. Models mathints as unit256 that may over/underflow",
        default_desc="May report counterexamples caused by incorrect modeling of bitwise operations,"
                     " but supports unbounded integers (mathints)",
        jar_flag='-useBitVectorTheory',
        jar_no_value=True,
        temporary_jar_invocation_allowed=True,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    DISABLE_INTERNAL_FUNCTION_INSTRUMENTATION = CertoraArgument(
        flag='--disable_internal_function_instrumentation',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=True,
        disables_build_cache=True
    )

    GROUP_ID = CertoraArgument(
        attr_validation_func=Vf.validate_uuid,
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    FOUNDRY_TESTS_MODE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-foundry',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        },
        affects_build_cache_key=False,
        disables_build_cache=False
    )

    def validate_value(self, value: str, cli_flag: bool = True) -> None:
        if self.value.attr_validation_func is not None:
            try:
                self.value.attr_validation_func(value)
            except Util.CertoraUserInputError as e:
                msg = f'{self.get_flag()}: {e}'
                if cli_flag and isinstance(value, str) and value.strip()[0] == '-':
                    flag_error = f'{value}: Please remember, CLI flags should be preceded with double dashes. ' \
                                 f'{Util.NEW_LINE}For more help run the tool with the option --help'
                    msg = flag_error + msg
                raise Util.CertoraUserInputError(msg) from None

    def get_conf_key(self) -> str:
        dest = self.value.get_dest()
        return dest if dest is not None else self.get_flag().lstrip('--')

    def __str__(self) -> str:
        return self.name.lower()


@lru_cache(maxsize=1, typed=False)
def all_context_keys() -> List[str]:
    return [attr.get_conf_key() for attr in ContextAttribute]
