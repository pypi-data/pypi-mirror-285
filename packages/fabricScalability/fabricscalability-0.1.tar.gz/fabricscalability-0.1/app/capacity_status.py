from azure.identity import DefaultAzureCredential#,AzureDeveloperCliCredential
from azure.mgmt.resource import ResourceManagementClient

def capacity_status(subscription_id,resource_group_name,capacity_name):

    # Authenticate using default credentials
    #credential = AzureDeveloperCliCredential() # With Azure Developer Credential we are able to authenticate with azd auth login  and test with Visual Studio
    credential = DefaultAzureCredential()

    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get the capacity resource
    capacity_resource = resource_client.resources.get_by_id(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Fabric/capacities/{capacity_name}",
        "2022-07-01-preview"
    )

    # Check if the capacity is active
    print(capacity_resource.properties["provisioningState"])
    return capacity_resource.properties["provisioningState"]