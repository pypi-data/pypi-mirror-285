# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from . import _utilities
import typing
# Export this package's modules as members:
from .access_package import *
from .access_package_assignment_policy import *
from .access_package_catalog import *
from .access_package_catalog_role_assignment import *
from .access_package_resource_catalog_association import *
from .access_package_resource_package_association import *
from .administrative_unit import *
from .administrative_unit_member import *
from .administrative_unit_role_member import *
from .app_role_assignment import *
from .application import *
from .application_api_access import *
from .application_app_role import *
from .application_certificate import *
from .application_fallback_public_client import *
from .application_federated_identity_credential import *
from .application_from_template import *
from .application_identifier_uri import *
from .application_known_clients import *
from .application_optional_claims import *
from .application_owner import *
from .application_password import *
from .application_permission_scope import *
from .application_pre_authorized import *
from .application_redirect_uris import *
from .application_registration import *
from .authentication_strength_policy import *
from .claims_mapping_policy import *
from .conditional_access_policy import *
from .custom_directory_role import *
from .directory_role import *
from .directory_role_assignment import *
from .directory_role_eligibility_schedule_request import *
from .directory_role_member import *
from .get_access_package import *
from .get_access_package_catalog import *
from .get_access_package_catalog_role import *
from .get_administrative_unit import *
from .get_application import *
from .get_application_published_app_ids import *
from .get_application_template import *
from .get_client_config import *
from .get_directory_object import *
from .get_directory_role_templates import *
from .get_directory_roles import *
from .get_domains import *
from .get_group import *
from .get_group_role_management_policy import *
from .get_groups import *
from .get_named_location import *
from .get_service_principal import *
from .get_service_principals import *
from .get_user import *
from .get_users import *
from .group import *
from .group_member import *
from .group_role_management_policy import *
from .invitation import *
from .named_location import *
from .privileged_access_group_assignment_schedule import *
from .privileged_access_group_eligibility_schedule import *
from .provider import *
from .service_principal import *
from .service_principal_certificate import *
from .service_principal_claims_mapping_policy_assignment import *
from .service_principal_delegated_permission_grant import *
from .service_principal_password import *
from .service_principal_token_signing_certificate import *
from .synchronization_job import *
from .synchronization_job_provision_on_demand import *
from .synchronization_secret import *
from .user import *
from .user_flow_attribute import *
from ._inputs import *
from . import outputs

# Make subpackages available:
if typing.TYPE_CHECKING:
    import pulumi_azuread.config as __config
    config = __config
else:
    config = _utilities.lazy_import('pulumi_azuread.config')

_utilities.register(
    resource_modules="""
[
 {
  "pkg": "azuread",
  "mod": "index/accessPackage",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackage:AccessPackage": "AccessPackage"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/accessPackageAssignmentPolicy",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackageAssignmentPolicy:AccessPackageAssignmentPolicy": "AccessPackageAssignmentPolicy"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/accessPackageCatalog",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackageCatalog:AccessPackageCatalog": "AccessPackageCatalog"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/accessPackageCatalogRoleAssignment",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackageCatalogRoleAssignment:AccessPackageCatalogRoleAssignment": "AccessPackageCatalogRoleAssignment"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/accessPackageResourceCatalogAssociation",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackageResourceCatalogAssociation:AccessPackageResourceCatalogAssociation": "AccessPackageResourceCatalogAssociation"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/accessPackageResourcePackageAssociation",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/accessPackageResourcePackageAssociation:AccessPackageResourcePackageAssociation": "AccessPackageResourcePackageAssociation"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/administrativeUnit",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/administrativeUnit:AdministrativeUnit": "AdministrativeUnit"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/administrativeUnitMember",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/administrativeUnitMember:AdministrativeUnitMember": "AdministrativeUnitMember"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/administrativeUnitRoleMember",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/administrativeUnitRoleMember:AdministrativeUnitRoleMember": "AdministrativeUnitRoleMember"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/appRoleAssignment",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/appRoleAssignment:AppRoleAssignment": "AppRoleAssignment"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/application",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/application:Application": "Application"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationApiAccess",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationApiAccess:ApplicationApiAccess": "ApplicationApiAccess"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationAppRole",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationAppRole:ApplicationAppRole": "ApplicationAppRole"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationCertificate",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationCertificate:ApplicationCertificate": "ApplicationCertificate"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationFallbackPublicClient",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationFallbackPublicClient:ApplicationFallbackPublicClient": "ApplicationFallbackPublicClient"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationFederatedIdentityCredential",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationFederatedIdentityCredential:ApplicationFederatedIdentityCredential": "ApplicationFederatedIdentityCredential"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationFromTemplate",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationFromTemplate:ApplicationFromTemplate": "ApplicationFromTemplate"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationIdentifierUri",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationIdentifierUri:ApplicationIdentifierUri": "ApplicationIdentifierUri"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationKnownClients",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationKnownClients:ApplicationKnownClients": "ApplicationKnownClients"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationOptionalClaims",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationOptionalClaims:ApplicationOptionalClaims": "ApplicationOptionalClaims"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationOwner",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationOwner:ApplicationOwner": "ApplicationOwner"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationPassword",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationPassword:ApplicationPassword": "ApplicationPassword"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationPermissionScope",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationPermissionScope:ApplicationPermissionScope": "ApplicationPermissionScope"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationPreAuthorized",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationPreAuthorized:ApplicationPreAuthorized": "ApplicationPreAuthorized"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationRedirectUris",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationRedirectUris:ApplicationRedirectUris": "ApplicationRedirectUris"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/applicationRegistration",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/applicationRegistration:ApplicationRegistration": "ApplicationRegistration"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/authenticationStrengthPolicy",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/authenticationStrengthPolicy:AuthenticationStrengthPolicy": "AuthenticationStrengthPolicy"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/claimsMappingPolicy",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/claimsMappingPolicy:ClaimsMappingPolicy": "ClaimsMappingPolicy"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/conditionalAccessPolicy",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/conditionalAccessPolicy:ConditionalAccessPolicy": "ConditionalAccessPolicy"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/customDirectoryRole",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/customDirectoryRole:CustomDirectoryRole": "CustomDirectoryRole"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/directoryRole",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/directoryRole:DirectoryRole": "DirectoryRole"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/directoryRoleAssignment",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/directoryRoleAssignment:DirectoryRoleAssignment": "DirectoryRoleAssignment"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/directoryRoleEligibilityScheduleRequest",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/directoryRoleEligibilityScheduleRequest:DirectoryRoleEligibilityScheduleRequest": "DirectoryRoleEligibilityScheduleRequest"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/directoryRoleMember",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/directoryRoleMember:DirectoryRoleMember": "DirectoryRoleMember"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/group",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/group:Group": "Group"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/groupMember",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/groupMember:GroupMember": "GroupMember"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/groupRoleManagementPolicy",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/groupRoleManagementPolicy:GroupRoleManagementPolicy": "GroupRoleManagementPolicy"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/invitation",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/invitation:Invitation": "Invitation"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/namedLocation",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/namedLocation:NamedLocation": "NamedLocation"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/privilegedAccessGroupAssignmentSchedule",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/privilegedAccessGroupAssignmentSchedule:PrivilegedAccessGroupAssignmentSchedule": "PrivilegedAccessGroupAssignmentSchedule"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/privilegedAccessGroupEligibilitySchedule",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/privilegedAccessGroupEligibilitySchedule:PrivilegedAccessGroupEligibilitySchedule": "PrivilegedAccessGroupEligibilitySchedule"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipal",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipal:ServicePrincipal": "ServicePrincipal"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipalCertificate",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipalCertificate:ServicePrincipalCertificate": "ServicePrincipalCertificate"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipalClaimsMappingPolicyAssignment",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipalClaimsMappingPolicyAssignment:ServicePrincipalClaimsMappingPolicyAssignment": "ServicePrincipalClaimsMappingPolicyAssignment"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipalDelegatedPermissionGrant",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipalDelegatedPermissionGrant:ServicePrincipalDelegatedPermissionGrant": "ServicePrincipalDelegatedPermissionGrant"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipalPassword",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipalPassword:ServicePrincipalPassword": "ServicePrincipalPassword"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/servicePrincipalTokenSigningCertificate",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/servicePrincipalTokenSigningCertificate:ServicePrincipalTokenSigningCertificate": "ServicePrincipalTokenSigningCertificate"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/synchronizationJob",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/synchronizationJob:SynchronizationJob": "SynchronizationJob"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/synchronizationJobProvisionOnDemand",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/synchronizationJobProvisionOnDemand:SynchronizationJobProvisionOnDemand": "SynchronizationJobProvisionOnDemand"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/synchronizationSecret",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/synchronizationSecret:SynchronizationSecret": "SynchronizationSecret"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/user",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/user:User": "User"
  }
 },
 {
  "pkg": "azuread",
  "mod": "index/userFlowAttribute",
  "fqn": "pulumi_azuread",
  "classes": {
   "azuread:index/userFlowAttribute:UserFlowAttribute": "UserFlowAttribute"
  }
 }
]
""",
    resource_packages="""
[
 {
  "pkg": "azuread",
  "token": "pulumi:providers:azuread",
  "fqn": "pulumi_azuread",
  "class": "Provider"
 }
]
"""
)
