from typing import Any, List, Optional, cast, Dict

import requests
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.fhirtypes import (
    AddressType,
    String,
    ExtensionType,
)

from helix_personmatching.standardizers.address_geolocator_result import (
    AddressGeoLocatorResult,
)


class AddressGeoLocator:
    @staticmethod
    def standardize(
        *, addresses: List[AddressType] | None, verbose: bool = False
    ) -> List[AddressGeoLocatorResult] | None:
        """
        Adds geolocation information to a list of FHIR Address objects.  Returns a list of standardized FHIR Address

        :param addresses: List of FHIR Address objects
        :param verbose: Whether to print verbose output
        :return: List of standardized FHIR Address objects
        """

        if not addresses:
            return None

        assert isinstance(addresses, list)

        standardized_addresses: List[AddressGeoLocatorResult | None] = [
            AddressGeoLocator.standardize_single(address=address, verbose=verbose)
            for address in addresses
        ]

        return [s for s in standardized_addresses if s]

    @staticmethod
    def standardize_single(
        *, address: Optional[AddressType], verbose: bool
    ) -> Optional[AddressGeoLocatorResult]:
        """
        Adds geolocation information to a FHIR Address object.  Returns a standardized FHIR Address object

        :param address: FHIR Address object
        :param verbose: Whether to print verbose output
        :return: Standardized FHIR Address object
        """
        if not address:
            return None

        assert isinstance(address, Address)

        response_json: Optional[Dict[str, Any]] = AddressGeoLocator.get_geolocation(
            address=cast(AddressType, address)
        )

        return AddressGeoLocator.parse_geolocation_response(
            response_json=response_json, address=address
        )

    @staticmethod
    def get_geolocation(*, address: AddressType) -> Optional[Dict[str, Any]]:
        """
        Get geolocation information for a FHIR Address object from calling the US Census API.  Returns a JSON response

        :param address: FHIR Address object
        :return: JSON response
        """
        typed_address: Address = cast(Address, address)

        # Define the parameters
        one_line_address: Optional[str] = (
            " ".join([f"{a}" for a in typed_address.line if a])
            if typed_address.line
            else None
        )
        if one_line_address:
            one_line_address += f", {typed_address.city}, {typed_address.state} {typed_address.postalCode}"
        elif typed_address.text:
            one_line_address = typed_address.text

        if not one_line_address:
            return None

        params = {
            "address": one_line_address,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json",
        }

        # Make the request
        # https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
        # ex: "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=9000%20Franklin%20Square%20Dr.%2C%20Baltimore%2C%20MD%2021237&benchmark=Public_AR_Current&format=json"
        response = requests.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params=params,
        )

        # Check the response
        if response.status_code != 200:
            return None

        # Parse the response
        #
        response_json: Dict[str, Any] = response.json()
        if "result" not in response_json:
            return None

        return response_json

    @staticmethod
    def parse_geolocation_response(
        *, response_json: Dict[str, Any], address: Address
    ) -> Optional[AddressGeoLocatorResult]:
        """
        Parse the JSON response from the US Census API and return a standardized FHIR Address object

        :param response_json: JSON response
        :param address: FHIR Address object
        :return: Standardized FHIR Address object
        """
        if not response_json:
            return None

        if not address:
            return None

        # Get the result
        result: Dict[str, Any] | None = cast(
            Dict[str, Any] | None, response_json.get("result")
        )
        if not result or "addressMatches" not in result:
            return None

        # Get the address matches
        address_matches: List[Dict[str, Any]] | None = cast(
            List[Dict[str, Any]] | None, result.get("addressMatches")
        )
        if not address_matches or len(address_matches) == 0:
            return None

        # Get the first address match
        first_address_match: Dict[str, Any] = address_matches[0]
        if "coordinates" not in first_address_match:
            return None

        # Get the coordinates
        coordinates: Dict[str, Any] | None = cast(
            Dict[str, Any] | None, first_address_match.get("coordinates")
        )
        if not coordinates or "x" not in coordinates or "y" not in coordinates:
            return None

        # Get the x and y coordinates
        longitude: Optional[float] = coordinates.get("x")
        latitude: Optional[float] = coordinates.get("y")

        # parse addressComponents
        if "addressComponents" not in first_address_match:
            return None

        address_components: Dict[str, Any] | None = cast(
            Dict[str, Any] | None, first_address_match.get("addressComponents")
        )
        if not address_components:
            return None

        # Get the street number
        # street_number: Optional[str] = address_components.get("fromAddress")
        # street_name: Optional[str] = address_components.get("streetName")
        # street_type: Optional[str] = address_components.get("streetSuffix")
        # pre_type: Optional[str] = address_components.get("preType")
        # pre_direction: Optional[str] = address_components.get("preDirection")
        # pre_qualifier: Optional[str] = address_components.get("preQualifier")
        # suffix_direction: Optional[str] = address_components.get("suffixDirection")
        # suffix_type: Optional[str] = address_components.get("suffixType")
        # suffix_qualifier: Optional[str] = address_components.get("suffixQualifier")
        city: Optional[str] = cast(Optional[str], address_components.get("city"))
        state: Optional[str] = cast(Optional[str], address_components.get("state"))
        postal_code: Optional[str] = cast(Optional[str], address_components.get("zip"))

        # Helper function to clean and concatenate address parts
        def clean_and_concat(*parts: str | Any) -> str:
            return " ".join(filter(None, parts))

        # Construct the address line using all components
        address_line: str = clean_and_concat(
            address_components.get("fromAddress"),
            address_components.get("preQualifier"),
            address_components.get("preDirection"),
            address_components.get("preType"),
            address_components.get("streetName"),
            address_components.get("suffixType"),
            address_components.get("suffixDirection"),
            address_components.get("suffixQualifier"),
        )

        # Get matched address
        matched_address: Optional[str] = first_address_match.get("matchedAddress")

        # Create a new address object
        standardized_address: Address = address.copy()
        if address_line:
            standardized_address.line = [cast(String, address_line)]
        if city:
            standardized_address.city = cast(String, city)
        if state:
            standardized_address.state = cast(String, state)
        if postal_code:
            standardized_address.postalCode = cast(String, postal_code)

        if matched_address:
            standardized_address.text = cast(String, matched_address)

        if latitude and longitude:
            # we use this standard: https://www.hl7.org/implement/standards/fhir/R4B/extension-geolocation.html
            standardized_address.extension = [
                cast(
                    ExtensionType,
                    Extension.parse_obj(
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                            "extension": [
                                {"url": "latitude", "valueDecimal": f"{latitude}"},
                                {"url": "longitude", "valueDecimal": f"{longitude}"},
                            ],
                        }
                    ),
                )
            ]

        return AddressGeoLocatorResult(
            address=cast(AddressType, standardized_address),
            latitude=latitude,
            longitude=longitude,
        )

    @staticmethod
    def standardize_text(*, address: str | None) -> AddressGeoLocatorResult | None:
        """
        Standardize an address

        :param address: Address to standardize
        :return: Standardized address
        """
        if not address:
            return None

        assert isinstance(address, str)

        result = AddressGeoLocator.standardize_single(
            address=cast(AddressType, Address.parse_obj(dict(text=address))),
            verbose=False,
        )

        return result

    @staticmethod
    def standardize_text_simple(*, address: str | None) -> str | None:
        """
        Standardize an address

        :param address: Address to standardize
        :return: Standardized address
        """
        if not address:
            return None

        assert isinstance(address, str)

        result = AddressGeoLocator.standardize_text(address=address)

        return cast(Address, result.address).text if result and result.address else None
