import json
from boto3 import Session
from requests_aws4auth import AWS4Auth
from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.appsync_websockets import AppSyncWebsocketsTransport
from gql.transport.appsync_auth import AppSyncIAMAuthentication


class AppSyncClient:
    query_get_job = """
    query getJob($id: ID!) {
        getJob(id: $id) {
            status
            updatedAt
        }
    }"""
    subscription_on_update_job = """
    subscription OnUpdateJob {
        onUpdateJob {
            id
            status
            updatedAt
        }
    }"""
    query_get_creds = """
    query listTasks($nextToken: String) {
        listTasks(nextToken: $nextToken) {
            items {
                toolCodename
                taskCodename
                defaultMaxCost
            }
        }
    }
    """
    query_get_storage_usage = """
    query GetStorageUsage {
        getStorageUsage{
            usage
            limit
        }
    }"""

    def __init__(self, refreshable_session, devstr):
        auth_job = AWS4Auth(
            region=refreshable_session.region_name,
            service='appsync',
            refreshable_credentials=refreshable_session.get_credentials()
        )

        auth = AppSyncIAMAuthentication(
            host=f"graphql{devstr}.datoma.cloud",
            credentials=refreshable_session.get_credentials(),
            region_name=refreshable_session.region_name
        )
        self._transport = AppSyncWebsocketsTransport(
            url=f"wss://graphql{devstr}.datoma.cloud/graphql/realtime",
            auth=auth
        )
        self._transport_job = RequestsHTTPTransport(
            url=f"https://graphql{devstr}.datoma.cloud/graphql/",
            auth=auth_job
        )
        self._client = Client(
            transport=self._transport_job,
            fetch_schema_from_transport=False
        )

    def _get_job(self, job_id: str):
        params = {'id': job_id}
        resp = self._client.execute(gql(self.query_get_job),
                                     variable_values=json.dumps(params))
        return resp["getJob"]
    def _get_creds(self):
        resp = self._client.execute(gql(self.query_get_creds))
        return resp
    
    def _get_storage_usage(self):
        resp = self._client.execute(gql(self.query_get_storage_usage))
        return resp
    #a function to subscribe to the updates of a job
    async def _subscribe_to_updates(self):
        async with Client(transport=self._transport) as session:
            subscription = gql(self.subscription_on_update_job)
            async for result in session.subscribe(subscription):
                yield result
