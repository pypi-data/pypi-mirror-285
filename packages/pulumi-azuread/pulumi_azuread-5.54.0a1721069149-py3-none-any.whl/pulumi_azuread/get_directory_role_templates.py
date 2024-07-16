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
    'GetDirectoryRoleTemplatesResult',
    'AwaitableGetDirectoryRoleTemplatesResult',
    'get_directory_role_templates',
    'get_directory_role_templates_output',
]

@pulumi.output_type
class GetDirectoryRoleTemplatesResult:
    """
    A collection of values returned by getDirectoryRoleTemplates.
    """
    def __init__(__self__, id=None, object_ids=None, role_templates=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if object_ids and not isinstance(object_ids, list):
            raise TypeError("Expected argument 'object_ids' to be a list")
        pulumi.set(__self__, "object_ids", object_ids)
        if role_templates and not isinstance(role_templates, list):
            raise TypeError("Expected argument 'role_templates' to be a list")
        pulumi.set(__self__, "role_templates", role_templates)

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="objectIds")
    def object_ids(self) -> Sequence[str]:
        """
        The object IDs of the role templates.
        """
        return pulumi.get(self, "object_ids")

    @property
    @pulumi.getter(name="roleTemplates")
    def role_templates(self) -> Sequence['outputs.GetDirectoryRoleTemplatesRoleTemplateResult']:
        """
        A list of role templates. Each `role_template` object provides the attributes documented below.
        """
        return pulumi.get(self, "role_templates")


class AwaitableGetDirectoryRoleTemplatesResult(GetDirectoryRoleTemplatesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetDirectoryRoleTemplatesResult(
            id=self.id,
            object_ids=self.object_ids,
            role_templates=self.role_templates)


def get_directory_role_templates(opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetDirectoryRoleTemplatesResult:
    """
    Use this data source to access information about directory role templates within Azure Active Directory.

    ## API Permissions

    The following API permissions are required in order to use this resource.

    When authenticated with a service principal, this resource requires one of the following application roles: `RoleManagement.Read.Directory` or `Directory.Read.All`

    When authenticated with a user principal, this data source does not require any additional roles.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azuread as azuread

    current = azuread.get_directory_role_templates()
    pulumi.export("roles", current.object_ids)
    ```
    """
    __args__ = dict()
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('azuread:index/getDirectoryRoleTemplates:getDirectoryRoleTemplates', __args__, opts=opts, typ=GetDirectoryRoleTemplatesResult).value

    return AwaitableGetDirectoryRoleTemplatesResult(
        id=pulumi.get(__ret__, 'id'),
        object_ids=pulumi.get(__ret__, 'object_ids'),
        role_templates=pulumi.get(__ret__, 'role_templates'))


@_utilities.lift_output_func(get_directory_role_templates)
def get_directory_role_templates_output(opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetDirectoryRoleTemplatesResult]:
    """
    Use this data source to access information about directory role templates within Azure Active Directory.

    ## API Permissions

    The following API permissions are required in order to use this resource.

    When authenticated with a service principal, this resource requires one of the following application roles: `RoleManagement.Read.Directory` or `Directory.Read.All`

    When authenticated with a user principal, this data source does not require any additional roles.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azuread as azuread

    current = azuread.get_directory_role_templates()
    pulumi.export("roles", current.object_ids)
    ```
    """
    ...
