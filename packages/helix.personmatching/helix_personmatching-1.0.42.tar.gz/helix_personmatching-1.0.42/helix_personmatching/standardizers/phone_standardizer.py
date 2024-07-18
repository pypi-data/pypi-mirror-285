from typing import Optional, List, cast

import phonenumbers
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.fhirtypes import ContactPointType
from phonenumbers import PhoneNumber

from helix_personmatching.standardizers.phone_standardizer_result import (
    PhoneStandardizerResult,
)


class PhoneStandardizer:
    @staticmethod
    def standardize_single(
        *, phone: str | None, verbose: bool = False
    ) -> PhoneStandardizerResult | None:
        """
        Standardize a phone number

        :param phone: Phone number to standardize
        :param verbose: Whether to print verbose output
        :return: Standardized phone number
        """
        if not phone:
            return None

        assert isinstance(phone, str)

        # phone_formatted = re.sub("[+\s()-]+", "", phone)
        # https://github.com/daviddrysdale/python-phonenumbers
        phone_formatted: Optional[PhoneNumber] = (
            PhoneStandardizer.safe_phone_parse(
                phone=phone, country="US", verbose=verbose
            )
            if phone
            else None
        )
        phone_clean = str(phone_formatted.national_number) if phone_formatted else None
        return PhoneStandardizerResult(
            phone=phone_clean,
            phone_area=phone_clean[0:3] if phone_clean else None,
            phone_local=phone_clean[3:6] if phone_clean else None,
            phone_line=phone_clean[6:10] if phone_clean else None,
        )

    @staticmethod
    def safe_phone_parse(
        *,
        phone: str,
        country: str,
        verbose: bool = False,
    ) -> Optional[PhoneNumber]:
        if verbose:
            print("FhirToAttributeDict:safe_phone_parse()...")

        if not phone or not country:
            return None

        assert isinstance(phone, str)
        assert isinstance(country, str)
        assert phone is not None
        assert country is not None

        try:
            return phonenumbers.parse(phone, country)
        except Exception as e:
            if verbose:
                print(f"Exception (returning None): Parsing Phone: {phone}: {e}")

            return None

    @staticmethod
    def get_primary_phone_number(
        *, telecom: Optional[List[ContactPointType]], verbose: bool = False
    ) -> Optional[str]:
        if not telecom or len(telecom) == 0:
            return None
        assert isinstance(telecom, list)

        if verbose:
            print("FhirToAttributeDict:get_phone_number()...")

        phones = PhoneStandardizer.get_telecom_with_system(
            telecom=telecom, telecom_system="phone", verbose=verbose
        )
        if phones and len(phones) > 0:
            # prefer use=mobile
            mobile_phones = [phone for phone in phones if phone.use == "mobile"]
            if len(mobile_phones) > 0:
                return cast(Optional[str], mobile_phones[0].value)
            return cast(Optional[str], cast(ContactPoint, phones[0]).value)
        else:
            return None

    @staticmethod
    def get_telecom_with_system(
        *, telecom: List[ContactPointType], telecom_system: str, verbose: bool = False
    ) -> Optional[List[ContactPointType]]:
        if not telecom or len(telecom) == 0:
            return None

        assert isinstance(telecom, list)

        if verbose:
            print(
                f"FhirToAttributeDict:get_telecom_with_system() for {telecom_system}..."
            )

        matching_telecoms = [
            t for t in telecom if cast(ContactPoint, t).system == telecom_system
        ]
        return matching_telecoms

    @staticmethod
    def standardize_text_simple(*, text: str | None) -> str | None:
        """
        Standardize a phone number

        :param text: Phone number to standardize
        :return: Standardized phone number
        """
        if not text:
            return None

        assert isinstance(text, str)

        result = PhoneStandardizer.standardize_single(phone=text)
        return result.phone if result else None
