r'''
# `databricks_automatic_cluster_update_workspace_setting`

Refer to the Terraform Registry for docs: [`databricks_automatic_cluster_update_workspace_setting`](https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class AutomaticClusterUpdateWorkspaceSetting(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSetting",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting databricks_automatic_cluster_update_workspace_setting}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        automatic_cluster_update_workspace: typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]],
        etag: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        setting_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting databricks_automatic_cluster_update_workspace_setting} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param automatic_cluster_update_workspace: automatic_cluster_update_workspace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#automatic_cluster_update_workspace AutomaticClusterUpdateWorkspaceSetting#automatic_cluster_update_workspace}
        :param etag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#etag AutomaticClusterUpdateWorkspaceSetting#etag}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#id AutomaticClusterUpdateWorkspaceSetting#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param setting_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#setting_name AutomaticClusterUpdateWorkspaceSetting#setting_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ebfc83f016a10f650fcbb2db8b1fbfa55d6d950a943ec4d79edc9060e5d485)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AutomaticClusterUpdateWorkspaceSettingConfig(
            automatic_cluster_update_workspace=automatic_cluster_update_workspace,
            etag=etag,
            id=id,
            setting_name=setting_name,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a AutomaticClusterUpdateWorkspaceSetting resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AutomaticClusterUpdateWorkspaceSetting to import.
        :param import_from_id: The id of the existing AutomaticClusterUpdateWorkspaceSetting that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AutomaticClusterUpdateWorkspaceSetting to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82945f25f5ffbe72ea39194e6f3bd320eb4935b7bf44054181d7a63826c9beb0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutomaticClusterUpdateWorkspace")
    def put_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#can_toggle AutomaticClusterUpdateWorkspaceSetting#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enabled AutomaticClusterUpdateWorkspaceSetting#enabled}.
        :param enablement_details: enablement_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enablement_details AutomaticClusterUpdateWorkspaceSetting#enablement_details}
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#maintenance_window AutomaticClusterUpdateWorkspaceSetting#maintenance_window}
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#restart_even_if_no_updates_available AutomaticClusterUpdateWorkspaceSetting#restart_even_if_no_updates_available}.
        '''
        value = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace(
            can_toggle=can_toggle,
            enabled=enabled,
            enablement_details=enablement_details,
            maintenance_window=maintenance_window,
            restart_even_if_no_updates_available=restart_even_if_no_updates_available,
        )

        return typing.cast(None, jsii.invoke(self, "putAutomaticClusterUpdateWorkspace", [value]))

    @jsii.member(jsii_name="resetEtag")
    def reset_etag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEtag", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSettingName")
    def reset_setting_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettingName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspace")
    def automatic_cluster_update_workspace(
        self,
    ) -> "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "automaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspaceInput")
    def automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace"]:
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace"], jsii.get(self, "automaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="etagInput")
    def etag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "etagInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="settingNameInput")
    def setting_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "settingNameInput"))

    @builtins.property
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @etag.setter
    def etag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__defd23d34ef3d71954190ea3658d64bab78fcc81afb1a3faeb235846cae27213)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "etag", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d4de4c93532bec2cdaad304383418909333d2b1bf0b5bd7c4c1e109e7f2ffc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="settingName")
    def setting_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "settingName"))

    @setting_name.setter
    def setting_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057ba424ffd5e318dee14af529842bd317693ee0387e83f7944e492085d2628a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "settingName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#can_toggle AutomaticClusterUpdateWorkspaceSetting#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enabled AutomaticClusterUpdateWorkspaceSetting#enabled}.
        :param enablement_details: enablement_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enablement_details AutomaticClusterUpdateWorkspaceSetting#enablement_details}
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#maintenance_window AutomaticClusterUpdateWorkspaceSetting#maintenance_window}
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#restart_even_if_no_updates_available AutomaticClusterUpdateWorkspaceSetting#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__779b0d1f79603176ed9c046085acef68ef2218de38ee06160674e4592dd1de32)
            check_type(argname="argument can_toggle", value=can_toggle, expected_type=type_hints["can_toggle"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument enablement_details", value=enablement_details, expected_type=type_hints["enablement_details"])
            check_type(argname="argument maintenance_window", value=maintenance_window, expected_type=type_hints["maintenance_window"])
            check_type(argname="argument restart_even_if_no_updates_available", value=restart_even_if_no_updates_available, expected_type=type_hints["restart_even_if_no_updates_available"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if can_toggle is not None:
            self._values["can_toggle"] = can_toggle
        if enabled is not None:
            self._values["enabled"] = enabled
        if enablement_details is not None:
            self._values["enablement_details"] = enablement_details
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if restart_even_if_no_updates_available is not None:
            self._values["restart_even_if_no_updates_available"] = restart_even_if_no_updates_available

    @builtins.property
    def can_toggle(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#can_toggle AutomaticClusterUpdateWorkspaceSetting#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enabled AutomaticClusterUpdateWorkspaceSetting#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''enablement_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#enablement_details AutomaticClusterUpdateWorkspaceSetting#enablement_details}
        '''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''maintenance_window block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#maintenance_window AutomaticClusterUpdateWorkspaceSetting#maintenance_window}
        '''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#restart_even_if_no_updates_available AutomaticClusterUpdateWorkspaceSetting#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#forced_for_compliance_mode AutomaticClusterUpdateWorkspaceSetting#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_disabled_entitlement AutomaticClusterUpdateWorkspaceSetting#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_non_enterprise_tier AutomaticClusterUpdateWorkspaceSetting#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2191689149ade9e10a6774820afd4bdcc5264f00159b2103b27824414b59ea90)
            check_type(argname="argument forced_for_compliance_mode", value=forced_for_compliance_mode, expected_type=type_hints["forced_for_compliance_mode"])
            check_type(argname="argument unavailable_for_disabled_entitlement", value=unavailable_for_disabled_entitlement, expected_type=type_hints["unavailable_for_disabled_entitlement"])
            check_type(argname="argument unavailable_for_non_enterprise_tier", value=unavailable_for_non_enterprise_tier, expected_type=type_hints["unavailable_for_non_enterprise_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if forced_for_compliance_mode is not None:
            self._values["forced_for_compliance_mode"] = forced_for_compliance_mode
        if unavailable_for_disabled_entitlement is not None:
            self._values["unavailable_for_disabled_entitlement"] = unavailable_for_disabled_entitlement
        if unavailable_for_non_enterprise_tier is not None:
            self._values["unavailable_for_non_enterprise_tier"] = unavailable_for_non_enterprise_tier

    @builtins.property
    def forced_for_compliance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#forced_for_compliance_mode AutomaticClusterUpdateWorkspaceSetting#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_disabled_entitlement AutomaticClusterUpdateWorkspaceSetting#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_non_enterprise_tier AutomaticClusterUpdateWorkspaceSetting#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a72b33487aff6b7dbf17e1a50c23b5e5d5fd5afe9b71a4653f063786ff4b44)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetForcedForComplianceMode")
    def reset_forced_for_compliance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForcedForComplianceMode", []))

    @jsii.member(jsii_name="resetUnavailableForDisabledEntitlement")
    def reset_unavailable_for_disabled_entitlement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForDisabledEntitlement", []))

    @jsii.member(jsii_name="resetUnavailableForNonEnterpriseTier")
    def reset_unavailable_for_non_enterprise_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForNonEnterpriseTier", []))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceModeInput")
    def forced_for_compliance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forcedForComplianceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlementInput")
    def unavailable_for_disabled_entitlement_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForDisabledEntitlementInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTierInput")
    def unavailable_for_non_enterprise_tier_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForNonEnterpriseTierInput"))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceMode")
    def forced_for_compliance_mode(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forcedForComplianceMode"))

    @forced_for_compliance_mode.setter
    def forced_for_compliance_mode(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfc1c949c08915527117c9f50bb97cf45837f088157bac1b42434298a2dcdb47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forcedForComplianceMode", value)

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlement")
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForDisabledEntitlement"))

    @unavailable_for_disabled_entitlement.setter
    def unavailable_for_disabled_entitlement(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__095a46e8aae4cdbfb9b409a9197406b385b9a3c7c813ea263f7c2efc08cc8aa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForDisabledEntitlement", value)

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTier")
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForNonEnterpriseTier"))

    @unavailable_for_non_enterprise_tier.setter
    def unavailable_for_non_enterprise_tier(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b64f15619c4503927ce8e0704624f6616bef22482416c741ad7ee6536a8bc30f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b56d03fa50ad382c77564963b8176d40c14f28494ae0383f707af3727c7eb8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: week_day_based_schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#week_day_based_schedule AutomaticClusterUpdateWorkspaceSetting#week_day_based_schedule}
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30fa031b04a12bff21de4f0475e9aa92bd907b3a18a9ba4a470241c158a79a0a)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''week_day_based_schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#week_day_based_schedule AutomaticClusterUpdateWorkspaceSetting#week_day_based_schedule}
        '''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4b03b4604f1e8bf380daa6dff7de11f52a5c2d2883ee8e1fab9e8805e548ed1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#day_of_week AutomaticClusterUpdateWorkspaceSetting#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#frequency AutomaticClusterUpdateWorkspaceSetting#frequency}.
        :param window_start_time: window_start_time block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#window_start_time AutomaticClusterUpdateWorkspaceSetting#window_start_time}
        '''
        value = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
            day_of_week=day_of_week,
            frequency=frequency,
            window_start_time=window_start_time,
        )

        return typing.cast(None, jsii.invoke(self, "putWeekDayBasedSchedule", [value]))

    @jsii.member(jsii_name="resetWeekDayBasedSchedule")
    def reset_week_day_based_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeekDayBasedSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedSchedule")
    def week_day_based_schedule(
        self,
    ) -> "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__396106a20c274420543315e8d2db8bfb36221d239774e212f46757f154d4fd97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#day_of_week AutomaticClusterUpdateWorkspaceSetting#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#frequency AutomaticClusterUpdateWorkspaceSetting#frequency}.
        :param window_start_time: window_start_time block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#window_start_time AutomaticClusterUpdateWorkspaceSetting#window_start_time}
        '''
        if isinstance(window_start_time, dict):
            window_start_time = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b80b7c4735b8806371ecde4279d7c5245b88891a017e63b2c36d983960bf013b)
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument window_start_time", value=window_start_time, expected_type=type_hints["window_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day_of_week is not None:
            self._values["day_of_week"] = day_of_week
        if frequency is not None:
            self._values["frequency"] = frequency
        if window_start_time is not None:
            self._values["window_start_time"] = window_start_time

    @builtins.property
    def day_of_week(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#day_of_week AutomaticClusterUpdateWorkspaceSetting#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#frequency AutomaticClusterUpdateWorkspaceSetting#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''window_start_time block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#window_start_time AutomaticClusterUpdateWorkspaceSetting#window_start_time}
        '''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8d90be73bcd57c798c5035ade93bc9548d848b67a48b7f4a3ce5a22bdfff53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWindowStartTime")
    def put_window_start_time(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#hours AutomaticClusterUpdateWorkspaceSetting#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#minutes AutomaticClusterUpdateWorkspaceSetting#minutes}.
        '''
        value = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
            hours=hours, minutes=minutes
        )

        return typing.cast(None, jsii.invoke(self, "putWindowStartTime", [value]))

    @jsii.member(jsii_name="resetDayOfWeek")
    def reset_day_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDayOfWeek", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetWindowStartTime")
    def reset_window_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowStartTime", []))

    @builtins.property
    @jsii.member(jsii_name="windowStartTime")
    def window_start_time(
        self,
    ) -> "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property
    @jsii.member(jsii_name="windowStartTimeInput")
    def window_start_time_input(
        self,
    ) -> typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        return typing.cast(typing.Optional["AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b58ce83afa7d1a214802be4428ffa93ddafa081dca581e31a2a4f672b36daf66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value)

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc92f5b5c8b4992e1dba649c20242d452f3fc2d161ab1f137422210871628b4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27d2312695d205f24369cf09f9b3d9a9be06b6b55e2672f0a050474b1dfdc1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#hours AutomaticClusterUpdateWorkspaceSetting#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#minutes AutomaticClusterUpdateWorkspaceSetting#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dd585ffbef0c9645a320ba09ed91cdc949951a72616ecec44917d08eb5670cc)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#hours AutomaticClusterUpdateWorkspaceSetting#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#minutes AutomaticClusterUpdateWorkspaceSetting#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f438fbce40850c9d65309b2de07c502d2ea2449243d2fd8bced1a24d0137794)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHours")
    def reset_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHours", []))

    @jsii.member(jsii_name="resetMinutes")
    def reset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinutes", []))

    @builtins.property
    @jsii.member(jsii_name="hoursInput")
    def hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hoursInput"))

    @builtins.property
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property
    @jsii.member(jsii_name="hours")
    def hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hours"))

    @hours.setter
    def hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcd5026969b78272d0f0f685e88a3029eba809997f128123c5c04de71d07a4c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value)

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b9de4b880dd5f9dbbf88eb3212194f819043b11542f8a0e4f7dbfe3fc8f807)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c767fbf64ec593084364eeda4ac111f7150a7ec47d8775267c3ee4e95addc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__229c3ab1817d8dc65bb66a2fb4b263d93c1a6725e507b712922c883a8d0dc73a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEnablementDetails")
    def put_enablement_details(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#forced_for_compliance_mode AutomaticClusterUpdateWorkspaceSetting#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_disabled_entitlement AutomaticClusterUpdateWorkspaceSetting#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#unavailable_for_non_enterprise_tier AutomaticClusterUpdateWorkspaceSetting#unavailable_for_non_enterprise_tier}.
        '''
        value = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: week_day_based_schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#week_day_based_schedule AutomaticClusterUpdateWorkspaceSetting#week_day_based_schedule}
        '''
        value = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow(
            week_day_based_schedule=week_day_based_schedule
        )

        return typing.cast(None, jsii.invoke(self, "putMaintenanceWindow", [value]))

    @jsii.member(jsii_name="resetCanToggle")
    def reset_can_toggle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanToggle", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnablementDetails")
    def reset_enablement_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablementDetails", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetRestartEvenIfNoUpdatesAvailable")
    def reset_restart_even_if_no_updates_available(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartEvenIfNoUpdatesAvailable", []))

    @builtins.property
    @jsii.member(jsii_name="enablementDetails")
    def enablement_details(
        self,
    ) -> AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

    @builtins.property
    @jsii.member(jsii_name="canToggleInput")
    def can_toggle_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "canToggleInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enablementDetailsInput")
    def enablement_details_input(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailableInput")
    def restart_even_if_no_updates_available_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "restartEvenIfNoUpdatesAvailableInput"))

    @builtins.property
    @jsii.member(jsii_name="canToggle")
    def can_toggle(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "canToggle"))

    @can_toggle.setter
    def can_toggle(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5f1b440ede3815f5e1768b18191861bc00067b28dfce6b66ec94ac56709a57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canToggle", value)

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9034d846af5e36b3a6e3f93c9acd0fc96b2961e0df6ff0870b17280fed0261e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailable")
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "restartEvenIfNoUpdatesAvailable"))

    @restart_even_if_no_updates_available.setter
    def restart_even_if_no_updates_available(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec9663da20e276fe4d1def7344517068bc1492bb2f8a6a33039d8e3f4f852643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace]:
        return typing.cast(typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ab773ebb6462b542df5b1f1d240d3d5c3af258b5c893e45021ae93d6619bafd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.automaticClusterUpdateWorkspaceSetting.AutomaticClusterUpdateWorkspaceSettingConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "automatic_cluster_update_workspace": "automaticClusterUpdateWorkspace",
        "etag": "etag",
        "id": "id",
        "setting_name": "settingName",
    },
)
class AutomaticClusterUpdateWorkspaceSettingConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        automatic_cluster_update_workspace: typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]],
        etag: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        setting_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param automatic_cluster_update_workspace: automatic_cluster_update_workspace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#automatic_cluster_update_workspace AutomaticClusterUpdateWorkspaceSetting#automatic_cluster_update_workspace}
        :param etag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#etag AutomaticClusterUpdateWorkspaceSetting#etag}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#id AutomaticClusterUpdateWorkspaceSetting#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param setting_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#setting_name AutomaticClusterUpdateWorkspaceSetting#setting_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(automatic_cluster_update_workspace, dict):
            automatic_cluster_update_workspace = AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace(**automatic_cluster_update_workspace)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fa1281ba2cc1c2b6dcb23579f1c15601b70bcfd3f8f18e726823afaff9926b8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument automatic_cluster_update_workspace", value=automatic_cluster_update_workspace, expected_type=type_hints["automatic_cluster_update_workspace"])
            check_type(argname="argument etag", value=etag, expected_type=type_hints["etag"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument setting_name", value=setting_name, expected_type=type_hints["setting_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "automatic_cluster_update_workspace": automatic_cluster_update_workspace,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if etag is not None:
            self._values["etag"] = etag
        if id is not None:
            self._values["id"] = id
        if setting_name is not None:
            self._values["setting_name"] = setting_name

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def automatic_cluster_update_workspace(
        self,
    ) -> AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace:
        '''automatic_cluster_update_workspace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#automatic_cluster_update_workspace AutomaticClusterUpdateWorkspaceSetting#automatic_cluster_update_workspace}
        '''
        result = self._values.get("automatic_cluster_update_workspace")
        assert result is not None, "Required property 'automatic_cluster_update_workspace' is missing"
        return typing.cast(AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace, result)

    @builtins.property
    def etag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#etag AutomaticClusterUpdateWorkspaceSetting#etag}.'''
        result = self._values.get("etag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#id AutomaticClusterUpdateWorkspaceSetting#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def setting_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/automatic_cluster_update_workspace_setting#setting_name AutomaticClusterUpdateWorkspaceSetting#setting_name}.'''
        result = self._values.get("setting_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomaticClusterUpdateWorkspaceSettingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AutomaticClusterUpdateWorkspaceSetting",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceOutputReference",
    "AutomaticClusterUpdateWorkspaceSettingConfig",
]

publication.publish()

def _typecheckingstub__56ebfc83f016a10f650fcbb2db8b1fbfa55d6d950a943ec4d79edc9060e5d485(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    automatic_cluster_update_workspace: typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]],
    etag: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    setting_name: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82945f25f5ffbe72ea39194e6f3bd320eb4935b7bf44054181d7a63826c9beb0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__defd23d34ef3d71954190ea3658d64bab78fcc81afb1a3faeb235846cae27213(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d4de4c93532bec2cdaad304383418909333d2b1bf0b5bd7c4c1e109e7f2ffc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057ba424ffd5e318dee14af529842bd317693ee0387e83f7944e492085d2628a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__779b0d1f79603176ed9c046085acef68ef2218de38ee06160674e4592dd1de32(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2191689149ade9e10a6774820afd4bdcc5264f00159b2103b27824414b59ea90(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a72b33487aff6b7dbf17e1a50c23b5e5d5fd5afe9b71a4653f063786ff4b44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfc1c949c08915527117c9f50bb97cf45837f088157bac1b42434298a2dcdb47(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__095a46e8aae4cdbfb9b409a9197406b385b9a3c7c813ea263f7c2efc08cc8aa5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b64f15619c4503927ce8e0704624f6616bef22482416c741ad7ee6536a8bc30f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b56d03fa50ad382c77564963b8176d40c14f28494ae0383f707af3727c7eb8c(
    value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceEnablementDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30fa031b04a12bff21de4f0475e9aa92bd907b3a18a9ba4a470241c158a79a0a(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4b03b4604f1e8bf380daa6dff7de11f52a5c2d2883ee8e1fab9e8805e548ed1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__396106a20c274420543315e8d2db8bfb36221d239774e212f46757f154d4fd97(
    value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindow],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b80b7c4735b8806371ecde4279d7c5245b88891a017e63b2c36d983960bf013b(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8d90be73bcd57c798c5035ade93bc9548d848b67a48b7f4a3ce5a22bdfff53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b58ce83afa7d1a214802be4428ffa93ddafa081dca581e31a2a4f672b36daf66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc92f5b5c8b4992e1dba649c20242d452f3fc2d161ab1f137422210871628b4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27d2312695d205f24369cf09f9b3d9a9be06b6b55e2672f0a050474b1dfdc1dd(
    value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dd585ffbef0c9645a320ba09ed91cdc949951a72616ecec44917d08eb5670cc(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f438fbce40850c9d65309b2de07c502d2ea2449243d2fd8bced1a24d0137794(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcd5026969b78272d0f0f685e88a3029eba809997f128123c5c04de71d07a4c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b9de4b880dd5f9dbbf88eb3212194f819043b11542f8a0e4f7dbfe3fc8f807(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c767fbf64ec593084364eeda4ac111f7150a7ec47d8775267c3ee4e95addc8(
    value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__229c3ab1817d8dc65bb66a2fb4b263d93c1a6725e507b712922c883a8d0dc73a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5f1b440ede3815f5e1768b18191861bc00067b28dfce6b66ec94ac56709a57(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9034d846af5e36b3a6e3f93c9acd0fc96b2961e0df6ff0870b17280fed0261e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec9663da20e276fe4d1def7344517068bc1492bb2f8a6a33039d8e3f4f852643(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ab773ebb6462b542df5b1f1d240d3d5c3af258b5c893e45021ae93d6619bafd(
    value: typing.Optional[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa1281ba2cc1c2b6dcb23579f1c15601b70bcfd3f8f18e726823afaff9926b8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    automatic_cluster_update_workspace: typing.Union[AutomaticClusterUpdateWorkspaceSettingAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]],
    etag: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    setting_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
