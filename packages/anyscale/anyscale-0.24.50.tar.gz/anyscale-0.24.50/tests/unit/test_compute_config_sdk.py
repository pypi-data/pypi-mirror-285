from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import uuid

from common import OPENAPI_NO_VALIDATION, TestLogger
import pytest

from anyscale import Anyscale
from anyscale._private.anyscale_client import FakeAnyscaleClient
from anyscale._private.sdk.timer import FakeTimer
from anyscale.client.openapi_client.models import (
    Cloud,
    CloudProviders,
    ComputeNodeType as InternalApiComputeNodeType,
    ComputeTemplateConfig,
    DecoratedComputeTemplate,
    Resources,
    WorkerNodeType as InternalApiWorkerNodeType,
)
from anyscale.compute_config import ComputeConfigSDK
from anyscale.compute_config.models import (
    ComputeConfig,
    ComputeConfigVersion,
    HeadNodeConfig,
    MarketType,
    WorkerNodeGroupConfig,
)
from anyscale.sdk.anyscale_client.models import (
    ClusterCompute,
    ClusterComputeConfig,
    ComputeNodeType,
)


@pytest.fixture()
def compute_config_sdk_with_fakes(
    sdk_with_fakes: Tuple[Anyscale, FakeAnyscaleClient, TestLogger, FakeTimer]
) -> Tuple[ComputeConfigSDK, FakeAnyscaleClient]:
    sdk, client, _, _ = sdk_with_fakes
    return sdk.compute_config, client


class TestCreateComputeConfig:
    def test_name(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        # First version.
        full_name_1 = sdk.create(ComputeConfig(), name="test-compute-config-name")
        compute_config_id_1 = sdk.get(full_name_1).id
        assert full_name_1 == "test-compute-config-name:1"

        created_compute_config_1 = fake_client.get_compute_config(compute_config_id_1)
        assert created_compute_config_1 is not None
        assert created_compute_config_1.name == "test-compute-config-name"

        # Second version.
        full_name_2 = sdk.create(ComputeConfig(), name="test-compute-config-name")
        compute_config_id_2 = sdk.get(full_name_2).id
        assert full_name_2 == "test-compute-config-name:2"

        created_compute_config_2 = fake_client.get_compute_config(compute_config_id_2)
        assert created_compute_config_2 is not None
        assert created_compute_config_2.name == "test-compute-config-name"

    def test_name_with_version_tag(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        with pytest.raises(
            ValueError,
            match="A version tag cannot be provided when creating a compute config. The latest version tag will be generated and returned.",
        ):
            sdk.create(ComputeConfig(), name="test-compute-config-name:1")

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("has_no_worker_nodes", [False, True])
    def test_no_head_node_uses_cloud_default(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        has_no_worker_nodes: bool,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        custom_cloud_name = "test-non-default-cloud"
        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=custom_cloud_name,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud_name)
        fake_client.set_default_compute_config(
            ClusterCompute(
                id="test-custom-compute-config-id",
                config=ClusterComputeConfig(
                    cloud_id=custom_cloud_id,
                    head_node_type=ComputeNodeType(
                        name="non-default-head",
                        instance_type="custom-instance-type",
                        resources={"CPU": 24, "GPU": 2, "custom": 1},
                    ),
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            cloud_id=custom_cloud_id,
        )

        config = ComputeConfig()
        if has_no_worker_nodes:
            # Explicitly set no worker nodes.
            # Only in this case should the head node be schedulable.
            config = config.options(worker_nodes=[])
        if use_custom_cloud:
            config = config.options(cloud=custom_cloud_name)

        full_name = sdk.create(config, name="test123")
        compute_config_id = sdk.get(full_name).id
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        # Serverless worker config should only be set if worker_nodes is `None`.
        assert created.auto_select_worker_config is not has_no_worker_nodes

        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
            assert created.head_node_type.instance_type == "custom-instance-type"
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID
            default_compute_config = fake_client.get_default_compute_config(
                cloud_id=fake_client.DEFAULT_CLOUD_ID
            )
            assert (
                created.head_node_type.instance_type
                == default_compute_config.config.head_node_type.instance_type
            )

        if has_no_worker_nodes:
            assert created.head_node_type.resources is None
        else:
            assert created.head_node_type.resources == Resources(cpu=0, gpu=0)

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("has_no_worker_nodes", [False, True])
    @pytest.mark.parametrize("has_resources", [False, True])
    def test_custom_head_node(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        has_no_worker_nodes: bool,
        has_resources: bool,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        custom_cloud_name = "test-non-default-cloud"
        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=custom_cloud_name,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud_name)

        head_node_config = HeadNodeConfig(instance_type="head-node-instance-type",)
        if has_resources:
            head_node_config = head_node_config.options(
                resources={"CPU": 1, "head_node": 1}
            )

        config = ComputeConfig(head_node=head_node_config)
        if has_no_worker_nodes:
            # Explicitly set no worker nodes.
            # Only in this case should the head node be schedulable.
            config = config.options(worker_nodes=[])
        if use_custom_cloud:
            config = config.options(cloud=custom_cloud_name)

        full_name = sdk.create(config, name="test123")
        compute_config_id = sdk.get(full_name).id
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID

        assert created.head_node_type.instance_type == "head-node-instance-type"

        # Serverless worker config should only be set if worker_nodes is `None`.
        assert created.auto_select_worker_config is not has_no_worker_nodes

        # If the user explicitly provides resources, they should always be set.
        if has_resources:
            assert created.head_node_type.resources == Resources(
                cpu=1, custom_resources={"head_node": 1}
            )
        # If there are no worker nodes, resources should be empty (populated by backend).
        elif has_no_worker_nodes:
            assert created.head_node_type.resources is None
        # Otherwise, head node is unschedulable by default.
        else:
            assert created.head_node_type.resources == Resources(cpu=0, gpu=0)

    @pytest.mark.parametrize(
        "provider",
        [CloudProviders.AWS, CloudProviders.GCP, CloudProviders.CLOUDGATEWAY],
    )
    @pytest.mark.parametrize("advanced_instance_config", [None, {}, {"foo": "bar"}])
    @pytest.mark.parametrize(
        "location", ["TOP_LEVEL", "HEAD", "WORKER"],
    )
    def test_advanced_instance_config(  # noqa: PLR0912
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        provider: CloudProviders,
        advanced_instance_config: Optional[Dict],
        location: str,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        custom_cloud_name = "test-non-default-cloud"
        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=custom_cloud_name,
                provider=provider,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud_name)

        config = ComputeConfig(
            cloud=custom_cloud_name,
            advanced_instance_config=advanced_instance_config
            if location == "TOP_LEVEL"
            else None,
            head_node=HeadNodeConfig(
                instance_type="head-node-instance-type",
                advanced_instance_config=advanced_instance_config
                if location == "HEAD"
                else None,
            ),
            worker_nodes=[
                WorkerNodeGroupConfig(
                    instance_type="worker-node-instance-type",
                    advanced_instance_config=advanced_instance_config
                    if location == "WORKER"
                    else None,
                ),
            ],
        )

        if advanced_instance_config and provider not in {
            CloudProviders.AWS,
            CloudProviders.GCP,
        }:
            with pytest.raises(
                ValueError,
                match=f"'advanced_instance_config' is not implemented for cloud provider: '{provider}'",
            ):
                sdk.create(config, name="test123")

            return

        full_name = sdk.create(config, name="test123")
        compute_config_id = sdk.get(full_name).id
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        assert created.cloud_id == custom_cloud_id
        assert created.head_node_type.instance_type == "head-node-instance-type"
        if not advanced_instance_config:
            assert created.aws_advanced_configurations_json is None
            assert created.gcp_advanced_configurations_json is None
            assert created.head_node_type.aws_advanced_configurations_json is None
            assert created.head_node_type.gcp_advanced_configurations_json is None
            assert created.worker_node_types[0].aws_advanced_configurations_json is None
            assert created.worker_node_types[0].gcp_advanced_configurations_json is None
        elif provider == CloudProviders.AWS:
            if location == "TOP_LEVEL":
                assert (
                    created.aws_advanced_configurations_json == advanced_instance_config
                )
            else:
                assert created.aws_advanced_configurations_json is None
            assert created.gcp_advanced_configurations_json is None

            if location == "HEAD":
                assert (
                    created.head_node_type.aws_advanced_configurations_json
                    == advanced_instance_config
                )
            else:
                assert created.head_node_type.aws_advanced_configurations_json is None
            assert created.head_node_type.gcp_advanced_configurations_json is None

            if location == "WORKER":
                assert (
                    created.worker_node_types[0].aws_advanced_configurations_json
                    == advanced_instance_config
                )
            else:
                assert (
                    created.worker_node_types[0].aws_advanced_configurations_json
                    is None
                )
            assert created.worker_node_types[0].gcp_advanced_configurations_json is None

        elif provider == CloudProviders.GCP:
            assert created.aws_advanced_configurations_json is None
            if location == "TOP_LEVEL":
                assert (
                    created.gcp_advanced_configurations_json == advanced_instance_config
                )
            else:
                assert created.gcp_advanced_configurations_json is None

            assert created.head_node_type.aws_advanced_configurations_json is None
            if location == "HEAD":
                assert (
                    created.head_node_type.gcp_advanced_configurations_json
                    == advanced_instance_config
                )
            else:
                assert created.head_node_type.gcp_advanced_configurations_json is None

            assert created.worker_node_types[0].aws_advanced_configurations_json is None
            if location == "WORKER":
                assert (
                    created.worker_node_types[0].gcp_advanced_configurations_json
                    == advanced_instance_config
                )
            else:
                assert (
                    created.worker_node_types[0].gcp_advanced_configurations_json
                    is None
                )
        else:
            raise AssertionError(f"Unexpected provider '{provider}'")

    @pytest.mark.parametrize("use_custom_cloud", [False, True])
    @pytest.mark.parametrize("enable_cross_zone_scaling", [False, True])
    @pytest.mark.parametrize("zones", [None, ["zone1", "zone2"]])
    @pytest.mark.parametrize("max_resources", [None, {"CPU": 10, "GPU": 5}])
    @pytest.mark.parametrize(
        "cluster_flags",
        [None, {"fake-cluster-feature-1": True, "fake-cluster-feature-2": "yes"}],
    )
    @pytest.mark.parametrize(
        "head_node_flags",
        [None, {"fake-head-node-feature-1": False, "fake-head-node-feature-2": "no"}],
    )
    def test_flags(  # noqa: PLR0913
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_custom_cloud: bool,
        enable_cross_zone_scaling: bool,
        zones: Optional[List[str]],
        max_resources: Optional[Dict[str, float]],
        cluster_flags: Optional[Dict[str, Any]],
        head_node_flags: Optional[Dict[str, Any]],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        custom_cloud_name = "test-non-default-cloud"
        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=custom_cloud_name,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        custom_cloud_id = fake_client.get_cloud_id(cloud_name=custom_cloud_name)

        head_node_config = HeadNodeConfig(instance_type="head-node-instance-type",)
        if head_node_flags:
            head_node_config = head_node_config.options(flags=head_node_flags)

        config = ComputeConfig(
            head_node=head_node_config, zones=zones, max_resources=max_resources,
        )
        if use_custom_cloud:
            config = config.options(cloud=custom_cloud_name)
        if enable_cross_zone_scaling:
            config = config.options(enable_cross_zone_scaling=True)
        if cluster_flags:
            config = config.options(flags=cluster_flags)

        full_name = sdk.create(config, name="test123")
        compute_config_id = sdk.get(full_name).id
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config
        if use_custom_cloud:
            assert created.cloud_id == custom_cloud_id
        else:
            assert created.cloud_id == fake_client.DEFAULT_CLOUD_ID

        assert created.head_node_type.instance_type == "head-node-instance-type"
        if head_node_flags:
            for key, value in head_node_flags.items():
                assert created.head_node_type.flags[key] == value

        assert (
            created.flags["allow-cross-zone-autoscaling"] == enable_cross_zone_scaling
        )
        assert created.allowed_azs == zones
        assert created.auto_select_worker_config is True
        if max_resources is None:
            assert "max-cpus" not in created.flags
            assert "max-gpus" not in created.flags
        else:
            assert created.flags["max-cpus"] == max_resources["CPU"]
            assert created.flags["max-gpus"] == max_resources["GPU"]
        if cluster_flags:
            for key, value in cluster_flags.items():
                assert created.flags[key] == value

    def test_custom_worker_nodes(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        config = ComputeConfig(
            worker_nodes=[
                WorkerNodeGroupConfig(instance_type="instance-type-1",),
                WorkerNodeGroupConfig(
                    name="group2",
                    instance_type="instance-type-2",
                    min_nodes=0,
                    max_nodes=100,
                    market_type=MarketType.SPOT,
                ),
                WorkerNodeGroupConfig(
                    name="group3",
                    instance_type="instance-type-2",
                    min_nodes=0,
                    max_nodes=100,
                    resources={"CPU": 1000, "custom": 1},
                    market_type=MarketType.PREFER_SPOT,
                    flags={
                        "fake-worker-node-feature-1": False,
                        "fake-worker-node-feature-2": "no",
                    },
                ),
            ],
        )

        full_name = sdk.create(config, name="test123")
        compute_config_id = sdk.get(full_name).id
        created_compute_config = fake_client.get_compute_config(compute_config_id)
        assert created_compute_config is not None

        created = created_compute_config.config

        # Serverless worker config should not be set if worker nodes are provided.
        assert created.auto_select_worker_config is False

        assert created.worker_node_types[0].name == "instance-type-1"
        assert created.worker_node_types[0].instance_type == "instance-type-1"
        assert created.worker_node_types[0].resources is None
        assert created.worker_node_types[0].min_workers == 0
        assert created.worker_node_types[0].max_workers == 10
        assert created.worker_node_types[0].use_spot is False
        assert created.worker_node_types[0].fallback_to_ondemand is False

        assert created.worker_node_types[1].name == "group2"
        assert created.worker_node_types[1].instance_type == "instance-type-2"
        assert created.worker_node_types[1].resources is None
        assert created.worker_node_types[1].min_workers == 0
        assert created.worker_node_types[1].max_workers == 100
        assert created.worker_node_types[1].use_spot is True
        assert created.worker_node_types[1].fallback_to_ondemand is False

        assert created.worker_node_types[2].name == "group3"
        assert created.worker_node_types[2].instance_type == "instance-type-2"
        assert created.worker_node_types[2].resources == Resources(
            cpu=1000, custom_resources={"custom": 1}
        )
        assert created.worker_node_types[2].min_workers == 0
        assert created.worker_node_types[2].max_workers == 100
        assert created.worker_node_types[2].use_spot is True
        assert created.worker_node_types[2].fallback_to_ondemand is True

        assert created.worker_node_types[2].flags["fake-worker-node-feature-1"] is False
        assert created.worker_node_types[2].flags["fake-worker-node-feature-2"] == "no"


@dataclass
class ResourcesTestCase:
    api_resources: Optional[Resources]
    expected_resources_dict: Optional[Dict[str, float]]


RESOURCES_TEST_CASES = [
    ResourcesTestCase(None, None),
    ResourcesTestCase(Resources(), {}),
    ResourcesTestCase(Resources(cpu=1), {"CPU": 1}),
    ResourcesTestCase(
        Resources(cpu=1, gpu=2, memory=1024, object_store_memory=1024 ** 2),
        {"CPU": 1, "GPU": 2, "memory": 1024, "object_store_memory": 1024 ** 2},
    ),
    # Keys with `None` values should be omitted.
    ResourcesTestCase(Resources(cpu=1, gpu=None), {"CPU": 1}),
    # custom_resources field should be flattened.
    ResourcesTestCase(
        Resources(cpu=1, custom_resources={"custom": 123}), {"CPU": 1, "custom": 123}
    ),
]


class TestGetComputeConfig:
    def test_no_name_or_id(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, _ = compute_config_sdk_with_fakes
        with pytest.raises(ValueError, match="Either name or ID must be provided."):
            sdk.get(name="")

    def test_not_found(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        with pytest.raises(
            RuntimeError, match="Compute config 'does-not-exist' not found."
        ):
            sdk.get(name="does-not-exist")

        with pytest.raises(
            RuntimeError, match="Compute config with ID 'does-not-exist' not found."
        ):
            sdk.get(name="", _id="does-not-exist")

    @pytest.mark.parametrize("by_id", [False, True])
    def test_cloud_name(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        by_id: bool,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="default-cloud-compute-config-id",
                name="default-cloud-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        default_cloud_config: ComputeConfig = sdk.get(
            _id="default-cloud-compute-config-id" if by_id else None,
            name="default-cloud-compute-config-name" if not by_id else "",
        ).config
        assert default_cloud_config.cloud == fake_client.DEFAULT_CLOUD_NAME

        fake_client.add_cloud(
            Cloud(
                id="fake-custom-cloud-id",
                name="fake-custom-cloud",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="custom-cloud-compute-config-id",
                name="custom-cloud-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id="fake-custom-cloud-id",
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        custom_cloud_config: ComputeConfig = sdk.get(
            _id="custom-cloud-compute-config-id" if by_id else None,
            name="custom-cloud-compute-config-name" if not by_id else None,
        ).config
        assert custom_cloud_config.cloud == "fake-custom-cloud"

    @pytest.mark.parametrize(
        ("api_zones", "expected_zones"),
        [
            (None, None),
            ([], None),
            # API returns ["any"] if no zones are passed in.
            (["any"], None),
            (["az1"], ["az1"]),
            (["az1", "az2"], ["az1", "az2"]),
        ],
    )
    def test_zones(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        api_zones: Optional[List[str]],
        expected_zones: Optional[List[str]],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    allowed_azs=api_zones,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.zones == expected_zones

    @pytest.mark.parametrize(
        ("flags", "expected"),
        [
            (None, False),
            ({}, False),
            ({"something-else": "foobar"}, False),
            ({"allow-cross-zone-autoscaling": False}, False),
            ({"allow-cross-zone-autoscaling": True}, True),
        ],
    )
    def test_enable_cross_zone_scaling(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        flags: Optional[Dict],
        expected: bool,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    flags=flags,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.enable_cross_zone_scaling == expected

    @pytest.mark.parametrize(
        ("flags", "expected"),
        [
            (None, None),
            ({}, None),
            ({"max-cpus": None, "max-gpus": None}, None),
            ({"max-cpus": 10, "max-gpus": None}, {"CPU": 10}),
            ({"max-cpus": None, "max-gpus": 5}, {"GPU": 5}),
            ({"max-cpus": 10, "max-gpus": 5}, {"CPU": 10, "GPU": 5}),
        ],
    )
    def test_max_resources(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        flags: Optional[Dict],
        expected: Optional[Dict],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    flags=flags,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.max_resources == expected

    def test_auto_select_worker_config(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="serverless-compute-config-id",
                name="serverless-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    auto_select_worker_config=True,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        serverless_config: ComputeConfig = sdk.get(
            name="serverless-compute-config-name"
        ).config
        assert serverless_config.worker_nodes is None

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="non-serverless-compute-config-id",
                name="non-serverless-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    auto_select_worker_config=False,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        non_serverless_config: ComputeConfig = sdk.get(
            name="non-serverless-compute-config-name"
        ).config
        assert non_serverless_config.worker_nodes == []

    @pytest.mark.parametrize("test_case", RESOURCES_TEST_CASES)
    def test_convert_head_node(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        test_case: ResourcesTestCase,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name",
                        instance_type="head-node-instance-type",
                        resources=test_case.api_resources,
                    ),
                    worker_node_types=[],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.head_node == HeadNodeConfig(
            instance_type="head-node-instance-type",
            resources=test_case.expected_resources_dict,
        )

    @pytest.mark.parametrize("test_case", RESOURCES_TEST_CASES)
    def test_convert_worker_nodes(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        test_case: ResourcesTestCase,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[
                        InternalApiWorkerNodeType(
                            name="basic",
                            instance_type="instance-type-1",
                            min_workers=0,
                            max_workers=10,
                        ),
                        InternalApiWorkerNodeType(
                            name="custom-resources",
                            instance_type="instance-type-2",
                            resources=test_case.api_resources,
                            min_workers=1,
                            max_workers=1,
                        ),
                        InternalApiWorkerNodeType(
                            name="min-workers-none",
                            instance_type="instance-type-3",
                            min_workers=None,
                            max_workers=1,
                        ),
                        InternalApiWorkerNodeType(
                            name="max-workers-none",
                            instance_type="instance-type-4",
                            min_workers=0,
                            max_workers=None,
                        ),
                    ],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.worker_nodes == [
            WorkerNodeGroupConfig(
                name="basic",
                instance_type="instance-type-1",
                min_nodes=0,
                max_nodes=10,
            ),
            WorkerNodeGroupConfig(
                name="custom-resources",
                instance_type="instance-type-2",
                resources=test_case.expected_resources_dict,
                min_nodes=1,
                max_nodes=1,
            ),
            WorkerNodeGroupConfig(
                name="min-workers-none",
                instance_type="instance-type-3",
                min_nodes=0,
                max_nodes=1,
            ),
            WorkerNodeGroupConfig(
                name="max-workers-none",
                instance_type="instance-type-4",
                min_nodes=0,
                max_nodes=10,
            ),
        ]

    def test_worker_node_market_type(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[
                        InternalApiWorkerNodeType(
                            name="on-demand-worker-node-group",
                            instance_type="on-demand-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=False,
                            fallback_to_ondemand=False,
                        ),
                        InternalApiWorkerNodeType(
                            name="spot-worker-node-group",
                            instance_type="spot-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=True,
                            fallback_to_ondemand=False,
                        ),
                        InternalApiWorkerNodeType(
                            name="prefer-spot-worker-node-group",
                            instance_type="prefer-spot-worker-node-group",
                            min_workers=1,
                            max_workers=1,
                            use_spot=True,
                            fallback_to_ondemand=True,
                        ),
                    ],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.worker_nodes == [
            WorkerNodeGroupConfig(
                name="on-demand-worker-node-group",
                instance_type="on-demand-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.ON_DEMAND,
            ),
            WorkerNodeGroupConfig(
                name="spot-worker-node-group",
                instance_type="spot-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.SPOT,
            ),
            WorkerNodeGroupConfig(
                name="prefer-spot-worker-node-group",
                instance_type="prefer-spot-worker-node-group",
                min_nodes=1,
                max_nodes=1,
                market_type=MarketType.PREFER_SPOT,
            ),
        ]

    @pytest.mark.parametrize(
        "provider", [CloudProviders.AWS, CloudProviders.GCP],
    )
    @pytest.mark.parametrize("advanced_instance_config", [None, {}, {"foo": "bar"}])
    @pytest.mark.parametrize(
        "location", ["TOP_LEVEL", "HEAD", "WORKER"],
    )
    def test_advanced_instance_config(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        provider: CloudProviders,
        advanced_instance_config: Optional[Dict],
        location: str,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes
        fake_client.add_cloud(
            Cloud(
                id="fake-custom-cloud-id",
                name="fake-custom-cloud",
                provider=provider,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        aws_config = (
            advanced_instance_config if provider == CloudProviders.AWS else None
        )
        gcp_config = (
            advanced_instance_config if provider == CloudProviders.GCP else None
        )
        fake_client.add_compute_config(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id="fake-custom-cloud-id",
                    aws_advanced_configurations_json=aws_config
                    if location == "TOP_LEVEL"
                    else None,
                    gcp_advanced_configurations_json=gcp_config
                    if location == "TOP_LEVEL"
                    else None,
                    head_node_type=InternalApiComputeNodeType(
                        name="head-node-name",
                        instance_type="head-node-instance-type",
                        aws_advanced_configurations_json=aws_config
                        if location == "HEAD"
                        else None,
                        gcp_advanced_configurations_json=gcp_config
                        if location == "HEAD"
                        else None,
                    ),
                    worker_node_types=[
                        InternalApiWorkerNodeType(
                            name="worker-node-group",
                            instance_type="worker-node-group",
                            aws_advanced_configurations_json=aws_config
                            if location == "WORKER"
                            else None,
                            gcp_advanced_configurations_json=gcp_config
                            if location == "WORKER"
                            else None,
                        ),
                    ],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config: ComputeConfig = sdk.get(name="fake-compute-config-name").config
        assert config.advanced_instance_config == (
            advanced_instance_config or None if location == "TOP_LEVEL" else None
        )
        assert isinstance(config.head_node, HeadNodeConfig)
        assert config.head_node.advanced_instance_config == (
            advanced_instance_config or None if location == "HEAD" else None
        )
        assert isinstance(config.worker_nodes, list) and isinstance(
            config.worker_nodes[0], WorkerNodeGroupConfig
        )
        assert config.worker_nodes[0].advanced_instance_config == (
            advanced_instance_config or None if location == "WORKER" else None
        )


class TestArchive:
    def test_not_found(
        self, compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient]
    ):
        sdk, _ = compute_config_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Compute config 'does-not-exist' not found"
        ):
            sdk.archive(name="does-not-exist")

    @pytest.mark.parametrize("use_full_name", [False, True])
    def test_basic(
        self,
        compute_config_sdk_with_fakes: Tuple[ComputeConfigSDK, FakeAnyscaleClient],
        use_full_name: bool,
    ):
        sdk, fake_client = compute_config_sdk_with_fakes

        full_name = sdk.create(ComputeConfig(), name="test-compute-config-name")
        compute_config_id = sdk.get(full_name).id

        assert full_name == "test-compute-config-name:1"

        assert not fake_client.is_archived_compute_config(compute_config_id)

        if use_full_name:
            sdk.archive(name=full_name)
        else:
            sdk.archive(name="test-compute-config-name")

        assert fake_client.is_archived_compute_config(compute_config_id)

        with pytest.raises(
            RuntimeError, match="Compute config 'test-compute-config-name' not found"
        ):
            sdk.get(name="test-compute-config-name")

        archived_version: ComputeConfigVersion = sdk.get(
            name="test-compute-config-name", include_archived=True
        )
        assert archived_version.config is not None
