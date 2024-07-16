"""platform Class."""

from typing import Any, Dict, List, Tuple
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from enum import Enum, auto

from targeting_platform.utils_common import closest_index, flatten_concatenation, generate_batches
from .utils_cache import RedisCache
import h3
from numpy import mean

ALL_WEEK = {
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
    "SUNDAY": 0,
}
ALL_WEEK_BACK = {
    1: "MONDAY",
    2: "TUESDAY",
    3: "WEDNESDAY",
    4: "THURSDAY",
    5: "FRIDAY",
    6: "SATURDAY",
    0: "SUNDAY",
}
H3_RADIUSES = [h3.edge_length(15 - i, unit="km") for i in range(0, 16)]


class LocationFormats(Enum):
    """Location Formats."""

    h3 = auto()
    lat_lng = auto()

    @staticmethod
    def edge_length(cell: str, unit: str) -> float:
        """Get H3 cell edge lenght.

        Args:
        ----
            cell (str): cell index.
            unit (str): units to return lenght.

        Returns:
        -------
            float: H3 cell edge lenght.

        """
        return float(mean([h3.exact_edge_length(v, unit=unit) for v in h3.get_h3_unidirectional_edges_from_hexagon(cell)]))


class Platform:
    """Base class for Targeting platform."""

    ACCESS_ROLES: set[str] = set()
    STATUS_MAPPING: Dict[str, str] = {}
    CHANNELS_MAPPING: Dict[str, str] = {}
    _MAX_LOCATION_PER_PLACEMENT: int = 10000
    _MAX_LOCATION_RADIUS: int = 800  # km
    _CHUNK_SIZE: int = 5000
    _CACHE_TTL: int = 86400  # Seconds
    _RETRIES: int = 10

    _credentials: Any | None = None

    def __init__(self, credentials: Any, retries: int = 0, retries_interval: int = 0, integration_code: str = "", redis_host: str = "localhost:6379") -> None:
        """Create base platform object.

        Args:
        ----
            credentials (Any): platform credentials
            retries (int, optional): Number of retries for HTTP or platform operations. Defaults to 0.
            retries_interval (int, optional): Retries interval in seconds. Applicable for wait for rediness operations. Defaults to 0.
            integration_code (str, optional): Arbitrary string which will be stored in platform items to identify them as created by code. Defaults to "".
            redis_host (str, optional): redis host for read/write. Defaults to "localhost:6379".

        """
        self._retries = retries
        self._retries_interval = retries_interval
        self._integration_code = integration_code

        self._cache = RedisCache(redis_host=redis_host)

        self._http_session = Session()
        self._http_session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=retries,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504, 521],
                    allowed_methods=["GET", "POST", "PUT", "DELETE"],
                )
            ),
        )

        self._set_credentials(credentials)

    def _set_credentials(self, credentials: Any) -> None:
        """Set platform credentials.

        Args:
        ----
            credentials (Any): Provided credentials.

        """
        self._credentials = credentials

    def _is_credentials(self) -> bool:
        """Check if credential is valid and reissue token (or other credentials) if needed.

        Returns
        -------
            bool: if can connect

        """
        return self._credentials is not None

    def validate_credentials(self, first_level_id: str) -> bool:
        """Validate connection to the platform.

        For connection credentials from object will be used.

        Args:
        ----
            first_level_id (str): id for main platform identificator to validate access to.

        Returns:
        -------
            bool: True if platform can be access with current credentials and id

        """
        return True

    def get_locations_max(self) -> int:
        """Return max number of locations per placement.

        Returns
        -------
            int: max number of locations per placement.

        """
        return self._MAX_LOCATION_PER_PLACEMENT

    def get_catalog(
        self,
        first_level_id: str,
        second_level_ids: List[str] | None = None,
        only_placements: bool = False,
        no_placements: bool = False,
        is_force_update: bool = False,
    ) -> Dict[str, Any]:
        """Return catalog of elements for platform.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            second_level_ids (List[str] | None, optional): list of second level elements to get (campaigns e.g.). Defaults to None.
            only_placements (bool, optional): Return only placement in response. Defaults to False.
            no_placements (bool, optional): Does not return placements in response. Defaults to False.
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            Dict[str, Any]: platform catalog. Structure {"second_level_items":[{"third_level_items":[{"placements":[]}]}]}.

        """
        return {}

    def get_all_placements(
        self, first_level_id: str, second_level_id: str | None = None, third_level_id: str | None = None, is_force_update: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all placements.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            second_level_id (str | None, optional): list of second level elements to get (campaigns e.g.). Defaults to None.
            third_level_id (str | None, optional): list of third level elements to get (insertion orders e.g.). Defaults to None.
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            Dict[str, List[Dict[str, Any]]]: placements information.

        """
        return {"placements": []}

    def get_placement(self, first_level_id: str, placement_id: str, is_force_update: bool = False) -> Any:
        """Get placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_id (str): placement id to duplicate.
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            Any: placement object or information.

        """
        return {}

    def duplicate_placement(self, first_level_id: str, placement_id: str, suffixes: List[str]) -> List[str]:
        """Duplicate placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_id (str): placement id to duplicate.
            suffixes (list): suffixes for placement display names. Number of suffixes will produce number of dublicates.

        Returns:
        -------
            list: list of created placement ids.

        """
        return []

    def delete_placement(self, first_level_id: str, placement_ids: List[str]) -> List[str] | Any:
        """Delete placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to delete.

        Returns:
        -------
            list: list of deleted placement ids.

        """
        return placement_ids

    def clear_placement(self, first_level_id: str, placement_ids: List[str]) -> List[str] | Any:
        """Clear placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to clear.

        Returns:
        -------
            list: list of cleared placement ids.

        """
        return placement_ids

    def pause_placement(self, first_level_id: str, placement_ids: List[str]) -> List[str] | Any:
        """Pause placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to pause.

        Returns:
        -------
            list: list of paused placement ids.

        """
        return placement_ids

    def _prepare_targeting_options(
        self,
        first_level_id: str,
        placement_ids: List[str],
        locations: List[List[str] | List[Tuple[float, float, float]]],
        periods: List[List[Tuple[str, Tuple[int, int]]]],
        is_set_in_each_placement: bool = True,
        is_create_duplicates: bool = True,
    ) -> Tuple[List[str], List[str], List[List[str] | List[Tuple[float, float, float]]], List[List[Tuple[str, Tuple[int, int]]]]]:
        """Split targeting options (cardinality os equal to placement_ids array) to be set in placements.

        Also create duplicates if required.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to pause.
            locations (List[List[str] | List[Tuple[float, float, float]]]): list of locations either H3 list or list of (latitude,longitude,radius).
            periods (List[List[Tuple[str, Tuple[int, int]]]]): time periods in format (day_of_week,(start_hour, end_hour)). end_hour is not included.
            is_set_in_each_placement (bool, optional): set the same locations and periods to all placements.
                Locations and periods should have the same size as placement_ids. Defaults to True.
            is_create_duplicates (bool, optional): if to create required duplicates. Default to True.

        Returns:
        -------
            Tuple[List[str], List[str], List[List[str] | List[Tuple[float, float, float]]], List[List[Tuple[str, Tuple[int, int]]]]]:
                list of updated placement ids, list of created placement dublicates ids, splitted location, splitted periods.

        """
        duplicate_ids: List[str] = []
        local_placement_ids: List[str] = []
        if is_set_in_each_placement:
            full_periods = sorted(set(flatten_concatenation(periods)))
            full_locations = sorted(set(flatten_concatenation(locations)))
            local_periods = [full_periods for _ in placement_ids]
            local_locations = [full_locations for _ in placement_ids]
        else:
            local_periods = periods
            local_locations = locations
        # Depends on number of elements in locations split and create duplicates if needed
        locations_to_set: List[Any] = []
        periods_to_set: List[Any] = []
        for i, lineitem_id in enumerate(placement_ids):
            max_locations = self.get_locations_max()
            local_placement_ids.append(lineitem_id)
            if len(local_locations[i]) > max_locations:
                splitted_locations = [location for location in generate_batches(local_locations[i], max_locations)]
                if is_create_duplicates:
                    duplicated_placement_ids = self.duplicate_placement(
                        first_level_id=first_level_id, placement_id=lineitem_id, suffixes=[f" - # {j}" for j in range(len(splitted_locations) - 1)]
                    )
                else:
                    duplicated_placement_ids = [f" - # {j}" for j in range(len(splitted_locations) - 1)]
                duplicate_ids.extend(duplicated_placement_ids)
                local_placement_ids.extend(duplicated_placement_ids)
                periods_to_set.append(local_periods[i])
                for _ in duplicated_placement_ids:
                    periods_to_set.append(local_periods[i])
                for location in splitted_locations:
                    locations_to_set.append(location)
            else:
                locations_to_set.append(local_locations[i])
                periods_to_set.append(local_periods[i])
        return local_placement_ids, duplicate_ids, locations_to_set, periods_to_set

    def set_targeting_options(
        self,
        first_level_id: str,
        placement_ids: List[str],
        locations: List[List[str] | List[Tuple[float, float, float]]],
        periods: List[List[Tuple[str, Tuple[int, int]]]],
        format: LocationFormats = LocationFormats.h3,
        is_set_in_each_placement: bool = True,
    ) -> Tuple[List[str], List[str], Any]:
        """Set targeting into placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to pause.
            locations (List[List[str] | List[Tuple[float, float, float]]]): list of locations either H3 list or list of (latitude,longitude,radius).
            periods (List[List[Tuple[str, Tuple[int, int]]]]): time periods in format (day_of_week,(start_hour, end_hour)). end_hour is not included.
            format (LocationFormats, optional): format of locations. Default: LocationFormats.h3
            is_set_in_each_placement (bool, optional): set the same locations and periods to all placements.
                Locations and periods should have the same size as placement_ids. Defaults to True.

        Returns:
        -------
            Tuple[List[str], List[str]]: list of updated placement ids, list of created placement dublicates ids.

        """
        return placement_ids, [], None

    def get_targeting_options(
        self, first_level_id: str, placement_ids: List[str], format: LocationFormats = LocationFormats.h3, is_force_update: bool = False
    ) -> List[Tuple[List[str] | List[Tuple[float, float, float]], List[Tuple[str, Tuple[int, int]]]]]:
        """Get targeting for placement.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to pause.
            format (LocationFormats, optional): format of locations. Default: LocationFormats.h3
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            List[Tuple[List[str] | List[Tuple[float, float, float]]], List[Tuple[str, Tuple[int, int]]]]]: per each placement - list of locations, list of periods.

        """
        return []

    def validate_targeting_options(
        self,
        first_level_id: str,
        placement_ids: List[str],
        locations: List[List[str] | List[Tuple[float, float, float]]],
        periods: List[List[Tuple[str, Tuple[int, int]]]],
        format: LocationFormats = LocationFormats.h3,
        is_force_update: bool = False,
    ) -> List[Tuple[bool, bool]]:
        """Validate targeting options in placements.

        Args:
        ----
            first_level_id (str): id for main platform identificator to get catalog for.
            placement_ids (List[str]): placement ids to pause.
            locations (List[List[str] | List[Tuple[float, float, float]]]): list of locations either H3 list or list of (latitude,longitude,radius).
            periods (List[List[Tuple[str, Tuple[int, int]]]]): time periods in format (day_of_week,(start_hour, end_hour)). end_hour is not included.
            format (LocationFormats, optional): format of locations. Default: LocationFormats.h3
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            List[Tuple[bool, bool]]: list of validation statuses for placement ids - (is_cottect_locations,is_correct_periods).

        """
        result: List[Tuple[bool, bool]] = []
        targeting_options = self.get_targeting_options(first_level_id=first_level_id, placement_ids=placement_ids, format=format)
        for i, targeting_option in enumerate(targeting_options):
            result.append((set(locations[i]) == set(targeting_option[0]), set(periods[i]) == set(targeting_option[1])))
        return result

    @staticmethod
    def to_format_periods(periods: List[Tuple[str, Tuple[int, int]]]) -> List[Any]:
        """Return datetime periods in platform format.

        Args:
        ----
            periods (List[Tuple[str, Tuple[int, int]]]): periods in format (day_of_week,(start_hour, end_hour)).

        Returns:
        -------
            List[Any]: periods in platform format.

        """
        return periods

    @staticmethod
    def from_format_periods(periods: List[Any]) -> List[Tuple[str, Tuple[int, int]]]:
        """Return datetime periods in generic format.

        Args:
        ----
            periods (List[Any]): periods in platform format.

        Returns:
        -------
            List[Tuple[str, Tuple[int, int]]]: periods in generic format (day_of_week,(start_hour, end_hour)).

        """
        return periods

    @staticmethod
    def to_format_locations(locations: List[str] | List[Tuple[float, float, float]], format: LocationFormats = LocationFormats.h3) -> List[Any]:
        """Return locations in platform format.

        Args:
        ----
            locations (List[str] | List[Tuple[float, float, float]]): list of locations either H3 list or list of (latitude,longitude,radius).
            format (LocationFormats, optional): format of locations. Default: LocationFormats.h3

        Returns:
        -------
            List[Any]: locations in platform format.

        """
        return locations

    @staticmethod
    def from_format_locations(locations: List[Any], format: LocationFormats = LocationFormats.h3) -> List[str] | List[Tuple[float, float, float]]:
        """Return location in requested format.

        Args:
        ----
            locations (List[Any]): locations in platform format.
            format (LocationFormats, optional): format of locations. Default: LocationFormats.h3

        Returns:
        -------
            List[str] | List[Tuple[float, float, float]]: locations in requested format.

        """
        return locations

    @staticmethod
    def location_to_h3(locations: List[Tuple[float, float, float]]) -> List[str]:
        """Return locations in Uber H3 format.

        H3 level is selected based on radius. Incorrect lat and lng are filtered out.

        Args:
        ----
            locations (List[Tuple[float, float, float]]): locations in format (lat,lng,radius). Radius is in kilometers.


        Returns:
        -------
            List[str]: list of H3.

        """
        return [h3.geo_to_h3(v[0], v[1], 15 - closest_index(H3_RADIUSES, v[2])) for v in locations if -90 <= v[0] <= 90 and -180 <= v[1] <= 180]
