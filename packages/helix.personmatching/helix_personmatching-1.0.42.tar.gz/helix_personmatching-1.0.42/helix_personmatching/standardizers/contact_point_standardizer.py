from typing import cast, Optional, List

from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.fhirtypes import ContactPointType

from helix_personmatching.standardizers.contact_point_standardizer_result import (
    ContactPointStandardizerResult,
)
from helix_personmatching.standardizers.email_standardizer import EmailStandardizer
from helix_personmatching.standardizers.email_standardizer_result import (
    EmailStandardizerResult,
)
from helix_personmatching.standardizers.phone_standardizer import PhoneStandardizer
from helix_personmatching.standardizers.phone_standardizer_result import (
    PhoneStandardizerResult,
)


class ContactPointStandardizer:
    @staticmethod
    def standardize(
        *,
        contact_points: Optional[list[ContactPointType]],
    ) -> List[ContactPointStandardizerResult] | None:
        """
        Standardize a list of ContactPoint objects

        :param contact_points: List of ContactPoint objects to standardize
        :return: List of ContactPointStandardizerResult objects
        """
        if not contact_points:
            return None

        assert isinstance(contact_points, list)

        standardized_contact_points: list[ContactPointStandardizerResult] = []
        for contact_point in contact_points:
            standardized_contact_point_result: Optional[
                ContactPointStandardizerResult
            ] = ContactPointStandardizer.standardize_single(
                contact_point=contact_point,
            )
            if standardized_contact_point_result:
                standardized_contact_points.append(standardized_contact_point_result)

        return standardized_contact_points

    @staticmethod
    def standardize_single(
        *,
        contact_point: ContactPointType | None,
    ) -> ContactPointStandardizerResult | None:
        """
        Standardize a ContactPoint object

        :param contact_point: ContactPoint object to standardize
        :return: ContactPointStandardizerResult object
        """
        if not contact_point:
            return None

        assert isinstance(contact_point, ContactPoint)

        if cast(ContactPoint, contact_point).system == "phone":
            standardized_phone_result: Optional[
                PhoneStandardizerResult
            ] = PhoneStandardizer.standardize_single(
                phone=cast(ContactPoint, contact_point).value,
            )
            if standardized_phone_result:
                cast(
                    ContactPoint, contact_point
                ).value = standardized_phone_result.phone
            return ContactPointStandardizerResult(
                contact_point=cast(ContactPointType, contact_point)
            )
        elif cast(ContactPoint, contact_point).system == "email":
            standardized_email_result: Optional[
                EmailStandardizerResult
            ] = EmailStandardizer.standardize_single(
                email=cast(ContactPoint, contact_point).value,
            )
            if standardized_email_result:
                cast(
                    ContactPoint, contact_point
                ).value = standardized_email_result.email
            return ContactPointStandardizerResult(
                contact_point=cast(ContactPointType, contact_point)
            )

        return ContactPointStandardizerResult(
            contact_point=cast(ContactPointType, contact_point),
        )
