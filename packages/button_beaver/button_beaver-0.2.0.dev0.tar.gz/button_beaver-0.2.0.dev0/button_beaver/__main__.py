"""
button_beaver - a helper for all your 88x31 buttoning needs!
Copyright (C) 2024  Lily "MinekPo1" A. N. - minekpo1@dimension.sh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import hashlib
import json
import sys
from typing import Literal
from pathlib import Path
import html

import lxml.html
import yaml
import requests


from . import model
from . import adder
from .urls import URL

class Args(argparse.Namespace):
	...

class AddArgs(Args):
	name: str
	ref: str | None = None
	id: str | None = None
	html: bool = False
	own: bool = False
	group: str | None = None
	color: Literal["light","dark","other"] = "other"
	animation: Literal["none","minimal","high", None]
	contrast: Literal["standard","more","less"] = "standard"

class InitArgs(Args):
	res: str = "./res"
	url: str = ""

class GetArgs(Args):
	name: str
	id: str
	code: str = ""
	format: Literal["html","json"]
	url: str = ""
	fallback: bool

class PrefixArgs(Args):
	name: str
	prefix: str | None = None

class ListArgs(Args):
	name: str | None
	remote: str | None

class ViewArgs(Args):
	name_or_ref: str
	id: str
	code: str = ""
	format: Literal["html","json"]

class GenerateArgs(Args):
	url: str | None

def find_beaverfile() -> Path | None:
	p = Path(".").absolute()
	while True:
		if (p/".beaver.yml").exists():
			return p/".beaver.yml"
		if p == p.parent:
			return None
		p = p.parent

def do_add(args: AddArgs):
	beaverfile_loc = find_beaverfile()
	if beaverfile_loc is None:
		print("couldn't find beaverfile!",file=sys.stderr)
		return 1
	with beaverfile_loc.open() as f:
		beaverfile = model.BeaverFile.model_validate(yaml.safe_load(f))

	if args.id is not None:
		button = model.Button(id=args.id,uri="temp",alt="temp",groupId=args.group)
		if args.html:
			if sys.stdin.isatty():
				print(f"End with ^D:")
			html_string = ""
			while True:
				try:
					html_string += input()
				except EOFError:
					break
			elm: lxml.html.HtmlElement = lxml.html.fragment_fromstring(html_string)
			if elm.tag == 'a':
				button.link = elm.get("href")
				elm = elm[0]
			if elm.tag != 'img':
				print("Cant understand given html!")
				return 1
			button.alt = elm.get("alt")
			button.uri = elm.get("src")
		else:
			if sys.stdin.isatty():
				button.uri = input("Image uri:")
				button.alt = input("Alt text:")
				button.link= input("Link:") or None
			else:
				button.uri = input("")
				button.alt = input("")
				button.link= input("") or None
		adder.get_button_hash(button)
		if args.name not in beaverfile.sources:
			beaverfile.sources[args.name] = model.Buttons(ref="")
		beaverfile.sources[args.name].add(button)
		print("Added button!",file=sys.stderr)
	else:
		if args.ref is not None:
			try:
				buttons = adder.get_buttons(args.ref)
			except FileNotFoundError:
				print("ref does not exist!",file=sys.stderr)
				return 1
			except requests.HTTPError as ex:
				print(f"querying ref failed: {ex}")
				return 1
		else:
			buttons = model.Buttons(ref="")
		prefixes: set[str] | None = None
		for button in buttons.by_id.values():
			bprefixes = set([button.id[:i] for i in range(len(button.id))])
			if prefixes is None:
				prefixes = bprefixes
			else:
				prefixes &= bprefixes
			if button.sha256 is None:
				adder.get_button_hash(button)
		if prefixes:
			prefix = max(prefixes,key=len)
			if prefix not in buttons.by_id:
				print("Setting prefix to",prefix)
				buttons.prefix = prefix
		beaverfile.sources[args.name] = buttons
		print(f"Added {len(buttons.by_id)} button{'s' if len(buttons.by_id) != 1 else ''}!",file=sys.stderr)

	with beaverfile_loc.open("w") as f:
		yaml.safe_dump(beaverfile.model_dump(),f)

def do_init(args: InitArgs):
	if Path(".beaver.yml").exists():
		print("beaverfile already exists!",file=sys.stderr)
		return 1
	beaverfile = model.BeaverFile(res=args.res,url=args.url,sources={},own_sources=set())
	with open(".beaver.yml","w") as f:
		yaml.safe_dump(beaverfile.model_dump(),f)
	print("initialized!",file=sys.stderr)

def do_update(args: Args):
	beaverfile_loc = find_beaverfile()
	if beaverfile_loc is None:
		print("couldn't find beaverfile!",file=sys.stderr)
		return 1
	with beaverfile_loc.open() as f:
		beaverfile = model.BeaverFile.model_validate(yaml.safe_load(f))
	for name,source in beaverfile.sources.copy().items():
		print(f"{name}...                     ",end="\r")
		try:
			if source.ref != "":
				new_source = adder.get_buttons(source.ref)
				new_source.prefix = source.prefix
				source = new_source
				for button in source.by_id.values():
					if button.sha256 is None:
						adder.get_button_hash(button)
				beaverfile.sources[name] = source
			for button in source.by_id.values():
				print(f"{name} {button.id}...                     ",end="\r")
				file_ext = button.uri.split(".")[-1]
				own_file = f"88x31-{name}-{html.escape(button.id.removeprefix(source.prefix)).replace('/','-')}.{file_ext}"
				if (Path(beaverfile.res) / own_file).exists():
					with (Path(beaverfile.res) / own_file).open("rb") as f:
						own_hash = hashlib.file_digest(f,"sha256").digest().hex()
					if own_hash != button.sha256:
						with (Path(beaverfile.res) / own_file).open("wb") as f:
							f.write(adder.get_button(button).read())
		except FileNotFoundError:
			print(f"file not found for source {name} (ref is {source.ref})",file=sys.stderr)
		except requests.HTTPError as ex:
			print(f"HTTPError {ex} for source {name} (ref is {source.ref})",file=sys.stderr)

	with beaverfile_loc.open("w") as f:
		yaml.safe_dump(beaverfile.model_dump(),f)

def do_get(args: GetArgs):
	beaverfile_loc = find_beaverfile()
	if beaverfile_loc is None:
		print("couldn't find beaverfile!",file=sys.stderr)
		return 1
	with beaverfile_loc.open() as f:
		beaverfile = model.BeaverFile.model_validate(yaml.safe_load(f))
	if args.name not in beaverfile.sources:
		if not args.fallback or beaverfile.fallback is None:
			print(f"unknown name {args.name}",file=sys.stderr)
			return 1
		args.name,args.id = beaverfile.fallback
	source = beaverfile.sources[args.name]
	if args.id not in source.by_id and args.id not in source.by_group and \
		source.prefix + args.id not in source.by_id and source.prefix + args.id not in source.by_group:
		if not args.fallback:
			print(f"unknown id: {args.id}",file=sys.stderr)
			return 1
		args.id = source.default_id
	button = source.get(args.id,args.code)
	if button is None:
		print("couldn't satisfy requirements",file=sys.stderr)
		return 1
	file_ext = button.uri.split(".")[-1]
	if args.name not in beaverfile.own_sources:
		own_file = f"88x31-{args.name}-{html.escape(button.id.removeprefix(source.prefix)).replace('/','-')}.{file_ext}"
		if not (Path(beaverfile.res) / own_file).exists():
			with (Path(beaverfile.res) / own_file).open("wb") as f:
				f.write(adder.get_button(button).read())
		elif button.sha256 is not None:
			with (Path(beaverfile.res) / own_file).open("rb") as f:
				own_hash = hashlib.file_digest(f,"sha256").digest().hex()
			if own_hash != button.sha256:
				with (Path(beaverfile.res) / own_file).open("wb") as f:
					f.write(adder.get_button(button).read())
	else:
		own_file = URL.parse(button.uri).path.name

	if args.format == 'html':
		if button.link is not None:
			if beaverfile.template_with_link is None:
				print(
					f'<a href="{button.link}"><img src="{beaverfile.url}{own_file}" alt="{button.alt}"/></a>'
				)
			else:
				print(beaverfile.template_with_link.format_map({
					'button': button,
					'own_file': own_file,
					'url': beaverfile.url,
				}))
			return
		if beaverfile.template_no_link is None:
			print(
				f'<img src="{beaverfile.url}{own_file}" alt={button.alt}/>\n'
			)
		else:
			print(beaverfile.template_no_link.format_map({
				'button': button,
				'own_file': own_file,
				'url': beaverfile.url,
			}))
		return
	if args.format == 'json':
		obj = button.model_dump(mode="json")
		obj['uri'] = beaverfile.url+own_file
		print(json.dumps(obj,indent='\t'))
		return
	print("unknown output format",file=sys.stderr)
	return 1

def do_prefix(args: PrefixArgs):
	beaverfile_loc = find_beaverfile()
	if beaverfile_loc is None:
		print("couldn't find beaverfile!",file=sys.stderr)
		return 1
	with beaverfile_loc.open() as f:
		beaverfile = model.BeaverFile.model_validate(yaml.safe_load(f))
	if args.name not in beaverfile.sources:
		print(f"unknown name {args.name}",file=sys.stderr)
		return 1
	source = beaverfile.sources[args.name]
	if args.prefix is None:
		print("prefix is", source.prefix)
		return
	source.prefix = args.prefix
	with beaverfile_loc.open("w") as f:
		yaml.safe_dump(beaverfile.model_dump(),f)

def do_list(args: ListArgs):
	if args.remote is not None:
		source = adder.get_buttons(args.remote)
		groups = {}
		for button in source.by_id.values():
			if button.groupId is not None:
				if button.groupId not in groups:
					groups[button.groupId] = []
				groups[button.groupId].append(button.code)
				continue
			print(button.id.removeprefix(source.prefix),f"({button.code})")
		for id,codes in groups.items():
			print(id.removeprefix(source.prefix),"("+", ".join(codes)+")")
		return

	beaverfile_loc = find_beaverfile()
	if beaverfile_loc is None:
		print("couldn't find beaverfile!",file=sys.stderr)
		return 1
	with beaverfile_loc.open() as f:
		beaverfile = model.BeaverFile.model_validate(yaml.safe_load(f))
	if args.name is not None:
		if args.name not in beaverfile.sources:
			print(f"unknown name: {args.name}",file=sys.stderr)
			return 1
		source = beaverfile.sources[args.name]
		groups = {}
		for button in source.by_id.values():
			if button.groupId is not None:
				if button.groupId not in groups:
					groups[button.groupId] = []
				groups[button.groupId].append(button.code)
				continue
			print(button.id.removeprefix(source.prefix),f"({button.code})")
		for id,codes in groups.items():
			print(id.removeprefix(source.prefix),"("+", ".join(codes)+")")
	else:
		for name,source in beaverfile.sources.items():
			print(f"{name}:")
			groups = {}
			for button in source.by_id.values():
				if button.groupId is not None:
					if button.groupId not in groups:
						groups[button.groupId] = []
					groups[button.groupId].append(button.code)
					continue
				print(" ",button.id.removeprefix(source.prefix),f"({button.code})")
			for id,codes in groups.items():
				print(" ",id.removeprefix(source.prefix),"("+", ".join(codes)+")")

prog = argparse.ArgumentParser("button_beaver",
	epilog=
		"button codes:\n"
		"  (ho~)\n"
		"   ||'- contrast: `+` for high, `-` for low, `~` for standard\n"
		"   |'-- color scheme: `l` for light, `d` for dark, `o` for other\n"
		"   '--- animation: `h` for high, `l` for low, `n` for none, blank for unknown\n"
		"\n"
		'button_beaver  Copyright (C) 2024  Lily "MinekPo1" A. N.\n'
		'This program comes with ABSOLUTELY NO WARRANTY.\n'
		'This is free software, and you are welcome to redistribute it\n'
		'under certain conditions.',
	formatter_class=argparse.RawDescriptionHelpFormatter
)

subparsers = prog.add_subparsers(required=True)

prog_add = subparsers.add_parser("add")
prog_add.add_argument("name")
prog_add.add_argument("--ref",'-r',default=None)
group = prog_add.add_argument_group("button options")
group.add_argument("--id",'-i',default=None)
group.add_argument("--group",default=None)
group.add_argument("--html",action="store_true")
group.add_argument("--own",action="store_true")
group.add_argument("--color","-c",choices=["light","dark","other"],default="other")
group.add_argument("--animation","-a",choices=["none","minimal","high"],default=None)
group.add_argument("--contrast","-C",choices=["standard","more","less"],default="standard")
prog_add.set_defaults(func=do_add)

prog_init = subparsers.add_parser("init")
prog_init.add_argument("--res","-r",default="res")
prog_init.add_argument("--url","-u",default="")
prog_init.set_defaults(func=do_init)

prog_update = subparsers.add_parser("update")
prog_update.set_defaults(func=do_update)

prog_get = subparsers.add_parser("get")
prog_get.add_argument("name")
prog_get.add_argument("id")
prog_get.add_argument("code",nargs="?",default="")
prog_get.add_argument("--format","-f",choices=["html","json"],default="html")
prog_get.add_argument("--url","-u",default="")
prog_get.add_argument("--fallback","-F",action="store_true")
prog_get.set_defaults(func=do_get)

prog_prefix = subparsers.add_parser("prefix")
prog_prefix.add_argument("name")
prog_prefix.add_argument("prefix",nargs='?')
prog_prefix.set_defaults(func=do_prefix)

prog_list = subparsers.add_parser("list")
prog_list.add_argument("name",nargs="?")
prog_list.add_argument("--remote","-r",default=None)
prog_list.set_defaults(func=do_list)

if __name__ == "__main__":
	args = prog.parse_args(sys.argv[1:])
	exit(args.func(args))
