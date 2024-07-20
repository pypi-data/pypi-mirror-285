import sys
import traceback
from typing import Callable

from .argparser import ArgParser
from .command import Command
from .exceptions import CommandException
from .interface import Interface
from .utils import validate_type_hints

class SingleCommand:

	def __init__(self, error_handler: Callable[[Exception], None] = None):
		self.__error_handler = error_handler
		self.__command = None

	def use(self):
		def dec(func: Callable) -> Callable:
			if self.__command is not None:
				raise CommandException("You can't use more than one command with SingleCommand")
			validate_type_hints(func)
			self.__command = Command(("__main__",), func)
			return func
		return dec

	def process(self, argv: list[str] = None):
		if argv is None:
			argv = sys.argv[1:]
		if len(argv) == 1 and argv[0] in ("--help", "-help", "-h", "--h"):
			Interface.command_usage(self.__command)
			return
		try:
			args, kwargs = ArgParser.parse(argv, self.__command)
			self.__command.func(*args, **kwargs)
		except CommandException as e:
			print("\n" + str(e))
			Interface.command_usage(self.__command)
		except Exception as e:
			print("\n" + traceback.format_exc())
			if isinstance(self.__error_handler, Callable):
				self.__error_handler(e)
