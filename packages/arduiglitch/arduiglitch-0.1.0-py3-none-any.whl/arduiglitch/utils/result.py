"""
Arduiglitch - voltage glitch training on an ATMega328P
Copyright (C) 2024  Hugo PERRIN (h.perrin@emse.fr)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

TypeAlias of two dataclasses to emulate the behaviour of Rust Result
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Ok(Generic[T]):
    value: T


@dataclass
class Err:
    value: Exception


Result: TypeAlias = Ok[T] | Err
