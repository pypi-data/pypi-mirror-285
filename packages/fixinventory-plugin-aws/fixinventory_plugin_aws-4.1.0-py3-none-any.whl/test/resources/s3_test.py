from fixlib.graph import Graph
from test.resources import round_trip_for
from types import SimpleNamespace
from typing import cast, Any, Callable
from fix_plugin_aws.aws_client import AwsClient
from fix_plugin_aws.resource.s3 import AwsS3Bucket, AwsS3AccountSettings


def test_buckets() -> None:
    first, builder = round_trip_for(AwsS3Bucket)
    assert len(builder.resources_of(AwsS3Bucket)) == 4
    assert len(first.bucket_encryption_rules or []) == 1
    assert first.arn == "arn:aws:s3:::bucket-1"
    assert len(first.tags) == 1


def test_name_from_path() -> None:
    assert AwsS3Bucket.name_from_path("S3://mybucket/puppy.jpg") == "mybucket"
    assert AwsS3Bucket.name_from_path("https://s3.region-code.amazonaws.com/bucket-name/key-name") == "bucket-name"
    assert AwsS3Bucket.name_from_path("https://some-bucket.s3.region-code.amazonaws.com/key-name") == "some-bucket"


def test_s3_account_settings() -> None:
    round_trip_for(AwsS3AccountSettings)


def test_tagging() -> None:
    bucket, _ = round_trip_for(AwsS3Bucket)

    def validate_update_args(**kwargs: Any) -> Any:
        if kwargs["action"] == "get-bucket-tagging":
            assert kwargs["Bucket"] == bucket.name
            return [{"Key": "foo", "Value": "bar"}]

        if kwargs["action"] == "put-bucket-tagging":
            assert kwargs["Bucket"] == bucket.name
            assert kwargs["Tagging"] == {"TagSet": [{"Key": "foo", "Value": "bar"}]}

    def validate_delete_args(**kwargs: Any) -> Any:
        if kwargs["action"] == "get-bucket-tagging":
            assert kwargs["Bucket"] == bucket.name
            return [{"Key": "foo", "Value": "bar"}]

        if kwargs["action"] == "put-bucket-tagging":
            assert kwargs["Bucket"] == bucket.name
            assert kwargs["Tagging"] == {"TagSet": []}

    client = cast(AwsClient, SimpleNamespace(list=validate_update_args, call=validate_update_args))
    bucket.update_resource_tag(client, "foo", "bar")

    client = cast(AwsClient, SimpleNamespace(list=validate_delete_args, call=validate_delete_args))
    bucket.delete_resource_tag(client, "foo")


def test_deletion() -> None:
    bucket, _ = round_trip_for(AwsS3Bucket)

    def validate_delete_args(aws_service: str, fn: Callable[[Any], None]) -> Any:
        assert aws_service == "s3"

    client = cast(AwsClient, SimpleNamespace(with_resource=validate_delete_args))
    bucket.delete_resource(client, Graph())


# TODO: fix 'RuntimeError: cannot schedule new futures after shutdown'
# def test_s3_usage_metrics(account_collector: AwsAccountCollector) -> None:
#     bucket, builder = round_trip_for(AwsS3Bucket)
#     builder.all_regions.update({"us-east-1": AwsRegion(id="us-east-1", name="us-east-1")})
#     account_collector.collect_usage_metrics(builder)
#     bucket.complete_graph(builder, {})
#     assert bucket._resource_usage["standard_storage_bucket_size_bytes"]["avg"] == 1.0
#     assert bucket._resource_usage["intelligent_tiering_storage_bucket_size_bytes"]["avg"] == 2.0
#     assert bucket._resource_usage["standard_ia_storage_bucket_size_bytes"]["avg"] == 3.0
#     # This values is computed internally using the other values. If the number does not match, the logic is broken!
#     assert bucket._resource_usage["bucket_size_bytes"]["avg"] == 6.0
