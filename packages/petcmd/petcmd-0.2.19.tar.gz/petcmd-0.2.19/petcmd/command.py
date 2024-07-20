import re
from typing import Callable

from .utils import get_signature

class Command:

	def __init__(self, cmds: tuple[str, ...], func: Callable):
		self.cmds = cmds
		self.func = func
		self.aliases = self.__generate_aliases()

	def match(self, cmd: str | tuple[str, ...]) -> bool:
		if isinstance(cmd, str):
			return cmd in self.cmds
		return any(c in cmd for c in self.cmds)

	def __generate_aliases(self) -> dict[str, str]:
		"""Returns {alias: argument}"""
		positionals, keyword, *_ = get_signature(self.func)
		aliases = {}
		for arg in [*positionals, *keyword]:
			aliases[arg] = arg
			aliases[arg.replace('_', '-')] = arg
			first_letter = re.search(r"[a-zA-Z]", arg).group(0)
			if first_letter.lower() not in aliases:
				aliases[first_letter.lower()] = arg
			elif first_letter.upper() not in aliases:
				aliases[first_letter.upper()] = arg
		return aliases
