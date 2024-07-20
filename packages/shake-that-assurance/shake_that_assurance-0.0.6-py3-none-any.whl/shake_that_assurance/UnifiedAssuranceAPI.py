import logging
import requests, json
from time import sleep

class UnifiedAssuranceAPI:
    """Unified Assurance API wrapper."""

    def __init__(self, endpoint: str, username: str, password: str, log_level=logging.INFO) -> None:
        """Initialize with required parameters."""

        self.ua_api_username = username or input("Enter Unified Assurance API username: ")
        self.ua_api_password = password or input("Enter Unified Assurance API password: ")
        self.ua_endpoint = endpoint or input("Enter Unified Assurance API endpoint: ")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    def _handle_response(self, ua_request: requests.Response) -> dict:
        """Handle response from Unified Assurance API."""

        try:
            ua_request.raise_for_status()
            return ua_request.json()
        except Exception as e:
            raise requests.exceptions.RequestException(f"API error: {e}")

    def _get(self, api_path: str, ua_params: dict = {}, max_attempts = 1) -> dict:
        """Get data from Unified Assurance API."""

#       max_attempts = 3
        backoff_time = 5  # seconds
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    self.ua_endpoint + api_path,
                    auth=(self.ua_api_username, self.ua_api_password),
                    params=ua_params,
                    headers={"Accept": "application/json"},
                )
                # Check HTTP status code for success (200 range)
                if response.status_code // 100 == 2:
                    return self._handle_response(response)
                else:
                    logging.warning(f"HTTP error {response.status_code}: {response.text}")

            except Exception as e:
                logging.warning(f"Request failed: {e}")

            # Log failed attempt
            logging.warning(f"Attempt {attempt + 1} failed. Retrying...")

            # Sleep before next attempt, with a maximum wait time of 120 seconds
            sleep_time = min(backoff_time * (2 ** attempt), 120)
            if attempt < max_attempts - 1:
                sleep(sleep_time)
            else:
                logging.error(f"Failed to get data after {max_attempts} attempts")
                return {}

    def _post(self, api_path: str, request_body: dict, max_attempts = 1) -> dict:
        """Post data to Unified Assurance API."""

#       max_attempts = 6
        backoff_time = 3  # seconds
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    self.ua_endpoint + api_path,
                    auth=(self.ua_api_username, self.ua_api_password),
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=json.dumps(request_body),
                )
                # Check HTTP status code for success (200 range)
                if response.status_code // 100 == 2:
                    response_data = response.json()
                    if response_data.get("success"):  # Assuming 'success' is a boolean field in the response
                        return response_data
                    else:
                        logging.warning(f"API responded with failure: {response.text}")
                else:
                    logging.warning(f"HTTP error {response.status_code}: {response.text}")

            except Exception as e:
                logging.warning(f"Request failed: {e}")

            logging.warning(f"Attempt {attempt + 1} failed. Retrying...")
            sleep_time = min(backoff_time * (2 ** attempt), 120)
            if attempt < max_attempts - 1:
                sleep(sleep_time)
            else:
                logging.error(f"Failed to post data after {max_attempts} attempts")

        # Return an empty dict or raise an exception if all attempts fail
        logging.error("All attempts to post data have failed.")
        return {}

    def _put(self, api_path: str, request_body: dict, max_attempts=1) -> dict:
        """Put data to Unified Assurance API."""

        backoff_time = 3  # seconds
        for attempt in range(max_attempts):
            try:
                response = requests.put(
                    self.ua_endpoint + api_path,
                    auth=(self.ua_api_username, self.ua_api_password),
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=json.dumps(request_body),
                )
                # Check HTTP status code for success (200 range)
                if response.status_code // 100 == 2:
                    response_data = response.json()
                    if response_data.get("success"):
                        return response_data
                    else:
                        logging.warning(f"API responded with failure: {response.text}")
                else:
                    logging.warning(f"HTTP error {response.status_code}: {response.text}")

            except Exception as e:
                logging.warning(f"Request failed: {e}")

            logging.warning(f"Attempt {attempt + 1} failed. Retrying...")
            sleep_time = min(backoff_time * (2 ** attempt), 120)
            if attempt < max_attempts - 1:
                sleep(sleep_time)
            else:
                logging.error(f"Failed to put data after {max_attempts} attempts")

        # If the loop completes without breaking (success), log and return an error or empty dict
        logging.error("All attempts to put data have failed.")
        return {}

    def test_authentication(self) -> bool:
        """Test the Unified Assurance API authentication."""

        try:
            response = self._get('/api/core/globalProperties')
            if 'success' in response and response['success'] is True:
                logging.info("Authentication successful.")
                return True
            else:
                logging.error("Authentication failed.")
                return False
        except Exception as e:
            logging.error(f"Exception occurred while testing authentication: {e}")
            return False

    def get_groups(self) -> list:
        """Get all device groups from Unified Assurance API."""

        request_params = {
            "readChildren": "true",
        }
        groups_response = self._get("/api/device/groups/1", request_params, 3)
        if not groups_response.get('success'):
            logging.error(f"Failed to retrieve groups: {groups_response.get('message')}")
            return []

        # sort by the zone name, "casefold" is case insensitive
        return sorted(groups_response['data'], key=lambda item: item['DisplayName'].casefold())

    def get_zones(self) -> list:
        """Get all device zones from Unified Assurance API."""

        request_params = {
            "limit": 1000,
        }
        zones_response = self._get("/api/device/zones", request_params, 3)
        if not zones_response.get('success'):
            logging.error(f"Failed to retrieve zones: {zones_response.get('message')}")
            return []

        # sort by the zone name, "casefold" is case insensitive
        return sorted(zones_response['data'], key=lambda item: item['DeviceZoneName'].casefold())

    def get_broker_servers(self) -> list:
        request_params = {
            "limit": 1000,
            "page": 1,
            "start": 0,
        }
        ua_response = self._get("/api/broker/servers", request_params, 3)
        if not isinstance(ua_response, dict):
            logging.debug(ua_response)
            raise Exception(f"ua_response is not a dict: {ua_response}")
        elif not ua_response.get('success'):
            logging.warning( f"assure1 get_devices Exception:\n{ua_response.text}")
            raise Exception("ua_response was not successful")

        return ua_response['data']

    """Testing:
    ua_api.get_devices('zayotelemetry-us-east-2a.federos-collectors.qosdevops.com', by_name=True)
    company_devices = ua_api.get_devices("federos-collectors.qosdevops.com", by_name=True)
    company_devices = ua_api.get_devices("Suez", by_group=True)
    """
    def get_devices(self, filter_value: str, by_group=False, by_name=False, by_zone=False, by_ip=False, page_size = 1000) -> list:
        """Get all devices from Unified Assurance API, handling pagination."""

        # Determine the filtering property based on method arguments
        if by_name:
            device_property = "DeviceName"
        elif by_zone:
            device_property = "DeviceZoneName"
        elif by_group:
            device_property = "DeviceGroupName"
        elif by_ip:
            device_property = "IPAddress"
        else:
            logging.error("A device filter property must be specified.")
            return []

        page = 1
        devices = []
        has_more_pages = True

        while has_more_pages:
            filter_params = {
                "property": device_property,
                "operator": "like",
                "type": "string",
                "value": filter_value,
            }
            sort_params = {
                "property": device_property,
                "direction": "ASC",
            }

            request_params = {
                "filter": json.dumps([filter_params], separators=(',', ':')),
                "sort": json.dumps([sort_params], separators=(',', ':')),
                "limit": page_size,
                "page": page,
                "start": (page - 1) * page_size,
            }

            ua_response = self._get("/api/device/devices", request_params, 3)
            if not isinstance(ua_response, dict):
                logging.debug(ua_response)
                raise Exception(f"Unified Assurance response is not a dict: {ua_response}")
            elif not ua_response.get('success'):
                logging.warning(f"Unified Assurance get_devices Exception:\n{ua_response.get('message', 'No message available')}")
                raise Exception("Unified Assurance response was not successful")

            # Add the retrieved devices to our list
            devices.extend(ua_response['data'])

            # Check if we've gotten all devices
            if len(ua_response['data']) < page_size:
                has_more_pages = False
            else:
                page += 1  # Prepare for the next iteration/page
                logging.info(f"Retrieved {len(devices)} devices for {filter_value} so far...")

        return devices

    def get_meta_type_id(self, meta_type_name: str) -> str:
        """Get the meta type ID for a given meta type name."""

        response = self._get('/api/device/metaTypes', {}, 3)
        if not response.get('success'):
            logging.error(f"Failed to retrieve meta types: {response}")
            raise ValueError(f"Failed to retrieve meta types: {response}")
        for meta_type in response.get('data'):
            if meta_type['DeviceMetaTypeName'] == meta_type_name:
                return meta_type['DeviceMetaTypeID']
        

    def add_device(self, device: dict, group_name:str, zone_name: str, snmp_profile = "") -> dict:
        """Add a device to Unified Assurance."""

        # get the ID for the given group and zone name using list comprehensions, selecting the first result ([0])
        zone_matches = [zone['DeviceZoneID'] for zone in self.get_zones() if zone['DeviceZoneName'] == zone_name]
        if not zone_matches:
            logging.error(f"Zone {zone_name} not found.")
            return dict()
        zone_id = zone_matches[0]

        group_matches = [group['DeviceGroupID'] for group in self.get_groups() if group['DisplayName'] == group_name]
        if not group_matches:
            logging.error(f"Group {group_name} not found.")
            return dict()
        group_id = group_matches[0]

        sys_id_matches = [d['MetaData'] for d in device['MetaData'] if d['DeviceMetaTypeName'] == 'sys_id']
        if sys_id_matches:
            sys_id = sys_id_matches[0]
            meta_type_id = self.get_meta_type_id("sys_id")
            if not meta_type_id:
                logging.error("Transient error, unable to obtain meta type for sys_id. Please try again.")
                return dict()
            device_metadata = [{
                "DeviceMetaTypeID": meta_type_id,
                "DeviceMetaTypeName": "sys_id",
                "MetaData": sys_id,
                "RenderType": "1",
            }]
        else:
            logging.error("No sys_id was found in device metadata. Refusing to add device.")
            return dict()

        # Forward slashes break UA Events, result in alerts not sending to BP
        custom_name = device["CustomName"].replace("/", "-")

        post_body = {
            "DeviceZoneID": zone_id,
            "InitialDeviceGroupID": group_id,
            "DeviceStateID": 2, # Verified, ie. let it be re-discovered by the new collector
            "IPv4": device["IPv4"],
            "IPv6": device["IPv6"] or "", # cannot be null
            "CustomName": custom_name,
            "DeviceSNMPAccessID": snmp_profile,
            "DeviceTypeCategoryID": device["DeviceTypeCategoryID"] or 0, # cannot be blank
            "DevicePriorityID": device["DevicePriorityID"],
            "MetaData": device_metadata,
            "ShardID": 1,
        }
        
        # UA prefers DNSName over IP addresses, and many DNSnames are incorrect
        if not device["IPv4"]:
            post_body["DNSName"] = device["DNSName"]
        
        logging.info(post_body)
        return self._post("/api/device/devices", post_body)

    def update_device_sys_id(self, id: int, sys_id: str) -> dict:
        """Update a device sys_id in Unified Assurance with the value from CMDB."""

        logging.debug(f"Update Device ID: {id}")
        assert id > 0, "Numeric Device ID is required."
        post_body = {
            "MetaData": [{
                "DeviceMetaTypeID": 1001,
                "DeviceMetaTypeName": "sys_id",
                "MetaData": sys_id,
                "RenderType": "1",
            }],
        }
        logging.debug(post_body)
        put_result = self._put(f"/api/device/devices/{id}", post_body)
        if put_result.get('errors'):
            logging.error(f"Failed to update record: {put_result['errors']}")
            return dict()
        return put_result

    def update_device_field(self, ua_id: int, cmdb_device: dict, ua_field: str, cmdb_field: str) -> dict:
        """Update a device field in Unified Assurance with the value from CMDB

        Updating one field like the IP address wipes out the MetaData. So we always need to update sys_id too.
        """

        logging.info(f"ID: {ua_id}")
        assert ua_id > 0, "Device ID is required."
        post_body = {
#           "DeviceName": device['name'],
            ua_field: cmdb_device[cmdb_field],
            "MetaData": [{
                "DeviceMetaTypeID": 1001,
                "DeviceMetaTypeName": "sys_id",
                "MetaData": cmdb_device['sys_id'],
                "RenderType": "1",
            }],
        }
        logging.debug(post_body)
        put_result = self._put(f"/api/device/devices/{ua_id}", post_body)
        if put_result.get('errors'):
            logging.error(f"Failed to update record: {put_result['errors']}")
            return dict()
        logging.info(f"++ Fixed name: {cmdb_device['name']} ip: {cmdb_device['ip_address']}, sys_id: {cmdb_device['sys_id']}")
        return put_result

    def update_device_ip(self, id: int, device: dict) -> dict:
        """Update a device IP address in Unified Assurance with the value from CMDB.
        
        Updating one field like the IP address wipes out the MetaData. So we always need to update sys_id too.
        """

        post_body = {
            "IPv4": device['ip_address'],
            "MetaData": [{
                "DeviceMetaTypeID": 1001,
                "DeviceMetaTypeName": "sys_id",
                "MetaData": device['sys_id'],
                "RenderType": "1",
            }],
        }
        put_result = self._put(f"/api/device/devices/{id}", post_body)
        if not put_result.get('success'):
            logging.error(f"Failed to update record: {put_result['message']}")
            return dict()
        logging.info(f"Updated IP address for {device['name']} to {device['ip_address']}.")
        return put_result

    def delete_device(self, id: int) -> dict:
        """Delete a device from Unified Assurance."""

        assert id > 0, "Device ID is required."
        api_path = f"/api/device/devices/{id}"
        ua_response = requests.delete(
            self.ua_endpoint + api_path,
            auth=(self.ua_api_username, self.ua_api_password),
            headers={"Accept": "application/json"},
        )
        result = json.loads(ua_response.text)
        if not result.get('success'):
            logging.error(f"Failed to update record: {result['message']}")
            return dict()
        return result

    # ua_api.create_zone()
    def create_zone(self, zone_name = "") -> dict:
        """Create a device zone in Unified Assurance."""

        if not zone_name:
            zone_name = input("Please enter a zone name: ")

        if self.zone_exists(zone_name):
            logging.error(f"Zone {zone_name} already exists.")
            return {
                "success": True,
                "message": f"Zone {zone_name} already exists.",
                }

        post_body = {
            "DeviceZoneName": zone_name,
        }
        logging.debug(post_body)
        return self._post("/api/device/zones", post_body)

    def zone_exists(self, zone_name: str) -> bool:
        """Check if a zone with the given name already exists."""

        response = self._get("/api/device/zones", {}, 3)
        if response.get('success'):
            zones = response.get('data', [])
            for zone in zones:
                if zone.get('DeviceZoneName') == zone_name:
                    return True
        else:
            logging.error(f"Failed to retrieve device zones: {response.get('message')}")
            exit(1)
        return False

    def create_group(self, group_name = "") -> dict:
        """Create a device group in Unified Assurance."""

        if not group_name:
            group_name = input("Please enter a group name: ")

        if self.group_exists(group_name):
            logging.error(f"Group {group_name} already exists.")
            return {
                "success": True,
                "message": f"Group {group_name} already exists.",
                }

        post_body = {
            "DeviceGroupName": group_name,
            "ParentDeviceGroupID": 1,
            "Devices": [],
        }
        logging.debug(post_body)
        return self._post("/api/device/groups", post_body)
    
    def group_exists(self, group_name: str) -> bool:
        """Check if a group with the given name already exists."""

        groups = self.get_groups()
        for group in groups:
            if group.get('DisplayName') == group_name:
                return True
        return False

    def get_broker_job(self, search_field: str, collector_fqdn: str) -> dict:
        """Get an existing broker job that is on the Broker Control > Jobs page.

        Example:
        select_broker_job("Device Auto Discover", "beggarspizza-us-east-2.federos-collectors.qosdevops.com")
        Returns a dictionary of the job details.
        """

        search_filter = [{
            "property": "JobName",
            "value": search_field,
            "type": "string",
            "operator": "like"
        }]
        request_params = {'filter': json.dumps(search_filter)}
        ua_jobs = self._get('/api/broker/jobs', request_params)

        if not ua_jobs.get('success'):
            return ua_jobs

        for result in ua_jobs.get('data'):
            if result['ServerName'] == collector_fqdn:
                return result

    def ensure_device_type_category(self, category_name: str, category_icon = None) -> str:
        """Get a device type category ID or create it if it does not exist.
        
        Returns the ID of the category.
        """

        device_type_category = {
            'DeviceTypeCategoryName': category_name,
            'ImageName': category_icon
        }

        api_path = "/api/device/categories"
        response = self._get(api_path)
        if response.get("success"):
            current_categories = response.get("data")

            for category in current_categories:
                if category['DeviceTypeCategoryName'] == category_name:
                    logging.debug(f"Category was found: {category_name}")
                    return category["DeviceTypeCategoryID"]

            # If the category does not exist, create it.
            response = self._post(api_path, device_type_category)
            if response.get("success"):
                logging.info(f"Added category: {category_name}")
                return response["data"][0]["DeviceTypeCategoryID"]
            else:
                logging.error(response)
