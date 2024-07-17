from typing import Any, List, Mapping, Optional, OrderedDict, Union, cast, Tuple

import usaddress
from fhir.resources.R4B.address import Address

from fhir.resources.R4B.fhirtypes import (
    AddressType,
    String,
)
from scourgify import normalize_address_record

from helix_personmatching.standardizers.address_standardizer_result import (
    AddressStandardizerResult,
)
from helix_personmatching.utils.list_utils import get_first_element_or_null


class AddressStandardizer:
    @staticmethod
    def standardize(
        *, addresses: List[AddressType] | None, verbose: bool = False
    ) -> List[AddressStandardizerResult] | None:
        """
        Standardize a list of FHIR Address objects

        :param addresses: List of FHIR Address objects
        :param verbose: Whether to print verbose output
        :return: List of standardized FHIR Address objects
        """

        if not addresses:
            return None

        assert isinstance(addresses, list)

        standardized_addresses: List[AddressStandardizerResult | None] = [
            AddressStandardizer.standardize_single(address=address, verbose=verbose)
            for address in addresses
        ]

        return [s for s in standardized_addresses if s]

    @staticmethod
    def standardize_single(
        *, address: Optional[AddressType], verbose: bool
    ) -> Optional[AddressStandardizerResult]:
        """
        Standardize a single FHIR Address object.  Returns a structure that includes the standardized address, the
        street number, and the first five digits of the postal code.

        :param address: FHIR Address object
        :param verbose: Whether to print verbose output
        :return: Standardized FHIR Address object
        """
        if not address:
            return None

        assert isinstance(address, Address)

        # https://github.com/GreenBuildingRegistry/usaddress-scourgify
        # noinspection PyUnresolvedReferences
        address_dict = (
            {
                "address_line_1": address.line[0]
                if address.line and len(address.line) > 0
                else None,
                "address_line_2": address.line[1]
                if address.line and len(address.line) > 1
                else None,
                "city": address.city if address.city else None,
                "state": address.state if address.state else None,
                "postal_code": address.postalCode[0:5]
                if address.postalCode and len(address.postalCode) >= 5
                else None,
            }
            if address and address.postalCode and address.city and address.state
            else None
        )
        combined_address = (
            f"{address_dict['address_line_1'] or ''} "
            f"{address_dict['address_line_2'] or ''} "
            f"{address_dict['city']} {address_dict['state']} {address_dict['postal_code']}"
            if address_dict
            else address.text
        )
        parsed_address: Optional[OrderedDict[str, Union[List[str], str]]]
        parsed_address_type: Optional[str]
        parsed_address, parsed_address_type = (
            AddressStandardizer.safe_tag_address(
                address_line=combined_address,
                tag_mapping={
                    "Recipient": "recipient",
                    "AddressNumber": "address_line_1",
                    "AddressNumberPrefix": "address_line_1",
                    "AddressNumberSuffix": "address_line_1",
                    "StreetName": "address_line_1",
                    "StreetNamePreDirectional": "address_line_1",
                    "StreetNamePreModifier": "address_line_1",
                    "StreetNamePreType": "address_line_1",
                    "StreetNamePostDirectional": "address_line_1",
                    "StreetNamePostModifier": "address_line_1",
                    "StreetNamePostType": "address_line_1",
                    "CornerOf": "address_line_1",
                    "IntersectionSeparator": "address_line_1",
                    "LandmarkName": "address_line_1",
                    "USPSBoxGroupID": "address_line_1",
                    "USPSBoxGroupType": "address_line_1",
                    "USPSBoxID": "address_line_1",
                    "USPSBoxType": "address_line_1",
                    "BuildingName": "address_line_2",
                    "OccupancyType": "address_line_2",
                    "OccupancyIdentifier": "address_line_2",
                    "SubaddressIdentifier": "address_line_2",
                    "SubaddressType": "address_line_2",
                    "PlaceName": "city",
                    "StateName": "state",
                    "ZipCode": "postal_code",
                },
                verbose=verbose,
            )
            if combined_address
            else (None, None)
        )
        address_formatted: Optional[Mapping[str, str]] = (
            AddressStandardizer.safe_normalize_address_record(address_dict, verbose)
            if address_dict  # normalization fails on PO Boxes
            and (
                not parsed_address_type
                or parsed_address_type not in ["PO Box", "Ambiguous"]
            )
            and address_dict.get("postal_code")
            and address_dict.get("city")
            and address_dict.get("state")
            else AddressStandardizer.safe_normalize_address_record(
                parsed_address, verbose
            )
            if parsed_address
            # normalization fails on PO Boxes
            and (
                not parsed_address_type
                or parsed_address_type not in ["PO Box", "Ambiguous"]
            )
            else None
        )
        # https://github.com/datamade/usaddress
        address_tagged: Optional[OrderedDict[str, Union[List[Any], str]]]
        address_type: Optional[str]
        # noinspection PyUnresolvedReferences
        address_tagged, address_type = (
            (
                AddressStandardizer.safe_tag_address(
                    address_line=combined_address,
                    verbose=verbose,
                )
            )
            if address and address.line and len(address.line) > 0
            else (None, None)
        )
        # noinspection PyUnresolvedReferences
        address_street_num: Optional[str] = (
            cast(Optional[str], address_tagged.get("AddressNumber"))
            if address_tagged
            else None
        )
        # Get postal code in any way we can
        address_postal_code: Optional[str] = None
        if address_formatted and "postal_code" in address_formatted:
            address_postal_code = address_formatted.get("postal_code")
        if not address_postal_code and address_tagged and "ZipCode" in address_tagged:
            address_tagged_zip_code = address_tagged.get("ZipCode")
            if (
                isinstance(address_tagged_zip_code, list)
                and len(address_tagged_zip_code) > 0
            ):
                address_postal_code = address_tagged_zip_code[0]
            elif not isinstance(address_tagged_zip_code, list):
                address_postal_code = address_tagged_zip_code
        if (
            not address_postal_code
            and parsed_address
            and "postal_code" in parsed_address
        ):
            parsed_address_zip_code = parsed_address.get("postal_code")
            if (
                isinstance(parsed_address_zip_code, list)
                and len(parsed_address_zip_code) > 0
            ):
                address_postal_code = parsed_address_zip_code[0]
            elif not isinstance(parsed_address_zip_code, list):
                address_postal_code = parsed_address_zip_code
        # noinspection PyUnresolvedReferences
        if not address_postal_code and address and address.postalCode:
            # noinspection PyUnresolvedReferences
            address_postal_code = address.postalCode
        # Get address line 1 any way we can
        address_line_1: Optional[str] = None
        if address_formatted and "address_line_1" in address_formatted:
            address_line_1 = address_formatted.get("address_line_1")
        if not address_line_1 and parsed_address and "address_line_1" in parsed_address:
            parsed_address_line_1 = parsed_address.get("address_line_1")
            if (
                isinstance(parsed_address_line_1, list)
                and len(parsed_address_line_1) > 0
            ):
                address_line_1 = parsed_address_line_1[0]
            elif not isinstance(parsed_address_line_1, list):
                address_line_1 = parsed_address_line_1
        # noinspection PyUnresolvedReferences
        if not address_line_1 and address and address.line and len(address.line) > 0:
            # noinspection PyUnresolvedReferences
            address_line_1 = address.line[0]
        # now create the list of address lines
        address_lines = []
        if address_line_1:
            address_lines.append(address_line_1)
        if address_formatted and "address_line_2" in address_formatted:
            address_line_2 = address_formatted.get("address_line_2")
            if address_line_2:
                address_lines.append(address_line_2)
        elif (
            address
            and cast(Address, address).line
            and len(cast(Address, address).line) > 1
            and cast(Address, address).line[1]
        ):
            address_lines.append(cast(String, cast(Address, address).line[1]))
        elif (
            address
            and cast(Address, address).line
            and len(cast(Address, address).line) > 2
            and cast(Address, address).line[2]
        ):
            address_lines.append(cast(String, cast(Address, address).line[2]))

        standardized_address: Address = cast(Address, address).copy()
        # update some fields
        standardized_address.line = cast(List[String | None], address_lines)
        standardized_address.city = cast(
            String, address_formatted.get("city") if address_formatted else None
        )
        standardized_address.state = cast(
            String, address_formatted.get("state") if address_formatted else None
        )
        standardized_address.postalCode = cast(
            String, address_postal_code if address_postal_code else None
        )
        standardized_address_parts: List[str] = []
        if standardized_address.line and len(standardized_address.line) > 0:
            standardized_address_parts.extend(standardized_address.line)
        if standardized_address.city:
            standardized_address_parts.append(standardized_address.city)
        if standardized_address.state:
            standardized_address_parts.append(standardized_address.state)
        if standardized_address.postalCode:
            standardized_address_parts.append(standardized_address.postalCode)
        if len(standardized_address_parts) > 0:
            standardized_address.text = " ".join(standardized_address_parts)

        address_postal_code_first_five = (
            standardized_address.postalCode[0:5]
            if standardized_address.postalCode
            and len(standardized_address.postalCode) >= 5
            else None
        )

        return AddressStandardizerResult(
            address=cast(AddressType, standardized_address),
            street_number=address_street_num,
            postal_code_five=address_postal_code_first_five,
        )

    @staticmethod
    def safe_tag_address(
        address_line: Optional[str],
        tag_mapping: Optional[Mapping[str, str]] = None,
        verbose: bool = False,
    ) -> Tuple[OrderedDict[str, Union[List[str], str]], str]:
        if verbose:
            print("AddressStandardizer.safe_tag_address() - tagging address...")

        if not address_line:
            tagged_address = OrderedDict[str, Union[List[Any], str]]()
            return tagged_address, "Ambiguous"
        try:
            return cast(
                Tuple[OrderedDict[str, Union[List[str], str]], str],
                usaddress.tag(address_line, tag_mapping=tag_mapping),
            )
        except Exception as e:
            if verbose:
                print(
                    f"Exception (graceful-handling): Tagging Address: {address_line} {e}"
                )

            tagged_address = OrderedDict[str, Union[List[Any], str]]()
            return tagged_address, "Ambiguous"

    @staticmethod
    def safe_normalize_address_record(
        address: Union[str, Mapping[str, str]],
        verbose: bool = False,
    ) -> Mapping[str, str]:
        if verbose:
            print(
                "AddressStandardizer.safe_normalize_address_record() - normalizing the address..."
            )

        if not isinstance(address, str) and (
            not address.get("postal_code")
            or not address.get("city")
            or not address.get("state")
        ):
            return address
        try:
            return cast(Mapping[str, str], normalize_address_record(address=address))
        except Exception as e:
            if verbose:
                print(
                    f"Exception (graceful-handling): Standardizing Address: {address!r} {e}"
                )

            # Handle this exception gracefully,
            #  returning address object 'as is' and not normalized.
            return cast(Mapping[str, str], address)

    @staticmethod
    def get_primary_address(
        *, addresses: Optional[List[AddressType]], verbose: bool = False
    ) -> Optional[AddressType]:
        if not addresses or len(addresses) == 0:
            return None

        # https://hl7.org/FHIR/valueset-address-use.html

        if verbose:
            print("FhirToAttributeDict:get_address()...")

        # 1. use == "official"
        official_address: Optional[AddressType] = get_first_element_or_null(
            [address for address in addresses if address.use == "official"]
        )
        if official_address:
            return official_address

        # 2. use == "home"
        home_address: Optional[AddressType] = get_first_element_or_null(
            [address for address in addresses if address.use == "home"]
        )
        if home_address:
            return home_address

        # 2. use == "work"
        work_address: Optional[AddressType] = get_first_element_or_null(
            [address for address in addresses if address.use == "work"]
        )
        if work_address:
            return work_address

        # 3. IF there is no use property, use the first address element by default
        return cast(Optional[AddressType], get_first_element_or_null(addresses))

    @staticmethod
    def standardize_text(*, address: str) -> AddressStandardizerResult | None:
        """
        Standardize a single address string.  Returns a structure that includes the standardized address, the
        street number, and the first five digits of the postal code.

        :param address: Address string
        :return: Standardized FHIR Address object
        """

        result = AddressStandardizer.standardize_single(
            address=cast(AddressType, Address.parse_obj(dict(text=address))),
            verbose=False,
        )

        return result

    @staticmethod
    def standardize_text_simple(*, address: str | None) -> str | None:
        """
        Standardize a single address string.  Returns a structure that includes the standardized address, the
        street number, and the first five digits of the postal code.

        :param address: Address string
        :return: Standardized FHIR Address object
        """

        if not address:
            return None

        result = AddressStandardizer.standardize_text(address=address)

        return (
            cast(Optional[str], cast(Address, result.address).text)
            if result and result.address
            else None
        )
