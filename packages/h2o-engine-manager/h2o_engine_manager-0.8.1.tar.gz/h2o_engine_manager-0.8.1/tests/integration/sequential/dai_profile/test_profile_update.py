import http

import pytest

from h2o_engine_manager.clients.exception import CustomApiException


@pytest.mark.parametrize(
    "mask",
    [
        "unknown",
        "invalid character",
        "gpu, *",
        " ",
    ],
)
def test_update_mask_validation(dai_profile_client, mask, dai_profile_cleanup_after):
    profile = dai_profile_client.create_profile(
        profile_id="profile1",
        cpu=1,
        gpu=0,
        memory_bytes="1Gi",
        storage_bytes="1Gi",
        display_name="Smokerinho",
    )
    profile.display_name = "Changed Smokerinho"

    with pytest.raises(CustomApiException) as exc:
        dai_profile_client.update_profile(profile=profile, update_mask=mask)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_update(dai_profile_client, dai_profile):
    dai_profile.cpu = 2
    dai_profile.gpu = 1
    dai_profile.memory_bytes = "2Mi"
    dai_profile.storage_bytes = "2Mi"

    # Update profile with update_mask.
    updated = dai_profile_client.update_profile(dai_profile, update_mask="cpu,memory_bytes")

    assert updated.cpu == 2
    assert updated.gpu == 0
    assert updated.memory_bytes == "2Mi"
    assert updated.storage_bytes == "1Gi"

    # Update profile without update_mask (update all).
    updated = dai_profile_client.update_profile(dai_profile)

    assert updated.cpu == 2
    assert updated.gpu == 1
    assert updated.memory_bytes == "2Mi"
    assert updated.storage_bytes == "2Mi"


def test_update_validate_only_update_mask_fields(dai_profile_client, dai_profile):
    dai_profile.cpu = 2
    # Set invalid GPU.
    dai_profile.gpu = -1
    dai_profile.memory_bytes = "2Mi"
    # Set invalid storage bytes.
    dai_profile.storage_bytes = "0"

    # Update only cpu and memory_bytes.
    updated = dai_profile_client.update_profile(dai_profile, update_mask="cpu,memory_bytes")

    assert updated.cpu == 2
    assert updated.gpu == 0
    assert updated.memory_bytes == "2Mi"
    assert updated.storage_bytes == "1Gi"

    # Try to update all, should get BAD_REQUEST due to invalid .
    with pytest.raises(CustomApiException) as exc:
        dai_profile_client.update_profile(profile=dai_profile)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
