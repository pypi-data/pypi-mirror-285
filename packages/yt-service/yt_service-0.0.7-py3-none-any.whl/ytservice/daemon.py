# -*- coding: utf-8 -*-

import os
import plistlib

PREFIX_LABEL = "org.seven"
CMD_LOAD = "launchctl load -w {}"
CMD_UNLOAD = "launchctl unload -w {}"
CMD_LIST = "launchctl list"


def launch_agents() -> str:
    """
    launch agents
    """
    agents = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents")
    if not os.path.exists(agents):
        os.mkdir(agents)
    return agents


def _plist_file(name: str) -> (str, str):
    """
    plist file
    """
    label = "{}.{}".format(PREFIX_LABEL, name)
    plist = os.path.join(launch_agents(), label + ".plist")
    return label, plist


def mac_start(name: str) -> None:
    if not mac_is_install(name=name):
        raise RuntimeError("Not Install")
    running = mac_is_running(name=name)
    if not running:
        _, plist = _plist_file(name=name)
        os.system(CMD_LOAD.format(plist))


def mac_stop(name: str) -> None:
    if not mac_is_install(name=name):
        raise RuntimeError("Not Install")
    running = mac_is_running(name=name)
    if running:
        _, plist = _plist_file(name=name)
        os.system(CMD_UNLOAD.format(plist))


def mac_rm(name: str) -> None:
    """
    mac rm
    """
    if mac_is_install(name=name):
        if mac_is_running(name=name):
            mac_stop(name=name)
        _, plist = _plist_file(name=name)
        os.remove(plist)


def mac_is_install(name: str) -> bool:
    """
    is install
    """
    _, plist = _plist_file(name=name)
    return os.path.exists(plist)


def mac_is_running(name: str) -> bool:
    """
    is running
    """
    l, _ = _plist_file(name=name)
    result = False
    cmd_result = os.popen(cmd=CMD_LIST).readlines()
    if cmd_result and len(cmd_result) > 0:
        for line in cmd_result:
            item = line.strip().split("\t")
            if len(item) == 3:
                pid = item[0].strip()
                label = item[2].strip()
                if l == label and pid != "-":
                    result = int(pid) > 0
    return result


def mac_install(name: str,
                out_path: str,
                error_path: str,
                program_arguments: list = None,
                keep_alive: bool = True,
                run_at_load: bool = True,
                working_dir: str = None,
                environment_variables: dict = None) -> None:
    """
    plist install
    :param name:
    :param program_arguments:
    :param out_path:
    :param error_path:
    :param keep_alive:
    :param run_at_load:
    :param working_dir:
    :return:
    """
    if not name:
        raise ValueError("label empty")
    if not program_arguments:
        raise ValueError("program arguments empty")
    label, plist = _plist_file(name=name)
    if os.path.exists(plist):
        raise RuntimeError("{0} - exists".format(label))

    pl = dict(
        Label=label,
        ProgramArguments=program_arguments,
        KeepAlive=keep_alive,
        RunAtLoad=run_at_load,
        StandardOutPath=out_path,
        StandardErrorPath=error_path
    )
    if working_dir:
        pl["WorkingDirectory"] = working_dir
    if environment_variables:
        pl["EnvironmentVariables"] = environment_variables

    with open(plist, "wb") as f:
        plistlib.dump(pl, f)
