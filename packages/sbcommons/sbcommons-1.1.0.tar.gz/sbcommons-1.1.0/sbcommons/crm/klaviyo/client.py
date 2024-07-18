import json
import logging
import time
from typing import Dict, Callable
from typing import List
import requests
from requests.structures import CaseInsensitiveDict

from sbcommons.crm.klaviyo.url import (get_next_page_cursor_arg,
                                       get_filter_url,
                                       get_url_since_timestamp_filter_args,
                                       get_url_until_timestamp_filter_args,
                                       get_field_arg)
from sbcommons.utils import get_field_from_included
from sbcommons.crm.client import CrmClient
from sbcommons.crm.klaviyo.metric import KlaviyoMetric
from sbcommons.crm.klaviyo.metric import KlaviyoMetricError
from string import Template


class KlaviyoClientError(Exception):
    """ Klaviyo client exception class"""

    def __init__(self, msg):
        super(KlaviyoClientError, self).__init__(msg)


class KlaviyoClient(CrmClient):
    """ A client class to interact with Klaviyo's API.

    Attributes:
        token (Dict[str, str]): A Dict with two keys, the PUBLIC_API_KEY and PRIVATE_API_KEY
            required to make requests to Klaviyo. Inherited from CrmClient.
        list_id (int): Identifier of the list to use for pushing/retrieving customers.
        session (requests.Session): The session object for the Klaviyo connection. Inherited from
            CrmClient.
        rate_limit (int): Amounts of second to wait after getting a rate limited error (HTTP 429),
            in order to make a successful request again. Inherited from CrmClient.
        max_rate_limit_retries (int): Number of times to retry making a request if a rate limited
            error occurs (status code 429/Too Many Requests). Inherited from CrmClient.
    """

    _KLAVIYO_IDENTIFY_URL = 'https://a.klaviyo.com/client/profiles/?company_id='
    _KLAVIYO_UNSUBSCRIBE_URL = 'https://a.klaviyo.com/api/v1/people/exclusions'
    _KLAVIYO_TRACK_URL = 'https://a.klaviyo.com/client/events/?company_id='

    _KLAVIYO_GET_GROUP_MEMBERS_URL_TEMPLATE = ('https://a.klaviyo.com/api/lists/'
                                               '{list_id}/profiles/?fields[profile]=email&'
                                               'page[size]=100')
    _KLAVIYO_GET_SEGMENT_MEMBERS_URL_TEMPLATE = ('https://a.klaviyo.com/api/segments/{segment_id}'
                                                 '/profiles/?page[size]=100')
    _KLAVIYO_LIST_MEMBERS_URL = Template('https://a.klaviyo.com/api/lists/$id/relationships/'
                                         'profiles/?fields[profile]=email&page[size]=100')
    _KLAVIYO_SUBSCRIBE_PROFILES = 'https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs/'
    _KLAVIYO_UPDATE_PROFILE_URL = 'https://a.klaviyo.com/api/profile-import/'

    EXCLUSION_REASONS = [
        'unsubscribed', 'bounced', 'invalid_email', 'reported_spam', 'manually_excluded'
    ]

    def __init__(self, token: Dict[str, str], list_id: int = None, segment_id=None, rate_limit=60,
                 max_rate_limit_retries=2, logger: logging.Logger = None):
        CrmClient.__init__(self, token=token, rate_limit=rate_limit,
                           max_rate_limit_retries=max_rate_limit_retries)
        self.list_id = list_id
        self.segment_id = segment_id
        # If logger argument is None, use default logger
        self._logger = logger or logging.getLogger(__name__)

    @property
    def klaviyo_identify_url(self):
        return self._KLAVIYO_IDENTIFY_URL

    @property
    def klaviyo_unsubscribe_url(self):
        return self._KLAVIYO_UNSUBSCRIBE_URL

    @property
    def klaviyo_track_url(self):
        return self._KLAVIYO_TRACK_URL

    @property
    def logger(self) -> logging.Logger:
        """ Returns the logger object to be used by the instance. """
        return self._logger

    def connect(self):
        """ Performs the necessary actions required to be able to make requests to Klaviyo.

        This method is automatically called when this class is used in a context manager i.e. when
        __enter__ is called.
        """
        self.session.mount('https://', self._retry_adapter(retries=3, backoff_factor=4))
        self.session.headers = self._build_base_header()

    def close(self):
        """  Performs necessary actions to terminate the connection with Klaviyo. """
        self.session.close()

    def _build_base_header(self) -> CaseInsensitiveDict:
        return CaseInsensitiveDict({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Klaviyo-API-Key {self.get_private_api_key()}',
            'revision': '2024-05-15'
        })

    def get_public_api_key(self):
        return self.token['PUBLIC_API_KEY']

    def get_private_api_key(self):
        return self.token['PRIVATE_API_KEY']

    def get_public_private_api_key(self):
        return self.get_public_api_key(), self.get_private_api_key()

    def get_all_metrics(self) -> List[Dict]:
        """ Returns a list of all Klaviyo metrics as dictionaries.

            Returns:
                A list of dictionaries, where each dictionary represents a metric.
        """
        data = []
        page_cursor = None
        while not data or page_cursor:
            next_page_arg = get_next_page_cursor_arg(next_page=page_cursor)
            url = f'{KlaviyoMetric.metrics_info_url}?{next_page_arg}'
            res = self._request(method='GET', url=url).json()
            page_cursor = res['links']['next']
            data.extend(res['data'])
        return data

    def get_events(self, since_ts: str,
                   end_ts: str,
                   metric_name: str,
                   include: str = 'profile',
                   obj_to_get_from_inc : List = None):
        """ Gets all Klaviyo events for <metric_name>, during the period (<since_ts>, <end_ts>).

            Args:
                since_ts: A unix timestamp with the seconds since epoch in UTC. Marks the beginning
                    of the window for which we will extract event data.
                end_ts: A unix timestamp with the seconds since epoch in UTC. Marks the end of the
                    window for which we will extract event data. If set to None, then we extract
                    all data available since <since_ts>.
                metric_name: Name of the Klaviyo metric.
                include: if any additional fields are needed (e.g profile)
                obj_to_get_from_inc: A list of objects to get from the included field

            Returns:
                A list of event dictionaries.

            Raises:
                KlaviyoError if the metric with the specified name is not found.
        """
        # Get id of metric given the name
        metric_id = self.get_metric_id(metric_name=metric_name)

        # Configure URL and URL arguments to get events for <metric_id> since <since_ts>
        url_base = KlaviyoMetric.get_metric_events_url(metric_id)
        url_args = ''
        if since_ts:
            url_args += f"%2C{get_url_since_timestamp_filter_args(since_ts)}"
        if end_ts:
            url_args += f"%2C{get_url_until_timestamp_filter_args(end_ts)}"

        url = url_base + url_args
        url += f'&{KlaviyoMetric.include_template.substitute(value = include)}'
        # Get all events in batches
        event_list = []
        next_page = None
        while not event_list or next_page:
            # Get data with Klaviyo client
            res = self._request(method='GET', url=url).json()
            # Add data to list
            for ob in obj_to_get_from_inc:
                event_list.extend(get_field_from_included(res['data'],
                                                          res['included'],
                                                          f'attributes.properties.{ob}'))

            # If there are no more pages then break the loop
            if res['links']['next'] is None:
                break
            next_page = res['links']['next']
            url = next_page
            # Sleep for a bit - Klaviyo allows 350 calls per second before a rate limited error
            time.sleep(0.01)

        return event_list

    def get_metric_id(self, metric_name: str) -> str:
        """ Calls the Klaviyo API to get the metric id given a metric name.

        k_client: KlaviyoClient object for making the call.

        Returns:
            The metric id character string.

        Raises:
            KlaviyoError if the metric with the specified name is not found.
        """
        # Iterate over data and return correct metric_id
        metric_list = self.get_all_metrics()
        for metric in metric_list:
            if metric['attributes']['name'] == metric_name:
                return metric['id']
        raise KlaviyoMetricError(f'Metric with name {metric_name} not found.')

    def get_global_exclusions(self, count: int = 5000, max_pages: int = 50,
                              reason: str = '') -> List[Dict]:
        """ Returns global exclusions/unsubscribes.

         Global exclusions are distinct from list exclusions in that these email addresses will not
         receive any emails from any list.

         https://developers.klaviyo.com/en/reference/get-global-exclusions

        Args:
            count: The number of results to return.
            max_pages: The maximum amount of pages that is expected to contain all the unsubscribes,
                with <count> unsubscribes in each page.
            reason: The exclusion reason based on which we can filter which types of exclusions we
                want to retrieve by calling get_global_exclusions. The value of this should be
                a member of the EXCLUSION_REASONS list attribute of the KlaviyoClient class.

        Returns:
            A list of dictionaries where each dictionary represents a global unsubscribe.

        Raises:
            KlaviyoClientError if the exclusion reason is a non empty string that is not in the
                EXCLUSION_REASONS list attribute.
        """
        if reason and reason not in self.EXCLUSION_REASONS:
            raise KlaviyoClientError('The value provided to the get_global_exclusions call for'
                                     'the argument <reason> is not a member of the '
                                     'EXCLUSION_REASONS list attribute in KlaviyoClient.')
        unsubscribes_list = []
        for page_i in range(max_pages):
            url_args = (f'reason={reason}&count={count}&page={page_i}'
                        f'&api_key={self.get_private_api_key()}')
            url = f'{self.klaviyo_unsubscribe_url}?{url_args}'
            response = self._request(method="GET", url=url)
            unsubscribes_list.extend(response.json()['data'])
        return unsubscribes_list

    def update_profiles(self, update_data: List[Dict], company_id: str, store: str = 'N/A'):
        """ Updates the profile attributes specified in <update_data>

        Args:
            update_data: A list of dictionaries where each dictionary represents a profile and
                includes the attributes that are going to be updated and their corresponding values.
                In the dictionary we additionally expect an extra field called 'email' we use that
                for logging purposes in case the update fails. We then delete that from the dictio
                nary
            company_id: The public API key/ site ID to be used.
            store: Store name for which we run the update. This is used for logging failed updates.
        """

        def format_payload_json(record, **kwargs):
            email = record.pop('$email')
            record['email'] = email
            f = {
                'data':
                    {
                        'type': 'profile',
                        'attributes': {
                            "email": email,
                            'properties': record}
                    }
               }

            data = json.dumps(f, indent=4)
            return email, data

        self._klaviyo_request(update_data, store, url=f'{self._KLAVIYO_IDENTIFY_URL}{company_id}',
                              method=format_payload_json)

    def update_location(self,update_data: List[Dict],store: str = 'N/A'):
        """ Updates location information for a given user

        Args:
            update_data: A list of dictionaries where each dictionary contains information regarding
            the customer location (zip code, city e.t.c).

            store: Store name for which we run the update. This is used for logging failed updates.
        """
        def format_payload_json(record, **kwargs):
            email = record.pop('$email')
            f = {"data": {
                    "type": "profile",
                    "attributes": {
                        "email": email,
                        "location": {
                           **record
                        }
                    }
                }
            }
            data = json.dumps(f, indent=4)
            return email, data

        self._klaviyo_request(update_data, store, url=f'{self._KLAVIYO_UPDATE_PROFILE_URL}',
                              method=format_payload_json)

    def create_event_in_metric(self, update_data: List[Dict], store: str = 'N/A'):
        """ Updates a Klaviyo metric with event attributes specified in <update_data>

        Args:
            update_data: A list of dictionaries where each dictionary represents a customer's email,
            event name, metric name, token and also includes the attributes that are going to be
            updated and their corresponding values.
            store: Store name for which we run the update. This is used for logging failed updates.
        """
        def format_payload_json(record, **kwargs):
            email = record.pop('email')
            event_name = record.pop('event_name')
            f = {
                'data': {
                    'type': 'event',
                    'attributes': {
                        'properties': record,
                        'metric': {
                            'data': {
                                "type": "metric",
                                'attributes':
                                    {'name': event_name,
                                     }
                            }
                        },
                        'profile': {'data':
                                    {'type': 'profile',
                                        'attributes': {
                                            'email': email,
                                         }
                                     }
                                    }
                    }
                }
            }

            data = json.dumps(f, indent=4)
            return email, data

        self._klaviyo_request(update_data, store,
                              url=self._KLAVIYO_TRACK_URL + self.token['PUBLIC_API_KEY'],
                              method=format_payload_json)

    def _klaviyo_request(self, update_data: List[Dict], store: str,
                         url: str, method: Callable, **kwargs):
        """ Calls a request post method

               Args:
                   update_data: A list of dictionaries where each dictionary represents a
                       customer's profile and includes the attributes that are going to
                       be updated and their corresponding values.
                   store: Store name for which we run the update. This is used for logging
                       failed updates.
                   url: endpoint /api url
                   method: a callable function that returns a json formatted str.
               """
        for record in update_data:
            email, data = method(record, **kwargs)
            try:
                self._request(method='POST', url=url, data=data)
            except Exception as e:
                self.logger.exception(f"Failed to update {email} for {store} got exception {e}")

    def get_segment_members(self) -> List[Dict]:
        """Get all members from the segment

        Returns:
            A list of dictionaries where each dictionary corresponds to a member of the segment. E.g.
            [{'id': '01GCY4YJKP67R3ZEHAVEYC1KXK', 'email': 'test1@hayppgroup.com'},
             {'id': '01GD38S642GQW6TR46S30KBYNQ', 'email': 'test2@hayppgroup.com'}]
        """
        get_members_url = self._KLAVIYO_GET_SEGMENT_MEMBERS_URL_TEMPLATE.format(
            segment_id=self.segment_id
        )
        url = get_members_url
        # Use pagination to iterate over all members
        segment_members = []

        next_page = None
        while not segment_members or next_page:
            json_response = self._request(method='GET', url=url).json()
            for data in json_response['data']:
                segment_members.append({'id': data['id'],
                                        'email': data['attributes']['email']})

            next_page = json_response['links']['next']
            url = next_page
        return segment_members

    def get_list_members(self) -> List[Dict]:
        """ Gets all members from the list.

        Returns:
            A list of dictionaries where each dictionary corresponds to a member of the list. E.g.
            [{'id': '01GCY4YJKP67R3ZEHAVEYC1KXK', 'email': 'test1@hayppgroup.com'},
             {'id': '01GD38S642GQW6TR46S30KBYNQ', 'email': 'test2@hayppgroup.com'}]
        """
        get_members_url = self._KLAVIYO_GET_GROUP_MEMBERS_URL_TEMPLATE.format(
            list_id=self.list_id
        )
        url = get_members_url
        # Use pagination to iterate over all members
        list_members = []

        next_page = None
        while not list_members or next_page:
            json_response = self._request(method='GET', url=url).json()
            list_members.extend([{'id': data['id'], 'email': data['attributes']['email']}
                                 for data in json_response['data']])
            next_page = json_response['links']['next']
            url = next_page
        return list_members

    def remove_list_members(self, list_id, members_payload):
        """ Removes specified members from a list.

        Args:
             list_id: the id of the list from which to remove members.
             members_payload: A dictionary where the key is a type of customer identifier (e.g.
             "emails"), and the value is a list with the identifier values (e.g. e-mail addresses)
             of the customers we want to delete. E.g.

             {"emails": ['test@hayppgroup.com', 'test2@hayppgroup.com']}
        """
        def _preprocess_payload(payload):
            return {'data': [{'type': 'profile',
                              **member} for member in payload]}

        url = self._KLAVIYO_LIST_MEMBERS_URL.substitute(id=list_id)
        return self._request(method='DELETE', url=url, json=_preprocess_payload(members_payload))

    def clean_list(self, list_id) -> bool:
        """ Clears the list.

            Returns:
                True if no exception is raised while clearing the list.
        """
        records = self.get_list_members()
        if not records:
            # Return because if we make a request with no records it will cause a 400 Bad Request
            return True
        self.remove_list_members(list_id=list_id,
                                 members_payload=records)
        return True

    def post_list_sync(self, list_data: List, import_type: str = 'ADD'):
        """ Posts a list of customers to the Klaviyo list.

        Args:
            import_type: This can be either 'ADD' or 'REPLACE'. Using 'ADD' will add new customers
                to the list, while 'REPLACE' will first clear the list and then add those new
                customers.
            list_data: A dictionary with two keys list_id and a  key ("profiles") which is
            mapped to a list of dictionaries where each dictionary corresponds to the customer
            profile we want to add to the list. The profile must have an identifier such as a mobile
             phone number or e-mail address to be added to the list. Uses the Klaviyo API function
             described in https://developers.klaviyo.com/en/reference/add-members.

        Returns:
            We return True if the call is successful. False, otherwise.

        Raises:
            AssertionError if import_type is not 'REPLACE' or 'ADD'.
        """
        def format_payload_json(records, **kwargs):
            f = {
                  "data": {
                    "type": "profile-subscription-bulk-create-job",
                    "attributes": {
                      "profiles": {
                        "data": [
                          {
                            "attributes": {
                              **record
                             }
                          }
                        ] for record in records
                      }
                    },
                    "relationships": {
                          "list": {
                            "data": {
                              "type": "list",
                              "id": list_id
                            }
                          }
                      }
                 }
            }

            data = json.dumps(f, indent=4)
            return data

        list_id = self.list_id
        assert import_type in ('REPLACE', 'ADD')
        if import_type == 'REPLACE':
            self.clean_list(list_id=list_id)
        if not len(list_data):
            return True
        url = self._KLAVIYO_SUBSCRIBE_PROFILES
        self._request(method='POST', url=url, json=format_payload_json(list_data))
        return True

    def post_survey_candidates(self, **kwargs):
        """ Wrapper around create_event_in_metric. Used to achieve polymorphism with other CrmClient
        subclasses such as SymplifyClient. We do this because we might use different methods to post
        survey candidates in different CRM systems. """
        self.create_event_in_metric(**kwargs)
        return True
