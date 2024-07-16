# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import sys
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, TypeAlias
else:
    from typing_extensions import NotRequired, TypedDict, TypeAlias
from . import _utilities
from . import outputs

__all__ = [
    'GetGroupResult',
    'AwaitableGetGroupResult',
    'get_group',
    'get_group_output',
]

@pulumi.output_type
class GetGroupResult:
    """
    A collection of values returned by getGroup.
    """
    def __init__(__self__, assignable_to_role=None, auto_subscribe_new_members=None, behaviors=None, description=None, display_name=None, dynamic_memberships=None, external_senders_allowed=None, hide_from_address_lists=None, hide_from_outlook_clients=None, id=None, include_transitive_members=None, mail=None, mail_enabled=None, mail_nickname=None, members=None, object_id=None, onpremises_domain_name=None, onpremises_group_type=None, onpremises_netbios_name=None, onpremises_sam_account_name=None, onpremises_security_identifier=None, onpremises_sync_enabled=None, owners=None, preferred_language=None, provisioning_options=None, proxy_addresses=None, security_enabled=None, theme=None, types=None, visibility=None, writeback_enabled=None):
        if assignable_to_role and not isinstance(assignable_to_role, bool):
            raise TypeError("Expected argument 'assignable_to_role' to be a bool")
        pulumi.set(__self__, "assignable_to_role", assignable_to_role)
        if auto_subscribe_new_members and not isinstance(auto_subscribe_new_members, bool):
            raise TypeError("Expected argument 'auto_subscribe_new_members' to be a bool")
        pulumi.set(__self__, "auto_subscribe_new_members", auto_subscribe_new_members)
        if behaviors and not isinstance(behaviors, list):
            raise TypeError("Expected argument 'behaviors' to be a list")
        pulumi.set(__self__, "behaviors", behaviors)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if display_name and not isinstance(display_name, str):
            raise TypeError("Expected argument 'display_name' to be a str")
        pulumi.set(__self__, "display_name", display_name)
        if dynamic_memberships and not isinstance(dynamic_memberships, list):
            raise TypeError("Expected argument 'dynamic_memberships' to be a list")
        pulumi.set(__self__, "dynamic_memberships", dynamic_memberships)
        if external_senders_allowed and not isinstance(external_senders_allowed, bool):
            raise TypeError("Expected argument 'external_senders_allowed' to be a bool")
        pulumi.set(__self__, "external_senders_allowed", external_senders_allowed)
        if hide_from_address_lists and not isinstance(hide_from_address_lists, bool):
            raise TypeError("Expected argument 'hide_from_address_lists' to be a bool")
        pulumi.set(__self__, "hide_from_address_lists", hide_from_address_lists)
        if hide_from_outlook_clients and not isinstance(hide_from_outlook_clients, bool):
            raise TypeError("Expected argument 'hide_from_outlook_clients' to be a bool")
        pulumi.set(__self__, "hide_from_outlook_clients", hide_from_outlook_clients)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if include_transitive_members and not isinstance(include_transitive_members, bool):
            raise TypeError("Expected argument 'include_transitive_members' to be a bool")
        pulumi.set(__self__, "include_transitive_members", include_transitive_members)
        if mail and not isinstance(mail, str):
            raise TypeError("Expected argument 'mail' to be a str")
        pulumi.set(__self__, "mail", mail)
        if mail_enabled and not isinstance(mail_enabled, bool):
            raise TypeError("Expected argument 'mail_enabled' to be a bool")
        pulumi.set(__self__, "mail_enabled", mail_enabled)
        if mail_nickname and not isinstance(mail_nickname, str):
            raise TypeError("Expected argument 'mail_nickname' to be a str")
        pulumi.set(__self__, "mail_nickname", mail_nickname)
        if members and not isinstance(members, list):
            raise TypeError("Expected argument 'members' to be a list")
        pulumi.set(__self__, "members", members)
        if object_id and not isinstance(object_id, str):
            raise TypeError("Expected argument 'object_id' to be a str")
        pulumi.set(__self__, "object_id", object_id)
        if onpremises_domain_name and not isinstance(onpremises_domain_name, str):
            raise TypeError("Expected argument 'onpremises_domain_name' to be a str")
        pulumi.set(__self__, "onpremises_domain_name", onpremises_domain_name)
        if onpremises_group_type and not isinstance(onpremises_group_type, str):
            raise TypeError("Expected argument 'onpremises_group_type' to be a str")
        pulumi.set(__self__, "onpremises_group_type", onpremises_group_type)
        if onpremises_netbios_name and not isinstance(onpremises_netbios_name, str):
            raise TypeError("Expected argument 'onpremises_netbios_name' to be a str")
        pulumi.set(__self__, "onpremises_netbios_name", onpremises_netbios_name)
        if onpremises_sam_account_name and not isinstance(onpremises_sam_account_name, str):
            raise TypeError("Expected argument 'onpremises_sam_account_name' to be a str")
        pulumi.set(__self__, "onpremises_sam_account_name", onpremises_sam_account_name)
        if onpremises_security_identifier and not isinstance(onpremises_security_identifier, str):
            raise TypeError("Expected argument 'onpremises_security_identifier' to be a str")
        pulumi.set(__self__, "onpremises_security_identifier", onpremises_security_identifier)
        if onpremises_sync_enabled and not isinstance(onpremises_sync_enabled, bool):
            raise TypeError("Expected argument 'onpremises_sync_enabled' to be a bool")
        pulumi.set(__self__, "onpremises_sync_enabled", onpremises_sync_enabled)
        if owners and not isinstance(owners, list):
            raise TypeError("Expected argument 'owners' to be a list")
        pulumi.set(__self__, "owners", owners)
        if preferred_language and not isinstance(preferred_language, str):
            raise TypeError("Expected argument 'preferred_language' to be a str")
        pulumi.set(__self__, "preferred_language", preferred_language)
        if provisioning_options and not isinstance(provisioning_options, list):
            raise TypeError("Expected argument 'provisioning_options' to be a list")
        pulumi.set(__self__, "provisioning_options", provisioning_options)
        if proxy_addresses and not isinstance(proxy_addresses, list):
            raise TypeError("Expected argument 'proxy_addresses' to be a list")
        pulumi.set(__self__, "proxy_addresses", proxy_addresses)
        if security_enabled and not isinstance(security_enabled, bool):
            raise TypeError("Expected argument 'security_enabled' to be a bool")
        pulumi.set(__self__, "security_enabled", security_enabled)
        if theme and not isinstance(theme, str):
            raise TypeError("Expected argument 'theme' to be a str")
        pulumi.set(__self__, "theme", theme)
        if types and not isinstance(types, list):
            raise TypeError("Expected argument 'types' to be a list")
        pulumi.set(__self__, "types", types)
        if visibility and not isinstance(visibility, str):
            raise TypeError("Expected argument 'visibility' to be a str")
        pulumi.set(__self__, "visibility", visibility)
        if writeback_enabled and not isinstance(writeback_enabled, bool):
            raise TypeError("Expected argument 'writeback_enabled' to be a bool")
        pulumi.set(__self__, "writeback_enabled", writeback_enabled)

    @property
    @pulumi.getter(name="assignableToRole")
    def assignable_to_role(self) -> bool:
        """
        Indicates whether this group can be assigned to an Azure Active Directory role.
        """
        return pulumi.get(self, "assignable_to_role")

    @property
    @pulumi.getter(name="autoSubscribeNewMembers")
    def auto_subscribe_new_members(self) -> bool:
        """
        Indicates whether new members added to the group will be auto-subscribed to receive email notifications. Only set for Unified groups.
        """
        return pulumi.get(self, "auto_subscribe_new_members")

    @property
    @pulumi.getter
    def behaviors(self) -> Sequence[str]:
        """
        A list of behaviors for a Microsoft 365 group, such as `AllowOnlyMembersToPost`, `HideGroupInOutlook`, `SubscribeNewGroupMembers` and `WelcomeEmailDisabled`. See [official documentation](https://docs.microsoft.com/en-us/graph/group-set-options) for more details.
        """
        return pulumi.get(self, "behaviors")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        The optional description of the group.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> str:
        """
        The display name for the group.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="dynamicMemberships")
    def dynamic_memberships(self) -> Sequence['outputs.GetGroupDynamicMembershipResult']:
        """
        A `dynamic_membership` block as documented below.
        """
        return pulumi.get(self, "dynamic_memberships")

    @property
    @pulumi.getter(name="externalSendersAllowed")
    def external_senders_allowed(self) -> bool:
        """
        Indicates whether people external to the organization can send messages to the group. Only set for Unified groups.
        """
        return pulumi.get(self, "external_senders_allowed")

    @property
    @pulumi.getter(name="hideFromAddressLists")
    def hide_from_address_lists(self) -> bool:
        """
        Indicates whether the group is displayed in certain parts of the Outlook user interface: in the Address Book, in address lists for selecting message recipients, and in the Browse Groups dialog for searching groups. Only set for Unified groups.
        """
        return pulumi.get(self, "hide_from_address_lists")

    @property
    @pulumi.getter(name="hideFromOutlookClients")
    def hide_from_outlook_clients(self) -> bool:
        """
        Indicates whether the group is displayed in Outlook clients, such as Outlook for Windows and Outlook on the web. Only set for Unified groups.
        """
        return pulumi.get(self, "hide_from_outlook_clients")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="includeTransitiveMembers")
    def include_transitive_members(self) -> Optional[bool]:
        return pulumi.get(self, "include_transitive_members")

    @property
    @pulumi.getter
    def mail(self) -> str:
        """
        The SMTP address for the group.
        """
        return pulumi.get(self, "mail")

    @property
    @pulumi.getter(name="mailEnabled")
    def mail_enabled(self) -> bool:
        """
        Whether the group is mail-enabled.
        """
        return pulumi.get(self, "mail_enabled")

    @property
    @pulumi.getter(name="mailNickname")
    def mail_nickname(self) -> str:
        """
        The mail alias for the group, unique in the organisation.
        """
        return pulumi.get(self, "mail_nickname")

    @property
    @pulumi.getter
    def members(self) -> Sequence[str]:
        """
        List of object IDs of the group members. When `include_transitive_members` is `true`, contains a list of object IDs of all transitive group members.
        """
        return pulumi.get(self, "members")

    @property
    @pulumi.getter(name="objectId")
    def object_id(self) -> str:
        """
        The object ID of the group.
        """
        return pulumi.get(self, "object_id")

    @property
    @pulumi.getter(name="onpremisesDomainName")
    def onpremises_domain_name(self) -> str:
        """
        The on-premises FQDN, also called dnsDomainName, synchronised from the on-premises directory when Azure AD Connect is used.
        """
        return pulumi.get(self, "onpremises_domain_name")

    @property
    @pulumi.getter(name="onpremisesGroupType")
    def onpremises_group_type(self) -> str:
        """
        The on-premises group type that the AAD group will be written as, when writeback is enabled. Possible values are `UniversalDistributionGroup`, `UniversalMailEnabledSecurityGroup`, or `UniversalSecurityGroup`.
        """
        return pulumi.get(self, "onpremises_group_type")

    @property
    @pulumi.getter(name="onpremisesNetbiosName")
    def onpremises_netbios_name(self) -> str:
        """
        The on-premises NetBIOS name, synchronised from the on-premises directory when Azure AD Connect is used.
        """
        return pulumi.get(self, "onpremises_netbios_name")

    @property
    @pulumi.getter(name="onpremisesSamAccountName")
    def onpremises_sam_account_name(self) -> str:
        """
        The on-premises SAM account name, synchronised from the on-premises directory when Azure AD Connect is used.
        """
        return pulumi.get(self, "onpremises_sam_account_name")

    @property
    @pulumi.getter(name="onpremisesSecurityIdentifier")
    def onpremises_security_identifier(self) -> str:
        """
        The on-premises security identifier (SID), synchronised from the on-premises directory when Azure AD Connect is used.
        """
        return pulumi.get(self, "onpremises_security_identifier")

    @property
    @pulumi.getter(name="onpremisesSyncEnabled")
    def onpremises_sync_enabled(self) -> bool:
        """
        Whether this group is synchronised from an on-premises directory (`true`), no longer synchronised (`false`), or has never been synchronised (`null`).
        """
        return pulumi.get(self, "onpremises_sync_enabled")

    @property
    @pulumi.getter
    def owners(self) -> Sequence[str]:
        """
        List of object IDs of the group owners.
        """
        return pulumi.get(self, "owners")

    @property
    @pulumi.getter(name="preferredLanguage")
    def preferred_language(self) -> str:
        """
        The preferred language for a Microsoft 365 group, in ISO 639-1 notation.
        """
        return pulumi.get(self, "preferred_language")

    @property
    @pulumi.getter(name="provisioningOptions")
    def provisioning_options(self) -> Sequence[str]:
        """
        A list of provisioning options for a Microsoft 365 group, such as `Team`. See [official documentation](https://docs.microsoft.com/en-us/graph/group-set-options) for details.
        """
        return pulumi.get(self, "provisioning_options")

    @property
    @pulumi.getter(name="proxyAddresses")
    def proxy_addresses(self) -> Sequence[str]:
        """
        List of email addresses for the group that direct to the same group mailbox.
        """
        return pulumi.get(self, "proxy_addresses")

    @property
    @pulumi.getter(name="securityEnabled")
    def security_enabled(self) -> bool:
        """
        Whether the group is a security group.
        """
        return pulumi.get(self, "security_enabled")

    @property
    @pulumi.getter
    def theme(self) -> str:
        """
        The colour theme for a Microsoft 365 group. Possible values are `Blue`, `Green`, `Orange`, `Pink`, `Purple`, `Red` or `Teal`. When no theme is set, the value is `null`.
        """
        return pulumi.get(self, "theme")

    @property
    @pulumi.getter
    def types(self) -> Sequence[str]:
        """
        A list of group types configured for the group. Supported values are `DynamicMembership`, which denotes a group with dynamic membership, and `Unified`, which specifies a Microsoft 365 group.
        """
        return pulumi.get(self, "types")

    @property
    @pulumi.getter
    def visibility(self) -> str:
        """
        The group join policy and group content visibility. Possible values are `Private`, `Public`, or `Hiddenmembership`. Only Microsoft 365 groups can have `Hiddenmembership` visibility.
        """
        return pulumi.get(self, "visibility")

    @property
    @pulumi.getter(name="writebackEnabled")
    def writeback_enabled(self) -> bool:
        """
        Whether the group will be written back to the configured on-premises Active Directory when Azure AD Connect is used.
        """
        return pulumi.get(self, "writeback_enabled")


class AwaitableGetGroupResult(GetGroupResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetGroupResult(
            assignable_to_role=self.assignable_to_role,
            auto_subscribe_new_members=self.auto_subscribe_new_members,
            behaviors=self.behaviors,
            description=self.description,
            display_name=self.display_name,
            dynamic_memberships=self.dynamic_memberships,
            external_senders_allowed=self.external_senders_allowed,
            hide_from_address_lists=self.hide_from_address_lists,
            hide_from_outlook_clients=self.hide_from_outlook_clients,
            id=self.id,
            include_transitive_members=self.include_transitive_members,
            mail=self.mail,
            mail_enabled=self.mail_enabled,
            mail_nickname=self.mail_nickname,
            members=self.members,
            object_id=self.object_id,
            onpremises_domain_name=self.onpremises_domain_name,
            onpremises_group_type=self.onpremises_group_type,
            onpremises_netbios_name=self.onpremises_netbios_name,
            onpremises_sam_account_name=self.onpremises_sam_account_name,
            onpremises_security_identifier=self.onpremises_security_identifier,
            onpremises_sync_enabled=self.onpremises_sync_enabled,
            owners=self.owners,
            preferred_language=self.preferred_language,
            provisioning_options=self.provisioning_options,
            proxy_addresses=self.proxy_addresses,
            security_enabled=self.security_enabled,
            theme=self.theme,
            types=self.types,
            visibility=self.visibility,
            writeback_enabled=self.writeback_enabled)


def get_group(display_name: Optional[str] = None,
              include_transitive_members: Optional[bool] = None,
              mail_enabled: Optional[bool] = None,
              mail_nickname: Optional[str] = None,
              object_id: Optional[str] = None,
              security_enabled: Optional[bool] = None,
              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetGroupResult:
    """
    Gets information about an Azure Active Directory group.

    ## API Permissions

    The following API permissions are required in order to use this data source.

    When authenticated with a service principal, this data source requires one of the following application roles: `Group.Read.All` or `Directory.Read.All`

    When authenticated with a user principal, this data source does not require any additional roles.

    ## Example Usage

    ### By Group Display Name)

    ```python
    import pulumi
    import pulumi_azuread as azuread

    example = azuread.get_group(display_name="MyGroupName",
        security_enabled=True)
    ```


    :param str display_name: The display name for the group.
    :param bool include_transitive_members: Whether to include transitive members (a flat list of all nested members). Defaults to `false`.
    :param bool mail_enabled: Whether the group is mail-enabled.
    :param str mail_nickname: The mail alias for the group, unique in the organisation.
    :param str object_id: Specifies the object ID of the group.
    :param bool security_enabled: Whether the group is a security group.
           
           > One of `display_name`, `object_id` or `mail_nickname` must be specified.
    """
    __args__ = dict()
    __args__['displayName'] = display_name
    __args__['includeTransitiveMembers'] = include_transitive_members
    __args__['mailEnabled'] = mail_enabled
    __args__['mailNickname'] = mail_nickname
    __args__['objectId'] = object_id
    __args__['securityEnabled'] = security_enabled
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('azuread:index/getGroup:getGroup', __args__, opts=opts, typ=GetGroupResult).value

    return AwaitableGetGroupResult(
        assignable_to_role=pulumi.get(__ret__, 'assignable_to_role'),
        auto_subscribe_new_members=pulumi.get(__ret__, 'auto_subscribe_new_members'),
        behaviors=pulumi.get(__ret__, 'behaviors'),
        description=pulumi.get(__ret__, 'description'),
        display_name=pulumi.get(__ret__, 'display_name'),
        dynamic_memberships=pulumi.get(__ret__, 'dynamic_memberships'),
        external_senders_allowed=pulumi.get(__ret__, 'external_senders_allowed'),
        hide_from_address_lists=pulumi.get(__ret__, 'hide_from_address_lists'),
        hide_from_outlook_clients=pulumi.get(__ret__, 'hide_from_outlook_clients'),
        id=pulumi.get(__ret__, 'id'),
        include_transitive_members=pulumi.get(__ret__, 'include_transitive_members'),
        mail=pulumi.get(__ret__, 'mail'),
        mail_enabled=pulumi.get(__ret__, 'mail_enabled'),
        mail_nickname=pulumi.get(__ret__, 'mail_nickname'),
        members=pulumi.get(__ret__, 'members'),
        object_id=pulumi.get(__ret__, 'object_id'),
        onpremises_domain_name=pulumi.get(__ret__, 'onpremises_domain_name'),
        onpremises_group_type=pulumi.get(__ret__, 'onpremises_group_type'),
        onpremises_netbios_name=pulumi.get(__ret__, 'onpremises_netbios_name'),
        onpremises_sam_account_name=pulumi.get(__ret__, 'onpremises_sam_account_name'),
        onpremises_security_identifier=pulumi.get(__ret__, 'onpremises_security_identifier'),
        onpremises_sync_enabled=pulumi.get(__ret__, 'onpremises_sync_enabled'),
        owners=pulumi.get(__ret__, 'owners'),
        preferred_language=pulumi.get(__ret__, 'preferred_language'),
        provisioning_options=pulumi.get(__ret__, 'provisioning_options'),
        proxy_addresses=pulumi.get(__ret__, 'proxy_addresses'),
        security_enabled=pulumi.get(__ret__, 'security_enabled'),
        theme=pulumi.get(__ret__, 'theme'),
        types=pulumi.get(__ret__, 'types'),
        visibility=pulumi.get(__ret__, 'visibility'),
        writeback_enabled=pulumi.get(__ret__, 'writeback_enabled'))


@_utilities.lift_output_func(get_group)
def get_group_output(display_name: Optional[pulumi.Input[Optional[str]]] = None,
                     include_transitive_members: Optional[pulumi.Input[Optional[bool]]] = None,
                     mail_enabled: Optional[pulumi.Input[Optional[bool]]] = None,
                     mail_nickname: Optional[pulumi.Input[Optional[str]]] = None,
                     object_id: Optional[pulumi.Input[Optional[str]]] = None,
                     security_enabled: Optional[pulumi.Input[Optional[bool]]] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetGroupResult]:
    """
    Gets information about an Azure Active Directory group.

    ## API Permissions

    The following API permissions are required in order to use this data source.

    When authenticated with a service principal, this data source requires one of the following application roles: `Group.Read.All` or `Directory.Read.All`

    When authenticated with a user principal, this data source does not require any additional roles.

    ## Example Usage

    ### By Group Display Name)

    ```python
    import pulumi
    import pulumi_azuread as azuread

    example = azuread.get_group(display_name="MyGroupName",
        security_enabled=True)
    ```


    :param str display_name: The display name for the group.
    :param bool include_transitive_members: Whether to include transitive members (a flat list of all nested members). Defaults to `false`.
    :param bool mail_enabled: Whether the group is mail-enabled.
    :param str mail_nickname: The mail alias for the group, unique in the organisation.
    :param str object_id: Specifies the object ID of the group.
    :param bool security_enabled: Whether the group is a security group.
           
           > One of `display_name`, `object_id` or `mail_nickname` must be specified.
    """
    ...
