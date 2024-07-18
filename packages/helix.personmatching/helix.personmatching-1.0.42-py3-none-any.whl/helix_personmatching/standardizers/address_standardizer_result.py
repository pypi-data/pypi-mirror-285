import dataclasses
from typing import Optional

from fhir.resources.R4B.fhirtypes import AddressType


@dataclasses.dataclass
class AddressStandardizerResult:
    address: Optional[AddressType]
    street_number: Optional[str]
    postal_code_five: Optional[str]
