# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.o_365_region_proto
import cohesity_management_sdk.models.registered_entity_sfdc_params


class AdditionalConnectorParams(object):

    """Implementation of the 'AdditionalConnectorParams' model.

    Message that encapsulates the additional connector params to establish a
    connection with a particular environment.


    Attributes:
        graph_token_endpoint (string): Endpoint URL for querying the MS graph
            token fetched from openid-configuration.
        max_vmware_http_sessions (int): Max http sessions per context for
            VMWare vAPI calls.
        msgraph_host (string):  Endpoint or host url where all the graph calls
            are made. It is fetched from openid-configuration.
        o_365_emulator_entity_info (string): A token used only in O365 Emulator
            identifying the information of number of Users, Sites, Groups,
            Teams & Public Folders and their ids.
        o_365_region (O365RegionProto): Optional o365_region proto to store the
            region info to be used while making ews/graph api calls in o365
            adapter.
        outlook_skip_creating_autodiscover_proxy (bool): Whether we should skip
            creating autodiscove proxy. This is needed only during fetching eh
            and in public folder backups setup.
        registered_entity_sfdc_params (RegisteredEntitySfdcParams):
            RegisteredEntitySfdcParams contains soap_endpoint_url and
            metadata_endpoint_url which are needed for connecting to Sfdc in
            connector params.
        use_get_searchable_mailboxes_api (bool): Wheather to use
            GetSearchableMailboxes EWS API while descovering User Mailboxes or
            not.
        use_outlook_ews_oauth (bool): Whether OAuth should be used for
            authentication with EWS API (outlook backup), applicable only for
            Exchange Online.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "graph_token_endpoint": 'graphTokenEndpoint',
        "max_vmware_http_sessions":'maxVmwareHttpSessions',
        "msgraph_host": 'msgraphHost',
        "o_365_emulator_entity_info":'o365EmulatorEntityInfo',
        "o_365_region":'o365Region',
        "outlook_skip_creating_autodiscover_proxy":'outlookSkipCreatingAutodiscoverProxy',
        "registered_entity_sfdc_params":'registeredEntitySfdcParams',
        "use_get_searchable_mailboxes_api":'useGetSearchableMailboxesApi',
        "use_outlook_ews_oauth":'useOutlookEwsOauth',
    }
    def __init__(self,
                 graph_token_endpoint = None,
                 max_vmware_http_sessions=None,
                 msgraph_host=None,
                 o_365_emulator_entity_info=None,
                 o_365_region=None,
                 outlook_skip_creating_autodiscover_proxy=None,
                 registered_entity_sfdc_params=None,
                 use_get_searchable_mailboxes_api=None,
                 use_outlook_ews_oauth=None,
            ):

        """Constructor for the AdditionalConnectorParams class"""

        # Initialize members of the class
        self.graph_token_endpoint = graph_token_endpoint
        self.max_vmware_http_sessions = max_vmware_http_sessions
        self.msgraph_host = msgraph_host
        self.o_365_emulator_entity_info = o_365_emulator_entity_info
        self.o_365_region = o_365_region
        self.outlook_skip_creating_autodiscover_proxy = outlook_skip_creating_autodiscover_proxy
        self.registered_entity_sfdc_params = registered_entity_sfdc_params
        self.use_get_searchable_mailboxes_api = use_get_searchable_mailboxes_api
        self.use_outlook_ews_oauth = use_outlook_ews_oauth

    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        graph_token_endpoint = dictionary.get('graphTokenEndpoint')
        max_vmware_http_sessions = dictionary.get('maxVmwareHttpSessions')
        msgraph_host = dictionary.get('msgraphHost')
        o_365_emulator_entity_info = dictionary.get('o365EmulatorEntityInfo')
        o_365_region = cohesity_management_sdk.models.o_365_region_proto.O365RegionProto.from_dictionary(dictionary.get('o365Region')) if dictionary.get('o365Region') else None
        outlook_skip_creating_autodiscover_proxy = dictionary.get('outlookSkipCreatingAutodiscoverProxy')
        registered_entity_sfdc_params = cohesity_management_sdk.models.registered_entity_sfdc_params.RegisteredEntitySfdcParams.from_dictionary(dictionary.get('registeredEntitySfdcParams')) if dictionary.get('registeredEntitySfdcParams') else None
        use_get_searchable_mailboxes_api = dictionary.get('useGetSearchableMailboxesApi')
        use_outlook_ews_oauth = dictionary.get('useOutlookEwsOauth')

        # Return an object of this model
        return cls(
            graph_token_endpoint,
            max_vmware_http_sessions,
            msgraph_host,
            o_365_emulator_entity_info,
            o_365_region,
            outlook_skip_creating_autodiscover_proxy,
            registered_entity_sfdc_params,
            use_get_searchable_mailboxes_api,
            use_outlook_ews_oauth
)