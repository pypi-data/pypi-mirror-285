r'''
# `databricks_model_serving`

Refer to the Terraform Registry for docs: [`databricks_model_serving`](https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving).
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


class ModelServing(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServing",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving databricks_model_serving}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        config: typing.Union["ModelServingConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving databricks_model_serving} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#config ModelServing#config}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#id ModelServing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param route_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#tags ModelServing#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#timeouts ModelServing#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcdceab54e050923170b39eff538055f8b76b660bb8732c203c9c67261d31d37)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = ModelServingConfig(
            config=config,
            name=name,
            id=id,
            rate_limits=rate_limits,
            route_optimized=route_optimized,
            tags=tags,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ModelServing resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ModelServing to import.
        :param import_from_id: The id of the existing ModelServing that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ModelServing to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1bb539ded3a1716a5800f3c306bd3bf91c26ca2eb1bd182e8248cdbaff5430)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        auto_capture_config: typing.Optional[typing.Union["ModelServingConfigAutoCaptureConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_capture_config: auto_capture_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_entities ModelServing#served_entities}
        :param served_models: served_models block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_models ModelServing#served_models}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        value = ModelServingConfigA(
            auto_capture_config=auto_capture_config,
            served_entities=served_entities,
            served_models=served_models,
            traffic_config=traffic_config,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putRateLimits")
    def put_rate_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a275a6bfdceace553e2be007a16e27fa4711760199dc7e1aa3df554d09920e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRateLimits", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9a326d60c6d2388605269123ef001af7186ca3f81f93ddf683edaaa2863033b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#create ModelServing#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#update ModelServing#update}.
        '''
        value = ModelServingTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRateLimits")
    def reset_rate_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimits", []))

    @jsii.member(jsii_name="resetRouteOptimized")
    def reset_route_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteOptimized", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "ModelServingConfigAOutputReference":
        return typing.cast("ModelServingConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="rateLimits")
    def rate_limits(self) -> "ModelServingRateLimitsList":
        return typing.cast("ModelServingRateLimitsList", jsii.get(self, "rateLimits"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointId")
    def serving_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servingEndpointId"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ModelServingTagsList":
        return typing.cast("ModelServingTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ModelServingTimeoutsOutputReference":
        return typing.cast("ModelServingTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["ModelServingConfigA"]:
        return typing.cast(typing.Optional["ModelServingConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitsInput")
    def rate_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]], jsii.get(self, "rateLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="routeOptimizedInput")
    def route_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "routeOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ModelServingTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754d4971dd64df250d28b3640fa44fa399b715301fc0dd43ff8d8304e9ef8d25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb43c6ec513eda5c793054e174b6c273a821c9b323b20667ced44837696142c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="routeOptimized")
    def route_optimized(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "routeOptimized"))

    @route_optimized.setter
    def route_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d34de5d9b9fed3c9898fd854fd3464a901fd46e11ea543b532dd7d7a7df273a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeOptimized", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "name": "name",
        "id": "id",
        "rate_limits": "rateLimits",
        "route_optimized": "routeOptimized",
        "tags": "tags",
        "timeouts": "timeouts",
    },
)
class ModelServingConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: typing.Union["ModelServingConfigA", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingRateLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["ModelServingTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#config ModelServing#config}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#id ModelServing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rate_limits: rate_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        :param route_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#tags ModelServing#tags}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#timeouts ModelServing#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = ModelServingConfigA(**config)
        if isinstance(timeouts, dict):
            timeouts = ModelServingTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ab99c61d3a667a89d9f5f2278213a6b075df770286584a1c864bfffbe20082)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rate_limits", value=rate_limits, expected_type=type_hints["rate_limits"])
            check_type(argname="argument route_optimized", value=route_optimized, expected_type=type_hints["route_optimized"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "name": name,
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
        if id is not None:
            self._values["id"] = id
        if rate_limits is not None:
            self._values["rate_limits"] = rate_limits
        if route_optimized is not None:
            self._values["route_optimized"] = route_optimized
        if tags is not None:
            self._values["tags"] = tags
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def config(self) -> "ModelServingConfigA":
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#config ModelServing#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("ModelServingConfigA", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#id ModelServing#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rate_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]]:
        '''rate_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#rate_limits ModelServing#rate_limits}
        '''
        result = self._values.get("rate_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingRateLimits"]]], result)

    @builtins.property
    def route_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#route_optimized ModelServing#route_optimized}.'''
        result = self._values.get("route_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#tags ModelServing#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingTags"]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ModelServingTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#timeouts ModelServing#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ModelServingTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "auto_capture_config": "autoCaptureConfig",
        "served_entities": "servedEntities",
        "served_models": "servedModels",
        "traffic_config": "trafficConfig",
    },
)
class ModelServingConfigA:
    def __init__(
        self,
        *,
        auto_capture_config: typing.Optional[typing.Union["ModelServingConfigAutoCaptureConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic_config: typing.Optional[typing.Union["ModelServingConfigTrafficConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_capture_config: auto_capture_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        :param served_entities: served_entities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_entities ModelServing#served_entities}
        :param served_models: served_models block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_models ModelServing#served_models}
        :param traffic_config: traffic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        if isinstance(auto_capture_config, dict):
            auto_capture_config = ModelServingConfigAutoCaptureConfig(**auto_capture_config)
        if isinstance(traffic_config, dict):
            traffic_config = ModelServingConfigTrafficConfig(**traffic_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f209635c93e31eb79747b450ef07f331215993fe3c611af60329c1181395d96)
            check_type(argname="argument auto_capture_config", value=auto_capture_config, expected_type=type_hints["auto_capture_config"])
            check_type(argname="argument served_entities", value=served_entities, expected_type=type_hints["served_entities"])
            check_type(argname="argument served_models", value=served_models, expected_type=type_hints["served_models"])
            check_type(argname="argument traffic_config", value=traffic_config, expected_type=type_hints["traffic_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_capture_config is not None:
            self._values["auto_capture_config"] = auto_capture_config
        if served_entities is not None:
            self._values["served_entities"] = served_entities
        if served_models is not None:
            self._values["served_models"] = served_models
        if traffic_config is not None:
            self._values["traffic_config"] = traffic_config

    @builtins.property
    def auto_capture_config(
        self,
    ) -> typing.Optional["ModelServingConfigAutoCaptureConfig"]:
        '''auto_capture_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#auto_capture_config ModelServing#auto_capture_config}
        '''
        result = self._values.get("auto_capture_config")
        return typing.cast(typing.Optional["ModelServingConfigAutoCaptureConfig"], result)

    @builtins.property
    def served_entities(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]]:
        '''served_entities block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_entities ModelServing#served_entities}
        '''
        result = self._values.get("served_entities")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]], result)

    @builtins.property
    def served_models(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]]:
        '''served_models block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_models ModelServing#served_models}
        '''
        result = self._values.get("served_models")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]], result)

    @builtins.property
    def traffic_config(self) -> typing.Optional["ModelServingConfigTrafficConfig"]:
        '''traffic_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#traffic_config ModelServing#traffic_config}
        '''
        result = self._values.get("traffic_config")
        return typing.cast(typing.Optional["ModelServingConfigTrafficConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39de19fd4e2e3b391a36cec3ae6b58c26f839e9b7717318f9c83712d464b8240)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoCaptureConfig")
    def put_auto_capture_config(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        value = ModelServingConfigAutoCaptureConfig(
            catalog_name=catalog_name,
            enabled=enabled,
            schema_name=schema_name,
            table_name_prefix=table_name_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoCaptureConfig", [value]))

    @jsii.member(jsii_name="putServedEntities")
    def put_served_entities(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedEntities", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9147fd79fb2787c00f1d1d5fcb304fbacd554791d29739786eb47f169656f6f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedEntities", [value]))

    @jsii.member(jsii_name="putServedModels")
    def put_served_models(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigServedModels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ca446d7fd23d5b8a13db8091cb8d50a52da9d34dc0d71f3453cc4df48cef58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServedModels", [value]))

    @jsii.member(jsii_name="putTrafficConfig")
    def put_traffic_config(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#routes ModelServing#routes}
        '''
        value = ModelServingConfigTrafficConfig(routes=routes)

        return typing.cast(None, jsii.invoke(self, "putTrafficConfig", [value]))

    @jsii.member(jsii_name="resetAutoCaptureConfig")
    def reset_auto_capture_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoCaptureConfig", []))

    @jsii.member(jsii_name="resetServedEntities")
    def reset_served_entities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedEntities", []))

    @jsii.member(jsii_name="resetServedModels")
    def reset_served_models(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServedModels", []))

    @jsii.member(jsii_name="resetTrafficConfig")
    def reset_traffic_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficConfig", []))

    @builtins.property
    @jsii.member(jsii_name="autoCaptureConfig")
    def auto_capture_config(
        self,
    ) -> "ModelServingConfigAutoCaptureConfigOutputReference":
        return typing.cast("ModelServingConfigAutoCaptureConfigOutputReference", jsii.get(self, "autoCaptureConfig"))

    @builtins.property
    @jsii.member(jsii_name="servedEntities")
    def served_entities(self) -> "ModelServingConfigServedEntitiesList":
        return typing.cast("ModelServingConfigServedEntitiesList", jsii.get(self, "servedEntities"))

    @builtins.property
    @jsii.member(jsii_name="servedModels")
    def served_models(self) -> "ModelServingConfigServedModelsList":
        return typing.cast("ModelServingConfigServedModelsList", jsii.get(self, "servedModels"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfig")
    def traffic_config(self) -> "ModelServingConfigTrafficConfigOutputReference":
        return typing.cast("ModelServingConfigTrafficConfigOutputReference", jsii.get(self, "trafficConfig"))

    @builtins.property
    @jsii.member(jsii_name="autoCaptureConfigInput")
    def auto_capture_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigAutoCaptureConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigAutoCaptureConfig"], jsii.get(self, "autoCaptureConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="servedEntitiesInput")
    def served_entities_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedEntities"]]], jsii.get(self, "servedEntitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="servedModelsInput")
    def served_models_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigServedModels"]]], jsii.get(self, "servedModelsInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficConfigInput")
    def traffic_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigTrafficConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigTrafficConfig"], jsii.get(self, "trafficConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigA]:
        return typing.cast(typing.Optional[ModelServingConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ModelServingConfigA]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9ca6d2b3625d2fe9064559e5ae3834b4a7d876e85a62ac1aedf940272c521b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAutoCaptureConfig",
    jsii_struct_bases=[],
    name_mapping={
        "catalog_name": "catalogName",
        "enabled": "enabled",
        "schema_name": "schemaName",
        "table_name_prefix": "tableNamePrefix",
    },
)
class ModelServingConfigAutoCaptureConfig:
    def __init__(
        self,
        *,
        catalog_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schema_name: typing.Optional[builtins.str] = None,
        table_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#enabled ModelServing#enabled}.
        :param schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#schema_name ModelServing#schema_name}.
        :param table_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf8b2cb451924e6518496f1ef57ccd7f223277cadafa3d24b53b01883eebebe)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument schema_name", value=schema_name, expected_type=type_hints["schema_name"])
            check_type(argname="argument table_name_prefix", value=table_name_prefix, expected_type=type_hints["table_name_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name
        if enabled is not None:
            self._values["enabled"] = enabled
        if schema_name is not None:
            self._values["schema_name"] = schema_name
        if table_name_prefix is not None:
            self._values["table_name_prefix"] = table_name_prefix

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#catalog_name ModelServing#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#enabled ModelServing#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schema_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#schema_name ModelServing#schema_name}.'''
        result = self._values.get("schema_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#table_name_prefix ModelServing#table_name_prefix}.'''
        result = self._values.get("table_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigAutoCaptureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigAutoCaptureConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigAutoCaptureConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67b5a32de74ec757f3fd7506a723ede01a5cbb72fe8a9e8f7f55a463e336efb9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCatalogName")
    def reset_catalog_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalogName", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetSchemaName")
    def reset_schema_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchemaName", []))

    @jsii.member(jsii_name="resetTableNamePrefix")
    def reset_table_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableNamePrefix", []))

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaNameInput")
    def schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefixInput")
    def table_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d853ac5156bce5e1133f54bfb86fe697d8ede486fe731bfa34903faa9f25753c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__f88136c1faf06edab8a7bc50c6c0024a15189007716a85bd8e4bdf7614acadd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="schemaName")
    def schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaName"))

    @schema_name.setter
    def schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7efdad892ab787aa5957098c51102ad9ba0b8cbd0427823bc099599637c9475)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaName", value)

    @builtins.property
    @jsii.member(jsii_name="tableNamePrefix")
    def table_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableNamePrefix"))

    @table_name_prefix.setter
    def table_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8067336e1bc5f02cec3e8f5ba3e25eee6475ed8fb875a21dee0d49ed8a33c796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableNamePrefix", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigAutoCaptureConfig]:
        return typing.cast(typing.Optional[ModelServingConfigAutoCaptureConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigAutoCaptureConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db8d7706dcbc2a14ef38e7145ac608ca0bbc7781baea610fd87821dbd601e6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntities",
    jsii_struct_bases=[],
    name_mapping={
        "entity_name": "entityName",
        "entity_version": "entityVersion",
        "environment_vars": "environmentVars",
        "external_model": "externalModel",
        "instance_profile_arn": "instanceProfileArn",
        "max_provisioned_throughput": "maxProvisionedThroughput",
        "min_provisioned_throughput": "minProvisionedThroughput",
        "name": "name",
        "scale_to_zero_enabled": "scaleToZeroEnabled",
        "workload_size": "workloadSize",
        "workload_type": "workloadType",
    },
)
class ModelServingConfigServedEntities:
    def __init__(
        self,
        *,
        entity_name: typing.Optional[builtins.str] = None,
        entity_version: typing.Optional[builtins.str] = None,
        environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        external_model: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModel", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        max_provisioned_throughput: typing.Optional[jsii.Number] = None,
        min_provisioned_throughput: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_size: typing.Optional[builtins.str] = None,
        workload_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#entity_name ModelServing#entity_name}.
        :param entity_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#entity_version ModelServing#entity_version}.
        :param environment_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.
        :param external_model: external_model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#external_model ModelServing#external_model}
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        :param max_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.
        :param min_provisioned_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param scale_to_zero_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.
        :param workload_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_size ModelServing#workload_size}.
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_type ModelServing#workload_type}.
        '''
        if isinstance(external_model, dict):
            external_model = ModelServingConfigServedEntitiesExternalModel(**external_model)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9403ea38a33e4adf7cbe8b181e16d03e70709409f2f5b3cd020360a19e5995d8)
            check_type(argname="argument entity_name", value=entity_name, expected_type=type_hints["entity_name"])
            check_type(argname="argument entity_version", value=entity_version, expected_type=type_hints["entity_version"])
            check_type(argname="argument environment_vars", value=environment_vars, expected_type=type_hints["environment_vars"])
            check_type(argname="argument external_model", value=external_model, expected_type=type_hints["external_model"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument max_provisioned_throughput", value=max_provisioned_throughput, expected_type=type_hints["max_provisioned_throughput"])
            check_type(argname="argument min_provisioned_throughput", value=min_provisioned_throughput, expected_type=type_hints["min_provisioned_throughput"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument scale_to_zero_enabled", value=scale_to_zero_enabled, expected_type=type_hints["scale_to_zero_enabled"])
            check_type(argname="argument workload_size", value=workload_size, expected_type=type_hints["workload_size"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entity_name is not None:
            self._values["entity_name"] = entity_name
        if entity_version is not None:
            self._values["entity_version"] = entity_version
        if environment_vars is not None:
            self._values["environment_vars"] = environment_vars
        if external_model is not None:
            self._values["external_model"] = external_model
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if max_provisioned_throughput is not None:
            self._values["max_provisioned_throughput"] = max_provisioned_throughput
        if min_provisioned_throughput is not None:
            self._values["min_provisioned_throughput"] = min_provisioned_throughput
        if name is not None:
            self._values["name"] = name
        if scale_to_zero_enabled is not None:
            self._values["scale_to_zero_enabled"] = scale_to_zero_enabled
        if workload_size is not None:
            self._values["workload_size"] = workload_size
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def entity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#entity_name ModelServing#entity_name}.'''
        result = self._values.get("entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#entity_version ModelServing#entity_version}.'''
        result = self._values.get("entity_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.'''
        result = self._values.get("environment_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def external_model(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModel"]:
        '''external_model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#external_model ModelServing#external_model}
        '''
        result = self._values.get("external_model")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModel"], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#max_provisioned_throughput ModelServing#max_provisioned_throughput}.'''
        result = self._values.get("max_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_provisioned_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#min_provisioned_throughput ModelServing#min_provisioned_throughput}.'''
        result = self._values.get("min_provisioned_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_to_zero_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.'''
        result = self._values.get("scale_to_zero_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_size ModelServing#workload_size}.'''
        result = self._values.get("workload_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workload_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_type ModelServing#workload_type}.'''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModel",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "provider": "provider",
        "task": "task",
        "ai21_labs_config": "ai21LabsConfig",
        "amazon_bedrock_config": "amazonBedrockConfig",
        "anthropic_config": "anthropicConfig",
        "cohere_config": "cohereConfig",
        "databricks_model_serving_config": "databricksModelServingConfig",
        "openai_config": "openaiConfig",
        "palm_config": "palmConfig",
    },
)
class ModelServingConfigServedEntitiesExternalModel:
    def __init__(
        self,
        *,
        name: builtins.str,
        provider: builtins.str,
        task: builtins.str,
        ai21_labs_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        amazon_bedrock_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        anthropic_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelAnthropicConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        cohere_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelCohereConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        databricks_model_serving_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        openai_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelOpenaiConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        palm_config: typing.Optional[typing.Union["ModelServingConfigServedEntitiesExternalModelPalmConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#provider ModelServing#provider}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#task ModelServing#task}.
        :param ai21_labs_config: ai21labs_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        :param amazon_bedrock_config: amazon_bedrock_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        :param anthropic_config: anthropic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        :param cohere_config: cohere_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        :param databricks_model_serving_config: databricks_model_serving_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        :param openai_config: openai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_config ModelServing#openai_config}
        :param palm_config: palm_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        if isinstance(ai21_labs_config, dict):
            ai21_labs_config = ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(**ai21_labs_config)
        if isinstance(amazon_bedrock_config, dict):
            amazon_bedrock_config = ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(**amazon_bedrock_config)
        if isinstance(anthropic_config, dict):
            anthropic_config = ModelServingConfigServedEntitiesExternalModelAnthropicConfig(**anthropic_config)
        if isinstance(cohere_config, dict):
            cohere_config = ModelServingConfigServedEntitiesExternalModelCohereConfig(**cohere_config)
        if isinstance(databricks_model_serving_config, dict):
            databricks_model_serving_config = ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(**databricks_model_serving_config)
        if isinstance(openai_config, dict):
            openai_config = ModelServingConfigServedEntitiesExternalModelOpenaiConfig(**openai_config)
        if isinstance(palm_config, dict):
            palm_config = ModelServingConfigServedEntitiesExternalModelPalmConfig(**palm_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b566f9c1a169a08e2dd41b8ad9ddbe16d86060bfdb3621f6f0b19ed393bf4b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
            check_type(argname="argument ai21_labs_config", value=ai21_labs_config, expected_type=type_hints["ai21_labs_config"])
            check_type(argname="argument amazon_bedrock_config", value=amazon_bedrock_config, expected_type=type_hints["amazon_bedrock_config"])
            check_type(argname="argument anthropic_config", value=anthropic_config, expected_type=type_hints["anthropic_config"])
            check_type(argname="argument cohere_config", value=cohere_config, expected_type=type_hints["cohere_config"])
            check_type(argname="argument databricks_model_serving_config", value=databricks_model_serving_config, expected_type=type_hints["databricks_model_serving_config"])
            check_type(argname="argument openai_config", value=openai_config, expected_type=type_hints["openai_config"])
            check_type(argname="argument palm_config", value=palm_config, expected_type=type_hints["palm_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "provider": provider,
            "task": task,
        }
        if ai21_labs_config is not None:
            self._values["ai21_labs_config"] = ai21_labs_config
        if amazon_bedrock_config is not None:
            self._values["amazon_bedrock_config"] = amazon_bedrock_config
        if anthropic_config is not None:
            self._values["anthropic_config"] = anthropic_config
        if cohere_config is not None:
            self._values["cohere_config"] = cohere_config
        if databricks_model_serving_config is not None:
            self._values["databricks_model_serving_config"] = databricks_model_serving_config
        if openai_config is not None:
            self._values["openai_config"] = openai_config
        if palm_config is not None:
            self._values["palm_config"] = palm_config

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#provider ModelServing#provider}.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#task ModelServing#task}.'''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ai21_labs_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig"]:
        '''ai21labs_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        '''
        result = self._values.get("ai21_labs_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAi21LabsConfig"], result)

    @builtins.property
    def amazon_bedrock_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig"]:
        '''amazon_bedrock_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        '''
        result = self._values.get("amazon_bedrock_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig"], result)

    @builtins.property
    def anthropic_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelAnthropicConfig"]:
        '''anthropic_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        '''
        result = self._values.get("anthropic_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelAnthropicConfig"], result)

    @builtins.property
    def cohere_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelCohereConfig"]:
        '''cohere_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        '''
        result = self._values.get("cohere_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelCohereConfig"], result)

    @builtins.property
    def databricks_model_serving_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig"]:
        '''databricks_model_serving_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        '''
        result = self._values.get("databricks_model_serving_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig"], result)

    @builtins.property
    def openai_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelOpenaiConfig"]:
        '''openai_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_config ModelServing#openai_config}
        '''
        result = self._values.get("openai_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelOpenaiConfig"], result)

    @builtins.property
    def palm_config(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"]:
        '''palm_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        result = self._values.get("palm_config")
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAi21LabsConfig",
    jsii_struct_bases=[],
    name_mapping={"ai21_labs_api_key": "ai21LabsApiKey"},
)
class ModelServingConfigServedEntitiesExternalModelAi21LabsConfig:
    def __init__(self, *, ai21_labs_api_key: builtins.str) -> None:
        '''
        :param ai21_labs_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c0ee9dc2d1327236ae97d5c3fe5c5338c3794a40d2d88c02560c83925676710)
            check_type(argname="argument ai21_labs_api_key", value=ai21_labs_api_key, expected_type=type_hints["ai21_labs_api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ai21_labs_api_key": ai21_labs_api_key,
        }

    @builtins.property
    def ai21_labs_api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.'''
        result = self._values.get("ai21_labs_api_key")
        assert result is not None, "Required property 'ai21_labs_api_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec48b6283533d5b4c9aeb09b046668b46db9832fe3be06b87645bbc1fe6b77af)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKeyInput")
    def ai21_labs_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ai21LabsApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsApiKey")
    def ai21_labs_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ai21LabsApiKey"))

    @ai21_labs_api_key.setter
    def ai21_labs_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edd2ee0da33d9d6eea9698dda6843afedb835973ae8037fa09e4c0271c49a7d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ai21LabsApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b145ea06e1bd8516ff0cc11cbf9fd2f0e536da81a5b9c4cbc7ff9c0165bb85a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig",
    jsii_struct_bases=[],
    name_mapping={
        "aws_access_key_id": "awsAccessKeyId",
        "aws_region": "awsRegion",
        "aws_secret_access_key": "awsSecretAccessKey",
        "bedrock_provider": "bedrockProvider",
    },
)
class ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig:
    def __init__(
        self,
        *,
        aws_access_key_id: builtins.str,
        aws_region: builtins.str,
        aws_secret_access_key: builtins.str,
        bedrock_provider: builtins.str,
    ) -> None:
        '''
        :param aws_access_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_region ModelServing#aws_region}.
        :param aws_secret_access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.
        :param bedrock_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90dd82469e7808adf0a9158c33b32ac196f631841b5b828af93d7f461ae108ca)
            check_type(argname="argument aws_access_key_id", value=aws_access_key_id, expected_type=type_hints["aws_access_key_id"])
            check_type(argname="argument aws_region", value=aws_region, expected_type=type_hints["aws_region"])
            check_type(argname="argument aws_secret_access_key", value=aws_secret_access_key, expected_type=type_hints["aws_secret_access_key"])
            check_type(argname="argument bedrock_provider", value=bedrock_provider, expected_type=type_hints["bedrock_provider"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aws_access_key_id": aws_access_key_id,
            "aws_region": aws_region,
            "aws_secret_access_key": aws_secret_access_key,
            "bedrock_provider": bedrock_provider,
        }

    @builtins.property
    def aws_access_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.'''
        result = self._values.get("aws_access_key_id")
        assert result is not None, "Required property 'aws_access_key_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_region ModelServing#aws_region}.'''
        result = self._values.get("aws_region")
        assert result is not None, "Required property 'aws_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_secret_access_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.'''
        result = self._values.get("aws_secret_access_key")
        assert result is not None, "Required property 'aws_secret_access_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bedrock_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.'''
        result = self._values.get("bedrock_provider")
        assert result is not None, "Required property 'bedrock_provider' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f80d852ac84bb277b80e781606f1e4dd2b8f0b03f4b4f4ce3d3d3f4f752061e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdInput")
    def aws_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsRegionInput")
    def aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyInput")
    def aws_secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSecretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="bedrockProviderInput")
    def bedrock_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bedrockProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyId")
    def aws_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessKeyId"))

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a72a91085af2cd622a5c4761f65046e6b7f2a78c1bd2cb36a4dcac5671bdb1f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d32624b5e375ebc73dc077d306d42c18f51d38659a7f1881d39b43af1a5693cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsRegion", value)

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKey")
    def aws_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsSecretAccessKey"))

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8628231e26f171719205ff1342000dc222ab9ce51be0e6d9ad62573609694543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKey", value)

    @builtins.property
    @jsii.member(jsii_name="bedrockProvider")
    def bedrock_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bedrockProvider"))

    @bedrock_provider.setter
    def bedrock_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c269a46ec95800bb1f6e9e676994c75ad9c42fc985f8a721b147636f09ea1add)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bedrockProvider", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee68940f0acb9b42fcf03a36fc4c76724008a5a5bd4d0a07014abf027865cf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAnthropicConfig",
    jsii_struct_bases=[],
    name_mapping={"anthropic_api_key": "anthropicApiKey"},
)
class ModelServingConfigServedEntitiesExternalModelAnthropicConfig:
    def __init__(self, *, anthropic_api_key: builtins.str) -> None:
        '''
        :param anthropic_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__218f5a41e3d93d07362768598313f8b6139fdb7702b337199d420fb89c368361)
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "anthropic_api_key": anthropic_api_key,
        }

    @builtins.property
    def anthropic_api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.'''
        result = self._values.get("anthropic_api_key")
        assert result is not None, "Required property 'anthropic_api_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelAnthropicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd5800a1e5ff7cbebc7e2b6b8a7272a5844a5b75fcb4202bafab87d419f8cb2f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "anthropicApiKey"))

    @anthropic_api_key.setter
    def anthropic_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b023fe17c98d566c8fac5e33cf5eab2d6ab8b5f2aac678aab6bc169b3745228)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a64d693f11d3435c35e4ed3c8d0458aadee5227005cf5947d024560f5846c673)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCohereConfig",
    jsii_struct_bases=[],
    name_mapping={"cohere_api_key": "cohereApiKey"},
)
class ModelServingConfigServedEntitiesExternalModelCohereConfig:
    def __init__(self, *, cohere_api_key: builtins.str) -> None:
        '''
        :param cohere_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dcb9995c75742d273441f3c12353f2a8a2afcd41c6de6865efd4504723a0455)
            check_type(argname="argument cohere_api_key", value=cohere_api_key, expected_type=type_hints["cohere_api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cohere_api_key": cohere_api_key,
        }

    @builtins.property
    def cohere_api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.'''
        result = self._values.get("cohere_api_key")
        assert result is not None, "Required property 'cohere_api_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelCohereConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49817b6641b2bf6dfba75fda89240974cad2adba5d155e98e85da7ac13731ecb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="cohereApiKeyInput")
    def cohere_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cohereApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereApiKey")
    def cohere_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cohereApiKey"))

    @cohere_api_key.setter
    def cohere_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b46b4f09d11ea820e7e30599eccb4dc33c186404ec5c41a642550f3c870525)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cohereApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a60f8a840727e7cd3ce21617d1ae19459196adef749e8e5126eb54fd90b745a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "databricks_api_token": "databricksApiToken",
        "databricks_workspace_url": "databricksWorkspaceUrl",
    },
)
class ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig:
    def __init__(
        self,
        *,
        databricks_api_token: builtins.str,
        databricks_workspace_url: builtins.str,
    ) -> None:
        '''
        :param databricks_api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.
        :param databricks_workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc7d014e30705b1d364c1fdbb4051d5a7521e5c6874f14751d9b24ade962ccae)
            check_type(argname="argument databricks_api_token", value=databricks_api_token, expected_type=type_hints["databricks_api_token"])
            check_type(argname="argument databricks_workspace_url", value=databricks_workspace_url, expected_type=type_hints["databricks_workspace_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "databricks_api_token": databricks_api_token,
            "databricks_workspace_url": databricks_workspace_url,
        }

    @builtins.property
    def databricks_api_token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.'''
        result = self._values.get("databricks_api_token")
        assert result is not None, "Required property 'databricks_api_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def databricks_workspace_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.'''
        result = self._values.get("databricks_workspace_url")
        assert result is not None, "Required property 'databricks_workspace_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cda49ad248f1b0eb4e12f1d86fc09682a280a677deaf69662836e58db84f468)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="databricksApiTokenInput")
    def databricks_api_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksApiTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksWorkspaceUrlInput")
    def databricks_workspace_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksWorkspaceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksApiToken")
    def databricks_api_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksApiToken"))

    @databricks_api_token.setter
    def databricks_api_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a09b862ceaf8807cca67fb6c462f92e28e9578762c5c262d8bfba2228fd0f6d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksApiToken", value)

    @builtins.property
    @jsii.member(jsii_name="databricksWorkspaceUrl")
    def databricks_workspace_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databricksWorkspaceUrl"))

    @databricks_workspace_url.setter
    def databricks_workspace_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764fd45b87e6fd1d6cc9ef7428ca7893495c45311e54982f5cf24b55fe956143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksWorkspaceUrl", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a2eeb97c7e347fa469adfa492f6e516d30265f9a57baa620b6237d20f748bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOpenaiConfig",
    jsii_struct_bases=[],
    name_mapping={
        "microsoft_entra_client_id": "microsoftEntraClientId",
        "microsoft_entra_client_secret": "microsoftEntraClientSecret",
        "microsoft_entra_tenant_id": "microsoftEntraTenantId",
        "openai_api_base": "openaiApiBase",
        "openai_api_key": "openaiApiKey",
        "openai_api_type": "openaiApiType",
        "openai_api_version": "openaiApiVersion",
        "openai_deployment_name": "openaiDeploymentName",
        "openai_organization": "openaiOrganization",
    },
)
class ModelServingConfigServedEntitiesExternalModelOpenaiConfig:
    def __init__(
        self,
        *,
        microsoft_entra_client_id: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
        microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
        openai_api_base: typing.Optional[builtins.str] = None,
        openai_api_key: typing.Optional[builtins.str] = None,
        openai_api_type: typing.Optional[builtins.str] = None,
        openai_api_version: typing.Optional[builtins.str] = None,
        openai_deployment_name: typing.Optional[builtins.str] = None,
        openai_organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param microsoft_entra_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.
        :param microsoft_entra_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.
        :param microsoft_entra_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.
        :param openai_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.
        :param openai_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.
        :param openai_api_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.
        :param openai_api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.
        :param openai_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.
        :param openai_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8f3651cd444a6a03a04e10e5b69221f40bf7182b94e27a3f39209873e1a2293)
            check_type(argname="argument microsoft_entra_client_id", value=microsoft_entra_client_id, expected_type=type_hints["microsoft_entra_client_id"])
            check_type(argname="argument microsoft_entra_client_secret", value=microsoft_entra_client_secret, expected_type=type_hints["microsoft_entra_client_secret"])
            check_type(argname="argument microsoft_entra_tenant_id", value=microsoft_entra_tenant_id, expected_type=type_hints["microsoft_entra_tenant_id"])
            check_type(argname="argument openai_api_base", value=openai_api_base, expected_type=type_hints["openai_api_base"])
            check_type(argname="argument openai_api_key", value=openai_api_key, expected_type=type_hints["openai_api_key"])
            check_type(argname="argument openai_api_type", value=openai_api_type, expected_type=type_hints["openai_api_type"])
            check_type(argname="argument openai_api_version", value=openai_api_version, expected_type=type_hints["openai_api_version"])
            check_type(argname="argument openai_deployment_name", value=openai_deployment_name, expected_type=type_hints["openai_deployment_name"])
            check_type(argname="argument openai_organization", value=openai_organization, expected_type=type_hints["openai_organization"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if microsoft_entra_client_id is not None:
            self._values["microsoft_entra_client_id"] = microsoft_entra_client_id
        if microsoft_entra_client_secret is not None:
            self._values["microsoft_entra_client_secret"] = microsoft_entra_client_secret
        if microsoft_entra_tenant_id is not None:
            self._values["microsoft_entra_tenant_id"] = microsoft_entra_tenant_id
        if openai_api_base is not None:
            self._values["openai_api_base"] = openai_api_base
        if openai_api_key is not None:
            self._values["openai_api_key"] = openai_api_key
        if openai_api_type is not None:
            self._values["openai_api_type"] = openai_api_type
        if openai_api_version is not None:
            self._values["openai_api_version"] = openai_api_version
        if openai_deployment_name is not None:
            self._values["openai_deployment_name"] = openai_deployment_name
        if openai_organization is not None:
            self._values["openai_organization"] = openai_organization

    @builtins.property
    def microsoft_entra_client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.'''
        result = self._values.get("microsoft_entra_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_client_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.'''
        result = self._values.get("microsoft_entra_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_entra_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.'''
        result = self._values.get("microsoft_entra_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_base(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.'''
        result = self._values.get("openai_api_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.'''
        result = self._values.get("openai_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.'''
        result = self._values.get("openai_api_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_api_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.'''
        result = self._values.get("openai_api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_deployment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.'''
        result = self._values.get("openai_deployment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openai_organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.'''
        result = self._values.get("openai_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelOpenaiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96eca2227ca1f6fbe25592666bfb974076efa4c4f49bad0f227b4a2e3eb17f28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMicrosoftEntraClientId")
    def reset_microsoft_entra_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraClientId", []))

    @jsii.member(jsii_name="resetMicrosoftEntraClientSecret")
    def reset_microsoft_entra_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraClientSecret", []))

    @jsii.member(jsii_name="resetMicrosoftEntraTenantId")
    def reset_microsoft_entra_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftEntraTenantId", []))

    @jsii.member(jsii_name="resetOpenaiApiBase")
    def reset_openai_api_base(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiBase", []))

    @jsii.member(jsii_name="resetOpenaiApiKey")
    def reset_openai_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiKey", []))

    @jsii.member(jsii_name="resetOpenaiApiType")
    def reset_openai_api_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiType", []))

    @jsii.member(jsii_name="resetOpenaiApiVersion")
    def reset_openai_api_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiApiVersion", []))

    @jsii.member(jsii_name="resetOpenaiDeploymentName")
    def reset_openai_deployment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiDeploymentName", []))

    @jsii.member(jsii_name="resetOpenaiOrganization")
    def reset_openai_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiOrganization", []))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientIdInput")
    def microsoft_entra_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecretInput")
    def microsoft_entra_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraTenantIdInput")
    def microsoft_entra_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftEntraTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiBaseInput")
    def openai_api_base_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiBaseInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiKeyInput")
    def openai_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiTypeInput")
    def openai_api_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiApiVersionInput")
    def openai_api_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiApiVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiDeploymentNameInput")
    def openai_deployment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiDeploymentNameInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiOrganizationInput")
    def openai_organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openaiOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientId")
    def microsoft_entra_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientId"))

    @microsoft_entra_client_id.setter
    def microsoft_entra_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01bce6ae02663c936859b6fdd65bf9c0787e0a2cbca469a27e0254691e4f99e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientId", value)

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraClientSecret")
    def microsoft_entra_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraClientSecret"))

    @microsoft_entra_client_secret.setter
    def microsoft_entra_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8acf6fc23afd1ec6f16b8d814ba0c5fd3202eb75dc88075e6fa2e70bf74e1a24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraClientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="microsoftEntraTenantId")
    def microsoft_entra_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftEntraTenantId"))

    @microsoft_entra_tenant_id.setter
    def microsoft_entra_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810652b88b687685a4925c644374a2c91f370a298407a4299026d674b5c21875)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftEntraTenantId", value)

    @builtins.property
    @jsii.member(jsii_name="openaiApiBase")
    def openai_api_base(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiBase"))

    @openai_api_base.setter
    def openai_api_base(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d910ae46138165d13f96fcad38ba4d03ea99b4f6398de8d21648bf91c47f812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiBase", value)

    @builtins.property
    @jsii.member(jsii_name="openaiApiKey")
    def openai_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiKey"))

    @openai_api_key.setter
    def openai_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2942665469b2d114c5b1da0a35801aba473b6fd397a92822aba7a01d3bdb6a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="openaiApiType")
    def openai_api_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiType"))

    @openai_api_type.setter
    def openai_api_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa62ef264416b3877aac41273f2288de305f9b5513e98b5feda0976afb36e2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiType", value)

    @builtins.property
    @jsii.member(jsii_name="openaiApiVersion")
    def openai_api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiApiVersion"))

    @openai_api_version.setter
    def openai_api_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c39917ad5aa16b52b380336edcb2f53961c8750fdc6125952517ccc54b6a951)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiApiVersion", value)

    @builtins.property
    @jsii.member(jsii_name="openaiDeploymentName")
    def openai_deployment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiDeploymentName"))

    @openai_deployment_name.setter
    def openai_deployment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__139733bf0f71f12b8e4408aa3bb941024091eb852488a633b731789178eda8c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiDeploymentName", value)

    @builtins.property
    @jsii.member(jsii_name="openaiOrganization")
    def openai_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openaiOrganization"))

    @openai_organization.setter
    def openai_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6bd90ea04878cc2aeedd21c4ab7495629f3d00b634d97096aff7e311c7d9b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openaiOrganization", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0833c7b0577230e49679060b337fdaee600a3cc50d57218dab1a5fcc76ee558f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingConfigServedEntitiesExternalModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__286957a797d7d3795901e718c685222247720c7959b31372363ced1053c8349c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAi21LabsConfig")
    def put_ai21_labs_config(self, *, ai21_labs_api_key: builtins.str) -> None:
        '''
        :param ai21_labs_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_api_key ModelServing#ai21labs_api_key}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAi21LabsConfig(
            ai21_labs_api_key=ai21_labs_api_key
        )

        return typing.cast(None, jsii.invoke(self, "putAi21LabsConfig", [value]))

    @jsii.member(jsii_name="putAmazonBedrockConfig")
    def put_amazon_bedrock_config(
        self,
        *,
        aws_access_key_id: builtins.str,
        aws_region: builtins.str,
        aws_secret_access_key: builtins.str,
        bedrock_provider: builtins.str,
    ) -> None:
        '''
        :param aws_access_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_access_key_id ModelServing#aws_access_key_id}.
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_region ModelServing#aws_region}.
        :param aws_secret_access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#aws_secret_access_key ModelServing#aws_secret_access_key}.
        :param bedrock_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#bedrock_provider ModelServing#bedrock_provider}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig(
            aws_access_key_id=aws_access_key_id,
            aws_region=aws_region,
            aws_secret_access_key=aws_secret_access_key,
            bedrock_provider=bedrock_provider,
        )

        return typing.cast(None, jsii.invoke(self, "putAmazonBedrockConfig", [value]))

    @jsii.member(jsii_name="putAnthropicConfig")
    def put_anthropic_config(self, *, anthropic_api_key: builtins.str) -> None:
        '''
        :param anthropic_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_api_key ModelServing#anthropic_api_key}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelAnthropicConfig(
            anthropic_api_key=anthropic_api_key
        )

        return typing.cast(None, jsii.invoke(self, "putAnthropicConfig", [value]))

    @jsii.member(jsii_name="putCohereConfig")
    def put_cohere_config(self, *, cohere_api_key: builtins.str) -> None:
        '''
        :param cohere_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_api_key ModelServing#cohere_api_key}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelCohereConfig(
            cohere_api_key=cohere_api_key
        )

        return typing.cast(None, jsii.invoke(self, "putCohereConfig", [value]))

    @jsii.member(jsii_name="putDatabricksModelServingConfig")
    def put_databricks_model_serving_config(
        self,
        *,
        databricks_api_token: builtins.str,
        databricks_workspace_url: builtins.str,
    ) -> None:
        '''
        :param databricks_api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_api_token ModelServing#databricks_api_token}.
        :param databricks_workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_workspace_url ModelServing#databricks_workspace_url}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig(
            databricks_api_token=databricks_api_token,
            databricks_workspace_url=databricks_workspace_url,
        )

        return typing.cast(None, jsii.invoke(self, "putDatabricksModelServingConfig", [value]))

    @jsii.member(jsii_name="putOpenaiConfig")
    def put_openai_config(
        self,
        *,
        microsoft_entra_client_id: typing.Optional[builtins.str] = None,
        microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
        microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
        openai_api_base: typing.Optional[builtins.str] = None,
        openai_api_key: typing.Optional[builtins.str] = None,
        openai_api_type: typing.Optional[builtins.str] = None,
        openai_api_version: typing.Optional[builtins.str] = None,
        openai_deployment_name: typing.Optional[builtins.str] = None,
        openai_organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param microsoft_entra_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_id ModelServing#microsoft_entra_client_id}.
        :param microsoft_entra_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_client_secret ModelServing#microsoft_entra_client_secret}.
        :param microsoft_entra_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#microsoft_entra_tenant_id ModelServing#microsoft_entra_tenant_id}.
        :param openai_api_base: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_base ModelServing#openai_api_base}.
        :param openai_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_key ModelServing#openai_api_key}.
        :param openai_api_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_type ModelServing#openai_api_type}.
        :param openai_api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_api_version ModelServing#openai_api_version}.
        :param openai_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_deployment_name ModelServing#openai_deployment_name}.
        :param openai_organization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_organization ModelServing#openai_organization}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelOpenaiConfig(
            microsoft_entra_client_id=microsoft_entra_client_id,
            microsoft_entra_client_secret=microsoft_entra_client_secret,
            microsoft_entra_tenant_id=microsoft_entra_tenant_id,
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            openai_api_type=openai_api_type,
            openai_api_version=openai_api_version,
            openai_deployment_name=openai_deployment_name,
            openai_organization=openai_organization,
        )

        return typing.cast(None, jsii.invoke(self, "putOpenaiConfig", [value]))

    @jsii.member(jsii_name="putPalmConfig")
    def put_palm_config(self, *, palm_api_key: builtins.str) -> None:
        '''
        :param palm_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.
        '''
        value = ModelServingConfigServedEntitiesExternalModelPalmConfig(
            palm_api_key=palm_api_key
        )

        return typing.cast(None, jsii.invoke(self, "putPalmConfig", [value]))

    @jsii.member(jsii_name="resetAi21LabsConfig")
    def reset_ai21_labs_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAi21LabsConfig", []))

    @jsii.member(jsii_name="resetAmazonBedrockConfig")
    def reset_amazon_bedrock_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmazonBedrockConfig", []))

    @jsii.member(jsii_name="resetAnthropicConfig")
    def reset_anthropic_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicConfig", []))

    @jsii.member(jsii_name="resetCohereConfig")
    def reset_cohere_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCohereConfig", []))

    @jsii.member(jsii_name="resetDatabricksModelServingConfig")
    def reset_databricks_model_serving_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksModelServingConfig", []))

    @jsii.member(jsii_name="resetOpenaiConfig")
    def reset_openai_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenaiConfig", []))

    @jsii.member(jsii_name="resetPalmConfig")
    def reset_palm_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPalmConfig", []))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsConfig")
    def ai21_labs_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference, jsii.get(self, "ai21LabsConfig"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfig")
    def amazon_bedrock_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference, jsii.get(self, "amazonBedrockConfig"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfig")
    def anthropic_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference, jsii.get(self, "anthropicConfig"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfig")
    def cohere_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference, jsii.get(self, "cohereConfig"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfig")
    def databricks_model_serving_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference, jsii.get(self, "databricksModelServingConfig"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfig")
    def openai_config(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference, jsii.get(self, "openaiConfig"))

    @builtins.property
    @jsii.member(jsii_name="palmConfig")
    def palm_config(
        self,
    ) -> "ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference":
        return typing.cast("ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference", jsii.get(self, "palmConfig"))

    @builtins.property
    @jsii.member(jsii_name="ai21LabsConfigInput")
    def ai21_labs_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig], jsii.get(self, "ai21LabsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="amazonBedrockConfigInput")
    def amazon_bedrock_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig], jsii.get(self, "amazonBedrockConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicConfigInput")
    def anthropic_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig], jsii.get(self, "anthropicConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="cohereConfigInput")
    def cohere_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig], jsii.get(self, "cohereConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksModelServingConfigInput")
    def databricks_model_serving_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig], jsii.get(self, "databricksModelServingConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="openaiConfigInput")
    def openai_config_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig], jsii.get(self, "openaiConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="palmConfigInput")
    def palm_config_input(
        self,
    ) -> typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"]:
        return typing.cast(typing.Optional["ModelServingConfigServedEntitiesExternalModelPalmConfig"], jsii.get(self, "palmConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="taskInput")
    def task_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__186cb5665bc59aaa9ce409cb8208fb7dd40871e7acf79134bf4c7cdc5c10a2c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12796f48f59357a3d01909964205037a61611468763c992eaf3a5e51a410b9d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value)

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55764731d175dec17e4fc1dd16886f842c2d8074da5de0878b95679f89c7a6d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModel]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModel], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModel],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23c418f265754be146809c589f248006a2e823e8931bce27139b60be00a944fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelPalmConfig",
    jsii_struct_bases=[],
    name_mapping={"palm_api_key": "palmApiKey"},
)
class ModelServingConfigServedEntitiesExternalModelPalmConfig:
    def __init__(self, *, palm_api_key: builtins.str) -> None:
        '''
        :param palm_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d7f69696e468cd3ad5ffddae6add89fbf9597eef2db2a900972795882f84260)
            check_type(argname="argument palm_api_key", value=palm_api_key, expected_type=type_hints["palm_api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "palm_api_key": palm_api_key,
        }

    @builtins.property
    def palm_api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_api_key ModelServing#palm_api_key}.'''
        result = self._values.get("palm_api_key")
        assert result is not None, "Required property 'palm_api_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedEntitiesExternalModelPalmConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2415e41a2d65031da7ad03ff288304364d2a75d69e744f5986dbebe1cd84314)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="palmApiKeyInput")
    def palm_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "palmApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="palmApiKey")
    def palm_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "palmApiKey"))

    @palm_api_key.setter
    def palm_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d267a559f3a647aa1bad3826b5c511002c6e84c231d14e688498f3452c1edc93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "palmApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c92e50429bcc356c4a64039fd323e25eec3aac1617b8e44b20de759640c3439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingConfigServedEntitiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5b118db3d06fdd140973d3aa4cc3a885623a42ff336d2eba7d45380b7f73959)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigServedEntitiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77acb6ce6c67f79a9b0d1314c0324692cb1fa6f244647ce53272762d81da2526)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigServedEntitiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a14f5528daebd60ea2786187c3c5a4423f153db7ab0e49a07d1ebac0cae40d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b2a27fd791322888d58ee916ba218a9018446d6ac345466008049d6bd107087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee9cad630026f7541c897b5d7427a66841f3a7b37ea702e67476de9e4e66337f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db21c169a62214a095fb313b873f0316c06668343c8a393d69f0adf180eee16d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingConfigServedEntitiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedEntitiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bce219b1818dd301c72b49d3cd1ee61649975cbfc261e27ce547ecf3c22dd279)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putExternalModel")
    def put_external_model(
        self,
        *,
        name: builtins.str,
        provider: builtins.str,
        task: builtins.str,
        ai21_labs_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        amazon_bedrock_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        anthropic_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cohere_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        databricks_model_serving_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        openai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        palm_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#provider ModelServing#provider}.
        :param task: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#task ModelServing#task}.
        :param ai21_labs_config: ai21labs_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#ai21labs_config ModelServing#ai21labs_config}
        :param amazon_bedrock_config: amazon_bedrock_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#amazon_bedrock_config ModelServing#amazon_bedrock_config}
        :param anthropic_config: anthropic_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#anthropic_config ModelServing#anthropic_config}
        :param cohere_config: cohere_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#cohere_config ModelServing#cohere_config}
        :param databricks_model_serving_config: databricks_model_serving_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#databricks_model_serving_config ModelServing#databricks_model_serving_config}
        :param openai_config: openai_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#openai_config ModelServing#openai_config}
        :param palm_config: palm_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#palm_config ModelServing#palm_config}
        '''
        value = ModelServingConfigServedEntitiesExternalModel(
            name=name,
            provider=provider,
            task=task,
            ai21_labs_config=ai21_labs_config,
            amazon_bedrock_config=amazon_bedrock_config,
            anthropic_config=anthropic_config,
            cohere_config=cohere_config,
            databricks_model_serving_config=databricks_model_serving_config,
            openai_config=openai_config,
            palm_config=palm_config,
        )

        return typing.cast(None, jsii.invoke(self, "putExternalModel", [value]))

    @jsii.member(jsii_name="resetEntityName")
    def reset_entity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityName", []))

    @jsii.member(jsii_name="resetEntityVersion")
    def reset_entity_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityVersion", []))

    @jsii.member(jsii_name="resetEnvironmentVars")
    def reset_environment_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVars", []))

    @jsii.member(jsii_name="resetExternalModel")
    def reset_external_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalModel", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetMaxProvisionedThroughput")
    def reset_max_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxProvisionedThroughput", []))

    @jsii.member(jsii_name="resetMinProvisionedThroughput")
    def reset_min_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinProvisionedThroughput", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetScaleToZeroEnabled")
    def reset_scale_to_zero_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleToZeroEnabled", []))

    @jsii.member(jsii_name="resetWorkloadSize")
    def reset_workload_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadSize", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="externalModel")
    def external_model(
        self,
    ) -> ModelServingConfigServedEntitiesExternalModelOutputReference:
        return typing.cast(ModelServingConfigServedEntitiesExternalModelOutputReference, jsii.get(self, "externalModel"))

    @builtins.property
    @jsii.member(jsii_name="entityNameInput")
    def entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityVersionInput")
    def entity_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentVarsInput")
    def environment_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="externalModelInput")
    def external_model_input(
        self,
    ) -> typing.Optional[ModelServingConfigServedEntitiesExternalModel]:
        return typing.cast(typing.Optional[ModelServingConfigServedEntitiesExternalModel], jsii.get(self, "externalModelInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughputInput")
    def max_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughputInput")
    def min_provisioned_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minProvisionedThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabledInput")
    def scale_to_zero_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "scaleToZeroEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadSizeInput")
    def workload_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="entityName")
    def entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityName"))

    @entity_name.setter
    def entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5115ac461b91328a1e6dc01d00fc56cc73127601942a8e2bfdf61a81faef83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityName", value)

    @builtins.property
    @jsii.member(jsii_name="entityVersion")
    def entity_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityVersion"))

    @entity_version.setter
    def entity_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a95a0cf2db47ff6a22b93698ae18fd680c16bfffea288ef207e3f6d3b19b3ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityVersion", value)

    @builtins.property
    @jsii.member(jsii_name="environmentVars")
    def environment_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environmentVars"))

    @environment_vars.setter
    def environment_vars(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0ee29c76865b6a9038e2d80fdd880b5452ddf1d26a05c17b26c5a5c21de86e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environmentVars", value)

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00de5f6a64e69f35f91ab15d64763aa2dcf66850be1d320dd964dc82d83d16db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value)

    @builtins.property
    @jsii.member(jsii_name="maxProvisionedThroughput")
    def max_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxProvisionedThroughput"))

    @max_provisioned_throughput.setter
    def max_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a225a3719b5f9c5ed1f2f06d7da50f6edaa8750290b4de359c01f3e40a080563)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxProvisionedThroughput", value)

    @builtins.property
    @jsii.member(jsii_name="minProvisionedThroughput")
    def min_provisioned_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minProvisionedThroughput"))

    @min_provisioned_throughput.setter
    def min_provisioned_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f52003d4a91bc7d946132069fb47cefe31a03c327e8f02aa9ab78527fda020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minProvisionedThroughput", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433fc1fe0c4f22dff549f3df966f4772b6f051027df685b4697db5f8188cf8b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabled")
    def scale_to_zero_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "scaleToZeroEnabled"))

    @scale_to_zero_enabled.setter
    def scale_to_zero_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__599c4926eb4037b5468d52469b0e74e25a1761e72aa97bfb197e66bd64775c50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleToZeroEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="workloadSize")
    def workload_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadSize"))

    @workload_size.setter
    def workload_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e75d8d050a460878e877a289cf925e1c7f4a6801b15a82d76bab5bca968748b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadSize", value)

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78afd2dd0ca10f2743b78f75b3e0ad3d2dae0e40f1c360b06b9dc9e867dce67d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4174906e58d55e3fcba05db5a4e8a4dd65ca404b2f456b42386ab0fd1cdb28a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModels",
    jsii_struct_bases=[],
    name_mapping={
        "model_name": "modelName",
        "model_version": "modelVersion",
        "workload_size": "workloadSize",
        "environment_vars": "environmentVars",
        "instance_profile_arn": "instanceProfileArn",
        "name": "name",
        "scale_to_zero_enabled": "scaleToZeroEnabled",
        "workload_type": "workloadType",
    },
)
class ModelServingConfigServedModels:
    def __init__(
        self,
        *,
        model_name: builtins.str,
        model_version: builtins.str,
        workload_size: builtins.str,
        environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#model_name ModelServing#model_name}.
        :param model_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#model_version ModelServing#model_version}.
        :param workload_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_size ModelServing#workload_size}.
        :param environment_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.
        :param scale_to_zero_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_type ModelServing#workload_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bec3cb547e17150f62247591fe28ea70f0c54212835f4df101f3b4570944be47)
            check_type(argname="argument model_name", value=model_name, expected_type=type_hints["model_name"])
            check_type(argname="argument model_version", value=model_version, expected_type=type_hints["model_version"])
            check_type(argname="argument workload_size", value=workload_size, expected_type=type_hints["workload_size"])
            check_type(argname="argument environment_vars", value=environment_vars, expected_type=type_hints["environment_vars"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument scale_to_zero_enabled", value=scale_to_zero_enabled, expected_type=type_hints["scale_to_zero_enabled"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "model_name": model_name,
            "model_version": model_version,
            "workload_size": workload_size,
        }
        if environment_vars is not None:
            self._values["environment_vars"] = environment_vars
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if name is not None:
            self._values["name"] = name
        if scale_to_zero_enabled is not None:
            self._values["scale_to_zero_enabled"] = scale_to_zero_enabled
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def model_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#model_name ModelServing#model_name}.'''
        result = self._values.get("model_name")
        assert result is not None, "Required property 'model_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#model_version ModelServing#model_version}.'''
        result = self._values.get("model_version")
        assert result is not None, "Required property 'model_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workload_size(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_size ModelServing#workload_size}.'''
        result = self._values.get("workload_size")
        assert result is not None, "Required property 'workload_size' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#environment_vars ModelServing#environment_vars}.'''
        result = self._values.get("environment_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#instance_profile_arn ModelServing#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#name ModelServing#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_to_zero_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#scale_to_zero_enabled ModelServing#scale_to_zero_enabled}.'''
        result = self._values.get("scale_to_zero_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#workload_type ModelServing#workload_type}.'''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigServedModels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigServedModelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModelsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff05e578ae924655a4766db44c640492b6da80d47a4d397d162294686bb36e28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigServedModelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84178d8320aa70e5900bbea218aeecdfbe05a2428b168395a9aa09448d97dbbe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigServedModelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77aa0d1b2688e799e89ca07474343e53c443abeaf05a0c5156a33508d59fd95a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8f1442c8f42d7e7012d749108f7abb52f31f2b526ec10327597cf72e34b592a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bd25af1f756a83a5d27b03efa85ec9bacb1572a074c8d1cb601c2981ae8b2ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ada08f44b74200500d8225f02a86080e59672509df4a491bf0c862b7d6f82931)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingConfigServedModelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigServedModelsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5e5fee82cb78ad16f4c3ce5d5b29f795f4c7e2b4d4ccb36068062744dd45bba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEnvironmentVars")
    def reset_environment_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVars", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetScaleToZeroEnabled")
    def reset_scale_to_zero_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleToZeroEnabled", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="environmentVarsInput")
    def environment_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="modelNameInput")
    def model_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="modelVersionInput")
    def model_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabledInput")
    def scale_to_zero_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "scaleToZeroEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadSizeInput")
    def workload_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentVars")
    def environment_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environmentVars"))

    @environment_vars.setter
    def environment_vars(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c94b7c74795cba572f02b2d4bbeceffa53726338e6d644eea2330d1d67e2ab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environmentVars", value)

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__600c13055a167361ee8c1b924c85d37f4aed1c0dc1adcbde9c77bf70323c88a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value)

    @builtins.property
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelName"))

    @model_name.setter
    def model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246db0f2e3c2794ec642ff5589afcd225d22aeeef0173856cd1b8a19e3be72f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelName", value)

    @builtins.property
    @jsii.member(jsii_name="modelVersion")
    def model_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelVersion"))

    @model_version.setter
    def model_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8faa5d39a1c50c0937e9ada650301611ebdbcbb2c72a533d76d7a13350b7d4bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelVersion", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d85df55ade7de8d5146a1a1809561baadddfe8c2162f49382f9749aca4a35517)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="scaleToZeroEnabled")
    def scale_to_zero_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "scaleToZeroEnabled"))

    @scale_to_zero_enabled.setter
    def scale_to_zero_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f13f0668cd4c89869f5cdd22f46f6bd6faed171f0a66453ab8cd82788afa283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleToZeroEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="workloadSize")
    def workload_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadSize"))

    @workload_size.setter
    def workload_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__310a1ec81c55dc2863fe2f526e0675e18185afcb588ed135018894a496895da5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadSize", value)

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92590622baa0c6b330e9ed5bbf461036c23f78b0a6fa109df1fa80da7b963ee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d23a7f41385d0449902edb78963b500da63de3a8166b4db1d089812f4e547f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfig",
    jsii_struct_bases=[],
    name_mapping={"routes": "routes"},
)
class ModelServingConfigTrafficConfig:
    def __init__(
        self,
        *,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#routes ModelServing#routes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26c7c05757d593b8a0348c6024c652a7d84c6460ca0619c9d6bf44268a2e6a30)
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if routes is not None:
            self._values["routes"] = routes

    @builtins.property
    def routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]]:
        '''routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#routes ModelServing#routes}
        '''
        result = self._values.get("routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigTrafficConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigTrafficConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a27c3dbafebf718cda970a54eb8a52a6feffd4ebdb9c01c773b771ed47506e52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRoutes")
    def put_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ModelServingConfigTrafficConfigRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__753bbf141b0f2bf6e6d75290fc838f96cb1be6fbe13fa1104c5ff64d7b8af24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutes", [value]))

    @jsii.member(jsii_name="resetRoutes")
    def reset_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutes", []))

    @builtins.property
    @jsii.member(jsii_name="routes")
    def routes(self) -> "ModelServingConfigTrafficConfigRoutesList":
        return typing.cast("ModelServingConfigTrafficConfigRoutesList", jsii.get(self, "routes"))

    @builtins.property
    @jsii.member(jsii_name="routesInput")
    def routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ModelServingConfigTrafficConfigRoutes"]]], jsii.get(self, "routesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ModelServingConfigTrafficConfig]:
        return typing.cast(typing.Optional[ModelServingConfigTrafficConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ModelServingConfigTrafficConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ed3546f7b58d1656c88678d778ef88d67153c95cb8fcf3363bb2f5cdb1f9774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutes",
    jsii_struct_bases=[],
    name_mapping={
        "served_model_name": "servedModelName",
        "traffic_percentage": "trafficPercentage",
    },
)
class ModelServingConfigTrafficConfigRoutes:
    def __init__(
        self,
        *,
        served_model_name: builtins.str,
        traffic_percentage: jsii.Number,
    ) -> None:
        '''
        :param served_model_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_model_name ModelServing#served_model_name}.
        :param traffic_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#traffic_percentage ModelServing#traffic_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1034d01ae478d0ff7d53fa8e9eb3f1c39ce5e246f6938f2d2ff8db93266d84cc)
            check_type(argname="argument served_model_name", value=served_model_name, expected_type=type_hints["served_model_name"])
            check_type(argname="argument traffic_percentage", value=traffic_percentage, expected_type=type_hints["traffic_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "served_model_name": served_model_name,
            "traffic_percentage": traffic_percentage,
        }

    @builtins.property
    def served_model_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#served_model_name ModelServing#served_model_name}.'''
        result = self._values.get("served_model_name")
        assert result is not None, "Required property 'served_model_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def traffic_percentage(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#traffic_percentage ModelServing#traffic_percentage}.'''
        result = self._values.get("traffic_percentage")
        assert result is not None, "Required property 'traffic_percentage' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingConfigTrafficConfigRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingConfigTrafficConfigRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a51890fd2e83e06f326c7e4c2e56f53f42d2a7347050aeba6ca2e8851f42c13)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ModelServingConfigTrafficConfigRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d50a454e94f6ba0de77ca3ed6e4c986773aafeecf1e7bdf013d3c9f0bfb06d9d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingConfigTrafficConfigRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a171e44cdcb8fb5d35b9cf544b2f317c0b5a31052f8d7208c6cd6bc7ef45df13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d44c0aed82c54a25287ef87d8aa45152a3f4a88476b012faabf73df46cfaaf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14b0792afdfea0d401f6a4b08a68a01a419bda2856995bf92b3cb2c2ece2d4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d72e120537a643722e3ea01eaf526635108818279a9b0704008c436ca2e3c02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingConfigTrafficConfigRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingConfigTrafficConfigRoutesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ac51e4233ba30b56f41451336d2ab9323ee19d8cacf5a288fb6f25f8399ddac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="servedModelNameInput")
    def served_model_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servedModelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficPercentageInput")
    def traffic_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "trafficPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="servedModelName")
    def served_model_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servedModelName"))

    @served_model_name.setter
    def served_model_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ccf13241fbb6393fb91175bcbf263b744222f548e831da937cb15d48d8688ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servedModelName", value)

    @builtins.property
    @jsii.member(jsii_name="trafficPercentage")
    def traffic_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trafficPercentage"))

    @traffic_percentage.setter
    def traffic_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__343f7be9975e8626741942367396097be01927f29440a79139a39535ac8a8173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficPercentage", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dcb2ae9c367370cace88cc97cb46ffe88301875cc46f2d6d6448cf8b18ec7f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimits",
    jsii_struct_bases=[],
    name_mapping={"calls": "calls", "renewal_period": "renewalPeriod", "key": "key"},
)
class ModelServingRateLimits:
    def __init__(
        self,
        *,
        calls: jsii.Number,
        renewal_period: builtins.str,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param calls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#calls ModelServing#calls}.
        :param renewal_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#key ModelServing#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2bc096bf5dd0480d8136763a51159848fe345d057322b64d9f93fc1a58719b6)
            check_type(argname="argument calls", value=calls, expected_type=type_hints["calls"])
            check_type(argname="argument renewal_period", value=renewal_period, expected_type=type_hints["renewal_period"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "calls": calls,
            "renewal_period": renewal_period,
        }
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def calls(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#calls ModelServing#calls}.'''
        result = self._values.get("calls")
        assert result is not None, "Required property 'calls' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def renewal_period(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#renewal_period ModelServing#renewal_period}.'''
        result = self._values.get("renewal_period")
        assert result is not None, "Required property 'renewal_period' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingRateLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingRateLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimitsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1362c38391e0cb26581a25774e7eed3b6e178f663ead9afee1161feeb83fb48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ModelServingRateLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61851880faeff49a81473200274e4ce2e204ab143df73de97a32d952b4570a7b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingRateLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__825f37b8790e58259c73e79d1dad7a668f733d725bf9af9b1b00831b59578300)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d1401843efa3e74ab777e10b9feab0ef230eaea5db66f4fedb2078ee0e39558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e47bd8423b35ca890f53c03d8d0be70442107984d50519d49c4ab0326be04cd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aabe8bc96732726ad1c9e42d2f57d12a265956a00f17aa2891088d19b091ec53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingRateLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingRateLimitsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83414be43189d74dae6a84d3b6a5331272e36a2093d6b88c4d170f6fcc7166d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @builtins.property
    @jsii.member(jsii_name="callsInput")
    def calls_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "callsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="renewalPeriodInput")
    def renewal_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "renewalPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="calls")
    def calls(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "calls"))

    @calls.setter
    def calls(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f669cb62b2a669d360afd50e30b208fbdd8522b0016c009cdd71c84a9ae901)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "calls", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc01a76da7a8d3824df4f3913e92b255d59c5c9f8d6b2767fe20975a7a9f99f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="renewalPeriod")
    def renewal_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "renewalPeriod"))

    @renewal_period.setter
    def renewal_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14c2267ddb817069579eb9bf438ee0a312cddbdefa1eb8a7ae14c2cccb5034b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewalPeriod", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb61e9bb41688605ab3418be9af2fc66a958f2fb816325a9450810b7b3c64146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ModelServingTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#key ModelServing#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#value ModelServing#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c62ce7cce72ef70c2428d7efe9f31163de11a07e4c94766ca334f8e343dcd0d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#key ModelServing#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#value ModelServing#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTagsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c155cf36304447b4779b4f494bd3b9370f807b5926c72db693948914a4b55151)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ModelServingTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89eca721b95cf42590c1ba8cc3403371cf0d9b5a94888458923f984ec9dc970d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ModelServingTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a2c05f9fa66fff11484970211c5e9ae0662030eecbecc2f2ea501dd8f1b8f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__477ad4776aa26ecb9e618c7b0035cf66c938e01254c57404ae31523e057be727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f64cbdc16de436c2c3d7bc1adf27bb37d42a8b2c14308c97f56a9d208680bcac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e9e5bd2d0014f499fe35c264e1a053c54bdc94a4b2d47f9a4d3aa057fb27d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ModelServingTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTagsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36b3532e5dc1504e1b7674aeab27c0175023fdac78e3d7eb290f91b9a2df070a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__791ce1ebcead96a87b728e97fcd3ff06dcc4f688709921baf24258441d8e868b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac92fbf7c52eb91a7d52b396b5fc11efec5f570e498e18fa941975426be8610e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a608f26707d3f3f118ff4c5c2867c43fbbb58c1da84119abbf8089350b8728b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class ModelServingTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#create ModelServing#create}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#update ModelServing#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6740d3ce1034ef1c5164ea8e67bc93e961d0e6bee92c28b46a7d580aae113d72)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#create ModelServing#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/model_serving#update ModelServing#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelServingTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ModelServingTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.modelServing.ModelServingTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad7cdc805e234f89caecb43dd029116fcd47986f72c09c48a3ef890d34cd6e0f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d4d42baea57d3eecd43743b3e8ad0c09b839b4fd8a0a56b3e1473279f20bc4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__463e97a8ca2acb32f0e249dce79fddab40fedb89cabb04620d42884d619be2ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c1feefc886a66c011e7d75efdbea27a7dfb17cf6eea23040fa7988b6826603c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ModelServing",
    "ModelServingConfig",
    "ModelServingConfigA",
    "ModelServingConfigAOutputReference",
    "ModelServingConfigAutoCaptureConfig",
    "ModelServingConfigAutoCaptureConfigOutputReference",
    "ModelServingConfigServedEntities",
    "ModelServingConfigServedEntitiesExternalModel",
    "ModelServingConfigServedEntitiesExternalModelAi21LabsConfig",
    "ModelServingConfigServedEntitiesExternalModelAi21LabsConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig",
    "ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelAnthropicConfig",
    "ModelServingConfigServedEntitiesExternalModelAnthropicConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelCohereConfig",
    "ModelServingConfigServedEntitiesExternalModelCohereConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig",
    "ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelOpenaiConfig",
    "ModelServingConfigServedEntitiesExternalModelOpenaiConfigOutputReference",
    "ModelServingConfigServedEntitiesExternalModelOutputReference",
    "ModelServingConfigServedEntitiesExternalModelPalmConfig",
    "ModelServingConfigServedEntitiesExternalModelPalmConfigOutputReference",
    "ModelServingConfigServedEntitiesList",
    "ModelServingConfigServedEntitiesOutputReference",
    "ModelServingConfigServedModels",
    "ModelServingConfigServedModelsList",
    "ModelServingConfigServedModelsOutputReference",
    "ModelServingConfigTrafficConfig",
    "ModelServingConfigTrafficConfigOutputReference",
    "ModelServingConfigTrafficConfigRoutes",
    "ModelServingConfigTrafficConfigRoutesList",
    "ModelServingConfigTrafficConfigRoutesOutputReference",
    "ModelServingRateLimits",
    "ModelServingRateLimitsList",
    "ModelServingRateLimitsOutputReference",
    "ModelServingTags",
    "ModelServingTagsList",
    "ModelServingTagsOutputReference",
    "ModelServingTimeouts",
    "ModelServingTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__fcdceab54e050923170b39eff538055f8b76b660bb8732c203c9c67261d31d37(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    config: typing.Union[ModelServingConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__ee1bb539ded3a1716a5800f3c306bd3bf91c26ca2eb1bd182e8248cdbaff5430(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a275a6bfdceace553e2be007a16e27fa4711760199dc7e1aa3df554d09920e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a326d60c6d2388605269123ef001af7186ca3f81f93ddf683edaaa2863033b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754d4971dd64df250d28b3640fa44fa399b715301fc0dd43ff8d8304e9ef8d25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb43c6ec513eda5c793054e174b6c273a821c9b323b20667ced44837696142c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d34de5d9b9fed3c9898fd854fd3464a901fd46e11ea543b532dd7d7a7df273a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ab99c61d3a667a89d9f5f2278213a6b075df770286584a1c864bfffbe20082(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: typing.Union[ModelServingConfigA, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    rate_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingRateLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    route_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[ModelServingTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f209635c93e31eb79747b450ef07f331215993fe3c611af60329c1181395d96(
    *,
    auto_capture_config: typing.Optional[typing.Union[ModelServingConfigAutoCaptureConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    served_entities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    served_models: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedModels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    traffic_config: typing.Optional[typing.Union[ModelServingConfigTrafficConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39de19fd4e2e3b391a36cec3ae6b58c26f839e9b7717318f9c83712d464b8240(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9147fd79fb2787c00f1d1d5fcb304fbacd554791d29739786eb47f169656f6f9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedEntities, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ca446d7fd23d5b8a13db8091cb8d50a52da9d34dc0d71f3453cc4df48cef58(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigServedModels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9ca6d2b3625d2fe9064559e5ae3834b4a7d876e85a62ac1aedf940272c521b(
    value: typing.Optional[ModelServingConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf8b2cb451924e6518496f1ef57ccd7f223277cadafa3d24b53b01883eebebe(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schema_name: typing.Optional[builtins.str] = None,
    table_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67b5a32de74ec757f3fd7506a723ede01a5cbb72fe8a9e8f7f55a463e336efb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d853ac5156bce5e1133f54bfb86fe697d8ede486fe731bfa34903faa9f25753c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88136c1faf06edab8a7bc50c6c0024a15189007716a85bd8e4bdf7614acadd6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7efdad892ab787aa5957098c51102ad9ba0b8cbd0427823bc099599637c9475(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8067336e1bc5f02cec3e8f5ba3e25eee6475ed8fb875a21dee0d49ed8a33c796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db8d7706dcbc2a14ef38e7145ac608ca0bbc7781baea610fd87821dbd601e6f3(
    value: typing.Optional[ModelServingConfigAutoCaptureConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9403ea38a33e4adf7cbe8b181e16d03e70709409f2f5b3cd020360a19e5995d8(
    *,
    entity_name: typing.Optional[builtins.str] = None,
    entity_version: typing.Optional[builtins.str] = None,
    environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    external_model: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModel, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    max_provisioned_throughput: typing.Optional[jsii.Number] = None,
    min_provisioned_throughput: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_size: typing.Optional[builtins.str] = None,
    workload_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b566f9c1a169a08e2dd41b8ad9ddbe16d86060bfdb3621f6f0b19ed393bf4b(
    *,
    name: builtins.str,
    provider: builtins.str,
    task: builtins.str,
    ai21_labs_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    amazon_bedrock_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    anthropic_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelAnthropicConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cohere_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelCohereConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    databricks_model_serving_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    openai_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelOpenaiConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    palm_config: typing.Optional[typing.Union[ModelServingConfigServedEntitiesExternalModelPalmConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c0ee9dc2d1327236ae97d5c3fe5c5338c3794a40d2d88c02560c83925676710(
    *,
    ai21_labs_api_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec48b6283533d5b4c9aeb09b046668b46db9832fe3be06b87645bbc1fe6b77af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd2ee0da33d9d6eea9698dda6843afedb835973ae8037fa09e4c0271c49a7d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b145ea06e1bd8516ff0cc11cbf9fd2f0e536da81a5b9c4cbc7ff9c0165bb85a2(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAi21LabsConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90dd82469e7808adf0a9158c33b32ac196f631841b5b828af93d7f461ae108ca(
    *,
    aws_access_key_id: builtins.str,
    aws_region: builtins.str,
    aws_secret_access_key: builtins.str,
    bedrock_provider: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f80d852ac84bb277b80e781606f1e4dd2b8f0b03f4b4f4ce3d3d3f4f752061e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a72a91085af2cd622a5c4761f65046e6b7f2a78c1bd2cb36a4dcac5671bdb1f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d32624b5e375ebc73dc077d306d42c18f51d38659a7f1881d39b43af1a5693cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8628231e26f171719205ff1342000dc222ab9ce51be0e6d9ad62573609694543(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c269a46ec95800bb1f6e9e676994c75ad9c42fc985f8a721b147636f09ea1add(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee68940f0acb9b42fcf03a36fc4c76724008a5a5bd4d0a07014abf027865cf5(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAmazonBedrockConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__218f5a41e3d93d07362768598313f8b6139fdb7702b337199d420fb89c368361(
    *,
    anthropic_api_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5800a1e5ff7cbebc7e2b6b8a7272a5844a5b75fcb4202bafab87d419f8cb2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b023fe17c98d566c8fac5e33cf5eab2d6ab8b5f2aac678aab6bc169b3745228(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64d693f11d3435c35e4ed3c8d0458aadee5227005cf5947d024560f5846c673(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelAnthropicConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dcb9995c75742d273441f3c12353f2a8a2afcd41c6de6865efd4504723a0455(
    *,
    cohere_api_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49817b6641b2bf6dfba75fda89240974cad2adba5d155e98e85da7ac13731ecb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b46b4f09d11ea820e7e30599eccb4dc33c186404ec5c41a642550f3c870525(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a60f8a840727e7cd3ce21617d1ae19459196adef749e8e5126eb54fd90b745a(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelCohereConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc7d014e30705b1d364c1fdbb4051d5a7521e5c6874f14751d9b24ade962ccae(
    *,
    databricks_api_token: builtins.str,
    databricks_workspace_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cda49ad248f1b0eb4e12f1d86fc09682a280a677deaf69662836e58db84f468(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a09b862ceaf8807cca67fb6c462f92e28e9578762c5c262d8bfba2228fd0f6d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764fd45b87e6fd1d6cc9ef7428ca7893495c45311e54982f5cf24b55fe956143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a2eeb97c7e347fa469adfa492f6e516d30265f9a57baa620b6237d20f748bc(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelDatabricksModelServingConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8f3651cd444a6a03a04e10e5b69221f40bf7182b94e27a3f39209873e1a2293(
    *,
    microsoft_entra_client_id: typing.Optional[builtins.str] = None,
    microsoft_entra_client_secret: typing.Optional[builtins.str] = None,
    microsoft_entra_tenant_id: typing.Optional[builtins.str] = None,
    openai_api_base: typing.Optional[builtins.str] = None,
    openai_api_key: typing.Optional[builtins.str] = None,
    openai_api_type: typing.Optional[builtins.str] = None,
    openai_api_version: typing.Optional[builtins.str] = None,
    openai_deployment_name: typing.Optional[builtins.str] = None,
    openai_organization: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96eca2227ca1f6fbe25592666bfb974076efa4c4f49bad0f227b4a2e3eb17f28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b01bce6ae02663c936859b6fdd65bf9c0787e0a2cbca469a27e0254691e4f99e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8acf6fc23afd1ec6f16b8d814ba0c5fd3202eb75dc88075e6fa2e70bf74e1a24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810652b88b687685a4925c644374a2c91f370a298407a4299026d674b5c21875(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d910ae46138165d13f96fcad38ba4d03ea99b4f6398de8d21648bf91c47f812(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2942665469b2d114c5b1da0a35801aba473b6fd397a92822aba7a01d3bdb6a1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa62ef264416b3877aac41273f2288de305f9b5513e98b5feda0976afb36e2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c39917ad5aa16b52b380336edcb2f53961c8750fdc6125952517ccc54b6a951(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__139733bf0f71f12b8e4408aa3bb941024091eb852488a633b731789178eda8c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6bd90ea04878cc2aeedd21c4ab7495629f3d00b634d97096aff7e311c7d9b72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0833c7b0577230e49679060b337fdaee600a3cc50d57218dab1a5fcc76ee558f(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelOpenaiConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286957a797d7d3795901e718c685222247720c7959b31372363ced1053c8349c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__186cb5665bc59aaa9ce409cb8208fb7dd40871e7acf79134bf4c7cdc5c10a2c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12796f48f59357a3d01909964205037a61611468763c992eaf3a5e51a410b9d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55764731d175dec17e4fc1dd16886f842c2d8074da5de0878b95679f89c7a6d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23c418f265754be146809c589f248006a2e823e8931bce27139b60be00a944fb(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModel],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d7f69696e468cd3ad5ffddae6add89fbf9597eef2db2a900972795882f84260(
    *,
    palm_api_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2415e41a2d65031da7ad03ff288304364d2a75d69e744f5986dbebe1cd84314(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d267a559f3a647aa1bad3826b5c511002c6e84c231d14e688498f3452c1edc93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c92e50429bcc356c4a64039fd323e25eec3aac1617b8e44b20de759640c3439(
    value: typing.Optional[ModelServingConfigServedEntitiesExternalModelPalmConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b118db3d06fdd140973d3aa4cc3a885623a42ff336d2eba7d45380b7f73959(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77acb6ce6c67f79a9b0d1314c0324692cb1fa6f244647ce53272762d81da2526(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a14f5528daebd60ea2786187c3c5a4423f153db7ab0e49a07d1ebac0cae40d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b2a27fd791322888d58ee916ba218a9018446d6ac345466008049d6bd107087(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9cad630026f7541c897b5d7427a66841f3a7b37ea702e67476de9e4e66337f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db21c169a62214a095fb313b873f0316c06668343c8a393d69f0adf180eee16d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedEntities]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bce219b1818dd301c72b49d3cd1ee61649975cbfc261e27ce547ecf3c22dd279(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae5115ac461b91328a1e6dc01d00fc56cc73127601942a8e2bfdf61a81faef83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a95a0cf2db47ff6a22b93698ae18fd680c16bfffea288ef207e3f6d3b19b3ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0ee29c76865b6a9038e2d80fdd880b5452ddf1d26a05c17b26c5a5c21de86e(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00de5f6a64e69f35f91ab15d64763aa2dcf66850be1d320dd964dc82d83d16db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a225a3719b5f9c5ed1f2f06d7da50f6edaa8750290b4de359c01f3e40a080563(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f52003d4a91bc7d946132069fb47cefe31a03c327e8f02aa9ab78527fda020(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433fc1fe0c4f22dff549f3df966f4772b6f051027df685b4697db5f8188cf8b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599c4926eb4037b5468d52469b0e74e25a1761e72aa97bfb197e66bd64775c50(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e75d8d050a460878e877a289cf925e1c7f4a6801b15a82d76bab5bca968748b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78afd2dd0ca10f2743b78f75b3e0ad3d2dae0e40f1c360b06b9dc9e867dce67d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4174906e58d55e3fcba05db5a4e8a4dd65ca404b2f456b42386ab0fd1cdb28a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedEntities]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bec3cb547e17150f62247591fe28ea70f0c54212835f4df101f3b4570944be47(
    *,
    model_name: builtins.str,
    model_version: builtins.str,
    workload_size: builtins.str,
    environment_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    scale_to_zero_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff05e578ae924655a4766db44c640492b6da80d47a4d397d162294686bb36e28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84178d8320aa70e5900bbea218aeecdfbe05a2428b168395a9aa09448d97dbbe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77aa0d1b2688e799e89ca07474343e53c443abeaf05a0c5156a33508d59fd95a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f1442c8f42d7e7012d749108f7abb52f31f2b526ec10327597cf72e34b592a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bd25af1f756a83a5d27b03efa85ec9bacb1572a074c8d1cb601c2981ae8b2ff(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ada08f44b74200500d8225f02a86080e59672509df4a491bf0c862b7d6f82931(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigServedModels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5e5fee82cb78ad16f4c3ce5d5b29f795f4c7e2b4d4ccb36068062744dd45bba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c94b7c74795cba572f02b2d4bbeceffa53726338e6d644eea2330d1d67e2ab4(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__600c13055a167361ee8c1b924c85d37f4aed1c0dc1adcbde9c77bf70323c88a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246db0f2e3c2794ec642ff5589afcd225d22aeeef0173856cd1b8a19e3be72f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8faa5d39a1c50c0937e9ada650301611ebdbcbb2c72a533d76d7a13350b7d4bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d85df55ade7de8d5146a1a1809561baadddfe8c2162f49382f9749aca4a35517(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f13f0668cd4c89869f5cdd22f46f6bd6faed171f0a66453ab8cd82788afa283(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__310a1ec81c55dc2863fe2f526e0675e18185afcb588ed135018894a496895da5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92590622baa0c6b330e9ed5bbf461036c23f78b0a6fa109df1fa80da7b963ee6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d23a7f41385d0449902edb78963b500da63de3a8166b4db1d089812f4e547f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigServedModels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c7c05757d593b8a0348c6024c652a7d84c6460ca0619c9d6bf44268a2e6a30(
    *,
    routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a27c3dbafebf718cda970a54eb8a52a6feffd4ebdb9c01c773b771ed47506e52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__753bbf141b0f2bf6e6d75290fc838f96cb1be6fbe13fa1104c5ff64d7b8af24c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ModelServingConfigTrafficConfigRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ed3546f7b58d1656c88678d778ef88d67153c95cb8fcf3363bb2f5cdb1f9774(
    value: typing.Optional[ModelServingConfigTrafficConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1034d01ae478d0ff7d53fa8e9eb3f1c39ce5e246f6938f2d2ff8db93266d84cc(
    *,
    served_model_name: builtins.str,
    traffic_percentage: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a51890fd2e83e06f326c7e4c2e56f53f42d2a7347050aeba6ca2e8851f42c13(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50a454e94f6ba0de77ca3ed6e4c986773aafeecf1e7bdf013d3c9f0bfb06d9d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a171e44cdcb8fb5d35b9cf544b2f317c0b5a31052f8d7208c6cd6bc7ef45df13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d44c0aed82c54a25287ef87d8aa45152a3f4a88476b012faabf73df46cfaaf4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14b0792afdfea0d401f6a4b08a68a01a419bda2856995bf92b3cb2c2ece2d4de(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d72e120537a643722e3ea01eaf526635108818279a9b0704008c436ca2e3c02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingConfigTrafficConfigRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ac51e4233ba30b56f41451336d2ab9323ee19d8cacf5a288fb6f25f8399ddac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ccf13241fbb6393fb91175bcbf263b744222f548e831da937cb15d48d8688ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__343f7be9975e8626741942367396097be01927f29440a79139a39535ac8a8173(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dcb2ae9c367370cace88cc97cb46ffe88301875cc46f2d6d6448cf8b18ec7f8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingConfigTrafficConfigRoutes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2bc096bf5dd0480d8136763a51159848fe345d057322b64d9f93fc1a58719b6(
    *,
    calls: jsii.Number,
    renewal_period: builtins.str,
    key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1362c38391e0cb26581a25774e7eed3b6e178f663ead9afee1161feeb83fb48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61851880faeff49a81473200274e4ce2e204ab143df73de97a32d952b4570a7b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__825f37b8790e58259c73e79d1dad7a668f733d725bf9af9b1b00831b59578300(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d1401843efa3e74ab777e10b9feab0ef230eaea5db66f4fedb2078ee0e39558(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e47bd8423b35ca890f53c03d8d0be70442107984d50519d49c4ab0326be04cd8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aabe8bc96732726ad1c9e42d2f57d12a265956a00f17aa2891088d19b091ec53(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingRateLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83414be43189d74dae6a84d3b6a5331272e36a2093d6b88c4d170f6fcc7166d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f669cb62b2a669d360afd50e30b208fbdd8522b0016c009cdd71c84a9ae901(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc01a76da7a8d3824df4f3913e92b255d59c5c9f8d6b2767fe20975a7a9f99f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14c2267ddb817069579eb9bf438ee0a312cddbdefa1eb8a7ae14c2cccb5034b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb61e9bb41688605ab3418be9af2fc66a958f2fb816325a9450810b7b3c64146(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingRateLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c62ce7cce72ef70c2428d7efe9f31163de11a07e4c94766ca334f8e343dcd0d(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c155cf36304447b4779b4f494bd3b9370f807b5926c72db693948914a4b55151(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89eca721b95cf42590c1ba8cc3403371cf0d9b5a94888458923f984ec9dc970d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a2c05f9fa66fff11484970211c5e9ae0662030eecbecc2f2ea501dd8f1b8f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__477ad4776aa26ecb9e618c7b0035cf66c938e01254c57404ae31523e057be727(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64cbdc16de436c2c3d7bc1adf27bb37d42a8b2c14308c97f56a9d208680bcac(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e9e5bd2d0014f499fe35c264e1a053c54bdc94a4b2d47f9a4d3aa057fb27d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ModelServingTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b3532e5dc1504e1b7674aeab27c0175023fdac78e3d7eb290f91b9a2df070a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__791ce1ebcead96a87b728e97fcd3ff06dcc4f688709921baf24258441d8e868b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac92fbf7c52eb91a7d52b396b5fc11efec5f570e498e18fa941975426be8610e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a608f26707d3f3f118ff4c5c2867c43fbbb58c1da84119abbf8089350b8728b6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6740d3ce1034ef1c5164ea8e67bc93e961d0e6bee92c28b46a7d580aae113d72(
    *,
    create: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7cdc805e234f89caecb43dd029116fcd47986f72c09c48a3ef890d34cd6e0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d4d42baea57d3eecd43743b3e8ad0c09b839b4fd8a0a56b3e1473279f20bc4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__463e97a8ca2acb32f0e249dce79fddab40fedb89cabb04620d42884d619be2ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1feefc886a66c011e7d75efdbea27a7dfb17cf6eea23040fa7988b6826603c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ModelServingTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
