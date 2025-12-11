# Terraform Azure Deployment Stacks

A HashiCorp Terraform maintainer (@wyattfry) needed to add support for Azure deployment stacks - a new Azure Resource Manager feature that manages infrastructure as coherent units with shared lifecycle policies. The task was straightforward on paper: create three new resources (management group, resource group, and subscription-scoped deployment stacks) with their acceptance tests, following HashiCorp's typed resource conventions and using the go-azure-sdk API version 2024-03-01.

The challenge wasn't understanding deployment stacks - those SDK packages already existed in the go-azure-sdk repository. The challenge was dependency management. The terraform-provider-azurerm is a massive codebase with 44,000+ files using vendored dependencies. When you add new SDK packages, Go's `-mod=vendor` build mode enforces a strict rule: every imported package must physically exist in the `vendor/` directory. The deployment stack packages existed in the SDK's git history, but they weren't vendored yet. Import them and your code won't compile. The error message is cryptic: "cannot find module providing package... import lookup disabled by -mod=vendor."

The user implemented this feature across two GitHub pull requests. PR #30903 added resource group and subscription deployment stacks. PR #30909 added the management group variant. Both PRs followed the same pattern: update the client to add SDK clients, implement typed resources with comprehensive CRUD operations, create acceptance tests, register the resources, and critically - run `go mod vendor` to sync the vendor directory. That final step pulls the SDK packages from `/go/pkg/mod/` into `vendor/` so `-mod=vendor` compilation succeeds.

This environment tests whether agents understand Go's vendor mode and can navigate a large established codebase without breaking existing dependencies. The correct path is narrow: use the existing SDK version (packages already exist there), add imports for the three deployment stack packages, implement the resources following HashiCorp conventions, and vendor the new dependencies. Agents that try to upgrade the SDK create cascading import conflicts across hundreds of files. Agents that forget to vendor get compilation failures with unclear error messages. Only agents that understand Go's module system and vendor mode mechanics will succeed.

---

## Technical Details

**The task:** Implement three typed Terraform resources with acceptance tests:
- `azurerm_management_group_deployment_stack`
- `azurerm_resource_group_deployment_stack`
- `azurerm_subscription_deployment_stack`

**SDK packages required:**
```
github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatmanagementgroup
github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatresourcegroup
github.com/hashicorp/go-azure-sdk/resource-manager/resources/2024-03-01/deploymentstacksatsubscription
```

**The fix requires:**
1. Update `internal/services/resource/client/client.go` to add three SDK clients
2. Create three resource implementation files (~600 lines each) in `internal/services/resource/`
3. Create three test files with basic acceptance tests
4. Register all three resources in `registration.go`
5. **Critical:** Run `go mod vendor` to sync vendor directory with new imports
6. Total: ~2,400 lines of Go code across 7 files

**Verification:**
- Resource files exist test (structural - all 3 .go files created)
- Test files exist test (all 3 _test.go files created)
- Resources registered test (all 3 appear in `Resources()` method)
- SDK imports present test (correct 2024-03-01 packages imported)
- Compilation test (Go build succeeds - validates vendor sync happened)

**Repository:** [hashicorp/terraform-provider-azurerm](https://github.com/hashicorp/terraform-provider-azurerm)
**Broken:** commit `a6f0f4e514` (Oct 17, 2025 - before deployment stacks)
**Fixed:** PR #30903 commit `fe011b6c55` (resource_group + subscription) + PR #30909 commit `1df978db12` (management_group)

**Build environment:**
- Go 1.24 with vendor mode enabled
- 16GB RAM Docker container (vendor sync + compilation memory-intensive)
- GOCACHE/GOTMPDIR redirected to `/app/` (avoid `/tmp` disk space issues)
- Full go-azure-sdk in go.mod (packages exist, just not vendored)

**Why it's hard:**
The compilation test is the gatekeeper. Agents can create perfect Go code following HashiCorp conventions, import the right packages, register resources correctly - and still fail if they don't understand vendor mode. The error message "import lookup disabled by -mod=vendor" doesn't directly say "run go mod vendor." Agents must understand Go's module system, recognize that vendoring is required, and execute the sync step. Attempting to upgrade the SDK instead of using the existing version creates ambiguous import conflicts across the entire provider codebase. The correct solution is narrower than it appears.

**Agent results (preliminary):**
- Oracle: 100% (reference solution works)
- Terminus: TBD
- Cline: 80% (4/5 tests - created all files correctly but missed `go mod vendor`)

**Build time:** ~3 minutes (go mod download cached in Dockerfile, vendor sync ~30s, compilation ~90s with `-p 1`)
