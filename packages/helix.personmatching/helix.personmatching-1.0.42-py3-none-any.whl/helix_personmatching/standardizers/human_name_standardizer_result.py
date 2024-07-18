import dataclasses
from typing import Optional

from fhir.resources.R4B.fhirtypes import HumanNameType


@dataclasses.dataclass
class HumanNameStandardizerResult:
    name: Optional[HumanNameType]
    middle_initial: Optional[str]
    nick_name: Optional[str]
