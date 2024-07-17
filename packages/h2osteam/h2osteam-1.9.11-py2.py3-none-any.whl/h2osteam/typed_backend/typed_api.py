# -*- coding: utf-8 -*-
# ------------------------------
# --- This is generated code ---
# ---      DO NOT EDIT       ---
# ------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals
import json
from typing import List, Tuple, Optional


class ProfileValue(object):
    def __init__(self,
                id: int,
                min: int,
                is_min_set: bool,
                max: int,
                is_max_set: bool,
                initial: int,
                is_initial_set: bool,
                profile_max: int,
                is_profile_max_set: bool,
    ):

        self.id=id
        self.min=min
        self.is_min_set=is_min_set
        self.max=max
        self.is_max_set=is_max_set
        self.initial=initial
        self.is_initial_set=is_initial_set
        self.profile_max=profile_max
        self.is_profile_max_set=is_profile_max_set

    @classmethod
    def from_dict(cls,
             id,
             min,
             is_min_set,
             max,
             is_max_set,
             initial,
             is_initial_set,
             profile_max,
             is_profile_max_set,
    ):

        return cls(
            id,
            min,
            is_min_set,
            max,
            is_max_set,
            initial,
            is_initial_set,
            profile_max,
            is_profile_max_set,
        )

class ProfileH2o(object):
    def __init__(self,
                id: int,
                h2o_nodes: Optional[ProfileValue],
                h2o_memory: Optional[ProfileValue],
                h2o_threads: Optional[ProfileValue],
                h2o_extramempercent: Optional[ProfileValue],
                max_idle_time: Optional[ProfileValue],
                max_uptime: Optional[ProfileValue],
                yarn_vcores: Optional[ProfileValue],
                yarn_queue: str,
                start_timeout: Optional[ProfileValue],
                use_legacy_ui: bool,
                is_cluster_saving_enabled: bool,
                hadoop_opts: str,
                h2o_opts: str,
                environment_variables: str,
    ):

        self.id=id
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.yarn_vcores=yarn_vcores
        self.yarn_queue=yarn_queue
        self.start_timeout=start_timeout
        self.use_legacy_ui=use_legacy_ui
        self.is_cluster_saving_enabled=is_cluster_saving_enabled
        self.hadoop_opts=hadoop_opts
        self.h2o_opts=h2o_opts
        self.environment_variables=environment_variables

    @classmethod
    def from_dict(cls,
             id,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             max_idle_time,
             max_uptime,
             yarn_vcores,
             yarn_queue,
             start_timeout,
             use_legacy_ui,
             is_cluster_saving_enabled,
             hadoop_opts,
             h2o_opts,
             environment_variables,
    ):

        return cls(
            id,
            h2o_nodes if h2o_nodes is None else ProfileValue.from_dict(**h2o_nodes),
            h2o_memory if h2o_memory is None else ProfileValue.from_dict(**h2o_memory),
            h2o_threads if h2o_threads is None else ProfileValue.from_dict(**h2o_threads),
            h2o_extramempercent if h2o_extramempercent is None else ProfileValue.from_dict(**h2o_extramempercent),
            max_idle_time if max_idle_time is None else ProfileValue.from_dict(**max_idle_time),
            max_uptime if max_uptime is None else ProfileValue.from_dict(**max_uptime),
            yarn_vcores if yarn_vcores is None else ProfileValue.from_dict(**yarn_vcores),
            yarn_queue,
            start_timeout if start_timeout is None else ProfileValue.from_dict(**start_timeout),
            use_legacy_ui,
            is_cluster_saving_enabled,
            hadoop_opts,
            h2o_opts,
            environment_variables,
        )

class ProfileSparklingInternal(object):
    def __init__(self,
                id: int,
                driver_cores: Optional[ProfileValue],
                driver_memory: Optional[ProfileValue],
                num_executors: Optional[ProfileValue],
                executor_cores: Optional[ProfileValue],
                executor_memory: Optional[ProfileValue],
                h2o_threads: Optional[ProfileValue],
                h2o_extramempercent: Optional[ProfileValue],
                start_timeout: Optional[ProfileValue],
                yarn_queue: str,
                spark_properties: str,
                environment_ids: List[int],
                max_idle_time: Optional[ProfileValue],
                max_uptime: Optional[ProfileValue],
                use_legacy_ui: bool,
                is_cluster_saving_enabled: bool,
    ):

        self.id=id
        self.driver_cores=driver_cores
        self.driver_memory=driver_memory
        self.num_executors=num_executors
        self.executor_cores=executor_cores
        self.executor_memory=executor_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.start_timeout=start_timeout
        self.yarn_queue=yarn_queue
        self.spark_properties=spark_properties
        self.environment_ids=environment_ids
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.use_legacy_ui=use_legacy_ui
        self.is_cluster_saving_enabled=is_cluster_saving_enabled

    @classmethod
    def from_dict(cls,
             id,
             driver_cores,
             driver_memory,
             num_executors,
             executor_cores,
             executor_memory,
             h2o_threads,
             h2o_extramempercent,
             start_timeout,
             yarn_queue,
             spark_properties,
             environment_ids,
             max_idle_time,
             max_uptime,
             use_legacy_ui,
             is_cluster_saving_enabled,
    ):

        return cls(
            id,
            driver_cores if driver_cores is None else ProfileValue.from_dict(**driver_cores),
            driver_memory if driver_memory is None else ProfileValue.from_dict(**driver_memory),
            num_executors if num_executors is None else ProfileValue.from_dict(**num_executors),
            executor_cores if executor_cores is None else ProfileValue.from_dict(**executor_cores),
            executor_memory if executor_memory is None else ProfileValue.from_dict(**executor_memory),
            h2o_threads if h2o_threads is None else ProfileValue.from_dict(**h2o_threads),
            h2o_extramempercent if h2o_extramempercent is None else ProfileValue.from_dict(**h2o_extramempercent),
            start_timeout if start_timeout is None else ProfileValue.from_dict(**start_timeout),
            yarn_queue,
            spark_properties,
            environment_ids,
            max_idle_time if max_idle_time is None else ProfileValue.from_dict(**max_idle_time),
            max_uptime if max_uptime is None else ProfileValue.from_dict(**max_uptime),
            use_legacy_ui,
            is_cluster_saving_enabled,
        )

class ProfileSparklingExternal(object):
    def __init__(self,
                id: int,
                driver_cores: Optional[ProfileValue],
                driver_memory: Optional[ProfileValue],
                num_executors: Optional[ProfileValue],
                executor_cores: Optional[ProfileValue],
                executor_memory: Optional[ProfileValue],
                h2o_nodes: Optional[ProfileValue],
                h2o_memory: Optional[ProfileValue],
                h2o_threads: Optional[ProfileValue],
                h2o_extramempercent: Optional[ProfileValue],
                start_timeout: Optional[ProfileValue],
                yarn_queue: str,
                spark_properties: str,
                environment_ids: List[int],
                max_idle_time: Optional[ProfileValue],
                max_uptime: Optional[ProfileValue],
                use_legacy_ui: bool,
                is_cluster_saving_enabled: bool,
    ):

        self.id=id
        self.driver_cores=driver_cores
        self.driver_memory=driver_memory
        self.num_executors=num_executors
        self.executor_cores=executor_cores
        self.executor_memory=executor_memory
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.start_timeout=start_timeout
        self.yarn_queue=yarn_queue
        self.spark_properties=spark_properties
        self.environment_ids=environment_ids
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.use_legacy_ui=use_legacy_ui
        self.is_cluster_saving_enabled=is_cluster_saving_enabled

    @classmethod
    def from_dict(cls,
             id,
             driver_cores,
             driver_memory,
             num_executors,
             executor_cores,
             executor_memory,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             start_timeout,
             yarn_queue,
             spark_properties,
             environment_ids,
             max_idle_time,
             max_uptime,
             use_legacy_ui,
             is_cluster_saving_enabled,
    ):

        return cls(
            id,
            driver_cores if driver_cores is None else ProfileValue.from_dict(**driver_cores),
            driver_memory if driver_memory is None else ProfileValue.from_dict(**driver_memory),
            num_executors if num_executors is None else ProfileValue.from_dict(**num_executors),
            executor_cores if executor_cores is None else ProfileValue.from_dict(**executor_cores),
            executor_memory if executor_memory is None else ProfileValue.from_dict(**executor_memory),
            h2o_nodes if h2o_nodes is None else ProfileValue.from_dict(**h2o_nodes),
            h2o_memory if h2o_memory is None else ProfileValue.from_dict(**h2o_memory),
            h2o_threads if h2o_threads is None else ProfileValue.from_dict(**h2o_threads),
            h2o_extramempercent if h2o_extramempercent is None else ProfileValue.from_dict(**h2o_extramempercent),
            start_timeout if start_timeout is None else ProfileValue.from_dict(**start_timeout),
            yarn_queue,
            spark_properties,
            environment_ids,
            max_idle_time if max_idle_time is None else ProfileValue.from_dict(**max_idle_time),
            max_uptime if max_uptime is None else ProfileValue.from_dict(**max_uptime),
            use_legacy_ui,
            is_cluster_saving_enabled,
        )

class ProfileH2oKubernetes(object):
    def __init__(self,
                id: int,
                node_count: Optional[ProfileValue],
                cpu_count: Optional[ProfileValue],
                gpu_count: Optional[ProfileValue],
                memory_gb: Optional[ProfileValue],
                max_uptime_hours: Optional[ProfileValue],
                max_idle_hours: Optional[ProfileValue],
                timeout_seconds: Optional[ProfileValue],
                h2o_options: str,
                java_options: str,
                node_selector: str,
                kubernetes_volumes: List[int],
                custom_service_labels: str,
                custom_pod_labels: str,
                custom_pod_annotations: str,
                tolerations: str,
                init_containers: str,
                disabled: bool,
                env: str,
    ):

        self.id=id
        self.node_count=node_count
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.max_uptime_hours=max_uptime_hours
        self.max_idle_hours=max_idle_hours
        self.timeout_seconds=timeout_seconds
        self.h2o_options=h2o_options
        self.java_options=java_options
        self.node_selector=node_selector
        self.kubernetes_volumes=kubernetes_volumes
        self.custom_service_labels=custom_service_labels
        self.custom_pod_labels=custom_pod_labels
        self.custom_pod_annotations=custom_pod_annotations
        self.tolerations=tolerations
        self.init_containers=init_containers
        self.disabled=disabled
        self.env=env

    @classmethod
    def from_dict(cls,
             id,
             node_count,
             cpu_count,
             gpu_count,
             memory_gb,
             max_uptime_hours,
             max_idle_hours,
             timeout_seconds,
             h2o_options,
             java_options,
             node_selector,
             kubernetes_volumes,
             custom_service_labels,
             custom_pod_labels,
             custom_pod_annotations,
             tolerations,
             init_containers,
             disabled,
             env,
    ):

        return cls(
            id,
            node_count if node_count is None else ProfileValue.from_dict(**node_count),
            cpu_count if cpu_count is None else ProfileValue.from_dict(**cpu_count),
            gpu_count if gpu_count is None else ProfileValue.from_dict(**gpu_count),
            memory_gb if memory_gb is None else ProfileValue.from_dict(**memory_gb),
            max_uptime_hours if max_uptime_hours is None else ProfileValue.from_dict(**max_uptime_hours),
            max_idle_hours if max_idle_hours is None else ProfileValue.from_dict(**max_idle_hours),
            timeout_seconds if timeout_seconds is None else ProfileValue.from_dict(**timeout_seconds),
            h2o_options,
            java_options,
            node_selector,
            kubernetes_volumes,
            custom_service_labels,
            custom_pod_labels,
            custom_pod_annotations,
            tolerations,
            init_containers,
            disabled,
            env,
        )

class ProfileDriverlessKubernetes(object):
    def __init__(self,
                id: int,
                cpu_count: Optional[ProfileValue],
                gpu_count: Optional[ProfileValue],
                memory_gb: Optional[ProfileValue],
                storage_gb: Optional[ProfileValue],
                max_uptime_hours: Optional[ProfileValue],
                max_idle_hours: Optional[ProfileValue],
                timeout_seconds: Optional[ProfileValue],
                license_manager_project_name: str,
                config_toml: str,
                allow_instance_config_toml: bool,
                whitelist_instance_config_toml: str,
                node_selector: str,
                kubernetes_volumes: List[int],
                env: str,
                custom_pod_labels: str,
                custom_pod_annotations: str,
                load_balancer_source_ranges: str,
                tolerations: str,
                init_containers: str,
                disabled: bool,
                multinode: bool,
                main_cpu_count: int,
                main_memory_gb: int,
                min_worker_count: int,
                max_worker_count: int,
                buffer_worker_count: int,
                worker_processor_count: int,
                worker_downscale_delay_seconds: int,
                main_processor_count: int,
                main_node_selector: str,
    ):

        self.id=id
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.storage_gb=storage_gb
        self.max_uptime_hours=max_uptime_hours
        self.max_idle_hours=max_idle_hours
        self.timeout_seconds=timeout_seconds
        self.license_manager_project_name=license_manager_project_name
        self.config_toml=config_toml
        self.allow_instance_config_toml=allow_instance_config_toml
        self.whitelist_instance_config_toml=whitelist_instance_config_toml
        self.node_selector=node_selector
        self.kubernetes_volumes=kubernetes_volumes
        self.env=env
        self.custom_pod_labels=custom_pod_labels
        self.custom_pod_annotations=custom_pod_annotations
        self.load_balancer_source_ranges=load_balancer_source_ranges
        self.tolerations=tolerations
        self.init_containers=init_containers
        self.disabled=disabled
        self.multinode=multinode
        self.main_cpu_count=main_cpu_count
        self.main_memory_gb=main_memory_gb
        self.min_worker_count=min_worker_count
        self.max_worker_count=max_worker_count
        self.buffer_worker_count=buffer_worker_count
        self.worker_processor_count=worker_processor_count
        self.worker_downscale_delay_seconds=worker_downscale_delay_seconds
        self.main_processor_count=main_processor_count
        self.main_node_selector=main_node_selector

    @classmethod
    def from_dict(cls,
             id,
             cpu_count,
             gpu_count,
             memory_gb,
             storage_gb,
             max_uptime_hours,
             max_idle_hours,
             timeout_seconds,
             license_manager_project_name,
             config_toml,
             allow_instance_config_toml,
             whitelist_instance_config_toml,
             node_selector,
             kubernetes_volumes,
             env,
             custom_pod_labels,
             custom_pod_annotations,
             load_balancer_source_ranges,
             tolerations,
             init_containers,
             disabled,
             multinode,
             main_cpu_count,
             main_memory_gb,
             min_worker_count,
             max_worker_count,
             buffer_worker_count,
             worker_processor_count,
             worker_downscale_delay_seconds,
             main_processor_count,
             main_node_selector,
    ):

        return cls(
            id,
            cpu_count if cpu_count is None else ProfileValue.from_dict(**cpu_count),
            gpu_count if gpu_count is None else ProfileValue.from_dict(**gpu_count),
            memory_gb if memory_gb is None else ProfileValue.from_dict(**memory_gb),
            storage_gb if storage_gb is None else ProfileValue.from_dict(**storage_gb),
            max_uptime_hours if max_uptime_hours is None else ProfileValue.from_dict(**max_uptime_hours),
            max_idle_hours if max_idle_hours is None else ProfileValue.from_dict(**max_idle_hours),
            timeout_seconds if timeout_seconds is None else ProfileValue.from_dict(**timeout_seconds),
            license_manager_project_name,
            config_toml,
            allow_instance_config_toml,
            whitelist_instance_config_toml,
            node_selector,
            kubernetes_volumes,
            env,
            custom_pod_labels,
            custom_pod_annotations,
            load_balancer_source_ranges,
            tolerations,
            init_containers,
            disabled,
            multinode,
            main_cpu_count,
            main_memory_gb,
            min_worker_count,
            max_worker_count,
            buffer_worker_count,
            worker_processor_count,
            worker_downscale_delay_seconds,
            main_processor_count,
            main_node_selector,
        )

class Permission(object):
    def __init__(self,
                id: int,
                code: str,
                description: str,
    ):

        self.id=id
        self.code=code
        self.description=description

    @classmethod
    def from_dict(cls,
             id,
             code,
             description,
    ):

        return cls(
            id,
            code,
            description,
        )

class Event(object):
    def __init__(self,
                entity_type: str,
                entity_id: int,
                level: str,
                message: str,
                created_at: int,
    ):

        self.entity_type=entity_type
        self.entity_id=entity_id
        self.level=level
        self.message=message
        self.created_at=created_at

    @classmethod
    def from_dict(cls,
             entity_type,
             entity_id,
             level,
             message,
             created_at,
    ):

        return cls(
            entity_type,
            entity_id,
            level,
            message,
            created_at,
        )

class KubernetesVolumeHostPath(object):
    def __init__(self,
                id: int,
                path: str,
    ):

        self.id=id
        self.path=path

    @classmethod
    def from_dict(cls,
             id,
             path,
    ):

        return cls(
            id,
            path,
        )

class KubernetesVolumeSecret(object):
    def __init__(self,
                id: int,
                secret_name: str,
    ):

        self.id=id
        self.secret_name=secret_name

    @classmethod
    def from_dict(cls,
             id,
             secret_name,
    ):

        return cls(
            id,
            secret_name,
        )

class KubernetesVolumeConfigMap(object):
    def __init__(self,
                id: int,
                config_map_name: str,
    ):

        self.id=id
        self.config_map_name=config_map_name

    @classmethod
    def from_dict(cls,
             id,
             config_map_name,
    ):

        return cls(
            id,
            config_map_name,
        )

class KubernetesVolumePvc(object):
    def __init__(self,
                id: int,
                claim_name: str,
    ):

        self.id=id
        self.claim_name=claim_name

    @classmethod
    def from_dict(cls,
             id,
             claim_name,
    ):

        return cls(
            id,
            claim_name,
        )

class KubernetesVolumeNfs(object):
    def __init__(self,
                id: int,
                server: str,
                path: str,
    ):

        self.id=id
        self.server=server
        self.path=path

    @classmethod
    def from_dict(cls,
             id,
             server,
             path,
    ):

        return cls(
            id,
            server,
            path,
        )

class KubernetesVolumeCsi(object):
    def __init__(self,
                id: int,
                driver: str,
                f_s_type: str,
                volume_attributes: str,
    ):

        self.id=id
        self.driver=driver
        self.f_s_type=f_s_type
        self.volume_attributes=volume_attributes

    @classmethod
    def from_dict(cls,
             id,
             driver,
             f_s_type,
             volume_attributes,
    ):

        return cls(
            id,
            driver,
            f_s_type,
            volume_attributes,
        )

class Config(object):
    def __init__(self,
                authentication_type: str,
                cluster_proxy_address: str,
                h2o_enabled: bool,
                kerberos_enabled: bool,
                version: str,
                username: str,
                is_admin: bool,
                is_user_oidc_auth: bool,
                permissions: List[Permission],
                sparkling_enabled: bool,
                logout_url: str,
                web_timeout_min: int,
                jupyter_disabled: bool,
                yarn_queue: str,
                driverless_enabled: bool,
                sparkling_default_backend: str,
                hadoop_super_admin: bool,
                kubernetes_super_admin: bool,
                host_path_mount_disabled: bool,
                docs_upload_disabled: bool,
                d_a_i_o_id_c_auth: bool,
    ):

        self.authentication_type=authentication_type
        self.cluster_proxy_address=cluster_proxy_address
        self.h2o_enabled=h2o_enabled
        self.kerberos_enabled=kerberos_enabled
        self.version=version
        self.username=username
        self.is_admin=is_admin
        self.is_user_oidc_auth=is_user_oidc_auth
        self.permissions=permissions
        self.sparkling_enabled=sparkling_enabled
        self.logout_url=logout_url
        self.web_timeout_min=web_timeout_min
        self.jupyter_disabled=jupyter_disabled
        self.yarn_queue=yarn_queue
        self.driverless_enabled=driverless_enabled
        self.sparkling_default_backend=sparkling_default_backend
        self.hadoop_super_admin=hadoop_super_admin
        self.kubernetes_super_admin=kubernetes_super_admin
        self.host_path_mount_disabled=host_path_mount_disabled
        self.docs_upload_disabled=docs_upload_disabled
        self.d_a_i_o_id_c_auth=d_a_i_o_id_c_auth

    @classmethod
    def from_dict(cls,
             authentication_type,
             cluster_proxy_address,
             h2o_enabled,
             kerberos_enabled,
             version,
             username,
             is_admin,
             is_user_oidc_auth,
             permissions,
             sparkling_enabled,
             logout_url,
             web_timeout_min,
             jupyter_disabled,
             yarn_queue,
             driverless_enabled,
             sparkling_default_backend,
             hadoop_super_admin,
             kubernetes_super_admin,
             host_path_mount_disabled,
             docs_upload_disabled,
             d_a_i_o_id_c_auth,
    ):
        list_objects_permissions = []
        for i in permissions:
           list_objects_permissions.append(Permission(**i))

        return cls(
            authentication_type,
            cluster_proxy_address,
            h2o_enabled,
            kerberos_enabled,
            version,
            username,
            is_admin,
            is_user_oidc_auth,
            list_objects_permissions,
            sparkling_enabled,
            logout_url,
            web_timeout_min,
            jupyter_disabled,
            yarn_queue,
            driverless_enabled,
            sparkling_default_backend,
            hadoop_super_admin,
            kubernetes_super_admin,
            host_path_mount_disabled,
            docs_upload_disabled,
            d_a_i_o_id_c_auth,
        )

class LdapConfig(object):
    def __init__(self,
                host: str,
                port: int,
                ldaps: bool,
                internal_ca: bool,
                ca_cert_path: str,
                bind_dn: str,
                bind_password: str,
                user_base_dn: str,
                user_base_filter: str,
                user_name_attribute: str,
                user_uid_number_attribute: str,
                user_gid_number_attribute: str,
                group_base_dn: str,
                group_name_attribute: str,
                static_member_attribute: str,
                search_request_size_limit: int,
                search_request_time_limit: int,
                cache_invalidation_age: int,
    ):

        self.host=host
        self.port=port
        self.ldaps=ldaps
        self.internal_ca=internal_ca
        self.ca_cert_path=ca_cert_path
        self.bind_dn=bind_dn
        self.bind_password=bind_password
        self.user_base_dn=user_base_dn
        self.user_base_filter=user_base_filter
        self.user_name_attribute=user_name_attribute
        self.user_uid_number_attribute=user_uid_number_attribute
        self.user_gid_number_attribute=user_gid_number_attribute
        self.group_base_dn=group_base_dn
        self.group_name_attribute=group_name_attribute
        self.static_member_attribute=static_member_attribute
        self.search_request_size_limit=search_request_size_limit
        self.search_request_time_limit=search_request_time_limit
        self.cache_invalidation_age=cache_invalidation_age

    @classmethod
    def from_dict(cls,
             host,
             port,
             ldaps,
             internal_ca,
             ca_cert_path,
             bind_dn,
             bind_password,
             user_base_dn,
             user_base_filter,
             user_name_attribute,
             user_uid_number_attribute,
             user_gid_number_attribute,
             group_base_dn,
             group_name_attribute,
             static_member_attribute,
             search_request_size_limit,
             search_request_time_limit,
             cache_invalidation_age,
    ):

        return cls(
            host,
            port,
            ldaps,
            internal_ca,
            ca_cert_path,
            bind_dn,
            bind_password,
            user_base_dn,
            user_base_filter,
            user_name_attribute,
            user_uid_number_attribute,
            user_gid_number_attribute,
            group_base_dn,
            group_name_attribute,
            static_member_attribute,
            search_request_size_limit,
            search_request_time_limit,
            cache_invalidation_age,
        )

class SamlConfig(object):
    def __init__(self,
                key_store_path: str,
                key_store_password: str,
                id_p_metadata_path: str,
                entity_base_url: str,
                user_name_attribute: str,
                group_name_attribute: str,
                entity_id: str,
                force_authentication: bool,
                logout_url: str,
    ):

        self.key_store_path=key_store_path
        self.key_store_password=key_store_password
        self.id_p_metadata_path=id_p_metadata_path
        self.entity_base_url=entity_base_url
        self.user_name_attribute=user_name_attribute
        self.group_name_attribute=group_name_attribute
        self.entity_id=entity_id
        self.force_authentication=force_authentication
        self.logout_url=logout_url

    @classmethod
    def from_dict(cls,
             key_store_path,
             key_store_password,
             id_p_metadata_path,
             entity_base_url,
             user_name_attribute,
             group_name_attribute,
             entity_id,
             force_authentication,
             logout_url,
    ):

        return cls(
            key_store_path,
            key_store_password,
            id_p_metadata_path,
            entity_base_url,
            user_name_attribute,
            group_name_attribute,
            entity_id,
            force_authentication,
            logout_url,
        )

class PamConfig(object):
    def __init__(self,
                service_name: str,
    ):

        self.service_name=service_name

    @classmethod
    def from_dict(cls,
             service_name,
    ):

        return cls(
            service_name,
        )

class OidcConfig(object):
    def __init__(self,
                issuer: str,
                client_id: str,
                client_secret: str,
                scopes: str,
                userinfo_username_key: str,
                userinfo_email_key: str,
                userinfo_roles_key: str,
                userinfo_uid_key: str,
                userinfo_gid_key: str,
                redirect_url: str,
                logout_redirect_url: str,
                enable_logout_id_token_hint: bool,
                a_c_r_values: str,
    ):

        self.issuer=issuer
        self.client_id=client_id
        self.client_secret=client_secret
        self.scopes=scopes
        self.userinfo_username_key=userinfo_username_key
        self.userinfo_email_key=userinfo_email_key
        self.userinfo_roles_key=userinfo_roles_key
        self.userinfo_uid_key=userinfo_uid_key
        self.userinfo_gid_key=userinfo_gid_key
        self.redirect_url=redirect_url
        self.logout_redirect_url=logout_redirect_url
        self.enable_logout_id_token_hint=enable_logout_id_token_hint
        self.a_c_r_values=a_c_r_values

    @classmethod
    def from_dict(cls,
             issuer,
             client_id,
             client_secret,
             scopes,
             userinfo_username_key,
             userinfo_email_key,
             userinfo_roles_key,
             userinfo_uid_key,
             userinfo_gid_key,
             redirect_url,
             logout_redirect_url,
             enable_logout_id_token_hint,
             a_c_r_values,
    ):

        return cls(
            issuer,
            client_id,
            client_secret,
            scopes,
            userinfo_username_key,
            userinfo_email_key,
            userinfo_roles_key,
            userinfo_uid_key,
            userinfo_gid_key,
            redirect_url,
            logout_redirect_url,
            enable_logout_id_token_hint,
            a_c_r_values,
        )

class LdapConnection(object):
    def __init__(self,
                id: int,
                name: str,
                priority: int,
                host: str,
                port: int,
                ldaps: bool,
                internal_ca: bool,
                ca_cert_path: str,
                bind_dn: str,
                bind_password: str,
                user_base_dn: str,
                user_base_filter: str,
                user_name_attribute: str,
                user_uid_number_attribute: str,
                user_gid_number_attribute: str,
                group_base_dn: str,
                group_name_attribute: str,
                static_member_attribute: str,
                search_request_size_limit: int,
                search_request_time_limit: int,
                cache_invalidation_age: int,
    ):

        self.id=id
        self.name=name
        self.priority=priority
        self.host=host
        self.port=port
        self.ldaps=ldaps
        self.internal_ca=internal_ca
        self.ca_cert_path=ca_cert_path
        self.bind_dn=bind_dn
        self.bind_password=bind_password
        self.user_base_dn=user_base_dn
        self.user_base_filter=user_base_filter
        self.user_name_attribute=user_name_attribute
        self.user_uid_number_attribute=user_uid_number_attribute
        self.user_gid_number_attribute=user_gid_number_attribute
        self.group_base_dn=group_base_dn
        self.group_name_attribute=group_name_attribute
        self.static_member_attribute=static_member_attribute
        self.search_request_size_limit=search_request_size_limit
        self.search_request_time_limit=search_request_time_limit
        self.cache_invalidation_age=cache_invalidation_age

    @classmethod
    def from_dict(cls,
             id,
             name,
             priority,
             host,
             port,
             ldaps,
             internal_ca,
             ca_cert_path,
             bind_dn,
             bind_password,
             user_base_dn,
             user_base_filter,
             user_name_attribute,
             user_uid_number_attribute,
             user_gid_number_attribute,
             group_base_dn,
             group_name_attribute,
             static_member_attribute,
             search_request_size_limit,
             search_request_time_limit,
             cache_invalidation_age,
    ):

        return cls(
            id,
            name,
            priority,
            host,
            port,
            ldaps,
            internal_ca,
            ca_cert_path,
            bind_dn,
            bind_password,
            user_base_dn,
            user_base_filter,
            user_name_attribute,
            user_uid_number_attribute,
            user_gid_number_attribute,
            group_base_dn,
            group_name_attribute,
            static_member_attribute,
            search_request_size_limit,
            search_request_time_limit,
            cache_invalidation_age,
        )

class LdapGroup(object):
    def __init__(self,
                name: str,
                users: int,
                user_names: List[str],
    ):

        self.name=name
        self.users=users
        self.user_names=user_names

    @classmethod
    def from_dict(cls,
             name,
             users,
             user_names,
    ):

        return cls(
            name,
            users,
            user_names,
        )

class RolesConfig(object):
    def __init__(self,
                access_groups: str,
                admin_groups: str,
    ):

        self.access_groups=access_groups
        self.admin_groups=admin_groups

    @classmethod
    def from_dict(cls,
             access_groups,
             admin_groups,
    ):

        return cls(
            access_groups,
            admin_groups,
        )

class HadoopConfig(object):
    def __init__(self,
                enabled: bool,
                conf_dir: str,
                tmp_dir: str,
                lower_usernames: bool,
                kerberos_enabled: bool,
                kerberos_principal: str,
                kerberos_keytab_path: str,
                kerberos_config_path: str,
                mapr_enabled: bool,
                mapr_ticketfile_location: str,
                hive_enabled: bool,
                hive_jdbc_driver_path: str,
                hive_principal: str,
                hive_host: str,
                hive_jdbc_url_pattern: str,
                hive_ssl_enabled: bool,
    ):

        self.enabled=enabled
        self.conf_dir=conf_dir
        self.tmp_dir=tmp_dir
        self.lower_usernames=lower_usernames
        self.kerberos_enabled=kerberos_enabled
        self.kerberos_principal=kerberos_principal
        self.kerberos_keytab_path=kerberos_keytab_path
        self.kerberos_config_path=kerberos_config_path
        self.mapr_enabled=mapr_enabled
        self.mapr_ticketfile_location=mapr_ticketfile_location
        self.hive_enabled=hive_enabled
        self.hive_jdbc_driver_path=hive_jdbc_driver_path
        self.hive_principal=hive_principal
        self.hive_host=hive_host
        self.hive_jdbc_url_pattern=hive_jdbc_url_pattern
        self.hive_ssl_enabled=hive_ssl_enabled

    @classmethod
    def from_dict(cls,
             enabled,
             conf_dir,
             tmp_dir,
             lower_usernames,
             kerberos_enabled,
             kerberos_principal,
             kerberos_keytab_path,
             kerberos_config_path,
             mapr_enabled,
             mapr_ticketfile_location,
             hive_enabled,
             hive_jdbc_driver_path,
             hive_principal,
             hive_host,
             hive_jdbc_url_pattern,
             hive_ssl_enabled,
    ):

        return cls(
            enabled,
            conf_dir,
            tmp_dir,
            lower_usernames,
            kerberos_enabled,
            kerberos_principal,
            kerberos_keytab_path,
            kerberos_config_path,
            mapr_enabled,
            mapr_ticketfile_location,
            hive_enabled,
            hive_jdbc_driver_path,
            hive_principal,
            hive_host,
            hive_jdbc_url_pattern,
            hive_ssl_enabled,
        )

class HadoopInfo(object):
    def __init__(self,
                version: str,
                distribution_version: str,
                common_path: str,
    ):

        self.version=version
        self.distribution_version=distribution_version
        self.common_path=common_path

    @classmethod
    def from_dict(cls,
             version,
             distribution_version,
             common_path,
    ):

        return cls(
            version,
            distribution_version,
            common_path,
        )

class KubernetesConfig(object):
    def __init__(self,
                enabled: bool,
                inside_cluster: bool,
                kubeconfig_path: str,
                namespace: str,
                use_default_storage_class: bool,
                storage_class: str,
                allow_volume_expansion: bool,
                gpu_resource_name: str,
                fallback_uid: int,
                fallback_gid: int,
                force_fallback: bool,
                load_balancer_annotations: str,
                r_w_m_storage_class: str,
                seccomp_profile_runtime_default: bool,
    ):

        self.enabled=enabled
        self.inside_cluster=inside_cluster
        self.kubeconfig_path=kubeconfig_path
        self.namespace=namespace
        self.use_default_storage_class=use_default_storage_class
        self.storage_class=storage_class
        self.allow_volume_expansion=allow_volume_expansion
        self.gpu_resource_name=gpu_resource_name
        self.fallback_uid=fallback_uid
        self.fallback_gid=fallback_gid
        self.force_fallback=force_fallback
        self.load_balancer_annotations=load_balancer_annotations
        self.r_w_m_storage_class=r_w_m_storage_class
        self.seccomp_profile_runtime_default=seccomp_profile_runtime_default

    @classmethod
    def from_dict(cls,
             enabled,
             inside_cluster,
             kubeconfig_path,
             namespace,
             use_default_storage_class,
             storage_class,
             allow_volume_expansion,
             gpu_resource_name,
             fallback_uid,
             fallback_gid,
             force_fallback,
             load_balancer_annotations,
             r_w_m_storage_class,
             seccomp_profile_runtime_default,
    ):

        return cls(
            enabled,
            inside_cluster,
            kubeconfig_path,
            namespace,
            use_default_storage_class,
            storage_class,
            allow_volume_expansion,
            gpu_resource_name,
            fallback_uid,
            fallback_gid,
            force_fallback,
            load_balancer_annotations,
            r_w_m_storage_class,
            seccomp_profile_runtime_default,
        )

class KubernetesInfo(object):
    def __init__(self,
                version: str,
    ):

        self.version=version

    @classmethod
    def from_dict(cls,
             version,
    ):

        return cls(
            version,
        )

class KubernetesHdfsConfig(object):
    def __init__(self,
                enabled: bool,
                config_path: str,
                keytab_path: str,
                principal: str,
                kerberos_config_path: str,
                hdfs_classpath: str,
                hive_enabled: bool,
                hive_classpath: str,
                mounted_volumes: List[int],
    ):

        self.enabled=enabled
        self.config_path=config_path
        self.keytab_path=keytab_path
        self.principal=principal
        self.kerberos_config_path=kerberos_config_path
        self.hdfs_classpath=hdfs_classpath
        self.hive_enabled=hive_enabled
        self.hive_classpath=hive_classpath
        self.mounted_volumes=mounted_volumes

    @classmethod
    def from_dict(cls,
             enabled,
             config_path,
             keytab_path,
             principal,
             kerberos_config_path,
             hdfs_classpath,
             hive_enabled,
             hive_classpath,
             mounted_volumes,
    ):

        return cls(
            enabled,
            config_path,
            keytab_path,
            principal,
            kerberos_config_path,
            hdfs_classpath,
            hive_enabled,
            hive_classpath,
            mounted_volumes,
        )

class NewH2oStartupParameter(object):
    def __init__(self,
                name: str,
                value: str,
                kind: int,
                priority: int,
    ):

        self.name=name
        self.value=value
        self.kind=kind
        self.priority=priority

    @classmethod
    def from_dict(cls,
             name,
             value,
             kind,
             priority,
    ):

        return cls(
            name,
            value,
            kind,
            priority,
        )

class H2oStartupParameter(object):
    def __init__(self,
                id: int,
                name: str,
                value: str,
                kind: int,
                priority: int,
    ):

        self.id=id
        self.name=name
        self.value=value
        self.kind=kind
        self.priority=priority

    @classmethod
    def from_dict(cls,
             id,
             name,
             value,
             kind,
             priority,
    ):

        return cls(
            id,
            name,
            value,
            kind,
            priority,
        )

class LaunchH2oClusterParameters(object):
    def __init__(self,
                name: str,
                profile_id: int,
                h2o_nodes: int,
                h2o_memory: int,
                h2o_threads: int,
                h2o_extramempercent: int,
                yarn_vcores: int,
                yarn_queue: str,
                h2o_engine_id: int,
                leader_node_id: int,
                start_timeout: int,
                max_idle_time: int,
                max_uptime: int,
                rec_memory: int,
                rec_extra_memory_percent: int,
                save_cluster_data: bool,
                load_data_cluster_id: int,
                recover_grid_search: bool,
    ):

        self.name=name
        self.profile_id=profile_id
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.yarn_vcores=yarn_vcores
        self.yarn_queue=yarn_queue
        self.h2o_engine_id=h2o_engine_id
        self.leader_node_id=leader_node_id
        self.start_timeout=start_timeout
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.rec_memory=rec_memory
        self.rec_extra_memory_percent=rec_extra_memory_percent
        self.save_cluster_data=save_cluster_data
        self.load_data_cluster_id=load_data_cluster_id
        self.recover_grid_search=recover_grid_search

    @classmethod
    def from_dict(cls,
             name,
             profile_id,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             yarn_vcores,
             yarn_queue,
             h2o_engine_id,
             leader_node_id,
             start_timeout,
             max_idle_time,
             max_uptime,
             rec_memory,
             rec_extra_memory_percent,
             save_cluster_data,
             load_data_cluster_id,
             recover_grid_search,
    ):

        return cls(
            name,
            profile_id,
            h2o_nodes,
            h2o_memory,
            h2o_threads,
            h2o_extramempercent,
            yarn_vcores,
            yarn_queue,
            h2o_engine_id,
            leader_node_id,
            start_timeout,
            max_idle_time,
            max_uptime,
            rec_memory,
            rec_extra_memory_percent,
            save_cluster_data,
            load_data_cluster_id,
            recover_grid_search,
        )

class H2oCluster(object):
    def __init__(self,
                id: int,
                status: str,
                created_at: int,
                created_by: str,
                is_saved: bool,
                cluster_name: str,
                profile_name: str,
                h2o_nodes: int,
                h2o_memory: int,
                h2o_threads: int,
                h2o_extramempercent: int,
                max_idle_time: int,
                max_uptime: int,
                yarn_vcores: int,
                yarn_queue: str,
                h2o_engine_version: str,
                leader_node_id: int,
                start_timeout: int,
                address: str,
                context_path: str,
                application_id: str,
                idle_time: int,
                up_time: int,
                xgb_status: str,
                xgb_address: str,
                xgb_context_path: str,
                xgb_application_id: str,
    ):

        self.id=id
        self.status=status
        self.created_at=created_at
        self.created_by=created_by
        self.is_saved=is_saved
        self.cluster_name=cluster_name
        self.profile_name=profile_name
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.yarn_vcores=yarn_vcores
        self.yarn_queue=yarn_queue
        self.h2o_engine_version=h2o_engine_version
        self.leader_node_id=leader_node_id
        self.start_timeout=start_timeout
        self.address=address
        self.context_path=context_path
        self.application_id=application_id
        self.idle_time=idle_time
        self.up_time=up_time
        self.xgb_status=xgb_status
        self.xgb_address=xgb_address
        self.xgb_context_path=xgb_context_path
        self.xgb_application_id=xgb_application_id

    @classmethod
    def from_dict(cls,
             id,
             status,
             created_at,
             created_by,
             is_saved,
             cluster_name,
             profile_name,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             max_idle_time,
             max_uptime,
             yarn_vcores,
             yarn_queue,
             h2o_engine_version,
             leader_node_id,
             start_timeout,
             address,
             context_path,
             application_id,
             idle_time,
             up_time,
             xgb_status,
             xgb_address,
             xgb_context_path,
             xgb_application_id,
    ):

        return cls(
            id,
            status,
            created_at,
            created_by,
            is_saved,
            cluster_name,
            profile_name,
            h2o_nodes,
            h2o_memory,
            h2o_threads,
            h2o_extramempercent,
            max_idle_time,
            max_uptime,
            yarn_vcores,
            yarn_queue,
            h2o_engine_version,
            leader_node_id,
            start_timeout,
            address,
            context_path,
            application_id,
            idle_time,
            up_time,
            xgb_status,
            xgb_address,
            xgb_context_path,
            xgb_application_id,
        )

class H2oClusterLogs(object):
    def __init__(self,
                driver: str,
                h2o: str,
                yarn: str,
                hdfs: str,
                xgboost_driver: str,
                xgboost: str,
                xgboost_yarn: str,
    ):

        self.driver=driver
        self.h2o=h2o
        self.yarn=yarn
        self.hdfs=hdfs
        self.xgboost_driver=xgboost_driver
        self.xgboost=xgboost
        self.xgboost_yarn=xgboost_yarn

    @classmethod
    def from_dict(cls,
             driver,
             h2o,
             yarn,
             hdfs,
             xgboost_driver,
             xgboost,
             xgboost_yarn,
    ):

        return cls(
            driver,
            h2o,
            yarn,
            hdfs,
            xgboost_driver,
            xgboost,
            xgboost_yarn,
        )

class H2oConfig(object):
    def __init__(self,
                enabled: bool,
                backend_type: str,
                internal_secure_connections: bool,
                enable_external_xgboost: bool,
                allow_insecure_xgboost: bool,
                extra_hadoop_classpath: str,
                jobname_prefix: str,
                override_driver_output_directory: bool,
                driver_output_directory: str,
    ):

        self.enabled=enabled
        self.backend_type=backend_type
        self.internal_secure_connections=internal_secure_connections
        self.enable_external_xgboost=enable_external_xgboost
        self.allow_insecure_xgboost=allow_insecure_xgboost
        self.extra_hadoop_classpath=extra_hadoop_classpath
        self.jobname_prefix=jobname_prefix
        self.override_driver_output_directory=override_driver_output_directory
        self.driver_output_directory=driver_output_directory

    @classmethod
    def from_dict(cls,
             enabled,
             backend_type,
             internal_secure_connections,
             enable_external_xgboost,
             allow_insecure_xgboost,
             extra_hadoop_classpath,
             jobname_prefix,
             override_driver_output_directory,
             driver_output_directory,
    ):

        return cls(
            enabled,
            backend_type,
            internal_secure_connections,
            enable_external_xgboost,
            allow_insecure_xgboost,
            extra_hadoop_classpath,
            jobname_prefix,
            override_driver_output_directory,
            driver_output_directory,
        )

class H2oEngine(object):
    def __init__(self,
                id: int,
                h2o_version: str,
                hadoop_version: str,
                jar_name: str,
                jar_location: str,
                created_at: int,
                py_name: str,
                py_location: str,
                r_name: str,
                r_location: str,
    ):

        self.id=id
        self.h2o_version=h2o_version
        self.hadoop_version=hadoop_version
        self.jar_name=jar_name
        self.jar_location=jar_location
        self.created_at=created_at
        self.py_name=py_name
        self.py_location=py_location
        self.r_name=r_name
        self.r_location=r_location

    @classmethod
    def from_dict(cls,
             id,
             h2o_version,
             hadoop_version,
             jar_name,
             jar_location,
             created_at,
             py_name,
             py_location,
             r_name,
             r_location,
    ):

        return cls(
            id,
            h2o_version,
            hadoop_version,
            jar_name,
            jar_location,
            created_at,
            py_name,
            py_location,
            r_name,
            r_location,
        )

class EntityType(object):
    def __init__(self,
                id: int,
                name: str,
    ):

        self.id=id
        self.name=name

    @classmethod
    def from_dict(cls,
             id,
             name,
    ):

        return cls(
            id,
            name,
        )

class DatasetParameters(object):
    def __init__(self,
                dataset_size_gb: int,
                rows: int,
                cols: int,
                using_x_g_boost: bool,
    ):

        self.dataset_size_gb=dataset_size_gb
        self.rows=rows
        self.cols=cols
        self.using_x_g_boost=using_x_g_boost

    @classmethod
    def from_dict(cls,
             dataset_size_gb,
             rows,
             cols,
             using_x_g_boost,
    ):

        return cls(
            dataset_size_gb,
            rows,
            cols,
            using_x_g_boost,
        )

class EstimatedClusterMemory(object):
    def __init__(self,
                total_memory_gb: int,
                extra_mem_percent: int,
    ):

        self.total_memory_gb=total_memory_gb
        self.extra_mem_percent=extra_mem_percent

    @classmethod
    def from_dict(cls,
             total_memory_gb,
             extra_mem_percent,
    ):

        return cls(
            total_memory_gb,
            extra_mem_percent,
        )

class Role(object):
    def __init__(self,
                id: int,
                name: str,
                description: str,
                created: int,
    ):

        self.id=id
        self.name=name
        self.description=description
        self.created=created

    @classmethod
    def from_dict(cls,
             id,
             name,
             description,
             created,
    ):

        return cls(
            id,
            name,
            description,
            created,
        )

class Workgroup(object):
    def __init__(self,
                id: int,
                name: str,
                description: str,
                created: int,
    ):

        self.id=id
        self.name=name
        self.description=description
        self.created=created

    @classmethod
    def from_dict(cls,
             id,
             name,
             description,
             created,
    ):

        return cls(
            id,
            name,
            description,
            created,
        )

class Identity(object):
    def __init__(self,
                id: int,
                uid: int,
                gid: int,
                sub: str,
                name: str,
                is_active: bool,
                auth_type: str,
                last_login: int,
                created: int,
                yarn_queue: str,
                override_is_admin: bool,
    ):

        self.id=id
        self.uid=uid
        self.gid=gid
        self.sub=sub
        self.name=name
        self.is_active=is_active
        self.auth_type=auth_type
        self.last_login=last_login
        self.created=created
        self.yarn_queue=yarn_queue
        self.override_is_admin=override_is_admin

    @classmethod
    def from_dict(cls,
             id,
             uid,
             gid,
             sub,
             name,
             is_active,
             auth_type,
             last_login,
             created,
             yarn_queue,
             override_is_admin,
    ):

        return cls(
            id,
            uid,
            gid,
            sub,
            name,
            is_active,
            auth_type,
            last_login,
            created,
            yarn_queue,
            override_is_admin,
        )

class UserRole(object):
    def __init__(self,
                kind: str,
                identity_id: int,
                identity_name: str,
                role_id: int,
                role_name: str,
    ):

        self.kind=kind
        self.identity_id=identity_id
        self.identity_name=identity_name
        self.role_id=role_id
        self.role_name=role_name

    @classmethod
    def from_dict(cls,
             kind,
             identity_id,
             identity_name,
             role_id,
             role_name,
    ):

        return cls(
            kind,
            identity_id,
            identity_name,
            role_id,
            role_name,
        )

class EntityPrivilege(object):
    def __init__(self,
                kind: str,
                workgroup_id: int,
                workgroup_name: str,
                workgroup_description: str,
    ):

        self.kind=kind
        self.workgroup_id=workgroup_id
        self.workgroup_name=workgroup_name
        self.workgroup_description=workgroup_description

    @classmethod
    def from_dict(cls,
             kind,
             workgroup_id,
             workgroup_name,
             workgroup_description,
    ):

        return cls(
            kind,
            workgroup_id,
            workgroup_name,
            workgroup_description,
        )

class EntityHistory(object):
    def __init__(self,
                identity_id: int,
                action: str,
                description: str,
                created_at: int,
    ):

        self.identity_id=identity_id
        self.action=action
        self.description=description
        self.created_at=created_at

    @classmethod
    def from_dict(cls,
             identity_id,
             action,
             description,
             created_at,
    ):

        return cls(
            identity_id,
            action,
            description,
            created_at,
        )

class License(object):
    def __init__(self,
                type: str,
                days_left: int,
                max_users: int,
    ):

        self.type=type
        self.days_left=days_left
        self.max_users=max_users

    @classmethod
    def from_dict(cls,
             type,
             days_left,
             max_users,
    ):

        return cls(
            type,
            days_left,
            max_users,
        )

class SparklingCluster(object):
    def __init__(self,
                id: int,
                cluster_state: str,
                created_by: str,
                created_at: int,
                backend_type: str,
                is_saved: bool,
                cluster_name: str,
                profile_id: int,
                session_id: int,
                h2o_version: str,
                sparkling_version: str,
                profile_name: str,
                driver_cores: int,
                driver_memory: int,
                num_executors: int,
                executor_cores: int,
                executor_memory: int,
                h2o_nodes: int,
                h2o_memory: int,
                h2o_threads: int,
                h2o_extramempercent: int,
                yarn_queue: str,
                h2o_engine_id: int,
                sparkling_engine_id: int,
                spark_properties: str,
                spark_ui_url: str,
                driver_log_url: str,
                python_environment_id: int,
                python_environment_name: str,
                max_idle_time: int,
                max_uptime: int,
                start_timeout: int,
                h2o_cluster_address: str,
                h2o_cluster_password: str,
                context_path: str,
                application_id: str,
                idle_time: int,
                up_time: int,
    ):

        self.id=id
        self.cluster_state=cluster_state
        self.created_by=created_by
        self.created_at=created_at
        self.backend_type=backend_type
        self.is_saved=is_saved
        self.cluster_name=cluster_name
        self.profile_id=profile_id
        self.session_id=session_id
        self.h2o_version=h2o_version
        self.sparkling_version=sparkling_version
        self.profile_name=profile_name
        self.driver_cores=driver_cores
        self.driver_memory=driver_memory
        self.num_executors=num_executors
        self.executor_cores=executor_cores
        self.executor_memory=executor_memory
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.yarn_queue=yarn_queue
        self.h2o_engine_id=h2o_engine_id
        self.sparkling_engine_id=sparkling_engine_id
        self.spark_properties=spark_properties
        self.spark_ui_url=spark_ui_url
        self.driver_log_url=driver_log_url
        self.python_environment_id=python_environment_id
        self.python_environment_name=python_environment_name
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.start_timeout=start_timeout
        self.h2o_cluster_address=h2o_cluster_address
        self.h2o_cluster_password=h2o_cluster_password
        self.context_path=context_path
        self.application_id=application_id
        self.idle_time=idle_time
        self.up_time=up_time

    @classmethod
    def from_dict(cls,
             id,
             cluster_state,
             created_by,
             created_at,
             backend_type,
             is_saved,
             cluster_name,
             profile_id,
             session_id,
             h2o_version,
             sparkling_version,
             profile_name,
             driver_cores,
             driver_memory,
             num_executors,
             executor_cores,
             executor_memory,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             yarn_queue,
             h2o_engine_id,
             sparkling_engine_id,
             spark_properties,
             spark_ui_url,
             driver_log_url,
             python_environment_id,
             python_environment_name,
             max_idle_time,
             max_uptime,
             start_timeout,
             h2o_cluster_address,
             h2o_cluster_password,
             context_path,
             application_id,
             idle_time,
             up_time,
    ):

        return cls(
            id,
            cluster_state,
            created_by,
            created_at,
            backend_type,
            is_saved,
            cluster_name,
            profile_id,
            session_id,
            h2o_version,
            sparkling_version,
            profile_name,
            driver_cores,
            driver_memory,
            num_executors,
            executor_cores,
            executor_memory,
            h2o_nodes,
            h2o_memory,
            h2o_threads,
            h2o_extramempercent,
            yarn_queue,
            h2o_engine_id,
            sparkling_engine_id,
            spark_properties,
            spark_ui_url,
            driver_log_url,
            python_environment_id,
            python_environment_name,
            max_idle_time,
            max_uptime,
            start_timeout,
            h2o_cluster_address,
            h2o_cluster_password,
            context_path,
            application_id,
            idle_time,
            up_time,
        )

class SparklingClusterLogs(object):
    def __init__(self,
                session: str,
                h2o: str,
                yarn: str,
                hdfs: str,
    ):

        self.session=session
        self.h2o=h2o
        self.yarn=yarn
        self.hdfs=hdfs

    @classmethod
    def from_dict(cls,
             session,
             h2o,
             yarn,
             hdfs,
    ):

        return cls(
            session,
            h2o,
            yarn,
            hdfs,
        )

class LaunchSparklingClusterParameters(object):
    def __init__(self,
                cluster_name: str,
                profile_id: int,
                environment_id: int,
                driver_cores: int,
                driver_memory: int,
                num_executors: int,
                executor_cores: int,
                executor_memory: int,
                h2o_nodes: int,
                h2o_memory: int,
                h2o_threads: int,
                h2o_extramempercent: int,
                yarn_queue: str,
                h2o_engine_id: int,
                sparkling_engine_id: int,
                spark_properties: str,
                start_timeout: int,
                max_idle_time: int,
                max_uptime: int,
                rec_memory: int,
                rec_extra_memory_percent: int,
                save_cluster_data: bool,
                load_data_cluster_id: int,
    ):

        self.cluster_name=cluster_name
        self.profile_id=profile_id
        self.environment_id=environment_id
        self.driver_cores=driver_cores
        self.driver_memory=driver_memory
        self.num_executors=num_executors
        self.executor_cores=executor_cores
        self.executor_memory=executor_memory
        self.h2o_nodes=h2o_nodes
        self.h2o_memory=h2o_memory
        self.h2o_threads=h2o_threads
        self.h2o_extramempercent=h2o_extramempercent
        self.yarn_queue=yarn_queue
        self.h2o_engine_id=h2o_engine_id
        self.sparkling_engine_id=sparkling_engine_id
        self.spark_properties=spark_properties
        self.start_timeout=start_timeout
        self.max_idle_time=max_idle_time
        self.max_uptime=max_uptime
        self.rec_memory=rec_memory
        self.rec_extra_memory_percent=rec_extra_memory_percent
        self.save_cluster_data=save_cluster_data
        self.load_data_cluster_id=load_data_cluster_id

    @classmethod
    def from_dict(cls,
             cluster_name,
             profile_id,
             environment_id,
             driver_cores,
             driver_memory,
             num_executors,
             executor_cores,
             executor_memory,
             h2o_nodes,
             h2o_memory,
             h2o_threads,
             h2o_extramempercent,
             yarn_queue,
             h2o_engine_id,
             sparkling_engine_id,
             spark_properties,
             start_timeout,
             max_idle_time,
             max_uptime,
             rec_memory,
             rec_extra_memory_percent,
             save_cluster_data,
             load_data_cluster_id,
    ):

        return cls(
            cluster_name,
            profile_id,
            environment_id,
            driver_cores,
            driver_memory,
            num_executors,
            executor_cores,
            executor_memory,
            h2o_nodes,
            h2o_memory,
            h2o_threads,
            h2o_extramempercent,
            yarn_queue,
            h2o_engine_id,
            sparkling_engine_id,
            spark_properties,
            start_timeout,
            max_idle_time,
            max_uptime,
            rec_memory,
            rec_extra_memory_percent,
            save_cluster_data,
            load_data_cluster_id,
        )

class SparklingConfig(object):
    def __init__(self,
                enabled: bool,
                spark_home: str,
                override_hadoop_conf_dir: bool,
                java_home: str,
                internal_secure_connections: bool,
                allow_insecure_xgboost: bool,
                default_backend: str,
                extra_jars: str,
                r_enabled: bool,
                existing_livy: bool,
                existing_livy_url: str,
                jobname_prefix: str,
                use_sudospawner: bool,
                notebook_directory: str,
    ):

        self.enabled=enabled
        self.spark_home=spark_home
        self.override_hadoop_conf_dir=override_hadoop_conf_dir
        self.java_home=java_home
        self.internal_secure_connections=internal_secure_connections
        self.allow_insecure_xgboost=allow_insecure_xgboost
        self.default_backend=default_backend
        self.extra_jars=extra_jars
        self.r_enabled=r_enabled
        self.existing_livy=existing_livy
        self.existing_livy_url=existing_livy_url
        self.jobname_prefix=jobname_prefix
        self.use_sudospawner=use_sudospawner
        self.notebook_directory=notebook_directory

    @classmethod
    def from_dict(cls,
             enabled,
             spark_home,
             override_hadoop_conf_dir,
             java_home,
             internal_secure_connections,
             allow_insecure_xgboost,
             default_backend,
             extra_jars,
             r_enabled,
             existing_livy,
             existing_livy_url,
             jobname_prefix,
             use_sudospawner,
             notebook_directory,
    ):

        return cls(
            enabled,
            spark_home,
            override_hadoop_conf_dir,
            java_home,
            internal_secure_connections,
            allow_insecure_xgboost,
            default_backend,
            extra_jars,
            r_enabled,
            existing_livy,
            existing_livy_url,
            jobname_prefix,
            use_sudospawner,
            notebook_directory,
        )

class SparklingEngine(object):
    def __init__(self,
                id: int,
                name: str,
                h2o_version: str,
                location: str,
                created_at: int,
    ):

        self.id=id
        self.name=name
        self.h2o_version=h2o_version
        self.location=location
        self.created_at=created_at

    @classmethod
    def from_dict(cls,
             id,
             name,
             h2o_version,
             location,
             created_at,
    ):

        return cls(
            id,
            name,
            h2o_version,
            location,
            created_at,
        )

class PythonEnvironment(object):
    def __init__(self,
                id: int,
                name: str,
                pyspark_python_path: str,
                conda_pack_path: str,
                created_by: str,
                created_at: int,
                profile_ids: List[int],
                is_default: bool,
    ):

        self.id=id
        self.name=name
        self.pyspark_python_path=pyspark_python_path
        self.conda_pack_path=conda_pack_path
        self.created_by=created_by
        self.created_at=created_at
        self.profile_ids=profile_ids
        self.is_default=is_default

    @classmethod
    def from_dict(cls,
             id,
             name,
             pyspark_python_path,
             conda_pack_path,
             created_by,
             created_at,
             profile_ids,
             is_default,
    ):

        return cls(
            id,
            name,
            pyspark_python_path,
            conda_pack_path,
            created_by,
            created_at,
            profile_ids,
            is_default,
        )

class Profile(object):
    def __init__(self,
                id: int,
                name: str,
                created_at: int,
                user_groups: str,
                cluster_limit: int,
                profile_type: str,
                sparkling_internal: Optional[ProfileSparklingInternal],
                sparkling_external: Optional[ProfileSparklingExternal],
                h2o: Optional[ProfileH2o],
                driverless_kubernetes: Optional[ProfileDriverlessKubernetes],
                h2o_kubernetes: Optional[ProfileH2oKubernetes],
    ):

        self.id=id
        self.name=name
        self.created_at=created_at
        self.user_groups=user_groups
        self.cluster_limit=cluster_limit
        self.profile_type=profile_type
        self.sparkling_internal=sparkling_internal
        self.sparkling_external=sparkling_external
        self.h2o=h2o
        self.driverless_kubernetes=driverless_kubernetes
        self.h2o_kubernetes=h2o_kubernetes

    @classmethod
    def from_dict(cls,
             id,
             name,
             created_at,
             user_groups,
             cluster_limit,
             profile_type,
             sparkling_internal,
             sparkling_external,
             h2o,
             driverless_kubernetes,
             h2o_kubernetes,
    ):

        return cls(
            id,
            name,
            created_at,
            user_groups,
            cluster_limit,
            profile_type,
            sparkling_internal if sparkling_internal is None else ProfileSparklingInternal.from_dict(**sparkling_internal),
            sparkling_external if sparkling_external is None else ProfileSparklingExternal.from_dict(**sparkling_external),
            h2o if h2o is None else ProfileH2o.from_dict(**h2o),
            driverless_kubernetes if driverless_kubernetes is None else ProfileDriverlessKubernetes.from_dict(**driverless_kubernetes),
            h2o_kubernetes if h2o_kubernetes is None else ProfileH2oKubernetes.from_dict(**h2o_kubernetes),
        )

class ProfileUsage(object):
    def __init__(self,
                running_instances: int,
                cpu_count: int,
                gpu_count: int,
                memory_gb: int,
                storage_gb: int,
    ):

        self.running_instances=running_instances
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.storage_gb=storage_gb

    @classmethod
    def from_dict(cls,
             running_instances,
             cpu_count,
             gpu_count,
             memory_gb,
             storage_gb,
    ):

        return cls(
            running_instances,
            cpu_count,
            gpu_count,
            memory_gb,
            storage_gb,
        )

class DriverlessInstance(object):
    def __init__(self,
                id: int,
                turbine_id: str,
                profile_name: str,
                name: str,
                status: str,
                target_status: str,
                version: str,
                backend_type: str,
                instance_type: str,
                master_id: int,
                cpu_count: int,
                gpu_count: int,
                memory_gb: int,
                storage_gb: int,
                max_idle_seconds: int,
                max_uptime_seconds: int,
                timeout_seconds: int,
                address: str,
                authentication: str,
                password: str,
                created_at: int,
                started_at: int,
                created_by: str,
                current_uptime_seconds: int,
                current_idle_seconds: int,
                pod_latest_event: Optional[Event],
                service_latest_event: Optional[Event],
                pvc_latest_event: Optional[Event],
                stop_reason: str,
                config_toml: str,
                volumes: str,
    ):

        self.id=id
        self.turbine_id=turbine_id
        self.profile_name=profile_name
        self.name=name
        self.status=status
        self.target_status=target_status
        self.version=version
        self.backend_type=backend_type
        self.instance_type=instance_type
        self.master_id=master_id
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.storage_gb=storage_gb
        self.max_idle_seconds=max_idle_seconds
        self.max_uptime_seconds=max_uptime_seconds
        self.timeout_seconds=timeout_seconds
        self.address=address
        self.authentication=authentication
        self.password=password
        self.created_at=created_at
        self.started_at=started_at
        self.created_by=created_by
        self.current_uptime_seconds=current_uptime_seconds
        self.current_idle_seconds=current_idle_seconds
        self.pod_latest_event=pod_latest_event
        self.service_latest_event=service_latest_event
        self.pvc_latest_event=pvc_latest_event
        self.stop_reason=stop_reason
        self.config_toml=config_toml
        self.volumes=volumes

    @classmethod
    def from_dict(cls,
             id,
             turbine_id,
             profile_name,
             name,
             status,
             target_status,
             version,
             backend_type,
             instance_type,
             master_id,
             cpu_count,
             gpu_count,
             memory_gb,
             storage_gb,
             max_idle_seconds,
             max_uptime_seconds,
             timeout_seconds,
             address,
             authentication,
             password,
             created_at,
             started_at,
             created_by,
             current_uptime_seconds,
             current_idle_seconds,
             pod_latest_event,
             service_latest_event,
             pvc_latest_event,
             stop_reason,
             config_toml,
             volumes,
    ):

        return cls(
            id,
            turbine_id,
            profile_name,
            name,
            status,
            target_status,
            version,
            backend_type,
            instance_type,
            master_id,
            cpu_count,
            gpu_count,
            memory_gb,
            storage_gb,
            max_idle_seconds,
            max_uptime_seconds,
            timeout_seconds,
            address,
            authentication,
            password,
            created_at,
            started_at,
            created_by,
            current_uptime_seconds,
            current_idle_seconds,
            pod_latest_event if pod_latest_event is None else Event.from_dict(**pod_latest_event),
            service_latest_event if service_latest_event is None else Event.from_dict(**service_latest_event),
            pvc_latest_event if pvc_latest_event is None else Event.from_dict(**pvc_latest_event),
            stop_reason,
            config_toml,
            volumes,
        )

class LaunchDriverlessInstanceParameters(object):
    def __init__(self,
                name: str,
                profile_name: str,
                version: str,
                cpu_count: int,
                gpu_count: int,
                memory_gb: int,
                storage_gb: int,
                max_uptime_hours: int,
                max_idle_hours: int,
                timeout_seconds: int,
                config_toml: str,
                volumes: str,
    ):

        self.name=name
        self.profile_name=profile_name
        self.version=version
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.storage_gb=storage_gb
        self.max_uptime_hours=max_uptime_hours
        self.max_idle_hours=max_idle_hours
        self.timeout_seconds=timeout_seconds
        self.config_toml=config_toml
        self.volumes=volumes

    @classmethod
    def from_dict(cls,
             name,
             profile_name,
             version,
             cpu_count,
             gpu_count,
             memory_gb,
             storage_gb,
             max_uptime_hours,
             max_idle_hours,
             timeout_seconds,
             config_toml,
             volumes,
    ):

        return cls(
            name,
            profile_name,
            version,
            cpu_count,
            gpu_count,
            memory_gb,
            storage_gb,
            max_uptime_hours,
            max_idle_hours,
            timeout_seconds,
            config_toml,
            volumes,
        )

class DriverlessInstanceLogs(object):
    def __init__(self,
                dai: str,
                prev_logs: str,
                h2o: str,
                procsy: str,
                vis: str,
    ):

        self.dai=dai
        self.prev_logs=prev_logs
        self.h2o=h2o
        self.procsy=procsy
        self.vis=vis

    @classmethod
    def from_dict(cls,
             dai,
             prev_logs,
             h2o,
             procsy,
             vis,
    ):

        return cls(
            dai,
            prev_logs,
            h2o,
            procsy,
            vis,
        )

class DriverlessEngine(object):
    def __init__(self,
                version: str,
                major: int,
                minor: int,
                patch: int,
                fix: int,
                experimental: bool,
    ):

        self.version=version
        self.major=major
        self.minor=minor
        self.patch=patch
        self.fix=fix
        self.experimental=experimental

    @classmethod
    def from_dict(cls,
             version,
             major,
             minor,
             patch,
             fix,
             experimental,
    ):

        return cls(
            version,
            major,
            minor,
            patch,
            fix,
            experimental,
        )

class DriverlessConfig(object):
    def __init__(self,
                enabled: bool,
                backend_type: str,
                storage_directory: str,
                license: str,
                o_id_c_auth: bool,
                enable_triton: bool,
    ):

        self.enabled=enabled
        self.backend_type=backend_type
        self.storage_directory=storage_directory
        self.license=license
        self.o_id_c_auth=o_id_c_auth
        self.enable_triton=enable_triton

    @classmethod
    def from_dict(cls,
             enabled,
             backend_type,
             storage_directory,
             license,
             o_id_c_auth,
             enable_triton,
    ):

        return cls(
            enabled,
            backend_type,
            storage_directory,
            license,
            o_id_c_auth,
            enable_triton,
        )

class DriverlessClient(object):
    def __init__(self,
                version: str,
                created_at: int,
                is_outdated: bool,
    ):

        self.version=version
        self.created_at=created_at
        self.is_outdated=is_outdated

    @classmethod
    def from_dict(cls,
             version,
             created_at,
             is_outdated,
    ):

        return cls(
            version,
            created_at,
            is_outdated,
        )

class DriverlessKubernetesEngine(object):
    def __init__(self,
                version: str,
                image: str,
                image_pull_policy: str,
                image_pull_secret: str,
                created_at: int,
                experimental: bool,
    ):

        self.version=version
        self.image=image
        self.image_pull_policy=image_pull_policy
        self.image_pull_secret=image_pull_secret
        self.created_at=created_at
        self.experimental=experimental

    @classmethod
    def from_dict(cls,
             version,
             image,
             image_pull_policy,
             image_pull_secret,
             created_at,
             experimental,
    ):

        return cls(
            version,
            image,
            image_pull_policy,
            image_pull_secret,
            created_at,
            experimental,
        )

class LaunchDriverlessMultinodeParameters(object):
    def __init__(self,
                name: str,
                profile_name: str,
                version: str,
                master_cpu_count: int,
                master_gpu_count: int,
                master_memory_gb: int,
                master_storage_gb: int,
                worker_count: int,
                worker_cpu_count: int,
                worker_gpu_count: int,
                worker_memory_gb: int,
                worker_storage_gb: int,
                timeout_seconds: int,
                autoscaling_enabled: bool,
                autoscaling_min_workers: int,
                autoscaling_max_workers: int,
                autoscaling_buffer: int,
                autoscaling_downscale_delay_seconds: int,
    ):

        self.name=name
        self.profile_name=profile_name
        self.version=version
        self.master_cpu_count=master_cpu_count
        self.master_gpu_count=master_gpu_count
        self.master_memory_gb=master_memory_gb
        self.master_storage_gb=master_storage_gb
        self.worker_count=worker_count
        self.worker_cpu_count=worker_cpu_count
        self.worker_gpu_count=worker_gpu_count
        self.worker_memory_gb=worker_memory_gb
        self.worker_storage_gb=worker_storage_gb
        self.timeout_seconds=timeout_seconds
        self.autoscaling_enabled=autoscaling_enabled
        self.autoscaling_min_workers=autoscaling_min_workers
        self.autoscaling_max_workers=autoscaling_max_workers
        self.autoscaling_buffer=autoscaling_buffer
        self.autoscaling_downscale_delay_seconds=autoscaling_downscale_delay_seconds

    @classmethod
    def from_dict(cls,
             name,
             profile_name,
             version,
             master_cpu_count,
             master_gpu_count,
             master_memory_gb,
             master_storage_gb,
             worker_count,
             worker_cpu_count,
             worker_gpu_count,
             worker_memory_gb,
             worker_storage_gb,
             timeout_seconds,
             autoscaling_enabled,
             autoscaling_min_workers,
             autoscaling_max_workers,
             autoscaling_buffer,
             autoscaling_downscale_delay_seconds,
    ):

        return cls(
            name,
            profile_name,
            version,
            master_cpu_count,
            master_gpu_count,
            master_memory_gb,
            master_storage_gb,
            worker_count,
            worker_cpu_count,
            worker_gpu_count,
            worker_memory_gb,
            worker_storage_gb,
            timeout_seconds,
            autoscaling_enabled,
            autoscaling_min_workers,
            autoscaling_max_workers,
            autoscaling_buffer,
            autoscaling_downscale_delay_seconds,
        )

class DriverlessMultinode(object):
    def __init__(self,
                id: int,
                master_id: int,
                name: str,
                profile_name: str,
                master_status: str,
                master_target_status: str,
                version: str,
                master_cpu_count: int,
                master_gpu_count: int,
                master_memory_gb: int,
                master_storage_gb: int,
                worker_cpu_count: int,
                worker_gpu_count: int,
                worker_memory_gb: int,
                worker_storage_gb: int,
                autoscaling_enabled: bool,
                autoscaling_min_workers: int,
                autoscaling_max_workers: int,
                autoscaling_buffer: int,
                autoscaling_downscale_delay_seconds: int,
                target_worker_count: int,
                starting_worker_count: int,
                running_worker_count: int,
                stopping_worker_count: int,
                address: str,
                authentication: str,
                username: str,
                password: str,
                created_at: int,
                started_at: int,
    ):

        self.id=id
        self.master_id=master_id
        self.name=name
        self.profile_name=profile_name
        self.master_status=master_status
        self.master_target_status=master_target_status
        self.version=version
        self.master_cpu_count=master_cpu_count
        self.master_gpu_count=master_gpu_count
        self.master_memory_gb=master_memory_gb
        self.master_storage_gb=master_storage_gb
        self.worker_cpu_count=worker_cpu_count
        self.worker_gpu_count=worker_gpu_count
        self.worker_memory_gb=worker_memory_gb
        self.worker_storage_gb=worker_storage_gb
        self.autoscaling_enabled=autoscaling_enabled
        self.autoscaling_min_workers=autoscaling_min_workers
        self.autoscaling_max_workers=autoscaling_max_workers
        self.autoscaling_buffer=autoscaling_buffer
        self.autoscaling_downscale_delay_seconds=autoscaling_downscale_delay_seconds
        self.target_worker_count=target_worker_count
        self.starting_worker_count=starting_worker_count
        self.running_worker_count=running_worker_count
        self.stopping_worker_count=stopping_worker_count
        self.address=address
        self.authentication=authentication
        self.username=username
        self.password=password
        self.created_at=created_at
        self.started_at=started_at

    @classmethod
    def from_dict(cls,
             id,
             master_id,
             name,
             profile_name,
             master_status,
             master_target_status,
             version,
             master_cpu_count,
             master_gpu_count,
             master_memory_gb,
             master_storage_gb,
             worker_cpu_count,
             worker_gpu_count,
             worker_memory_gb,
             worker_storage_gb,
             autoscaling_enabled,
             autoscaling_min_workers,
             autoscaling_max_workers,
             autoscaling_buffer,
             autoscaling_downscale_delay_seconds,
             target_worker_count,
             starting_worker_count,
             running_worker_count,
             stopping_worker_count,
             address,
             authentication,
             username,
             password,
             created_at,
             started_at,
    ):

        return cls(
            id,
            master_id,
            name,
            profile_name,
            master_status,
            master_target_status,
            version,
            master_cpu_count,
            master_gpu_count,
            master_memory_gb,
            master_storage_gb,
            worker_cpu_count,
            worker_gpu_count,
            worker_memory_gb,
            worker_storage_gb,
            autoscaling_enabled,
            autoscaling_min_workers,
            autoscaling_max_workers,
            autoscaling_buffer,
            autoscaling_downscale_delay_seconds,
            target_worker_count,
            starting_worker_count,
            running_worker_count,
            stopping_worker_count,
            address,
            authentication,
            username,
            password,
            created_at,
            started_at,
        )

class SecurityConfig(object):
    def __init__(self,
                tls_cert_path: str,
                tls_key_path: str,
                server_strict_transport: str,
                server_x_xss_protection: str,
                server_content_security_policy: str,
                web_ui_timeout_min: int,
                disable_admin: bool,
                disable_jupyter: bool,
                session_duration_min: int,
                personal_access_token_duration_hours: int,
                allow_external_token_refresh: bool,
                global_url_prefix: str,
                secure_cookie: bool,
                support_email: str,
                strip_auth_errors: bool,
    ):

        self.tls_cert_path=tls_cert_path
        self.tls_key_path=tls_key_path
        self.server_strict_transport=server_strict_transport
        self.server_x_xss_protection=server_x_xss_protection
        self.server_content_security_policy=server_content_security_policy
        self.web_ui_timeout_min=web_ui_timeout_min
        self.disable_admin=disable_admin
        self.disable_jupyter=disable_jupyter
        self.session_duration_min=session_duration_min
        self.personal_access_token_duration_hours=personal_access_token_duration_hours
        self.allow_external_token_refresh=allow_external_token_refresh
        self.global_url_prefix=global_url_prefix
        self.secure_cookie=secure_cookie
        self.support_email=support_email
        self.strip_auth_errors=strip_auth_errors

    @classmethod
    def from_dict(cls,
             tls_cert_path,
             tls_key_path,
             server_strict_transport,
             server_x_xss_protection,
             server_content_security_policy,
             web_ui_timeout_min,
             disable_admin,
             disable_jupyter,
             session_duration_min,
             personal_access_token_duration_hours,
             allow_external_token_refresh,
             global_url_prefix,
             secure_cookie,
             support_email,
             strip_auth_errors,
    ):

        return cls(
            tls_cert_path,
            tls_key_path,
            server_strict_transport,
            server_x_xss_protection,
            server_content_security_policy,
            web_ui_timeout_min,
            disable_admin,
            disable_jupyter,
            session_duration_min,
            personal_access_token_duration_hours,
            allow_external_token_refresh,
            global_url_prefix,
            secure_cookie,
            support_email,
            strip_auth_errors,
        )

class LoggingConfig(object):
    def __init__(self,
                directory: str,
                level: int,
                permissions: str,
    ):

        self.directory=directory
        self.level=level
        self.permissions=permissions

    @classmethod
    def from_dict(cls,
             directory,
             level,
             permissions,
    ):

        return cls(
            directory,
            level,
            permissions,
        )

class ConfigMeta(object):
    def __init__(self,
                version: str,
                build: str,
                built: str,
                restart_pending: bool,
                support_email: str,
                license_valid: bool,
                is_hadoop_enabled: bool,
                is_kubernetes_enabled: bool,
                is_h2o_enabled: bool,
                is_h2o_running: bool,
                is_sparkling_enabled: bool,
                is_sparkling_running: bool,
                is_driverless_enabled: bool,
                is_driverless_running: bool,
                is_h2o_engine_uploaded: bool,
                is_h2o_kubernetes_engine_uploaded: bool,
                is_sparkling_engine_uploaded: bool,
                is_driverless_engine_uploaded: bool,
                driverless_backend_type: str,
                is_minio_enabled: bool,
                h2o_backend_type: str,
                inside_cluster: bool,
                deprecation_mode: bool,
    ):

        self.version=version
        self.build=build
        self.built=built
        self.restart_pending=restart_pending
        self.support_email=support_email
        self.license_valid=license_valid
        self.is_hadoop_enabled=is_hadoop_enabled
        self.is_kubernetes_enabled=is_kubernetes_enabled
        self.is_h2o_enabled=is_h2o_enabled
        self.is_h2o_running=is_h2o_running
        self.is_sparkling_enabled=is_sparkling_enabled
        self.is_sparkling_running=is_sparkling_running
        self.is_driverless_enabled=is_driverless_enabled
        self.is_driverless_running=is_driverless_running
        self.is_h2o_engine_uploaded=is_h2o_engine_uploaded
        self.is_h2o_kubernetes_engine_uploaded=is_h2o_kubernetes_engine_uploaded
        self.is_sparkling_engine_uploaded=is_sparkling_engine_uploaded
        self.is_driverless_engine_uploaded=is_driverless_engine_uploaded
        self.driverless_backend_type=driverless_backend_type
        self.is_minio_enabled=is_minio_enabled
        self.h2o_backend_type=h2o_backend_type
        self.inside_cluster=inside_cluster
        self.deprecation_mode=deprecation_mode

    @classmethod
    def from_dict(cls,
             version,
             build,
             built,
             restart_pending,
             support_email,
             license_valid,
             is_hadoop_enabled,
             is_kubernetes_enabled,
             is_h2o_enabled,
             is_h2o_running,
             is_sparkling_enabled,
             is_sparkling_running,
             is_driverless_enabled,
             is_driverless_running,
             is_h2o_engine_uploaded,
             is_h2o_kubernetes_engine_uploaded,
             is_sparkling_engine_uploaded,
             is_driverless_engine_uploaded,
             driverless_backend_type,
             is_minio_enabled,
             h2o_backend_type,
             inside_cluster,
             deprecation_mode,
    ):

        return cls(
            version,
            build,
            built,
            restart_pending,
            support_email,
            license_valid,
            is_hadoop_enabled,
            is_kubernetes_enabled,
            is_h2o_enabled,
            is_h2o_running,
            is_sparkling_enabled,
            is_sparkling_running,
            is_driverless_enabled,
            is_driverless_running,
            is_h2o_engine_uploaded,
            is_h2o_kubernetes_engine_uploaded,
            is_sparkling_engine_uploaded,
            is_driverless_engine_uploaded,
            driverless_backend_type,
            is_minio_enabled,
            h2o_backend_type,
            inside_cluster,
            deprecation_mode,
        )

class LicensingConfig(object):
    def __init__(self,
                license_manager_enabled: bool,
                license_manager_address: str,
                deprecation_mode: bool,
    ):

        self.license_manager_enabled=license_manager_enabled
        self.license_manager_address=license_manager_address
        self.deprecation_mode=deprecation_mode

    @classmethod
    def from_dict(cls,
             license_manager_enabled,
             license_manager_address,
             deprecation_mode,
    ):

        return cls(
            license_manager_enabled,
            license_manager_address,
            deprecation_mode,
        )

class Documentation(object):
    def __init__(self,
                id: int,
                name: str,
                private_name: str,
                link: str,
                section: str,
                created_at: int,
    ):

        self.id=id
        self.name=name
        self.private_name=private_name
        self.link=link
        self.section=section
        self.created_at=created_at

    @classmethod
    def from_dict(cls,
             id,
             name,
             private_name,
             link,
             section,
             created_at,
    ):

        return cls(
            id,
            name,
            private_name,
            link,
            section,
            created_at,
        )

class KubernetesVolume(object):
    def __init__(self,
                id: int,
                name: str,
                type: str,
                mount_path: str,
                read_only: bool,
                created_at: int,
                created_by: str,
                unbound: bool,
                volume_host_path: Optional[KubernetesVolumeHostPath],
                volume_secret: Optional[KubernetesVolumeSecret],
                volume_configmap: Optional[KubernetesVolumeConfigMap],
                volume_pvc: Optional[KubernetesVolumePvc],
                volume_nfs: Optional[KubernetesVolumeNfs],
                volume_csi: Optional[KubernetesVolumeCsi],
    ):

        self.id=id
        self.name=name
        self.type=type
        self.mount_path=mount_path
        self.read_only=read_only
        self.created_at=created_at
        self.created_by=created_by
        self.unbound=unbound
        self.volume_host_path=volume_host_path
        self.volume_secret=volume_secret
        self.volume_configmap=volume_configmap
        self.volume_pvc=volume_pvc
        self.volume_nfs=volume_nfs
        self.volume_csi=volume_csi

    @classmethod
    def from_dict(cls,
             id,
             name,
             type,
             mount_path,
             read_only,
             created_at,
             created_by,
             unbound,
             volume_host_path,
             volume_secret,
             volume_configmap,
             volume_pvc,
             volume_nfs,
             volume_csi,
    ):

        return cls(
            id,
            name,
            type,
            mount_path,
            read_only,
            created_at,
            created_by,
            unbound,
            volume_host_path if volume_host_path is None else KubernetesVolumeHostPath.from_dict(**volume_host_path),
            volume_secret if volume_secret is None else KubernetesVolumeSecret.from_dict(**volume_secret),
            volume_configmap if volume_configmap is None else KubernetesVolumeConfigMap.from_dict(**volume_configmap),
            volume_pvc if volume_pvc is None else KubernetesVolumePvc.from_dict(**volume_pvc),
            volume_nfs if volume_nfs is None else KubernetesVolumeNfs.from_dict(**volume_nfs),
            volume_csi if volume_csi is None else KubernetesVolumeCsi.from_dict(**volume_csi),
        )

class MinioConfig(object):
    def __init__(self,
                enabled: bool,
                endpoint_url: str,
                skip_cert_verification: bool,
                use_global_credentials: bool,
                access_key: str,
                secret_key: str,
    ):

        self.enabled=enabled
        self.endpoint_url=endpoint_url
        self.skip_cert_verification=skip_cert_verification
        self.use_global_credentials=use_global_credentials
        self.access_key=access_key
        self.secret_key=secret_key

    @classmethod
    def from_dict(cls,
             enabled,
             endpoint_url,
             skip_cert_verification,
             use_global_credentials,
             access_key,
             secret_key,
    ):

        return cls(
            enabled,
            endpoint_url,
            skip_cert_verification,
            use_global_credentials,
            access_key,
            secret_key,
        )

class PersonalMinioCredentials(object):
    def __init__(self,
                access_key: str,
                secret_key: str,
    ):

        self.access_key=access_key
        self.secret_key=secret_key

    @classmethod
    def from_dict(cls,
             access_key,
             secret_key,
    ):

        return cls(
            access_key,
            secret_key,
        )

class StorageConfig(object):
    def __init__(self,
                enabled: bool,
                address: str,
                oidc_scopes: str,
                tls_enabled: bool,
                tls_ca_secret_name: str,
                tls_ca_secret_data_crt: str,
                tls_client_secret_name: str,
                tls_client_secret_data_crt: str,
                tls_client_secret_data_key: str,
    ):

        self.enabled=enabled
        self.address=address
        self.oidc_scopes=oidc_scopes
        self.tls_enabled=tls_enabled
        self.tls_ca_secret_name=tls_ca_secret_name
        self.tls_ca_secret_data_crt=tls_ca_secret_data_crt
        self.tls_client_secret_name=tls_client_secret_name
        self.tls_client_secret_data_crt=tls_client_secret_data_crt
        self.tls_client_secret_data_key=tls_client_secret_data_key

    @classmethod
    def from_dict(cls,
             enabled,
             address,
             oidc_scopes,
             tls_enabled,
             tls_ca_secret_name,
             tls_ca_secret_data_crt,
             tls_client_secret_name,
             tls_client_secret_data_crt,
             tls_client_secret_data_key,
    ):

        return cls(
            enabled,
            address,
            oidc_scopes,
            tls_enabled,
            tls_ca_secret_name,
            tls_ca_secret_data_crt,
            tls_client_secret_name,
            tls_client_secret_data_crt,
            tls_client_secret_data_key,
        )

class OidcTokenProvider(object):
    def __init__(self,
                enabled: bool,
                access_token: str,
                refresh_token: str,
                client_id: str,
                client_secret: str,
                token_endpoint_url: str,
                token_introspection_url: str,
                expires_at: int,
    ):

        self.enabled=enabled
        self.access_token=access_token
        self.refresh_token=refresh_token
        self.client_id=client_id
        self.client_secret=client_secret
        self.token_endpoint_url=token_endpoint_url
        self.token_introspection_url=token_introspection_url
        self.expires_at=expires_at

    @classmethod
    def from_dict(cls,
             enabled,
             access_token,
             refresh_token,
             client_id,
             client_secret,
             token_endpoint_url,
             token_introspection_url,
             expires_at,
    ):

        return cls(
            enabled,
            access_token,
            refresh_token,
            client_id,
            client_secret,
            token_endpoint_url,
            token_introspection_url,
            expires_at,
        )

class H2oKubernetesCluster(object):
    def __init__(self,
                id: int,
                profile_name: str,
                name: str,
                status: str,
                target_status: str,
                version: str,
                node_count: int,
                cpu_count: int,
                gpu_count: int,
                memory_gb: int,
                max_idle_hours: int,
                max_uptime_hours: int,
                timeout_seconds: int,
                context_path: str,
                created_at: int,
                created_by: str,
                current_uptime_millis: int,
                current_idle_millis: int,
                volumes: str,
    ):

        self.id=id
        self.profile_name=profile_name
        self.name=name
        self.status=status
        self.target_status=target_status
        self.version=version
        self.node_count=node_count
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.max_idle_hours=max_idle_hours
        self.max_uptime_hours=max_uptime_hours
        self.timeout_seconds=timeout_seconds
        self.context_path=context_path
        self.created_at=created_at
        self.created_by=created_by
        self.current_uptime_millis=current_uptime_millis
        self.current_idle_millis=current_idle_millis
        self.volumes=volumes

    @classmethod
    def from_dict(cls,
             id,
             profile_name,
             name,
             status,
             target_status,
             version,
             node_count,
             cpu_count,
             gpu_count,
             memory_gb,
             max_idle_hours,
             max_uptime_hours,
             timeout_seconds,
             context_path,
             created_at,
             created_by,
             current_uptime_millis,
             current_idle_millis,
             volumes,
    ):

        return cls(
            id,
            profile_name,
            name,
            status,
            target_status,
            version,
            node_count,
            cpu_count,
            gpu_count,
            memory_gb,
            max_idle_hours,
            max_uptime_hours,
            timeout_seconds,
            context_path,
            created_at,
            created_by,
            current_uptime_millis,
            current_idle_millis,
            volumes,
        )

class LaunchH2oKubernetesClusterParameters(object):
    def __init__(self,
                name: str,
                profile_name: str,
                version: str,
                node_count: int,
                cpu_count: int,
                gpu_count: int,
                memory_gb: int,
                max_idle_hours: int,
                max_uptime_hours: int,
                timeout_seconds: int,
                rec_memory: int,
                volumes: str,
    ):

        self.name=name
        self.profile_name=profile_name
        self.version=version
        self.node_count=node_count
        self.cpu_count=cpu_count
        self.gpu_count=gpu_count
        self.memory_gb=memory_gb
        self.max_idle_hours=max_idle_hours
        self.max_uptime_hours=max_uptime_hours
        self.timeout_seconds=timeout_seconds
        self.rec_memory=rec_memory
        self.volumes=volumes

    @classmethod
    def from_dict(cls,
             name,
             profile_name,
             version,
             node_count,
             cpu_count,
             gpu_count,
             memory_gb,
             max_idle_hours,
             max_uptime_hours,
             timeout_seconds,
             rec_memory,
             volumes,
    ):

        return cls(
            name,
            profile_name,
            version,
            node_count,
            cpu_count,
            gpu_count,
            memory_gb,
            max_idle_hours,
            max_uptime_hours,
            timeout_seconds,
            rec_memory,
            volumes,
        )

class H2oK8sLogs(object):
    def __init__(self,
                logs: str,
                prev_logs: str,
    ):

        self.logs=logs
        self.prev_logs=prev_logs

    @classmethod
    def from_dict(cls,
             logs,
             prev_logs,
    ):

        return cls(
            logs,
            prev_logs,
        )

class H2oKubernetesEngine(object):
    def __init__(self,
                version: str,
                image: str,
                image_pull_policy: str,
                image_pull_secret: str,
                created_at: int,
                experimental: bool,
    ):

        self.version=version
        self.image=image
        self.image_pull_policy=image_pull_policy
        self.image_pull_secret=image_pull_secret
        self.created_at=created_at
        self.experimental=experimental

    @classmethod
    def from_dict(cls,
             version,
             image,
             image_pull_policy,
             image_pull_secret,
             created_at,
             experimental,
    ):

        return cls(
            version,
            image,
            image_pull_policy,
            image_pull_secret,
            created_at,
            experimental,
        )

class H2oClusterConnectParams(object):
    def __init__(self,
                https: bool,
                verify_ssl_certificates: bool,
                context_path: str,
                cookies: List[str],
                ip: str,
                port: int,
    ):

        self.https=https
        self.verify_ssl_certificates=verify_ssl_certificates
        self.context_path=context_path
        self.cookies=cookies
        self.ip=ip
        self.port=port

    @classmethod
    def from_dict(cls,
             https,
             verify_ssl_certificates,
             context_path,
             cookies,
             ip,
             port,
    ):

        return cls(
            https,
            verify_ssl_certificates,
            context_path,
            cookies,
            ip,
            port,
        )



class TypedSteamApi:

    @staticmethod
    def __to_dict(obj):
        return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

    

    def priority_list(self, ) -> Tuple[ProfileValue, ProfileH2o, ProfileSparklingInternal, ProfileSparklingExternal, ProfileH2oKubernetes, ProfileDriverlessKubernetes, Permission, Event, KubernetesVolumeHostPath, KubernetesVolumeSecret, KubernetesVolumeConfigMap, KubernetesVolumePvc, KubernetesVolumeNfs, KubernetesVolumeCsi]:
        """
        Dummy method to discover structs in a correct order for Python API

        Parameters:

        Returns:
        a: No description available (ProfileValue)
        b: No description available (ProfileH2o)
        c: No description available (ProfileSparklingInternal)
        d: No description available (ProfileSparklingExternal)
        e: No description available (ProfileH2oKubernetes)
        f: No description available (ProfileDriverlessKubernetes)
        g: No description available (Permission)
        h: No description available (Event)
        i: No description available (KubernetesVolumeHostPath)
        j: No description available (KubernetesVolumeSecret)
        k: No description available (KubernetesVolumeConfigMap)
        l: No description available (KubernetesVolumePvc)
        m: No description available (KubernetesVolumeNfs)
        n: No description available (KubernetesVolumeCsi)
        """
        request = {
        }
        response = self.call("PriorityList", request)
        output_a=ProfileValue.from_dict(**response['a'])
        output_b=ProfileH2o.from_dict(**response['b'])
        output_c=ProfileSparklingInternal.from_dict(**response['c'])
        output_d=ProfileSparklingExternal.from_dict(**response['d'])
        output_e=ProfileH2oKubernetes.from_dict(**response['e'])
        output_f=ProfileDriverlessKubernetes.from_dict(**response['f'])
        output_g=Permission.from_dict(**response['g'])
        output_h=Event.from_dict(**response['h'])
        output_i=KubernetesVolumeHostPath.from_dict(**response['i'])
        output_j=KubernetesVolumeSecret.from_dict(**response['j'])
        output_k=KubernetesVolumeConfigMap.from_dict(**response['k'])
        output_l=KubernetesVolumePvc.from_dict(**response['l'])
        output_m=KubernetesVolumeNfs.from_dict(**response['m'])
        output_n=KubernetesVolumeCsi.from_dict(**response['n'])

        return output_a, output_b, output_c, output_d, output_e, output_f, output_g, output_h, output_i, output_j, output_k, output_l, output_m, output_n
    

    def ping_server(self, input: str) -> str:
        """
        Ping the Enterprise Steam server

        Parameters:
        input: Message to send (string)

        Returns:
        output: Version of the Python/R API (string)
        """
        request = {
            'input': TypedSteamApi.__to_dict(input)
        }
        response = self.call("PingServer", request)
        output_output=response['output']

        return output_output
    

    def get_config(self, ) -> Config:
        """
        Get Enterprise Steam start up configurations

        Parameters:

        Returns:
        config: An object containing Enterprise Steam startup configurations (Config)
        """
        request = {
        }
        response = self.call("GetConfig", request)
        output_config=Config.from_dict(**response['config'])

        return output_config
    

    def set_authentication(self, enabled_type: str, ldap: LdapConfig, saml: SamlConfig, pam: PamConfig, oidc: OidcConfig) -> None:
        """
        Set authentication config

        Parameters:
        enabled_type: No description available (string)
        ldap: No description available (LdapConfig)
        saml: No description available (SamlConfig)
        pam: No description available (PamConfig)
        oidc: No description available (OidcConfig)

        Returns:None
        """
        request = {
            'enabled_type': TypedSteamApi.__to_dict(enabled_type),
            'ldap': TypedSteamApi.__to_dict(ldap),
            'saml': TypedSteamApi.__to_dict(saml),
            'pam': TypedSteamApi.__to_dict(pam),
            'oidc': TypedSteamApi.__to_dict(oidc)
        }
        response = self.call("SetAuthentication", request)

        return None
    

    def get_authentication(self, ) -> Tuple[str, LdapConfig, SamlConfig, PamConfig, OidcConfig]:
        """
        Get authentication config

        Parameters:

        Returns:
        enabled_type: No description available (string)
        ldap: No description available (LdapConfig)
        saml: No description available (SamlConfig)
        pam: No description available (PamConfig)
        oidc: No description available (OidcConfig)
        """
        request = {
        }
        response = self.call("GetAuthentication", request)
        output_enabled_type=response['enabled_type']
        output_ldap=LdapConfig.from_dict(**response['ldap'])
        output_saml=SamlConfig.from_dict(**response['saml'])
        output_pam=PamConfig.from_dict(**response['pam'])
        output_oidc=OidcConfig.from_dict(**response['oidc'])

        return output_enabled_type, output_ldap, output_saml, output_pam, output_oidc
    

    def create_ldap_connection(self, ldap: LdapConnection) -> int:
        """
        Create new Ldap connection

        Parameters:
        ldap: No description available (LdapConnection)

        Returns:
        id: No description available (int64)
        """
        request = {
            'ldap': TypedSteamApi.__to_dict(ldap)
        }
        response = self.call("CreateLdapConnection", request)
        output_id=response['id']

        return output_id
    

    def get_ldap_connections(self, ) -> List[LdapConnection]:
        """
        Get existing ldap connections

        Parameters:

        Returns:
        connections: No description available (LdapConnection)
        """
        request = {
        }
        response = self.call("GetLdapConnections", request)
        output_connections=[]
        for i in response['connections']:
             output_connections.append(LdapConnection(**i))

        return output_connections
    

    def update_ldap_connection(self, ldap: LdapConnection) -> None:
        """
        Update existing ldap connection

        Parameters:
        ldap: No description available (LdapConnection)

        Returns:None
        """
        request = {
            'ldap': TypedSteamApi.__to_dict(ldap)
        }
        response = self.call("UpdateLdapConnection", request)

        return None
    

    def delete_ldap_connection(self, id: int) -> None:
        """
        Delete existing ldap connection

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id)
        }
        response = self.call("DeleteLdapConnection", request)

        return None
    

    def swap_ldap_connection_priorities(self, id_a: int, id_b: int) -> None:
        """
        Swap priorities between two ldap connections

        Parameters:
        id_a: No description available (int64)
        id_b: No description available (int64)

        Returns:None
        """
        request = {
            'id_a': TypedSteamApi.__to_dict(id_a),
            'id_b': TypedSteamApi.__to_dict(id_b)
        }
        response = self.call("SwapLdapConnectionPriorities", request)

        return None
    

    def test_ldap_config(self, config: LdapConfig) -> Tuple[int, List[LdapGroup]]:
        """
        Test LDAP security configurations

        Parameters:
        config: No description available (LdapConfig)

        Returns:
        count: No description available (int)
        groups: No description available (LdapGroup)
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("TestLdapConfig", request)
        output_count=response['count']
        output_groups=[]
        for i in response['groups']:
             output_groups.append(LdapGroup(**i))

        return output_count, output_groups
    

    def get_roles_config(self, ) -> RolesConfig:
        """
        Get roles config

        Parameters:

        Returns:
        config: No description available (RolesConfig)
        """
        request = {
        }
        response = self.call("GetRolesConfig", request)
        output_config=RolesConfig.from_dict(**response['config'])

        return output_config
    

    def set_roles_config(self, config: RolesConfig) -> None:
        """
        Set roles config

        Parameters:
        config: No description available (RolesConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetRolesConfig", request)

        return None
    

    def get_auth_type(self, ) -> str:
        """
        Get enabled auth type

        Parameters:

        Returns:
        enabled_type: No description available (string)
        """
        request = {
        }
        response = self.call("GetAuthType", request)
        output_enabled_type=response['enabled_type']

        return output_enabled_type
    

    def set_hadoop_config(self, config: HadoopConfig) -> None:
        """
        Set configuration for YARN deployment backend

        Parameters:
        config: No description available (HadoopConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetHadoopConfig", request)

        return None
    

    def get_hadoop_config(self, ) -> Tuple[HadoopConfig, HadoopInfo]:
        """
        Get configuration for YARN deployment backend

        Parameters:

        Returns:
        config: No description available (HadoopConfig)
        hadoop_info: No description available (HadoopInfo)
        """
        request = {
        }
        response = self.call("GetHadoopConfig", request)
        output_config=HadoopConfig.from_dict(**response['config'])
        output_hadoop_info=HadoopInfo.from_dict(**response['hadoop_info'])

        return output_config, output_hadoop_info
    

    def test_generate_hive_token(self, username: str) -> None:
        """
        Test generation of Hive token

        Parameters:
        username: No description available (string)

        Returns:None
        """
        request = {
            'username': TypedSteamApi.__to_dict(username)
        }
        response = self.call("TestGenerateHiveToken", request)

        return None
    

    def set_kubernetes_config(self, config: KubernetesConfig) -> None:
        """
        Set configuration for Kubernetes deployment backend

        Parameters:
        config: No description available (KubernetesConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetKubernetesConfig", request)

        return None
    

    def get_kubernetes_config(self, ) -> Tuple[KubernetesConfig, KubernetesInfo]:
        """
        Get configuration for Kubernetes deployment backend

        Parameters:

        Returns:
        config: No description available (KubernetesConfig)
        kubernetes_info: No description available (KubernetesInfo)
        """
        request = {
        }
        response = self.call("GetKubernetesConfig", request)
        output_config=KubernetesConfig.from_dict(**response['config'])
        output_kubernetes_info=KubernetesInfo.from_dict(**response['kubernetes_info'])

        return output_config, output_kubernetes_info
    

    def set_kubernetes_hdfs_config(self, config: KubernetesHdfsConfig) -> None:
        """
        Set configuration for HDFS on Kubernetes

        Parameters:
        config: No description available (KubernetesHdfsConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetKubernetesHdfsConfig", request)

        return None
    

    def get_kubernetes_hdfs_config(self, ) -> KubernetesHdfsConfig:
        """
        Get configuration for HDFS on Kubernetes

        Parameters:

        Returns:
        config: No description available (KubernetesHdfsConfig)
        """
        request = {
        }
        response = self.call("GetKubernetesHdfsConfig", request)
        output_config=KubernetesHdfsConfig.from_dict(**response['config'])

        return output_config
    

    def create_h2o_startup_parameter(self, parameter: NewH2oStartupParameter) -> None:
        """
        Create a global startup parameter for launching H2O clusters

        Parameters:
        parameter: No description available (NewH2oStartupParameter)

        Returns:None
        """
        request = {
            'parameter': TypedSteamApi.__to_dict(parameter)
        }
        response = self.call("CreateH2oStartupParameter", request)

        return None
    

    def get_h2o_startup_parameters(self, ) -> List[H2oStartupParameter]:
        """
        Get a global startup parameter for launching H2O clusters

        Parameters:

        Returns:
        parameter: No description available (H2oStartupParameter)
        """
        request = {
        }
        response = self.call("GetH2oStartupParameters", request)
        output_parameter=[]
        for i in response['parameter']:
             output_parameter.append(H2oStartupParameter(**i))

        return output_parameter
    

    def update_h2o_startup_parameter(self, id: int, parameter: NewH2oStartupParameter) -> None:
        """
        Update a global startup parameter for launching H2O clusters

        Parameters:
        id: No description available (int64)
        parameter: No description available (NewH2oStartupParameter)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id),
            'parameter': TypedSteamApi.__to_dict(parameter)
        }
        response = self.call("UpdateH2oStartupParameter", request)

        return None
    

    def remove_h2o_startup_parameter(self, id: int) -> None:
        """
        Delete a global startup parameter for launching H2O clusters

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id)
        }
        response = self.call("RemoveH2oStartupParameter", request)

        return None
    

    def launch_h2o_cluster(self, parameters: LaunchH2oClusterParameters) -> int:
        """
        Launch H2O cluster

        Parameters:
        parameters: No description available (LaunchH2oClusterParameters)

        Returns:
        id: No description available (int64)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("LaunchH2oCluster", request)
        output_id=response['id']

        return output_id
    

    def start_h2o_cluster(self, id: int, parameters: LaunchH2oClusterParameters) -> None:
        """
        Start stopped H2O cluster

        Parameters:
        id: No description available (int64)
        parameters: No description available (LaunchH2oClusterParameters)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id),
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("StartH2oCluster", request)

        return None
    

    def get_h2o_clusters(self, ) -> List[H2oCluster]:
        """
        Get all my H2O clusters

        Parameters:

        Returns:
        clusters: No description available (H2oCluster)
        """
        request = {
        }
        response = self.call("GetH2oClusters", request)
        output_clusters=[]
        for i in response['clusters']:
             output_clusters.append(H2oCluster(**i))

        return output_clusters
    

    def get_h2o_cluster(self, cluster_id: int) -> H2oCluster:
        """
        Get H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (H2oCluster)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("GetH2oCluster", request)
        output_cluster=H2oCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def get_h2o_cluster_by_name(self, name: str) -> H2oCluster:
        """
        Get H2O cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (H2oCluster)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetH2oClusterByName", request)
        output_cluster=H2oCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def stop_h2o_cluster(self, cluster_id: int, should_save: bool) -> None:
        """
        Stop H2O cluster

        Parameters:
        cluster_id: No description available (int64)
        should_save: No description available (bool)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id),
            'should_save': TypedSteamApi.__to_dict(should_save)
        }
        response = self.call("StopH2oCluster", request)

        return None
    

    def fail_h2o_cluster(self, cluster_id: int) -> None:
        """
        Mark H2O cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("FailH2oCluster", request)

        return None
    

    def delete_h2o_cluster(self, cluster_id: int) -> None:
        """
        Delete H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("DeleteH2oCluster", request)

        return None
    

    def get_h2o_cluster_logs(self, cluster_id: int) -> H2oClusterLogs:
        """
        Get H2O cluster logs

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        logs: No description available (H2oClusterLogs)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("GetH2oClusterLogs", request)
        output_logs=H2oClusterLogs.from_dict(**response['logs'])

        return output_logs
    

    def get_h2o_config(self, ) -> H2oConfig:
        """
        Get H2O configuration

        Parameters:

        Returns:
        config: No description available (H2oConfig)
        """
        request = {
        }
        response = self.call("GetH2oConfig", request)
        output_config=H2oConfig.from_dict(**response['config'])

        return output_config
    

    def set_h2o_config(self, config: H2oConfig) -> None:
        """
        Set H2O configuration

        Parameters:
        config: No description available (H2oConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetH2oConfig", request)

        return None
    

    def import_h2o_engine(self, path: str) -> None:
        """
        Import engine from server path

        Parameters:
        path: No description available (string)

        Returns:None
        """
        request = {
            'path': TypedSteamApi.__to_dict(path)
        }
        response = self.call("ImportH2oEngine", request)

        return None
    

    def get_h2o_engine(self, engine_id: int) -> H2oEngine:
        """
        Get H2O engine details

        Parameters:
        engine_id: No description available (int64)

        Returns:
        engine: No description available (H2oEngine)
        """
        request = {
            'engine_id': TypedSteamApi.__to_dict(engine_id)
        }
        response = self.call("GetH2oEngine", request)
        output_engine=H2oEngine.from_dict(**response['engine'])

        return output_engine
    

    def get_h2o_engine_by_version(self, version: str) -> H2oEngine:
        """
        Get an H2O engine by a version substring

        Parameters:
        version: No description available (string)

        Returns:
        engine: No description available (H2oEngine)
        """
        request = {
            'version': TypedSteamApi.__to_dict(version)
        }
        response = self.call("GetH2oEngineByVersion", request)
        output_engine=H2oEngine.from_dict(**response['engine'])

        return output_engine
    

    def get_h2o_engines(self, ) -> List[H2oEngine]:
        """
        List H2O engines

        Parameters:

        Returns:
        engines: No description available (H2oEngine)
        """
        request = {
        }
        response = self.call("GetH2oEngines", request)
        output_engines=[]
        for i in response['engines']:
             output_engines.append(H2oEngine(**i))

        return output_engines
    

    def delete_h2o_engine(self, engine_id: int) -> None:
        """
        Delete an H2O engine

        Parameters:
        engine_id: No description available (int64)

        Returns:None
        """
        request = {
            'engine_id': TypedSteamApi.__to_dict(engine_id)
        }
        response = self.call("DeleteH2oEngine", request)

        return None
    

    def get_all_entity_types(self, ) -> List[EntityType]:
        """
        List all entity types

        Parameters:

        Returns:
        entity_types: A list of Enterprise Steam entity types. (EntityType)
        """
        request = {
        }
        response = self.call("GetAllEntityTypes", request)
        output_entity_types=[]
        for i in response['entity_types']:
             output_entity_types.append(EntityType(**i))

        return output_entity_types
    

    def get_all_permissions(self, ) -> List[Permission]:
        """
        List all permissions

        Parameters:

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
        }
        response = self.call("GetAllPermissions", request)
        output_permissions=[]
        for i in response['permissions']:
             output_permissions.append(Permission(**i))

        return output_permissions
    

    def get_permissions_for_role(self, role_id: int) -> List[Permission]:
        """
        List permissions for a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("GetPermissionsForRole", request)
        output_permissions=[]
        for i in response['permissions']:
             output_permissions.append(Permission(**i))

        return output_permissions
    

    def get_permissions_for_identity(self, identity_id: int) -> List[Permission]:
        """
        List permissions for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        permissions: A list of Enterprise Steam permissions. (Permission)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("GetPermissionsForIdentity", request)
        output_permissions=[]
        for i in response['permissions']:
             output_permissions.append(Permission(**i))

        return output_permissions
    

    def get_estimated_cluster_memory(self, parameters: DatasetParameters) -> EstimatedClusterMemory:
        """
        Get estimated cluster memory

        Parameters:
        parameters: No description available (DatasetParameters)

        Returns:
        cluster_memory: No description available (EstimatedClusterMemory)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("GetEstimatedClusterMemory", request)
        output_cluster_memory=EstimatedClusterMemory.from_dict(**response['cluster_memory'])

        return output_cluster_memory
    

    def create_role(self, name: str, description: str) -> int:
        """
        Create a role

        Parameters:
        name: A string name. (string)
        description: A string description (string)

        Returns:
        role_id: Integer ID of the role in Enterprise Steam. (int64)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name),
            'description': TypedSteamApi.__to_dict(description)
        }
        response = self.call("CreateRole", request)
        output_role_id=response['role_id']

        return output_role_id
    

    def get_roles(self, offset: int, limit: int) -> List[Role]:
        """
        List roles

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        roles: A list of Enterprise Steam roles. (Role)
        """
        request = {
            'offset': TypedSteamApi.__to_dict(offset),
            'limit': TypedSteamApi.__to_dict(limit)
        }
        response = self.call("GetRoles", request)
        output_roles=[]
        for i in response['roles']:
             output_roles.append(Role(**i))

        return output_roles
    

    def get_roles_for_identity(self, identity_id: int) -> List[Role]:
        """
        List roles for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        roles: A list of Enterprise Steam roles. (Role)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("GetRolesForIdentity", request)
        output_roles=[]
        for i in response['roles']:
             output_roles.append(Role(**i))

        return output_roles
    

    def get_role(self, role_id: int) -> Role:
        """
        Get role details

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        role: A Enterprise Steam role. (Role)
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("GetRole", request)
        output_role=Role.from_dict(**response['role'])

        return output_role
    

    def get_role_by_name(self, name: str) -> Role:
        """
        Get role details by name

        Parameters:
        name: A role name. (string)

        Returns:
        role: A Enterprise Steam role. (Role)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetRoleByName", request)
        output_role=Role.from_dict(**response['role'])

        return output_role
    

    def update_role(self, role_id: int, name: str, description: str) -> None:
        """
        Update a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        name: A string name. (string)
        description: A string description (string)

        Returns:None
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id),
            'name': TypedSteamApi.__to_dict(name),
            'description': TypedSteamApi.__to_dict(description)
        }
        response = self.call("UpdateRole", request)

        return None
    

    def delete_role(self, role_id: int) -> None:
        """
        Delete a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("DeleteRole", request)

        return None
    

    def link_role_with_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        """
        Link a role with permissions

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_ids: A list of Integer IDs for permissions in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id),
            'permission_ids': TypedSteamApi.__to_dict(permission_ids)
        }
        response = self.call("LinkRoleWithPermissions", request)

        return None
    

    def link_role_with_permission(self, role_id: int, permission_id: int) -> None:
        """
        Link a role with a permission

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_id: Integer ID of a permission in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id),
            'permission_id': TypedSteamApi.__to_dict(permission_id)
        }
        response = self.call("LinkRoleWithPermission", request)

        return None
    

    def unlink_role_from_permission(self, role_id: int, permission_id: int) -> None:
        """
        Unlink a role from a permission

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)
        permission_id: Integer ID of a permission in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id),
            'permission_id': TypedSteamApi.__to_dict(permission_id)
        }
        response = self.call("UnlinkRoleFromPermission", request)

        return None
    

    def create_workgroup(self, name: str, description: str) -> int:
        """
        Create a workgroup

        Parameters:
        name: A string name. (string)
        description: A string description (string)

        Returns:
        workgroup_id: Integer ID of the workgroup in Enterprise Steam. (int64)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name),
            'description': TypedSteamApi.__to_dict(description)
        }
        response = self.call("CreateWorkgroup", request)
        output_workgroup_id=response['workgroup_id']

        return output_workgroup_id
    

    def get_workgroups(self, offset: int, limit: int) -> List[Workgroup]:
        """
        List workgroups

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        workgroups: A list of workgroups in Enterprise Steam. (Workgroup)
        """
        request = {
            'offset': TypedSteamApi.__to_dict(offset),
            'limit': TypedSteamApi.__to_dict(limit)
        }
        response = self.call("GetWorkgroups", request)
        output_workgroups=[]
        for i in response['workgroups']:
             output_workgroups.append(Workgroup(**i))

        return output_workgroups
    

    def get_workgroups_for_identity(self, identity_id: int) -> List[Workgroup]:
        """
        List workgroups for an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        workgroups: A list of workgroups in Enterprise Steam. (Workgroup)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("GetWorkgroupsForIdentity", request)
        output_workgroups=[]
        for i in response['workgroups']:
             output_workgroups.append(Workgroup(**i))

        return output_workgroups
    

    def get_workgroup(self, workgroup_id: int) -> Workgroup:
        """
        Get workgroup details

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:
        workgroup: A workgroup in Enterprise Steam. (Workgroup)
        """
        request = {
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id)
        }
        response = self.call("GetWorkgroup", request)
        output_workgroup=Workgroup.from_dict(**response['workgroup'])

        return output_workgroup
    

    def get_workgroup_by_name(self, name: str) -> Workgroup:
        """
        Get workgroup details by name

        Parameters:
        name: A string name. (string)

        Returns:
        workgroup: A workgroup in Enterprise Steam. (Workgroup)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetWorkgroupByName", request)
        output_workgroup=Workgroup.from_dict(**response['workgroup'])

        return output_workgroup
    

    def update_workgroup(self, workgroup_id: int, name: str, description: str) -> None:
        """
        Update a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgrou in Enterprise Steam. (int64)
        name: A string name. (string)
        description: A string description (string)

        Returns:None
        """
        request = {
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id),
            'name': TypedSteamApi.__to_dict(name),
            'description': TypedSteamApi.__to_dict(description)
        }
        response = self.call("UpdateWorkgroup", request)

        return None
    

    def delete_workgroup(self, workgroup_id: int) -> None:
        """
        Delete a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id)
        }
        response = self.call("DeleteWorkgroup", request)

        return None
    

    def create_identity(self, name: str, password: str, yarn_queue: str) -> int:
        """
        Create an identity

        Parameters:
        name: A string name. (string)
        password: A string password (string)
        yarn_queue: No description available (string)

        Returns:
        identity_id: Integer ID of the identity in Enterprise Steam. (int64)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name),
            'password': TypedSteamApi.__to_dict(password),
            'yarn_queue': TypedSteamApi.__to_dict(yarn_queue)
        }
        response = self.call("CreateIdentity", request)
        output_identity_id=response['identity_id']

        return output_identity_id
    

    def get_identities(self, offset: int, limit: int) -> List[Identity]:
        """
        List identities

        Parameters:
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'offset': TypedSteamApi.__to_dict(offset),
            'limit': TypedSteamApi.__to_dict(limit)
        }
        response = self.call("GetIdentities", request)
        output_identities=[]
        for i in response['identities']:
             output_identities.append(Identity(**i))

        return output_identities
    

    def get_identities_for_workgroup(self, workgroup_id: int) -> List[Identity]:
        """
        List identities for a workgroup

        Parameters:
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id)
        }
        response = self.call("GetIdentitiesForWorkgroup", request)
        output_identities=[]
        for i in response['identities']:
             output_identities.append(Identity(**i))

        return output_identities
    

    def get_identities_for_role(self, role_id: int) -> List[Identity]:
        """
        List identities for a role

        Parameters:
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:
        identities: A list of identities in Enterprise Steam. (Identity)
        """
        request = {
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("GetIdentitiesForRole", request)
        output_identities=[]
        for i in response['identities']:
             output_identities.append(Identity(**i))

        return output_identities
    

    def get_identities_for_entity(self, entity_type: int, entity_id: int) -> List[UserRole]:
        """
        Get a list of identities and roles with access to an entity

        Parameters:
        entity_type: An entity type ID. (int64)
        entity_id: An entity ID. (int64)

        Returns:
        users: A list of identites and roles (UserRole)
        """
        request = {
            'entity_type': TypedSteamApi.__to_dict(entity_type),
            'entity_id': TypedSteamApi.__to_dict(entity_id)
        }
        response = self.call("GetIdentitiesForEntity", request)
        output_users=[]
        for i in response['users']:
             output_users.append(UserRole(**i))

        return output_users
    

    def get_identity(self, identity_id: int) -> Identity:
        """
        Get identity details

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:
        identity: An identity in Enterprise Steam. (Identity)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("GetIdentity", request)
        output_identity=Identity.from_dict(**response['identity'])

        return output_identity
    

    def get_identity_by_name(self, name: str) -> Identity:
        """
        Get identity details by name

        Parameters:
        name: An identity name. (string)

        Returns:
        identity: An identity in Enterprise Steam. (Identity)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetIdentityByName", request)
        output_identity=Identity.from_dict(**response['identity'])

        return output_identity
    

    def update_identity(self, identity_id: int, password: str) -> None:
        """
        Update an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        password: Password for identity (string)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'password': TypedSteamApi.__to_dict(password)
        }
        response = self.call("UpdateIdentity", request)

        return None
    

    def update_identity_auth(self, identity_id: int, auth_type: str) -> None:
        """
        Update an identity login type

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        auth_type: The auth type to use for login (string)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'auth_type': TypedSteamApi.__to_dict(auth_type)
        }
        response = self.call("UpdateIdentityAuth", request)

        return None
    

    def update_identity_yarn(self, identity_id: int, yarn_queue: str) -> None:
        """
        Update yarn queues of the idenity

        Parameters:
        identity_id: No description available (int64)
        yarn_queue: No description available (string)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'yarn_queue': TypedSteamApi.__to_dict(yarn_queue)
        }
        response = self.call("UpdateIdentityYarn", request)

        return None
    

    def update_identity_uid_gid(self, identity_id: int, uid: int, gid: int) -> None:
        """
        Update UID and GID of identity

        Parameters:
        identity_id: No description available (int64)
        uid: No description available (int64)
        gid: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'uid': TypedSteamApi.__to_dict(uid),
            'gid': TypedSteamApi.__to_dict(gid)
        }
        response = self.call("UpdateIdentityUidGid", request)

        return None
    

    def activate_identity(self, identity_id: int) -> None:
        """
        Activate an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("ActivateIdentity", request)

        return None
    

    def deactivate_identity(self, identity_id: int) -> None:
        """
        Deactivate an identity

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("DeactivateIdentity", request)

        return None
    

    def link_identity_with_workgroup(self, identity_id: int, workgroup_id: int) -> None:
        """
        Link an identity with a workgroup

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id)
        }
        response = self.call("LinkIdentityWithWorkgroup", request)

        return None
    

    def unlink_identity_from_workgroup(self, identity_id: int, workgroup_id: int) -> None:
        """
        Unlink an identity from a workgroup

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id)
        }
        response = self.call("UnlinkIdentityFromWorkgroup", request)

        return None
    

    def link_identity_with_role(self, identity_id: int, role_id: int) -> None:
        """
        Link an identity with a role

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("LinkIdentityWithRole", request)

        return None
    

    def unlink_identity_from_role(self, identity_id: int, role_id: int) -> None:
        """
        Unlink an identity from a role

        Parameters:
        identity_id: Integer ID of an identity in Enterprise Steam. (int64)
        role_id: Integer ID of a role in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'role_id': TypedSteamApi.__to_dict(role_id)
        }
        response = self.call("UnlinkIdentityFromRole", request)

        return None
    

    def share_entity(self, kind: str, workgroup_id: int, entity_type_id: int, entity_id: int) -> None:
        """
        Share an entity with a workgroup

        Parameters:
        kind: Type of permission. Can be view, edit, or own. (string)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'kind': TypedSteamApi.__to_dict(kind),
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id),
            'entity_type_id': TypedSteamApi.__to_dict(entity_type_id),
            'entity_id': TypedSteamApi.__to_dict(entity_id)
        }
        response = self.call("ShareEntity", request)

        return None
    

    def get_privileges(self, entity_type_id: int, entity_id: int) -> List[EntityPrivilege]:
        """
        List privileges for an entity

        Parameters:
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:
        privileges: A list of entity privileges (EntityPrivilege)
        """
        request = {
            'entity_type_id': TypedSteamApi.__to_dict(entity_type_id),
            'entity_id': TypedSteamApi.__to_dict(entity_id)
        }
        response = self.call("GetPrivileges", request)
        output_privileges=[]
        for i in response['privileges']:
             output_privileges.append(EntityPrivilege(**i))

        return output_privileges
    

    def unshare_entity(self, kind: str, workgroup_id: int, entity_type_id: int, entity_id: int) -> None:
        """
        Unshare an entity

        Parameters:
        kind: Type of permission. Can be view, edit, or own. (string)
        workgroup_id: Integer ID of a workgroup in Enterprise Steam. (int64)
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)

        Returns:None
        """
        request = {
            'kind': TypedSteamApi.__to_dict(kind),
            'workgroup_id': TypedSteamApi.__to_dict(workgroup_id),
            'entity_type_id': TypedSteamApi.__to_dict(entity_type_id),
            'entity_id': TypedSteamApi.__to_dict(entity_id)
        }
        response = self.call("UnshareEntity", request)

        return None
    

    def get_history(self, entity_type_id: int, entity_id: int, offset: int, limit: int) -> List[EntityHistory]:
        """
        List audit trail records for an entity

        Parameters:
        entity_type_id: Integer ID for the type of entity. (int64)
        entity_id: Integer ID for an entity in Enterprise Steam. (int64)
        offset: An offset uint start the search on. (uint)
        limit: The maximum uint objects. (uint)

        Returns:
        history: A list of actions performed on the entity. (EntityHistory)
        """
        request = {
            'entity_type_id': TypedSteamApi.__to_dict(entity_type_id),
            'entity_id': TypedSteamApi.__to_dict(entity_id),
            'offset': TypedSteamApi.__to_dict(offset),
            'limit': TypedSteamApi.__to_dict(limit)
        }
        response = self.call("GetHistory", request)
        output_history=[]
        for i in response['history']:
             output_history.append(EntityHistory(**i))

        return output_history
    

    def set_license(self, license: str) -> None:
        """
        Set license from license text

        Parameters:
        license: No description available (string)

        Returns:None
        """
        request = {
            'license': TypedSteamApi.__to_dict(license)
        }
        response = self.call("SetLicense", request)

        return None
    

    def get_license(self, ) -> License:
        """
        Get the current provided license

        Parameters:

        Returns:
        license: No description available (License)
        """
        request = {
        }
        response = self.call("GetLicense", request)
        output_license=License.from_dict(**response['license'])

        return output_license
    

    def delete_license(self, ) -> None:
        """
        Delete the current license

        Parameters:

        Returns:None
        """
        request = {
        }
        response = self.call("DeleteLicense", request)

        return None
    

    def invalidate_ldap_cache(self, ) -> None:
        """
        Invalidate LDAP cache

        Parameters:

        Returns:None
        """
        request = {
        }
        response = self.call("InvalidateLdapCache", request)

        return None
    

    def change_my_password(self, password: str) -> None:
        """
        Change my password

        Parameters:
        password: No description available (string)

        Returns:None
        """
        request = {
            'password': TypedSteamApi.__to_dict(password)
        }
        response = self.call("ChangeMyPassword", request)

        return None
    

    def reset_password_for_identity(self, identity_id: int) -> str:
        """
        Reset user's password and get a new one'

        Parameters:
        identity_id: No description available (int64)

        Returns:
        password: No description available (string)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("ResetPasswordForIdentity", request)
        output_password=response['password']

        return output_password
    

    def generate_identity_token(self, ) -> str:
        """
        Generate new login token for identity

        Parameters:

        Returns:
        token: No description available (string)
        """
        request = {
        }
        response = self.call("GenerateIdentityToken", request)
        output_token=response['token']

        return output_token
    

    def set_identity_admin_override(self, identity_id: int, is_admin: bool) -> None:
        """
        Set identity as admin overriding roles

        Parameters:
        identity_id: No description available (int64)
        is_admin: No description available (bool)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'is_admin': TypedSteamApi.__to_dict(is_admin)
        }
        response = self.call("SetIdentityAdminOverride", request)

        return None
    

    def terminate_identity_resources(self, username: str) -> None:
        """
        Terminates all clusters and instances owned by the user

        Parameters:
        username: No description available (string)

        Returns:None
        """
        request = {
            'username': TypedSteamApi.__to_dict(username)
        }
        response = self.call("TerminateIdentityResources", request)

        return None
    

    def get_sparkling_clusters(self, ) -> List[SparklingCluster]:
        """
        Get Sparkling Water clusters

        Parameters:

        Returns:
        clusters: No description available (SparklingCluster)
        """
        request = {
        }
        response = self.call("GetSparklingClusters", request)
        output_clusters=[]
        for i in response['clusters']:
             output_clusters.append(SparklingCluster(**i))

        return output_clusters
    

    def get_sparkling_cluster(self, cluster_id: int) -> SparklingCluster:
        """
        Get Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (SparklingCluster)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("GetSparklingCluster", request)
        output_cluster=SparklingCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def get_sparkling_cluster_by_name(self, name: str) -> SparklingCluster:
        """
        Get Sparkling Water cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (SparklingCluster)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetSparklingClusterByName", request)
        output_cluster=SparklingCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def get_sparkling_cluster_logs(self, cluster_id: int) -> SparklingClusterLogs:
        """
        Get Sparkling cluster logs

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        logs: No description available (SparklingClusterLogs)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("GetSparklingClusterLogs", request)
        output_logs=SparklingClusterLogs.from_dict(**response['logs'])

        return output_logs
    

    def launch_sparkling_cluster(self, parameters: LaunchSparklingClusterParameters) -> int:
        """
        Launch Sparkling Water cluster

        Parameters:
        parameters: No description available (LaunchSparklingClusterParameters)

        Returns:
        cluster_id: No description available (int64)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("LaunchSparklingCluster", request)
        output_cluster_id=response['cluster_id']

        return output_cluster_id
    

    def start_sparkling_cluster(self, id: int, parameters: LaunchSparklingClusterParameters) -> None:
        """
        Start stopped Sparkling Water cluster

        Parameters:
        id: No description available (int64)
        parameters: No description available (LaunchSparklingClusterParameters)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id),
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("StartSparklingCluster", request)

        return None
    

    def stop_sparkling_cluster(self, cluster_id: int, should_save: bool) -> None:
        """
        Stop Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)
        should_save: No description available (bool)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id),
            'should_save': TypedSteamApi.__to_dict(should_save)
        }
        response = self.call("StopSparklingCluster", request)

        return None
    

    def fail_sparkling_cluster(self, cluster_id: int) -> None:
        """
        Mark cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("FailSparklingCluster", request)

        return None
    

    def delete_sparkling_cluster(self, cluster_id: int) -> None:
        """
        Delete Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("DeleteSparklingCluster", request)

        return None
    

    def send_sparkling_statement(self, cluster_id: int, statement: str, statement_kind: str) -> str:
        """
        Send statement to Sparkling Water cluster

        Parameters:
        cluster_id: No description available (int64)
        statement: No description available (string)
        statement_kind: No description available (string)

        Returns:
        response: No description available (string)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id),
            'statement': TypedSteamApi.__to_dict(statement),
            'statement_kind': TypedSteamApi.__to_dict(statement_kind)
        }
        response = self.call("SendSparklingStatement", request)
        output_response=response['response']

        return output_response
    

    def get_sparkling_config(self, ) -> SparklingConfig:
        """
        Get Sparkling Water configuration

        Parameters:

        Returns:
        config: No description available (SparklingConfig)
        """
        request = {
        }
        response = self.call("GetSparklingConfig", request)
        output_config=SparklingConfig.from_dict(**response['config'])

        return output_config
    

    def set_sparkling_config(self, config: SparklingConfig) -> None:
        """
        Set Sparkling Water configuration

        Parameters:
        config: No description available (SparklingConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetSparklingConfig", request)

        return None
    

    def get_sparkling_engines(self, ) -> List[SparklingEngine]:
        """
        List sparkling engines

        Parameters:

        Returns:
        engines: No description available (SparklingEngine)
        """
        request = {
        }
        response = self.call("GetSparklingEngines", request)
        output_engines=[]
        for i in response['engines']:
             output_engines.append(SparklingEngine(**i))

        return output_engines
    

    def import_sparkling_engine(self, path: str) -> None:
        """
        Import sparkling engine from server path

        Parameters:
        path: No description available (string)

        Returns:None
        """
        request = {
            'path': TypedSteamApi.__to_dict(path)
        }
        response = self.call("ImportSparklingEngine", request)

        return None
    

    def get_sparkling_engine(self, engine_id: int) -> SparklingEngine:
        """
        Get sparkling engine details

        Parameters:
        engine_id: No description available (int64)

        Returns:
        engine: No description available (SparklingEngine)
        """
        request = {
            'engine_id': TypedSteamApi.__to_dict(engine_id)
        }
        response = self.call("GetSparklingEngine", request)
        output_engine=SparklingEngine.from_dict(**response['engine'])

        return output_engine
    

    def get_sparkling_engine_by_version(self, version: str) -> Tuple[int, int]:
        """
        Get a sparkling engine by a version substring

        Parameters:
        version: No description available (string)

        Returns:
        sparkling_engine_id: No description available (int64)
        h2o_engine_id: No description available (int64)
        """
        request = {
            'version': TypedSteamApi.__to_dict(version)
        }
        response = self.call("GetSparklingEngineByVersion", request)
        output_sparkling_engine_id=response['sparkling_engine_id']
        output_h2o_engine_id=response['h2o_engine_id']

        return output_sparkling_engine_id, output_h2o_engine_id
    

    def delete_sparkling_engine(self, engine_id: int) -> None:
        """
        Delete a sparkling engine

        Parameters:
        engine_id: No description available (int64)

        Returns:None
        """
        request = {
            'engine_id': TypedSteamApi.__to_dict(engine_id)
        }
        response = self.call("DeleteSparklingEngine", request)

        return None
    

    def get_python_environment(self, environment_id: int) -> PythonEnvironment:
        """
        Get python environment details

        Parameters:
        environment_id: No description available (int64)

        Returns:
        environment: No description available (PythonEnvironment)
        """
        request = {
            'environment_id': TypedSteamApi.__to_dict(environment_id)
        }
        response = self.call("GetPythonEnvironment", request)
        output_environment=PythonEnvironment.from_dict(**response['environment'])

        return output_environment
    

    def get_python_environment_by_name(self, environment_name: str) -> PythonEnvironment:
        """
        Get python environment details by environment name

        Parameters:
        environment_name: No description available (string)

        Returns:
        environment: No description available (PythonEnvironment)
        """
        request = {
            'environment_name': TypedSteamApi.__to_dict(environment_name)
        }
        response = self.call("GetPythonEnvironmentByName", request)
        output_environment=PythonEnvironment.from_dict(**response['environment'])

        return output_environment
    

    def get_python_environments(self, ) -> List[PythonEnvironment]:
        """
        Get python environments available to current user

        Parameters:

        Returns:
        environments: No description available (PythonEnvironment)
        """
        request = {
        }
        response = self.call("GetPythonEnvironments", request)
        output_environments=[]
        for i in response['environments']:
             output_environments.append(PythonEnvironment(**i))

        return output_environments
    

    def create_python_environment(self, name: str, conda_pack_archive_name: str, pyspark_python_path: str, profile_ids: List[int]) -> int:
        """
        Create new python environment

        Parameters:
        name: No description available (string)
        conda_pack_archive_name: No description available (string)
        pyspark_python_path: No description available (string)
        profile_ids: No description available (int64)

        Returns:
        environment_id: No description available (int64)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name),
            'conda_pack_archive_name': TypedSteamApi.__to_dict(conda_pack_archive_name),
            'pyspark_python_path': TypedSteamApi.__to_dict(pyspark_python_path),
            'profile_ids': TypedSteamApi.__to_dict(profile_ids)
        }
        response = self.call("CreatePythonEnvironment", request)
        output_environment_id=response['environment_id']

        return output_environment_id
    

    def delete_python_environment(self, environment_id: int) -> None:
        """
        Delete python environment

        Parameters:
        environment_id: No description available (int64)

        Returns:None
        """
        request = {
            'environment_id': TypedSteamApi.__to_dict(environment_id)
        }
        response = self.call("DeletePythonEnvironment", request)

        return None
    

    def create_profile(self, profile: Profile) -> int:
        """
        Create new profile

        Parameters:
        profile: No description available (Profile)

        Returns:
        profile_id: No description available (int64)
        """
        request = {
            'profile': TypedSteamApi.__to_dict(profile)
        }
        response = self.call("CreateProfile", request)
        output_profile_id=response['profile_id']

        return output_profile_id
    

    def get_profile(self, profile_id: int) -> Profile:
        """
        Get existing profile by ID

        Parameters:
        profile_id: No description available (int64)

        Returns:
        profile: No description available (Profile)
        """
        request = {
            'profile_id': TypedSteamApi.__to_dict(profile_id)
        }
        response = self.call("GetProfile", request)
        output_profile=Profile.from_dict(**response['profile'])

        return output_profile
    

    def get_profile_by_name(self, name: str) -> Profile:
        """
        Get existing profile by name

        Parameters:
        name: No description available (string)

        Returns:
        profile: No description available (Profile)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetProfileByName", request)
        output_profile=Profile.from_dict(**response['profile'])

        return output_profile
    

    def get_profiles(self, ) -> List[Profile]:
        """
        Get existing profiles by ID

        Parameters:

        Returns:
        profiles: No description available (Profile)
        """
        request = {
        }
        response = self.call("GetProfiles", request)
        output_profiles=[]
        for i in response['profiles']:
             output_profiles.append(Profile(**i))

        return output_profiles
    

    def get_profiles_for_identity(self, identity_id: int) -> List[Profile]:
        """
        Get profiles for an identity

        Parameters:
        identity_id: No description available (int64)

        Returns:
        profiles: No description available (Profile)
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id)
        }
        response = self.call("GetProfilesForIdentity", request)
        output_profiles=[]
        for i in response['profiles']:
             output_profiles.append(Profile(**i))

        return output_profiles
    

    def update_profile(self, profile: Profile) -> None:
        """
        Update existing profile by ID

        Parameters:
        profile: No description available (Profile)

        Returns:None
        """
        request = {
            'profile': TypedSteamApi.__to_dict(profile)
        }
        response = self.call("UpdateProfile", request)

        return None
    

    def delete_profile(self, profile_id: int) -> None:
        """
        Delete existing profile by ID

        Parameters:
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'profile_id': TypedSteamApi.__to_dict(profile_id)
        }
        response = self.call("DeleteProfile", request)

        return None
    

    def link_identity_with_profile(self, identity_id: int, profile_id: int) -> None:
        """
        Link an identity with a profile

        Parameters:
        identity_id: No description available (int64)
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'profile_id': TypedSteamApi.__to_dict(profile_id)
        }
        response = self.call("LinkIdentityWithProfile", request)

        return None
    

    def unlink_identity_from_profile(self, identity_id: int, profile_id: int) -> None:
        """
        Unlink an identity from a profile

        Parameters:
        identity_id: No description available (int64)
        profile_id: No description available (int64)

        Returns:None
        """
        request = {
            'identity_id': TypedSteamApi.__to_dict(identity_id),
            'profile_id': TypedSteamApi.__to_dict(profile_id)
        }
        response = self.call("UnlinkIdentityFromProfile", request)

        return None
    

    def get_profile_usage(self, profile_id: int) -> ProfileUsage:
        """
        Get profile usage statistics

        Parameters:
        profile_id: No description available (int64)

        Returns:
        profile_usage: No description available (ProfileUsage)
        """
        request = {
            'profile_id': TypedSteamApi.__to_dict(profile_id)
        }
        response = self.call("GetProfileUsage", request)
        output_profile_usage=ProfileUsage.from_dict(**response['profile_usage'])

        return output_profile_usage
    

    def get_driverless_instances(self, ) -> List[DriverlessInstance]:
        """
        Get my Driverless AI instances

        Parameters:

        Returns:
        instances: No description available (DriverlessInstance)
        """
        request = {
        }
        response = self.call("GetDriverlessInstances", request)
        output_instances=[]
        for i in response['instances']:
             output_instances.append(DriverlessInstance(**i))

        return output_instances
    

    def get_driverless_instance(self, name: str) -> DriverlessInstance:
        """
        Get Driverless AI instance by name

        Parameters:
        name: No description available (string)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetDriverlessInstance", request)
        output_instance=DriverlessInstance.from_dict(**response['instance'])

        return output_instance
    

    def get_driverless_instance_created_by(self, name: str, created_by: str) -> DriverlessInstance:
        """
        Get Driverless AI instance by name and user

        Parameters:
        name: No description available (string)
        created_by: No description available (string)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name),
            'created_by': TypedSteamApi.__to_dict(created_by)
        }
        response = self.call("GetDriverlessInstanceCreatedBy", request)
        output_instance=DriverlessInstance.from_dict(**response['instance'])

        return output_instance
    

    def get_driverless_instance_by_id(self, id: int) -> DriverlessInstance:
        """
        Get Driverless AI instance by ID

        Parameters:
        id: No description available (int64)

        Returns:
        instance: No description available (DriverlessInstance)
        """
        request = {
            'id': TypedSteamApi.__to_dict(id)
        }
        response = self.call("GetDriverlessInstanceByID", request)
        output_instance=DriverlessInstance.from_dict(**response['instance'])

        return output_instance
    

    def launch_driverless_instance(self, parameters: LaunchDriverlessInstanceParameters) -> int:
        """
        Launch Driverless AI instance

        Parameters:
        parameters: No description available (LaunchDriverlessInstanceParameters)

        Returns:
        instance_id: No description available (int64)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("LaunchDriverlessInstance", request)
        output_instance_id=response['instance_id']

        return output_instance_id
    

    def start_driverless_instance(self, instance_id: int, parameters: LaunchDriverlessInstanceParameters) -> None:
        """
        Start Driverless AI instance

        Parameters:
        instance_id: No description available (int64)
        parameters: No description available (LaunchDriverlessInstanceParameters)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id),
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("StartDriverlessInstance", request)

        return None
    

    def stop_driverless_instance(self, instance_id: int) -> None:
        """
        Stop Driverless AI instance

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id)
        }
        response = self.call("StopDriverlessInstance", request)

        return None
    

    def terminate_driverless_instance(self, instance_id: int) -> None:
        """
        Terminate Driverless AI instance

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id)
        }
        response = self.call("TerminateDriverlessInstance", request)

        return None
    

    def fail_driverless_instance(self, instance_id: int) -> None:
        """
        Mark Driverless AI instance as failed

        Parameters:
        instance_id: No description available (int64)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id)
        }
        response = self.call("FailDriverlessInstance", request)

        return None
    

    def upgrade_driverless_instance(self, instance_id: int, version: str) -> None:
        """
        Upgrade Driverless AI instance

        Parameters:
        instance_id: No description available (int64)
        version: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id),
            'version': TypedSteamApi.__to_dict(version)
        }
        response = self.call("UpgradeDriverlessInstance", request)

        return None
    

    def get_driverless_instance_logs(self, instance_id: int) -> DriverlessInstanceLogs:
        """
        Get Driverless AI instance logs

        Parameters:
        instance_id: No description available (int64)

        Returns:
        logs: No description available (DriverlessInstanceLogs)
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id)
        }
        response = self.call("GetDriverlessInstanceLogs", request)
        output_logs=DriverlessInstanceLogs.from_dict(**response['logs'])

        return output_logs
    

    def get_driverless_engines(self, ) -> List[DriverlessEngine]:
        """
        Get Driverless AI engines

        Parameters:

        Returns:
        engines: No description available (DriverlessEngine)
        """
        request = {
        }
        response = self.call("GetDriverlessEngines", request)
        output_engines=[]
        for i in response['engines']:
             output_engines.append(DriverlessEngine(**i))

        return output_engines
    

    def set_driverless_config(self, config: DriverlessConfig) -> None:
        """
        Set Driverless AI config

        Parameters:
        config: No description available (DriverlessConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetDriverlessConfig", request)

        return None
    

    def get_driverless_config(self, ) -> DriverlessConfig:
        """
        Get Driverless AI config

        Parameters:

        Returns:
        config: No description available (DriverlessConfig)
        """
        request = {
        }
        response = self.call("GetDriverlessConfig", request)
        output_config=DriverlessConfig.from_dict(**response['config'])

        return output_config
    

    def get_driverless_client(self, ) -> DriverlessClient:
        """
        Get Driverless AI Python client info

        Parameters:

        Returns:
        client: No description available (DriverlessClient)
        """
        request = {
        }
        response = self.call("GetDriverlessClient", request)
        output_client=DriverlessClient.from_dict(**response['client'])

        return output_client
    

    def set_driverless_instance_name(self, instance_id: int, name: str) -> None:
        """
        Change the name of a Driverless AI Instance

        Parameters:
        instance_id: No description available (int64)
        name: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id),
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("SetDriverlessInstanceName", request)

        return None
    

    def set_driverless_instance_owner(self, instance_id: int, name: str) -> None:
        """
        Change the owner of a Driverless AI Instance

        Parameters:
        instance_id: No description available (int64)
        name: No description available (string)

        Returns:None
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id),
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("SetDriverlessInstanceOwner", request)

        return None
    

    def get_driverless_kubernetes_engines(self, ) -> List[DriverlessKubernetesEngine]:
        """
        Get engines for Driverless AI on Kubernetes

        Parameters:

        Returns:
        engines: No description available (DriverlessKubernetesEngine)
        """
        request = {
        }
        response = self.call("GetDriverlessKubernetesEngines", request)
        output_engines=[]
        for i in response['engines']:
             output_engines.append(DriverlessKubernetesEngine(**i))

        return output_engines
    

    def add_driverless_kubernetes_engine(self, engine: DriverlessKubernetesEngine) -> None:
        """
        Add engine for Driverless AI on Kubernetes

        Parameters:
        engine: No description available (DriverlessKubernetesEngine)

        Returns:None
        """
        request = {
            'engine': TypedSteamApi.__to_dict(engine)
        }
        response = self.call("AddDriverlessKubernetesEngine", request)

        return None
    

    def remove_driverless_kubernetes_engine(self, version: str) -> None:
        """
        Remove engine for Driverless AI on Kubernetes

        Parameters:
        version: No description available (string)

        Returns:None
        """
        request = {
            'version': TypedSteamApi.__to_dict(version)
        }
        response = self.call("RemoveDriverlessKubernetesEngine", request)

        return None
    

    def launch_driverless_multinode(self, parameters: LaunchDriverlessMultinodeParameters) -> int:
        """
        Launch Driverless AI multinode cluster

        Parameters:
        parameters: No description available (LaunchDriverlessMultinodeParameters)

        Returns:
        instance_id: No description available (int64)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("LaunchDriverlessMultinode", request)
        output_instance_id=response['instance_id']

        return output_instance_id
    

    def get_driverless_multinode(self, name: str) -> DriverlessMultinode:
        """
        Get Driverless AI multinode cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (DriverlessMultinode)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetDriverlessMultinode", request)
        output_cluster=DriverlessMultinode.from_dict(**response['cluster'])

        return output_cluster
    

    def get_driverless_multinodes(self, ) -> List[DriverlessMultinode]:
        """
        Get all Driverless AI multinode clusters

        Parameters:

        Returns:
        cluster: No description available (DriverlessMultinode)
        """
        request = {
        }
        response = self.call("GetDriverlessMultinodes", request)
        output_cluster=[]
        for i in response['cluster']:
             output_cluster.append(DriverlessMultinode(**i))

        return output_cluster
    

    def terminate_driverless_multinode(self, name: str) -> None:
        """
        Terminate Driverless AI multinode cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("TerminateDriverlessMultinode", request)

        return None
    

    def restart_driverless_multinode(self, name: str) -> None:
        """
        Restart failed Driverless AI multinode cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("RestartDriverlessMultinode", request)

        return None
    

    def set_security_config(self, config: SecurityConfig) -> None:
        """
        Set security configuration

        Parameters:
        config: No description available (SecurityConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetSecurityConfig", request)

        return None
    

    def get_security_config(self, ) -> SecurityConfig:
        """
        Set security configuration

        Parameters:

        Returns:
        config: No description available (SecurityConfig)
        """
        request = {
        }
        response = self.call("GetSecurityConfig", request)
        output_config=SecurityConfig.from_dict(**response['config'])

        return output_config
    

    def set_logging_config(self, config: LoggingConfig) -> None:
        """
        Set logging configuration

        Parameters:
        config: No description available (LoggingConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetLoggingConfig", request)

        return None
    

    def get_logging_config(self, ) -> LoggingConfig:
        """
        Get logging configuration

        Parameters:

        Returns:
        config: No description available (LoggingConfig)
        """
        request = {
        }
        response = self.call("GetLoggingConfig", request)
        output_config=LoggingConfig.from_dict(**response['config'])

        return output_config
    

    def get_config_meta(self, ) -> ConfigMeta:
        """
        Get config metadata

        Parameters:

        Returns:
        meta: No description available (ConfigMeta)
        """
        request = {
        }
        response = self.call("GetConfigMeta", request)
        output_meta=ConfigMeta.from_dict(**response['meta'])

        return output_meta
    

    def set_licensing_config(self, config: LicensingConfig) -> None:
        """
        Get Licensing configuration

        Parameters:
        config: No description available (LicensingConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetLicensingConfig", request)

        return None
    

    def get_licensing_config(self, ) -> LicensingConfig:
        """
        Get Licensing configuration

        Parameters:

        Returns:
        config: No description available (LicensingConfig)
        """
        request = {
        }
        response = self.call("GetLicensingConfig", request)
        output_config=LicensingConfig.from_dict(**response['config'])

        return output_config
    

    def get_events(self, entity_type: str, entity_id: int) -> List[Event]:
        """
        Get events associated with given entity

        Parameters:
        entity_type: No description available (string)
        entity_id: No description available (int64)

        Returns:
        events: No description available (Event)
        """
        request = {
            'entity_type': TypedSteamApi.__to_dict(entity_type),
            'entity_id': TypedSteamApi.__to_dict(entity_id)
        }
        response = self.call("GetEvents", request)
        output_events=[]
        for i in response['events']:
             output_events.append(Event(**i))

        return output_events
    

    def get_documentation(self, ) -> List[Documentation]:
        """
        Get all documentation

        Parameters:

        Returns:
        documentation: No description available (Documentation)
        """
        request = {
        }
        response = self.call("GetDocumentation", request)
        output_documentation=[]
        for i in response['documentation']:
             output_documentation.append(Documentation(**i))

        return output_documentation
    

    def delete_documentation(self, item_id: int) -> None:
        """
        Delete a single documentation piece

        Parameters:
        item_id: No description available (int64)

        Returns:None
        """
        request = {
            'item_id': TypedSteamApi.__to_dict(item_id)
        }
        response = self.call("DeleteDocumentation", request)

        return None
    

    def create_kubernetes_volume(self, volume: KubernetesVolume) -> None:
        """
        Create Kubernetes volume

        Parameters:
        volume: No description available (KubernetesVolume)

        Returns:None
        """
        request = {
            'volume': TypedSteamApi.__to_dict(volume)
        }
        response = self.call("CreateKubernetesVolume", request)

        return None
    

    def get_kubernetes_volumes(self, ) -> List[KubernetesVolume]:
        """
        Get all created Kubernetes volumes

        Parameters:

        Returns:
        volumes: No description available (KubernetesVolume)
        """
        request = {
        }
        response = self.call("GetKubernetesVolumes", request)
        output_volumes=[]
        for i in response['volumes']:
             output_volumes.append(KubernetesVolume(**i))

        return output_volumes
    

    def get_profile_kubernetes_volumes(self, ) -> List[KubernetesVolume]:
        """
        Get all profile-specific Kubernetes volumes

        Parameters:

        Returns:
        volumes: No description available (KubernetesVolume)
        """
        request = {
        }
        response = self.call("GetProfileKubernetesVolumes", request)
        output_volumes=[]
        for i in response['volumes']:
             output_volumes.append(KubernetesVolume(**i))

        return output_volumes
    

    def delete_kubernetes_volume(self, id: int) -> None:
        """
        Delete Kubernetes volume

        Parameters:
        id: No description available (int64)

        Returns:None
        """
        request = {
            'id': TypedSteamApi.__to_dict(id)
        }
        response = self.call("DeleteKubernetesVolume", request)

        return None
    

    def set_minio_config(self, config: MinioConfig) -> None:
        """
        Set global Minio configuration

        Parameters:
        config: No description available (MinioConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetMinioConfig", request)

        return None
    

    def get_minio_config(self, ) -> MinioConfig:
        """
        Get global Minio configuration

        Parameters:

        Returns:
        config: No description available (MinioConfig)
        """
        request = {
        }
        response = self.call("GetMinioConfig", request)
        output_config=MinioConfig.from_dict(**response['config'])

        return output_config
    

    def set_personal_minio_credentials(self, credentials: PersonalMinioCredentials) -> None:
        """
        Set personal Minio credentials

        Parameters:
        credentials: No description available (PersonalMinioCredentials)

        Returns:None
        """
        request = {
            'credentials': TypedSteamApi.__to_dict(credentials)
        }
        response = self.call("SetPersonalMinioCredentials", request)

        return None
    

    def get_personal_minio_credentials(self, ) -> PersonalMinioCredentials:
        """
        Get personal Minio credentials

        Parameters:

        Returns:
        credentials: No description available (PersonalMinioCredentials)
        """
        request = {
        }
        response = self.call("GetPersonalMinioCredentials", request)
        output_credentials=PersonalMinioCredentials.from_dict(**response['credentials'])

        return output_credentials
    

    def set_storage_config(self, config: StorageConfig) -> None:
        """
        Set global H2O.ai Storage configuration

        Parameters:
        config: No description available (StorageConfig)

        Returns:None
        """
        request = {
            'config': TypedSteamApi.__to_dict(config)
        }
        response = self.call("SetStorageConfig", request)

        return None
    

    def get_storage_config(self, ) -> StorageConfig:
        """
        Get global H2O.ai Storage configuration

        Parameters:

        Returns:
        config: No description available (StorageConfig)
        """
        request = {
        }
        response = self.call("GetStorageConfig", request)
        output_config=StorageConfig.from_dict(**response['config'])

        return output_config
    

    def get_oidc_token_provider(self, ) -> OidcTokenProvider:
        """
        Get details to establish personal Open ID token provider

        Parameters:

        Returns:
        provider: No description available (OidcTokenProvider)
        """
        request = {
        }
        response = self.call("GetOidcTokenProvider", request)
        output_provider=OidcTokenProvider.from_dict(**response['provider'])

        return output_provider
    

    def get_h2o_kubernetes_clusters(self, ) -> List[H2oKubernetesCluster]:
        """
        Get my H2O cluster

        Parameters:

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
        }
        response = self.call("GetH2oKubernetesClusters", request)
        output_cluster=[]
        for i in response['cluster']:
             output_cluster.append(H2oKubernetesCluster(**i))

        return output_cluster
    

    def get_h2o_kubernetes_cluster_by_id(self, cluster_id: int) -> H2oKubernetesCluster:
        """
        Get H2O cluster by id

        Parameters:
        cluster_id: No description available (int64)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("GetH2oKubernetesClusterById", request)
        output_cluster=H2oKubernetesCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def stop_h2o_kubernetes_cluster_by_id(self, cluster_id: int) -> None:
        """
        Stop H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("StopH2oKubernetesClusterById", request)

        return None
    

    def fail_h2o_kubernetes_cluster_by_id(self, cluster_id: int) -> None:
        """
        Mark H2O cluster as failed

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("FailH2oKubernetesClusterById", request)

        return None
    

    def delete_h2o_kubernetes_cluster_by_id(self, cluster_id: int) -> None:
        """
        Terminate H2O cluster

        Parameters:
        cluster_id: No description available (int64)

        Returns:None
        """
        request = {
            'cluster_id': TypedSteamApi.__to_dict(cluster_id)
        }
        response = self.call("DeleteH2oKubernetesClusterById", request)

        return None
    

    def get_h2o_kubernetes_cluster_by_name(self, cluster_name: str) -> H2oKubernetesCluster:
        """
        Get H2O cluster by name

        Parameters:
        cluster_name: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_name': TypedSteamApi.__to_dict(cluster_name)
        }
        response = self.call("GetH2oKubernetesClusterByName", request)
        output_cluster=H2oKubernetesCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def get_h2o_kubernetes_cluster_by_name_created_by(self, cluster_name: str, created_by: str) -> H2oKubernetesCluster:
        """
        Get H2o cluster by name created by specified user

        Parameters:
        cluster_name: No description available (string)
        created_by: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'cluster_name': TypedSteamApi.__to_dict(cluster_name),
            'created_by': TypedSteamApi.__to_dict(created_by)
        }
        response = self.call("GetH2oKubernetesClusterByNameCreatedBy", request)
        output_cluster=H2oKubernetesCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def launch_h2o_kubernetes_cluster(self, parameters: LaunchH2oKubernetesClusterParameters) -> H2oKubernetesCluster:
        """
        Launch H2O cluster

        Parameters:
        parameters: No description available (LaunchH2oKubernetesClusterParameters)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'parameters': TypedSteamApi.__to_dict(parameters)
        }
        response = self.call("LaunchH2oKubernetesCluster", request)
        output_cluster=H2oKubernetesCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def get_h2o_kubernetes_cluster_logs(self, instance_id: int) -> H2oK8sLogs:
        """
        Get H2O cluster logs

        Parameters:
        instance_id: No description available (int64)

        Returns:
        logs: No description available (H2oK8sLogs)
        """
        request = {
            'instance_id': TypedSteamApi.__to_dict(instance_id)
        }
        response = self.call("GetH2oKubernetesClusterLogs", request)
        output_logs=H2oK8sLogs.from_dict(**response['logs'])

        return output_logs
    

    def get_h2o_kubernetes_engines(self, ) -> List[H2oKubernetesEngine]:
        """
        Get engines for H2O on Kubernetes

        Parameters:

        Returns:
        engines: No description available (H2oKubernetesEngine)
        """
        request = {
        }
        response = self.call("GetH2oKubernetesEngines", request)
        output_engines=[]
        for i in response['engines']:
             output_engines.append(H2oKubernetesEngine(**i))

        return output_engines
    

    def add_h2o_kubernetes_engine(self, engine: H2oKubernetesEngine) -> None:
        """
        Add engine for H2O on Kubernetes

        Parameters:
        engine: No description available (H2oKubernetesEngine)

        Returns:None
        """
        request = {
            'engine': TypedSteamApi.__to_dict(engine)
        }
        response = self.call("AddH2oKubernetesEngine", request)

        return None
    

    def remove_h2o_kubernetes_engine(self, version: str) -> None:
        """
        Remove engine for H2O on Kubernetes

        Parameters:
        version: No description available (string)

        Returns:None
        """
        request = {
            'version': TypedSteamApi.__to_dict(version)
        }
        response = self.call("RemoveH2oKubernetesEngine", request)

        return None
    

    def get_h2o_kubernetes_cluster(self, name: str) -> H2oKubernetesCluster:
        """
        Get H2O cluster by name

        Parameters:
        name: No description available (string)

        Returns:
        cluster: No description available (H2oKubernetesCluster)
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("GetH2oKubernetesCluster", request)
        output_cluster=H2oKubernetesCluster.from_dict(**response['cluster'])

        return output_cluster
    

    def stop_h2o_kubernetes_cluster(self, name: str) -> None:
        """
        Stop H2O cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("StopH2oKubernetesCluster", request)

        return None
    

    def fail_h2o_kubernetes_cluster(self, name: str) -> None:
        """
        Mark H2O cluster as failed

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("FailH2oKubernetesCluster", request)

        return None
    

    def delete_h2o_kubernetes_cluster(self, name: str) -> None:
        """
        Terminate H2O cluster

        Parameters:
        name: No description available (string)

        Returns:None
        """
        request = {
            'name': TypedSteamApi.__to_dict(name)
        }
        response = self.call("DeleteH2oKubernetesCluster", request)

        return None
    

    def dummy(self, a: ProfileValue, b: ProfileSparklingInternal, c: ProfileSparklingExternal, d: ProfileH2o, f: ProfileDriverlessKubernetes, g: H2oClusterConnectParams, h: KubernetesVolumeHostPath, i: KubernetesVolumeSecret, j: KubernetesVolumeConfigMap, k: KubernetesVolumePvc, l: KubernetesVolumeNfs, m: KubernetesVolumeCsi, n: ProfileH2oKubernetes) -> None:
        """
        Does nothing

        Parameters:
        a: No description available (ProfileValue)
        b: No description available (ProfileSparklingInternal)
        c: No description available (ProfileSparklingExternal)
        d: No description available (ProfileH2o)
        f: No description available (ProfileDriverlessKubernetes)
        g: No description available (H2oClusterConnectParams)
        h: No description available (KubernetesVolumeHostPath)
        i: No description available (KubernetesVolumeSecret)
        j: No description available (KubernetesVolumeConfigMap)
        k: No description available (KubernetesVolumePvc)
        l: No description available (KubernetesVolumeNfs)
        m: No description available (KubernetesVolumeCsi)
        n: No description available (ProfileH2oKubernetes)

        Returns:None
        """
        request = {
            'a': TypedSteamApi.__to_dict(a),
            'b': TypedSteamApi.__to_dict(b),
            'c': TypedSteamApi.__to_dict(c),
            'd': TypedSteamApi.__to_dict(d),
            'f': TypedSteamApi.__to_dict(f),
            'g': TypedSteamApi.__to_dict(g),
            'h': TypedSteamApi.__to_dict(h),
            'i': TypedSteamApi.__to_dict(i),
            'j': TypedSteamApi.__to_dict(j),
            'k': TypedSteamApi.__to_dict(k),
            'l': TypedSteamApi.__to_dict(l),
            'm': TypedSteamApi.__to_dict(m),
            'n': TypedSteamApi.__to_dict(n)
        }
        response = self.call("Dummy", request)

        return None
    
    
