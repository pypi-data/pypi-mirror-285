"""Meta API Integration.."""

import datetime
import json
import logging
from time import sleep
from typing import Any, Dict, List, Tuple, cast
import pytz
from typing_extensions import override

from targeting_platform.platform import ALL_WEEK, ALL_WEEK_BACK, LocationFormats, Platform
from targeting_platform.utils_common import generate_batches
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError
import h3


def _callback_failure(meta_response: Any) -> Any:
    raise meta_response.error()


class PlatformMeta(Platform):
    """Implementation of Meta Activation platform."""

    ACCESS_ROLES = {"ADVERTISE", "MANAGE"}
    _MAX_LOCATION_PER_PLACEMENT: int = 200
    _MAX_LOCATION_RADIUS: int = 80  # km
    _CHUNK_SIZE: int = 50
    _CACHE_TTL: int = 3600  # Seconds

    _API_VERSION: str = "v20.0"
    _api: FacebookAdsApi = None

    @override
    def _set_credentials(self, credentials: Any) -> None:
        """Set platform credentials.

        Args:
        ----
            credentials (Any): Provided credentials. Format: {"access_token": "","app_secret": "","app_id": ""}

        """
        self._credentials: Dict[str, str] = cast(Dict[str, str], credentials)

    @override
    def _is_credentials(self) -> bool:
        """Check if credential is valid and reissue token (or other credentials) if needed.

        Returns
        -------
            bool: if can connect

        """
        if not self._credentials:
            return False
        if not self._api:
            self._api = FacebookAdsApi.init(
                access_token=self._credentials.get("access_token", ""),
                app_id=self._credentials.get("app_id", ""),
                app_secret=self._credentials.get("app_secret", ""),
            )
        return self._api is not None

    def _get_ad_account(self, adaccount_id: str) -> Dict[str, Any]:
        """Get ad accounr information.

        Args:
        ----
            adaccount_id (str): adaccount id

        Returns:
        -------
            dict: Advertiser

        """
        result = {}
        if self._is_credentials():
            response = self._http_session.get(
                f"https://graph.facebook.com/{self._API_VERSION}/{adaccount_id}/",
                headers={
                    "Accept": "application/json",
                },
                params={
                    "access_token": self._credentials["access_token"],
                    "fields": "timezone_id,timezone_name,timezone_offset_hours_utc,currency",
                },
                timeout=None,
            )
            response.raise_for_status()

            if response.status_code == 200:
                result = response.json()
            for item in json.loads(response.headers.get("x-business-use-case-usage", "{}")).get(adaccount_id.replace("act_", ""), []):
                if item["type"] == "ads_management":
                    result["rate_limit"] = item
                    break

        return result

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
        result: list[Any] = []
        if self._is_credentials() and self._credentials.get("app_scoped_system_user_id", ""):
            response = self._http_session.get(
                f"https://graph.facebook.com/{self._API_VERSION}/{self._credentials.get('app_scoped_system_user_id', '')}/",
                headers={"Accept": "application/json"},
                params={"access_token": self._credentials["access_token"], "fields": "assigned_ad_accounts"},
                timeout=None,
            )
            response.raise_for_status()
            roles = set(
                [
                    role
                    for account_roles in response.json().get("assigned_ad_accounts", {}).get("data", [])
                    for role in account_roles.get("tasks", [])
                    if account_roles.get("account_id", "") == first_level_id or account_roles.get("id", "") == first_level_id
                ]
            )
            result = list(roles & self.ACCESS_ROLES)
            if result:
                result = [self._get_ad_account(first_level_id)]
        else:
            result = [self._get_ad_account(first_level_id)]
        logging.info(f"FUNCTION 'validate_credentials': Roles {result}.")
        return bool(result) and bool(result[0])

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
            first_level_id (str): id for main platform identificator to get catalog for.
            second_level_ids (List[str] | None, optional): list of second level elements to get (campaigns e.g.). Defaults to None.
            only_placements (bool, optional): Return only placement in response. Defaults to False.
            no_placements (bool, optional): Does not return placements in response. Defaults to False.
            is_force_update (bool, optional): Force update even if cache is exists. Defaults to False.

        Returns:
        -------
            Dict[str, Any]: platform catalog. Structure {"second_level_items":[{"third_level_items":[{"placements":[]}]}]}.

        """
        response: Dict[str, Any] = {"second_level_items": []}

        def __to_utc_date(date_string: str) -> str:
            return datetime.datetime.fromisoformat(date_string).astimezone(pytz.timezone("UTC")).date().isoformat() if date_string else ""

        if self._is_credentials():
            try:
                if not no_placements:
                    # Get all adsets
                    adsets: List[Any] | None = None if is_force_update else self._cache.get_cache(name="meta_adsets", first_level_id=first_level_id)
                    if adsets is None or is_force_update:
                        results = AdAccount(first_level_id).get_ad_sets(
                            fields=[
                                AdSet.Field.name,
                                AdSet.Field.campaign_id,
                                AdSet.Field.status,
                                AdSet.Field.start_time,
                                AdSet.Field.end_time,
                                AdSet.Field.lifetime_budget,
                                AdSet.Field.source_adset,
                            ]
                        )
                        adsets = [result._json for result in results]
                        self._cache.set_cache(
                            name="meta_adsets",
                            value=adsets,
                            ttl=self._CACHE_TTL,
                            first_level_id=first_level_id,
                        )
                    response_adset: List[Any] = sorted(
                        [result for result in adsets if not second_level_ids or result["campaign_id"] in second_level_ids],
                        key=lambda item: item["name"],
                    )

                # Get currency
                currency: str = ""
                adaccount: Dict[str, Any] | None = None if is_force_update else self._cache.get_cache(name="meta_adaccount", first_level_id=first_level_id)
                if adaccount is None or is_force_update:
                    adaccount = self._get_ad_account(first_level_id)
                    self._cache.set_cache(
                        name="meta_adaccount",
                        value=adaccount,
                        ttl=self._CACHE_TTL,
                        first_level_id=first_level_id,
                    )
                    currency = adaccount.get("currency", "")

                if only_placements and not no_placements:
                    # Only lineitems as dict
                    response = {
                        "placements": {
                            item["id"]: {
                                "id": item["id"],
                                "name": item["name"],
                                "status": item["status"].title(),
                                "budget": f"{currency} {(int(item.get('lifetime_budget', 0)) / 100):.2f}",
                                "channel": "Social",
                                "start_date": __to_utc_date(item.get("start_time", "")),
                                "end_date": __to_utc_date(item.get("stop_time", "")),
                            }
                            for item in response_adset
                        }
                    }
                else:
                    # Prepare intermediate dictionary (need to take names later)
                    campaigns_dict: Dict[str, Any] = {}
                    if not no_placements:
                        for item in response_adset:
                            if item["campaign_id"] not in campaigns_dict:
                                campaigns_dict[item["campaign_id"]] = []
                            campaigns_dict[item["campaign_id"]].append(
                                {
                                    "id": item["id"],
                                    "name": item["name"],
                                    "status": item["status"].title(),
                                    "budget": f"{currency} {(int(item.get('lifetime_budget', 0)) / 100):.2f}",
                                    "channel": "Social",
                                    "start_date": __to_utc_date(item.get("start_time", "")),
                                    "end_date": __to_utc_date(item.get("stop_time", "")),
                                    "is_duplicate": len(item.get("source_adset", [])) > 0,
                                    "is_youtube": False,
                                }
                            )
                    # All campaings
                    # It is fatser to get all in one request and then filter
                    campaigns: List[Any] | None = None if is_force_update else self._cache.get_cache(name="meta_campaigns", first_level_id=first_level_id)
                    if campaigns is None or is_force_update:
                        results = AdAccount(first_level_id).get_campaigns(fields=[Campaign.Field.name, Campaign.Field.start_time, Campaign.Field.stop_time, Campaign.Field.status])
                        campaigns = [result._json for result in results]
                        self._cache.set_cache(
                            name="meta_campaigns",
                            value=campaigns,
                            ttl=self._CACHE_TTL,
                            first_level_id=first_level_id,
                        )

                    response = {
                        "second_level_items": [
                            {
                                "id": campaign["id"],
                                "name": campaign["name"],
                                "status": campaign["status"].title(),
                                "start_date": __to_utc_date(campaign.get("start_time", "")),
                                "end_date": __to_utc_date(campaign.get("stop_time", "")),
                                "third_level_items": [
                                    {
                                        "id": "",
                                        "name": "",
                                        "status": "",
                                        "placements": [] if no_placements else campaigns_dict[campaign["id"]],
                                    }
                                ],
                            }
                            for campaign in campaigns
                            if (no_placements or campaign["id"] in campaigns_dict) and (not second_level_ids or campaign["id"] in second_level_ids)
                        ]
                    }
            except FacebookRequestError as error:
                # Artifitially slowdown
                if error.api_error_code() == 17:
                    sleep(50)
                raise Exception(json.dumps(error.body() | {"rate_limit": self._get_ad_account(first_level_id).get("rate_limit", {})}))

        logging.info(f"FUNCTION 'get_catalog': Catalog size {len(response)} for {first_level_id} ({second_level_ids}).")
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
        cached_values: Dict[str, List[Dict[str, Any]]] | None = (
            None
            if is_force_update
            else self._cache.get_cache(name="meta_get_placements", first_level_id=first_level_id, second_level_id=second_level_id, third_level_id=third_level_id)
        )
        if (cached_values is None or is_force_update) and self._is_credentials():
            try:
                results = Campaign(second_level_id).get_ad_sets(
                    fields=[
                        AdSet.Field.name,
                        AdSet.Field.optimization_goal,
                        AdSet.Field.billing_event,
                        AdSet.Field.lifetime_budget,
                        AdSet.Field.campaign_id,
                        AdSet.Field.start_time,
                        AdSet.Field.end_time,
                        AdSet.Field.status,
                        AdSet.Field.pacing_type,
                        AdSet.Field.source_adset,
                        AdSet.Field.updated_time,
                    ]
                )
                cached_values = {"placements": [result._json for result in results]}
                self._cache.set_cache(
                    name="meta_get_placements",
                    value=cached_values,
                    ttl=self._CACHE_TTL,
                    first_level_id=first_level_id,
                    second_level_id=second_level_id,
                    third_level_id=third_level_id,
                )
            except FacebookRequestError as error:
                logging.error(f"FUNCTION 'get_all_placements': {error}")

        response = cached_values if cached_values else {"placements": []}
        logging.info(f"FUNCTION 'get_all_placements': Catalog size {len(response.get('placements',[]))} for {first_level_id}.{second_level_id}.{third_level_id}.")
        return response

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
        cached_values: Any | None = None if is_force_update else self._cache.get_cache(name="meta_get_placement", first_level_id=first_level_id, placement_id=placement_id)
        if (cached_values is None or is_force_update) and self._is_credentials():
            try:
                result = AdSet(placement_id).api_get(
                    fields=[
                        AdSet.Field.name,
                        AdSet.Field.optimization_goal,
                        AdSet.Field.billing_event,
                        AdSet.Field.lifetime_budget,
                        AdSet.Field.campaign_id,
                        AdSet.Field.start_time,
                        AdSet.Field.end_time,
                        AdSet.Field.status,
                        AdSet.Field.pacing_type,
                        AdSet.Field.source_adset,
                        AdSet.Field.updated_time,
                    ]
                )
                cached_values = result._json
                self._cache.set_cache(
                    name="meta_get_placement",
                    value=cached_values,
                    ttl=self._CACHE_TTL,
                    first_level_id=first_level_id,
                    placement_id=placement_id,
                )
            except FacebookRequestError as error:
                logging.error(f"FUNCTION 'get_placement': {error}")

        response = cast(Dict[str, Any], cached_values) if cached_values else {}
        logging.info(f"FUNCTION 'get_placement': Placement size {len(response)} for {first_level_id}.{placement_id}.")
        return response

    @override
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
        result: List[str] = []
        if self._is_credentials():

            def _callback_success(meta_response: Any) -> None:
                result.append(meta_response.json().get("copied_adset_id", ""))

            if len(suffixes) > 0:
                ads = [ad._json for ad in AdSet(placement_id).get_ads(fields=[Ad.Field.name, Ad.Field.creative, Ad.Field.account_id])]
                for batch_suffixes in generate_batches(suffixes, self._CHUNK_SIZE):
                    api_batch = self._api.new_batch()
                    for suffix in batch_suffixes:
                        # Do not run deep copy as can be error with AdCreatives
                        AdSet(placement_id).create_copy(
                            params={"deep_copy": False, "rename_options": {"rename_suffix": suffix}},
                            batch=api_batch,
                            success=_callback_success,
                            failure=_callback_failure,
                        )
                    api_batch.execute()
                    if ads:
                        for i, new_adset_id in enumerate(result[-len(batch_suffixes) :]):
                            api_batch = self._api.new_batch()
                            for ad in ads:
                                if ad.get("creative", {}).get("id", ""):
                                    AdAccount(f"act_{ad['account_id']}").create_ad(
                                        params={
                                            Ad.Field.name: f"{ad['name']}{batch_suffixes[i]}",
                                            Ad.Field.adset_id: new_adset_id,
                                            Ad.Field.creative: {"creative_id": ad.get("creative", {}).get("id", "")},
                                            Ad.Field.status: Ad.Status.paused,
                                        },
                                        batch=api_batch,
                                        failure=_callback_failure,
                                    )
                            api_batch.execute()
        logging.info(f"FUNCTION 'duplicate_placement': Created duplicates {result} for {first_level_id}.{placement_id} with suffixes ({suffixes}).")
        return result

    @override
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
        if self._is_credentials():
            locks = [self._cache.lock(name="meta_delete_placement", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return []
            for batch_adset_ids in generate_batches(placement_ids, self._CHUNK_SIZE):
                api_batch = self._api.new_batch()
                for adset_id in batch_adset_ids:
                    AdSet(adset_id).api_delete(batch=api_batch, failure=_callback_failure)
                api_batch.execute()
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)
        logging.info(f"FUNCTION 'delete_placement': Deleted {first_level_id} ({placement_ids}).")
        return placement_ids

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
        if self._is_credentials():
            locks = [self._cache.lock(name="meta_pause_placement", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return []
            for batch_adset_ids in generate_batches(placement_ids, self._CHUNK_SIZE):
                api_batch = self._api.new_batch()
                for adset_id in batch_adset_ids:
                    AdSet(adset_id).api_update({AdSet.Field.status: AdSet.Status.paused}, batch=api_batch, failure=_callback_failure)
                api_batch.execute()
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)
        logging.info(f"FUNCTION 'pause_placement': Paused {first_level_id} ({placement_ids}).")
        return placement_ids

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
        placement_ids, _, _ = self.set_targeting_options(
            first_level_id=first_level_id,
            placement_ids=placement_ids,
            locations=[[(51.508283, -0.106669, 1.0)]],
            periods=[[("SUNDAY", (0, 1))]],
            format=LocationFormats.lat_lng,
            is_set_in_each_placement=True,
        )
        logging.info(f"FUNCTION 'clear_placement': Cleared {first_level_id} ({placement_ids}).")
        return placement_ids

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
        response: List[bool] = []
        duplicate_ids: List[str] = []
        local_placement_ids: List[str] = []

        def _callback_success(meta_response: Any) -> Any:
            result = meta_response.json()
            response.append(result["success"])

        if self._is_credentials():
            locks = [self._cache.lock(name="meta_set_targeting_options", first_level_id=first_level_id, placement_id=placement_id) for placement_id in placement_ids]
            if not all(locks):
                # Release only set locks
                for i, lock in enumerate(locks):
                    if not lock:
                        self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_ids[i])
                return [], [], None
            local_placement_ids, duplicate_ids, locations_to_set, periods_to_set = self._prepare_targeting_options(
                first_level_id=first_level_id,
                placement_ids=placement_ids,
                locations=locations,
                periods=periods,
                is_set_in_each_placement=is_set_in_each_placement,
                is_create_duplicates=True,
            )
            i = 0
            for batch_adset_ids in generate_batches(local_placement_ids, self._CHUNK_SIZE):
                api_batch = self._api.new_batch()
                for adset_id in batch_adset_ids:
                    params: Dict[str, Any] = {}
                    if periods_to_set[i]:
                        params["pacing_type"] = ["day_parting"]
                        params["adset_schedule"] = PlatformMeta.to_format_periods(periods=periods_to_set[i])
                    if locations_to_set[i]:
                        params["targeting"] = {"geo_locations": {"custom_locations": PlatformMeta.to_format_locations(locations=locations_to_set[i], format=format)}}
                    AdSet(adset_id).api_update(params=params, batch=api_batch, success=_callback_success, failure=_callback_failure)
                    i += 1
                api_batch.execute()
            # Release locks
            for placement_id in placement_ids:
                self._cache.release_lock(first_level_id=first_level_id, placement_id=placement_id)
        response_placement_ids = [placement_id for i, placement_id in enumerate(local_placement_ids) if response[i]]
        logging.info(f"FUNCTION 'set_targeting_options': All placements ({response_placement_ids}) with duplicates ({duplicate_ids}) for {first_level_id} ({placement_ids}).")
        return response_placement_ids, duplicate_ids, None

    @override
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
            List[Tuple[List[str] | List[Tuple[float, float, float]], List[Tuple[str, Tuple[int, int]]]]]: per each placement - list of locations, list of periods.

        """
        cached_values: List[Tuple[List[str] | List[Tuple[float, float, float]], List[Tuple[str, Tuple[int, int]]]]] = (
            [] if is_force_update else self._cache.get_cache(name="meta_get_targeting_options", first_level_id=first_level_id, placement_ids=placement_ids, format=format)
        )
        local_response: Dict[str, List[Any]] = {}

        def _callback_success(meta_response: Any) -> Any:
            result = meta_response.json()
            if result.get(AdSet.Field.status, "") != AdSet.Status.deleted:
                if result.get("id", ""):
                    if result["id"] not in local_response:
                        local_response[result["id"]] = []
                    local_response[result["id"]].append(result)

        if (cached_values is None or is_force_update) and self._is_credentials():
            cached_values = []
            for batch_adset_ids in generate_batches(placement_ids, self._CHUNK_SIZE):
                api_batch = self._api.new_batch()
                for adset_id in batch_adset_ids:
                    AdSet(adset_id).api_get(fields=[AdSet.Field.status, AdSet.Field.targeting, AdSet.Field.adset_schedule], batch=api_batch, success=_callback_success)
                api_batch.execute()
            for adset_id in placement_ids:
                result = local_response.get(adset_id, [])
                if result:
                    for v in result:
                        cached_values.append(
                            (
                                PlatformMeta.from_format_locations(locations=v.get("targeting", {}).get("geo_locations", {}).get("custom_locations", []), format=format),
                                PlatformMeta.from_format_periods(periods=v.get("adset_schedule", [])),
                            )
                        )
            self._cache.set_cache(
                name="meta_get_targeting_options", value=cached_values, ttl=self._CACHE_TTL, first_level_id=first_level_id, placement_ids=placement_ids, format=format
            )
        logging.info(f"FUNCTION 'get_targeting_options': Result size {len(cached_values)} for {first_level_id} ({placement_ids}) in format {format}.")
        return cached_values

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
        periods_grouped: Dict[Tuple[int, int], list[int]] = {}
        for day_of_week, period in periods:
            if day_of_week in ALL_WEEK:
                if period in periods_grouped:
                    periods_grouped[period].append(ALL_WEEK[day_of_week])
                else:
                    periods_grouped[period] = [ALL_WEEK[day_of_week]]
        logging.info(f"FUNCTION 'to_format_periods': Periods count {len(periods)}.")
        return [
            {
                "start_minute": min(max(period[0], 0), 23) * 60,
                "end_minute": max(min(period[1], 24), 1) * 60,
                "days": days,
                "timezone_type": "ADVERTISER",
            }
            for period, days in periods_grouped.items()
            if period[0] < period[1]
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
        logging.info(f"FUNCTION 'from_format_periods': Periods count {len(periods)}.")
        return [
            (
                ALL_WEEK_BACK[d],
                (
                    period["start_minute"] // 60,
                    period["end_minute"] // 60,
                ),
            )
            for period in periods
            for d in period["days"]
        ]

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
                            "latitude": lat,
                            "longitude": lng,
                            "radius": min(round(LocationFormats.edge_length(str(cell), unit="km"), 3), PlatformMeta._MAX_LOCATION_RADIUS),
                            "distance_unit": "kilometer",
                        }
                    )
                except Exception:
                    logging.error(f"FUNCTION 'to_format_locations': Error with transformation {cell} to format {format}.")
        else:
            for cell in locations:
                lat, lng, radius = tuple(cell)
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    result.append(
                        {
                            "latitude": lat,
                            "longitude": lng,
                            "radius": min(float(str(radius)), PlatformMeta._MAX_LOCATION_RADIUS),
                            "distance_unit": "kilometer",
                        }
                    )
        logging.info(f"FUNCTION 'to_format_locations': Locations count {len(locations)} to format {format}.")
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
        result: List[Any] = [(cell["latitude"], cell["longitude"], cell["radius"] * (1.60934 if cell["distance_unit"] == "mile" else 1.0)) for cell in locations]
        logging.info(f"FUNCTION 'from_format_locations': Locations count {len(locations)} from format {format}.")
        return Platform.location_to_h3(result) if format == LocationFormats.h3 else result
