import dataclasses

from fhir.resources.R4B.fhirtypes import ContactPointType


@dataclasses.dataclass
class ContactPointStandardizerResult:
    contact_point: ContactPointType | None
