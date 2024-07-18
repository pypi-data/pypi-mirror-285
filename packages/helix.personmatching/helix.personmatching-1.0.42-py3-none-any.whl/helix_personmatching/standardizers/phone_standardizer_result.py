import dataclasses


@dataclasses.dataclass
class PhoneStandardizerResult:
    phone: str | None
    phone_area: str | None
    phone_local: str | None
    phone_line: str | None
