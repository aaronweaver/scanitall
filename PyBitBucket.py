import json
import requests
from requests.auth import HTTPBasicAuth
import requests.exceptions
import requests.packages.urllib3
from xml.etree import cElementTree as ET

#from . import __version__ as version

class PyBitBucket(object):
    """A very basci API wrapper for BitBucket.
    https://confluence.atlassian.com/bitbucket/use-the-bitbucket-cloud-rest-apis-222724129.html
    V1 https://confluence.atlassian.com/bitbucket/version-1-423626337.html
    V2 https://developer.atlassian.com/bitbucket/api/2/reference/resource/
    """

    def __init__(self, user, password, api_version='v1', verify_ssl=True, timeout=60, proxies=None, user_agent=None, cert=None, debug=False):
        """Initialize a BitBucket.

        :param user: The BitBucket user, App passwords recommended.
        :param api_version: API version to call, the default is v1.
        :param verify_ssl: Specify if API requests will verify the host's SSL certificate, defaults to true.
        :param timeout: HTTP timeout in seconds, default is 30.
        :param proxies: Proxy for API requests.
        :param user_agent: HTTP user agent string, default is "BitBucket Enterprise_api/[version]".
        :param cert: You can also specify a local cert to use as client side certificate, as a single file (containing
        the private key and the certificate) or as a tuple of both file's path
        :param debug: Prints requests and responses, useful for debugging.

        """
        version = "0.2"
        self.user = user
        self.password = password
        self.host = "https://api.bitbucket.org/"
        self.api_version = api_version
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self.timeout = timeout

        if not user_agent:
            self.user_agent = 'PyBitBucket/v' + version
        else:
            self.user_agent = user_agent

        self.cert = cert
        self.debug = debug  # Prints request and response information.

        if not self.verify_ssl:
            requests.packages.urllib3.disable_warnings()  # Disabling SSL warning messages if verification is disabled.

    def get_all_repos_v1(self):
        """Lists the public and private repositories of the user

        """
        return self._request('GET', "1.0/user/repositories")

    def get_all_repos_public(self):
        """Lists the public repositories

        """
        return self._request('GET', "2.0/repositories/epxengineering")

    def get_all_repos(self, user):
        """Lists the private repositories of the user/group/team

        """
        page_results = {0 : self._request('GET', "2.0/repositories/" + user).json() }
        results = page_results
        page_url = results[0]["next"]

        i = 0
        while "next" in page_results[i]:
            url = page_results[i]["next"].replace("https://api.bitbucket.org/2.0/","")
            #print url
            i = i + 1
            page_results = {i : self._request('GET', "2.0/" + url).json() }
            results.update(page_results)

        return results

    def _request(self, method, url, params=None, data=None, files=None):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        if data:
            data = json.dumps(data)

        headers = {
            'User-Agent': self.user_agent
        }

        if not files:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'

        if self.proxies:
            proxies=self.proxies
        else:
            proxies = {}

        try:
            if self.debug:
                print(method + ' ' + url)
                print(params)

            response = requests.request(method=method, url=self.host + url, auth=HTTPBasicAuth(self.user, self.password), params=params, data=data, files=files, headers=headers,
                                        timeout=self.timeout, verify=self.verify_ssl, cert=self.cert, proxies=proxies)

            if self.debug:
                print(response.status_code)
                print(response.text)

            try:
                if response.status_code == 201: #Created new object
                    data = response.json()

                    return BitBucketResponse(message="Upload complete", data=data, success=True)
                elif response.status_code == 204: #Object updates
                    return BitBucketResponse(message="Object updated.", success=True)
                elif response.status_code == 404: #Object not created
                    return BitBucketResponse(message="Object id does not exist.", success=False)
                elif 'content-disposition' in response.headers:
                    data = response.content
                    return BitBucketResponse(message="Success", data=data, success=True, response_code=response.status_code)
                else:
                    data = response.json()
                    return BitBucketResponse(message="Success", data=data, success=True, response_code=response.status_code)
            except ValueError:
                return BitBucketResponse(message='JSON response could not be decoded.', success=False)
        except requests.exceptions.SSLError:
            return BitBucketResponse(message='An SSL error occurred.', success=False)
        except requests.exceptions.ConnectionError:
            return BitBucketResponse(message='A connection error occurred.', success=False)
        except requests.exceptions.Timeout:
            return BitBucketResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.',
                                     success=False)
        except requests.exceptions.RequestException:
            return BitBucketResponse(message='There was an error while handling the request.', success=False)


class BitBucketResponse(object):
    """
    Container for all BitBucket Enterprise API responses, even errors.

    """

    def __init__(self, message, success, data=None, response_code=-1):
        self.message = message
        self.data = data
        self.success = success
        self.response_code = response_code

    def __str__(self):
        if self.data:
            return str(self.data)
        else:
            return self.message

    def binary(self):
        return self.data

    def json(self):
        return self.data

    def id(self):
        if self.response_code == 400: #Bad Request
            raise ValueError('Object not created:' + json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': ')))
        return int(self.data)

    def count(self):
        return self.data["TotalCount"]

    def is_success(self):
        data = None

        try:
            data = self.data["IsSuccess"]
        except:
            data = self.data

        return data

    def error(self):
        return self.data["ErrorMessage"]

    def data_json(self, pretty=False):
        """Returns the data as a valid JSON string."""
        if pretty:
            return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.data)
