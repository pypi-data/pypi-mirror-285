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

from dataclasses import dataclass
from typing import Self
import urllib.parse
from pathlib import Path

@dataclass
class URL:
	scheme: str
	domain: str
	path: Path
	params: str
	query: str
	fragment: str

	@classmethod
	def parse(cls, urlstring: str) -> Self:
		urltuple = urllib.parse.urlparse(urlstring)
		return cls(urltuple.scheme,urltuple.netloc,Path(urltuple.path or "/"),urltuple.params,urltuple.query,urltuple.fragment)

	def __str__(self):
		return urllib.parse.urlunparse([self.scheme,self.domain,str(self.path),self.params,self.query,self.fragment])

	def copy_with(self, *, scheme: str | None = None, domain: str | None = None, path: Path | str | None = None, params: str | None = None, query: str | None = None, fragment: str | None = None):
		return URL(
			self.scheme if scheme is None else scheme,
			self.domain if domain is None else domain,
			self.path   if path   is None else Path(path),
			self.params if params is None else params,
			self.query  if query  is None else query,
			self.fragment if fragment is None else fragment
		)
