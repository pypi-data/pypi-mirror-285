import http
import json

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException


def test_update(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    v = internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.3-update",
        image="h2o-3.40.0.3-update",
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
        gpu_resource_name="amd.com/gpu",
        annotations={"key1": "value1", "key2": "value2"}
    )

    v.version = "will be ignored"
    v.image = "h2o-3.40.0.3-update-new-image"
    v.image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    v.image_pull_secrets = ["secret1", "secret3"]
    v.gpu_resource_name = "nvidia.com/gpu"
    v.annotations = {"key1": "value1-updated", "key2": "value2", "key3": "value3"}
    v.deprecated = False

    updated = internal_h2o_version_client.update_version(internal_h2o_version=v)

    assert updated.name == "internalH2OVersions/3.40.0.3-update"
    assert updated.version == "3.40.0.3-update"
    assert updated.image == "h2o-3.40.0.3-update-new-image"
    assert updated.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert updated.image_pull_secrets == ["secret1", "secret3"]
    assert updated.aliases == []
    assert updated.gpu_resource_name == "nvidia.com/gpu"
    assert updated.annotations == {"key1": "value1-updated", "key2": "value2", "key3": "value3"}
    assert updated.deprecated == False


def test_h2o_version_update_latest_to_deprecated(internal_h2o_version_client, internal_h2o_version):
    # Arrange - assign alias "latest"
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id=internal_h2o_version.internal_h2o_version_id,
        aliases=["latest"]
    )
    latest_version = versions[0]
    latest_version.deprecated = True

    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.update_version(internal_h2o_version=latest_version)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'cannot have alias "latest" and be deprecated at the same time' \
           in json.loads(exc.value.body)["message"]

    # Extra test explicit update mask
    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.update_version(internal_h2o_version=latest_version, update_mask="deprecated")
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'cannot have alias "latest" and be deprecated at the same time' \
           in json.loads(exc.value.body)["message"]

    # Extra test that when deprecated field is not part of update mask that the update does not fail.
    updated = internal_h2o_version_client.update_version(internal_h2o_version=latest_version, update_mask="image")
    assert updated.deprecated is False


def test_h2o_version_update_non_latest_to_deprecated(internal_h2o_version_client, internal_h2o_version):
    # Test that it is still possible to set version to deprecated if it does not have alias 'latest'.

    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id=internal_h2o_version.internal_h2o_version_id,
        aliases=["non-latest"]
    )

    non_latest_version = versions[0]
    non_latest_version.deprecated = True

    v = internal_h2o_version_client.update_version(internal_h2o_version=non_latest_version)
    assert v.deprecated is True
    assert v.aliases == ["non-latest"]
