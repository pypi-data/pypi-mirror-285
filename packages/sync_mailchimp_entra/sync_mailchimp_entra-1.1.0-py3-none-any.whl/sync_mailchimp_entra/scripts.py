import automationassets  # type: ignore
from sync_mailchimp_entra.core import sync
from sync_mailchimp_entra.core.mailchimp import MailchimpClient
from sync_mailchimp_entra.core.graph import GraphClient


async def main():
    """Run the synchronization between EntraID groups and MailChimp lists."""
    entra_groups_ids = []
    for k in range(1, int(automationassets.get_automation_variable("NB_TENANT")) + 1):
        # Config Graph
        GraphClient.get_instance(
            automationassets.get_automation_variable(f"TENANT{k}_ID"),
            automationassets.get_automation_variable(f"TENANT{k}_APPLICATION_ID"),
            automationassets.get_automation_variable(f"TENANT{k}_APPLICATION_SECRET"),
            ["https://graph.microsoft.com/.default"],
        )

        for i in range(1, int(automationassets.get_automation_variable(f"TENANT{k}_NB_ENTRA_GROUPS")) + 1):
            entra_groups_ids.append(
                (automationassets.get_automation_variable(f"TENANT{k}_ENTRA_GROUP_ID" + str(i)), k)
            )

    # Config Mailchimp
    for i in range(
        1, int(automationassets.get_automation_variable("NB_MAILCHIMP")) + 1
    ):
        print(f"Beginning sync for Mailchimp {i}.")
        MailchimpClient.get_instance(
            automationassets.get_automation_variable("API_TOKEN_MAILCHIMP" + str(i)),
            automationassets.get_automation_variable("SERVER_PREFIX" + str(i)),
        )
        list_mailchimp_id = automationassets.get_automation_variable(
            "LIST_MAILCHIMP_ID" + str(i)
        )

        await sync.mailchimp_entra(list_mailchimp_id, entra_groups_ids)
        print(f"Sync for Mailchimp {i} finished.")
