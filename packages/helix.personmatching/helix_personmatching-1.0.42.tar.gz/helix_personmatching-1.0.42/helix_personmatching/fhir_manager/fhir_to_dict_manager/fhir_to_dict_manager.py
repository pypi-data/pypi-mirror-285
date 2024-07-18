from datetime import date
from typing import Any, List, Optional, Union, cast

from fhir.resources.R4B.address import Address
from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.fhirtypes import (
    AddressType,
    IdentifierType,
    HumanNameType,
)
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.person import Person

from helix_personmatching.logics.scoring_input import ScoringInput
from helix_personmatching.standardizers.address_standardizer import AddressStandardizer
from helix_personmatching.standardizers.address_standardizer_result import (
    AddressStandardizerResult,
)
from helix_personmatching.standardizers.email_standardizer import EmailStandardizer
from helix_personmatching.standardizers.email_standardizer_result import (
    EmailStandardizerResult,
)
from helix_personmatching.standardizers.human_name_standardizer import (
    HumanNameStandardizer,
)
from helix_personmatching.standardizers.human_name_standardizer_result import (
    HumanNameStandardizerResult,
)
from helix_personmatching.standardizers.phone_standardizer import PhoneStandardizer
from helix_personmatching.standardizers.phone_standardizer_result import (
    PhoneStandardizerResult,
)


class FhirToAttributeDict:
    @staticmethod
    def get_scoring_input(
        resource: Union[Patient, Person],
        verbose: bool = False,
    ) -> ScoringInput:
        if verbose:
            print("FhirToAttributeDict:get_scoring_input()")

        standardized_name_result: Optional[
            HumanNameStandardizerResult
        ] = HumanNameStandardizer.standardize_single(
            name=(
                HumanNameStandardizer.get_primary_human_name(
                    name=cast(Optional[List[HumanNameType]], resource.name)
                )
            ),
            verbose=verbose,
        )
        standardized_name: Optional[HumanName] = (
            cast(Optional[HumanName], standardized_name_result.name)
            if standardized_name_result
            else None
        )
        address: Optional[AddressType] = AddressStandardizer.get_primary_address(
            addresses=resource.address, verbose=verbose
        )

        standardized_address_result: Optional[AddressStandardizerResult] = None
        standardized_address: Optional[Address] = None
        if address:
            standardized_address_result = AddressStandardizer.standardize_single(
                address=address, verbose=verbose
            )
            standardized_address = (
                cast(Optional[Address], standardized_address_result.address)
                if standardized_address_result
                else None
            )

        # phone
        phone: Optional[str] = PhoneStandardizer.get_primary_phone_number(
            telecom=resource.telecom, verbose=verbose
        )
        standardized_phone: Optional[
            PhoneStandardizerResult
        ] = PhoneStandardizer.standardize_single(phone=phone, verbose=verbose)

        # email
        email: Optional[str] = EmailStandardizer.get_primary_email(
            telecom=resource.telecom, verbose=verbose
        )
        standardized_email_result: Optional[
            EmailStandardizerResult
        ] = EmailStandardizer.standardize_single(email=email, verbose=verbose)

        # ssn
        ssn = FhirToAttributeDict.get_ssn(resource.identifier, verbose)

        meta_security_code = (
            FhirToAttributeDict.get_access_tag(
                cast(Meta, resource.meta).security, verbose
            )
            if resource.meta and cast(Meta, resource.meta).security
            else None
        )

        age_in_years = FhirToAttributeDict.calculate_age_in_years(
            resource.birthDate, verbose
        )

        scoring_input: ScoringInput = ScoringInput(
            id_=resource.id,
            name_given=standardized_name.given[0]
            if standardized_name
            and standardized_name.given
            and len(standardized_name.given) > 0
            else None,
            name_family=standardized_name.family if standardized_name else None,
            name_middle=standardized_name.given[1]
            if standardized_name
            and standardized_name.given
            and len(standardized_name.given) > 1
            else None,
            name_middle_initial=standardized_name_result.middle_initial
            if standardized_name_result
            else None,
            gender=resource.gender,
            birth_date=resource.birthDate.strftime("%Y-%m-%d")
            if resource.birthDate
            else None,
            address_postal_code=standardized_address.postalCode
            if standardized_address
            else None,
            address_postal_code_first_five=standardized_address_result.postal_code_five
            if standardized_address_result
            else None,
            address_line_1=standardized_address.line[0]
            if standardized_address
            and standardized_address.line
            and len(standardized_address.line) > 0
            else None,
            email=standardized_email_result.email
            if standardized_email_result
            else None,
            phone=standardized_phone.phone if standardized_phone else None,
            birth_date_year=str(resource.birthDate.year)
            if resource.birthDate and resource.birthDate.year
            else None,
            birth_date_month=str(resource.birthDate.month)
            if resource.birthDate and resource.birthDate.month
            else None,
            birth_date_day=str(resource.birthDate.day)
            if resource.birthDate and resource.birthDate.day
            else None,
            phone_area=standardized_phone.phone_area if standardized_phone else None,
            phone_local=standardized_phone.phone_local if standardized_phone else None,
            phone_line=standardized_phone.phone_line if standardized_phone else None,
            address_line_1_st_num=standardized_address_result.street_number
            if standardized_address_result
            else None,
            email_username=standardized_email_result.email_user_name
            if standardized_email_result
            else None,
            is_adult_today=age_in_years >= 18 if age_in_years else None,
            ssn=ssn,
            ssn_last4=ssn[-4] if ssn and len(ssn) >= 4 else None,
            meta_security_client_slug=meta_security_code,
        )
        return scoring_input

    @staticmethod
    def get_scoring_inputs_for_resource(
        *,
        bundle_or_resource: Union[Patient, Person, Bundle],
        verbose: bool = False,
    ) -> List[ScoringInput]:
        resources: List[Union[Patient, Person]]
        if isinstance(bundle_or_resource, Bundle):
            resources = [
                cast(Union[Patient, Person], cast(BundleEntry, e).resource)
                for e in bundle_or_resource.entry
            ]
        else:
            resources = [bundle_or_resource]

        if verbose:
            print("FhirToAttributeDict:get_scoring_inputs_for_resource()...")

        return [
            FhirToAttributeDict.get_scoring_input(
                resource=resource,
                verbose=verbose,
            )
            for resource in resources
        ]

    @staticmethod
    def get_access_tag(
        security_tags: Optional[List[Any]], verbose: bool = False
    ) -> Optional[str]:
        if not security_tags or len(security_tags) == 0:
            return None

        if verbose:
            print("FhirToAttributeDict:get_access_tag()...")

        access_tags = [
            tag
            for tag in security_tags
            if tag.system == "https://www.icanbwell.com/access"
        ]
        return access_tags[0].code if len(access_tags) > 0 else None

    @staticmethod
    def get_ssn(
        identifiers: Optional[List[IdentifierType]], verbose: bool = False
    ) -> Optional[str]:
        if not identifiers or len(identifiers) == 0:
            return None

        if verbose:
            print("FhirToAttributeDict:get_ssn()...")

        ssn_identifiers = [
            identifier
            for identifier in identifiers
            if identifier.system == "http://hl7.org/fhir/sid/us-ssn"
        ]
        return ssn_identifiers[0].value if len(ssn_identifiers) > 0 else None

    @staticmethod
    def calculate_age_in_years(
        birthdate: Optional[date], verbose: bool = False
    ) -> Optional[int]:
        if not birthdate:
            return None

        if verbose:
            print("FhirToAttributeDict:calculate_age_in_years()...")

        # Get today's date object
        today = date.today()

        # A bool that represents if today's day/month precedes the birthday/month
        one_or_zero = (today.month, today.day) < (birthdate.month, birthdate.day)

        # Calculate the difference in years from the date object's components
        year_difference = today.year - birthdate.year

        # The difference in years is not enough.
        # To get it right, subtract 1 or 0 based on if today precedes the
        # birthdate's month/day.

        # To do this, subtract the 'one_or_zero' boolean
        # from 'year_difference'. (This converts
        # True to 1 and False to 0 under the hood.)
        age = year_difference - one_or_zero

        return age
