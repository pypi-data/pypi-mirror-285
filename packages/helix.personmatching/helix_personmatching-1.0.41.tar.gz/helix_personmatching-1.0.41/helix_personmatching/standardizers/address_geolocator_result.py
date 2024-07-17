import dataclasses
from typing import Optional

from fhir.resources.R4B.fhirtypes import AddressType


@dataclasses.dataclass
class AddressGeoLocatorResult:
    address: Optional[AddressType]
    latitude: Optional[float]
    longitude: Optional[float]
