
import re
from types import GenericAlias
from typing import Type

from .command import Command
from .exceptions import CommandException
from .utils import get_signature

class ArgParser:

	@classmethod
	def parse(cls, argv: list[str], command: Command) -> tuple[list, dict]:
		positionals, keyword, defaults, spec = get_signature(command.func)
		# values specified by keywords
		values: dict = {}
		# list of positional values
		free_values: list[str] = []

		# parse command argv
		pointer = 0
		while pointer < len(argv):
			if alias := cls.__match_argument_name(argv[pointer]):
				argument = command.aliases.get(alias, alias)
				if argument in values:
					raise CommandException(f"Invalid usage: duplicate argument {argument}")
				typehint = spec.annotations.get(argument)
				if isinstance(typehint, GenericAlias):
					typehint = typehint.__origin__
				is_last = pointer + 1 == len(argv)
				next_argument = pointer + 1
				while next_argument < len(argv) and not cls.__match_argument_name(argv[next_argument]):
					next_argument += 1
				if typehint == bool and argument not in positionals and defaults.get(argument) is False:
					values[argument] = "True"
					pointer += 1
					continue
				elif is_last or pointer + 1 == next_argument:
					raise CommandException(f"Invalid usage: missing {alias} option value")
				elif typehint in (list, tuple, set):
					values[argument] = argv[pointer + 1:next_argument]
					pointer = next_argument
				elif typehint == dict:
					values[argument] = dict(value.split("=", 1) for value in argv[pointer + 1:next_argument])
					pointer = next_argument
				else:
					values[argument] = argv[pointer + 1]
					pointer += 2
			else:
				free_values.append(argv[pointer])
				pointer += 1

		# amount of positional arguments specified by keywords
		args_as_keyword = len([arg for arg in positionals if arg in values])
		# check all positional arguments are present
		if len(free_values) + args_as_keyword < len(positionals):
			# amount of free values and positional arguments specified by keywords
			# less than amount of required positional arguments
			raise CommandException("Invalid usage: missing required positional arguments")

		# checking positional arguments don't follow keyword arguments
		for i, arg in enumerate(positionals):
			if arg in values:
				for j, arg_ in enumerate(positionals[i + 1:]):
					if arg_ not in values:
						raise CommandException(f"Invalid usage: positional argument '{arg_}' follows keyword argument '{arg}'")
				break

		# checking unnecessary positional arguments
		if spec.varargs is None:
			if args_as_keyword > 0 and len(free_values) != len(positionals) - args_as_keyword:
				# varargs is None and some positional arguments were specified by keyword,
				# so it's denied to specify keyword arguments by position
				raise CommandException("Invalid usage: unexpected number of positional arguments")
			if args_as_keyword == 0 and len(free_values) > len(positionals) + len(keyword):
				# varargs is None and amount of all arguments is less than amount of given free values
				raise CommandException("Invalid usage: unexpected number of positional arguments")

		# checking unnecessary keyword arguments
		if spec.varkw is None and any(arg not in positionals and arg not in keyword for arg in values):
			raise CommandException("Invalid usage: unexpected number of keyword arguments")

		# amount of positional arguments specified by position
		args_as_positional = len(positionals) - args_as_keyword
		# map of positional arguments names to values specified by position
		args: dict = dict(zip(positionals[:args_as_positional], free_values[:args_as_positional]))
		# extend args with positional arguments specified by keywords
		args.update({arg: values[arg] for arg in positionals[args_as_positional:]})
		# rest of values specified by position after positional arguments were taken
		extra_args = free_values[args_as_positional:]

		# amount of keyword arguments specified by position
		# if varargs presents in the function signature specifying keyword argument by position is denied
		kwargs_as_positional = len(extra_args) if spec.varargs is None else 0
		# checking if any keyword argument specified by position was duplicated by keyword
		for arg in keyword[:kwargs_as_positional]:
			if arg in values:
				raise CommandException(f"Invalid usage: keyword argument {arg} have been specified as positional already")

		# map of keyword arguments names to values specified by corresponding keywords
		kwargs = {arg: value for arg, value in values.items() if arg not in positionals}
		kwargs.update(dict(zip(keyword[:kwargs_as_positional], extra_args)))
		if kwargs_as_positional:
			extra_args.clear()

		for arg in args:
			args[arg] = cls.__parse_value(args[arg], spec.annotations.get(arg))
		for kwarg in kwargs:
			kwargs[kwarg] = cls.__parse_value(kwargs[kwarg], spec.annotations.get(kwarg))
		extra_args = [cls.__parse_value(value, spec.annotations.get(spec.varargs)) for value in extra_args]

		return [*args.values(), *extra_args], kwargs

	@classmethod
	def __match_argument_name(cls, string: str) -> str:
		if match := re.match("^(-[a-zA-Z]|--[a-zA-Z_][a-zA-Z0-9_-]+)$", string):
			return match.group(1).lstrip("-")

	@classmethod
	def __parse_value[T](cls, value: str, typehint: Type[T]) -> T:
		origin = typehint.__origin__ if isinstance(typehint, GenericAlias) else typehint
		generics = list(typehint.__args__) if isinstance(typehint, GenericAlias) else []

		if origin in (str, None):
			return value
		elif origin in (int, float):
			try:
				return typehint(value)
			except ValueError:
				raise CommandException(f"{value} can't be converted to {typehint}")
		elif origin == bool:
			if value.lower() in ("1", "true"):
				return True
			elif value.lower() in ("0", "false"):
				return False
			raise CommandException(f"{value} can't be converted to {typehint}")
		elif isinstance(value, list):
			if origin in (list, set):
				if generics:
					return origin(cls.__parse_value(item, generics[0]) for item in value)
				return origin(value)
			if origin == tuple:
				if not generics:
					return origin(value)
				elif len(generics) == 1:
					return origin(cls.__parse_value(item, generics[0]) for item in value)
				elif len(generics) != len(value):
					raise CommandException("Mismatch between the number of elements and tuple generic types")
				return origin(cls.__parse_value(value[i], generics[i]) for i in range(len(value)))
		elif isinstance(value, dict):
			if not generics:
				return value
			if len(generics) != 2:
				raise CommandException("Invalid number of dict generic types, should be 2")
			key_type, value_type = generics
			return {cls.__parse_value(k, key_type): cls.__parse_value(v, value_type) for k, v in value.items()}
		elif origin in (list, tuple, set, dict):
			try:
				obj = eval(value)
				if isinstance(obj, origin):
					return obj
			except Exception:
				pass
			raise CommandException(f"{value} can't be converted to {typehint}")
		raise CommandException(f"{value} can't be converted to {typehint}")
