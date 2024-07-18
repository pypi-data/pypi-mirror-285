import dataclasses


@dataclasses.dataclass
class EmailStandardizerResult:
    email: str | None
    email_user_name: str | None
