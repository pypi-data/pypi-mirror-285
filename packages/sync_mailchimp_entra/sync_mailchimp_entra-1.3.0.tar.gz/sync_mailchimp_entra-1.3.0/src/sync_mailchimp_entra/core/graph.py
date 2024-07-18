from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError
from msgraph.generated.users.item.user_item_request_builder import (
    UserItemRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.group import Group
from msgraph.generated.users.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
import automationassets  # type: ignore
import time


class GraphClient(GraphServiceClient):
    """Client used to communicate with Graph."""

    _instance = None
    start_time = None

    @staticmethod
    def get_instance(tenant_id=None, client_id=None, secret=None, scopes=None):
        """Singleton to only create one instance of this class."""
        if GraphClient._instance is None or (
            tenant_id is not None
            and client_id is not None
            and secret is not None
            and scopes is not None
        ):
            if (
                tenant_id is None
                or client_id is None
                or secret is None
                or scopes is None
            ):
                raise ValueError(
                    "Tenant ID, Client ID, Secret, and Scopes must be provided for the first initialization of GraphClient."
                )
            GraphClient._instance = GraphClient(tenant_id, client_id, secret, scopes)
            if automationassets.get_automation_variable("DEBUG") == "1":
                print()
                print(f"GraphClient tenant {tenant_id} created.")
        return GraphClient._instance

    def __init__(self, tenant_id=None, client_id=None, secret=None, scopes=None):
        if not hasattr(self, "initialized") or not self.initialized:
            credentials = ClientSecretCredential(tenant_id, client_id, secret)
            super(GraphClient, self).__init__(credentials=credentials, scopes=scopes)
            self.initialized = True
            self.start_time = time.time()

    async def get_user(self, id):
        """Get Graph user."""
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=["givenName", "surname", "companyName", "userPrincipalName"],
        )

        request_configuration = RequestConfiguration(
            query_parameters=query_params,
        )

        return (
            await self.get_instance()
            .users.by_user_id(id)
            .get(request_configuration=request_configuration)
        )

    async def get_group_members(self, group_id):
        """Get members of a group."""
        try:
            return (
                await self.get_instance()
                .groups.by_group_id(group_id)
                .members.get(
                    RequestConfiguration(
                        query_parameters=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                            select=["id", "mail", "userPrincipalName"], top=999
                        )
                    )
                )
            )
        except APIError as e:
            raise Exception(e.error.message)

    async def list_entra_emails(self, group_id):
        """Get list of emails."""

        request = await self.get_group_members(group_id)
        users = request.value
        next_link = request.odata_next_link
        while next_link:
            request = await self.users.with_url(next_link).get(
                RequestConfiguration(
                    query_parameters=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                        select=["id", "mail", "userPrincipalName"], top=999
                    )
                )
            )
            users.extend(request.value)
            next_link = request.odata_next_link

        i = 0
        while i < len(users):
            if isinstance(users[i], Group):
                users.extend(
                    (
                        await GraphClient.get_instance().get_group_members(users[i].id)
                    ).value
                )
                users.pop(i)
            else:
                i += 1

        members_entra_emails = []
        for user in users:
            if user.user_principal_name:
                members_entra_emails.append(user.user_principal_name)
            elif user.mail:
                members_entra_emails.append(user.mail)
        print()
        return members_entra_emails
