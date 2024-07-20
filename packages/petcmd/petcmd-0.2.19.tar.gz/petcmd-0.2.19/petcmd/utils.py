
import inspect
from types import GenericAlias
from typing import Callable

from .exceptions import CommandException

def get_signature(func: Callable):
	"""Returns positionals, keyword, defaults, spec"""
	spec = inspect.getfullargspec(func)
	positionals = spec.args if spec.defaults is None else spec.args[:-len(spec.defaults)]
	keyword = spec.kwonlyargs
	if spec.defaults is not None:
		keyword.extend(spec.args[-len(spec.defaults):])
	defaults = spec.kwonlydefaults or {}
	if spec.defaults is not None:
		defaults.update(dict(zip(spec.args[-len(spec.defaults):], spec.defaults)))
	return positionals, keyword, defaults, spec

allowed_type_hints = (str, int, float, bool, list, tuple, set, dict)

def validate_type_hints(func: Callable):
	for arg, typehint in inspect.getfullargspec(func).annotations.items():
		origin = typehint.__origin__ if isinstance(typehint, GenericAlias) else typehint
		if origin not in allowed_type_hints:
			raise CommandException("Unsupported typehint: petcmd supports only next types: "
				+ ", ".join(map(lambda t: t.__name__, allowed_type_hints)))
		if isinstance(typehint, GenericAlias) and any(g not in allowed_type_hints for g in typehint.__args__):
			raise CommandException("Unsupported typehint generic: petcmd supports only basic generics")
