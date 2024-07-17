# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import h2osteam
import warnings

from .driverless_instance import DriverlessInstance
from h2osteam.utils import dai_instance_connect


class DriverlessClient:

    def __init__(self, steam=None):
        self.steam = steam

        self.launch_instance = self._launch_instance
        self.get_instance = self._get_instance

    def __api(self):
        return h2osteam.api() if self.steam is None else self.steam

    @staticmethod
    def launch_instance(name=None,
                        version=None,
                        profile_name=None,
                        cpu_count=None,
                        gpu_count=None,
                        memory_gb=None,
                        storage_gb=None,
                        max_idle_h=None,
                        max_uptime_h=None,
                        timeout_s=None,
                        config_toml_override=None,
                        sync=True,
                        volumes=""):

        """
        Launch new Driverless AI instance.

        The use of this static method is DEPRECATED in favour of `DriverlessClient().launch_instance()`
        and will be removed in v1.9

        Launches new Driverless AI instance using the parameters described below.
        You do not need to specify all parameters. In that case they will be filled
        based on the default values of the selected profile.
        The process of launching an instance can take up to 10 minutes.

        :param name: Name of the Driverless AI instance.
        :param version: Version of Driverless AI.
        :param profile_name: (Optional) Specify name of an existing profile that will be used for this cluster.
        :param cpu_count: (Optional) Number of CPUs (threads or virtual CPUs).
        :param gpu_count: (Optional) Number of GPUs.
        :param memory_gb: (Optional) Amount of memory in GB.
        :param storage_gb: (Optional) Amount of storage in GB.
        :param max_idle_h: (Optional) Maximum amount of time in hours the Driverless AI instance can be idle before shutting down.
        :param max_uptime_h: (Optional) Maximum amount of time in hours the the Driverless AI instance will be up before shutting down.
        :param timeout_s: (Optional) Maximum amount of time in seconds to wait for the Driverless AI instance to start.
        :param config_toml_override: (Optional) Enter additional Driverless AI configuration in TOML format that will be
         applied over the standard config.toml. Only available when permitted by selected profile. Override is limited
         to parameters allowed by profile.
        :param volumes: (Optional) Specify unbound volumes to mount with this instance.
        :param sync: Whether the call will block until the instance has finished launching. Otherwise use the wait() method.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import DriverlessClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> instance = DriverlessClient().launch_instance(name="test-instance",
        >>>                                               version="1.8.6.1",
        >>>                                               profile_name="default-driverless-kubernetes",
        >>>                                               gpu_count=1, memory_gb=32)

        """

        warnings.warn(
            "'DriverlessClient.launch_instance()' function is deprecated in favor of 'DriverlessClient("
            ").launch_instance()' and will be removed in v1.9",
            stacklevel=2
        )

        return DriverlessClient().launch_instance(name=name,
                                                  version=version,
                                                  profile_name=profile_name,
                                                  cpu_count=cpu_count,
                                                  gpu_count=gpu_count,
                                                  memory_gb=memory_gb,
                                                  storage_gb=storage_gb,
                                                  max_idle_h=max_idle_h,
                                                  max_uptime_h=max_uptime_h,
                                                  timeout_s=timeout_s,
                                                  config_toml_override=config_toml_override,
                                                  sync=sync,
                                                  volumes=volumes)

    def _launch_instance(self,
                         name=None,
                         version=None,
                         profile_name=None,
                         cpu_count=None,
                         gpu_count=None,
                         memory_gb=None,
                         storage_gb=None,
                         max_idle_h=None,
                         max_uptime_h=None,
                         timeout_s=None,
                         config_toml_override=None,
                         sync=True,
                         volumes=None):

        if name is None:
            raise Exception("Must enter valid instance name")
        if version is None:
            raise Exception("Must enter Driverless AI version")
        if profile_name is None:
            profile_name = "default-driverless-kubernetes"

        profile = self.__api().get_profile_by_name(profile_name)
        profile_type = profile['profile_type']

        if profile_type == "driverless_kubernetes":
            if cpu_count is None:
                cpu_count = profile[profile_type]['cpu_count']['initial']
            if gpu_count is None:
                gpu_count = profile[profile_type]['gpu_count']['initial']
            if memory_gb is None:
                memory_gb = profile[profile_type]['memory_gb']['initial']
            if storage_gb is None:
                storage_gb = profile[profile_type]['storage_gb']['initial']
            if max_idle_h is None:
                max_idle_h = profile[profile_type]['max_idle_hours']['initial']
            if max_uptime_h is None:
                max_uptime_h = profile[profile_type]['max_uptime_hours']['initial']
            if timeout_s is None:
                timeout_s = profile[profile_type]['timeout_seconds']['initial']

        instance_id = self.__api().launch_driverless_instance(parameters={
            "name": name,
            "profile_name": profile_name,
            "version": version,
            "cpu_count": cpu_count,
            "gpu_count": gpu_count,
            "memory_gb": memory_gb,
            "storage_gb": storage_gb,
            "timeout_seconds": timeout_s,
            "max_idle_hours": max_idle_h,
            "max_uptime_hours": max_uptime_h,
            "config_toml": config_toml_override,
            "volumes": volumes,
        })

        instance = DriverlessInstance(instance_id=instance_id, api=self.__api())

        if sync:
            print("Driverless AI instance is submitted, please wait...")
            instance.wait()

            if instance.status() == "running":
                print("Driverless AI instance is running")
            else:
                raise Exception("Driverless AI instance failed to start")

        return instance

    @staticmethod
    def get_instance(name=None, created_by=''):
        """
        Get existing Driverless AI instance.

        The use of this static method is DEPRECATED in favour of `DriverlessClient().get_instance()`
        and will be removed in v1.9

        :param name: Name of the Driverless AI instance.
        :param created_by: Name of the user that started the DAI instance.
        :returns: Driverless AI instance as an :class:`DriverlessInstance` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import DriverlessClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> instance = DriverlessClient().get_instance(name="test-instance")

        """

        warnings.warn(
            "'DriverlessClient.get_instance()' function is deprecated in favor of 'DriverlessClient().get_instance()' "
            "and will be removed in v1.9",
            stacklevel=2
        )

        return DriverlessClient().get_instance(name=name, created_by=created_by)

    def _get_instance(self, name=None, created_by=''):

        if name is None:
            raise Exception("Must enter instance name")

        if created_by:
            instance = self.__api().get_driverless_instance_created_by(name, created_by)
        else:
            instance = self.__api().get_driverless_instance(name)

        return DriverlessInstance(instance_id=instance['id'], api=self.__api())

    def get_instances(self):
        """
        Get a list of all Driverless AI instances that this user has permission to view.

        :returns: List of :class:`DriverlessInstance` objects.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import DriverlessClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here")
        >>> instances = DriverlessClient().get_instances()

        """
        out = []
        instances = self.__api().get_driverless_instances()

        for i in instances:
            out.append(DriverlessInstance(i["id"], api=self.__api()))

        return out

    @staticmethod
    def connect(api, id, use_h2oai_client=False, use_own_client=False, backend_version_override=None):
        return dai_instance_connect(api, id, use_h2oai_client, use_own_client, backend_version_override)
