import requests
import json
from typing import Union
from .about import get_client_user_agent

class UltraApi:
    def __init__(self, bu: str, pr: str = None, use_token: bool = False, debug: bool = False, pprint: bool = False, user_agent: str = None):
        """Initialize the client.

        Parameters:
        - bu (str): Either username or bearer token based on `use_token` flag.
        - pr (str, optional): Either password or refresh token based on `use_token` flag. Defaults to None.
        - use_token (bool, optional): If True, treats `bu` as bearer token and `pr` as refresh token. Defaults to False.
        - debug (bool, optional): If True, prints debug information. Defaults to False.
        - pprint (bool, optional): If True, prints JSON responses in a more human-readable format. Defaults to False.
        - user_agent (str, optional): The user agent to use. Defaults to None.

        Raises:
        - ValueError: If `pr` is not provided when `use_token` is True.
        """
        self.base_url = "https://api.ultradns.com"
        self.access_token = str()
        self.refresh_token = str()
        self.debug = debug
        self.pprint = pprint
        self.user_agent = user_agent

        if use_token:
            self.access_token = bu
            self.refresh_token = pr
            if not self.refresh_token:
                print(
                    "Warning: Passing a Bearer token with no refresh token means the client state will expire after an hour.")
        else:
            if not pr:
                raise ValueError("Password is required when providing a username.")
            self._auth(bu, pr)

    def _auth(self, username: str, password: str):
        """Authenticate using username and password.

        Returns:
        - dict: The response body.

        Raises:
        - Exception: If the status is an error.
        """
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        resp = requests.post(f"{self.base_url}/authorization/token", data=payload)
        resp.raise_for_status()
        self.access_token = resp.json().get('accessToken')
        self.refresh_token = resp.json().get('refreshToken')

    def _refresh(self):
        """Refresh the access token using the refresh token.

        Raises:
        - Exception: If the refresh token is not set.

        Returns:
        - dict: The response body.
        """
        if self.refresh_token:
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            resp = requests.post(f"{self.base_url}/authorization/token", data=payload)
            resp.raise_for_status()
            self.access_token = resp.json().get('accessToken')
            self.refresh_token = resp.json().get('refreshToken')
        else:
            raise Exception("Error: Your token cannot be refreshed.")

    def _headers(self, content_type: str = None) -> dict:
        """Generate request headers.

        Parameters:
        - content_type (str, optional): The content type of the request. Defaults to None.

        Returns:
        - dict: The request headers.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        else:
            headers["User-Agent"] = get_client_user_agent()

        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def toggle_debug(self):
        """Toggle debug mode. When this is enabled, the client will print verbose request information."""
        if self.debug:
            self.debug = False
            print("Debug mode disabled.")
        else:
            self.debug = True
            print("Debug mode enabled.")

    def toggle_pprint(self):
        """Toggle pretty print mode. When this is enabled, the client will print JSON responses in a more human-readable
        format.

        This will return a string instead of a dict, so if you want to use the JSON it will need to be loaded back into
        a dict. This is useful for debugging, but should not be used in production.
        """
        if self.pprint:
            self.pprint = False
            print("Pretty print mode disabled.")
        else:
            self.pprint = True
            print("Pretty print mode enabled.")

    def set_user_agent(self, user_agent: str):
        """Set the user agent to use.

        Parameters:
        - user_agent (str): The user agent to use.
        """
        print(f"User agent set to '{user_agent}'")
        self.user_agent = user_agent

    def post(self, uri: str, payload: str = None, plain_text: bool = False) -> Union[dict, str, bytes]:
        """Make a POST request.

        Parameters:
        - uri (str): The URI to call.
        - payload (str, optional): The payload to send. Defaults to None.

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        return self._call(uri, "POST", payload=payload, plain_text=plain_text)

    def put(self, uri: str, payload: str, plain_text: bool = False) -> Union[dict, str, bytes]:
        """Make a PUT request.

        Parameters:
        - uri (str): The URI to call.
        - payload (string): The payload to send.

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        return self._call(uri, "PUT", payload=payload, plain_text=plain_text)

    def patch(self, uri: str, payload: str, plain_text: bool = False) -> Union[dict, str, bytes]:
        """Make a PATCH request.

        Parameters:
        - uri (str): The URI to call.
        - payload (string): The payload to send.

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        return self._call(uri, "PATCH", payload=payload, plain_text=plain_text)

    def get(self, uri: str, params: dict = {}, content_type: str = None) -> Union[dict, str, bytes]:
        """Make a GET request.

        Parameters:
        - uri (str): The URI to call.
        - params (dict, optional): Query parameters. Defaults to {}.
        - content_type (str, optional): The content type of the request. Defaults to None.

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        # GET requests should always be x-www-form-urlencoded, but the UDNS endpoints inexplicably require "application/json"
        if content_type:
            return self._call(uri, "GET", params=params, content_type=content_type)
        else:
            return self._call(uri, "GET", params=params)

    def delete(self, uri: str, content_type: str = None) -> Union[dict, str, bytes]:
        """Make a DELETE request.

        Parameters:
        - uri (str): The URI to call.
        - content_type (str, optional): The content type of the request. Defaults to None.

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        # DELETE requests should, also, always be x-www-form-urlencoded (but of course they're not)
        if content_type:
            return self._call(uri, "DELETE", content_type=content_type)
        else:
            return self._call(uri, "DELETE")

    def _call(self, uri: str, method: str, params: dict = None, payload: dict = None, retry: bool = True, content_type: str = "application/json", plain_text: bool = False) -> Union[dict, str, bytes]:
        """Make an API call.

        Parameters:
        - uri (str): The URI to call.
        - method (str): The HTTP method to use.
        - params (dict, optional): Query parameters. Defaults to None.
        - payload (dict, optional): The payload to send. Defaults to None.
        - retry (bool, optional): Whether to retry the request if the access token has expired. Defaults to True.
        - content_type (str, optional): The content type of the request. Defaults to "application/json".

        Returns:
        - Union[dict, str, bytes]: The response body.
        """
        # Debugging
        if self.debug:
            debug_info ={
                "headers": self._headers(content_type),
                "method": method,
                "url": self.base_url+uri,
                "params": params,
                "payload": payload,
                "payload_type": type(payload).__name__,
                "retry": retry,
                "access_token": self.access_token,
                "refresh_token": self.refresh_token
            }
            print(f"Debug info: {json.dumps(debug_info, indent=4)}")

        # While uncommon, when dealing with records that have / characters in the name, you need to use a unicode string
        # representation of that character. This is a hacky way to do that. First, dump the json payload to a string,
        # then use the replace method to replace instances of "/" with "\u002F". If you load it back into a dict, it
        # reinterprets the unicode as the literal character. Instead, you need to use the "data" parameter of the
        # requests module and send it as a string. There may be other cases where this is necessary, but I haven't
        # encountered them yet. By default, this is disabled and the payload is sent as a dict.
        if plain_text:
            resp = requests.request(method, self.base_url+uri, params=params, data=payload, headers=self._headers(content_type))
        else:
            resp = requests.request(method, self.base_url+uri, params=params, json=payload, headers=self._headers(content_type))

        if resp.status_code == requests.codes.NO_CONTENT:
            # DELETE requests and a few other things return no response body
            if self.pprint:
                return json.dumps({"status_code": resp.status_code, "message": "No content"}, indent=4)
            else:
                return {'status_code': resp.status_code, 'message': 'No content'}

        # I discovered that certain endpoints return no content type, so I'm adding this to prevent errors
        if 'Content-Type' not in resp.headers:
            resp.headers['Content-Type'] = 'None'

        if resp.headers['Content-Type'] == 'application/zip':
            # Return the bytes. Zone exports return zip files
            return resp.content

        if resp.headers['Content-Type'] == 'text/plain':
            # Return plain text. If you request a zone export with 1 domain, it returns a plain text zone file
            return resp.text

        if resp.status_code == requests.codes.ACCEPTED:
            # If there's a task ID in the header, add it to the JSON so the result can be retrieved
            response_data = {}
            if resp.content:  # Check if the response content is not empty
                response_data = resp.json()
            if 'X-Task-Id' in resp.headers:  # Check if the header is present
                response_data.update({"task_id": resp.headers['X-Task-Id']})
            if 'Location' in resp.headers:
                response_data.update({"location": resp.headers['Location']})
            return response_data

        if resp.status_code == 401 and retry:
            # Refresh the token if it expired, then try again
            self._refresh()
            return self._call(uri, method, params=params, payload=payload, retry=False, content_type=content_type, plain_text=plain_text)

        # Raise any error statuses. Since the UDNS API also produces a response body in most cases, print that too
        try:
            resp.raise_for_status()
        except Exception as e:
            if resp.text and self.debug:
                print(f"Message: {resp.text}")
            raise

        # Everything else should be JSON (hopefully)
        if resp.content:  # Check if the response content is not empty
            if self.pprint:
                return json.dumps(resp.json(), indent=4)
            else:
                return resp.json()
        else:
            return None  # or an appropriate default value or message
