import requests
import os
import h2osteam
import tempfile
from h2osteam.backend import SteamConnection
from h2osteam.typed_backend import TypedSteamConnection
from h2osteam.typed_backend import Profile
from h2osteam.typed_backend import ProfileValue
from h2osteam.typed_backend import ProfileDriverlessKubernetes
from h2osteam.typed_backend import ProfileH2oKubernetes
from h2osteam.typed_backend import OidcConfig
from h2osteam.typed_backend import DriverlessKubernetesEngine
from h2osteam.typed_backend import H2oKubernetesEngine
from h2osteam.typed_backend import KubernetesConfig
from h2osteam.typed_backend import DriverlessConfig
from h2osteam.typed_backend import H2oConfig
from h2osteam.typed_backend import SecurityConfig


from typing import List, Tuple


class AdminKubernetesClient:
    def __init__(self, steam: SteamConnection = None):
        steam = steam if steam is not None else h2osteam.api()
        self.api = TypedSteamConnection(steam=steam)
        self.untyped_api = steam

    def internal_api(self) -> TypedSteamConnection:
        """
        :return: Steam internal API. Defined methods are generated and subject to a possible change in any future release.
        """
        return self.api

    @staticmethod
    def create_admin_account(
        steam_url: str, name: str, password: str, verify: bool = False
    ) -> Tuple[int, str]:
        """
        Creates unique local admin account.
        Any error during an account creation will be printed out.

        :param steam_url: the base URL of the Steam instance without a tailing slash
        :param name: local administrator account name
        :param password: local administrator password
        :param verify: (Optional) defaults to False, verify server's TLS certificate
        :return: Tuple[int, str]: response return code, response body as a text
        """
        print("Setting local administrator account...")
        res = requests.request(
            "POST",
            "%s/create" % steam_url,
            data={"username": name, "password": password},
            verify=verify,
            timeout=30,
        )
        return res.status_code, res.text

    def create_or_update_profile(self, p: Profile) -> None:
        """
        Creates or updates existing profile with given profile. Existing profile is matched by the profile name.

        :param p: Profile, use build_kubernetes_driverless_profile or build_kubernetes_h2o_profile to create a Profile
        :return: None
        """
        try:
            existing_id = self.api.get_profile_by_name(p.name).id
        except h2osteam.backend.connection.RPCError:
            print("Creating new profile %s" % p.name)
            self.api.create_profile(p)
            return

        print("Updating existing profile %s" % p.name)
        self.api.delete_profile(existing_id)
        self.api.create_profile(p)

    def build_kubernetes_dai_profile(
        self,
        name: str,
        user_groups: str,
        instances_per_user: int,
        cpu_count: Tuple[int, int, int, int],
        gpu_count: Tuple[int, int, int, int],
        memory_gb: Tuple[int, int, int, int],
        storage_gb: Tuple[int, int, int, int],
        max_uptime_hours: Tuple[int, int, int],
        max_idle_hours: Tuple[int, int, int],
        timeout_seconds: Tuple[int, int, int],
        license_manager_project_name: str = "",
        config_toml: str = "",
        allow_instance_config_toml: bool = False,
        whitelist_instance_config_toml: str = "",
        node_selector: str = "",
        kubernetes_volumes=None,
        env: str = "",
        custom_pod_labels: str = "",
        custom_pod_annotations: str = "",
        load_balancer_source_ranges: str = "0.0.0.0/0",
        tolerations: str = "",
        init_containers: str = "",
        disabled: bool = False,
        multinode: bool = False,
        main_cpu_count: int = 0,
        main_memory_gb: int = 0,
        min_worker_count: int = 0,
        max_worker_count: int = 0,
        buffer_worker_count: int = 0,
        worker_processor_count: int = 0,
        worker_downscale_delay_seconds: int = 0,
        main_processor_count: int = 0,
        main_node_selector: str = "",
    ) -> Profile:
        """
        Helper function to create a DriverlessAI Steam profile
        For parameters requesting multiple values, provide a tuple of four values (minimal, maximal, initial, profile_maximum) with profile_maximum=-1 indicating no limit.
        If a parameter requests three values, it means given parameter does not support profile_maximum limit.

        :param name: Name of the profile.
        :param user_groups: Comma-seprarated list of groups assigned to this profile. Accepts wildcard '*' character.
        :param instances_per_user: Limit the amount of H2O clusters a single user can launch with this profile.
        :param cpu_count: Specify the number of cpu units. One cpu, in Kubernetes, is equivalent to 1 vCPU/Core for cloud providers and 1 hyperthread on bare-metal Intel processors.
        :param gpu_count: Specify the number of GPUs.
        :param memory_gb: Specify the amount of memory in GB.
        :param storage_gb: Specify the amount of storage in GB.
        :param max_uptime_hours: Specify the duration in hours after which the instance will be automatically stopped if it has been idle for that long.
        :param max_idle_hours: Specify the duration in hours after which the instance will automatically stop.
        :param timeout_seconds: Instance will terminate if it was unable to start within this time limit.
        :param license_manager_project_name: License manager project name.
        :param config_toml: Enter additional Driverless AI configuration in TOML format that will be applied over the standard config.toml.
        :param allow_instance_config_toml: Allow users to override allow-listed Driverless AI configuration in TOML format.
        :param whitelist_instance_config_toml: Enter additional Driverless AI configuration in TOML format that will be available to user instances for override.
        :param node_selector: Enter Kubernetes labels (using 'key: value' format, one per line). Instances will be scheduled only on Kubernetes nodes with these labels. The most common usage is one key-value pair. Leave empty to use any node.
        :param kubernetes_volumes: List Kubernetes volume names that are mounted to clusters started using this profile.
        :param env: Enter extra environmental variables passed to the DriverlessAI image (using 'NAME=value' format, one per line).
        :param custom_pod_labels: Extra Kubernetes labels attached to pods of this profile. Use 'key: value' format, one per line.
        :param custom_pod_annotations: Extra Kubernetes annotations attached to pods of this profile. Use 'key: value' format, one per line.
        :param load_balancer_source_ranges: Restrict CIDR IP addresses for a LoadBalancer type service. Use one address range in format '143.231.0.0/16' per line. Only applies if Steam is running outside of a Kubernetes cluster.
        :param tolerations: DAI pods tolerations. Provide text in Kubernetes readable YAML format. Example value:
        tolerations:
        - key: "key1"
          operator: "Equal"
          value: "value1"
          effect: "NoSchedule"
        - key: "key2"
          operator: "Exists"
          effect: "NoExecute"
        :param init_containers: Initialization containers belonging to the DAI pod. Example value:
        initContainers:
        - name: init-myservice
          image: busybox:1.28
          command: ['sh', '-c', "until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for myservice; sleep 2; done"]
        - name: init-mydb
          image: busybox:1.28
          command: ['sh', '-c', "until nslookup mydb.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for mydb; sleep 2; done"]
        :param disabled: Disabled profile will be listed to the user but cant be used to start instances.
        :param multinode: Enable multinode mode.
        :param main_cpu_count: Main server CPU count.
        :param main_memory_gb: Main server memory in GB.
        :param min_worker_count: Minimal number of worker nodes.
        :param max_worker_count: Maximal number of worker nodes.
        :param buffer_worker_count: Number of worker nodes to keep running when no jobs are running.
        :param worker_processor_count: Number of processors per worker node.
        :param worker_downscale_delay_seconds: Delay in seconds before worker node is terminated after job is finished.
        :param main_processor_count: Number of processors on the main node
        :param main_node_selector: Node selector for the main node.


        :return: Profile
        """

        # Gather kubernetes volumes ids
        if kubernetes_volumes is None:
            kubernetes_volumes = []

        volumes_ids: List[int] = []
        for v in self.api.get_kubernetes_volumes():
            if v.name in kubernetes_volumes:
                volumes_ids.append(v.id)

        k8s_profile = ProfileDriverlessKubernetes(
            id=0,
            cpu_count=self.profile_value_with_limit(cpu_count),
            gpu_count=self.profile_value_with_limit(gpu_count),
            memory_gb=self.profile_value_with_limit(memory_gb),
            storage_gb=self.profile_value_with_limit(storage_gb),
            max_uptime_hours=self.profile_value(max_uptime_hours),
            max_idle_hours=self.profile_value(max_idle_hours),
            timeout_seconds=self.profile_value(timeout_seconds),
            license_manager_project_name=license_manager_project_name,
            config_toml=config_toml,
            allow_instance_config_toml=allow_instance_config_toml,
            whitelist_instance_config_toml=whitelist_instance_config_toml,
            node_selector=node_selector,
            kubernetes_volumes=volumes_ids,
            env=env,
            custom_pod_labels=custom_pod_labels,
            custom_pod_annotations=custom_pod_annotations,
            load_balancer_source_ranges=load_balancer_source_ranges,
            tolerations=tolerations,
            init_containers=init_containers,
            disabled=disabled,
            multinode=multinode,
            main_cpu_count=main_cpu_count,
            main_memory_gb=main_memory_gb,
            min_worker_count=min_worker_count,
            max_worker_count=max_worker_count,
            buffer_worker_count=buffer_worker_count,
            worker_processor_count=worker_processor_count,
            worker_downscale_delay_seconds=worker_downscale_delay_seconds,
            main_processor_count=main_processor_count,
            main_node_selector=main_node_selector,
        )

        return Profile(
            id=0,
            name=name,
            user_groups=user_groups,
            cluster_limit=instances_per_user,
            profile_type="driverless_kubernetes",
            driverless_kubernetes=k8s_profile,
            h2o=None,
            created_at=0,
            sparkling_internal=None,
            sparkling_external=None,
            h2o_kubernetes=None,
        )

    def build_kubernetes_h2o_profile(
        self,
        name: str,
        user_groups: str,
        instances_per_user: int,
        node_count: Tuple[int, int, int, int],
        cpu_count: Tuple[int, int, int, int],
        gpu_count: Tuple[int, int, int, int],
        memory_gb: Tuple[int, int, int, int],
        max_uptime_hours: Tuple[int, int, int],
        max_idle_hours: Tuple[int, int, int],
        timeout_seconds: Tuple[int, int, int],
        java_options: str = "",
        h2o_options: str = "",
        env: str = "",
        node_selector: str = "",
        kubernetes_volumes=None,
        custom_service_labels: str = "",
        custom_pod_labels: str = "",
        custom_pod_annotations: str = "",
        tolerations: str = "",
        init_containers: str = "",
        disabled: bool = False,
    ) -> Profile:
        """
        Helper function to create an H2O Kubernetes Steam profile
        For parameters requesting multiple values, provide a tuple of four values (minimal, maximal, initial, profile_maximum) with profile_maximum=-1 indicating no limit.
        If a parameter requests three values, it means given parameter does not support profile_maximum limit.

        :param name: Name of this profile.
        :param user_groups: Comma-seprarated list of groups assigned to this profile. Accepts wildcard '*' character.
        :param instances_per_user: Limit the amount of H2O clusters a single user can launch with this profile.
        :param node_count: Specify the number of nodes.
        :param cpu_count: Specify the number of cpu units. One cpu, in Kubernetes, is equivalent to 1 vCPU/Core for cloud providers and 1 hyperthread on bare-metal Intel processors.
        :param gpu_count: Specify the number of GPUs per node.
        :param memory_gb: Specify the amount of memory in GB per node.
        :param max_uptime_hours: Specify the duration in hours after which the cluster will be automatically stopped if it has been idle for that long. Provide a tuple of three values (minimal, maximal, initial).
        :param max_idle_hours: Specify the duration in hours after which the cluster will automatically stop.
        :param timeout_seconds: Cluster will terminate if it was unable to start within this time limit.
        :param java_options: Extra command line options passed to Java.
        :param h2o_options: Extra command line options passed to H2O-3.
        :param env: Enter extra environmental variables passed to the DriverlessAI image (using 'NAME=value' format, one per line).
        :param node_selector: Enter Kubernetes labels (using 'key: value' format, one per line). Instances will be scheduled only on Kubernetes nodes with these labels. The most common usage is one key-value pair. Leave empty to use any node.
        :param kubernetes_volumes: List Kubernetes volume names that are mounted to clusters started using this profile.
        :param custom_service_labels: Extra Kubernetes labels attached to services of this profile. Use 'key: value' format, one per line.
        :param custom_pod_labels: Extra Kubernetes labels attached to pods of this profile. Use 'key: value' format, one per line.
        :param custom_pod_annotations: Extra Kubernetes annotations attached to pods of this profile. Use 'key: value' format, one per line.
        :param tolerations: H2O pods tolerations. Provide text in Kubernetes readable YAML format. Example value:
        tolerations:
        - key: "key1"
          operator: "Equal"
          value: "value1"
          effect: "NoSchedule"
        - key: "key2"
          operator: "Exists"
          effect: "NoExecute"
        :param init_containers: Initialization containers belonging to the H2O pod. Example value:
        initContainers:
        - name: init-myservice
          image: busybox:1.28
          command: ['sh', '-c', "until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for myservice; sleep 2; done"]
        - name: init-mydb
          image: busybox:1.28
          command: ['sh', '-c', "until nslookup mydb.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do echo waiting for mydb; sleep 2; done"]
        :param disabled: Disabled profile will be listed to the user but cant be used to start instances.

        :return: Profile
        """

        # Gather kubernetes volumes ids
        if kubernetes_volumes is None:
            kubernetes_volumes = []

        volumes_ids: List[int] = []
        for v in self.api.get_kubernetes_volumes():
            if v.name in kubernetes_volumes:
                volumes_ids.append(v.id)

        k8s_profile = ProfileH2oKubernetes(
            id=0,
            node_count=self.profile_value_with_limit(node_count),
            cpu_count=self.profile_value_with_limit(cpu_count),
            gpu_count=self.profile_value_with_limit(gpu_count),
            memory_gb=self.profile_value_with_limit(memory_gb),
            max_uptime_hours=self.profile_value(max_uptime_hours),
            max_idle_hours=self.profile_value(max_idle_hours),
            timeout_seconds=self.profile_value(timeout_seconds),
            java_options=java_options,
            h2o_options=h2o_options,
            node_selector=node_selector,
            kubernetes_volumes=volumes_ids,
            custom_service_labels=custom_service_labels,
            custom_pod_labels=custom_pod_labels,
            custom_pod_annotations=custom_pod_annotations,
            tolerations=tolerations,
            init_containers=init_containers,
            disabled=disabled,
            env=env,
        )

        return Profile(
            id=0,
            name=name,
            user_groups=user_groups,
            cluster_limit=instances_per_user,
            profile_type="h2o_kubernetes",
            driverless_kubernetes=None,
            h2o=None,
            created_at=0,
            sparkling_internal=None,
            sparkling_external=None,
            h2o_kubernetes=k8s_profile,
        )

    def set_oidc_auth_config(
        self,
        issuer: str,
        client_id: str,
        client_secret: str,
        steam_url: str,
        scopes: str = "openid,offline_access,profile,email",
        userinfo_username_key: str = "preferred_username",
        userinfo_email_key: str = "email",
        userinfo_roles_key: str = "groups",
        userinfo_uid_key: str = "",
        userinfo_gid_key: str = "",
        enable_logout_id_token_hint: bool = True,
        acr_values: str = "",
    ) -> None:
        """
        Sets default authentication method to OIDC with specified configuration parameters.

        :param issuer: URL of the OpenID Provider server (ex: https://oidp.ourdomain.com)
        :param client_id: client ID registered with OpenID provider
        :param client_secret: secret associated with the client_id
        :param steam_url: the base URL of the Steam instance without a tailing slash
        :param scopes: Comma-separated list of scopes of user information Enterprise Steam will request from the OpenID provider.
        :param userinfo_username_key: Key that specifies username attribute from userinfo data (ex: preferred_username). Supports nesting (ex: realm1.key).
        :param userinfo_email_key: Key that specifies email attribute from userinfo data (ex: email). Supports nesting (ex: realm1.key).
        :param userinfo_roles_key: Key that specifies roles attribute from userinfo data (ex: roles). Supports nesting (ex: realm1.key).
        :param userinfo_uid_key: Key that specifies UNIX uid attribute from userinfo data. Supports nesting (ex: realm1.key).
        :param userinfo_gid_key: Key that specifies UNIX gid attribute from userinfo data. Supports nesting (ex: realm1.key).
        :param enable_logout_id_token_hint: Indicates whether id_token_hint should be passed in a logout URL parameter.
        :param acr_values: Comma-separated list of allowed authentication context classes.
        :return:
        """
        cfg = OidcConfig(
            issuer=issuer,
            client_id=client_id,
            client_secret=client_secret,
            redirect_url=f"{steam_url}/auth",
            logout_redirect_url=f"{steam_url}/oidc-login",
            scopes=scopes,
            userinfo_username_key=userinfo_username_key,
            userinfo_email_key=userinfo_email_key,
            userinfo_roles_key=userinfo_roles_key,
            userinfo_uid_key=userinfo_uid_key,
            userinfo_gid_key=userinfo_gid_key,
            enable_logout_id_token_hint=enable_logout_id_token_hint,
            a_c_r_values=acr_values,
        )

        self.api.set_authentication(
            "oidc",
            None,
            None,
            None,
            cfg,
        )

    def set_kubernetes_config(
        self,
        storage_class: str,
        namespace: str = "",
        gpu_resource_name: str = "nvidia.com/gpu",
        allow_volume_expansion: bool = False,
        fallback_uid: int = 0,
        fallback_gid: int = 0,
        force_fallback: bool = False,
        extra_load_balancer_annotations: str = "",
        rwm_storage_class: str = "",
        seccomp_profile_runtime_default: bool = True,
    ) -> None:
        """
        Sets kubernetes configuration for Steam

        :param storage_class: Name of the StorageClass object that manages provisioning of PersistentVolumes.
        :param namespace: Kubernetes namespace where all Steam objects live.
        :param gpu_resource_name: Resource name for GPU.
        :param allow_volume_expansion: Allow expansion of user PersistentVolumes. Must be supported by the StorageClass.
        :param fallback_uid: Pods will be started using this fallback UID when FORCE FALLBACK UID/GID option is used.
        :param fallback_gid: Pods will be started using this fallback GID when FORCE FALLBACK UID/GID option is used.
        :param force_fallback: Fallback UID/GID will be used overriding UID/GID received from authentication provider.
        :param extra_load_balancer_annotations: Extra LoadBalancer annotations in YAML format, one per line, key and value separated by ':'.
        :param rwm_storage_class: Name of the StorageClass object that manages provisioning of ReadWriteMany PersistentVolumes.
        :param seccomp_profile_runtime_default: Use the RuntimeDefault seccomp profile.

        :return:
        """
        self.api.set_kubernetes_config(
            KubernetesConfig(
                enabled=True,
                inside_cluster=True,
                use_default_storage_class=False,
                gpu_resource_name=gpu_resource_name,
                kubeconfig_path="",
                namespace=namespace,
                storage_class=storage_class,
                allow_volume_expansion=allow_volume_expansion,
                fallback_uid=fallback_uid,
                fallback_gid=fallback_gid,
                force_fallback=force_fallback,
                load_balancer_annotations=extra_load_balancer_annotations,
                r_w_m_storage_class=rwm_storage_class,
                seccomp_profile_runtime_default=seccomp_profile_runtime_default,
            )
        )

    def set_security_config(
        self,
        tls_cert_path="",
        tls_key_path="",
        server_strict_transport="max-age=631138519",
        server_x_xss_protection="0",
        server_content_security_policy="style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' "
        "https://fonts.gstatic.com data:;",
        session_duration_min=4320,
        personal_access_token_duration_hours=8760,
        web_ui_timeout_min=480,
        disable_admin=False,
        global_url_prefix="",
        secure_cookie=True,
        support_email="support@h2o.ai",
        hide_errors=False,
    ) -> None:
        """
        Sets security configuration for Steam

        :param tls_cert_path: Path to the server TLS certificate.
        :param tls_key_path: Path to the server TLS key.
        :param server_strict_transport: Value of the Strict-Transport-Security header in the server responses.
        :param server_x_xss_protection: Value of the X-XSS-Protection header in the server responses.
        :param server_content_security_policy: Value of the Content-Security-Policy header in the server responses.
        :param session_duration_min: The lifespan of Steam issued cookie/JWT token.
        :param personal_access_token_duration_hours: The lifespan of Steam issued personal access token.
        :param web_ui_timeout_min: Users will be automatically logged out when reaching the idle timeout.
        :param disable_admin: Disable the initial administrator account.
        :param global_url_prefix: Global URL prefix for the Enterprise Steam.
        :param secure_cookie: Set Secure cookie flag.
        :param support_email: Change the target of Support email address.
        :param hide_errors: If enabled, authentication errors will default to "forbidden" to hide configuration details.

        :return:
        """

        self.api.set_security_config(
            SecurityConfig(
                tls_cert_path=tls_cert_path,
                tls_key_path=tls_key_path,
                server_strict_transport=server_strict_transport,
                server_x_xss_protection=server_x_xss_protection,
                server_content_security_policy=server_content_security_policy,
                session_duration_min=session_duration_min,
                personal_access_token_duration_hours=personal_access_token_duration_hours,
                web_ui_timeout_min=web_ui_timeout_min,
                disable_admin=disable_admin,
                disable_jupyter=False,  # Hadoop only, disregard
                allow_external_token_refresh=False,  # Soon to be removed, disregard
                global_url_prefix=global_url_prefix,
                secure_cookie=secure_cookie,
                support_email=support_email,
                strip_auth_errors=hide_errors,
            )
        )

    def enable_dai_kubernetes(
        self,
        license_text: str,
        enabled=True,
        storage_directory="",
        backend_type="",
        oidc_auth=False,
        enable_triton=False,
    ):
        """
        Enables Driverless AI product deployment on Kubernetes backend.
        Kubernetes backend must be configured first using set_kubernetes_config function.

        :param license_text: text representation of a valid Driverless AI license
        :param enabled: Optional. Enable Driverless AI. Defaults to True.
        :param storage_directory: Optional. Deprecated. Defaults to ""  .
        :param backend_type: Optional. Deprecated. Defaults to ""  .
        :param oidc_auth: Optional. Enable new OIDC authentication available from 1.10.3 version. Defaults to False.
        :param enable_triton: Optional. Enable Triton inference server. Defaults to False.
        :return:
        """

        self.api.set_driverless_config(
            DriverlessConfig(
                enabled=enabled,
                license=license_text,
                storage_directory=storage_directory,
                backend_type=backend_type,
                o_id_c_auth=oidc_auth,
                enable_triton=enable_triton,
            )
        )

    def enable_h2o_kubernetes(self):
        """
        Enables H2O product deployment on Kubernetes backend.
        Kubernetes backend must be configured first using set_kubernetes_config function.

        :return:
        """
        self.api.set_h2o_config(
            H2oConfig(
                enabled=True,
                backend_type="kubernetes",
                internal_secure_connections=False,
                enable_external_xgboost=False,
                allow_insecure_xgboost=False,
                extra_hadoop_classpath="",
                jobname_prefix="",
                override_driver_output_directory=False,
                driver_output_directory="",
            )
        )

    def add_h2o_image(
        self,
        version: str,
        image: str,
        image_pull_policy: str = "Always",
        image_pull_secret: str = "",
        experimental: bool = False,
    ) -> None:
        """
        Adds H2O Docker image to Steam.

        :param version: version of the H2O release like 3.32.1.3
        :param image: full image name to be pulled like h2oai/h2o-open-source-k8s:3.32.1.3
        :param image_pull_policy: kubernetes image pull policy for a pod running H2O image
        :param image_pull_secret: reference to a secret in the same namespace to use for pulling the image.
        This secret will be passed to individual puller implementations for them to use. For example, in the case of
        docker, only DockerConfig type secrets are honored.
        :param experimental: experimental engine is not offered in the upgrade dialog and
        is listed last in the "create new" dropdown. Web UI only.

        :return: None
        """
        try:
            self.api.add_h2o_kubernetes_engine(
                H2oKubernetesEngine(
                    version=version,
                    image=image,
                    image_pull_policy=image_pull_policy,
                    image_pull_secret=image_pull_secret,
                    created_at=0,
                    experimental=experimental,
                )
            )
        except h2osteam.backend.connection.RPCError:
            print("H2O image already exists")

    def add_dai_image(
        self,
        version: str,
        image: str,
        image_pull_policy: str = "Always",
        image_pull_secret: str = "",
        experimental: bool = False,
    ) -> None:
        """
        Adds DriverlessAI Docker image to Steam.

        :param version: version of the DAI release like 1.9.2.2
        :param image: full image name to be pulled like gcr.io/vorvan/h2oai/dai-centos7-x86_64:1.9.2.2-cuda10.0
        :param image_pull_policy: kubernetes image pull policy for a pod running DriverlessAI image
        :param image_pull_secret: reference to a secret in the same namespace to use for pulling the image.
        This secret will be passed to individual puller implementations for them to use. For example, in the case of
        docker, only DockerConfig type secrets are honored.
        :param experimental: experimental engine is not offered in the upgrade dialog and
        is listed last in the "create new" dropdown. Web UI only.

        :return: None
        """
        try:
            self.api.add_driverless_kubernetes_engine(
                DriverlessKubernetesEngine(
                    version=version,
                    image=image,
                    image_pull_policy=image_pull_policy,
                    image_pull_secret=image_pull_secret,
                    created_at=0,
                    experimental=experimental,
                )
            )
        except h2osteam.backend.connection.RPCError:
            print("Driverless image already exists")

    def add_dai_python_client(self, url: str) -> None:
        """
        Uploads specified DriverlessAI Python client to Steam.
        The client version should be at least as new as the latest DAI version used in Steam.

        :param url: URL to download DAI Python client from pipy.org like https://files.pythonhosted.org/packages/bd/65/05e5c6b5c8d32575e655d98dba182dee26ce04899df8d72d0ca7c409d92d/driverlessai-1.9.2.1.post1-py3-none-any.whl

        :return: None
        """
        r = requests.get(url, allow_redirects=True)
        if r.status_code != 200:
            raise Exception("Invalid DAI Python client wheel file download URl")

        tmp_file = tempfile.NamedTemporaryFile()
        try:
            tmp_file.write(r.content)
            self.untyped_api.upload(
                target="/upload/driverless/client", path=tmp_file.name, payload=None
            )
        finally:
            tmp_file.close()

    def download_dai_usage_statistics(self, path: str) -> None:
        """
        Downloads DriverlessAI usage statistics (in a CSV format).
        :param path: Specify path for the downloaded file. Example: /home/user/report.csv
        :return:
        """

        self.untyped_api.download("/download/driverless/report", path)

    def download_h2o_usage_statistics(self, path: str) -> None:
        """
        Downloads H2O usage statistics (in a CSV format).
        :param path: Specify path for the downloaded file. Example: /home/user/report.csv
        :return:
        """

        self.untyped_api.download("/download/h2o-k8s/report", path)

    @staticmethod
    def profile_value(values: Tuple[int, int, int]) -> ProfileValue:
        """
        Helper function to create a ProfileValue.

        :param values: Tuple of 3 values: minimal, maximal and initial profile value

        :return: ProfileValue
        """
        return ProfileValue(
            0, values[0], True, values[1], True, values[2], True, -1, True
        )

    @staticmethod
    def profile_value_with_limit(values: Tuple[int, int, int, int]) -> ProfileValue:
        """
        Helper function to create a ProfileValue with defined profile maximum limit.

        :param values: Tuple of 4 values: minimal, maximal, initial and maximum profile limit of profile value

        :return: ProfileValue
        """
        return ProfileValue(
            0, values[0], True, values[1], True, values[2], True, values[3], True
        )
