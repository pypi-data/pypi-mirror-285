from typing import List, Optional, cast

from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.fhirtypes import ContactPointType

from helix_personmatching.standardizers.email_standardizer_result import (
    EmailStandardizerResult,
)
from helix_personmatching.standardizers.phone_standardizer import PhoneStandardizer


class EmailStandardizer:
    @staticmethod
    def standardize_single(
        *, email: str | None, verbose: bool = False
    ) -> EmailStandardizerResult | None:
        """
        Standardize an email address

        :param email: Email address to standardize
        :param verbose: Whether to print verbose output
        :return: Standardized email address
        """
        if not email:
            return None

        assert isinstance(email, str)
        # email_clean = email.strip().lower() if email else None
        return EmailStandardizerResult(
            email=email, email_user_name=email.split("@")[0] if email else None
        )

    @staticmethod
    def get_primary_email(
        *, telecom: Optional[List[ContactPointType]], verbose: bool = False
    ) -> Optional[str]:
        if not telecom or len(telecom) == 0:
            return None

        assert isinstance(telecom, list)

        if verbose:
            print("FhirToAttributeDict:get_email()...")

        emails: List[
            ContactPointType
        ] | None = PhoneStandardizer.get_telecom_with_system(
            telecom=telecom, telecom_system="email", verbose=verbose
        )
        if emails and len(emails) > 0:
            return cast(Optional[str], cast(ContactPoint, emails[0]).value)
        else:
            return None

    @staticmethod
    def standardize_text_simple(
        *, text: str | None, verbose: bool = False
    ) -> str | None:
        """
        Standardize an email address

        :param text: Email address to standardize
        :return: Standardized email address
        """
        if not text:
            return None

        assert isinstance(text, str)

        result = EmailStandardizer.standardize_single(email=text, verbose=verbose)
        return result.email if result else None
