# Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import inspect
import json
import logging
import os
import typing
from kfsfstr import kfsfstr
from kfslog  import kfslog


def force_input(prompt: str, inputs_allowed: list[str]=["y", "n"], tries_max: int=-1, match_case_sensitive: bool=False) -> str:
    """
    Forces user to input a string from a list of allowed strings. If case_sensitive is false, input matching is case-insensitive but case of inputs_allowed is returned. If user input is not in inputs_allowed and tries_max has been exhausted, raises ValueError.

    Arguments:
    - prompt: message to (repeatedly) display to user prompting for input
    - input_allowed: list of allowed user input
    - tries_max: maximum number of tries allowed before raising ValueError, -1 for infinite
    - match_case_sensitive: input evaluation case-sensitive or not

    Returns:
    - user_input_normalised: input string from inputs_allowed that user input matched

    Raises:
    - ValueError: user input is not in input_allowed and tries_max has been exhausted
    """

    input_allowed_matched: str  # entry from inputs_allowed that matched user input
    logger: logging.Logger      # logger
    try_current: int=0          # try current
    user_input: str             # user input


    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside kfs
    else:                                       # if no root logger defined:
        logger=kfslog.setup_logging("kfs")      # use kfs default format


    while try_current!=tries_max:   # as long as tries not exhausted: prompt for input
        try_current+=1              # increment try_current
        logger.info(prompt)         # prompt user for input
        user_input=input()          # get user input

        if user_input in inputs_allowed:                                                                                                # try to find match case-sensitive and prefer that
            input_allowed_matched=user_input
            break
        elif match_case_sensitive==False and user_input.casefold() in [input_allowed.casefold() for input_allowed in inputs_allowed]:   # if no match case-sensitive found and match case-insensitive allowed: fallback to try to find match case-insensitive
            input_allowed_matched=next(input_allowed for input_allowed in inputs_allowed if input_allowed.casefold()==user_input.casefold())
            break

        if try_current!=tries_max:  # if no match and not last try: try again
            logger.warning(f"Input \"{user_input}\" is invalid. Trying again...")
            continue
        else:                       # if no match and last try: error
            logger.error(f"Input \"{user_input}\" is invalid. Giving up.")
            raise ValueError(f"Error in {force_input.__name__}{inspect.signature(force_input)}: Input \"{user_input}\" is invalid. Giving up.")

    return input_allowed_matched


def load_config(env: bool=True, config_filepaths: list[str]|None=["./.env", "./config/config.json"], config_default: dict[str, typing.Any]={}, setting_None_ok: bool=False) -> dict[str, typing.Any]:
    """
    Tries to load config with the name of the config_default's keys. Multiple sources can be used and will be prioritised accordingly:
    1. if env is True: passed environemental variables from os.environ
    2. if config_filepath is not None: config from file at filepath with decreasing priority

    If any setting is still None after all sources have been tried and setting_None_ok is false, it is considered undefined and a ValueError is raised.
    If any setting is undefined and none of the enabled filepaths exist, creation of a default config file at the highest priority filepath will be offered using config_default's values.
    Depending on the file extension, the loaded data is stored differently, either using the whole dictionary or only using key "content". See argument config_default for details, same rules apply.

    Arguments:
    - config_default: defaults to use for creation of a default config file, depending on file extension interpreted differently:
        - .env: whole dictionary is used
        - .json: whole dictionary is used unless only key "content" is present, then only its value is used. This makes it possible to support other top level json data types than dict.
        - default: only key "content"'s raw value is used, all other keys are ignored
    - env: use passed environmental variables from os.environ?
    - config_filepath: filepath to config files or None if unused, formats depending on file extension, unformatted formats like .txt save raw string content from file in key "content"
    - setting_None_ok: allow settings to be None or require to be set?

    Returns:
    - config: loaded config, same keys as config_default

    Raises:
    - KeyError: config_default is missing key "content" while trying to save raw string content
    - ValueError: After going through all enabled sources, a setting is still None and setting_None_ok is false.
    """

    config: dict[str, typing.Any]={key: None for key in config_default.keys()}  # loaded config, initialised empty with same keys as config_default
    sources_loaded: list[str]=[]                                                # sources loaded successfully


    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside kfs
    else:                                       # if no root logger defined:
        logger=kfslog.setup_logging("kfs")      # use kfs default format

    if env==False and (config_filepaths==None or len(config_filepaths)==0): # if no source enabled: error
        logger.error(f"No config source is enabled. Loading config is impossible.")
        raise ValueError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: No config source is enabled. Loading config is impossible.")


    if env==True:
        config.update({k: v for k, v in _load_env().items() if k in config.keys() and config[k]==None}) # update config with environmental variables, only overwrite if key already exists and value is still None
        sources_loaded.append("environmental variables")                                                # log success

    if config_filepaths!=None and len(config_filepaths)!=0:
        for config_filepath in config_filepaths:
            try:
                config.update({k: v for k, v in _load_config_file(config_filepath).items() if k in config.keys() and config[k]==None})  # update config with config file, only overwrite if key already exists and value is still None
            except (FileNotFoundError, IsADirectoryError, OSError):                                                                     # if fails: ignore source
                pass
            else:
                sources_loaded.append(f"\"{config_filepath}\"")                                                                         # log success
    if 1<=len(sources_loaded):                                                                                                          # if source loaded: log
        logger.info(f"Loaded config from: {", ".join(sources_loaded)}")

    for k, v in config.items():
        if v==None:                                 # if setting is still None: do not convert data type
            continue
        try:
            config[k]=type(config_default[k])(v)    # convert data types to match data types given in config_default
        except TypeError:                           # not using dict comprehension to enable proper error messages here
            logger.warning(f"Converting data type of setting \"{k}\" from \"{type(v)}\" to \"{type(config_default[k])}\" failed. Using raw value: {v}")
    logger.debug(config)


    if any(v==None for v in config.values())==True and setting_None_ok==False:  # if any setting is still None and not allowed to be None: error
        logger.error(f"After going through all enabled sources, settings {[k for k, v in config.items() if v==None]} are still None and setting_None_ok is false.")

        if config_filepaths!=None and 1<=len(config_filepaths) and all([os.path.exists(config_filepath)==False for config_filepath in config_filepaths])==True: # if a file source is enabled and no files at set filepaths exist: offer creation of default config file at highest priority filepath using config_default's values
            match force_input(f"Would you like to create a default \"{config_filepaths[0]}\"? (y/n)"):
                case "y":
                    try:
                        _create_default_file(config_filepaths[0], config_default)                                                                               # create default config file at highest priority filepath using config_default's values
                    except OSError:                                                                                                                             # if creating fails: error, if file already exists error because it should have been checked before
                        pass
                case "n":
                    pass

        raise ValueError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: After going through all enabled sources, settings {[k for k, v in config.items() if v==None]} are still None and setting_None_ok is false.")

    return config

def _load_env() -> dict[str, typing.Any]:
    """
    Loads the passed environmental variables from os.environ and returns them as a dictionary.

    Returns:
    - passed environmental variables from os.environ
    """

    config: dict[str, typing.Any]   # passed environmental variables


    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside kfs
    else:                                       # if no root logger defined:
        logger=kfslog.setup_logging("kfs")      # use kfs default format


    logger.debug(f"Loading environmental variables...")
    config=dict(os.environ) # load environmental variables
    logger.debug(f"\rLoaded environmental variables.")
    logger.debug(config)

    return config


def _load_config_file(config_filepath: str) -> dict[str, typing.Any]:
    """
    Loads a config file from the specified filepath and returns its content as a dictionary.

    Arguments:
    - config_filepath: filepath to config file, interprets data depending on file extension, unformatted formats like .txt save raw string content from file in key "content"

    Returns:
    - config_filecontent: content of config file as a dictionary

    Raises:
    - FileNotFoundError: config_filepath does not exist
    - IsADirectoryError: config_filepath is a directory
    - OSError: loading config_filepath failed
    """

    config: dict[str, typing.Any]   # config file
    defaulted: bool=False           # defaulted to forwarding raw string content?


    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside kfs
    else:                                       # if no root logger defined:
        logger=kfslog.setup_logging("kfs")      # use kfs default format

    if os.path.exists(config_filepath)==False:  # if config file does not exist: error
        logger.warning(f"Loading \"{config_filepath}\" failed, because it does not exist. Source will be skipped.")
        raise FileNotFoundError(f"Warning in {load_config.__name__}{inspect.signature(load_config)}: Loading \"{config_filepath}\" failed, because file does not exist. Source will be skipped.")
    if os.path.isdir(config_filepath)==True:    # if config file is a directory: error
        logger.warning(f"Loading \"{config_filepath}\" failed, because it is a directory. Source will be skipped.")
        raise IsADirectoryError(f"Warning in {load_config.__name__}{inspect.signature(load_config)}: Loading \"{config_filepath}\" failed, because it is a directory. Source will be skipped.")


    logger.debug(f"Loading \"{config_filepath}\"...")
    try:
        with open(config_filepath, "rt", encoding="utf8") as config_file:                                                                                                               # read file
            match os.path.basename(config_filepath).rsplit(".", 1)[-1]:                                                                                                                 # parse file content
                case "env":
                    config={line.strip(" ").split("=")[0]: line.strip(" ").split("=")[1] for line in config_file.readlines() if "=" in line and line.strip(" ").startswith("#")==False} # parse env
                case "json":
                    config=json.loads(config_file.read())                                                                                                                               # parse json
                    if type(config)!=dict:                                                                                                                                              # if json is not dict:
                        config={"content": config}                                                                                                                                      # wrap in dict to match other formats
                case "token" | "txt":
                    config={"content": config_file.read()}                                                                                                                              # parse raw string
                case _:
                    defaulted=True                                                                                                                                                      # defaulted to forwarding raw string content
                    config={"content": config_file.read()}                                                                                                                              # parse raw string
    except OSError as e:                                                                                                                                                                # write to log, then forward exception
        logger.warning(f"\rLoading \"{config_filepath}\" failed with {kfsfstr.full_class_name(e)}. Source will be skipped.")
        raise
    else:
        if defaulted==False:
            logger.debug(f"\rLoaded \"{config_filepath}\".")
        else:                   # if defaulted to forwarding raw string content: warn
            logger.warning(f"\rLoaded \"{config_filepath}\", but custom behaviour for file extension \"{os.path.basename(config_filepath).rsplit(".", 1)[-1]}\" is not implemented. Defaulted to forwarding content unchanged into key \"content\".")
        logger.debug(config)

    return config


def _create_default_file(config_filepath: str, config_default: dict[str, typing.Any]) -> None:
    """
    Creates a default config file at the specified filepath using config_default.

    Arguments:
    - config_default: defaults to use for creation of a default config file, unformatted file formats like .txt require key "content"
    - config_filepath: filepath to config file, formats depending on file extension, unformatted formats like .txt save raw string value from key "content" in file

    Raises:
    - FileExistsError: config_filepath already exists
    - KeyError: config_default is missing key "content" while trying to save raw string content
    - OSError: creating config_filepath failed
    """

    defaulted: bool=False   # defaulted to forwarding raw string content?


    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside kfs
    else:                                       # if no root logger defined:
        logger=kfslog.setup_logging("kfs")      # use kfs default format

    if os.path.exists(config_filepath)==True:   # if config filepath already exists: error
        logger.error(f"Creating \"{config_filepath}\" is not possible, because it already exists.")
        raise FileExistsError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: Creating \"{config_filepath}\" is not possible, because it already exists.")


    logger.info(f"Creating default \"{config_filepath}\"...")
    try:
        if os.path.dirname(config_filepath)!="":
            os.makedirs(os.path.dirname(config_filepath), exist_ok=True)                    # create directories
        with open(config_filepath, "wt", encoding="utf8") as config_file:                   # create file
            match os.path.basename(config_filepath).rsplit(".", 1)[-1]:                     # fill with default content
                case "env":
                    config_file.write("\n".join([f"{k}={v}" for k, v in config_default.items()]))
                case "json":
                    if list(config_default.keys())==["content"]:                            # if only key is "content":
                        config_file.write(json.dumps(config_default["content"], indent=4))  # unwrap content, save that as json, for top level data type support other than dict
                    else:                                                                   # if normal json:
                        config_file.write(json.dumps(config_default, indent=4))             # save normally as json
                case "token" | "txt":
                    config_file.write(config_default["content"])
                case _:
                    defaulted=True                                                          # defaulted to forwarding raw string content
                    config_file.write(config_default["content"])
    except KeyError:
        logger.error(f"\rCreating default \"{config_filepath}\" failed, because config_default is missing key \"content\".")
        raise
    except OSError as e:
        logger.error(f"\rCreating default \"{config_filepath}\" failed with {kfsfstr.full_class_name(e)}.")
        raise
    else:
        if defaulted==False:
            logger.info(f"\rCreated default \"{config_filepath}\".")
        else:                                                                               #  if defaulted to forwarding raw string content: warn
            logger.warning(f"Created default \"{config_filepath}\", but custom behaviour for file extension \"{os.path.basename(config_filepath).rsplit(".", 1)[-1]}\" is not implemented. Defaulted to forwarding content unchanged from key \"content\".")

    return