big job for you: create three new (typed!) resources and their acceptance tests:
azurerm_management_group_deployment_stack
azurerm_resource_group_deployment_stack
azurerm_subscription_deployment_stack
in ./internal/services/resources
Using the go-azure-sdk API version 2024-03-01:

github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatsubscription
github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatresourcegroup
github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatmanagementgroup

run whatever commands or tests you need to verify as you go. always follow the contributor guide (./contributing/) and the precedent set by the rest of the code base.

i'm going to bed, good luck.

<environment_details>
# Visual Studio Code Visible Files
internal/services/policy/management_group_policy_assignment_resource_test.go

# Visual Studio Code Open Tabs
vendor/github.com/hashicorp/go-azure-sdk/resource-manager/search/2025-05-01/services/constants.go
internal/services/resource/management_group_template_deployment_resource.go
internal/services/resource/client/client.go
internal/services/policy/management_group_policy_assignment_resource_test.go
internal/services/resource/template_deployment_common.go
</environment_details>