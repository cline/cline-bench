#!/bin/bash
set -e

cd /app

# Re-initialize git (removed in Dockerfile to prevent agents from browsing history)
git init
git remote add origin https://github.com/hashicorp/terraform-provider-azurerm.git

# Fetch PR #30903 (resource_group + subscription deployment stacks)
echo "Fetching PR #30903 (resource_group + subscription variants)..."
git fetch origin fe011b6c555f9b422d10a58787e9f63e6b4ff054 --depth=1
git checkout -f fe011b6c555f9b422d10a58787e9f63e6b4ff054

# Now fetch and cherry-pick the management_group implementation from PR #30909
echo "Fetching PR #30909 (management_group variant)..."
git fetch origin 1df978db124f0c222c862cb0a5e11b743eb38826 --depth=1

# Extract the management_group files from PR #30909 (including client changes)
git checkout 1df978db124f0c222c862cb0a5e11b743eb38826 -- \
    internal/services/resource/management_group_deployment_stack_resource.go \
    internal/services/resource/management_group_deployment_stack_resource_test.go \
    internal/services/resource/client/client.go

# Update registration.go to include all 3 resources
# The PR #30903 version has resource_group and subscription registered
# We need to add management_group to the Resources() slice
cat > /tmp/registration_patch.go << 'REGEOF'
	return []sdk.Resource{
		ResourceManagementPrivateLinkAssociationResource{},
		ResourceProviderRegistrationResource{},
		ResourceManagementPrivateLinkResource{},
		ResourceDeploymentScriptAzurePowerShellResource{},
		ResourceDeploymentScriptAzureCliResource{},
		ResourceGroupDeploymentStackResource{},
		SubscriptionDeploymentStackResource{},
		ManagementGroupDeploymentStackResource{},
	}
REGEOF

# Replace the Resources() return block
sed -i '/^func (r Registration) Resources()/,/^}$/c\
func (r Registration) Resources() []sdk.Resource {\
	return []sdk.Resource{\
		ResourceManagementPrivateLinkAssociationResource{},\
		ResourceProviderRegistrationResource{},\
		ResourceManagementPrivateLinkResource{},\
		ResourceDeploymentScriptAzurePowerShellResource{},\
		ResourceDeploymentScriptAzureCliResource{},\
		ResourceGroupDeploymentStackResource{},\
		SubscriptionDeploymentStackResource{},\
		ManagementGroupDeploymentStackResource{},\
	}\
}' internal/services/resource/registration.go

# Update vendor directory to include management_group SDK package
echo "Updating vendor directory with management_group SDK package..."
/usr/local/go/bin/go mod vendor

echo "✓ Solution complete! All 3 deployment stack resources implemented."