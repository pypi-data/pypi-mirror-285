r'''
# `databricks_quality_monitor`

Refer to the Terraform Registry for docs: [`databricks_quality_monitor`](https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor).
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


class QualityMonitor(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitor",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor databricks_quality_monitor}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        assets_dir: builtins.str,
        output_schema_name: builtins.str,
        table_name: builtins.str,
        baseline_table_name: typing.Optional[builtins.str] = None,
        custom_metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QualityMonitorCustomMetrics", typing.Dict[builtins.str, typing.Any]]]]] = None,
        data_classification_config: typing.Optional[typing.Union["QualityMonitorDataClassificationConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        inference_log: typing.Optional[typing.Union["QualityMonitorInferenceLog", typing.Dict[builtins.str, typing.Any]]] = None,
        latest_monitor_failure_msg: typing.Optional[builtins.str] = None,
        notifications: typing.Optional[typing.Union["QualityMonitorNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["QualityMonitorSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        skip_builtin_dashboard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        slicing_exprs: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot: typing.Optional[typing.Union["QualityMonitorSnapshot", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["QualityMonitorTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        time_series: typing.Optional[typing.Union["QualityMonitorTimeSeries", typing.Dict[builtins.str, typing.Any]]] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor databricks_quality_monitor} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param assets_dir: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#assets_dir QualityMonitor#assets_dir}.
        :param output_schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#output_schema_name QualityMonitor#output_schema_name}.
        :param table_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#table_name QualityMonitor#table_name}.
        :param baseline_table_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#baseline_table_name QualityMonitor#baseline_table_name}.
        :param custom_metrics: custom_metrics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#custom_metrics QualityMonitor#custom_metrics}
        :param data_classification_config: data_classification_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#data_classification_config QualityMonitor#data_classification_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#id QualityMonitor#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param inference_log: inference_log block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#inference_log QualityMonitor#inference_log}
        :param latest_monitor_failure_msg: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#latest_monitor_failure_msg QualityMonitor#latest_monitor_failure_msg}.
        :param notifications: notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#notifications QualityMonitor#notifications}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#schedule QualityMonitor#schedule}
        :param skip_builtin_dashboard: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#skip_builtin_dashboard QualityMonitor#skip_builtin_dashboard}.
        :param slicing_exprs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#slicing_exprs QualityMonitor#slicing_exprs}.
        :param snapshot: snapshot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#snapshot QualityMonitor#snapshot}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timeouts QualityMonitor#timeouts}
        :param time_series: time_series block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#time_series QualityMonitor#time_series}
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#warehouse_id QualityMonitor#warehouse_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d63c34fadb49dde6d220b1647e4f061bca431d5d6a85ebe21aba05f7c865f650)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = QualityMonitorConfig(
            assets_dir=assets_dir,
            output_schema_name=output_schema_name,
            table_name=table_name,
            baseline_table_name=baseline_table_name,
            custom_metrics=custom_metrics,
            data_classification_config=data_classification_config,
            id=id,
            inference_log=inference_log,
            latest_monitor_failure_msg=latest_monitor_failure_msg,
            notifications=notifications,
            schedule=schedule,
            skip_builtin_dashboard=skip_builtin_dashboard,
            slicing_exprs=slicing_exprs,
            snapshot=snapshot,
            timeouts=timeouts,
            time_series=time_series,
            warehouse_id=warehouse_id,
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
        '''Generates CDKTF code for importing a QualityMonitor resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the QualityMonitor to import.
        :param import_from_id: The id of the existing QualityMonitor that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the QualityMonitor to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a37ef75111651cc186a8f53d70a65dd9446b1fc68d3688c3f6cf3ec2a7a08307)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCustomMetrics")
    def put_custom_metrics(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QualityMonitorCustomMetrics", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9667b89954cf426f5bf734ae0508eeecacf668f64408135cb321bfdd1c5b9524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomMetrics", [value]))

    @jsii.member(jsii_name="putDataClassificationConfig")
    def put_data_classification_config(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#enabled QualityMonitor#enabled}.
        '''
        value = QualityMonitorDataClassificationConfig(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putDataClassificationConfig", [value]))

    @jsii.member(jsii_name="putInferenceLog")
    def put_inference_log(
        self,
        *,
        granularities: typing.Sequence[builtins.str],
        model_id_col: builtins.str,
        prediction_col: builtins.str,
        problem_type: builtins.str,
        timestamp_col: builtins.str,
        label_col: typing.Optional[builtins.str] = None,
        prediction_proba_col: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param granularities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.
        :param model_id_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#model_id_col QualityMonitor#model_id_col}.
        :param prediction_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_col QualityMonitor#prediction_col}.
        :param problem_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#problem_type QualityMonitor#problem_type}.
        :param timestamp_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.
        :param label_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#label_col QualityMonitor#label_col}.
        :param prediction_proba_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_proba_col QualityMonitor#prediction_proba_col}.
        '''
        value = QualityMonitorInferenceLog(
            granularities=granularities,
            model_id_col=model_id_col,
            prediction_col=prediction_col,
            problem_type=problem_type,
            timestamp_col=timestamp_col,
            label_col=label_col,
            prediction_proba_col=prediction_proba_col,
        )

        return typing.cast(None, jsii.invoke(self, "putInferenceLog", [value]))

    @jsii.member(jsii_name="putNotifications")
    def put_notifications(
        self,
        *,
        on_failure: typing.Optional[typing.Union["QualityMonitorNotificationsOnFailure", typing.Dict[builtins.str, typing.Any]]] = None,
        on_new_classification_tag_detected: typing.Optional[typing.Union["QualityMonitorNotificationsOnNewClassificationTagDetected", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_failure QualityMonitor#on_failure}
        :param on_new_classification_tag_detected: on_new_classification_tag_detected block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_new_classification_tag_detected QualityMonitor#on_new_classification_tag_detected}
        '''
        value = QualityMonitorNotifications(
            on_failure=on_failure,
            on_new_classification_tag_detected=on_new_classification_tag_detected,
        )

        return typing.cast(None, jsii.invoke(self, "putNotifications", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        quartz_cron_expression: builtins.str,
        timezone_id: builtins.str,
        pause_status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quartz_cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#quartz_cron_expression QualityMonitor#quartz_cron_expression}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timezone_id QualityMonitor#timezone_id}.
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#pause_status QualityMonitor#pause_status}.
        '''
        value = QualityMonitorSchedule(
            quartz_cron_expression=quartz_cron_expression,
            timezone_id=timezone_id,
            pause_status=pause_status,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="putSnapshot")
    def put_snapshot(self) -> None:
        value = QualityMonitorSnapshot()

        return typing.cast(None, jsii.invoke(self, "putSnapshot", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#create QualityMonitor#create}.
        '''
        value = QualityMonitorTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTimeSeries")
    def put_time_series(
        self,
        *,
        granularities: typing.Sequence[builtins.str],
        timestamp_col: builtins.str,
    ) -> None:
        '''
        :param granularities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.
        :param timestamp_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.
        '''
        value = QualityMonitorTimeSeries(
            granularities=granularities, timestamp_col=timestamp_col
        )

        return typing.cast(None, jsii.invoke(self, "putTimeSeries", [value]))

    @jsii.member(jsii_name="resetBaselineTableName")
    def reset_baseline_table_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaselineTableName", []))

    @jsii.member(jsii_name="resetCustomMetrics")
    def reset_custom_metrics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMetrics", []))

    @jsii.member(jsii_name="resetDataClassificationConfig")
    def reset_data_classification_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataClassificationConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInferenceLog")
    def reset_inference_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceLog", []))

    @jsii.member(jsii_name="resetLatestMonitorFailureMsg")
    def reset_latest_monitor_failure_msg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatestMonitorFailureMsg", []))

    @jsii.member(jsii_name="resetNotifications")
    def reset_notifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifications", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetSkipBuiltinDashboard")
    def reset_skip_builtin_dashboard(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipBuiltinDashboard", []))

    @jsii.member(jsii_name="resetSlicingExprs")
    def reset_slicing_exprs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlicingExprs", []))

    @jsii.member(jsii_name="resetSnapshot")
    def reset_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshot", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTimeSeries")
    def reset_time_series(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeSeries", []))

    @jsii.member(jsii_name="resetWarehouseId")
    def reset_warehouse_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarehouseId", []))

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
    @jsii.member(jsii_name="customMetrics")
    def custom_metrics(self) -> "QualityMonitorCustomMetricsList":
        return typing.cast("QualityMonitorCustomMetricsList", jsii.get(self, "customMetrics"))

    @builtins.property
    @jsii.member(jsii_name="dashboardId")
    def dashboard_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardId"))

    @builtins.property
    @jsii.member(jsii_name="dataClassificationConfig")
    def data_classification_config(
        self,
    ) -> "QualityMonitorDataClassificationConfigOutputReference":
        return typing.cast("QualityMonitorDataClassificationConfigOutputReference", jsii.get(self, "dataClassificationConfig"))

    @builtins.property
    @jsii.member(jsii_name="driftMetricsTableName")
    def drift_metrics_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driftMetricsTableName"))

    @builtins.property
    @jsii.member(jsii_name="inferenceLog")
    def inference_log(self) -> "QualityMonitorInferenceLogOutputReference":
        return typing.cast("QualityMonitorInferenceLogOutputReference", jsii.get(self, "inferenceLog"))

    @builtins.property
    @jsii.member(jsii_name="monitorVersion")
    def monitor_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitorVersion"))

    @builtins.property
    @jsii.member(jsii_name="notifications")
    def notifications(self) -> "QualityMonitorNotificationsOutputReference":
        return typing.cast("QualityMonitorNotificationsOutputReference", jsii.get(self, "notifications"))

    @builtins.property
    @jsii.member(jsii_name="profileMetricsTableName")
    def profile_metrics_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileMetricsTableName"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "QualityMonitorScheduleOutputReference":
        return typing.cast("QualityMonitorScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="snapshot")
    def snapshot(self) -> "QualityMonitorSnapshotOutputReference":
        return typing.cast("QualityMonitorSnapshotOutputReference", jsii.get(self, "snapshot"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "QualityMonitorTimeoutsOutputReference":
        return typing.cast("QualityMonitorTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="timeSeries")
    def time_series(self) -> "QualityMonitorTimeSeriesOutputReference":
        return typing.cast("QualityMonitorTimeSeriesOutputReference", jsii.get(self, "timeSeries"))

    @builtins.property
    @jsii.member(jsii_name="assetsDirInput")
    def assets_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "assetsDirInput"))

    @builtins.property
    @jsii.member(jsii_name="baselineTableNameInput")
    def baseline_table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baselineTableNameInput"))

    @builtins.property
    @jsii.member(jsii_name="customMetricsInput")
    def custom_metrics_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QualityMonitorCustomMetrics"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QualityMonitorCustomMetrics"]]], jsii.get(self, "customMetricsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataClassificationConfigInput")
    def data_classification_config_input(
        self,
    ) -> typing.Optional["QualityMonitorDataClassificationConfig"]:
        return typing.cast(typing.Optional["QualityMonitorDataClassificationConfig"], jsii.get(self, "dataClassificationConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceLogInput")
    def inference_log_input(self) -> typing.Optional["QualityMonitorInferenceLog"]:
        return typing.cast(typing.Optional["QualityMonitorInferenceLog"], jsii.get(self, "inferenceLogInput"))

    @builtins.property
    @jsii.member(jsii_name="latestMonitorFailureMsgInput")
    def latest_monitor_failure_msg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latestMonitorFailureMsgInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationsInput")
    def notifications_input(self) -> typing.Optional["QualityMonitorNotifications"]:
        return typing.cast(typing.Optional["QualityMonitorNotifications"], jsii.get(self, "notificationsInput"))

    @builtins.property
    @jsii.member(jsii_name="outputSchemaNameInput")
    def output_schema_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputSchemaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["QualityMonitorSchedule"]:
        return typing.cast(typing.Optional["QualityMonitorSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="skipBuiltinDashboardInput")
    def skip_builtin_dashboard_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipBuiltinDashboardInput"))

    @builtins.property
    @jsii.member(jsii_name="slicingExprsInput")
    def slicing_exprs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "slicingExprsInput"))

    @builtins.property
    @jsii.member(jsii_name="snapshotInput")
    def snapshot_input(self) -> typing.Optional["QualityMonitorSnapshot"]:
        return typing.cast(typing.Optional["QualityMonitorSnapshot"], jsii.get(self, "snapshotInput"))

    @builtins.property
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "QualityMonitorTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "QualityMonitorTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeSeriesInput")
    def time_series_input(self) -> typing.Optional["QualityMonitorTimeSeries"]:
        return typing.cast(typing.Optional["QualityMonitorTimeSeries"], jsii.get(self, "timeSeriesInput"))

    @builtins.property
    @jsii.member(jsii_name="warehouseIdInput")
    def warehouse_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="assetsDir")
    def assets_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assetsDir"))

    @assets_dir.setter
    def assets_dir(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46cd0a53e344d796baea7bdcc6e37a8d789e3215bfbc511f9a790c504d5f17d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assetsDir", value)

    @builtins.property
    @jsii.member(jsii_name="baselineTableName")
    def baseline_table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baselineTableName"))

    @baseline_table_name.setter
    def baseline_table_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98b266f2dcb997a2ec008fab26230e816359add51154c601557e3f43e1a60333)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baselineTableName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95cc1e00eb3d154cef21a6d6c8a6ed065e45d62b29b35bce790f9f942f03afa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="latestMonitorFailureMsg")
    def latest_monitor_failure_msg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latestMonitorFailureMsg"))

    @latest_monitor_failure_msg.setter
    def latest_monitor_failure_msg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c605536426f82f4cb9b57c5d7b86d19c6cf09f52c33ad0efd7f469afe57e235)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latestMonitorFailureMsg", value)

    @builtins.property
    @jsii.member(jsii_name="outputSchemaName")
    def output_schema_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSchemaName"))

    @output_schema_name.setter
    def output_schema_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a68d01f79759c25e1932b4818627fb81eb52e937a01be71f7cf26eb63708737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputSchemaName", value)

    @builtins.property
    @jsii.member(jsii_name="skipBuiltinDashboard")
    def skip_builtin_dashboard(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "skipBuiltinDashboard"))

    @skip_builtin_dashboard.setter
    def skip_builtin_dashboard(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcfde5a49cb1961fbebcfb1c0614078b3eb4a57877f36e89b151ee811e264fe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipBuiltinDashboard", value)

    @builtins.property
    @jsii.member(jsii_name="slicingExprs")
    def slicing_exprs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "slicingExprs"))

    @slicing_exprs.setter
    def slicing_exprs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dba847556337aea6489a144d51697bb0ba5120777ddc6038eed6192b490db9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slicingExprs", value)

    @builtins.property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__092be18310f0903e365f5498fbc1fc812c4c359f1891aa6fcb13c0beaa9f1a8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tableName", value)

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e5c1a62bf693cc1592c67d18278dcca567246414bbc56597a1d7af2a1a26c40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "assets_dir": "assetsDir",
        "output_schema_name": "outputSchemaName",
        "table_name": "tableName",
        "baseline_table_name": "baselineTableName",
        "custom_metrics": "customMetrics",
        "data_classification_config": "dataClassificationConfig",
        "id": "id",
        "inference_log": "inferenceLog",
        "latest_monitor_failure_msg": "latestMonitorFailureMsg",
        "notifications": "notifications",
        "schedule": "schedule",
        "skip_builtin_dashboard": "skipBuiltinDashboard",
        "slicing_exprs": "slicingExprs",
        "snapshot": "snapshot",
        "timeouts": "timeouts",
        "time_series": "timeSeries",
        "warehouse_id": "warehouseId",
    },
)
class QualityMonitorConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        assets_dir: builtins.str,
        output_schema_name: builtins.str,
        table_name: builtins.str,
        baseline_table_name: typing.Optional[builtins.str] = None,
        custom_metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["QualityMonitorCustomMetrics", typing.Dict[builtins.str, typing.Any]]]]] = None,
        data_classification_config: typing.Optional[typing.Union["QualityMonitorDataClassificationConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        inference_log: typing.Optional[typing.Union["QualityMonitorInferenceLog", typing.Dict[builtins.str, typing.Any]]] = None,
        latest_monitor_failure_msg: typing.Optional[builtins.str] = None,
        notifications: typing.Optional[typing.Union["QualityMonitorNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["QualityMonitorSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        skip_builtin_dashboard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        slicing_exprs: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot: typing.Optional[typing.Union["QualityMonitorSnapshot", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["QualityMonitorTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        time_series: typing.Optional[typing.Union["QualityMonitorTimeSeries", typing.Dict[builtins.str, typing.Any]]] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param assets_dir: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#assets_dir QualityMonitor#assets_dir}.
        :param output_schema_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#output_schema_name QualityMonitor#output_schema_name}.
        :param table_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#table_name QualityMonitor#table_name}.
        :param baseline_table_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#baseline_table_name QualityMonitor#baseline_table_name}.
        :param custom_metrics: custom_metrics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#custom_metrics QualityMonitor#custom_metrics}
        :param data_classification_config: data_classification_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#data_classification_config QualityMonitor#data_classification_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#id QualityMonitor#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param inference_log: inference_log block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#inference_log QualityMonitor#inference_log}
        :param latest_monitor_failure_msg: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#latest_monitor_failure_msg QualityMonitor#latest_monitor_failure_msg}.
        :param notifications: notifications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#notifications QualityMonitor#notifications}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#schedule QualityMonitor#schedule}
        :param skip_builtin_dashboard: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#skip_builtin_dashboard QualityMonitor#skip_builtin_dashboard}.
        :param slicing_exprs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#slicing_exprs QualityMonitor#slicing_exprs}.
        :param snapshot: snapshot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#snapshot QualityMonitor#snapshot}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timeouts QualityMonitor#timeouts}
        :param time_series: time_series block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#time_series QualityMonitor#time_series}
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#warehouse_id QualityMonitor#warehouse_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(data_classification_config, dict):
            data_classification_config = QualityMonitorDataClassificationConfig(**data_classification_config)
        if isinstance(inference_log, dict):
            inference_log = QualityMonitorInferenceLog(**inference_log)
        if isinstance(notifications, dict):
            notifications = QualityMonitorNotifications(**notifications)
        if isinstance(schedule, dict):
            schedule = QualityMonitorSchedule(**schedule)
        if isinstance(snapshot, dict):
            snapshot = QualityMonitorSnapshot(**snapshot)
        if isinstance(timeouts, dict):
            timeouts = QualityMonitorTimeouts(**timeouts)
        if isinstance(time_series, dict):
            time_series = QualityMonitorTimeSeries(**time_series)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05678435f7570b290f763c3b5c86389a072ff9447799e981e821cfedf6cb4015)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument assets_dir", value=assets_dir, expected_type=type_hints["assets_dir"])
            check_type(argname="argument output_schema_name", value=output_schema_name, expected_type=type_hints["output_schema_name"])
            check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
            check_type(argname="argument baseline_table_name", value=baseline_table_name, expected_type=type_hints["baseline_table_name"])
            check_type(argname="argument custom_metrics", value=custom_metrics, expected_type=type_hints["custom_metrics"])
            check_type(argname="argument data_classification_config", value=data_classification_config, expected_type=type_hints["data_classification_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument inference_log", value=inference_log, expected_type=type_hints["inference_log"])
            check_type(argname="argument latest_monitor_failure_msg", value=latest_monitor_failure_msg, expected_type=type_hints["latest_monitor_failure_msg"])
            check_type(argname="argument notifications", value=notifications, expected_type=type_hints["notifications"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument skip_builtin_dashboard", value=skip_builtin_dashboard, expected_type=type_hints["skip_builtin_dashboard"])
            check_type(argname="argument slicing_exprs", value=slicing_exprs, expected_type=type_hints["slicing_exprs"])
            check_type(argname="argument snapshot", value=snapshot, expected_type=type_hints["snapshot"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument time_series", value=time_series, expected_type=type_hints["time_series"])
            check_type(argname="argument warehouse_id", value=warehouse_id, expected_type=type_hints["warehouse_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assets_dir": assets_dir,
            "output_schema_name": output_schema_name,
            "table_name": table_name,
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
        if baseline_table_name is not None:
            self._values["baseline_table_name"] = baseline_table_name
        if custom_metrics is not None:
            self._values["custom_metrics"] = custom_metrics
        if data_classification_config is not None:
            self._values["data_classification_config"] = data_classification_config
        if id is not None:
            self._values["id"] = id
        if inference_log is not None:
            self._values["inference_log"] = inference_log
        if latest_monitor_failure_msg is not None:
            self._values["latest_monitor_failure_msg"] = latest_monitor_failure_msg
        if notifications is not None:
            self._values["notifications"] = notifications
        if schedule is not None:
            self._values["schedule"] = schedule
        if skip_builtin_dashboard is not None:
            self._values["skip_builtin_dashboard"] = skip_builtin_dashboard
        if slicing_exprs is not None:
            self._values["slicing_exprs"] = slicing_exprs
        if snapshot is not None:
            self._values["snapshot"] = snapshot
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if time_series is not None:
            self._values["time_series"] = time_series
        if warehouse_id is not None:
            self._values["warehouse_id"] = warehouse_id

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
    def assets_dir(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#assets_dir QualityMonitor#assets_dir}.'''
        result = self._values.get("assets_dir")
        assert result is not None, "Required property 'assets_dir' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_schema_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#output_schema_name QualityMonitor#output_schema_name}.'''
        result = self._values.get("output_schema_name")
        assert result is not None, "Required property 'output_schema_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#table_name QualityMonitor#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def baseline_table_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#baseline_table_name QualityMonitor#baseline_table_name}.'''
        result = self._values.get("baseline_table_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_metrics(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QualityMonitorCustomMetrics"]]]:
        '''custom_metrics block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#custom_metrics QualityMonitor#custom_metrics}
        '''
        result = self._values.get("custom_metrics")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["QualityMonitorCustomMetrics"]]], result)

    @builtins.property
    def data_classification_config(
        self,
    ) -> typing.Optional["QualityMonitorDataClassificationConfig"]:
        '''data_classification_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#data_classification_config QualityMonitor#data_classification_config}
        '''
        result = self._values.get("data_classification_config")
        return typing.cast(typing.Optional["QualityMonitorDataClassificationConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#id QualityMonitor#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_log(self) -> typing.Optional["QualityMonitorInferenceLog"]:
        '''inference_log block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#inference_log QualityMonitor#inference_log}
        '''
        result = self._values.get("inference_log")
        return typing.cast(typing.Optional["QualityMonitorInferenceLog"], result)

    @builtins.property
    def latest_monitor_failure_msg(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#latest_monitor_failure_msg QualityMonitor#latest_monitor_failure_msg}.'''
        result = self._values.get("latest_monitor_failure_msg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notifications(self) -> typing.Optional["QualityMonitorNotifications"]:
        '''notifications block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#notifications QualityMonitor#notifications}
        '''
        result = self._values.get("notifications")
        return typing.cast(typing.Optional["QualityMonitorNotifications"], result)

    @builtins.property
    def schedule(self) -> typing.Optional["QualityMonitorSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#schedule QualityMonitor#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["QualityMonitorSchedule"], result)

    @builtins.property
    def skip_builtin_dashboard(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#skip_builtin_dashboard QualityMonitor#skip_builtin_dashboard}.'''
        result = self._values.get("skip_builtin_dashboard")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def slicing_exprs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#slicing_exprs QualityMonitor#slicing_exprs}.'''
        result = self._values.get("slicing_exprs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot(self) -> typing.Optional["QualityMonitorSnapshot"]:
        '''snapshot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#snapshot QualityMonitor#snapshot}
        '''
        result = self._values.get("snapshot")
        return typing.cast(typing.Optional["QualityMonitorSnapshot"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["QualityMonitorTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timeouts QualityMonitor#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["QualityMonitorTimeouts"], result)

    @builtins.property
    def time_series(self) -> typing.Optional["QualityMonitorTimeSeries"]:
        '''time_series block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#time_series QualityMonitor#time_series}
        '''
        result = self._values.get("time_series")
        return typing.cast(typing.Optional["QualityMonitorTimeSeries"], result)

    @builtins.property
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#warehouse_id QualityMonitor#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorCustomMetrics",
    jsii_struct_bases=[],
    name_mapping={
        "definition": "definition",
        "input_columns": "inputColumns",
        "name": "name",
        "output_data_type": "outputDataType",
        "type": "type",
    },
)
class QualityMonitorCustomMetrics:
    def __init__(
        self,
        *,
        definition: builtins.str,
        input_columns: typing.Sequence[builtins.str],
        name: builtins.str,
        output_data_type: builtins.str,
        type: builtins.str,
    ) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#definition QualityMonitor#definition}.
        :param input_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#input_columns QualityMonitor#input_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#name QualityMonitor#name}.
        :param output_data_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#output_data_type QualityMonitor#output_data_type}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#type QualityMonitor#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d28ab35228a4439c64f777de65f3e4976357ca1fcc9dfe3a21e2e91ccb664c7)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument input_columns", value=input_columns, expected_type=type_hints["input_columns"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_data_type", value=output_data_type, expected_type=type_hints["output_data_type"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "definition": definition,
            "input_columns": input_columns,
            "name": name,
            "output_data_type": output_data_type,
            "type": type,
        }

    @builtins.property
    def definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#definition QualityMonitor#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input_columns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#input_columns QualityMonitor#input_columns}.'''
        result = self._values.get("input_columns")
        assert result is not None, "Required property 'input_columns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#name QualityMonitor#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_data_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#output_data_type QualityMonitor#output_data_type}.'''
        result = self._values.get("output_data_type")
        assert result is not None, "Required property 'output_data_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#type QualityMonitor#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorCustomMetrics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorCustomMetricsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorCustomMetricsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9fe8366305e1fd50739f678163ca46b64d8b923b9f420e458738110743a82bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "QualityMonitorCustomMetricsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f9f1f61ad14ce9875b5316153462c04c3fd7ca198a864afff3cf2bc2b525d35)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("QualityMonitorCustomMetricsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e5ae56986e742f749adfa6a7762b3f4d9bfc27ffb174ec26030a0393155340)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7169aa2ac8916ca6fb0a91e7d276283ede0a67cf1d1703391b18833169296213)
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
            type_hints = typing.get_type_hints(_typecheckingstub__772599569cf3c69facdbb44eb108e7bca58d14a3fe1ca994476980edf2248710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QualityMonitorCustomMetrics]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QualityMonitorCustomMetrics]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QualityMonitorCustomMetrics]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aba9e1b66651e270fbf3002bc5f2a06fb4bbe70dd819a67778397bf4f5402a84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QualityMonitorCustomMetricsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorCustomMetricsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d939e7a82a0e2ef9f4a3f54faaa2e98ea1f7e827972a63c040fa6e7bc10268c4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "definitionInput"))

    @builtins.property
    @jsii.member(jsii_name="inputColumnsInput")
    def input_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "inputColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="outputDataTypeInput")
    def output_data_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputDataTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="definition")
    def definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24d7fb90fc1ce4805028809396e60a2f7fb97b2707db9f4442a319f787bcc390)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definition", value)

    @builtins.property
    @jsii.member(jsii_name="inputColumns")
    def input_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inputColumns"))

    @input_columns.setter
    def input_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f1cadfbbc78e2fc7f4b95705e0ffeda3a4c85abd29959ac29c7a92458e315f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputColumns", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f207fb706651d6a6ba70a0b6697bf7f4796e766a6e8c5e2affe916f313beb8ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="outputDataType")
    def output_data_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputDataType"))

    @output_data_type.setter
    def output_data_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c700264bea32a9b8b9f324fb966eaf2309a0ae3b3cd09c7925533164f6755e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputDataType", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4ad4803936e298da15456e9db82b9d00050a88ae80b476eeb80f7cf0f100f72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorCustomMetrics]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorCustomMetrics]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorCustomMetrics]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__648789b9fae843c92feda781f236712a39efb8662449d95ed0500532e51ac74c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorDataClassificationConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class QualityMonitorDataClassificationConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#enabled QualityMonitor#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a223d66f86b243616f9d1a6996a812aa9f6b57b8dd719a6c4393a94b1ec4b3fd)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#enabled QualityMonitor#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorDataClassificationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorDataClassificationConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorDataClassificationConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__45c442ed0428a36482f50483bf68c5b6b471cd2886b480612c3aee7b0f0a30a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__6a57d2c882b7f4182afc8dd04e69f19d923512b7b181a8a0f9ff93c0b8b85f81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorDataClassificationConfig]:
        return typing.cast(typing.Optional[QualityMonitorDataClassificationConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QualityMonitorDataClassificationConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d0be5496608e36c972c792be8b9b2775e600cdeb03f86df093fb683005bedf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorInferenceLog",
    jsii_struct_bases=[],
    name_mapping={
        "granularities": "granularities",
        "model_id_col": "modelIdCol",
        "prediction_col": "predictionCol",
        "problem_type": "problemType",
        "timestamp_col": "timestampCol",
        "label_col": "labelCol",
        "prediction_proba_col": "predictionProbaCol",
    },
)
class QualityMonitorInferenceLog:
    def __init__(
        self,
        *,
        granularities: typing.Sequence[builtins.str],
        model_id_col: builtins.str,
        prediction_col: builtins.str,
        problem_type: builtins.str,
        timestamp_col: builtins.str,
        label_col: typing.Optional[builtins.str] = None,
        prediction_proba_col: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param granularities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.
        :param model_id_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#model_id_col QualityMonitor#model_id_col}.
        :param prediction_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_col QualityMonitor#prediction_col}.
        :param problem_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#problem_type QualityMonitor#problem_type}.
        :param timestamp_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.
        :param label_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#label_col QualityMonitor#label_col}.
        :param prediction_proba_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_proba_col QualityMonitor#prediction_proba_col}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be45477ed1b5b91ddd3256f89b3641d285db9d26ed592a0d62cfd11307cbb9c)
            check_type(argname="argument granularities", value=granularities, expected_type=type_hints["granularities"])
            check_type(argname="argument model_id_col", value=model_id_col, expected_type=type_hints["model_id_col"])
            check_type(argname="argument prediction_col", value=prediction_col, expected_type=type_hints["prediction_col"])
            check_type(argname="argument problem_type", value=problem_type, expected_type=type_hints["problem_type"])
            check_type(argname="argument timestamp_col", value=timestamp_col, expected_type=type_hints["timestamp_col"])
            check_type(argname="argument label_col", value=label_col, expected_type=type_hints["label_col"])
            check_type(argname="argument prediction_proba_col", value=prediction_proba_col, expected_type=type_hints["prediction_proba_col"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "granularities": granularities,
            "model_id_col": model_id_col,
            "prediction_col": prediction_col,
            "problem_type": problem_type,
            "timestamp_col": timestamp_col,
        }
        if label_col is not None:
            self._values["label_col"] = label_col
        if prediction_proba_col is not None:
            self._values["prediction_proba_col"] = prediction_proba_col

    @builtins.property
    def granularities(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.'''
        result = self._values.get("granularities")
        assert result is not None, "Required property 'granularities' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def model_id_col(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#model_id_col QualityMonitor#model_id_col}.'''
        result = self._values.get("model_id_col")
        assert result is not None, "Required property 'model_id_col' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prediction_col(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_col QualityMonitor#prediction_col}.'''
        result = self._values.get("prediction_col")
        assert result is not None, "Required property 'prediction_col' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def problem_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#problem_type QualityMonitor#problem_type}.'''
        result = self._values.get("problem_type")
        assert result is not None, "Required property 'problem_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp_col(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.'''
        result = self._values.get("timestamp_col")
        assert result is not None, "Required property 'timestamp_col' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def label_col(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#label_col QualityMonitor#label_col}.'''
        result = self._values.get("label_col")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prediction_proba_col(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#prediction_proba_col QualityMonitor#prediction_proba_col}.'''
        result = self._values.get("prediction_proba_col")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorInferenceLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorInferenceLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorInferenceLogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a3f22b9570df585e9e685428b8c91330df7d95e55c56d2278a36ba87832fdc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabelCol")
    def reset_label_col(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabelCol", []))

    @jsii.member(jsii_name="resetPredictionProbaCol")
    def reset_prediction_proba_col(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPredictionProbaCol", []))

    @builtins.property
    @jsii.member(jsii_name="granularitiesInput")
    def granularities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "granularitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="labelColInput")
    def label_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelColInput"))

    @builtins.property
    @jsii.member(jsii_name="modelIdColInput")
    def model_id_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelIdColInput"))

    @builtins.property
    @jsii.member(jsii_name="predictionColInput")
    def prediction_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "predictionColInput"))

    @builtins.property
    @jsii.member(jsii_name="predictionProbaColInput")
    def prediction_proba_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "predictionProbaColInput"))

    @builtins.property
    @jsii.member(jsii_name="problemTypeInput")
    def problem_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "problemTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="timestampColInput")
    def timestamp_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timestampColInput"))

    @builtins.property
    @jsii.member(jsii_name="granularities")
    def granularities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "granularities"))

    @granularities.setter
    def granularities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e40999bd26735f7dea4ffa068100fc2714f6cf7f69d994613cbeec59adc226)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "granularities", value)

    @builtins.property
    @jsii.member(jsii_name="labelCol")
    def label_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "labelCol"))

    @label_col.setter
    def label_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca024d9a27572e124e6b4a3f86e9283ddd44c8e2a93fe8f0394ed7e5f1dd4d5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labelCol", value)

    @builtins.property
    @jsii.member(jsii_name="modelIdCol")
    def model_id_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelIdCol"))

    @model_id_col.setter
    def model_id_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72f93666b3ff5cf588d1679ec17c57b3b1cee6ddf03c308a0680a91b30dab89e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelIdCol", value)

    @builtins.property
    @jsii.member(jsii_name="predictionCol")
    def prediction_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "predictionCol"))

    @prediction_col.setter
    def prediction_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7df61a334aea3533729a64025fd3687c1eccdd599a00239058300e2fa670eb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "predictionCol", value)

    @builtins.property
    @jsii.member(jsii_name="predictionProbaCol")
    def prediction_proba_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "predictionProbaCol"))

    @prediction_proba_col.setter
    def prediction_proba_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcd19d45c547c2fb83f8fc93e9e17440479a1c174d3c968b2508610ec0d4b2a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "predictionProbaCol", value)

    @builtins.property
    @jsii.member(jsii_name="problemType")
    def problem_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "problemType"))

    @problem_type.setter
    def problem_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7d9b758560daf9ab7ab61a7878ed753765574425912c5b73502910738d5a26b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "problemType", value)

    @builtins.property
    @jsii.member(jsii_name="timestampCol")
    def timestamp_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestampCol"))

    @timestamp_col.setter
    def timestamp_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f057f6166d463bca66940e6a513afb960d1e31cd2fdefe65427166dc4118351c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timestampCol", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorInferenceLog]:
        return typing.cast(typing.Optional[QualityMonitorInferenceLog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QualityMonitorInferenceLog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f970bfa99f9f9cf2fae093c9dce933d2a28fb8bd58c576096140420648c3d18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_failure": "onFailure",
        "on_new_classification_tag_detected": "onNewClassificationTagDetected",
    },
)
class QualityMonitorNotifications:
    def __init__(
        self,
        *,
        on_failure: typing.Optional[typing.Union["QualityMonitorNotificationsOnFailure", typing.Dict[builtins.str, typing.Any]]] = None,
        on_new_classification_tag_detected: typing.Optional[typing.Union["QualityMonitorNotificationsOnNewClassificationTagDetected", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_failure QualityMonitor#on_failure}
        :param on_new_classification_tag_detected: on_new_classification_tag_detected block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_new_classification_tag_detected QualityMonitor#on_new_classification_tag_detected}
        '''
        if isinstance(on_failure, dict):
            on_failure = QualityMonitorNotificationsOnFailure(**on_failure)
        if isinstance(on_new_classification_tag_detected, dict):
            on_new_classification_tag_detected = QualityMonitorNotificationsOnNewClassificationTagDetected(**on_new_classification_tag_detected)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69eaf6c27e3b0bfcff44d7f00f2afe415d2517ce2847c900c446c52fa031f97f)
            check_type(argname="argument on_failure", value=on_failure, expected_type=type_hints["on_failure"])
            check_type(argname="argument on_new_classification_tag_detected", value=on_new_classification_tag_detected, expected_type=type_hints["on_new_classification_tag_detected"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_new_classification_tag_detected is not None:
            self._values["on_new_classification_tag_detected"] = on_new_classification_tag_detected

    @builtins.property
    def on_failure(self) -> typing.Optional["QualityMonitorNotificationsOnFailure"]:
        '''on_failure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_failure QualityMonitor#on_failure}
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional["QualityMonitorNotificationsOnFailure"], result)

    @builtins.property
    def on_new_classification_tag_detected(
        self,
    ) -> typing.Optional["QualityMonitorNotificationsOnNewClassificationTagDetected"]:
        '''on_new_classification_tag_detected block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#on_new_classification_tag_detected QualityMonitor#on_new_classification_tag_detected}
        '''
        result = self._values.get("on_new_classification_tag_detected")
        return typing.cast(typing.Optional["QualityMonitorNotificationsOnNewClassificationTagDetected"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorNotifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotificationsOnFailure",
    jsii_struct_bases=[],
    name_mapping={"email_addresses": "emailAddresses"},
)
class QualityMonitorNotificationsOnFailure:
    def __init__(
        self,
        *,
        email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa669c2b6d36ed887b58fe4b5f74a11fee27039f5339e2f2eae9b6f078f3365)
            check_type(argname="argument email_addresses", value=email_addresses, expected_type=type_hints["email_addresses"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email_addresses is not None:
            self._values["email_addresses"] = email_addresses

    @builtins.property
    def email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.'''
        result = self._values.get("email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorNotificationsOnFailure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorNotificationsOnFailureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotificationsOnFailureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__435538ec9138ab394338b4733ba693023783b9ae53807afbb2f9bd3173cdba4d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEmailAddresses")
    def reset_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAddresses", []))

    @builtins.property
    @jsii.member(jsii_name="emailAddressesInput")
    def email_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "emailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddresses")
    def email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "emailAddresses"))

    @email_addresses.setter
    def email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79795fb5503a2d063306304825179b312a70117a685ff4e7e2e360eacb669ad8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddresses", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorNotificationsOnFailure]:
        return typing.cast(typing.Optional[QualityMonitorNotificationsOnFailure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QualityMonitorNotificationsOnFailure],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b97c86869e32b9a5cf8729ddf29f65769d824b59430c311bc350e1510021339)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotificationsOnNewClassificationTagDetected",
    jsii_struct_bases=[],
    name_mapping={"email_addresses": "emailAddresses"},
)
class QualityMonitorNotificationsOnNewClassificationTagDetected:
    def __init__(
        self,
        *,
        email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87fb9ed56321a5a634e501af0e158e363f0b7ec6f54f478ff941de30dd37c833)
            check_type(argname="argument email_addresses", value=email_addresses, expected_type=type_hints["email_addresses"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email_addresses is not None:
            self._values["email_addresses"] = email_addresses

    @builtins.property
    def email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.'''
        result = self._values.get("email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorNotificationsOnNewClassificationTagDetected(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorNotificationsOnNewClassificationTagDetectedOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotificationsOnNewClassificationTagDetectedOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67e930698630102d2688164679ab175240b43823a471e3e475a34e2b7e0664ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEmailAddresses")
    def reset_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAddresses", []))

    @builtins.property
    @jsii.member(jsii_name="emailAddressesInput")
    def email_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "emailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddresses")
    def email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "emailAddresses"))

    @email_addresses.setter
    def email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44bb53bce81e0aa16ff54f962f0b8b7b3c78fe64369382063a2261ab2f89cd5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddresses", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected]:
        return typing.cast(typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8187f878a7c845f7f7a07f0d7ddcdc8fb1d553d1f57aad1e91afdd1e603a252d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QualityMonitorNotificationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorNotificationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e33280e48dbd46a587bf525331441974752c3209e88cbbaef652e9718343e496)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOnFailure")
    def put_on_failure(
        self,
        *,
        email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.
        '''
        value = QualityMonitorNotificationsOnFailure(email_addresses=email_addresses)

        return typing.cast(None, jsii.invoke(self, "putOnFailure", [value]))

    @jsii.member(jsii_name="putOnNewClassificationTagDetected")
    def put_on_new_classification_tag_detected(
        self,
        *,
        email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#email_addresses QualityMonitor#email_addresses}.
        '''
        value = QualityMonitorNotificationsOnNewClassificationTagDetected(
            email_addresses=email_addresses
        )

        return typing.cast(None, jsii.invoke(self, "putOnNewClassificationTagDetected", [value]))

    @jsii.member(jsii_name="resetOnFailure")
    def reset_on_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnFailure", []))

    @jsii.member(jsii_name="resetOnNewClassificationTagDetected")
    def reset_on_new_classification_tag_detected(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnNewClassificationTagDetected", []))

    @builtins.property
    @jsii.member(jsii_name="onFailure")
    def on_failure(self) -> QualityMonitorNotificationsOnFailureOutputReference:
        return typing.cast(QualityMonitorNotificationsOnFailureOutputReference, jsii.get(self, "onFailure"))

    @builtins.property
    @jsii.member(jsii_name="onNewClassificationTagDetected")
    def on_new_classification_tag_detected(
        self,
    ) -> QualityMonitorNotificationsOnNewClassificationTagDetectedOutputReference:
        return typing.cast(QualityMonitorNotificationsOnNewClassificationTagDetectedOutputReference, jsii.get(self, "onNewClassificationTagDetected"))

    @builtins.property
    @jsii.member(jsii_name="onFailureInput")
    def on_failure_input(self) -> typing.Optional[QualityMonitorNotificationsOnFailure]:
        return typing.cast(typing.Optional[QualityMonitorNotificationsOnFailure], jsii.get(self, "onFailureInput"))

    @builtins.property
    @jsii.member(jsii_name="onNewClassificationTagDetectedInput")
    def on_new_classification_tag_detected_input(
        self,
    ) -> typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected]:
        return typing.cast(typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected], jsii.get(self, "onNewClassificationTagDetectedInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorNotifications]:
        return typing.cast(typing.Optional[QualityMonitorNotifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QualityMonitorNotifications],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78c925a957649e253b03928d1e34ef8bb4c8265bda9d51f4972b6884b198b69b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "quartz_cron_expression": "quartzCronExpression",
        "timezone_id": "timezoneId",
        "pause_status": "pauseStatus",
    },
)
class QualityMonitorSchedule:
    def __init__(
        self,
        *,
        quartz_cron_expression: builtins.str,
        timezone_id: builtins.str,
        pause_status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quartz_cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#quartz_cron_expression QualityMonitor#quartz_cron_expression}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timezone_id QualityMonitor#timezone_id}.
        :param pause_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#pause_status QualityMonitor#pause_status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e7da5d310a308cd07f8b4791fd6bf8e7db65ab4d9df2923f6d8756a4843f248)
            check_type(argname="argument quartz_cron_expression", value=quartz_cron_expression, expected_type=type_hints["quartz_cron_expression"])
            check_type(argname="argument timezone_id", value=timezone_id, expected_type=type_hints["timezone_id"])
            check_type(argname="argument pause_status", value=pause_status, expected_type=type_hints["pause_status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "quartz_cron_expression": quartz_cron_expression,
            "timezone_id": timezone_id,
        }
        if pause_status is not None:
            self._values["pause_status"] = pause_status

    @builtins.property
    def quartz_cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#quartz_cron_expression QualityMonitor#quartz_cron_expression}.'''
        result = self._values.get("quartz_cron_expression")
        assert result is not None, "Required property 'quartz_cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timezone_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timezone_id QualityMonitor#timezone_id}.'''
        result = self._values.get("timezone_id")
        assert result is not None, "Required property 'timezone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pause_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#pause_status QualityMonitor#pause_status}.'''
        result = self._values.get("pause_status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1509485e5d5725cd429691759c19846e0b07c14ea6c33cebcd60b4a10732b4de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPauseStatus")
    def reset_pause_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPauseStatus", []))

    @builtins.property
    @jsii.member(jsii_name="pauseStatusInput")
    def pause_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pauseStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="quartzCronExpressionInput")
    def quartz_cron_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quartzCronExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="timezoneIdInput")
    def timezone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pauseStatus")
    def pause_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pauseStatus"))

    @pause_status.setter
    def pause_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3a3792cc919894f0263c2053701ba8069c744ff2973db79e2ca079a62fb55ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pauseStatus", value)

    @builtins.property
    @jsii.member(jsii_name="quartzCronExpression")
    def quartz_cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartzCronExpression"))

    @quartz_cron_expression.setter
    def quartz_cron_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e1bea2a37329a47748586f3f5e3ac08c87f607ff324d94b2cad0e3168f9fd67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quartzCronExpression", value)

    @builtins.property
    @jsii.member(jsii_name="timezoneId")
    def timezone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezoneId"))

    @timezone_id.setter
    def timezone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96e521a7b722f71548226334308e45ca1491b4b0580c4ac49c3ab2cd4befdce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezoneId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorSchedule]:
        return typing.cast(typing.Optional[QualityMonitorSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QualityMonitorSchedule]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5ea14070a87fff4e7c9f1f56afb1147d640436ef766960863966c7bbd04fa56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorSnapshot",
    jsii_struct_bases=[],
    name_mapping={},
)
class QualityMonitorSnapshot:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorSnapshot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorSnapshotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorSnapshotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7cbf3d4fe7d1337f8ff38b7013ef9404c390635c70e514bf440949f09b13c95b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorSnapshot]:
        return typing.cast(typing.Optional[QualityMonitorSnapshot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QualityMonitorSnapshot]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1c1c853c40658623c449b651b2a275b778b068742287683941956fb3911d33d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorTimeSeries",
    jsii_struct_bases=[],
    name_mapping={"granularities": "granularities", "timestamp_col": "timestampCol"},
)
class QualityMonitorTimeSeries:
    def __init__(
        self,
        *,
        granularities: typing.Sequence[builtins.str],
        timestamp_col: builtins.str,
    ) -> None:
        '''
        :param granularities: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.
        :param timestamp_col: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89e21e4d02f3884ea6553fb73df03251ef79c664485e610258c7277302173b08)
            check_type(argname="argument granularities", value=granularities, expected_type=type_hints["granularities"])
            check_type(argname="argument timestamp_col", value=timestamp_col, expected_type=type_hints["timestamp_col"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "granularities": granularities,
            "timestamp_col": timestamp_col,
        }

    @builtins.property
    def granularities(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#granularities QualityMonitor#granularities}.'''
        result = self._values.get("granularities")
        assert result is not None, "Required property 'granularities' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def timestamp_col(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#timestamp_col QualityMonitor#timestamp_col}.'''
        result = self._values.get("timestamp_col")
        assert result is not None, "Required property 'timestamp_col' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorTimeSeries(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorTimeSeriesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorTimeSeriesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2adff7c76520028e1b648a2b8952f8f8ae3e8caf66d87f3c9ec2d1d1bcc56d7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="granularitiesInput")
    def granularities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "granularitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="timestampColInput")
    def timestamp_col_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timestampColInput"))

    @builtins.property
    @jsii.member(jsii_name="granularities")
    def granularities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "granularities"))

    @granularities.setter
    def granularities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__960f354ffc6f8aaacd3a20d02fde81f6eac6397127e2487a89a6a39943ec9520)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "granularities", value)

    @builtins.property
    @jsii.member(jsii_name="timestampCol")
    def timestamp_col(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestampCol"))

    @timestamp_col.setter
    def timestamp_col(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d72d9a6d2931446c0024924719ea93af2d56ea94fbcda35793f19b4af159884a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timestampCol", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QualityMonitorTimeSeries]:
        return typing.cast(typing.Optional[QualityMonitorTimeSeries], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[QualityMonitorTimeSeries]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd1c9fc4690661d45bcedb3de2f832c173085438958d2782c40cbeac9a0d7ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class QualityMonitorTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#create QualityMonitor#create}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd58a52f189f1e41a4389dd55d5388ed13e031a9eaebd0aad55432a9b8857425)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.48.3/docs/resources/quality_monitor#create QualityMonitor#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QualityMonitorTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QualityMonitorTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.qualityMonitor.QualityMonitorTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__218fd412e9bbc052834f31c76e94acaba21d8cf82ce5470df3f29dbbfd4ec67e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07332f98fa8c0c05cc2fc878652a9f66f9fd652505648fde6a66223ed3ef377b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad459dae2dae2942ab9a224dcd8c22a49d0e7f88db308dfe26d5aad33263aa2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "QualityMonitor",
    "QualityMonitorConfig",
    "QualityMonitorCustomMetrics",
    "QualityMonitorCustomMetricsList",
    "QualityMonitorCustomMetricsOutputReference",
    "QualityMonitorDataClassificationConfig",
    "QualityMonitorDataClassificationConfigOutputReference",
    "QualityMonitorInferenceLog",
    "QualityMonitorInferenceLogOutputReference",
    "QualityMonitorNotifications",
    "QualityMonitorNotificationsOnFailure",
    "QualityMonitorNotificationsOnFailureOutputReference",
    "QualityMonitorNotificationsOnNewClassificationTagDetected",
    "QualityMonitorNotificationsOnNewClassificationTagDetectedOutputReference",
    "QualityMonitorNotificationsOutputReference",
    "QualityMonitorSchedule",
    "QualityMonitorScheduleOutputReference",
    "QualityMonitorSnapshot",
    "QualityMonitorSnapshotOutputReference",
    "QualityMonitorTimeSeries",
    "QualityMonitorTimeSeriesOutputReference",
    "QualityMonitorTimeouts",
    "QualityMonitorTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__d63c34fadb49dde6d220b1647e4f061bca431d5d6a85ebe21aba05f7c865f650(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    assets_dir: builtins.str,
    output_schema_name: builtins.str,
    table_name: builtins.str,
    baseline_table_name: typing.Optional[builtins.str] = None,
    custom_metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QualityMonitorCustomMetrics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data_classification_config: typing.Optional[typing.Union[QualityMonitorDataClassificationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    inference_log: typing.Optional[typing.Union[QualityMonitorInferenceLog, typing.Dict[builtins.str, typing.Any]]] = None,
    latest_monitor_failure_msg: typing.Optional[builtins.str] = None,
    notifications: typing.Optional[typing.Union[QualityMonitorNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[QualityMonitorSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    skip_builtin_dashboard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    slicing_exprs: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot: typing.Optional[typing.Union[QualityMonitorSnapshot, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[QualityMonitorTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    time_series: typing.Optional[typing.Union[QualityMonitorTimeSeries, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a37ef75111651cc186a8f53d70a65dd9446b1fc68d3688c3f6cf3ec2a7a08307(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9667b89954cf426f5bf734ae0508eeecacf668f64408135cb321bfdd1c5b9524(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QualityMonitorCustomMetrics, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46cd0a53e344d796baea7bdcc6e37a8d789e3215bfbc511f9a790c504d5f17d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98b266f2dcb997a2ec008fab26230e816359add51154c601557e3f43e1a60333(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95cc1e00eb3d154cef21a6d6c8a6ed065e45d62b29b35bce790f9f942f03afa7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c605536426f82f4cb9b57c5d7b86d19c6cf09f52c33ad0efd7f469afe57e235(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a68d01f79759c25e1932b4818627fb81eb52e937a01be71f7cf26eb63708737(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcfde5a49cb1961fbebcfb1c0614078b3eb4a57877f36e89b151ee811e264fe4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dba847556337aea6489a144d51697bb0ba5120777ddc6038eed6192b490db9a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__092be18310f0903e365f5498fbc1fc812c4c359f1891aa6fcb13c0beaa9f1a8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e5c1a62bf693cc1592c67d18278dcca567246414bbc56597a1d7af2a1a26c40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05678435f7570b290f763c3b5c86389a072ff9447799e981e821cfedf6cb4015(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    assets_dir: builtins.str,
    output_schema_name: builtins.str,
    table_name: builtins.str,
    baseline_table_name: typing.Optional[builtins.str] = None,
    custom_metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[QualityMonitorCustomMetrics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data_classification_config: typing.Optional[typing.Union[QualityMonitorDataClassificationConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    inference_log: typing.Optional[typing.Union[QualityMonitorInferenceLog, typing.Dict[builtins.str, typing.Any]]] = None,
    latest_monitor_failure_msg: typing.Optional[builtins.str] = None,
    notifications: typing.Optional[typing.Union[QualityMonitorNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[QualityMonitorSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    skip_builtin_dashboard: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    slicing_exprs: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot: typing.Optional[typing.Union[QualityMonitorSnapshot, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[QualityMonitorTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    time_series: typing.Optional[typing.Union[QualityMonitorTimeSeries, typing.Dict[builtins.str, typing.Any]]] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d28ab35228a4439c64f777de65f3e4976357ca1fcc9dfe3a21e2e91ccb664c7(
    *,
    definition: builtins.str,
    input_columns: typing.Sequence[builtins.str],
    name: builtins.str,
    output_data_type: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9fe8366305e1fd50739f678163ca46b64d8b923b9f420e458738110743a82bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f9f1f61ad14ce9875b5316153462c04c3fd7ca198a864afff3cf2bc2b525d35(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e5ae56986e742f749adfa6a7762b3f4d9bfc27ffb174ec26030a0393155340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7169aa2ac8916ca6fb0a91e7d276283ede0a67cf1d1703391b18833169296213(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__772599569cf3c69facdbb44eb108e7bca58d14a3fe1ca994476980edf2248710(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aba9e1b66651e270fbf3002bc5f2a06fb4bbe70dd819a67778397bf4f5402a84(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[QualityMonitorCustomMetrics]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d939e7a82a0e2ef9f4a3f54faaa2e98ea1f7e827972a63c040fa6e7bc10268c4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24d7fb90fc1ce4805028809396e60a2f7fb97b2707db9f4442a319f787bcc390(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f1cadfbbc78e2fc7f4b95705e0ffeda3a4c85abd29959ac29c7a92458e315f4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f207fb706651d6a6ba70a0b6697bf7f4796e766a6e8c5e2affe916f313beb8ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c700264bea32a9b8b9f324fb966eaf2309a0ae3b3cd09c7925533164f6755e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4ad4803936e298da15456e9db82b9d00050a88ae80b476eeb80f7cf0f100f72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__648789b9fae843c92feda781f236712a39efb8662449d95ed0500532e51ac74c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorCustomMetrics]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a223d66f86b243616f9d1a6996a812aa9f6b57b8dd719a6c4393a94b1ec4b3fd(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45c442ed0428a36482f50483bf68c5b6b471cd2886b480612c3aee7b0f0a30a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a57d2c882b7f4182afc8dd04e69f19d923512b7b181a8a0f9ff93c0b8b85f81(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d0be5496608e36c972c792be8b9b2775e600cdeb03f86df093fb683005bedf5(
    value: typing.Optional[QualityMonitorDataClassificationConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be45477ed1b5b91ddd3256f89b3641d285db9d26ed592a0d62cfd11307cbb9c(
    *,
    granularities: typing.Sequence[builtins.str],
    model_id_col: builtins.str,
    prediction_col: builtins.str,
    problem_type: builtins.str,
    timestamp_col: builtins.str,
    label_col: typing.Optional[builtins.str] = None,
    prediction_proba_col: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a3f22b9570df585e9e685428b8c91330df7d95e55c56d2278a36ba87832fdc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e40999bd26735f7dea4ffa068100fc2714f6cf7f69d994613cbeec59adc226(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca024d9a27572e124e6b4a3f86e9283ddd44c8e2a93fe8f0394ed7e5f1dd4d5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72f93666b3ff5cf588d1679ec17c57b3b1cee6ddf03c308a0680a91b30dab89e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7df61a334aea3533729a64025fd3687c1eccdd599a00239058300e2fa670eb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcd19d45c547c2fb83f8fc93e9e17440479a1c174d3c968b2508610ec0d4b2a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7d9b758560daf9ab7ab61a7878ed753765574425912c5b73502910738d5a26b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f057f6166d463bca66940e6a513afb960d1e31cd2fdefe65427166dc4118351c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f970bfa99f9f9cf2fae093c9dce933d2a28fb8bd58c576096140420648c3d18(
    value: typing.Optional[QualityMonitorInferenceLog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69eaf6c27e3b0bfcff44d7f00f2afe415d2517ce2847c900c446c52fa031f97f(
    *,
    on_failure: typing.Optional[typing.Union[QualityMonitorNotificationsOnFailure, typing.Dict[builtins.str, typing.Any]]] = None,
    on_new_classification_tag_detected: typing.Optional[typing.Union[QualityMonitorNotificationsOnNewClassificationTagDetected, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfa669c2b6d36ed887b58fe4b5f74a11fee27039f5339e2f2eae9b6f078f3365(
    *,
    email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__435538ec9138ab394338b4733ba693023783b9ae53807afbb2f9bd3173cdba4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79795fb5503a2d063306304825179b312a70117a685ff4e7e2e360eacb669ad8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b97c86869e32b9a5cf8729ddf29f65769d824b59430c311bc350e1510021339(
    value: typing.Optional[QualityMonitorNotificationsOnFailure],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87fb9ed56321a5a634e501af0e158e363f0b7ec6f54f478ff941de30dd37c833(
    *,
    email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e930698630102d2688164679ab175240b43823a471e3e475a34e2b7e0664ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44bb53bce81e0aa16ff54f962f0b8b7b3c78fe64369382063a2261ab2f89cd5b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8187f878a7c845f7f7a07f0d7ddcdc8fb1d553d1f57aad1e91afdd1e603a252d(
    value: typing.Optional[QualityMonitorNotificationsOnNewClassificationTagDetected],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e33280e48dbd46a587bf525331441974752c3209e88cbbaef652e9718343e496(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c925a957649e253b03928d1e34ef8bb4c8265bda9d51f4972b6884b198b69b(
    value: typing.Optional[QualityMonitorNotifications],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e7da5d310a308cd07f8b4791fd6bf8e7db65ab4d9df2923f6d8756a4843f248(
    *,
    quartz_cron_expression: builtins.str,
    timezone_id: builtins.str,
    pause_status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1509485e5d5725cd429691759c19846e0b07c14ea6c33cebcd60b4a10732b4de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3a3792cc919894f0263c2053701ba8069c744ff2973db79e2ca079a62fb55ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e1bea2a37329a47748586f3f5e3ac08c87f607ff324d94b2cad0e3168f9fd67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96e521a7b722f71548226334308e45ca1491b4b0580c4ac49c3ab2cd4befdce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5ea14070a87fff4e7c9f1f56afb1147d640436ef766960863966c7bbd04fa56(
    value: typing.Optional[QualityMonitorSchedule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cbf3d4fe7d1337f8ff38b7013ef9404c390635c70e514bf440949f09b13c95b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c1c853c40658623c449b651b2a275b778b068742287683941956fb3911d33d(
    value: typing.Optional[QualityMonitorSnapshot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e21e4d02f3884ea6553fb73df03251ef79c664485e610258c7277302173b08(
    *,
    granularities: typing.Sequence[builtins.str],
    timestamp_col: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2adff7c76520028e1b648a2b8952f8f8ae3e8caf66d87f3c9ec2d1d1bcc56d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__960f354ffc6f8aaacd3a20d02fde81f6eac6397127e2487a89a6a39943ec9520(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d72d9a6d2931446c0024924719ea93af2d56ea94fbcda35793f19b4af159884a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd1c9fc4690661d45bcedb3de2f832c173085438958d2782c40cbeac9a0d7ce(
    value: typing.Optional[QualityMonitorTimeSeries],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd58a52f189f1e41a4389dd55d5388ed13e031a9eaebd0aad55432a9b8857425(
    *,
    create: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__218fd412e9bbc052834f31c76e94acaba21d8cf82ce5470df3f29dbbfd4ec67e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07332f98fa8c0c05cc2fc878652a9f66f9fd652505648fde6a66223ed3ef377b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad459dae2dae2942ab9a224dcd8c22a49d0e7f88db308dfe26d5aad33263aa2c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, QualityMonitorTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
