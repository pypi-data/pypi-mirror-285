r'''
# `upcloud_managed_database_opensearch`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_opensearch`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch).
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


class ManagedDatabaseOpensearch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearch",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabaseOpensearchConfig(
            name=name,
            plan=plan,
            title=title,
            zone=zone,
            access_control=access_control,
            extended_access_control=extended_access_control,
            id=id,
            maintenance_window_dow=maintenance_window_dow,
            maintenance_window_time=maintenance_window_time,
            network=network,
            powered=powered,
            properties=properties,
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
        '''Generates CDKTF code for importing a ManagedDatabaseOpensearch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabaseOpensearch to import.
        :param import_from_id: The id of the existing ManagedDatabaseOpensearch that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabaseOpensearch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827b59afce111c617fb7e5a741d9b2a3004395e4c68a14fedcd8c61308c66442)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_failure_listeners: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListeners", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        custom_domain: typing.Optional[builtins.str] = None,
        email_sender_name: typing.Optional[builtins.str] = None,
        email_sender_password: typing.Optional[builtins.str] = None,
        email_sender_username: typing.Optional[builtins.str] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length: typing.Optional[jsii.Number] = None,
        http_max_header_size: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length: typing.Optional[jsii.Number] = None,
        index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_template: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
        keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
        openid: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpenid", typing.Dict[builtins.str, typing.Any]]] = None,
        opensearch_dashboards: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpensearchDashboards", typing.Dict[builtins.str, typing.Any]]] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_auto_create_index_enabled: action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        :param action_destructive_requires_name: Require explicit index names when deleting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        :param auth_failure_listeners: auth_failure_listeners block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param cluster_max_shards_per_node: Controls the number of shards allowed in the cluster per data node. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        :param cluster_routing_allocation_node_concurrent_recoveries: Concurrent incoming/outgoing shard recoveries per node. How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        :param custom_domain: Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        :param email_sender_name: Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore. This should be identical to the Sender name defined in Opensearch dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        :param email_sender_password: Sender password for Opensearch alerts to authenticate with SMTP server. Sender password for Opensearch alerts to authenticate with SMTP server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        :param email_sender_username: Sender username for Opensearch alerts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        :param enable_security_audit: Enable/Disable security audit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        :param http_max_content_length: Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        :param http_max_header_size: The max size of allowed headers, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        :param http_max_initial_line_length: The max length of an HTTP URL, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        :param index_patterns: Index patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        :param index_template: index_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        :param indices_fielddata_cache_size: Relative amount. Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        :param indices_memory_index_buffer_size: Percentage value. Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        :param indices_memory_max_index_buffer_size: Absolute value. Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        :param indices_memory_min_index_buffer_size: Absolute value. Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        :param indices_queries_cache_size: Percentage value. Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        :param indices_query_bool_max_clause_count: Maximum number of clauses Lucene BooleanQuery can have. The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        :param indices_recovery_max_bytes_per_sec: Limits total inbound and outbound recovery traffic for each node. Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        :param indices_recovery_max_concurrent_file_chunks: Number of file chunks sent in parallel for each recovery. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param ism_enabled: Specifies whether ISM is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        :param ism_history_enabled: Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        :param ism_history_max_age: The maximum age before rolling over the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        :param ism_history_max_docs: The maximum number of documents before rolling over the audit history index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        :param ism_history_rollover_check_period: The time between rollover checks for the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        :param ism_history_rollover_retention_period: How long audit history indices are kept in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        :param keep_index_refresh_interval: Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        :param knn_memory_circuit_breaker_enabled: Enable or disable KNN memory circuit breaker. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        :param knn_memory_circuit_breaker_limit: Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        :param openid: openid block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        :param opensearch_dashboards: opensearch_dashboards block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        :param override_main_response_version: Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        :param plugins_alerting_filter_by_backend_roles: Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param reindex_remote_whitelist: Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        :param script_max_compilations_rate: Script max compilation rate - circuit breaker to prevent/minimize OOMs. Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        :param search_max_buckets: Maximum number of aggregation buckets allowed in a single response. OpenSearch default value is used when this is not defined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        :param thread_pool_analyze_queue_size: analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        :param thread_pool_analyze_size: analyze thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        :param thread_pool_force_merge_size: force_merge thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        :param thread_pool_get_queue_size: get thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        :param thread_pool_get_size: get thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        :param thread_pool_search_queue_size: search thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        :param thread_pool_search_size: search thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        :param thread_pool_search_throttled_queue_size: search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        :param thread_pool_search_throttled_size: search_throttled thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        :param thread_pool_write_queue_size: write thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        :param thread_pool_write_size: write thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        value = ManagedDatabaseOpensearchProperties(
            action_auto_create_index_enabled=action_auto_create_index_enabled,
            action_destructive_requires_name=action_destructive_requires_name,
            auth_failure_listeners=auth_failure_listeners,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            cluster_max_shards_per_node=cluster_max_shards_per_node,
            cluster_routing_allocation_node_concurrent_recoveries=cluster_routing_allocation_node_concurrent_recoveries,
            custom_domain=custom_domain,
            email_sender_name=email_sender_name,
            email_sender_password=email_sender_password,
            email_sender_username=email_sender_username,
            enable_security_audit=enable_security_audit,
            http_max_content_length=http_max_content_length,
            http_max_header_size=http_max_header_size,
            http_max_initial_line_length=http_max_initial_line_length,
            index_patterns=index_patterns,
            index_template=index_template,
            indices_fielddata_cache_size=indices_fielddata_cache_size,
            indices_memory_index_buffer_size=indices_memory_index_buffer_size,
            indices_memory_max_index_buffer_size=indices_memory_max_index_buffer_size,
            indices_memory_min_index_buffer_size=indices_memory_min_index_buffer_size,
            indices_queries_cache_size=indices_queries_cache_size,
            indices_query_bool_max_clause_count=indices_query_bool_max_clause_count,
            indices_recovery_max_bytes_per_sec=indices_recovery_max_bytes_per_sec,
            indices_recovery_max_concurrent_file_chunks=indices_recovery_max_concurrent_file_chunks,
            ip_filter=ip_filter,
            ism_enabled=ism_enabled,
            ism_history_enabled=ism_history_enabled,
            ism_history_max_age=ism_history_max_age,
            ism_history_max_docs=ism_history_max_docs,
            ism_history_rollover_check_period=ism_history_rollover_check_period,
            ism_history_rollover_retention_period=ism_history_rollover_retention_period,
            keep_index_refresh_interval=keep_index_refresh_interval,
            knn_memory_circuit_breaker_enabled=knn_memory_circuit_breaker_enabled,
            knn_memory_circuit_breaker_limit=knn_memory_circuit_breaker_limit,
            openid=openid,
            opensearch_dashboards=opensearch_dashboards,
            override_main_response_version=override_main_response_version,
            plugins_alerting_filter_by_backend_roles=plugins_alerting_filter_by_backend_roles,
            public_access=public_access,
            reindex_remote_whitelist=reindex_remote_whitelist,
            saml=saml,
            script_max_compilations_rate=script_max_compilations_rate,
            search_max_buckets=search_max_buckets,
            service_log=service_log,
            thread_pool_analyze_queue_size=thread_pool_analyze_queue_size,
            thread_pool_analyze_size=thread_pool_analyze_size,
            thread_pool_force_merge_size=thread_pool_force_merge_size,
            thread_pool_get_queue_size=thread_pool_get_queue_size,
            thread_pool_get_size=thread_pool_get_size,
            thread_pool_search_queue_size=thread_pool_search_queue_size,
            thread_pool_search_size=thread_pool_search_size,
            thread_pool_search_throttled_queue_size=thread_pool_search_throttled_queue_size,
            thread_pool_search_throttled_size=thread_pool_search_throttled_size,
            thread_pool_write_queue_size=thread_pool_write_queue_size,
            thread_pool_write_size=thread_pool_write_size,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetAccessControl")
    def reset_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControl", []))

    @jsii.member(jsii_name="resetExtendedAccessControl")
    def reset_extended_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedAccessControl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaintenanceWindowDow")
    def reset_maintenance_window_dow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowDow", []))

    @jsii.member(jsii_name="resetMaintenanceWindowTime")
    def reset_maintenance_window_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowTime", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetPowered")
    def reset_powered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPowered", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

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
    @jsii.member(jsii_name="components")
    def components(self) -> "ManagedDatabaseOpensearchComponentsList":
        return typing.cast("ManagedDatabaseOpensearchComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ManagedDatabaseOpensearchNetworkList":
        return typing.cast("ManagedDatabaseOpensearchNetworkList", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseOpensearchNodeStatesList":
        return typing.cast("ManagedDatabaseOpensearchNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseOpensearchPropertiesOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property
    @jsii.member(jsii_name="serviceHost")
    def service_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceHost"))

    @builtins.property
    @jsii.member(jsii_name="servicePassword")
    def service_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePassword"))

    @builtins.property
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePort"))

    @builtins.property
    @jsii.member(jsii_name="serviceUri")
    def service_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUri"))

    @builtins.property
    @jsii.member(jsii_name="serviceUsername")
    def service_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUsername"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="accessControlInput")
    def access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControlInput")
    def extended_access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "extendedAccessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDowInput")
    def maintenance_window_dow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowDowInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTimeInput")
    def maintenance_window_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property
    @jsii.member(jsii_name="poweredInput")
    def powered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "poweredInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="accessControl")
    def access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "accessControl"))

    @access_control.setter
    def access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessControl", value)

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControl")
    def extended_access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "extendedAccessControl"))

    @extended_access_control.setter
    def extended_access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedAccessControl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value)

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plan", value)

    @builtins.property
    @jsii.member(jsii_name="powered")
    def powered(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "powered"))

    @powered.setter
    def powered(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "powered", value)

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value)

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseOpensearchComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="component")
    def component(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "component"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property
    @jsii.member(jsii_name="usage")
    def usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "plan": "plan",
        "title": "title",
        "zone": "zone",
        "access_control": "accessControl",
        "extended_access_control": "extendedAccessControl",
        "id": "id",
        "maintenance_window_dow": "maintenanceWindowDow",
        "maintenance_window_time": "maintenanceWindowTime",
        "network": "network",
        "powered": "powered",
        "properties": "properties",
    },
)
class ManagedDatabaseOpensearchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseOpensearchProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument extended_access_control", value=extended_access_control, expected_type=type_hints["extended_access_control"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument maintenance_window_dow", value=maintenance_window_dow, expected_type=type_hints["maintenance_window_dow"])
            check_type(argname="argument maintenance_window_time", value=maintenance_window_time, expected_type=type_hints["maintenance_window_time"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument powered", value=powered, expected_type=type_hints["powered"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "plan": plan,
            "title": title,
            "zone": zone,
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
        if access_control is not None:
            self._values["access_control"] = access_control
        if extended_access_control is not None:
            self._values["extended_access_control"] = extended_access_control
        if id is not None:
            self._values["id"] = id
        if maintenance_window_dow is not None:
            self._values["maintenance_window_dow"] = maintenance_window_dow
        if maintenance_window_time is not None:
            self._values["maintenance_window_time"] = maintenance_window_time
        if network is not None:
            self._values["network"] = network
        if powered is not None:
            self._values["powered"] = powered
        if properties is not None:
            self._values["properties"] = properties

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
    def name(self) -> builtins.str:
        '''Name of the service.

        The name is used as a prefix for the logical hostname. Must be unique within an account

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables users access control for OpenSearch service.

        User access control rules will only be enforced if this attribute is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def extended_access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs.

        Users are limited to perform operations on indices based on the user-specific access control rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        '''
        result = self._values.get("extended_access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetwork",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "type": "type", "uuid": "uuid"},
)
class ManagedDatabaseOpensearchNetwork:
    def __init__(
        self,
        *,
        family: builtins.str,
        name: builtins.str,
        type: builtins.str,
        uuid: builtins.str,
    ) -> None:
        '''
        :param family: Network family. Currently only ``IPv4`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#family ManagedDatabaseOpensearch#family}
        :param name: The name of the network. Must be unique within the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param type: The type of the network. Must be private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        :param uuid: Private network UUID. Must reside in the same zone as the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#uuid ManagedDatabaseOpensearch#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca8408590124dd06a9281b50a661dcbdbb53334fd0cbfb3b4fed6c54dc2fd83)
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "family": family,
            "name": name,
            "type": type,
            "uuid": uuid,
        }

    @builtins.property
    def family(self) -> builtins.str:
        '''Network family. Currently only ``IPv4`` is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#family ManagedDatabaseOpensearch#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network. Must be unique within the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the network. Must be private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uuid(self) -> builtins.str:
        '''Private network UUID. Must reside in the same zone as the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#uuid ManagedDatabaseOpensearch#uuid}
        '''
        result = self._values.get("uuid")
        assert result is not None, "Required property 'uuid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchNetworkList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetworkList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e329b18badd7d49b48b57bfe67898d0a24d2355460b3e92344a172ad07ecd4f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32720d726b88051a33b0a45fd56ea4118a2f932301f8c2b2a1d84423707660d7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f41e22d45dd70224aad1ec2381618b7683e3b9cbc00c500cdc37da46e33fbf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__517c0a72cf55cce1ae9b6342f33106b189fcd6dc12b3fb06aece1db1c9deae0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2429cd8dff761f1e319900b52e924676682282f94ad7505ba9fe22ee0013cf20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7988b51be371d4764a089b96fd2c9e8d7deb564eb6a899f5837744f8aa64b302)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ManagedDatabaseOpensearchNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14f5527b348fe4ce85b3f81d752ce7962795f510497f946d3c9fa3d824f60542)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caf0f3fab78ca354752f87686c4ceb87c0908570faaf71c9732bf3b9af492e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f552807981014b5ed36ce91c9049ddd1640edc60f00b525be36ade219e1114fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e73f2b43516cb1cd2e49b889369e26357e42dba138c5c96b56d7155745209e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae4a80d42aa53b63a4e5515fe09be52313dfd3d7869eb5dfcb8797bdfedaa35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17b8944baa901c2ed823dd7faa74dbd4e7cdddd833b000fe7f421fb4ee6b6a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseOpensearchNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchProperties",
    jsii_struct_bases=[],
    name_mapping={
        "action_auto_create_index_enabled": "actionAutoCreateIndexEnabled",
        "action_destructive_requires_name": "actionDestructiveRequiresName",
        "auth_failure_listeners": "authFailureListeners",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "cluster_max_shards_per_node": "clusterMaxShardsPerNode",
        "cluster_routing_allocation_node_concurrent_recoveries": "clusterRoutingAllocationNodeConcurrentRecoveries",
        "custom_domain": "customDomain",
        "email_sender_name": "emailSenderName",
        "email_sender_password": "emailSenderPassword",
        "email_sender_username": "emailSenderUsername",
        "enable_security_audit": "enableSecurityAudit",
        "http_max_content_length": "httpMaxContentLength",
        "http_max_header_size": "httpMaxHeaderSize",
        "http_max_initial_line_length": "httpMaxInitialLineLength",
        "index_patterns": "indexPatterns",
        "index_template": "indexTemplate",
        "indices_fielddata_cache_size": "indicesFielddataCacheSize",
        "indices_memory_index_buffer_size": "indicesMemoryIndexBufferSize",
        "indices_memory_max_index_buffer_size": "indicesMemoryMaxIndexBufferSize",
        "indices_memory_min_index_buffer_size": "indicesMemoryMinIndexBufferSize",
        "indices_queries_cache_size": "indicesQueriesCacheSize",
        "indices_query_bool_max_clause_count": "indicesQueryBoolMaxClauseCount",
        "indices_recovery_max_bytes_per_sec": "indicesRecoveryMaxBytesPerSec",
        "indices_recovery_max_concurrent_file_chunks": "indicesRecoveryMaxConcurrentFileChunks",
        "ip_filter": "ipFilter",
        "ism_enabled": "ismEnabled",
        "ism_history_enabled": "ismHistoryEnabled",
        "ism_history_max_age": "ismHistoryMaxAge",
        "ism_history_max_docs": "ismHistoryMaxDocs",
        "ism_history_rollover_check_period": "ismHistoryRolloverCheckPeriod",
        "ism_history_rollover_retention_period": "ismHistoryRolloverRetentionPeriod",
        "keep_index_refresh_interval": "keepIndexRefreshInterval",
        "knn_memory_circuit_breaker_enabled": "knnMemoryCircuitBreakerEnabled",
        "knn_memory_circuit_breaker_limit": "knnMemoryCircuitBreakerLimit",
        "openid": "openid",
        "opensearch_dashboards": "opensearchDashboards",
        "override_main_response_version": "overrideMainResponseVersion",
        "plugins_alerting_filter_by_backend_roles": "pluginsAlertingFilterByBackendRoles",
        "public_access": "publicAccess",
        "reindex_remote_whitelist": "reindexRemoteWhitelist",
        "saml": "saml",
        "script_max_compilations_rate": "scriptMaxCompilationsRate",
        "search_max_buckets": "searchMaxBuckets",
        "service_log": "serviceLog",
        "thread_pool_analyze_queue_size": "threadPoolAnalyzeQueueSize",
        "thread_pool_analyze_size": "threadPoolAnalyzeSize",
        "thread_pool_force_merge_size": "threadPoolForceMergeSize",
        "thread_pool_get_queue_size": "threadPoolGetQueueSize",
        "thread_pool_get_size": "threadPoolGetSize",
        "thread_pool_search_queue_size": "threadPoolSearchQueueSize",
        "thread_pool_search_size": "threadPoolSearchSize",
        "thread_pool_search_throttled_queue_size": "threadPoolSearchThrottledQueueSize",
        "thread_pool_search_throttled_size": "threadPoolSearchThrottledSize",
        "thread_pool_write_queue_size": "threadPoolWriteQueueSize",
        "thread_pool_write_size": "threadPoolWriteSize",
        "version": "version",
    },
)
class ManagedDatabaseOpensearchProperties:
    def __init__(
        self,
        *,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_failure_listeners: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListeners", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        custom_domain: typing.Optional[builtins.str] = None,
        email_sender_name: typing.Optional[builtins.str] = None,
        email_sender_password: typing.Optional[builtins.str] = None,
        email_sender_username: typing.Optional[builtins.str] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length: typing.Optional[jsii.Number] = None,
        http_max_header_size: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length: typing.Optional[jsii.Number] = None,
        index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_template: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
        keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
        openid: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpenid", typing.Dict[builtins.str, typing.Any]]] = None,
        opensearch_dashboards: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpensearchDashboards", typing.Dict[builtins.str, typing.Any]]] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_auto_create_index_enabled: action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        :param action_destructive_requires_name: Require explicit index names when deleting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        :param auth_failure_listeners: auth_failure_listeners block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param cluster_max_shards_per_node: Controls the number of shards allowed in the cluster per data node. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        :param cluster_routing_allocation_node_concurrent_recoveries: Concurrent incoming/outgoing shard recoveries per node. How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        :param custom_domain: Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        :param email_sender_name: Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore. This should be identical to the Sender name defined in Opensearch dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        :param email_sender_password: Sender password for Opensearch alerts to authenticate with SMTP server. Sender password for Opensearch alerts to authenticate with SMTP server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        :param email_sender_username: Sender username for Opensearch alerts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        :param enable_security_audit: Enable/Disable security audit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        :param http_max_content_length: Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        :param http_max_header_size: The max size of allowed headers, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        :param http_max_initial_line_length: The max length of an HTTP URL, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        :param index_patterns: Index patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        :param index_template: index_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        :param indices_fielddata_cache_size: Relative amount. Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        :param indices_memory_index_buffer_size: Percentage value. Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        :param indices_memory_max_index_buffer_size: Absolute value. Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        :param indices_memory_min_index_buffer_size: Absolute value. Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        :param indices_queries_cache_size: Percentage value. Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        :param indices_query_bool_max_clause_count: Maximum number of clauses Lucene BooleanQuery can have. The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        :param indices_recovery_max_bytes_per_sec: Limits total inbound and outbound recovery traffic for each node. Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        :param indices_recovery_max_concurrent_file_chunks: Number of file chunks sent in parallel for each recovery. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param ism_enabled: Specifies whether ISM is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        :param ism_history_enabled: Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        :param ism_history_max_age: The maximum age before rolling over the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        :param ism_history_max_docs: The maximum number of documents before rolling over the audit history index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        :param ism_history_rollover_check_period: The time between rollover checks for the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        :param ism_history_rollover_retention_period: How long audit history indices are kept in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        :param keep_index_refresh_interval: Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        :param knn_memory_circuit_breaker_enabled: Enable or disable KNN memory circuit breaker. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        :param knn_memory_circuit_breaker_limit: Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        :param openid: openid block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        :param opensearch_dashboards: opensearch_dashboards block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        :param override_main_response_version: Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        :param plugins_alerting_filter_by_backend_roles: Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param reindex_remote_whitelist: Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        :param script_max_compilations_rate: Script max compilation rate - circuit breaker to prevent/minimize OOMs. Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        :param search_max_buckets: Maximum number of aggregation buckets allowed in a single response. OpenSearch default value is used when this is not defined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        :param thread_pool_analyze_queue_size: analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        :param thread_pool_analyze_size: analyze thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        :param thread_pool_force_merge_size: force_merge thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        :param thread_pool_get_queue_size: get thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        :param thread_pool_get_size: get thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        :param thread_pool_search_queue_size: search thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        :param thread_pool_search_size: search thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        :param thread_pool_search_throttled_queue_size: search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        :param thread_pool_search_throttled_size: search_throttled thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        :param thread_pool_write_queue_size: write thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        :param thread_pool_write_size: write thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        if isinstance(auth_failure_listeners, dict):
            auth_failure_listeners = ManagedDatabaseOpensearchPropertiesAuthFailureListeners(**auth_failure_listeners)
        if isinstance(index_template, dict):
            index_template = ManagedDatabaseOpensearchPropertiesIndexTemplate(**index_template)
        if isinstance(openid, dict):
            openid = ManagedDatabaseOpensearchPropertiesOpenid(**openid)
        if isinstance(opensearch_dashboards, dict):
            opensearch_dashboards = ManagedDatabaseOpensearchPropertiesOpensearchDashboards(**opensearch_dashboards)
        if isinstance(saml, dict):
            saml = ManagedDatabaseOpensearchPropertiesSaml(**saml)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d)
            check_type(argname="argument action_auto_create_index_enabled", value=action_auto_create_index_enabled, expected_type=type_hints["action_auto_create_index_enabled"])
            check_type(argname="argument action_destructive_requires_name", value=action_destructive_requires_name, expected_type=type_hints["action_destructive_requires_name"])
            check_type(argname="argument auth_failure_listeners", value=auth_failure_listeners, expected_type=type_hints["auth_failure_listeners"])
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument cluster_max_shards_per_node", value=cluster_max_shards_per_node, expected_type=type_hints["cluster_max_shards_per_node"])
            check_type(argname="argument cluster_routing_allocation_node_concurrent_recoveries", value=cluster_routing_allocation_node_concurrent_recoveries, expected_type=type_hints["cluster_routing_allocation_node_concurrent_recoveries"])
            check_type(argname="argument custom_domain", value=custom_domain, expected_type=type_hints["custom_domain"])
            check_type(argname="argument email_sender_name", value=email_sender_name, expected_type=type_hints["email_sender_name"])
            check_type(argname="argument email_sender_password", value=email_sender_password, expected_type=type_hints["email_sender_password"])
            check_type(argname="argument email_sender_username", value=email_sender_username, expected_type=type_hints["email_sender_username"])
            check_type(argname="argument enable_security_audit", value=enable_security_audit, expected_type=type_hints["enable_security_audit"])
            check_type(argname="argument http_max_content_length", value=http_max_content_length, expected_type=type_hints["http_max_content_length"])
            check_type(argname="argument http_max_header_size", value=http_max_header_size, expected_type=type_hints["http_max_header_size"])
            check_type(argname="argument http_max_initial_line_length", value=http_max_initial_line_length, expected_type=type_hints["http_max_initial_line_length"])
            check_type(argname="argument index_patterns", value=index_patterns, expected_type=type_hints["index_patterns"])
            check_type(argname="argument index_template", value=index_template, expected_type=type_hints["index_template"])
            check_type(argname="argument indices_fielddata_cache_size", value=indices_fielddata_cache_size, expected_type=type_hints["indices_fielddata_cache_size"])
            check_type(argname="argument indices_memory_index_buffer_size", value=indices_memory_index_buffer_size, expected_type=type_hints["indices_memory_index_buffer_size"])
            check_type(argname="argument indices_memory_max_index_buffer_size", value=indices_memory_max_index_buffer_size, expected_type=type_hints["indices_memory_max_index_buffer_size"])
            check_type(argname="argument indices_memory_min_index_buffer_size", value=indices_memory_min_index_buffer_size, expected_type=type_hints["indices_memory_min_index_buffer_size"])
            check_type(argname="argument indices_queries_cache_size", value=indices_queries_cache_size, expected_type=type_hints["indices_queries_cache_size"])
            check_type(argname="argument indices_query_bool_max_clause_count", value=indices_query_bool_max_clause_count, expected_type=type_hints["indices_query_bool_max_clause_count"])
            check_type(argname="argument indices_recovery_max_bytes_per_sec", value=indices_recovery_max_bytes_per_sec, expected_type=type_hints["indices_recovery_max_bytes_per_sec"])
            check_type(argname="argument indices_recovery_max_concurrent_file_chunks", value=indices_recovery_max_concurrent_file_chunks, expected_type=type_hints["indices_recovery_max_concurrent_file_chunks"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument ism_enabled", value=ism_enabled, expected_type=type_hints["ism_enabled"])
            check_type(argname="argument ism_history_enabled", value=ism_history_enabled, expected_type=type_hints["ism_history_enabled"])
            check_type(argname="argument ism_history_max_age", value=ism_history_max_age, expected_type=type_hints["ism_history_max_age"])
            check_type(argname="argument ism_history_max_docs", value=ism_history_max_docs, expected_type=type_hints["ism_history_max_docs"])
            check_type(argname="argument ism_history_rollover_check_period", value=ism_history_rollover_check_period, expected_type=type_hints["ism_history_rollover_check_period"])
            check_type(argname="argument ism_history_rollover_retention_period", value=ism_history_rollover_retention_period, expected_type=type_hints["ism_history_rollover_retention_period"])
            check_type(argname="argument keep_index_refresh_interval", value=keep_index_refresh_interval, expected_type=type_hints["keep_index_refresh_interval"])
            check_type(argname="argument knn_memory_circuit_breaker_enabled", value=knn_memory_circuit_breaker_enabled, expected_type=type_hints["knn_memory_circuit_breaker_enabled"])
            check_type(argname="argument knn_memory_circuit_breaker_limit", value=knn_memory_circuit_breaker_limit, expected_type=type_hints["knn_memory_circuit_breaker_limit"])
            check_type(argname="argument openid", value=openid, expected_type=type_hints["openid"])
            check_type(argname="argument opensearch_dashboards", value=opensearch_dashboards, expected_type=type_hints["opensearch_dashboards"])
            check_type(argname="argument override_main_response_version", value=override_main_response_version, expected_type=type_hints["override_main_response_version"])
            check_type(argname="argument plugins_alerting_filter_by_backend_roles", value=plugins_alerting_filter_by_backend_roles, expected_type=type_hints["plugins_alerting_filter_by_backend_roles"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument reindex_remote_whitelist", value=reindex_remote_whitelist, expected_type=type_hints["reindex_remote_whitelist"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
            check_type(argname="argument script_max_compilations_rate", value=script_max_compilations_rate, expected_type=type_hints["script_max_compilations_rate"])
            check_type(argname="argument search_max_buckets", value=search_max_buckets, expected_type=type_hints["search_max_buckets"])
            check_type(argname="argument service_log", value=service_log, expected_type=type_hints["service_log"])
            check_type(argname="argument thread_pool_analyze_queue_size", value=thread_pool_analyze_queue_size, expected_type=type_hints["thread_pool_analyze_queue_size"])
            check_type(argname="argument thread_pool_analyze_size", value=thread_pool_analyze_size, expected_type=type_hints["thread_pool_analyze_size"])
            check_type(argname="argument thread_pool_force_merge_size", value=thread_pool_force_merge_size, expected_type=type_hints["thread_pool_force_merge_size"])
            check_type(argname="argument thread_pool_get_queue_size", value=thread_pool_get_queue_size, expected_type=type_hints["thread_pool_get_queue_size"])
            check_type(argname="argument thread_pool_get_size", value=thread_pool_get_size, expected_type=type_hints["thread_pool_get_size"])
            check_type(argname="argument thread_pool_search_queue_size", value=thread_pool_search_queue_size, expected_type=type_hints["thread_pool_search_queue_size"])
            check_type(argname="argument thread_pool_search_size", value=thread_pool_search_size, expected_type=type_hints["thread_pool_search_size"])
            check_type(argname="argument thread_pool_search_throttled_queue_size", value=thread_pool_search_throttled_queue_size, expected_type=type_hints["thread_pool_search_throttled_queue_size"])
            check_type(argname="argument thread_pool_search_throttled_size", value=thread_pool_search_throttled_size, expected_type=type_hints["thread_pool_search_throttled_size"])
            check_type(argname="argument thread_pool_write_queue_size", value=thread_pool_write_queue_size, expected_type=type_hints["thread_pool_write_queue_size"])
            check_type(argname="argument thread_pool_write_size", value=thread_pool_write_size, expected_type=type_hints["thread_pool_write_size"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action_auto_create_index_enabled is not None:
            self._values["action_auto_create_index_enabled"] = action_auto_create_index_enabled
        if action_destructive_requires_name is not None:
            self._values["action_destructive_requires_name"] = action_destructive_requires_name
        if auth_failure_listeners is not None:
            self._values["auth_failure_listeners"] = auth_failure_listeners
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if cluster_max_shards_per_node is not None:
            self._values["cluster_max_shards_per_node"] = cluster_max_shards_per_node
        if cluster_routing_allocation_node_concurrent_recoveries is not None:
            self._values["cluster_routing_allocation_node_concurrent_recoveries"] = cluster_routing_allocation_node_concurrent_recoveries
        if custom_domain is not None:
            self._values["custom_domain"] = custom_domain
        if email_sender_name is not None:
            self._values["email_sender_name"] = email_sender_name
        if email_sender_password is not None:
            self._values["email_sender_password"] = email_sender_password
        if email_sender_username is not None:
            self._values["email_sender_username"] = email_sender_username
        if enable_security_audit is not None:
            self._values["enable_security_audit"] = enable_security_audit
        if http_max_content_length is not None:
            self._values["http_max_content_length"] = http_max_content_length
        if http_max_header_size is not None:
            self._values["http_max_header_size"] = http_max_header_size
        if http_max_initial_line_length is not None:
            self._values["http_max_initial_line_length"] = http_max_initial_line_length
        if index_patterns is not None:
            self._values["index_patterns"] = index_patterns
        if index_template is not None:
            self._values["index_template"] = index_template
        if indices_fielddata_cache_size is not None:
            self._values["indices_fielddata_cache_size"] = indices_fielddata_cache_size
        if indices_memory_index_buffer_size is not None:
            self._values["indices_memory_index_buffer_size"] = indices_memory_index_buffer_size
        if indices_memory_max_index_buffer_size is not None:
            self._values["indices_memory_max_index_buffer_size"] = indices_memory_max_index_buffer_size
        if indices_memory_min_index_buffer_size is not None:
            self._values["indices_memory_min_index_buffer_size"] = indices_memory_min_index_buffer_size
        if indices_queries_cache_size is not None:
            self._values["indices_queries_cache_size"] = indices_queries_cache_size
        if indices_query_bool_max_clause_count is not None:
            self._values["indices_query_bool_max_clause_count"] = indices_query_bool_max_clause_count
        if indices_recovery_max_bytes_per_sec is not None:
            self._values["indices_recovery_max_bytes_per_sec"] = indices_recovery_max_bytes_per_sec
        if indices_recovery_max_concurrent_file_chunks is not None:
            self._values["indices_recovery_max_concurrent_file_chunks"] = indices_recovery_max_concurrent_file_chunks
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if ism_enabled is not None:
            self._values["ism_enabled"] = ism_enabled
        if ism_history_enabled is not None:
            self._values["ism_history_enabled"] = ism_history_enabled
        if ism_history_max_age is not None:
            self._values["ism_history_max_age"] = ism_history_max_age
        if ism_history_max_docs is not None:
            self._values["ism_history_max_docs"] = ism_history_max_docs
        if ism_history_rollover_check_period is not None:
            self._values["ism_history_rollover_check_period"] = ism_history_rollover_check_period
        if ism_history_rollover_retention_period is not None:
            self._values["ism_history_rollover_retention_period"] = ism_history_rollover_retention_period
        if keep_index_refresh_interval is not None:
            self._values["keep_index_refresh_interval"] = keep_index_refresh_interval
        if knn_memory_circuit_breaker_enabled is not None:
            self._values["knn_memory_circuit_breaker_enabled"] = knn_memory_circuit_breaker_enabled
        if knn_memory_circuit_breaker_limit is not None:
            self._values["knn_memory_circuit_breaker_limit"] = knn_memory_circuit_breaker_limit
        if openid is not None:
            self._values["openid"] = openid
        if opensearch_dashboards is not None:
            self._values["opensearch_dashboards"] = opensearch_dashboards
        if override_main_response_version is not None:
            self._values["override_main_response_version"] = override_main_response_version
        if plugins_alerting_filter_by_backend_roles is not None:
            self._values["plugins_alerting_filter_by_backend_roles"] = plugins_alerting_filter_by_backend_roles
        if public_access is not None:
            self._values["public_access"] = public_access
        if reindex_remote_whitelist is not None:
            self._values["reindex_remote_whitelist"] = reindex_remote_whitelist
        if saml is not None:
            self._values["saml"] = saml
        if script_max_compilations_rate is not None:
            self._values["script_max_compilations_rate"] = script_max_compilations_rate
        if search_max_buckets is not None:
            self._values["search_max_buckets"] = search_max_buckets
        if service_log is not None:
            self._values["service_log"] = service_log
        if thread_pool_analyze_queue_size is not None:
            self._values["thread_pool_analyze_queue_size"] = thread_pool_analyze_queue_size
        if thread_pool_analyze_size is not None:
            self._values["thread_pool_analyze_size"] = thread_pool_analyze_size
        if thread_pool_force_merge_size is not None:
            self._values["thread_pool_force_merge_size"] = thread_pool_force_merge_size
        if thread_pool_get_queue_size is not None:
            self._values["thread_pool_get_queue_size"] = thread_pool_get_queue_size
        if thread_pool_get_size is not None:
            self._values["thread_pool_get_size"] = thread_pool_get_size
        if thread_pool_search_queue_size is not None:
            self._values["thread_pool_search_queue_size"] = thread_pool_search_queue_size
        if thread_pool_search_size is not None:
            self._values["thread_pool_search_size"] = thread_pool_search_size
        if thread_pool_search_throttled_queue_size is not None:
            self._values["thread_pool_search_throttled_queue_size"] = thread_pool_search_throttled_queue_size
        if thread_pool_search_throttled_size is not None:
            self._values["thread_pool_search_throttled_size"] = thread_pool_search_throttled_size
        if thread_pool_write_queue_size is not None:
            self._values["thread_pool_write_queue_size"] = thread_pool_write_queue_size
        if thread_pool_write_size is not None:
            self._values["thread_pool_write_size"] = thread_pool_write_size
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        '''
        result = self._values.get("action_auto_create_index_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def action_destructive_requires_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require explicit index names when deleting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        '''
        result = self._values.get("action_destructive_requires_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auth_failure_listeners(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListeners"]:
        '''auth_failure_listeners block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        '''
        result = self._values.get("auth_failure_listeners")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListeners"], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_max_shards_per_node(self) -> typing.Optional[jsii.Number]:
        '''Controls the number of shards allowed in the cluster per data node.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        '''
        result = self._values.get("cluster_max_shards_per_node")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Concurrent incoming/outgoing shard recoveries per node.

        How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        '''
        result = self._values.get("cluster_routing_allocation_node_concurrent_recoveries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_domain(self) -> typing.Optional[builtins.str]:
        '''Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        '''
        result = self._values.get("custom_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_name(self) -> typing.Optional[builtins.str]:
        '''Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore.

        This should be identical to the Sender name defined in Opensearch dashboards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        '''
        result = self._values.get("email_sender_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_password(self) -> typing.Optional[builtins.str]:
        '''Sender password for Opensearch alerts to authenticate with SMTP server.

        Sender password for Opensearch alerts to authenticate with SMTP server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        '''
        result = self._values.get("email_sender_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_username(self) -> typing.Optional[builtins.str]:
        '''Sender username for Opensearch alerts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        '''
        result = self._values.get("email_sender_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_security_audit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable security audit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        '''
        result = self._values.get("enable_security_audit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http_max_content_length(self) -> typing.Optional[jsii.Number]:
        '''Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        '''
        result = self._values.get("http_max_content_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_header_size(self) -> typing.Optional[jsii.Number]:
        '''The max size of allowed headers, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        '''
        result = self._values.get("http_max_header_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_initial_line_length(self) -> typing.Optional[jsii.Number]:
        '''The max length of an HTTP URL, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        '''
        result = self._values.get("http_max_initial_line_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def index_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Index patterns.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        '''
        result = self._values.get("index_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def index_template(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesIndexTemplate"]:
        '''index_template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        '''
        result = self._values.get("index_template")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesIndexTemplate"], result)

    @builtins.property
    def indices_fielddata_cache_size(self) -> typing.Optional[jsii.Number]:
        '''Relative amount.

        Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        '''
        result = self._values.get("indices_fielddata_cache_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Percentage value.

        Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        '''
        result = self._values.get("indices_memory_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_max_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Absolute value.

        Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        '''
        result = self._values.get("indices_memory_max_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_min_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Absolute value.

        Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        '''
        result = self._values.get("indices_memory_min_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_queries_cache_size(self) -> typing.Optional[jsii.Number]:
        '''Percentage value.

        Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        '''
        result = self._values.get("indices_queries_cache_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_query_bool_max_clause_count(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of clauses Lucene BooleanQuery can have.

        The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        '''
        result = self._values.get("indices_query_bool_max_clause_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_bytes_per_sec(self) -> typing.Optional[jsii.Number]:
        '''Limits total inbound and outbound recovery traffic for each node.

        Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        '''
        result = self._values.get("indices_recovery_max_bytes_per_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_concurrent_file_chunks(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Number of file chunks sent in parallel for each recovery. Defaults to 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        '''
        result = self._values.get("indices_recovery_max_concurrent_file_chunks")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ism_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether ISM is enabled or not.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        '''
        result = self._values.get("ism_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        '''
        result = self._values.get("ism_history_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_max_age(self) -> typing.Optional[jsii.Number]:
        '''The maximum age before rolling over the audit history index in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        '''
        result = self._values.get("ism_history_max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_max_docs(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of documents before rolling over the audit history index.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        '''
        result = self._values.get("ism_history_max_docs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_check_period(self) -> typing.Optional[jsii.Number]:
        '''The time between rollover checks for the audit history index in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        '''
        result = self._values.get("ism_history_rollover_check_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_retention_period(self) -> typing.Optional[jsii.Number]:
        '''How long audit history indices are kept in days.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        '''
        result = self._values.get("ism_history_rollover_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keep_index_refresh_interval(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        '''
        result = self._values.get("keep_index_refresh_interval")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def knn_memory_circuit_breaker_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable KNN memory circuit breaker. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        '''
        result = self._values.get("knn_memory_circuit_breaker_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def knn_memory_circuit_breaker_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        '''
        result = self._values.get("knn_memory_circuit_breaker_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def openid(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesOpenid"]:
        '''openid block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        '''
        result = self._values.get("openid")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesOpenid"], result)

    @builtins.property
    def opensearch_dashboards(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesOpensearchDashboards"]:
        '''opensearch_dashboards block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        '''
        result = self._values.get("opensearch_dashboards")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesOpensearchDashboards"], result)

    @builtins.property
    def override_main_response_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        '''
        result = self._values.get("override_main_response_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def plugins_alerting_filter_by_backend_roles(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        '''
        result = self._values.get("plugins_alerting_filter_by_backend_roles")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public Access. Allow access to the service from the public Internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def reindex_remote_whitelist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        '''
        result = self._values.get("reindex_remote_whitelist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def saml(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"]:
        '''saml block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        '''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"], result)

    @builtins.property
    def script_max_compilations_rate(self) -> typing.Optional[builtins.str]:
        '''Script max compilation rate - circuit breaker to prevent/minimize OOMs.

        Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        '''
        result = self._values.get("script_max_compilations_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search_max_buckets(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of aggregation buckets allowed in a single response.

        OpenSearch default value is used when this is not defined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        '''
        result = self._values.get("search_max_buckets")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Service logging. Store logs for the service so that they are available in the HTTP API and console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        '''
        result = self._values.get("service_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def thread_pool_analyze_queue_size(self) -> typing.Optional[jsii.Number]:
        '''analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        '''
        result = self._values.get("thread_pool_analyze_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_analyze_size(self) -> typing.Optional[jsii.Number]:
        '''analyze thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        '''
        result = self._values.get("thread_pool_analyze_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_force_merge_size(self) -> typing.Optional[jsii.Number]:
        '''force_merge thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        '''
        result = self._values.get("thread_pool_force_merge_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_queue_size(self) -> typing.Optional[jsii.Number]:
        '''get thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        '''
        result = self._values.get("thread_pool_get_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_size(self) -> typing.Optional[jsii.Number]:
        '''get thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        '''
        result = self._values.get("thread_pool_get_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_queue_size(self) -> typing.Optional[jsii.Number]:
        '''search thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        '''
        result = self._values.get("thread_pool_search_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_size(self) -> typing.Optional[jsii.Number]:
        '''search thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        '''
        result = self._values.get("thread_pool_search_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_queue_size(self) -> typing.Optional[jsii.Number]:
        '''search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        '''
        result = self._values.get("thread_pool_search_throttled_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_size(self) -> typing.Optional[jsii.Number]:
        '''search_throttled thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        '''
        result = self._values.get("thread_pool_search_throttled_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_queue_size(self) -> typing.Optional[jsii.Number]:
        '''write thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        '''
        result = self._values.get("thread_pool_write_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_size(self) -> typing.Optional[jsii.Number]:
        '''write thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        '''
        result = self._values.get("thread_pool_write_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''OpenSearch major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListeners",
    jsii_struct_bases=[],
    name_mapping={
        "internal_authentication_backend_limiting": "internalAuthenticationBackendLimiting",
        "ip_rate_limiting": "ipRateLimiting",
    },
)
class ManagedDatabaseOpensearchPropertiesAuthFailureListeners:
    def __init__(
        self,
        *,
        internal_authentication_backend_limiting: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_rate_limiting: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internal_authentication_backend_limiting: internal_authentication_backend_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        :param ip_rate_limiting: ip_rate_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_rate_limiting ManagedDatabaseOpensearch#ip_rate_limiting}
        '''
        if isinstance(internal_authentication_backend_limiting, dict):
            internal_authentication_backend_limiting = ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(**internal_authentication_backend_limiting)
        if isinstance(ip_rate_limiting, dict):
            ip_rate_limiting = ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting(**ip_rate_limiting)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6df7d26b0238df040ca0d1aeaa659a956825f3139e84791c48d896c03493a3)
            check_type(argname="argument internal_authentication_backend_limiting", value=internal_authentication_backend_limiting, expected_type=type_hints["internal_authentication_backend_limiting"])
            check_type(argname="argument ip_rate_limiting", value=ip_rate_limiting, expected_type=type_hints["ip_rate_limiting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if internal_authentication_backend_limiting is not None:
            self._values["internal_authentication_backend_limiting"] = internal_authentication_backend_limiting
        if ip_rate_limiting is not None:
            self._values["ip_rate_limiting"] = ip_rate_limiting

    @builtins.property
    def internal_authentication_backend_limiting(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting"]:
        '''internal_authentication_backend_limiting block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        '''
        result = self._values.get("internal_authentication_backend_limiting")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting"], result)

    @builtins.property
    def ip_rate_limiting(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting"]:
        '''ip_rate_limiting block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_rate_limiting ManagedDatabaseOpensearch#ip_rate_limiting}
        '''
        result = self._values.get("ip_rate_limiting")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesAuthFailureListeners(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_tries": "allowedTries",
        "authentication_backend": "authenticationBackend",
        "block_expiry_seconds": "blockExpirySeconds",
        "max_blocked_clients": "maxBlockedClients",
        "max_tracked_clients": "maxTrackedClients",
        "time_window_seconds": "timeWindowSeconds",
        "type": "type",
    },
)
class ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting:
    def __init__(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        authentication_backend: typing.Optional[builtins.str] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param authentication_backend: The internal backend. Enter ``internal``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9435799fa69802c70cf9a1ec8b896a69d09f232c4c49f47ff2d40e3e18c2343b)
            check_type(argname="argument allowed_tries", value=allowed_tries, expected_type=type_hints["allowed_tries"])
            check_type(argname="argument authentication_backend", value=authentication_backend, expected_type=type_hints["authentication_backend"])
            check_type(argname="argument block_expiry_seconds", value=block_expiry_seconds, expected_type=type_hints["block_expiry_seconds"])
            check_type(argname="argument max_blocked_clients", value=max_blocked_clients, expected_type=type_hints["max_blocked_clients"])
            check_type(argname="argument max_tracked_clients", value=max_tracked_clients, expected_type=type_hints["max_tracked_clients"])
            check_type(argname="argument time_window_seconds", value=time_window_seconds, expected_type=type_hints["time_window_seconds"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_tries is not None:
            self._values["allowed_tries"] = allowed_tries
        if authentication_backend is not None:
            self._values["authentication_backend"] = authentication_backend
        if block_expiry_seconds is not None:
            self._values["block_expiry_seconds"] = block_expiry_seconds
        if max_blocked_clients is not None:
            self._values["max_blocked_clients"] = max_blocked_clients
        if max_tracked_clients is not None:
            self._values["max_tracked_clients"] = max_tracked_clients
        if time_window_seconds is not None:
            self._values["time_window_seconds"] = time_window_seconds
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def allowed_tries(self) -> typing.Optional[jsii.Number]:
        '''The number of login attempts allowed before login is blocked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        '''
        result = self._values.get("allowed_tries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def authentication_backend(self) -> typing.Optional[builtins.str]:
        '''The internal backend. Enter ``internal``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        '''
        result = self._values.get("authentication_backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_expiry_seconds(self) -> typing.Optional[jsii.Number]:
        '''The duration of time that login remains blocked after a failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        '''
        result = self._values.get("block_expiry_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_blocked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of blocked IP addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        '''
        result = self._values.get("max_blocked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_tracked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tracked IP addresses that have failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        '''
        result = self._values.get("max_tracked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_window_seconds(self) -> typing.Optional[jsii.Number]:
        '''The window of time in which the value for ``allowed_tries`` is enforced.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        '''
        result = self._values.get("time_window_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of rate limiting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__99749960614da71029c64a8b792ced764cdf27a0962414854d04210bb1ae2acd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedTries")
    def reset_allowed_tries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedTries", []))

    @jsii.member(jsii_name="resetAuthenticationBackend")
    def reset_authentication_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationBackend", []))

    @jsii.member(jsii_name="resetBlockExpirySeconds")
    def reset_block_expiry_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockExpirySeconds", []))

    @jsii.member(jsii_name="resetMaxBlockedClients")
    def reset_max_blocked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBlockedClients", []))

    @jsii.member(jsii_name="resetMaxTrackedClients")
    def reset_max_tracked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTrackedClients", []))

    @jsii.member(jsii_name="resetTimeWindowSeconds")
    def reset_time_window_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindowSeconds", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedTriesInput")
    def allowed_tries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allowedTriesInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationBackendInput")
    def authentication_backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationBackendInput"))

    @builtins.property
    @jsii.member(jsii_name="blockExpirySecondsInput")
    def block_expiry_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockExpirySecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClientsInput")
    def max_blocked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBlockedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClientsInput")
    def max_tracked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTrackedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowSecondsInput")
    def time_window_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeWindowSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedTries")
    def allowed_tries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allowedTries"))

    @allowed_tries.setter
    def allowed_tries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cd07b462b44760122178a37243eab5bce0c8902d031193949d1c2e9b173cef8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedTries", value)

    @builtins.property
    @jsii.member(jsii_name="authenticationBackend")
    def authentication_backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationBackend"))

    @authentication_backend.setter
    def authentication_backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c97e2414097315d7ba383e33a5dc0b3357f770c50a34a76b2c31435635e7ede3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBackend", value)

    @builtins.property
    @jsii.member(jsii_name="blockExpirySeconds")
    def block_expiry_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "blockExpirySeconds"))

    @block_expiry_seconds.setter
    def block_expiry_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8966671b06b0cb755048c486e085213fe8c8f8eb3434ef864493050eac73e366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockExpirySeconds", value)

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClients")
    def max_blocked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBlockedClients"))

    @max_blocked_clients.setter
    def max_blocked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0448c88bdb2b3db18c1c620763fad421cf34b0e345fd1cfeb0590539f6fbf08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBlockedClients", value)

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClients")
    def max_tracked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTrackedClients"))

    @max_tracked_clients.setter
    def max_tracked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0911499e4bd4d24c4fe2f3f9f3cd2c527bcfc391686536082567743a93ddb080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTrackedClients", value)

    @builtins.property
    @jsii.member(jsii_name="timeWindowSeconds")
    def time_window_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeWindowSeconds"))

    @time_window_seconds.setter
    def time_window_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe8bc44df1f627c05d7f87446be558febc5900c4b151855121869224bf95cf0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindowSeconds", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524634a3518077cc05d7163bab39b1e5c92bf78a97db61a74f322b581322cf1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827575e00c1eaecf35d33d817e94688109afe1fa2f142d1614bdc103f0e670cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_tries": "allowedTries",
        "block_expiry_seconds": "blockExpirySeconds",
        "max_blocked_clients": "maxBlockedClients",
        "max_tracked_clients": "maxTrackedClients",
        "time_window_seconds": "timeWindowSeconds",
        "type": "type",
    },
)
class ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting:
    def __init__(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5db9a9b662c1875b357f7775838b53f73b8761e853ab7dcb83a11de164679ed)
            check_type(argname="argument allowed_tries", value=allowed_tries, expected_type=type_hints["allowed_tries"])
            check_type(argname="argument block_expiry_seconds", value=block_expiry_seconds, expected_type=type_hints["block_expiry_seconds"])
            check_type(argname="argument max_blocked_clients", value=max_blocked_clients, expected_type=type_hints["max_blocked_clients"])
            check_type(argname="argument max_tracked_clients", value=max_tracked_clients, expected_type=type_hints["max_tracked_clients"])
            check_type(argname="argument time_window_seconds", value=time_window_seconds, expected_type=type_hints["time_window_seconds"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_tries is not None:
            self._values["allowed_tries"] = allowed_tries
        if block_expiry_seconds is not None:
            self._values["block_expiry_seconds"] = block_expiry_seconds
        if max_blocked_clients is not None:
            self._values["max_blocked_clients"] = max_blocked_clients
        if max_tracked_clients is not None:
            self._values["max_tracked_clients"] = max_tracked_clients
        if time_window_seconds is not None:
            self._values["time_window_seconds"] = time_window_seconds
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def allowed_tries(self) -> typing.Optional[jsii.Number]:
        '''The number of login attempts allowed before login is blocked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        '''
        result = self._values.get("allowed_tries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def block_expiry_seconds(self) -> typing.Optional[jsii.Number]:
        '''The duration of time that login remains blocked after a failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        '''
        result = self._values.get("block_expiry_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_blocked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of blocked IP addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        '''
        result = self._values.get("max_blocked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_tracked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tracked IP addresses that have failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        '''
        result = self._values.get("max_tracked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_window_seconds(self) -> typing.Optional[jsii.Number]:
        '''The window of time in which the value for ``allowed_tries`` is enforced.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        '''
        result = self._values.get("time_window_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of rate limiting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimitingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimitingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df0dba312f1a2c76f9255f0fb1b72fdd897dd359e92e7fee72537a28938c2369)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedTries")
    def reset_allowed_tries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedTries", []))

    @jsii.member(jsii_name="resetBlockExpirySeconds")
    def reset_block_expiry_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockExpirySeconds", []))

    @jsii.member(jsii_name="resetMaxBlockedClients")
    def reset_max_blocked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBlockedClients", []))

    @jsii.member(jsii_name="resetMaxTrackedClients")
    def reset_max_tracked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTrackedClients", []))

    @jsii.member(jsii_name="resetTimeWindowSeconds")
    def reset_time_window_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindowSeconds", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedTriesInput")
    def allowed_tries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allowedTriesInput"))

    @builtins.property
    @jsii.member(jsii_name="blockExpirySecondsInput")
    def block_expiry_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockExpirySecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClientsInput")
    def max_blocked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBlockedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClientsInput")
    def max_tracked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTrackedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowSecondsInput")
    def time_window_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeWindowSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedTries")
    def allowed_tries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allowedTries"))

    @allowed_tries.setter
    def allowed_tries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a52325c7915c1071265cd271c6e2f866e2f0ce00345d8db1c6d902a32520ac80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedTries", value)

    @builtins.property
    @jsii.member(jsii_name="blockExpirySeconds")
    def block_expiry_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "blockExpirySeconds"))

    @block_expiry_seconds.setter
    def block_expiry_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__796cfb9b8ca3c4b64710f662f3a18c90b5abb9244a2c08ec7526efc53ad12398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockExpirySeconds", value)

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClients")
    def max_blocked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBlockedClients"))

    @max_blocked_clients.setter
    def max_blocked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36141edd7d0702451532584374c7e02d7e170845dba24908b10804342a66cb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBlockedClients", value)

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClients")
    def max_tracked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTrackedClients"))

    @max_tracked_clients.setter
    def max_tracked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75f35635faa2fd5412b51dd24e58a0f75af6fe4a6d7bd85aa47f50293b747393)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTrackedClients", value)

    @builtins.property
    @jsii.member(jsii_name="timeWindowSeconds")
    def time_window_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeWindowSeconds"))

    @time_window_seconds.setter
    def time_window_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49cb110d320044051afe929f4bbb907778c0b28bcee7254ec289105ecb4c8d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindowSeconds", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6125754efc2d7bc2455a168b273c3b22cb9b8affc7cc5fdc05d86063ac71d005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47577b728e4aa4b36a74aee8a3bfb879d6b64f924bb185d4d8859a624071560c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bb457d048cf3243bf7b1785b9d3430cd66839097d28517e5978e7c0ff727704)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInternalAuthenticationBackendLimiting")
    def put_internal_authentication_backend_limiting(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        authentication_backend: typing.Optional[builtins.str] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param authentication_backend: The internal backend. Enter ``internal``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        value = ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(
            allowed_tries=allowed_tries,
            authentication_backend=authentication_backend,
            block_expiry_seconds=block_expiry_seconds,
            max_blocked_clients=max_blocked_clients,
            max_tracked_clients=max_tracked_clients,
            time_window_seconds=time_window_seconds,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putInternalAuthenticationBackendLimiting", [value]))

    @jsii.member(jsii_name="putIpRateLimiting")
    def put_ip_rate_limiting(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        value = ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting(
            allowed_tries=allowed_tries,
            block_expiry_seconds=block_expiry_seconds,
            max_blocked_clients=max_blocked_clients,
            max_tracked_clients=max_tracked_clients,
            time_window_seconds=time_window_seconds,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putIpRateLimiting", [value]))

    @jsii.member(jsii_name="resetInternalAuthenticationBackendLimiting")
    def reset_internal_authentication_backend_limiting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalAuthenticationBackendLimiting", []))

    @jsii.member(jsii_name="resetIpRateLimiting")
    def reset_ip_rate_limiting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpRateLimiting", []))

    @builtins.property
    @jsii.member(jsii_name="internalAuthenticationBackendLimiting")
    def internal_authentication_backend_limiting(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference, jsii.get(self, "internalAuthenticationBackendLimiting"))

    @builtins.property
    @jsii.member(jsii_name="ipRateLimiting")
    def ip_rate_limiting(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimitingOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimitingOutputReference, jsii.get(self, "ipRateLimiting"))

    @builtins.property
    @jsii.member(jsii_name="internalAuthenticationBackendLimitingInput")
    def internal_authentication_backend_limiting_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting], jsii.get(self, "internalAuthenticationBackendLimitingInput"))

    @builtins.property
    @jsii.member(jsii_name="ipRateLimitingInput")
    def ip_rate_limiting_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting], jsii.get(self, "ipRateLimitingInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9841d9da7d378cfedc4cae10fb3cd1f05a03ee8993362ac50891755214ff708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "mapping_nested_objects_limit": "mappingNestedObjectsLimit",
        "number_of_replicas": "numberOfReplicas",
        "number_of_shards": "numberOfShards",
    },
)
class ManagedDatabaseOpensearchPropertiesIndexTemplate:
    def __init__(
        self,
        *,
        mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
        number_of_replicas: typing.Optional[jsii.Number] = None,
        number_of_shards: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mapping_nested_objects_limit: index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        :param number_of_replicas: The number of replicas each primary shard has. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        :param number_of_shards: The number of primary shards that an index should have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__091ebe000c02a1dbf5147d4d6e2e100eaaea7c918311494e9ada1f78674a89e3)
            check_type(argname="argument mapping_nested_objects_limit", value=mapping_nested_objects_limit, expected_type=type_hints["mapping_nested_objects_limit"])
            check_type(argname="argument number_of_replicas", value=number_of_replicas, expected_type=type_hints["number_of_replicas"])
            check_type(argname="argument number_of_shards", value=number_of_shards, expected_type=type_hints["number_of_shards"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mapping_nested_objects_limit is not None:
            self._values["mapping_nested_objects_limit"] = mapping_nested_objects_limit
        if number_of_replicas is not None:
            self._values["number_of_replicas"] = number_of_replicas
        if number_of_shards is not None:
            self._values["number_of_shards"] = number_of_shards

    @builtins.property
    def mapping_nested_objects_limit(self) -> typing.Optional[jsii.Number]:
        '''index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        '''
        result = self._values.get("mapping_nested_objects_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_replicas(self) -> typing.Optional[jsii.Number]:
        '''The number of replicas each primary shard has.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        '''
        result = self._values.get("number_of_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_shards(self) -> typing.Optional[jsii.Number]:
        '''The number of primary shards that an index should have.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        result = self._values.get("number_of_shards")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesIndexTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__80db9e8d6bfffacb73cb1f100468062628a53d92d9dbb8e053b4f82011e7088d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMappingNestedObjectsLimit")
    def reset_mapping_nested_objects_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMappingNestedObjectsLimit", []))

    @jsii.member(jsii_name="resetNumberOfReplicas")
    def reset_number_of_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfReplicas", []))

    @jsii.member(jsii_name="resetNumberOfShards")
    def reset_number_of_shards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfShards", []))

    @builtins.property
    @jsii.member(jsii_name="mappingNestedObjectsLimitInput")
    def mapping_nested_objects_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mappingNestedObjectsLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfReplicasInput")
    def number_of_replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfReplicasInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfShardsInput")
    def number_of_shards_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfShardsInput"))

    @builtins.property
    @jsii.member(jsii_name="mappingNestedObjectsLimit")
    def mapping_nested_objects_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mappingNestedObjectsLimit"))

    @mapping_nested_objects_limit.setter
    def mapping_nested_objects_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9714605aa57197fc59ce6c9f2e363fa7bb5622ebb54ee19ef15e7857c251df97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mappingNestedObjectsLimit", value)

    @builtins.property
    @jsii.member(jsii_name="numberOfReplicas")
    def number_of_replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfReplicas"))

    @number_of_replicas.setter
    def number_of_replicas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99332dc6f1965838c8118775aebd1f65b3d65be63b32bd7b866815bfbe8a3d51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfReplicas", value)

    @builtins.property
    @jsii.member(jsii_name="numberOfShards")
    def number_of_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfShards"))

    @number_of_shards.setter
    def number_of_shards(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c96ce7acc291c5aaec545dcee6fda8acc85e631432e5aa54434163de41edffe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfShards", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16dccbd691a6d637fb1fe54be64ca4acfec30c4e49cc9add81d99b41d2f5ea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpenid",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "connect_url": "connectUrl",
        "enabled": "enabled",
        "header": "header",
        "jwt_header": "jwtHeader",
        "jwt_url_parameter": "jwtUrlParameter",
        "refresh_rate_limit_count": "refreshRateLimitCount",
        "refresh_rate_limit_time_window_ms": "refreshRateLimitTimeWindowMs",
        "roles_key": "rolesKey",
        "scope": "scope",
        "subject_key": "subjectKey",
    },
)
class ManagedDatabaseOpensearchPropertiesOpenid:
    def __init__(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        connect_url: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        header: typing.Optional[builtins.str] = None,
        jwt_header: typing.Optional[builtins.str] = None,
        jwt_url_parameter: typing.Optional[builtins.str] = None,
        refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
        refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
        roles_key: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        :param client_secret: The client secret of the OpenID Connect. The client secret of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        :param connect_url: OpenID Connect metadata/configuration URL. The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        :param enabled: Enable or disable OpenSearch OpenID Connect authentication. Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param header: HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        :param jwt_header: The HTTP header that stores the token. The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        :param jwt_url_parameter: URL JWT token. If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        :param refresh_rate_limit_count: The maximum number of unknown key IDs in the time frame. The maximum number of unknown key IDs in the time frame. Default is 10. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        :param refresh_rate_limit_time_window_ms: The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        :param roles_key: The key in the JSON payload that stores the user’s roles. The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param scope: The scope of the identity token issued by the IdP. The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        :param subject_key: The key in the JSON payload that stores the user’s name. The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c0a3837cca5d07ee0176744b302d89e862a8b39ec6f0e2781b94b27f82af92)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument connect_url", value=connect_url, expected_type=type_hints["connect_url"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument jwt_header", value=jwt_header, expected_type=type_hints["jwt_header"])
            check_type(argname="argument jwt_url_parameter", value=jwt_url_parameter, expected_type=type_hints["jwt_url_parameter"])
            check_type(argname="argument refresh_rate_limit_count", value=refresh_rate_limit_count, expected_type=type_hints["refresh_rate_limit_count"])
            check_type(argname="argument refresh_rate_limit_time_window_ms", value=refresh_rate_limit_time_window_ms, expected_type=type_hints["refresh_rate_limit_time_window_ms"])
            check_type(argname="argument roles_key", value=roles_key, expected_type=type_hints["roles_key"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument subject_key", value=subject_key, expected_type=type_hints["subject_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if connect_url is not None:
            self._values["connect_url"] = connect_url
        if enabled is not None:
            self._values["enabled"] = enabled
        if header is not None:
            self._values["header"] = header
        if jwt_header is not None:
            self._values["jwt_header"] = jwt_header
        if jwt_url_parameter is not None:
            self._values["jwt_url_parameter"] = jwt_url_parameter
        if refresh_rate_limit_count is not None:
            self._values["refresh_rate_limit_count"] = refresh_rate_limit_count
        if refresh_rate_limit_time_window_ms is not None:
            self._values["refresh_rate_limit_time_window_ms"] = refresh_rate_limit_time_window_ms
        if roles_key is not None:
            self._values["roles_key"] = roles_key
        if scope is not None:
            self._values["scope"] = scope
        if subject_key is not None:
            self._values["subject_key"] = subject_key

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''The client secret of the OpenID Connect.

        The client secret of the OpenID Connect client configured in your IdP. Required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_url(self) -> typing.Optional[builtins.str]:
        '''OpenID Connect metadata/configuration URL.

        The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        '''
        result = self._values.get("connect_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch OpenID Connect authentication.

        Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def header(self) -> typing.Optional[builtins.str]:
        '''HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_header(self) -> typing.Optional[builtins.str]:
        '''The HTTP header that stores the token.

        The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        '''
        result = self._values.get("jwt_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_url_parameter(self) -> typing.Optional[builtins.str]:
        '''URL JWT token.

        If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        '''
        result = self._values.get("jwt_url_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_rate_limit_count(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of unknown key IDs in the time frame.

        The maximum number of unknown key IDs in the time frame. Default is 10. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        '''
        result = self._values.get("refresh_rate_limit_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def refresh_rate_limit_time_window_ms(self) -> typing.Optional[jsii.Number]:
        '''The time frame to use when checking the maximum number of unknown key IDs, in milliseconds.

        The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        '''
        result = self._values.get("refresh_rate_limit_time_window_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def roles_key(self) -> typing.Optional[builtins.str]:
        '''The key in the JSON payload that stores the user’s roles.

        The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        '''
        result = self._values.get("roles_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The scope of the identity token issued by the IdP.

        The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_key(self) -> typing.Optional[builtins.str]:
        '''The key in the JSON payload that stores the user’s name.

        The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        result = self._values.get("subject_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesOpenid(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesOpenidOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpenidOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2d1f05510b29d1e71f1ca51d5c296f3e66e489b68f141c0cb11fdf1089181a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetConnectUrl")
    def reset_connect_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectUrl", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetJwtHeader")
    def reset_jwt_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtHeader", []))

    @jsii.member(jsii_name="resetJwtUrlParameter")
    def reset_jwt_url_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtUrlParameter", []))

    @jsii.member(jsii_name="resetRefreshRateLimitCount")
    def reset_refresh_rate_limit_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshRateLimitCount", []))

    @jsii.member(jsii_name="resetRefreshRateLimitTimeWindowMs")
    def reset_refresh_rate_limit_time_window_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshRateLimitTimeWindowMs", []))

    @jsii.member(jsii_name="resetRolesKey")
    def reset_roles_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRolesKey", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

    @jsii.member(jsii_name="resetSubjectKey")
    def reset_subject_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectKey", []))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="connectUrlInput")
    def connect_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtHeaderInput")
    def jwt_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtUrlParameterInput")
    def jwt_url_parameter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtUrlParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitCountInput")
    def refresh_rate_limit_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshRateLimitCountInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitTimeWindowMsInput")
    def refresh_rate_limit_time_window_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshRateLimitTimeWindowMsInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesKeyInput")
    def roles_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rolesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectKeyInput")
    def subject_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa7261a89918dbfb9f50fa9dfae42227fb7412ceab80b7a8b982e2db47c07f02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699da58a3d40107a39d2119729ecbb14aaeff7207705a003c1357d842dc1ea48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="connectUrl")
    def connect_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectUrl"))

    @connect_url.setter
    def connect_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e90a34de40e81274f86eb828ee2b88ed8bbf5ef9e0814fc5f8f5486266be9f71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectUrl", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__00987cb520a1f1a0ea820dcfda52b67895e8d1b1f813300c1440cda0e27f1139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "header"))

    @header.setter
    def header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f9bf04854b7ff6094b1426fa9ec13b04739a31f9863bbbcb53eec2116cdbafc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "header", value)

    @builtins.property
    @jsii.member(jsii_name="jwtHeader")
    def jwt_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwtHeader"))

    @jwt_header.setter
    def jwt_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3decaf18072bd601d7198339380575ee2070f319206ca5742d1ca686393ca774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtHeader", value)

    @builtins.property
    @jsii.member(jsii_name="jwtUrlParameter")
    def jwt_url_parameter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwtUrlParameter"))

    @jwt_url_parameter.setter
    def jwt_url_parameter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9e04be6387363a6fb27928afe6e422ba0787832599b73c3798bded4bbbeaa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtUrlParameter", value)

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitCount")
    def refresh_rate_limit_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshRateLimitCount"))

    @refresh_rate_limit_count.setter
    def refresh_rate_limit_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f125200f527ffbb5e3cbc957fcf1254d0f49b7bc28cc54daf6b9114de79a999e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshRateLimitCount", value)

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitTimeWindowMs")
    def refresh_rate_limit_time_window_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshRateLimitTimeWindowMs"))

    @refresh_rate_limit_time_window_ms.setter
    def refresh_rate_limit_time_window_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58b2b1fdb72bb20c47f3f3da6e88eb14a71ad8399fe12a1f255177f46d28dfec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshRateLimitTimeWindowMs", value)

    @builtins.property
    @jsii.member(jsii_name="rolesKey")
    def roles_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rolesKey"))

    @roles_key.setter
    def roles_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e308c3ca6ee25c5414c9c3b5b5add06951a6a78c7783c033bd7d39f387c28a89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolesKey", value)

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5cedd7c2ad307531bb92f92c1dc2b02714e9a953ac794098ab5e972da769fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value)

    @builtins.property
    @jsii.member(jsii_name="subjectKey")
    def subject_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subjectKey"))

    @subject_key.setter
    def subject_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2e8077939eb6e386d424c3909093dc0fd2f5595c3f150af06f218539a68a082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a06c0f82afb429010a7bf11d739c6e615490b1602601145c983041209f49f06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpensearchDashboards",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "max_old_space_size": "maxOldSpaceSize",
        "opensearch_request_timeout": "opensearchRequestTimeout",
    },
)
class ManagedDatabaseOpensearchPropertiesOpensearchDashboards:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_old_space_size: typing.Optional[jsii.Number] = None,
        opensearch_request_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param max_old_space_size: Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use. This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        :param opensearch_request_timeout: Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c02ebecf926c4894c4481fd34c44a4f69278e1e4c9c78e3ec30f9d08a36971c3)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument max_old_space_size", value=max_old_space_size, expected_type=type_hints["max_old_space_size"])
            check_type(argname="argument opensearch_request_timeout", value=opensearch_request_timeout, expected_type=type_hints["opensearch_request_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if max_old_space_size is not None:
            self._values["max_old_space_size"] = max_old_space_size
        if opensearch_request_timeout is not None:
            self._values["opensearch_request_timeout"] = opensearch_request_timeout

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch Dashboards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_old_space_size(self) -> typing.Optional[jsii.Number]:
        '''Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use.

        This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        '''
        result = self._values.get("max_old_space_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def opensearch_request_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        result = self._values.get("opensearch_request_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesOpensearchDashboards(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46269da753bb4825eb2d2eb52d1679232eb04b442c74f7cafddf4cf14945aec0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetMaxOldSpaceSize")
    def reset_max_old_space_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOldSpaceSize", []))

    @jsii.member(jsii_name="resetOpensearchRequestTimeout")
    def reset_opensearch_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpensearchRequestTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOldSpaceSizeInput")
    def max_old_space_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOldSpaceSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="opensearchRequestTimeoutInput")
    def opensearch_request_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "opensearchRequestTimeoutInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e1019ad4a6f0e57b8f798e7a399405937723d4cbd1b0109900787a017b35b7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="maxOldSpaceSize")
    def max_old_space_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOldSpaceSize"))

    @max_old_space_size.setter
    def max_old_space_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15484f5f1d02602bd803336a02543fef580fed4327eeca3c32e0e19880cb41a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOldSpaceSize", value)

    @builtins.property
    @jsii.member(jsii_name="opensearchRequestTimeout")
    def opensearch_request_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "opensearchRequestTimeout"))

    @opensearch_request_timeout.setter
    def opensearch_request_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f2bb44168338b5f62f27d6c68aa85795f001b64ec8ee27ccfd05945977e24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opensearchRequestTimeout", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__642b1eeba71d0c8859ae09897efcd46c46a7f3266c413676870e000d26269bab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ManagedDatabaseOpensearchPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAuthFailureListeners")
    def put_auth_failure_listeners(
        self,
        *,
        internal_authentication_backend_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_rate_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internal_authentication_backend_limiting: internal_authentication_backend_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        :param ip_rate_limiting: ip_rate_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#ip_rate_limiting ManagedDatabaseOpensearch#ip_rate_limiting}
        '''
        value = ManagedDatabaseOpensearchPropertiesAuthFailureListeners(
            internal_authentication_backend_limiting=internal_authentication_backend_limiting,
            ip_rate_limiting=ip_rate_limiting,
        )

        return typing.cast(None, jsii.invoke(self, "putAuthFailureListeners", [value]))

    @jsii.member(jsii_name="putIndexTemplate")
    def put_index_template(
        self,
        *,
        mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
        number_of_replicas: typing.Optional[jsii.Number] = None,
        number_of_shards: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mapping_nested_objects_limit: index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        :param number_of_replicas: The number of replicas each primary shard has. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        :param number_of_shards: The number of primary shards that an index should have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        value = ManagedDatabaseOpensearchPropertiesIndexTemplate(
            mapping_nested_objects_limit=mapping_nested_objects_limit,
            number_of_replicas=number_of_replicas,
            number_of_shards=number_of_shards,
        )

        return typing.cast(None, jsii.invoke(self, "putIndexTemplate", [value]))

    @jsii.member(jsii_name="putOpenid")
    def put_openid(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        connect_url: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        header: typing.Optional[builtins.str] = None,
        jwt_header: typing.Optional[builtins.str] = None,
        jwt_url_parameter: typing.Optional[builtins.str] = None,
        refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
        refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
        roles_key: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        :param client_secret: The client secret of the OpenID Connect. The client secret of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        :param connect_url: OpenID Connect metadata/configuration URL. The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        :param enabled: Enable or disable OpenSearch OpenID Connect authentication. Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param header: HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        :param jwt_header: The HTTP header that stores the token. The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        :param jwt_url_parameter: URL JWT token. If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        :param refresh_rate_limit_count: The maximum number of unknown key IDs in the time frame. The maximum number of unknown key IDs in the time frame. Default is 10. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        :param refresh_rate_limit_time_window_ms: The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        :param roles_key: The key in the JSON payload that stores the user’s roles. The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param scope: The scope of the identity token issued by the IdP. The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        :param subject_key: The key in the JSON payload that stores the user’s name. The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        value = ManagedDatabaseOpensearchPropertiesOpenid(
            client_id=client_id,
            client_secret=client_secret,
            connect_url=connect_url,
            enabled=enabled,
            header=header,
            jwt_header=jwt_header,
            jwt_url_parameter=jwt_url_parameter,
            refresh_rate_limit_count=refresh_rate_limit_count,
            refresh_rate_limit_time_window_ms=refresh_rate_limit_time_window_ms,
            roles_key=roles_key,
            scope=scope,
            subject_key=subject_key,
        )

        return typing.cast(None, jsii.invoke(self, "putOpenid", [value]))

    @jsii.member(jsii_name="putOpensearchDashboards")
    def put_opensearch_dashboards(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_old_space_size: typing.Optional[jsii.Number] = None,
        opensearch_request_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param max_old_space_size: Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use. This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        :param opensearch_request_timeout: Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        value = ManagedDatabaseOpensearchPropertiesOpensearchDashboards(
            enabled=enabled,
            max_old_space_size=max_old_space_size,
            opensearch_request_timeout=opensearch_request_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putOpensearchDashboards", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        idp_entity_id: typing.Optional[builtins.str] = None,
        idp_metadata_url: typing.Optional[builtins.str] = None,
        idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
        roles_key: typing.Optional[builtins.str] = None,
        sp_entity_id: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch SAML authentication. Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param idp_entity_id: Identity Provider Entity ID. The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        :param idp_metadata_url: Identity Provider (IdP) SAML metadata URL. The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        :param idp_pemtrustedcas_content: PEM-encoded root CA Content for SAML IdP server verification. This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        :param roles_key: SAML response role attribute. Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param sp_entity_id: Service Provider Entity ID. The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        :param subject_key: SAML response subject attribute. Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        value = ManagedDatabaseOpensearchPropertiesSaml(
            enabled=enabled,
            idp_entity_id=idp_entity_id,
            idp_metadata_url=idp_metadata_url,
            idp_pemtrustedcas_content=idp_pemtrustedcas_content,
            roles_key=roles_key,
            sp_entity_id=sp_entity_id,
            subject_key=subject_key,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="resetActionAutoCreateIndexEnabled")
    def reset_action_auto_create_index_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionAutoCreateIndexEnabled", []))

    @jsii.member(jsii_name="resetActionDestructiveRequiresName")
    def reset_action_destructive_requires_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionDestructiveRequiresName", []))

    @jsii.member(jsii_name="resetAuthFailureListeners")
    def reset_auth_failure_listeners(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthFailureListeners", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetClusterMaxShardsPerNode")
    def reset_cluster_max_shards_per_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMaxShardsPerNode", []))

    @jsii.member(jsii_name="resetClusterRoutingAllocationNodeConcurrentRecoveries")
    def reset_cluster_routing_allocation_node_concurrent_recoveries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRoutingAllocationNodeConcurrentRecoveries", []))

    @jsii.member(jsii_name="resetCustomDomain")
    def reset_custom_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDomain", []))

    @jsii.member(jsii_name="resetEmailSenderName")
    def reset_email_sender_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderName", []))

    @jsii.member(jsii_name="resetEmailSenderPassword")
    def reset_email_sender_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderPassword", []))

    @jsii.member(jsii_name="resetEmailSenderUsername")
    def reset_email_sender_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderUsername", []))

    @jsii.member(jsii_name="resetEnableSecurityAudit")
    def reset_enable_security_audit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSecurityAudit", []))

    @jsii.member(jsii_name="resetHttpMaxContentLength")
    def reset_http_max_content_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxContentLength", []))

    @jsii.member(jsii_name="resetHttpMaxHeaderSize")
    def reset_http_max_header_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxHeaderSize", []))

    @jsii.member(jsii_name="resetHttpMaxInitialLineLength")
    def reset_http_max_initial_line_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxInitialLineLength", []))

    @jsii.member(jsii_name="resetIndexPatterns")
    def reset_index_patterns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexPatterns", []))

    @jsii.member(jsii_name="resetIndexTemplate")
    def reset_index_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexTemplate", []))

    @jsii.member(jsii_name="resetIndicesFielddataCacheSize")
    def reset_indices_fielddata_cache_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesFielddataCacheSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryIndexBufferSize")
    def reset_indices_memory_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryMaxIndexBufferSize")
    def reset_indices_memory_max_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMaxIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryMinIndexBufferSize")
    def reset_indices_memory_min_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMinIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesQueriesCacheSize")
    def reset_indices_queries_cache_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueriesCacheSize", []))

    @jsii.member(jsii_name="resetIndicesQueryBoolMaxClauseCount")
    def reset_indices_query_bool_max_clause_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueryBoolMaxClauseCount", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxBytesPerSec")
    def reset_indices_recovery_max_bytes_per_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxBytesPerSec", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxConcurrentFileChunks")
    def reset_indices_recovery_max_concurrent_file_chunks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxConcurrentFileChunks", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetIsmEnabled")
    def reset_ism_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryEnabled")
    def reset_ism_history_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxAge")
    def reset_ism_history_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxAge", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxDocs")
    def reset_ism_history_max_docs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxDocs", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverCheckPeriod")
    def reset_ism_history_rollover_check_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverCheckPeriod", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverRetentionPeriod")
    def reset_ism_history_rollover_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverRetentionPeriod", []))

    @jsii.member(jsii_name="resetKeepIndexRefreshInterval")
    def reset_keep_index_refresh_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepIndexRefreshInterval", []))

    @jsii.member(jsii_name="resetKnnMemoryCircuitBreakerEnabled")
    def reset_knn_memory_circuit_breaker_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnnMemoryCircuitBreakerEnabled", []))

    @jsii.member(jsii_name="resetKnnMemoryCircuitBreakerLimit")
    def reset_knn_memory_circuit_breaker_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnnMemoryCircuitBreakerLimit", []))

    @jsii.member(jsii_name="resetOpenid")
    def reset_openid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenid", []))

    @jsii.member(jsii_name="resetOpensearchDashboards")
    def reset_opensearch_dashboards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpensearchDashboards", []))

    @jsii.member(jsii_name="resetOverrideMainResponseVersion")
    def reset_override_main_response_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideMainResponseVersion", []))

    @jsii.member(jsii_name="resetPluginsAlertingFilterByBackendRoles")
    def reset_plugins_alerting_filter_by_backend_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginsAlertingFilterByBackendRoles", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetReindexRemoteWhitelist")
    def reset_reindex_remote_whitelist(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReindexRemoteWhitelist", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

    @jsii.member(jsii_name="resetScriptMaxCompilationsRate")
    def reset_script_max_compilations_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptMaxCompilationsRate", []))

    @jsii.member(jsii_name="resetSearchMaxBuckets")
    def reset_search_max_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchMaxBuckets", []))

    @jsii.member(jsii_name="resetServiceLog")
    def reset_service_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceLog", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeQueueSize")
    def reset_thread_pool_analyze_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeSize")
    def reset_thread_pool_analyze_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeSize", []))

    @jsii.member(jsii_name="resetThreadPoolForceMergeSize")
    def reset_thread_pool_force_merge_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolForceMergeSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetQueueSize")
    def reset_thread_pool_get_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetSize")
    def reset_thread_pool_get_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchQueueSize")
    def reset_thread_pool_search_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchSize")
    def reset_thread_pool_search_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledQueueSize")
    def reset_thread_pool_search_throttled_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledSize")
    def reset_thread_pool_search_throttled_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteQueueSize")
    def reset_thread_pool_write_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteSize")
    def reset_thread_pool_write_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteSize", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="authFailureListeners")
    def auth_failure_listeners(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference, jsii.get(self, "authFailureListeners"))

    @builtins.property
    @jsii.member(jsii_name="indexTemplate")
    def index_template(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference, jsii.get(self, "indexTemplate"))

    @builtins.property
    @jsii.member(jsii_name="openid")
    def openid(self) -> ManagedDatabaseOpensearchPropertiesOpenidOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesOpenidOutputReference, jsii.get(self, "openid"))

    @builtins.property
    @jsii.member(jsii_name="opensearchDashboards")
    def opensearch_dashboards(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference, jsii.get(self, "opensearchDashboards"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ManagedDatabaseOpensearchPropertiesSamlOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabledInput")
    def action_auto_create_index_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionAutoCreateIndexEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresNameInput")
    def action_destructive_requires_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionDestructiveRequiresNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authFailureListenersInput")
    def auth_failure_listeners_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners], jsii.get(self, "authFailureListenersInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNodeInput")
    def cluster_max_shards_per_node_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterMaxShardsPerNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveriesInput")
    def cluster_routing_allocation_node_concurrent_recoveries_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveriesInput"))

    @builtins.property
    @jsii.member(jsii_name="customDomainInput")
    def custom_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderNameInput")
    def email_sender_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderNameInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderPasswordInput")
    def email_sender_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderUsernameInput")
    def email_sender_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAuditInput")
    def enable_security_audit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSecurityAuditInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLengthInput")
    def http_max_content_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxContentLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSizeInput")
    def http_max_header_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxHeaderSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLengthInput")
    def http_max_initial_line_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxInitialLineLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="indexPatternsInput")
    def index_patterns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "indexPatternsInput"))

    @builtins.property
    @jsii.member(jsii_name="indexTemplateInput")
    def index_template_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate], jsii.get(self, "indexTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSizeInput")
    def indices_fielddata_cache_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesFielddataCacheSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSizeInput")
    def indices_memory_index_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSizeInput")
    def indices_memory_max_index_buffer_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMaxIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSizeInput")
    def indices_memory_min_index_buffer_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMinIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSizeInput")
    def indices_queries_cache_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueriesCacheSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCountInput")
    def indices_query_bool_max_clause_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueryBoolMaxClauseCountInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxBytesPerSecInput")
    def indices_recovery_max_bytes_per_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxBytesPerSecInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunksInput")
    def indices_recovery_max_concurrent_file_chunks_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxConcurrentFileChunksInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="ismEnabledInput")
    def ism_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabledInput")
    def ism_history_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismHistoryEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAgeInput")
    def ism_history_max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocsInput")
    def ism_history_max_docs_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxDocsInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriodInput")
    def ism_history_rollover_check_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverCheckPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriodInput")
    def ism_history_rollover_retention_period_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverRetentionPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="keepIndexRefreshIntervalInput")
    def keep_index_refresh_interval_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepIndexRefreshIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerEnabledInput")
    def knn_memory_circuit_breaker_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "knnMemoryCircuitBreakerEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerLimitInput")
    def knn_memory_circuit_breaker_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "knnMemoryCircuitBreakerLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="openidInput")
    def openid_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid], jsii.get(self, "openidInput"))

    @builtins.property
    @jsii.member(jsii_name="opensearchDashboardsInput")
    def opensearch_dashboards_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards], jsii.get(self, "opensearchDashboardsInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersionInput")
    def override_main_response_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "overrideMainResponseVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRolesInput")
    def plugins_alerting_filter_by_backend_roles_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pluginsAlertingFilterByBackendRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelistInput")
    def reindex_remote_whitelist_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "reindexRemoteWhitelistInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRateInput")
    def script_max_compilations_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptMaxCompilationsRateInput"))

    @builtins.property
    @jsii.member(jsii_name="searchMaxBucketsInput")
    def search_max_buckets_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "searchMaxBucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceLogInput")
    def service_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serviceLogInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSizeInput")
    def thread_pool_analyze_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSizeInput")
    def thread_pool_analyze_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSizeInput")
    def thread_pool_force_merge_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolForceMergeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSizeInput")
    def thread_pool_get_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSizeInput")
    def thread_pool_get_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSizeInput")
    def thread_pool_search_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSizeInput")
    def thread_pool_search_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSizeInput")
    def thread_pool_search_throttled_queue_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSizeInput")
    def thread_pool_search_throttled_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSizeInput")
    def thread_pool_write_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSizeInput")
    def thread_pool_write_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabled")
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionAutoCreateIndexEnabled"))

    @action_auto_create_index_enabled.setter
    def action_auto_create_index_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f95b49868c2e1ec7544168878febf8b6696a57483b6f51fa99aa0925cb16697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionAutoCreateIndexEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresName")
    def action_destructive_requires_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionDestructiveRequiresName"))

    @action_destructive_requires_name.setter
    def action_destructive_requires_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e457da88de09c5532affd0a501416c99106d06518e52d2a5677fde17f0757fd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionDestructiveRequiresName", value)

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilter")
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automaticUtilityNetworkIpFilter"))

    @automatic_utility_network_ip_filter.setter
    def automatic_utility_network_ip_filter(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value)

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNode")
    def cluster_max_shards_per_node(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterMaxShardsPerNode"))

    @cluster_max_shards_per_node.setter
    def cluster_max_shards_per_node(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3368d21a864593369d41fa3b6553ceda22676badcd2892eab312b0d160b62f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterMaxShardsPerNode", value)

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveries")
    def cluster_routing_allocation_node_concurrent_recoveries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveries"))

    @cluster_routing_allocation_node_concurrent_recoveries.setter
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
        value: jsii.Number,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0448eb5420a97c55d350dfab1c0a0d3e8726d744e441f4fde0d412dd04f31497)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterRoutingAllocationNodeConcurrentRecoveries", value)

    @builtins.property
    @jsii.member(jsii_name="customDomain")
    def custom_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDomain"))

    @custom_domain.setter
    def custom_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07a65588eb7a4625bdb8375e03839f7d7ccf09b91bb824e3b31afc1c39388598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDomain", value)

    @builtins.property
    @jsii.member(jsii_name="emailSenderName")
    def email_sender_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderName"))

    @email_sender_name.setter
    def email_sender_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d549945259dc5d5d9b2134e2a3264e213b749e4f33396341c391bf22353af47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderName", value)

    @builtins.property
    @jsii.member(jsii_name="emailSenderPassword")
    def email_sender_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderPassword"))

    @email_sender_password.setter
    def email_sender_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b181764d7b414fdac2022d32d63421fe71b45025faa283d816517a60e472c6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderPassword", value)

    @builtins.property
    @jsii.member(jsii_name="emailSenderUsername")
    def email_sender_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderUsername"))

    @email_sender_username.setter
    def email_sender_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__342025668ce074acad3db548bb92de3b1aaf5e8a569bcdf9f928e24b1dce9c38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderUsername", value)

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAudit")
    def enable_security_audit(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSecurityAudit"))

    @enable_security_audit.setter
    def enable_security_audit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff78f5e79729d11ea6229a93440341c6dfb144628a5a51a9a4f0c10d9983ef87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecurityAudit", value)

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLength")
    def http_max_content_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxContentLength"))

    @http_max_content_length.setter
    def http_max_content_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09252df690d98b7364842578b7664698629fd55a3c709cedfc832883b986e93c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxContentLength", value)

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSize")
    def http_max_header_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxHeaderSize"))

    @http_max_header_size.setter
    def http_max_header_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f23654b3c993300d915c75caa2b551bed505e332e601ae1d318b6f7c22eec1d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxHeaderSize", value)

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLength")
    def http_max_initial_line_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxInitialLineLength"))

    @http_max_initial_line_length.setter
    def http_max_initial_line_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71c76b5482471bb5f448beac6f8f0c45b923c1fc3debd34a481229204fb99ca1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxInitialLineLength", value)

    @builtins.property
    @jsii.member(jsii_name="indexPatterns")
    def index_patterns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "indexPatterns"))

    @index_patterns.setter
    def index_patterns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c6add2afd8176cf65752af011b26017ea4026647b88807e7848153aa808c88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexPatterns", value)

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSize")
    def indices_fielddata_cache_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesFielddataCacheSize"))

    @indices_fielddata_cache_size.setter
    def indices_fielddata_cache_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa13f532a0cc1807de56948d104831eea41a922b8cccfa4dbededb8056bc2101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesFielddataCacheSize", value)

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSize")
    def indices_memory_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryIndexBufferSize"))

    @indices_memory_index_buffer_size.setter
    def indices_memory_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a8c26865a2a9328ae331cb883300375516826479d56c03bbe3b173701034e54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryIndexBufferSize", value)

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSize")
    def indices_memory_max_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMaxIndexBufferSize"))

    @indices_memory_max_index_buffer_size.setter
    def indices_memory_max_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__066a7c0b66ed33e66af285d45119ca128f33fc0bcbfe01b3a35bcf4a21b2f488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMaxIndexBufferSize", value)

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSize")
    def indices_memory_min_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMinIndexBufferSize"))

    @indices_memory_min_index_buffer_size.setter
    def indices_memory_min_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a2af7f1a139f5456a3f2eeca4e3867ef26c85c7ba01267c4acf3fcbe89eb9ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMinIndexBufferSize", value)

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSize")
    def indices_queries_cache_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueriesCacheSize"))

    @indices_queries_cache_size.setter
    def indices_queries_cache_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db0348b951ec966edf534f9e879d0bee16e2d53cf2ff85b213c5dc31755a5aa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueriesCacheSize", value)

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCount")
    def indices_query_bool_max_clause_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueryBoolMaxClauseCount"))

    @indices_query_bool_max_clause_count.setter
    def indices_query_bool_max_clause_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363b9a51b2ae015e89e6f9beea8cd6589eb3254d3e9a8ed918d7f8a059b00488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueryBoolMaxClauseCount", value)

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxBytesPerSec")
    def indices_recovery_max_bytes_per_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxBytesPerSec"))

    @indices_recovery_max_bytes_per_sec.setter
    def indices_recovery_max_bytes_per_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d857a7fba85a3ccba0ca1972bd70c474b4d2fea3a6f3b935d6bf1920e087333b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxBytesPerSec", value)

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunks")
    def indices_recovery_max_concurrent_file_chunks(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxConcurrentFileChunks"))

    @indices_recovery_max_concurrent_file_chunks.setter
    def indices_recovery_max_concurrent_file_chunks(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511b44be808d39b3f5d61cf6c8b691b91fc91afda941c083d2ba0fee3107aece)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxConcurrentFileChunks", value)

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value)

    @builtins.property
    @jsii.member(jsii_name="ismEnabled")
    def ism_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismEnabled"))

    @ism_enabled.setter
    def ism_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dde81e5014559bf79849f8363ddaef4d0fe9186cec22e692bf4b937ed30bf89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabled")
    def ism_history_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismHistoryEnabled"))

    @ism_history_enabled.setter
    def ism_history_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d409d4c93acb6dbddf3ea05ef640c8c083700c01312ae34de3c952a00933254)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAge")
    def ism_history_max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxAge"))

    @ism_history_max_age.setter
    def ism_history_max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd4ad47529fc509173d3341762a0c1b8ce4e8d381578c9db0e9588fb5bd11e69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxAge", value)

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocs")
    def ism_history_max_docs(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxDocs"))

    @ism_history_max_docs.setter
    def ism_history_max_docs(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7988c725f00df71948d13e3c7a67c37939bfbdf59be068727cb0f1b6fe5c0b49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxDocs", value)

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriod")
    def ism_history_rollover_check_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverCheckPeriod"))

    @ism_history_rollover_check_period.setter
    def ism_history_rollover_check_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6579b40abc92fc56536665342c25021b16220f2bd87f5e74283f08704cfe6abb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverCheckPeriod", value)

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriod")
    def ism_history_rollover_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverRetentionPeriod"))

    @ism_history_rollover_retention_period.setter
    def ism_history_rollover_retention_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb9144f9ff10e0665d17f1dab9d796961a1f30385738d5fac5012ac1e12d73c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverRetentionPeriod", value)

    @builtins.property
    @jsii.member(jsii_name="keepIndexRefreshInterval")
    def keep_index_refresh_interval(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepIndexRefreshInterval"))

    @keep_index_refresh_interval.setter
    def keep_index_refresh_interval(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__475c7d9ea1f132358fd8876b5bce857503b42c419cf0edd268668a9396576272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepIndexRefreshInterval", value)

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerEnabled")
    def knn_memory_circuit_breaker_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "knnMemoryCircuitBreakerEnabled"))

    @knn_memory_circuit_breaker_enabled.setter
    def knn_memory_circuit_breaker_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79543fe9d0bb8f49f03afaba4905ee1fc1c6bb8081b72a0ce935e05db800d019)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knnMemoryCircuitBreakerEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerLimit")
    def knn_memory_circuit_breaker_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "knnMemoryCircuitBreakerLimit"))

    @knn_memory_circuit_breaker_limit.setter
    def knn_memory_circuit_breaker_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d77bb2fd42dcdec4347d48a5fd38597e5fd7a8bd356c3b4be6c11e5d48f49eca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knnMemoryCircuitBreakerLimit", value)

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersion")
    def override_main_response_version(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "overrideMainResponseVersion"))

    @override_main_response_version.setter
    def override_main_response_version(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6c829c8246593bfea087d544de86602dcf1c3f827bb531e45fb456fd06b41a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideMainResponseVersion", value)

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRoles")
    def plugins_alerting_filter_by_backend_roles(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pluginsAlertingFilterByBackendRoles"))

    @plugins_alerting_filter_by_backend_roles.setter
    def plugins_alerting_filter_by_backend_roles(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc45a3b1177a7e18688e7dbcc3ca2d16552505944545509d4b5a66e029a2afd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginsAlertingFilterByBackendRoles", value)

    @builtins.property
    @jsii.member(jsii_name="publicAccess")
    def public_access(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "publicAccess"))

    @public_access.setter
    def public_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicAccess", value)

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelist")
    def reindex_remote_whitelist(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "reindexRemoteWhitelist"))

    @reindex_remote_whitelist.setter
    def reindex_remote_whitelist(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00d138e917ad74a2a8c043cd17d158357905bed6e23949c38b382514204bd13f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reindexRemoteWhitelist", value)

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRate")
    def script_max_compilations_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptMaxCompilationsRate"))

    @script_max_compilations_rate.setter
    def script_max_compilations_rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de1660d38a30c3e2336ab4a8e93e4240c706d088fe2d0a466fcf8ddb12386f10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptMaxCompilationsRate", value)

    @builtins.property
    @jsii.member(jsii_name="searchMaxBuckets")
    def search_max_buckets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "searchMaxBuckets"))

    @search_max_buckets.setter
    def search_max_buckets(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a031050a9e6f8a40b6fff2021afeb15b5ad471d2a0772dbf01945324746e1c4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "searchMaxBuckets", value)

    @builtins.property
    @jsii.member(jsii_name="serviceLog")
    def service_log(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serviceLog"))

    @service_log.setter
    def service_log(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8c3fe099944b1f56a32bc799baf5e867e2cdf4f7b392cab873ea63870b05066)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceLog", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSize")
    def thread_pool_analyze_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeQueueSize"))

    @thread_pool_analyze_queue_size.setter
    def thread_pool_analyze_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33a0fbdcfa0733a258cb09a7fec41cb87f369bb39dbe3d656186fee89fbfc0bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeQueueSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSize")
    def thread_pool_analyze_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeSize"))

    @thread_pool_analyze_size.setter
    def thread_pool_analyze_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284920e01c9389024b53f7d33cd743be906b889c598a63b378523ba83bee9165)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSize")
    def thread_pool_force_merge_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolForceMergeSize"))

    @thread_pool_force_merge_size.setter
    def thread_pool_force_merge_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c49306bfe5e374f98a93dbde13277a081ed1c78280db967a45ae6d9aa463d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolForceMergeSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSize")
    def thread_pool_get_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetQueueSize"))

    @thread_pool_get_queue_size.setter
    def thread_pool_get_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda12e0a9350f10cc58dfb4503e36cef9ef54b196da052bb6919eefe1b4ddcd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetQueueSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSize")
    def thread_pool_get_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetSize"))

    @thread_pool_get_size.setter
    def thread_pool_get_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ae2dc20f615630e63a616e89cc1fe881038dcec11ccd7feda4fbca3d504561)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSize")
    def thread_pool_search_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchQueueSize"))

    @thread_pool_search_queue_size.setter
    def thread_pool_search_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c716fb378769c59082cbd6ef2a98ab923895cd0d2907af1ddaa2e22ac6933d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchQueueSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSize")
    def thread_pool_search_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchSize"))

    @thread_pool_search_size.setter
    def thread_pool_search_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2acbdf19ba9102e2e1937592da16eb85b1c62ad65e6149f8c3d0a3bace050cad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSize")
    def thread_pool_search_throttled_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledQueueSize"))

    @thread_pool_search_throttled_queue_size.setter
    def thread_pool_search_throttled_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6c4b8bedfe2dab74ff62e0b49929a7e29387a92737dd6be0d7da5dc2e30672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledQueueSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSize")
    def thread_pool_search_throttled_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledSize"))

    @thread_pool_search_throttled_size.setter
    def thread_pool_search_throttled_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be01f06da11cbc0ff664fcfcdfa1885cecb35a2be2f64f3db7a6c82afe350d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSize")
    def thread_pool_write_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteQueueSize"))

    @thread_pool_write_queue_size.setter
    def thread_pool_write_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363d81378d4e1cd4dd5f6d81316deffe21c2b78c49e33a7350d70233def65523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteQueueSize", value)

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSize")
    def thread_pool_write_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteSize"))

    @thread_pool_write_size.setter
    def thread_pool_write_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b53d519b13b838c462a6929cbcbecaa084a53ce80392b3cfe23e41033ed0af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteSize", value)

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSaml",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "idp_entity_id": "idpEntityId",
        "idp_metadata_url": "idpMetadataUrl",
        "idp_pemtrustedcas_content": "idpPemtrustedcasContent",
        "roles_key": "rolesKey",
        "sp_entity_id": "spEntityId",
        "subject_key": "subjectKey",
    },
)
class ManagedDatabaseOpensearchPropertiesSaml:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        idp_entity_id: typing.Optional[builtins.str] = None,
        idp_metadata_url: typing.Optional[builtins.str] = None,
        idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
        roles_key: typing.Optional[builtins.str] = None,
        sp_entity_id: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch SAML authentication. Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param idp_entity_id: Identity Provider Entity ID. The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        :param idp_metadata_url: Identity Provider (IdP) SAML metadata URL. The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        :param idp_pemtrustedcas_content: PEM-encoded root CA Content for SAML IdP server verification. This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        :param roles_key: SAML response role attribute. Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param sp_entity_id: Service Provider Entity ID. The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        :param subject_key: SAML response subject attribute. Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b14f1e134e8d0c84c0341fd18666aca6f997046615ab52f5363393b4ab7937e)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument idp_entity_id", value=idp_entity_id, expected_type=type_hints["idp_entity_id"])
            check_type(argname="argument idp_metadata_url", value=idp_metadata_url, expected_type=type_hints["idp_metadata_url"])
            check_type(argname="argument idp_pemtrustedcas_content", value=idp_pemtrustedcas_content, expected_type=type_hints["idp_pemtrustedcas_content"])
            check_type(argname="argument roles_key", value=roles_key, expected_type=type_hints["roles_key"])
            check_type(argname="argument sp_entity_id", value=sp_entity_id, expected_type=type_hints["sp_entity_id"])
            check_type(argname="argument subject_key", value=subject_key, expected_type=type_hints["subject_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if idp_entity_id is not None:
            self._values["idp_entity_id"] = idp_entity_id
        if idp_metadata_url is not None:
            self._values["idp_metadata_url"] = idp_metadata_url
        if idp_pemtrustedcas_content is not None:
            self._values["idp_pemtrustedcas_content"] = idp_pemtrustedcas_content
        if roles_key is not None:
            self._values["roles_key"] = roles_key
        if sp_entity_id is not None:
            self._values["sp_entity_id"] = sp_entity_id
        if subject_key is not None:
            self._values["subject_key"] = subject_key

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch SAML authentication.

        Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def idp_entity_id(self) -> typing.Optional[builtins.str]:
        '''Identity Provider Entity ID.

        The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        '''
        result = self._values.get("idp_entity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_metadata_url(self) -> typing.Optional[builtins.str]:
        '''Identity Provider (IdP) SAML metadata URL.

        The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        '''
        result = self._values.get("idp_metadata_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_pemtrustedcas_content(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded root CA Content for SAML IdP server verification.

        This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        '''
        result = self._values.get("idp_pemtrustedcas_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def roles_key(self) -> typing.Optional[builtins.str]:
        '''SAML response role attribute.

        Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        '''
        result = self._values.get("roles_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sp_entity_id(self) -> typing.Optional[builtins.str]:
        '''Service Provider Entity ID.

        The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        '''
        result = self._values.get("sp_entity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_key(self) -> typing.Optional[builtins.str]:
        '''SAML response subject attribute.

        Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.8.0/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        result = self._values.get("subject_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9006f804233866e0bcbcabfee80e240d58ca3aa0b270b35fca9e093fc1e32e9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIdpEntityId")
    def reset_idp_entity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpEntityId", []))

    @jsii.member(jsii_name="resetIdpMetadataUrl")
    def reset_idp_metadata_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpMetadataUrl", []))

    @jsii.member(jsii_name="resetIdpPemtrustedcasContent")
    def reset_idp_pemtrustedcas_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpPemtrustedcasContent", []))

    @jsii.member(jsii_name="resetRolesKey")
    def reset_roles_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRolesKey", []))

    @jsii.member(jsii_name="resetSpEntityId")
    def reset_sp_entity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpEntityId", []))

    @jsii.member(jsii_name="resetSubjectKey")
    def reset_subject_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectKey", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idpEntityIdInput")
    def idp_entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpEntityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrlInput")
    def idp_metadata_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpMetadataUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idpPemtrustedcasContentInput")
    def idp_pemtrustedcas_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpPemtrustedcasContentInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesKeyInput")
    def roles_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rolesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="spEntityIdInput")
    def sp_entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spEntityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectKeyInput")
    def subject_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectKeyInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__4d469be80b1364917873721e8af88e7062483a039aaed7718db029f5ca170884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property
    @jsii.member(jsii_name="idpEntityId")
    def idp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpEntityId"))

    @idp_entity_id.setter
    def idp_entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__814ab6ecf48749b6d62f26b6567d61ef65ea0bfbbe19f1358d51810029ef998a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpEntityId", value)

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrl")
    def idp_metadata_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpMetadataUrl"))

    @idp_metadata_url.setter
    def idp_metadata_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__608b37237be872718973058fb30455a02be360f5053c70e96510693c9b9244d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpMetadataUrl", value)

    @builtins.property
    @jsii.member(jsii_name="idpPemtrustedcasContent")
    def idp_pemtrustedcas_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpPemtrustedcasContent"))

    @idp_pemtrustedcas_content.setter
    def idp_pemtrustedcas_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1814aa90ebfc251af6c91642e42ce08a47300fa1a8e3cacf378c1886d789c06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpPemtrustedcasContent", value)

    @builtins.property
    @jsii.member(jsii_name="rolesKey")
    def roles_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rolesKey"))

    @roles_key.setter
    def roles_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94553764dddbdb00b434cdebba04db1366d57e07aaf8f5c89ff45bf9529acbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolesKey", value)

    @builtins.property
    @jsii.member(jsii_name="spEntityId")
    def sp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spEntityId"))

    @sp_entity_id.setter
    def sp_entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf9acff0d36a02176d62a477d13b9d21e0065d4067d1da39833b3dc9b1054ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spEntityId", value)

    @builtins.property
    @jsii.member(jsii_name="subjectKey")
    def subject_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subjectKey"))

    @subject_key.setter
    def subject_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c2749a1852f09b8e903fc5f21f9fc37f4be29b4b73b365e767ca5ec1eed0097)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSaml]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3eef83ead552c9f4ef0503c6cd5db370ccfefde7338e3dca2b88ba0fdcc15ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ManagedDatabaseOpensearch",
    "ManagedDatabaseOpensearchComponents",
    "ManagedDatabaseOpensearchComponentsList",
    "ManagedDatabaseOpensearchComponentsOutputReference",
    "ManagedDatabaseOpensearchConfig",
    "ManagedDatabaseOpensearchNetwork",
    "ManagedDatabaseOpensearchNetworkList",
    "ManagedDatabaseOpensearchNetworkOutputReference",
    "ManagedDatabaseOpensearchNodeStates",
    "ManagedDatabaseOpensearchNodeStatesList",
    "ManagedDatabaseOpensearchNodeStatesOutputReference",
    "ManagedDatabaseOpensearchProperties",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListeners",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimitingOutputReference",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference",
    "ManagedDatabaseOpensearchPropertiesIndexTemplate",
    "ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference",
    "ManagedDatabaseOpensearchPropertiesOpenid",
    "ManagedDatabaseOpensearchPropertiesOpenidOutputReference",
    "ManagedDatabaseOpensearchPropertiesOpensearchDashboards",
    "ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference",
    "ManagedDatabaseOpensearchPropertiesOutputReference",
    "ManagedDatabaseOpensearchPropertiesSaml",
    "ManagedDatabaseOpensearchPropertiesSamlOutputReference",
]

publication.publish()

def _typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827b59afce111c617fb7e5a741d9b2a3004395e4c68a14fedcd8c61308c66442(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2(
    value: typing.Optional[ManagedDatabaseOpensearchComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca8408590124dd06a9281b50a661dcbdbb53334fd0cbfb3b4fed6c54dc2fd83(
    *,
    family: builtins.str,
    name: builtins.str,
    type: builtins.str,
    uuid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e329b18badd7d49b48b57bfe67898d0a24d2355460b3e92344a172ad07ecd4f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32720d726b88051a33b0a45fd56ea4118a2f932301f8c2b2a1d84423707660d7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f41e22d45dd70224aad1ec2381618b7683e3b9cbc00c500cdc37da46e33fbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517c0a72cf55cce1ae9b6342f33106b189fcd6dc12b3fb06aece1db1c9deae0b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2429cd8dff761f1e319900b52e924676682282f94ad7505ba9fe22ee0013cf20(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7988b51be371d4764a089b96fd2c9e8d7deb564eb6a899f5837744f8aa64b302(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f5527b348fe4ce85b3f81d752ce7962795f510497f946d3c9fa3d824f60542(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caf0f3fab78ca354752f87686c4ceb87c0908570faaf71c9732bf3b9af492e9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f552807981014b5ed36ce91c9049ddd1640edc60f00b525be36ade219e1114fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e73f2b43516cb1cd2e49b889369e26357e42dba138c5c96b56d7155745209e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae4a80d42aa53b63a4e5515fe09be52313dfd3d7869eb5dfcb8797bdfedaa35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17b8944baa901c2ed823dd7faa74dbd4e7cdddd833b000fe7f421fb4ee6b6a9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c(
    value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d(
    *,
    action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auth_failure_listeners: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListeners, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
    cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
    custom_domain: typing.Optional[builtins.str] = None,
    email_sender_name: typing.Optional[builtins.str] = None,
    email_sender_password: typing.Optional[builtins.str] = None,
    email_sender_username: typing.Optional[builtins.str] = None,
    enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_max_content_length: typing.Optional[jsii.Number] = None,
    http_max_header_size: typing.Optional[jsii.Number] = None,
    http_max_initial_line_length: typing.Optional[jsii.Number] = None,
    index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    index_template: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesIndexTemplate, typing.Dict[builtins.str, typing.Any]]] = None,
    indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
    indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_queries_cache_size: typing.Optional[jsii.Number] = None,
    indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
    indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
    indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_max_age: typing.Optional[jsii.Number] = None,
    ism_history_max_docs: typing.Optional[jsii.Number] = None,
    ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
    ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
    keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
    openid: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesOpenid, typing.Dict[builtins.str, typing.Any]]] = None,
    opensearch_dashboards: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesOpensearchDashboards, typing.Dict[builtins.str, typing.Any]]] = None,
    override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
    saml: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    script_max_compilations_rate: typing.Optional[builtins.str] = None,
    search_max_buckets: typing.Optional[jsii.Number] = None,
    service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
    thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_size: typing.Optional[jsii.Number] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6df7d26b0238df040ca0d1aeaa659a956825f3139e84791c48d896c03493a3(
    *,
    internal_authentication_backend_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_rate_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9435799fa69802c70cf9a1ec8b896a69d09f232c4c49f47ff2d40e3e18c2343b(
    *,
    allowed_tries: typing.Optional[jsii.Number] = None,
    authentication_backend: typing.Optional[builtins.str] = None,
    block_expiry_seconds: typing.Optional[jsii.Number] = None,
    max_blocked_clients: typing.Optional[jsii.Number] = None,
    max_tracked_clients: typing.Optional[jsii.Number] = None,
    time_window_seconds: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99749960614da71029c64a8b792ced764cdf27a0962414854d04210bb1ae2acd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd07b462b44760122178a37243eab5bce0c8902d031193949d1c2e9b173cef8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97e2414097315d7ba383e33a5dc0b3357f770c50a34a76b2c31435635e7ede3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8966671b06b0cb755048c486e085213fe8c8f8eb3434ef864493050eac73e366(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0448c88bdb2b3db18c1c620763fad421cf34b0e345fd1cfeb0590539f6fbf08(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0911499e4bd4d24c4fe2f3f9f3cd2c527bcfc391686536082567743a93ddb080(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe8bc44df1f627c05d7f87446be558febc5900c4b151855121869224bf95cf0a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524634a3518077cc05d7163bab39b1e5c92bf78a97db61a74f322b581322cf1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827575e00c1eaecf35d33d817e94688109afe1fa2f142d1614bdc103f0e670cf(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5db9a9b662c1875b357f7775838b53f73b8761e853ab7dcb83a11de164679ed(
    *,
    allowed_tries: typing.Optional[jsii.Number] = None,
    block_expiry_seconds: typing.Optional[jsii.Number] = None,
    max_blocked_clients: typing.Optional[jsii.Number] = None,
    max_tracked_clients: typing.Optional[jsii.Number] = None,
    time_window_seconds: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df0dba312f1a2c76f9255f0fb1b72fdd897dd359e92e7fee72537a28938c2369(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a52325c7915c1071265cd271c6e2f866e2f0ce00345d8db1c6d902a32520ac80(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__796cfb9b8ca3c4b64710f662f3a18c90b5abb9244a2c08ec7526efc53ad12398(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36141edd7d0702451532584374c7e02d7e170845dba24908b10804342a66cb9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75f35635faa2fd5412b51dd24e58a0f75af6fe4a6d7bd85aa47f50293b747393(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49cb110d320044051afe929f4bbb907778c0b28bcee7254ec289105ecb4c8d71(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6125754efc2d7bc2455a168b273c3b22cb9b8affc7cc5fdc05d86063ac71d005(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47577b728e4aa4b36a74aee8a3bfb879d6b64f924bb185d4d8859a624071560c(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersIpRateLimiting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bb457d048cf3243bf7b1785b9d3430cd66839097d28517e5978e7c0ff727704(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9841d9da7d378cfedc4cae10fb3cd1f05a03ee8993362ac50891755214ff708(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__091ebe000c02a1dbf5147d4d6e2e100eaaea7c918311494e9ada1f78674a89e3(
    *,
    mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
    number_of_replicas: typing.Optional[jsii.Number] = None,
    number_of_shards: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80db9e8d6bfffacb73cb1f100468062628a53d92d9dbb8e053b4f82011e7088d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9714605aa57197fc59ce6c9f2e363fa7bb5622ebb54ee19ef15e7857c251df97(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99332dc6f1965838c8118775aebd1f65b3d65be63b32bd7b866815bfbe8a3d51(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c96ce7acc291c5aaec545dcee6fda8acc85e631432e5aa54434163de41edffe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16dccbd691a6d637fb1fe54be64ca4acfec30c4e49cc9add81d99b41d2f5ea2(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c0a3837cca5d07ee0176744b302d89e862a8b39ec6f0e2781b94b27f82af92(
    *,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    connect_url: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    header: typing.Optional[builtins.str] = None,
    jwt_header: typing.Optional[builtins.str] = None,
    jwt_url_parameter: typing.Optional[builtins.str] = None,
    refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
    refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
    roles_key: typing.Optional[builtins.str] = None,
    scope: typing.Optional[builtins.str] = None,
    subject_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d1f05510b29d1e71f1ca51d5c296f3e66e489b68f141c0cb11fdf1089181a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa7261a89918dbfb9f50fa9dfae42227fb7412ceab80b7a8b982e2db47c07f02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__699da58a3d40107a39d2119729ecbb14aaeff7207705a003c1357d842dc1ea48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e90a34de40e81274f86eb828ee2b88ed8bbf5ef9e0814fc5f8f5486266be9f71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00987cb520a1f1a0ea820dcfda52b67895e8d1b1f813300c1440cda0e27f1139(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f9bf04854b7ff6094b1426fa9ec13b04739a31f9863bbbcb53eec2116cdbafc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3decaf18072bd601d7198339380575ee2070f319206ca5742d1ca686393ca774(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9e04be6387363a6fb27928afe6e422ba0787832599b73c3798bded4bbbeaa7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f125200f527ffbb5e3cbc957fcf1254d0f49b7bc28cc54daf6b9114de79a999e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b2b1fdb72bb20c47f3f3da6e88eb14a71ad8399fe12a1f255177f46d28dfec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e308c3ca6ee25c5414c9c3b5b5add06951a6a78c7783c033bd7d39f387c28a89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5cedd7c2ad307531bb92f92c1dc2b02714e9a953ac794098ab5e972da769fb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e8077939eb6e386d424c3909093dc0fd2f5595c3f150af06f218539a68a082(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a06c0f82afb429010a7bf11d739c6e615490b1602601145c983041209f49f06(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02ebecf926c4894c4481fd34c44a4f69278e1e4c9c78e3ec30f9d08a36971c3(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_old_space_size: typing.Optional[jsii.Number] = None,
    opensearch_request_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46269da753bb4825eb2d2eb52d1679232eb04b442c74f7cafddf4cf14945aec0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1019ad4a6f0e57b8f798e7a399405937723d4cbd1b0109900787a017b35b7f7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15484f5f1d02602bd803336a02543fef580fed4327eeca3c32e0e19880cb41a0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f2bb44168338b5f62f27d6c68aa85795f001b64ec8ee27ccfd05945977e24a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__642b1eeba71d0c8859ae09897efcd46c46a7f3266c413676870e000d26269bab(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f95b49868c2e1ec7544168878febf8b6696a57483b6f51fa99aa0925cb16697(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e457da88de09c5532affd0a501416c99106d06518e52d2a5677fde17f0757fd7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3368d21a864593369d41fa3b6553ceda22676badcd2892eab312b0d160b62f1a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0448eb5420a97c55d350dfab1c0a0d3e8726d744e441f4fde0d412dd04f31497(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07a65588eb7a4625bdb8375e03839f7d7ccf09b91bb824e3b31afc1c39388598(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d549945259dc5d5d9b2134e2a3264e213b749e4f33396341c391bf22353af47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b181764d7b414fdac2022d32d63421fe71b45025faa283d816517a60e472c6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__342025668ce074acad3db548bb92de3b1aaf5e8a569bcdf9f928e24b1dce9c38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff78f5e79729d11ea6229a93440341c6dfb144628a5a51a9a4f0c10d9983ef87(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09252df690d98b7364842578b7664698629fd55a3c709cedfc832883b986e93c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f23654b3c993300d915c75caa2b551bed505e332e601ae1d318b6f7c22eec1d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71c76b5482471bb5f448beac6f8f0c45b923c1fc3debd34a481229204fb99ca1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c6add2afd8176cf65752af011b26017ea4026647b88807e7848153aa808c88(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa13f532a0cc1807de56948d104831eea41a922b8cccfa4dbededb8056bc2101(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a8c26865a2a9328ae331cb883300375516826479d56c03bbe3b173701034e54(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__066a7c0b66ed33e66af285d45119ca128f33fc0bcbfe01b3a35bcf4a21b2f488(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a2af7f1a139f5456a3f2eeca4e3867ef26c85c7ba01267c4acf3fcbe89eb9ea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db0348b951ec966edf534f9e879d0bee16e2d53cf2ff85b213c5dc31755a5aa4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363b9a51b2ae015e89e6f9beea8cd6589eb3254d3e9a8ed918d7f8a059b00488(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d857a7fba85a3ccba0ca1972bd70c474b4d2fea3a6f3b935d6bf1920e087333b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511b44be808d39b3f5d61cf6c8b691b91fc91afda941c083d2ba0fee3107aece(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dde81e5014559bf79849f8363ddaef4d0fe9186cec22e692bf4b937ed30bf89(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d409d4c93acb6dbddf3ea05ef640c8c083700c01312ae34de3c952a00933254(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd4ad47529fc509173d3341762a0c1b8ce4e8d381578c9db0e9588fb5bd11e69(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7988c725f00df71948d13e3c7a67c37939bfbdf59be068727cb0f1b6fe5c0b49(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6579b40abc92fc56536665342c25021b16220f2bd87f5e74283f08704cfe6abb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb9144f9ff10e0665d17f1dab9d796961a1f30385738d5fac5012ac1e12d73c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__475c7d9ea1f132358fd8876b5bce857503b42c419cf0edd268668a9396576272(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79543fe9d0bb8f49f03afaba4905ee1fc1c6bb8081b72a0ce935e05db800d019(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d77bb2fd42dcdec4347d48a5fd38597e5fd7a8bd356c3b4be6c11e5d48f49eca(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6c829c8246593bfea087d544de86602dcf1c3f827bb531e45fb456fd06b41a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc45a3b1177a7e18688e7dbcc3ca2d16552505944545509d4b5a66e029a2afd3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d138e917ad74a2a8c043cd17d158357905bed6e23949c38b382514204bd13f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1660d38a30c3e2336ab4a8e93e4240c706d088fe2d0a466fcf8ddb12386f10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a031050a9e6f8a40b6fff2021afeb15b5ad471d2a0772dbf01945324746e1c4e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c3fe099944b1f56a32bc799baf5e867e2cdf4f7b392cab873ea63870b05066(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33a0fbdcfa0733a258cb09a7fec41cb87f369bb39dbe3d656186fee89fbfc0bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284920e01c9389024b53f7d33cd743be906b889c598a63b378523ba83bee9165(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c49306bfe5e374f98a93dbde13277a081ed1c78280db967a45ae6d9aa463d68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda12e0a9350f10cc58dfb4503e36cef9ef54b196da052bb6919eefe1b4ddcd2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ae2dc20f615630e63a616e89cc1fe881038dcec11ccd7feda4fbca3d504561(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c716fb378769c59082cbd6ef2a98ab923895cd0d2907af1ddaa2e22ac6933d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2acbdf19ba9102e2e1937592da16eb85b1c62ad65e6149f8c3d0a3bace050cad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6c4b8bedfe2dab74ff62e0b49929a7e29387a92737dd6be0d7da5dc2e30672(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be01f06da11cbc0ff664fcfcdfa1885cecb35a2be2f64f3db7a6c82afe350d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363d81378d4e1cd4dd5f6d81316deffe21c2b78c49e33a7350d70233def65523(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b53d519b13b838c462a6929cbcbecaa084a53ce80392b3cfe23e41033ed0af8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba(
    value: typing.Optional[ManagedDatabaseOpensearchProperties],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b14f1e134e8d0c84c0341fd18666aca6f997046615ab52f5363393b4ab7937e(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    idp_entity_id: typing.Optional[builtins.str] = None,
    idp_metadata_url: typing.Optional[builtins.str] = None,
    idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
    roles_key: typing.Optional[builtins.str] = None,
    sp_entity_id: typing.Optional[builtins.str] = None,
    subject_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9006f804233866e0bcbcabfee80e240d58ca3aa0b270b35fca9e093fc1e32e9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d469be80b1364917873721e8af88e7062483a039aaed7718db029f5ca170884(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814ab6ecf48749b6d62f26b6567d61ef65ea0bfbbe19f1358d51810029ef998a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__608b37237be872718973058fb30455a02be360f5053c70e96510693c9b9244d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1814aa90ebfc251af6c91642e42ce08a47300fa1a8e3cacf378c1886d789c06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94553764dddbdb00b434cdebba04db1366d57e07aaf8f5c89ff45bf9529acbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf9acff0d36a02176d62a477d13b9d21e0065d4067d1da39833b3dc9b1054ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c2749a1852f09b8e903fc5f21f9fc37f4be29b4b73b365e767ca5ec1eed0097(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3eef83ead552c9f4ef0503c6cd5db370ccfefde7338e3dca2b88ba0fdcc15ed(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSaml],
) -> None:
    """Type checking stubs"""
    pass
