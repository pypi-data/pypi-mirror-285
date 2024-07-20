
import os

try:
	# noinspection PyUnresolvedReferences
	import __main__
	tool_name = os.path.basename(__main__.__file__).rsplit(".", 1)[0]
	if tool_name == "__main__":
		tool_name = __main__.__package__
except (ImportError, AttributeError):
	tool_name = "cli"

import re
import inspect
from typing import Optional

from .command import Command
from .utils import get_signature

class Interface:

	@classmethod
	def commands_list(cls, commands: list[Command]):

		def view(c: Command):

			def docs_view() -> str:
				if docs := cls.__parse_doc(c.func.__doc__)[0]:
					return f"\n{" " * 8}" + f"\n{" " * 8}".join(docs)
				return ""

			return f"{" " * 4}{", ".join(c.cmds)}{docs_view()}"

		print(f"\n{tool_name} commands list:\n\n" + "\n\n".join(map(view, commands)) + "\n")

	@classmethod
	def command_usage(cls, command: Command):
		positionals, keyword, defaults, spec = get_signature(command.func)
		docs, args_docs = cls.__parse_doc(command.func.__doc__)

		def command_name_view() -> str:
			if command.cmds[0] == "__main__":
				return tool_name
			return f"{tool_name} {command.cmds[0]}"

		def positionals_view() -> str:
			if not positionals:
				return ""
			return " ".join(positionals) + " "

		def keywords_list_view() -> str:
			return " ".join(f"[-{arg}]" for arg in keyword)

		def positional_description_view(arg: str) -> str:
			return f"{arg:<{longest_pos_name + 1}}{typehint_view(arg):<{longest_pos_hint + 1}}" \
				+ f"\n{" " * (longest_pos_name + longest_pos_hint + 2)}".join(args_docs.get(arg, []))

		def typehint_view(arg: str) -> str:
			hint = spec.annotations.get(arg)
			if not hint:
				return ""
			if isinstance(hint, type):
				return hint.__name__
			return str(hint)

		def keyword_description_view(arg: str) -> str:
			desc = f"{aliases_view(arg):<{longest_kw_name + 1}}"
			desc += f"{typehint_view(arg):<{longest_kw_hint + 1}}"
			desc += default_value_view(arg)
			if arg in args_docs:
				desc += "\n" + " " * 16 + f"\n{" " * 16}".join(args_docs[arg])
			return " " * 8 + desc

		def aliases_view(arg: str) -> str:
			return " ".join(alias_view(alias) for alias, argument in command.aliases.items() if argument == arg)

		def alias_view(alias: str):
			if len(alias) == 1:
				return f"-{alias}"
			return f"--{alias}"

		def default_value_view(arg: str):
			if arg not in defaults:
				return ""
			return f"[default: {defaults[arg]}]"

		desc = f"Usage: {command_name_view()} {positionals_view()}{keywords_list_view()}"
		if docs:
			desc += f"\n\n{" " * 8}{"\n\t".join(docs)}"
		if positionals:
			longest_pos_name = max(len(arg) for arg in positionals)
			if longest_pos_name < 7:
				longest_pos_name = 7
			longest_pos_hint = max(len(typehint_view(arg)) for arg in positionals)
			if longest_pos_hint < 7:
				longest_pos_hint = 7
			desc += "\n\n" + "\n".join(map(positional_description_view, positionals))
		if keyword:
			longest_kw_name = max(len(aliases_view(arg)) for arg in keyword)
			if longest_kw_name < 15:
				longest_kw_name = 15
			longest_kw_hint = max(len(typehint_view(arg)) for arg in keyword)
			if longest_kw_hint < 7:
				longest_kw_hint = 7
			desc += "\n\nOptions:\n" + "\n".join(map(keyword_description_view, keyword))

		print("\n" + desc + "\n")

	@staticmethod
	def __parse_doc(doc: Optional[str]) -> tuple[list[str], dict[str, list[str]]]:
		"""Returns list of docs paragraphs and map of arguments to list of argument docs paragraphs"""
		if not doc:
			return [], {}
		doc = inspect.cleandoc(doc)
		desc = []
		roles = []

		lines = doc.splitlines()
		i = 0
		while i < len(lines):
			if match := re.match("^:([a-zA-Z]+) ?([^:]*): ?(.*)$", lines[i].strip()):
				role, arg, value = match.groups()
				indent = len(re.match(r"^(\s*)", lines[i]).group(0))
				content = [value]
				i += 1
				while i < len(lines) and len(re.match(r"^(\s*)", lines[i]).group(0)) > indent:
					content.append(lines[i].strip())
					i += 1
				roles.append({"name": role, "arg": arg, "content": content})
				continue
			elif not len(roles):
				desc.append(lines[i].strip())
			i += 1

		while desc and not desc[0]:
			desc.pop(0)
		while desc and not desc[-1]:
			desc.pop()

		return desc, {role["arg"]: role["content"] for role in roles if role["name"] == "param"}
