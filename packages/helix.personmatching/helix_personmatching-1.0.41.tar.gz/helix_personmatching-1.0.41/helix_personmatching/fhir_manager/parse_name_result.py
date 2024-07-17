from dataclasses import dataclass
from typing import Optional


@dataclass
class ParseNameResult:
    first: Optional[str]
    middle: Optional[str]
    last: Optional[str]
    suffix: Optional[str]
    prefix: Optional[str]
    title: Optional[str]
    nickname: Optional[str]
