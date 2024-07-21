r"""
Description
===========

The MainParser and ChildParser allows the creation of a fully intermixed argument parser:



Example\s
=========

.. code-block:: python

    # Start the parser so that the following is valid:
    # ./app (...) --cfgfile filename (...)
    main_parser = MainParser()
    main_parser.add_argument("--version", action="version", version="1.2.3")
    main_parser.add_argument("-c", "--cfgfile")
    main_parser.attach()

    # Add the "one" and "two" options:
    subparser = ChildParser(main_parser, "one")
    subparser.add_argument("file")
    subparser.attach()
    subparser = ChildParser(main_parser, "two")
    subparser.add_argument("file")
    subparser.attach()

    # Result (all the following are valid)
    # ./app one --cfgfile filename
    # ./app --cfgfile filename one
    # ./app two --cfgfile filename
    # ./app --cfgfile filename two

Classes
=======

.. autoclass:: BaseParser
   :members:

.. autoclass:: MainParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: ChildParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. seealso::

   Module :py:mod:`argparse`
      Documentation of the :py:mod:`argparse` standard module.

"""

# parse_intermixed_args is available only on python >= 3.7
import argparse
import sys
import typing as t


class BaseParser:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        if sys.version_info[0] == 3 and sys.version_info[1] <= 8:
            self._kwargs.pop("exit_on_error", None)

        self._fg_parser: argparse.ArgumentParser = None
        self._parent = None
        self._finalized: bool = False
        self._subparsers = None
        self._bg_parser: argparse.ArgumentParser = argparse.ArgumentParser(add_help=False)

    def add_argument(self, *args, **kwargs) -> None:
        """
        The add_argument() method attaches individual argument specifications to the parser. It supports positional
        arguments, options that accept values, and on/off flags.
        """
        if self._finalized:
            raise RuntimeError("Cannot add arguments to a parser that has been finalized")
        self._bg_parser.add_argument(*args, **kwargs)

    def set_defaults(self, **kwargs: t.Dict[str, t.Any]) -> None:
        """
        set_defaults() allows some additional attributes that are determined without any inspection of the command line
        to be added
        """
        self._not_finalized_fence()
        self._fg_parser.set_defaults(**kwargs)
        self._bg_parser.set_defaults(**kwargs)

    def _finalized_fence(self) -> None:
        # top parser
        if self._finalized:
            raise RuntimeError("Cannot attach an already finalized parser")
        self._finalized = True

    def _not_finalized_fence(self) -> None:
        # top parser
        if not self._finalized:
            raise RuntimeError("Parser must be finalized for that action")

    def _get_subparsers(self):
        # Called by the child on the parent parser
        self._finalized = True
        if not self._subparsers:
            self._subparsers = self._fg_parser.add_subparsers()
        return self._subparsers

    def _rebuild(self):
        arg_list = self._get_arguments()

        # add dummy positional argument to eat up previous subparsers
        count = max(0, len(arg_list) - 1)
        dummies = argparse.ArgumentParser(add_help=False)
        dummies.add_argument("_imxd_action", nargs=count)

        parents = [dummies]
        parents.extend(arg_list)

        parser = argparse.ArgumentParser(parents=parents)
        return parser


class MainParser(BaseParser):
    """
    Root parser which holds as many child parsers as you wish
    """

    def __init__(
        self,
        prog: t.Optional[t.Union[str, None]] = None,
        usage: t.Optional[t.Union[str, None]] = None,
        description: t.Optional[t.Union[str, None]] = None,
        epilog: t.Optional[t.Union[str, None]] = None,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: t.Optional[t.Union[str, None]] = None,
        argument_default=None,
        conflict_handler: str = "error",
        add_help: t.Optional[bool] = True,
        allow_abbrev: t.Optional[bool] = True,
        exit_on_error: t.Optional[bool] = True,
    ):
        """
        Create a base parser that holds an extra internal argument parser.

        Parameters
        ----------

        prog: dict[str]
            The name of the program (default: sys.argv[0])

        usage: str
            A usage message (default: auto-generated from arguments)

        description: str
            A description of what the program does

        epilog: str
            Text following the argument descriptions

        formatter_class:
            HelpFormatter class for printing help messages. Note: changed from default argparse.HelpFormatter

        prefix_chars: str
            Characters that prefix optional arguments

        fromfile_prefix_chars:
            Characters that prefix files containing additional arguments

        argument_default:
            The default value for all arguments

        conflict_handler: str
            String indicating how to handle conflicts

        add_help: boolean
            Add a -h/-help option

        allow_abbrev: bool
            Allow long options to be abbreviated unambiguously

        exit_on_error: bool
            Determines whether or not ArgumentParser exits with error info when an error occurs
        """
        super().__init__(
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help,
            allow_abbrev=allow_abbrev,
            exit_on_error=exit_on_error,
        )
        #

    def _get_arguments(self) -> t.List:
        """
        Get background parser as a list
        """
        return [self._bg_parser]

    def attach(self) -> None:
        """
        Finalize parser.
        """
        self._finalized_fence()
        self._fg_parser = argparse.ArgumentParser(parents=self._get_arguments(), **self._kwargs)
        self.set_defaults(prog=self._kwargs["prog"])

    def parse_args(self, args: t.List[str] = None, namespace: object = None):
        """
        Convert argument strings to objects and assign them as attributes of the namespace. Return the populated namespace.

        Parameters
        ----------
        args: list[str]
            List of strings to parse. The default is taken from sys.argv.

        namespace: object
            An object to take the attributes. The default is a new empty Namespace object.
        """
        # first pass handles help and invalid command lines
        rv = self._fg_parser.parse_args(args, namespace)
        if "_imxd_parser" not in rv:
            return rv

        # pylint: disable=protected-access
        parser = rv._imxd_parser._rebuild()
        rv = parser.parse_intermixed_args(args, namespace)
        del rv._imxd_action
        return rv


class ChildParser(BaseParser):
    """
    Child parser which holds as many other child parsers as you wish
    """

    def __init__(
        self,
        parent=None,
        prog: t.Optional[t.Union[str, None]] = None,
        usage: t.Optional[t.Union[str, None]] = None,
        description: t.Optional[t.Union[str, None]] = None,
        epilog: t.Optional[t.Union[str, None]] = None,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: t.Optional[t.Union[str, None]] = None,
        argument_default=None,
        conflict_handler: str = "error",
        add_help: t.Optional[bool] = True,
        allow_abbrev: t.Optional[bool] = True,
        exit_on_error: t.Optional[bool] = True,
    ):
        """
        Create a child parser that holds an extra internal argument parser.

        Parameters
        ----------

        parent:
            MainParser or ChildParser this parser depends on.

        prog: dict[str]
            The name of the program (default: sys.argv[0])

        usage: str
            A usage message (default: auto-generated from arguments)

        description: str
            A description of what the program does

        epilog: str
            Text following the argument descriptions

        formatter_class:
            HelpFormatter class for printing help messages. Note: changed from default argparse.HelpFormatter

        prefix_chars: str
            Characters that prefix optional arguments

        fromfile_prefix_chars:
            Characters that prefix files containing additional arguments

        argument_default:
            The default value for all arguments

        conflict_handler: str
            String indicating how to handle conflicts

        add_help: boolean
            Add a -h/-help option

        allow_abbrev: bool
            Allow long options to be abbreviated unambiguously

        exit_on_error: bool
            Determines whether or not ArgumentParser exits with error info when an error occurs
        """
        super().__init__()
        self._kwargs = {
            "prog": prog,
            "usage": usage,
            "description": description,
            "epilog": epilog,
            "formatter_class": formatter_class,
            "prefix_chars": prefix_chars,
            "fromfile_prefix_chars": fromfile_prefix_chars,
            "argument_default": argument_default,
            "conflict_handler": conflict_handler,
            "add_help": add_help,
            "allow_abbrev": allow_abbrev,
            "exit_on_error": exit_on_error,
        }
        if sys.version_info[0] == 3 and sys.version_info[1] <= 8:
            self._kwargs.pop("exit_on_error", None)

        self._parent = parent
        #

    def _get_arguments(self) -> t.List:
        """
        Get recursive arguments as a list
        """
        rv = []
        # pylint: disable=protected-access
        rv.extend(self._parent._get_arguments())
        rv.append(self._bg_parser)
        return rv

    def attach(self) -> None:
        """
        Finalize parser and attach to parent parser
        """
        self._finalized_fence()

        # Get parent subparser, creating it if necessary
        # pylint: disable=protected-access
        parent_subparsers = self._parent._get_subparsers()

        name = self._kwargs.get("prog", "")
        self._fg_parser = parent_subparsers.add_parser(name, parents=self._get_arguments(), **self._kwargs)

        # Set some magic on this parser
        self._fg_parser.set_defaults(_imxd_parser=self)
        self.set_defaults(prog=self._kwargs["prog"])
