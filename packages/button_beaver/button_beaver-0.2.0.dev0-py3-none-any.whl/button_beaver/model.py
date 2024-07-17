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

from typing import Literal, NotRequired, TypeAlias, TypedDict
import pydantic

class Button(pydantic.BaseModel):
	id:  str
	uri: str
	alt: str
	link:    None | str = None
	sha256:  None | str = None
	groupId: None | str = None
	colorScheme: Literal["light","dark","other"] = "other"
	animations:  Literal["none","minimal","high"] | None = None
	contrast:    Literal["standard","more","less"] = "standard"

	@property
	def code(self):
		return (self.animations[0] if self.animations is not None else " ") + self.colorScheme[0] + {"standard":"~","more":"+","less":"-"}[self.contrast]

	def score(self, code: str):
		if not code:
			return 0
		if "?" not in code:
			if (self.code[0] == ' ' or self.code[0] not in code) and 'nmh' in code:
				return -1
			if self.code[1] not in code and 'ldo' in code:
				return -1
			if self.code[2] not in code and '+-~' in code:
				return -1
		return sum([code.count(i) for i in self.code])

class Buttons(pydantic.BaseModel):
	ref: str
	by_id: dict[str, Button] = pydantic.Field(default_factory=dict)
	by_group: dict[str, list[Button]] = pydantic.Field(default_factory=dict,exclude=True)
	prefix: str = ""
	default_id: str = ""

	def model_post_init(self, __context) -> None:
		for button in self.by_id.values():
			if button.groupId is None:
				continue
			if button.groupId not in self.by_group:
				self.by_group[button.groupId] = []
			self.by_group[button.groupId].append(button)

	@property
	def default(self):
		return self.by_id.get(self.default_id)

	def add(self, button: Button):
		self.by_id[button.id] = button
		if button.groupId is None:
			return
		if button.groupId not in self.by_group:
			self.by_group[button.groupId] = []
		self.by_group[button.groupId].append(button)

	def get(self,id: str, code: str) -> Button | None:
		if id not in self.by_id and id not in self.by_group:
			id = self.prefix + id
		best = None
		bscore = -1
		
		if id in self.by_id:
			best = self.by_id[id]
			bscore = best.score(code)
		if id in self.by_group:
			bgroup = max(self.by_group[id],key=lambda i: i.score(code))
			if bgroup.score(code) > bscore:
				best = bgroup
				bscore = best.score(code)
		if bscore == -1:
			return None
		return best

class BeaverFile(pydantic.BaseModel):
	res: str = "res"
	url: str = ""
	sources: dict[str,Buttons]
	own_sources: set[str]
	template_with_link: str | None = None
	template_no_link: str | None = None
	fallback: tuple[str,str] | None = None

# typing version of the two schemas

class Draft1ButtonEntry(TypedDict):
	id: str
	uri: str
	alt: str
	link: str
	sha256: NotRequired[str]

Draft1Format: TypeAlias = list[Draft1ButtonEntry]

class ButtonEntry(TypedDict):
	id: str
	groupId: str
	uri: str
	alt: str
	link: str
	sha256: NotRequired[str]
	colorScheme: NotRequired[Literal["light","dark","other"]]
	animations: NotRequired[Literal["none","minimal","high"]]
	contrast: NotRequired[Literal["standard","high","low"]]

Format = TypedDict('Format', {'$schema': str, 'default': NotRequired[str], 'buttons': list[ButtonEntry]})
