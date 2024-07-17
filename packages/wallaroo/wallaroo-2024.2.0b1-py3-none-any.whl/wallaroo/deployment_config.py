from .engine_config import Acceleration, Architecture
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union
import json, os

if TYPE_CHECKING:
    from .model_version import ModelVersion


class DeploymentConfig(Dict):
    def guarantee_workspace_id(self, workspace_id: Optional[int]) -> "DeploymentConfig":
        if workspace_id is None:
            return self
        if self.get("workspace_id", None) is None:
            self["workspace_id"] = workspace_id
        return self

    def _deploy_config_to_engine_config(self):
        from wallaroo.wallaroo_ml_ops_api_client.models import (
            EngineConfig,
            Resources,
            ResourcesSpec,
            ResourceSpec,
            Images,
            ImagesImagesType0 as ImagesImages,
        )

        if self is None:
            return None

        # Engine block
        engine = self.get("engine")
        cpus = engine.get("cpus", 1.0)
        mem = engine.get("memory", "512Mi")
        arch = engine.get("arch", str(Architecture.default()))
        accel = engine.get("accel", str(Acceleration.default()))
        gpu = engine.get("gpu", 0)
        image = engine.get("image")
        resource_spec = ResourceSpec(cpus, mem)
        resources = ResourcesSpec(
            resource_spec,
            resource_spec,
            Acceleration(accel),
            Architecture(arch),
            gpu > 0,
            image,
        )

        # TODO: Is the engine_aux block always empty or is there an openapi problem?
        config = EngineConfig(Resources(resources), Images(ImagesImages()))

        return config


class DeploymentConfigBuilder(object):
    def __init__(self, workspace_id: Optional[int] = None) -> None:
        self._config: Dict[str, Any] = {
            "engine": {},
            "enginelb": {},
            "engineAux": {"images": {}},
            **({"workspace_id": workspace_id} if workspace_id is not None else {}),
            "node_selector": {},
        }

        env_config = os.environ.get("DEPLOYMENT_CONFIG", None)

        if env_config:
            conf = json.loads(env_config)
            setters: Dict[str, Callable[[Any], Any]] = {
                "image": self.image,
                "replicas": self.replica_count,
                "autoscale": self._autoscale,
                "cpus": self.cpus,
                "gpus": self.gpus,
                "node_selector": self.deployment_label,
                "memory": self.memory,
                "lb_cpus": self.lb_cpus,
                "lb_memory": self.lb_memory,
            }
            for key, set in setters.items():
                if key in conf:
                    set(conf[key])
            if "arch" in conf:
                self.arch(Architecture[conf["arch"]])
            if "accel" in conf:
                self.accel(Acceleration[conf["accel"]])

    def image(self, image: str) -> "DeploymentConfigBuilder":
        self._config["engine"]["image"] = image
        return self

    def replica_count(self, count: int) -> "DeploymentConfigBuilder":
        if (
            "autoscale" in self._config["engine"]
            and self._config["engine"]["autoscale"]["replica_max"] < count
        ):
            raise RuntimeError(
                "Replica count must be less than or equal to replica max. Use replica_autoscale_min_max to adjust this."
            )
        self._config["engine"]["replicas"] = count
        return self

    def _autoscale(self, autoscale: Dict[str, Any]):
        self._config["engine"]["autoscale"] = autoscale
        return self

    def replica_autoscale_min_max(self, maximum: int, minimum: int = 0):
        """Configures the minimum and maximum for autoscaling"""
        if minimum > maximum:
            raise RuntimeError("Minimum must be less than or equal to maximum")
        if minimum < 0:
            raise RuntimeError("Minimum must be at least 0")
        if "autoscale" not in self._config["engine"]:
            self._config["engine"]["autoscale"] = {}
        if (
            "replicas" in self._config["engine"]
            and self._config["engine"]["replicas"] > maximum
        ):
            raise RuntimeError(
                "Maximum must be greater than or equal to number of replicas"
            )
        self._config["engine"]["autoscale"]["replica_min"] = minimum
        self._config["engine"]["autoscale"]["replica_max"] = maximum
        self._config["engine"]["autoscale"]["type"] = "cpu"
        return self

    def autoscale_cpu_utilization(self, cpu_utilization_percentage: int):
        """Sets the average CPU metric to scale on in a percentage"""
        if "autoscale" not in self._config["engine"]:
            print(
                "Warn: min and max not set for autoscaling. These must be set to enable autoscaling"
            )
            self._config["engine"]["autoscale"] = {}
        self._config["engine"]["autoscale"][
            "cpu_utilization"
        ] = cpu_utilization_percentage
        return self

    def disable_autoscale(self):
        """Disables autoscaling in the deployment configuration"""
        if "autoscale" in ["engine"]:
            del self._config["engine"]["autoscale"]
        return self

    def _add_resource(
        self,
        component_stanza: Dict[str, Any],
        resource_name: str,
        value: Union[int, str],
    ) -> "DeploymentConfigBuilder":
        if "resources" not in component_stanza:
            component_stanza["resources"] = {"limits": {}, "requests": {}}
        component_stanza["resources"]["limits"][resource_name] = value
        component_stanza["resources"]["requests"][resource_name] = value
        return self

    def cpus(self, core_count: int) -> "DeploymentConfigBuilder":
        self._config["engine"]["cpu"] = core_count
        return self._add_resource(self._config["engine"], "cpu", core_count)

    def deployment_label(self, label: str) -> "DeploymentConfigBuilder":
        self._config["engine"]["node_selector"] = label
        return self

    def gpus(self, gpu_count: int) -> "DeploymentConfigBuilder":
        self._config["engine"]["gpu"] = gpu_count
        DeploymentConfigBuilder._clear_gpu_resources(self._config["engine"])
        key = (
            "gpu.intel.com/i915"
            if self._config["engine"].get("accel") == "openvino"
            else "nvidia.com/gpu"
        )
        return self._add_resource(self._config["engine"], key, gpu_count)

    def memory(self, memory_spec: str) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["engine"], "memory", memory_spec)

    def lb_cpus(self, core_count: int) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["enginelb"], "cpu", core_count)

    def lb_memory(self, memory_spec: int) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["enginelb"], "memory", memory_spec)

    def arch(self, arch: Architecture) -> "DeploymentConfigBuilder":
        self._config["engine"]["arch"] = str(arch)
        return self

    def accel(self, accel: Acceleration) -> "DeploymentConfigBuilder":
        old_accel = self._config["engine"].get("accel", str(Acceleration.default()))
        self._config["engine"]["accel"] = str(accel)
        DeploymentConfigBuilder._adjust_gpu_resources(
            self._config["engine"], accel, old_accel
        )
        return self

    def python_load_timeout_secs(self, timeout_secs: int) -> "DeploymentConfigBuilder":
        if "python" not in self._config["engine"]:
            self._config["engine"]["python"] = {}
        self._config["engine"]["python"]["load_timeout_millis"] = timeout_secs * 1000
        return self

    def _guarantee_sidekick_stanza(
        self, model_version: "ModelVersion"
    ) -> Dict[str, Any]:
        model_uid = model_version.uid()
        if model_uid not in self._config["engineAux"]["images"]:
            self._config["engineAux"]["images"][model_uid] = {}
        return self._config["engineAux"]["images"][model_uid]

    def sidekick_gpus(
        self, model_version: "ModelVersion", gpu_count: int
    ) -> "DeploymentConfigBuilder":
        """Sets the number of GPUs to be used for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param int core_count: Number of GPUs to use in this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""

        sidekick = self._guarantee_sidekick_stanza(model_version)
        DeploymentConfigBuilder._clear_gpu_resources(sidekick)
        key = (
            "gpu.intel.com/i915"
            if sidekick.get("accel") == "openvino"
            else "nvidia.com/gpu"
        )
        return self._add_resource(sidekick, key, gpu_count)

    def sidekick_cpus(
        self, model_version: "ModelVersion", core_count: int
    ) -> "DeploymentConfigBuilder":
        """Sets the number of CPUs to be used for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param int core_count: Number of CPU cores to use in this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""
        from .model_version import ModelVersion

        return self._add_resource(
            self._guarantee_sidekick_stanza(model_version), "cpu", core_count
        )

    def sidekick_memory(
        self, model_version: "ModelVersion", memory_spec: str
    ) -> "DeploymentConfigBuilder":
        """Sets the memory to be used for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param str memory_spec: Specification of amount of memory (e.g., "2Gi", "500Mi") to use in
        this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""

        return self._add_resource(
            self._guarantee_sidekick_stanza(model_version), "memory", memory_spec
        )

    def sidekick_env(
        self, model_version: "ModelVersion", environment: Dict[str, str]
    ) -> "DeploymentConfigBuilder":
        """Sets the environment variables to be set for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param Dict[str, str] environment: Dictionary of environment variables names and their
        corresponding values to be set in the sidekick container.
        :return: This DeploymentConfigBuilder instance for chaining."""

        stanza = self._guarantee_sidekick_stanza(model_version)
        stanza["env"] = []
        for name, value in environment.items():
            stanza["env"].append({"name": name, "value": value})

        return self

    def sidekick_arch(
        self, model_version: "ModelVersion", architecture: Architecture
    ) -> "DeploymentConfigBuilder":
        """Sets the machine architecture for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param Architecture architecture: Machine architecture for this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""

        config = self._guarantee_sidekick_stanza(model_version)
        config["arch"] = str(architecture)
        return self

    def sidekick_accel(
        self, model_version: "ModelVersion", acceleration: Acceleration
    ) -> "DeploymentConfigBuilder":
        """Sets the acceleration option for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param ModelVersion model_version: The sidekick model to configure.
        :param Acceleration acceleration: Acceleration option for this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""

        config = self._guarantee_sidekick_stanza(model_version)
        old_accel = config.get("accel", str(Acceleration.default()))
        config["accel"] = str(acceleration)
        DeploymentConfigBuilder._adjust_gpu_resources(config, acceleration, old_accel)
        return self

    @staticmethod
    def _adjust_gpu_resources(component: Dict[str, Any], accel: Acceleration, old: str):
        resources = component.get("resources", {"limits": {}, "requests": {}})
        if accel == Acceleration.OpenVINO and old != "openvino":
            limit = resources["limits"].pop("nvidia.com/gpu", None)
            if limit is not None:
                resources["limits"]["gpu.intel.com/i915"] = limit
            request = resources["requests"].pop("nvidia.com/gpu", None)
            if request is not None:
                resources["requests"]["gpu.intel.com/i915"] = request
        elif accel == Acceleration.CUDA and old == "openvino":
            limit = resources["limits"].pop("gpu.intel.com/i915", None)
            if limit is not None:
                resources["limits"]["nvidia.com/gpu"] = limit
            request = resources["requests"].pop("gpu.intel.com/i915", None)
            if request is not None:
                resources["requests"]["nvidia.com/gpu"] = request

    @staticmethod
    def _clear_gpu_resources(component: Dict[str, Any]):
        resources = component.get("resources", {"limits": {}, "requests": {}})
        resources["limits"].pop("gpu.intel.com/i915", None)
        resources["limits"].pop("nvidia.com/gpu", None)
        resources["requests"].pop("gpu.intel.com/i915", None)
        resources["requests"].pop("nvidia.com/gpu", None)

    def build(self) -> DeploymentConfig:
        return DeploymentConfig(self._config)
