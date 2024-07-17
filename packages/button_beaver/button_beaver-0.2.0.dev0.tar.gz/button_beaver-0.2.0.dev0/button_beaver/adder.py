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

import sys
from typing import BinaryIO
import json
import io
import urllib.robotparser
import hashlib

import requests

from . import model
from .urls import URL
from . import version

session = requests.Session()
session.headers["User-Agent"] = f"button_beaver/{version.version} (requests/{requests.__version__} python/{sys.version.split()[0]}) +https://tildegit.org/MinekPo1/button_beaver"

def _get(url: URL):
	if url.domain == "":
		with open(url.path) as f:
			return json.load(f)
	r_robots = session.get(str(url))
	if r_robots.status_code == 200:
		rp = urllib.robotparser.RobotFileParser(str(url.copy_with(path="/robots.txt")))
		rp.parse(r_robots.text)
		if not rp.can_fetch(session.headers["User-Agent"],str(url)):  # type: ignore
			raise ValueError("blocked by robots.txt")
	r = session.get(str(url))
	r.raise_for_status()
	return r.json()

def get_button(button: model.Button):
	url = URL.parse(button.uri)
	if url.domain is None:
		return open(url.path,"rb")
	return io.BytesIO(session.get(button.uri).content)

def get_button_hash(button: model.Button, file: BinaryIO | None = None):
	if file is None:
		with get_button(button) as button_f:
			button.sha256 = hashlib.file_digest(button_f,"sha256").digest().hex()
	else:
		button.sha256 = hashlib.file_digest(file,"sha256").digest().hex()  # type: ignore


def get_buttons(ref: str) -> model.Buttons:
	refu = URL.parse(ref)
	if refu.path.suffix == ".json":
		data: model.Draft1Format | model.Format = _get(refu)
		out = model.Buttons(ref=ref)
		if isinstance(data,list):
			# old version
			data = model.Format({"$schema": "","buttons": list[model.ButtonEntry](data)}) # type: ignore
		if "default" in data:
			out.default_id = data["default"]
		for i in data["buttons"]:
			out.add(model.Button.model_validate(i))
		return out
	refu.path /= ".well-known/button.json"

	data = _get(refu)
	out = model.Buttons(ref=ref)
	if isinstance(data,list):
		# old version
		data = model.Format({"$schema": "","buttons": list[model.ButtonEntry](data)}) # type: ignore
	if "default" in data:
		out.default_id = data["default"]
	for i in data["buttons"]:
		out.add(model.Button.model_validate(i))
	return out
