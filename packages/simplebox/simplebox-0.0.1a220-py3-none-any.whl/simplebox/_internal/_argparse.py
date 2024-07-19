#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sys
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, _SubParsersAction

from simplebox.config.log import LogConfig, LogLevel
from simplebox.config.property import PropertyConfig
from simplebox.config.rest import RestConfig

__all__ = ['init']

_level_choices = LogLevel.get_keys()


class BaseArgParse(metaclass=ABCMeta):

    @abstractmethod
    def parser(self):
        """
        parser args and execute action.
        :return:
        """


def _set_value(o, args):
    prefix = f"{o.__class__.__name__}__"
    for attr in o.__dict__:
        name = attr[len(prefix) - 1:]
        if hasattr(args, name):
            setattr(o, attr, getattr(args, name))


class __SimpleboxArgParse:

    def __init__(self):
        self.__parser = ArgumentParser(prog="simplebox",
                                       usage="python xxx.py --simplebox [logconfig|restconfig|propconfig] --[option]=value",
                                       add_help=True,
                                       description="When the command line starts, "
                                                   "the configuration value of the simplebox.config module is provided."
                                                   "use 'python -m simplebox.config.show', can show all config.")
        self.__switch = ArgumentParser(prog="simplebox",
                                       usage="python xxx.py --simplebox [logconfig|restconfig|propconfig] --[option]=value",
                                       add_help=True,
                                       description="When the command line starts, "
                                                   "the configuration value of the simplebox.config module is provided."
                                                   "use 'python -m simplebox.config.show', can show all config.")
        self.__switch.add_argument("--simplebox", action="store_true", default=False,
                                   help="Whether to enable the simplebox option or not, "
                                        "the specified must be displayed before the simplebox command can be resolved. "
                                        "To avoid conflicts with command-line commands of other frameworks, "
                                        "do not use them with other command-line frameworks.")
        self.__subparsers = self.__parser.add_subparsers()

    def parser(self):
        args = self.__switch.parse_known_args()[0]
        if not args.simplebox:
            return
        for config in BaseArgParse.__subclasses__():
            config(self.__subparsers).parser()
        common = CommonConfigParser(self.__parser)
        common.parser()
        all_args = sys.argv[1:]
        if "--simplebox" in all_args:
            all_args.remove("--simplebox")
        while all_args:
            args, tmp_all_args = self.__parser.parse_known_args(all_args)
            if set(tmp_all_args[:]) == set(all_args[:]):
                return
            all_args = tmp_all_args[:]
            if 'help' in args and args.help:
                self.__parser.print_help()
            common.exec(args)
            if "func" in args:
                args.func(args)


class CommonConfigParser:

    def __init__(self, parser: ArgumentParser):
        self.__parser = parser

    def parser(self):
        self.__parser.add_argument("--json-ensure-ascii", action='store_true', default=False,
                                   help="set global json.dumps ensure_ascii=True, default ensure_ascii=False")

    @staticmethod
    def exec(args):
        if not args.json_ensure_ascii:
            json.encoder.encode_basestring_ascii = json.encoder.encode_basestring


class LogConfigParser(BaseArgParse):

    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("logconfig", usage="logconfig --[dir|level|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--dir", type=str, default=LogConfig.dir,
                                   help="The directory where the log is saved, the current working directory is "
                                        "the default directory.")
        self.__parser.add_argument("--level",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level,
                                   help="log level")
        self.__parser.add_argument("--level-file",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level_file,
                                   help="The filter level of the log when it is saved to a file.")
        self.__parser.add_argument("--level-console",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level_console,
                                   help="The filter level of the log when it is output to console.")
        self.__parser.add_argument("--format",
                                   type=str,
                                   default=LogConfig.format,
                                   help="Log output format.")
        self.__parser.add_argument("--coding", type=str, default=LogConfig.coding, help="Log encode code.")
        self.__parser.add_argument("--name", type=str, default=LogConfig.name,
                                   help="The name of the file when the log is exported to the file. "
                                        "The .log suffix is added by default")
        self.__parser.add_argument("--rotating-when",
                                   type=str,
                                   choices=['S', 'M', 'H', 'D', 'W', 'midnight'],
                                   default=LogConfig.rotating_when,
                                   help="Specifies the time unit for log file rotation. S: Second\nM: Minutes\nH: "
                                        "Hour\nD: Days Day\nW: Week day (0 = Monday)(0-6)\nmidnight: Roll over at "
                                        "midnight, default.\nwhen cut_mode = 0 used.")
        self.__parser.add_argument("--max-bytes", type=int, default=LogConfig.max_bytes,
                                   help="Specifies the file size of the cut log.")
        self.__parser.add_argument("--delay", action="store_true", default=LogConfig.delay,
                                   help="If the default mode is append, and if the delay is true, the file will "
                                        "not be opened until the emitting method is executed. By default, "
                                        "the log file can grow indefinitely.")
        self.__parser.add_argument("--cut-mode",
                                   type=int,
                                   choices=[1, 2],
                                   default=LogConfig.cut_mode,
                                   help="Cutting mode, 1. Cut by time. 2. Cut by file size.")
        self.__parser.add_argument("--backup-count", type=int, default=LogConfig.backup_count,
                                   help="Maximum number of backup files.")
        self.__parser.add_argument("--off-banner", action="store_true", default=LogConfig.off_banner,
                                   help="Turn off the simplebox label and configuration information at startup")
        self.__parser.add_argument("--off-file", action="store_true", default=LogConfig.off_file,
                                   help="It will not be output to a file.")
        self.__parser.add_argument("--off-console", action="store_true", default=LogConfig.off_console,
                                   help="It will not be output to console.")
        self.__parser.add_argument("--off", action="store_true", default=LogConfig.off, help="Close all log.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(LogConfig, args)


class RestConfigParser(BaseArgParse):
    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("restconfig", usage="restconfig --[allow-redirection|encoding|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--allow-redirection", action="store_true", default=RestConfig.allow_redirection,
                                   help="Allow automatic redirects.")
        self.__parser.add_argument("--check-status", action="store_true", default=RestConfig.check_status,
                                   help="After the HTTP request is complete, check whether the http status is 2xx.")
        self.__parser.add_argument("--encoding", type=str, default=RestConfig.encoding,
                                   help="encode code.")
        self.__parser.add_argument("--http-log-level", type=str,
                                   choices=_level_choices,
                                   default=RestConfig.allow_redirection,
                                   help="This value is set only for the log of the REST module, if it is set.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(RestConfig, args)


class PropertyConfigParser(BaseArgParse):
    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("propconfig", usage="propconfig --[allow-redirection|encoding|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--resources-dir", type=str, default=PropertyConfig.resources,
                                   help="Set the directory of the resource file.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(PropertyConfig, args)


def init():
    try:
        __SimpleboxArgParse().parser()
    except SystemExit:
        pass
