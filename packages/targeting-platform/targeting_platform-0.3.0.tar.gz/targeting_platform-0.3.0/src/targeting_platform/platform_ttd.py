"""The Trade Desk (TTD) API Integration."""

from time import sleep
from typing import Any, Dict, List, Set, Tuple, cast
from requests import HTTPError
from typing_extensions import override
from targeting_platform.platform import ALL_WEEK, ALL_WEEK_BACK, LocationFormats, Platform
from targeting_platform.utils_common import get_time_periods
import h3


class PlatformTTD(Platform):
    """Implementation of The Trade Desk (TTD) Activation platform."""

    CHANNELS_MAPPING: Dict[str, str] = {
        "Other": "Display",
        "Display": "Display",
        "Video": "Video",
        "Audio": "Audio",
        "Native": "Display",
        "NativeDisplay": "Display",
        "NativeVideo": "Video",
        "TV": "Connected TV",
        "TVPersonal": "Connected TV",
        "OutOfHome": "DOOH",
        "Mixed": "Display",
    }
    _MAX_LOCATION_PER_PLACEMENT: int = 10000
    _MAX_LOCATION_RADIUS: int = 100000  # km
    _CHUNK_SIZE: int = 10000
    _CACHE_TTL: int = 86400  # Seconds

    @override
    def _set_credentials(self, credentials: Any) -> None:
        """Set platform credentials.

        Args:
        ----
            credentials (Any): Provided credentials. Format: {"api_url":"","partner_id":"","token":"","login":"","password":""}.

        """
        self._credentials: Dict[str, Any] = credentials
        self._api_headers = {
            "Content-Type": "application/json",
            "TTD-Auth": self._credentials.get("token", ""),
        }
        self._API_URL = self._credentials.get("api_url", "")

    @override
    def _is_credentials(self) -> bool:
        """Check if credential is valid and reissue token if needed.

        Returns
        -------
            bool: if can connect.

        """
        if not self._API_URL or not self._credentials.get("token", ""):
            return False
        response = self._http_session.post(
            f"{self._API_URL}introspectToken",
            headers=self._api_headers,
            timeout=None,
        )
        if response.status_code != 200:
            # Get new token
            if self._credentials:
                response = self._http_session.post(
                    f"{self._API_URL}authentication",
                    json={
                        "Login": self._credentials.get("login", ""),
                        "Password": self._credentials.get("password", ""),
                        "TokenExpirationInMinutes": 1440,
                    },
                    timeout=None,
                )
                if response.status_code == 200:
                    self._api_headers = {
                        "Content-Type": "application/json",
                        "TTD-Auth": response.json().get("Token", ""),
                    }
                else:
                    raise Exception(response.text)
            else:
                return False
        return True

    def _get_advertizer(self, advertizer_id: str, is_force_update: bool = False) -> Dict[str, Any]:
        """Get advertiser information from platform.

        Args:
        ----
            advertizer_id (str): advertizer_id.
            is_force_update (bool): force to update from API even if already in cache.

        Returns:
        -------
            Dict[str, Any]: Advertiser information.

        """
        partner_id = self._credentials.get("partner_id", "")
        cached_values: Dict[str, Any] | None = None if is_force_update else self._cache.get_cache(name="ttd_advertiser", partner_id=partner_id)
        if (cached_values is None or is_force_update) and self._is_credentials():
            response = self._http_session.post(
                f"{self._API_URL}delta/advertiser/query/partner",
                headers=self._api_headers,
                json={
                    "PartnerId": partner_id,
                    "ReturnEntireAdvertiser": True,
                    "LastChangeTrackingVersion": cached_values.get("LastChangeTrackingVersion", None) if cached_values else None,
                },
                timeout=None,
            )
            response.raise_for_status()

            result = response.json()
            if result.get("Advertisers", []):
                # There is new data
                new_advertisers = {advertiser["AdvertiserId"]: advertiser for advertiser in result.get("Advertisers", [])}
                if cached_values:
                    cached_values["Advertisers"].update(new_advertisers)
                    cached_values["LastChangeTrackingVersion"] = result["LastChangeTrackingVersion"]
                else:
                    cached_values = {
                        "Advertisers": new_advertisers,
                        "LastChangeTrackingVersion": result["LastChangeTrackingVersion"],
                    }
            self._cache.set_cache(
                name="ttd_advertiser",
                value=cached_values,
                ttl=self._CACHE_TTL,
                partner_id=partner_id,
            )
        return cast(Dict[str, Any], cached_values.get("Advertisers", {}).get(advertizer_id, {})) if cached_values else {}

    def _get_advertiser_campaigns(self, advertizer_id: str, is_force_update: bool = False) -> Dict[str, Any]:
        """Get Campaigns information from platform.

        Args:
        ----
            advertizer_id (str): advertizer_id.
            is_force_update (bool): force to update from API even if already in cache.


        Returns:
        -------
            Dict[str, Any]: Campaigns information.

        """
        cached_values: Dict[str, Any] | None = None if is_force_update else self._cache.get_cache(name="ttd_advertiser_campaigns", advertizer_id=advertizer_id)
        if (cached_values is None or is_force_update) and self._is_credentials():
            response = self._http_session.post(
                f"{self._API_URL}delta/campaign/query/advertiser",
                headers=self._api_headers,
                json={
                    "AdvertiserId": advertizer_id,
                    "ReturnEntireCampaign": True,
                    "LastChangeTrackingVersion": cached_values.get("LastChangeTrackingVersion", None) if cached_values else None,
                },
                timeout=None,
            )
            response.raise_for_status()

            result = response.json()
            if result.get("Campaigns", []):
                # There is new data
                new_campaigns = {campaign["CampaignId"]: campaign for campaign in result.get("Campaigns", [])}
                if cached_values:
                    cached_values["Campaigns"].update(new_campaigns)
                    cached_values["LastChangeTrackingVersion"] = result["LastChangeTrackingVersion"]
                else:
                    cached_values = {
                        "Campaigns": new_campaigns,
                        "LastChangeTrackingVersion": result["LastChangeTrackingVersion"],
                    }

            self._cache.set_cache(
                name="ttd_advertiser_campaigns",
                value=cached_values,
                ttl=self._CACHE_TTL,
                advertizer_id=advertizer_id,
            )

        return cast(Dict[str, Any], cached_values.get("Campaigns", {})) if cached_values else {}

    def _get_advertiser_adgroups(self, advertizer_id: str, is_force_update: bool = False) -> Dict[str, Any]:
        """Get AdGroups information from platform.

        Args:
        ----
            advertizer_id (str): advertizer_id.
            is_force_update (bool): force to update from API even if already in cache.


        Returns:
        -------
            Dict[str, Any]: AdGroups information.

        """
        cached_values: Dict[str, Any] | None = None if is_force_update else self._cache.get_cache(name="ttd_advertiser_adgroups", advertizer_id=advertizer_id)
        if (cached_values is None or is_force_update) and self._is_credentials():
            response = self._http_session.post(
                f"{self._API_URL}delta/adgroup/query/advertiser",
                headers=self._api_headers,
                json={
                    "AdvertiserId": advertizer_id,
                    "ReturnEntireAdGroup": True,
                    "IncludeTemplates": False,
                    "LastChangeTrackingVersion": cached_values.get("LastChangeTrackingVersion", None) if cached_values else None,
                },
                timeout=None,
            )
            result = response.json()
            if result.get("AdGroups", []):
                # There is new data
                new_adgroups = {adgroup["AdGroupId"]: adgroup for adgroup in result.get("AdGroups", [])}
                if cached_values:
                    cached_values["AdGroups"].update(new_adgroups)
                    cached_values["LastChangeTrackingVersion"] = result["LastChangeTrackingVersion"]
                else:
                    cached_values = {
                        "AdGroups": new_adgroups,
                        "LastChangeTrackingVersion": result["LastChangeTrackingVersion"],
                    }

            self._cache.set_cache(
                name="ttd_advertiser_adgroups",
                value=cached_values,
                ttl=self._CACHE_TTL,
                advertizer_id=advertizer_id,
            )

        return cast(Dict[str, Any], cached_values.get("AdGroups", {})) if cached_values else {}

    def _get_adgroup_budget(self, adgroup: Dict[str, Any]) -> float:
        """Get AdGroup budget value.

        Args:
        ----
            adgroup (Dict[str, Any]): adgroup information.

        Returns:
        -------
            float: budget value, 0 if not set.

        """
        return float(adgroup.get("RTBAttributes", {}).get("BudgetSettings", {}).get("Budget", {}).get("Amount", 0))

    @override
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
        advertizer = self._get_advertizer(advertizer_id=first_level_id, is_force_update=True)
        return bool(advertizer)

    @override
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
            first_level_id (str): iadvertiser id.
            second_level_ids (List[str] | None, optional): list of campaign ids. Defaults to None.
            only_placements (bool, optional): Return only placement in response. Defaults to False.
            no_placements (bool, optional): Does not return placements in response. Defaults to False.
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            Dict[str, Any]: platform catalog. Structure {"second_level_items":[{"third_level_items":[{"placements":[]}]}]}.

        """
        response: Dict[str, Any] = {}

        advertizer = self._get_advertizer(advertizer_id=first_level_id, is_force_update=is_force_update)
        adgroups = self._get_advertiser_adgroups(advertizer_id=first_level_id, is_force_update=is_force_update) if not no_placements else {}

        currency = advertizer.get("CurrencyCode", "")

        if only_placements:
            response = {
                "placements": {
                    item["AdGroupId"]: {
                        "id": item["AdGroupId"],
                        "name": item["AdGroupName"],
                        "status": "Enabled" if item["IsEnabled"] else "Disabled",
                        "budget": f"{currency} {self._get_adgroup_budget(item):.2f}",
                        "channel": self.CHANNELS_MAPPING.get(item["ChannelId"], item["ChannelId"]),
                        "start_date": "",
                        "end_date": "",
                    }
                    for item in adgroups.values()
                    if (not second_level_ids or item["CampaignId"] in second_level_ids) and item["Availability"] != "Archived"
                }
            }
        else:
            campaigns_dict: Dict[str, List[Dict[str, Any]]] = {}
            for item in adgroups.values():
                if (not second_level_ids or item["CampaignId"] in second_level_ids) and item["Availability"] != "Archived":
                    if item["CampaignId"] not in campaigns_dict:
                        campaigns_dict[item["CampaignId"]] = []
                    campaigns_dict[item["CampaignId"]].append(
                        {
                            "id": item["AdGroupId"],
                            "name": item["AdGroupName"],
                            "status": "Enabled" if item["IsEnabled"] else "Disabled",
                            "budget": f"{currency} {self._get_adgroup_budget(item):.2f}",
                            "channel": self.CHANNELS_MAPPING.get(item["ChannelId"], item["ChannelId"]),
                            "is_duplicate": False,
                            "is_youtube": False,
                        }
                    )
            campaigns = self._get_advertiser_campaigns(advertizer_id=first_level_id, is_force_update=is_force_update) if not only_placements else {}
            response = {
                "second_level_items": [
                    {
                        "id": campaign["CampaignId"],
                        "name": campaign["CampaignName"],
                        "status": campaign["Availability"],
                        "start_date": campaign.get("StartDate", "")[:10],
                        "end_date": campaign.get("EndDate", "")[:10],
                        "third_level_items": [
                            {
                                "id": "",
                                "name": "",
                                "status": "",
                                "placements": [
                                    placement
                                    | {
                                        "start_date": campaign.get("StartDate", "")[:10],
                                        "end_date": campaign.get("EndDate", "")[:10],
                                    }
                                    for placement in campaigns_dict.get(campaign["CampaignId"], [])
                                ],
                            }
                        ],
                    }
                    for campaign in campaigns.values()
                    if (not second_level_ids or campaign["CampaignId"] in second_level_ids) and campaign["Availability"] != "Archived"
                ]
            }

        return response

    @override
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
        adgroups = self._get_advertiser_adgroups(advertizer_id=first_level_id, is_force_update=is_force_update)
        return {"placements": [item for item in adgroups.values() if not second_level_id or item["CampaignId"] == second_level_id]}

    @override
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
        cached_values: Dict[str, Any] | None = (
            None if is_force_update else self._cache.get_cache(name="ttd_get_placement", first_level_id=first_level_id, placement_id=placement_id)
        )
        if (cached_values is None or is_force_update) and self._is_credentials():
            response = self._http_session.get(
                f"{self._API_URL}adgroup/{placement_id}",
                headers=self._api_headers,
                timeout=None,
            )
            if response.status_code == 200:
                cached_values = response.json()
                self._cache.set_cache(
                    name="ttd_get_placement",
                    value=cached_values,
                    ttl=self._CACHE_TTL,
                    first_level_id=first_level_id,
                    placement_id=placement_id,
                )
        return cached_values if cached_values else {}

    @override
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
        local_placement_ids: List[str] = []
        if self._is_credentials():
            locks = [self._cache.lock(name="ttd_clear_placement", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return []
            adgroups = self._get_advertiser_adgroups(advertizer_id=first_level_id, is_force_update=True)

            for placement_id in placement_ids:
                adgroup = adgroups.get(placement_id, {})

                # Clear time / only one can be and we clear it
                bilistids = [
                    bidlist["BidListId"] for bidlist in adgroup.get("AssociatedBidLists", []) if "HasHourOfWeek" in bidlist.get("BidListDimensions", [] and bidlist["IsEnabled"])
                ]
                if bilistids:
                    try:
                        for bilistid in bilistids:
                            response = self._http_session.delete(
                                f"{self._API_URL}bidlist/{bilistid}",
                                headers=self._api_headers,
                                timeout=None,
                            )
                            if response.status_code == 200:
                                if placement_id not in local_placement_ids:
                                    local_placement_ids.append(placement_id)
                    except HTTPError:
                        # Silent fail
                        pass
                else:
                    if placement_id not in local_placement_ids:
                        local_placement_ids.append(placement_id)
                # Get location
                audienceid = adgroup.get("RTBAttributes", {}).get("AudienceTargeting", {}).get("AudienceId", "")
                if audienceid:
                    try:
                        need_update = False
                        datagroup_ids: Set[str] = set()
                        # Need to check if audience has other datagroups
                        audience_response = self._http_session.get(
                            f"{self._API_URL}audience/{audienceid}",
                            headers=self._api_headers,
                            timeout=None,
                        )
                        if audience_response.status_code == 200:
                            audience = audience_response.json()
                            existing_datagroup_ids = set(audience.get("IncludedDataGroupIds", []) + audience.get("ExcludedDataGroupIds", []))
                            for existing_datagroup_id in existing_datagroup_ids:
                                datagroup_response = self._http_session.get(
                                    f"{self._API_URL}datagroup/name/{existing_datagroup_id}",
                                    headers=self._api_headers,
                                    timeout=None,
                                )
                                if datagroup_response.status_code == 200:
                                    # Identify if we have created datagroup by it's name
                                    if datagroup_response.json().get("name", "") == placement_id:
                                        need_update = True
                                        datagroup_ids.add(existing_datagroup_id)
                        if need_update:
                            # Only remove DataGroup added by us
                            response = self._http_session.put(
                                f"{self._API_URL}audience",
                                headers=self._api_headers,
                                json={
                                    "AudienceId": audienceid,
                                    "IncludedDataGroupIds": list(set(audience.get("IncludedDataGroupIds", [])) - datagroup_ids),
                                },
                                timeout=None,
                            )
                        else:
                            # Put newly created Audience
                            response = self._http_session.put(
                                f"{self._API_URL}adgroup",
                                headers=self._api_headers,
                                json={"AdGroupId": placement_id, "RTBAttributes": {"AudienceTargeting": {"AudienceId": None}}},
                                timeout=None,
                            )

                        if response.status_code == 200:
                            if placement_id not in local_placement_ids:
                                local_placement_ids.append(placement_id)
                    except HTTPError:
                        # Silent fail
                        pass
                else:
                    if placement_id not in local_placement_ids:
                        local_placement_ids.append(placement_id)

            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)

        return local_placement_ids

    @override
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
        result: List[str] = []
        if self._is_credentials():
            locks = [self._cache.lock(name="ttd_pause_placement", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return []
            for adgroup_id in placement_ids:
                response = self._http_session.put(
                    f"{self._API_URL}adgroup",
                    headers=self._api_headers,
                    json={"AdGroupId": adgroup_id, "IsEnabled": False},
                    timeout=None,
                )
                response.raise_for_status()
                if response.status_code == 200:
                    result.append(adgroup_id)
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)

        return result

    def prepare_targeting_options(
        self,
        first_level_id: str,
        placement_ids: List[str],
        locations: List[List[str] | List[Tuple[float, float, float]]],
        periods: List[List[Tuple[str, Tuple[int, int]]]],
        format: LocationFormats = LocationFormats.h3,
        is_set_in_each_placement: bool = True,
    ) -> Tuple[List[str], List[List[str]]]:
        """Prepare entities for targeting options.

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
            Tuple[List[str], List[List[str]]]: list per precement bidlist ids, thirdpartydata ids

        """
        bidlist_ids: List[str] = []
        thirdpartydata_ids: List[List[str]] = []

        if self._is_credentials():
            locks = [self._cache.lock(name="ttd_prepare_targeting_options", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return bidlist_ids, thirdpartydata_ids

            local_placement_ids, _, locations_to_set, _ = self._prepare_targeting_options(
                first_level_id=first_level_id,
                placement_ids=placement_ids,
                locations=locations,
                periods=periods,
                is_set_in_each_placement=is_set_in_each_placement,
                is_create_duplicates=False,
            )
            if periods:
                # Create BidLists
                for _ in range(int(self._RETRIES)):
                    response = self._http_session.post(
                        f"{self._API_URL}bidlist/batch",
                        headers=self._api_headers,
                        json=[
                            {
                                "Name": placement_id,
                                "BidListAdjustmentType": "TargetList",
                                "BidListOwner": "AdGroup",
                                "BidListOwnerId": placement_id,
                                "IsAvailableForLibraryUse": False,
                                "BidLines": PlatformTTD.to_format_periods(periods=periods[i]),
                            }
                            for i, placement_id in enumerate(placement_ids)
                            if periods[i]
                        ],
                        timeout=None,
                    )
                    if response.status_code == 200:
                        bidlist_ids = [bidlist["BidListId"] for bidlist in response.json()]
                        break
                    if response.status_code == 429:
                        sleep(int(response.headers["retry-after"]))
                    else:
                        # If error return empty bidlists ids
                        pass
            last_placement_id: str = ""
            local_thirdpartydata_ids: List[str] = []
            for i, placement_id in enumerate(local_placement_ids):
                if placement_id in placement_ids:
                    last_placement_id = placement_id
                    if local_thirdpartydata_ids:
                        thirdpartydata_ids.append(list(local_thirdpartydata_ids))
                    local_thirdpartydata_ids = []
                if locations_to_set[i]:
                    # Create geofences
                    for _ in range(int(self._RETRIES)):
                        response = self._http_session.post(
                            f"{self._API_URL}selfservegeofence",
                            headers=self._api_headers,
                            json={
                                "AdvertiserId": first_level_id,
                                "DisplayName": f"{last_placement_id}_{i+1}",
                                "Points": PlatformTTD.to_format_locations(locations=locations_to_set[i], format=format),
                            },
                            timeout=None,
                        )
                        if response.status_code == 200:
                            thirdpartydata = response.json()
                            local_thirdpartydata_ids.append(f"{thirdpartydata['ThirdPartyDataId']}|{thirdpartydata['ThirdPartyDataBrandId']}")
                            break
                        if response.status_code == 429:
                            sleep(int(response.headers["retry-after"]))
                        else:
                            # If error return empty thirdpartydata ids
                            pass
            if local_thirdpartydata_ids:
                thirdpartydata_ids.append(list(local_thirdpartydata_ids))
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)
        return bidlist_ids, thirdpartydata_ids

    @override
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
        local_placement_ids: List[str] = []
        bidlist_ids, thirdpartydata_ids = self.prepare_targeting_options(
            first_level_id=first_level_id, placement_ids=placement_ids, locations=locations, periods=periods, format=format, is_set_in_each_placement=is_set_in_each_placement
        )
        if self._is_credentials():
            locks = [self._cache.lock(name="ttd_set_targeting_options", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return [], [], None

            for i, placement_id in enumerate(placement_ids):
                datagroupid: str = ""
                if thirdpartydata_ids and thirdpartydata_ids[i]:
                    delay_seconds = 60
                    # Geofence not availiable immediatly, need to wait
                    for _ in range(int(self._RETRIES) * 2):
                        response = self._http_session.post(
                            f"{self._API_URL}datagroup",
                            headers=self._api_headers,
                            json={
                                "AdvertiserId": first_level_id,
                                "DataGroupName": placement_id,
                                "ThirdPartyDataIds": thirdpartydata_ids[i],
                            },
                            timeout=None,
                        )
                        if response.status_code == 200:
                            datagroupid = response.json()["DataGroupId"]
                            break
                        elif response.status_code == 429:
                            sleep(int(response.headers["retry-after"]))
                        else:
                            # Wait if geofences became availiable
                            sleep(min(600, delay_seconds))
                            delay_seconds = delay_seconds * 2

                new_audienceid: str = ""
                updated_adgroupids = []
                if datagroupid:
                    adgroups = self._get_advertiser_adgroups(advertizer_id=first_level_id, is_force_update=True)
                    adgroup_update: Dict[str, Any] = {"AdGroupId": placement_id}
                    adgroup = adgroups.get(placement_id, {})
                    # Update existing BidLists
                    associatedbidlists = [
                        associatedbidlist for associatedbidlist in adgroup.get("AssociatedBidLists", []) if "HasHourOfWeek" not in associatedbidlist["BidListDimensions"]
                    ]
                    if bidlist_ids and bidlist_ids[i]:
                        adgroup_update.update(
                            {
                                "AssociatedBidLists": associatedbidlists
                                + [
                                    {
                                        "BidListId": bidlist_ids[i],
                                        "IsEnabled": True,
                                    }
                                ]
                            }
                        )
                    # # Get existing audiences
                    # audienceid = adgroup.get("RTBAttributes", {}).get("AudienceTargeting", {}).get("AudienceId", "")

                    # Always create new Audience for now

                    audienceid = None  # Always create new Audience for now
                    if audienceid is None:
                        # Create new audience if not
                        if not new_audienceid:
                            response = self._http_session.post(
                                f"{self._API_URL}audience",
                                headers=self._api_headers,
                                json={
                                    "AdvertiserId": first_level_id,
                                    "AudienceName": placement_id,
                                    "IncludedDataGroupIds": [datagroupid],
                                },
                                timeout=None,
                            )
                            if response.status_code == 200:
                                new_audienceid = response.json()["AudienceId"]
                        adgroup_update.update({"RTBAttributes": {"AudienceTargeting": {"AudienceId": new_audienceid}}})
                    # else:
                    #     audience_response = self._http_session.get(
                    #         f"{self._API_URL}audience/{audienceid}",
                    #         headers=self._api_headers,
                    #         timeout=None,
                    #     )
                    #     if audience_response.status_code == 200:
                    #         audience = audience_response.json()
                    #         # Update existing audience with datagroup
                    #         response = self._http_session.put(
                    #             f"{self._API_URL}audience",
                    #             headers=self._api_headers,
                    #             json={
                    #                 "AudienceId": audienceid,
                    #                 "IncludedDataGroupIds": audience.get("IncludedDataGroupIds", []) + [datagroupid],
                    #             },
                    #             timeout=None,
                    #         )

                    # Finally update adgroup
                    response = self._http_session.put(
                        f"{self._API_URL}adgroup",
                        headers=self._api_headers,
                        json=adgroup_update,
                        timeout=None,
                    )
                    if response.status_code == 200:
                        updated_adgroupids.append(response.json()["AdGroupId"])
                        local_placement_ids.append(placement_id)
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)
        return local_placement_ids, [], None

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
        cached_values: List[Tuple[List[str] | List[Tuple[float, float, float]], List[Tuple[str, Tuple[int, int]]]]] = (
            [] if is_force_update else self._cache.get_cache(name="ttd_get_targeting_options", first_level_id=first_level_id, placement_ids=placement_ids, format=format)
        )
        if (cached_values is None or is_force_update) and self._is_credentials():
            cached_values = []

            adgroups = self._get_advertiser_adgroups(advertizer_id=first_level_id, is_force_update=is_force_update)
            for adgroup_id in placement_ids:
                adgroup = adgroups.get(adgroup_id, {})
                locations: List[str] = []
                periods: List[Tuple[str, Tuple[int, int]]] = []
                if adgroup:
                    # Get time
                    bilistids = [
                        bidlist["BidListId"]
                        for bidlist in adgroup.get("AssociatedBidLists", [])
                        if "HasHourOfWeek" in bidlist.get("BidListDimensions", [] and bidlist["IsEnabled"])
                    ]
                    if bilistids:
                        try:
                            response = self._http_session.post(
                                f"{self._API_URL}bidlist/batch/get",
                                headers=self._api_headers,
                                json=bilistids,
                                timeout=None,
                            )
                            if response.status_code == 200:
                                periods = PlatformTTD.from_format_periods(
                                    [
                                        bidline
                                        for item in response.json().get("BatchResponses", {}).values()
                                        if "Response" in item
                                        for bidline in item["Response"].get("BidLines", [])
                                    ]
                                )
                        except HTTPError:
                            # IF error return nothing
                            pass

                    # With currebt API we can get only ID of datagroups, not locations itself
                    # Disabled code for now
                    # # Get location
                    # audienceid = adgroup.get("RTBAttributes", {}).get("AudienceTargeting", {}).get("AudienceId", "")
                    # if audienceid:
                    #     try:
                    #         response = self.http_session.get(
                    #             f"{self._API_URL}audience/{audienceid}",
                    #             headers=self._api_headers,
                    #             timeout=None,
                    #         )
                    #         if response.status_code == 200:
                    #             audience = response.json()
                    #             # Expand datagroups
                    #             datagroups = {item["DataGroupId"]: item for item in self._get_advertiser_datagroups(advertizer_id, True)}
                    #             audience["IncludedDataGroupIds"] = [datagroups.get(datagroupid, datagroupid) for datagroupid in audience["IncludedDataGroupIds"]]
                    #             audience["ExcludedDataGroupIds"] = [datagroups.get(datagroupid, datagroupid) for datagroupid in audience["ExcludedDataGroupIds"]]
                    #     except HTTPError:
                    #         # IF error return nothing
                    #         pass
                cached_values.append((locations, periods))
            self._cache.set_cache(
                name="ttd_get_targeting_options", value=cached_values, ttl=self._CACHE_TTL, first_level_id=first_level_id, placement_ids=placement_ids, format=format
            )
        return cached_values

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
            # TTD does not have API to get all geofences (as location persisted), so always True for locations
            result.append((True, set(periods[i]) == set(targeting_option[1])))
        return result

    @override
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
        return [
            {
                "HourOfWeek": hour + ALL_WEEK[day_of_week] * 24,
            }
            for day_of_week, (start_hour, end_hour) in periods
            for hour in range(min(max(start_hour, 0), 23), max(min(end_hour, 24), 1))
            if start_hour < end_hour and day_of_week in ALL_WEEK
        ]

    @override
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
        grouped_days: Dict[str, List[int]] = {}
        for period in periods:
            dow = ALL_WEEK_BACK[period["HourOfWeek"] // 24]
            if dow in grouped_days:
                grouped_days[dow].append(period["HourOfWeek"] % 24)
            else:
                grouped_days[dow] = [period["HourOfWeek"] % 24]

        generic_periods = {k: get_time_periods(v) for k, v in grouped_days.items()}

        return [(k, v_) for k, v in generic_periods.items() for v_ in v]

    @override
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
        result: List[Any] = []
        if format == LocationFormats.h3:
            for cell in locations:
                try:
                    lat, lng = h3.h3_to_geo(cell)
                    result.append(
                        {
                            "LatDeg": lat,
                            "LngDeg": lng,
                            "RadMet": min(int(LocationFormats.edge_length(str(cell), unit="m")), PlatformTTD._MAX_LOCATION_RADIUS),
                        }
                    )
                except Exception:
                    pass
        else:
            for cell in locations:
                lat, lng, radius = tuple(cell)
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    result.append(
                        {
                            "LatDeg": lat,
                            "LngDeg": lng,
                            "RadMet": min(int(str(radius)), PlatformTTD._MAX_LOCATION_RADIUS),
                        }
                    )
        return result

    @override
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
        result: List[Any] = [(cell["LatDeg"], cell["LngDeg"], round(cell["RadMet"] / 1000, 3)) for cell in locations]
        return Platform.location_to_h3(result) if format == LocationFormats.h3 else result
