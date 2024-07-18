import http
import json

import pytest

from h2o_engine_manager.clients.exception import CustomApiException


def test_assign_internal_h2o_version_aliases(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.3",
        image="h2o-3.40.0.3",
    )
    internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.4",
        image="h2o-3.40.0.4",
    )
    internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.5",
        image="h2o-3.40.0.5",
    )

    internal_h2o_version_client.assign_aliases(internal_h2o_version_id="3.40.0.3", aliases=["foo"])
    internal_h2o_version_client.assign_aliases(internal_h2o_version_id="3.40.0.4", aliases=["bar", "baz"])
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.5", aliases=["latest", "wow"],
    )

    assert len(versions) == 3
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == ["latest", "wow"]
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo"]

    # Nothing will change when assigning the existing aliases.
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.4", aliases=["bar", "baz"],
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == ["latest", "wow"]
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo"]

    # Remove alias "wow" by assigning reduced existing aliases.
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.5", aliases=["latest"],
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == ["latest"]
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo"]

    # Move alias "latest" to another version
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.4", aliases=["bar", "baz", "latest"],
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == []
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == ["bar", "baz", "latest"]
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo"]

    # Add new alias
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.3", aliases=["foo", "new-foo"],
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == []
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == ["bar", "baz", "latest"]
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo", "new-foo"]

    # Delete all aliases
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id="3.40.0.4", aliases=[],
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].aliases == []
    assert versions[1].internal_h2o_version_id == "3.40.0.4"
    assert versions[1].aliases == []
    assert versions[2].internal_h2o_version_id == "3.40.0.3"
    assert versions[2].aliases == ["foo", "new-foo"]


def test_assign_internal_h2o_version_alias_conflict(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.3",
        image="h2o-3.40.0.3",
    )
    internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.4",
        image="h2o-3.40.0.4",
    )

    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.assign_aliases(internal_h2o_version_id="3.40.0.3", aliases=["3.40.0.4"])

    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'alias conflict: version 3.40.0.4 already exists, cannot assign the same named alias 3.40.0.4' \
           in json.loads(exc.value.body)["message"]


def test_assign_non_existing_version(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.assign_aliases(internal_h2o_version_id="non-existing", aliases=["3.40.0.4"])

    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_assign_invalid_version_name(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    # Server checks for correct InternalH2OVersion resource name format 'internalH2OVersions/*'.

    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.assign_aliases(internal_h2o_version_id="3.40.0.4/foo", aliases=["3.40.0.4"])

    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'invalid InternalH2OVersion name "internalH2OVersions/3.40.0.4/foo"'


def test_h2o_version_assign_latest_to_deprecated(internal_h2o_version_client, internal_h2o_version):
    # Arrange - set version to deprecated
    internal_h2o_version.deprecated = True
    updated_version = internal_h2o_version_client.update_version(
        internal_h2o_version=internal_h2o_version
    )

    with pytest.raises(CustomApiException) as exc:
        internal_h2o_version_client.assign_aliases(
            internal_h2o_version_id=updated_version.internal_h2o_version_id,
            aliases=["latest"]
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'cannot have alias "latest" and be deprecated at the same time' \
           in json.loads(exc.value.body)["message"]


def test_h2o_version_assign_non_latest_to_deprecated(internal_h2o_version_client, internal_h2o_version):
    # Arrange - set version to deprecated
    internal_h2o_version.deprecated = True
    updated_version = internal_h2o_version_client.update_version(
        internal_h2o_version=internal_h2o_version
    )

    # Assigning alias that is not 'latest' should work even for deprecated version.
    versions = internal_h2o_version_client.assign_aliases(
        internal_h2o_version_id=updated_version.internal_h2o_version_id,
        aliases=["non-latest"]
    )
    assert versions[0].internal_h2o_version_id == "3.40.0.5"
    assert versions[0].deprecated is True
    assert versions[0].aliases == ["non-latest"]

