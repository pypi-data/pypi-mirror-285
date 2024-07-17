"""
Strava API Handler
"""
from functools import lru_cache
from typing import Dict, Generator, List, Optional

import requests

# from tenacity import retry, stop_after_attempt, wait_fixed
from core_library.utilities.misc_utils import setup_console_logger

mds_logger = setup_console_logger()


class StravaHandler:
    """
    Strava Handler for communicating with API
    """

    def __init__(
        self,
        strava_client_id: str,
        strava_client_secret: str,
        grant_type: str,
        code: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        """Init class for the API

        Args:
            strava_client_id (str): Strava API Client ID
            strava_client_secret (str): Strava API Client Secret
            code (Optional[str], optional): Strava API Code for authorization_code
            refresh_token (Optional[str], optional): Refresh Token if using the refresh_token grant_type
            grant_type (Optional[str], optional): _description_. Defaults to "authorization_code".
        """
        mds_logger.info("Initiallizing the Strava client")
        self.strava_client_id = strava_client_id
        self.strava_client_secret = strava_client_secret
        self.code = code
        self.grant_type = grant_type
        self.refresh_token = refresh_token
        self.base_url = "https://www.strava.com/api/v3/"

    # TODO: implement a _post method for getting the data
    @lru_cache(maxsize=100)
    # TODO: I have to fix this for pytest (retry)
    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def generate_token(self) -> dict:
        """
        Gets a Stava API Bearer Token and associated data

        Returns:
            dict: _description_
        """

        mds_logger.info("Generating a Strava API Token")

        if self.grant_type == "authorization_code" and self.code is not None:
            # Construct URL
            url = (
                f"{self.base_url}oauth/token?client_id={self.strava_client_id}"
                f"&client_secret={self.strava_client_secret}"
                f"&grant_type={self.grant_type}&code={self.code}"
            )
        # refresh_token
        elif self.grant_type == "refresh_token" and self.refresh_token is not None:
            # Construct URL
            url = (
                f"{self.base_url}oauth/token?client_id={self.strava_client_id}"
                f"&client_secret={self.strava_client_secret}"
                f"&grant_type={self.grant_type}&refresh_token={self.refresh_token}"
            )

        else:
            raise Exception(
                "Please pass in either (authorization_code and code) or (refresh_token and refresh_token)"
            )
        # Make the Call
        response = requests.post(
            url=url,
            headers={},
            data={},
        )
        # Call Failed
        if response.status_code != 200:
            raise Exception(
                "Failed to generate Stava Token \n"
                f"status code: {response.status_code} \n"
                f"response: {response.text}"
            )
        # Parse response
        response = response.json()

        if "access_token" in response:
            return response.get("access_token")
        raise Exception("No token found in response")

    def get_api_headers(self) -> dict:
        """
        Returns the API Headers needed for the call
        """
        return {"Authorization": f"Bearer {self.generate_token()}"}

    def get_athlete(self) -> List:
        """
        Get Athelete Data - Includes basic information on athlete

        :yield: Data from API Call
        :rtype: Generator[dict, None, None]
        """

        mds_logger.info("Fetching Athlete Data")
        data = self._get(endpoint="athlete")

        return list(data)

    def get_equipment(self, ids: List[str]) -> List:
        """
        Equipment Data of stats on the equipment.

        :param ids: List of equipemnt id from strava
        :type ids: List[str]
        :return: data
        :rtype: dict
        """
        lod = []
        for id in ids:
            mds_logger.info(f"Fetching Equpment Data - {id}")
            data = self._get(endpoint=f"gear/{id}")
            lod.append(next(data))
        return lod

    def get_athlete_stats(self, ids: List[str]) -> List:
        """
        Get Athlets Stats

        :param id: athelete_id (must be same as authenticated athlete)
        :type id: str
        :return: data from api
        :rtype: dict
        """
        lod = []
        for id in ids:
            mds_logger.info("Fetching Athlete Stats Data")
            data = self._get(endpoint=f"athletes/{id}/stats")
            lod.append(next(data))
        return lod

    def get_activities(
        self,
        before_epoch: Optional[int] = None,
        after_epoch: Optional[int] = None,
        per_page: Optional[int] = 100,
    ) -> Generator[List[Dict], None, None]:
        """
        Get activity data from the authorized athlete

        :param before_epoch: Epoch timestamp to retreive data from before that time, defaults to None
        :type before_epoch: Optional[int], optional
        :param after_epoch: Epoch timestamp to retreive data from after that time, defaults to None
        :type after_epoch: Optional[int], optional
        :param per_page: Number of activities to return in call, defaults to None

        :yield: Data from API
        :rtype: Generator[List[Dict], None, None]
        """
        mds_logger.info("Fetching Athelete Activities")

        query_params = {}

        # Format the Query Params
        if per_page:
            query_params["per_page"] = per_page
        if before_epoch:
            query_params["before"] = before_epoch
        if after_epoch:
            query_params["after"] = after_epoch

        data = self._get(endpoint="athlete/activities", query_params=query_params)
        yield from data

    def _get(self, endpoint: str, query_params: Optional[Dict] = None) -> Generator:
        """
        Helper Method for get requests

        :param endpoint: endpoint that gets added to base url
        :type endpoint: str
        :raises Exception: Failed API Call
        :return: API Data returned
        :rtype: dict
        """
        url = f"{self.base_url}{endpoint}"
        mds_logger.info(f"Get Request: {url} - params {query_params}")
        headers = self.get_api_headers()

        response = requests.get(url, headers=headers, params=query_params)

        if response.status_code == 200:
            yield response.json()

        elif response.status_code != 200:
            raise ValueError(
                f"Failed API call with Get request: {response.status_code}\n"
                f"text: {response.text}"
            )
