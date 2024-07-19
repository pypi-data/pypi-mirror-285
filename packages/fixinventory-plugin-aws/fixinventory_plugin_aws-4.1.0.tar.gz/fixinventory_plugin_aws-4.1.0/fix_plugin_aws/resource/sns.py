from datetime import timedelta
from typing import ClassVar, Dict, List, Optional, Type, Any
from attrs import define, field


from fix_plugin_aws.aws_client import AwsClient
from fix_plugin_aws.resource.base import AwsApiSpec, AwsResource, GraphBuilder
from fix_plugin_aws.resource.cloudwatch import AwsCloudwatchQuery, normalizer_factory
from fix_plugin_aws.resource.iam import AwsIamRole
from fix_plugin_aws.resource.kms import AwsKmsKey
from fix_plugin_aws.utils import ToDict
from fixlib.baseresources import EdgeType, MetricName, ModelReference
from fixlib.graph import Graph
from fixlib.json_bender import F, Bender, S, bend, ParseJson, Sorted
from fixlib.types import Json

service_name = "sns"


@define(eq=False, slots=False)
class AwsSnsTopic(AwsResource):
    kind: ClassVar[str] = "aws_sns_topic"
    kind_display: ClassVar[str] = "AWS SNS Topic"
    aws_metadata: ClassVar[Dict[str, Any]] = {"provider_link_tpl": "https://{region_id}.console.aws.amazon.com/sns/v3/home?region={region}#/topic/{arn}", "arn_tpl": "arn:{partition}:sns:{region}:{account}:{name}"}  # fmt: skip
    kind_description: ClassVar[str] = (
        "AWS SNS (Simple Notification Service) Topic is a publish-subscribe messaging"
        " service provided by Amazon Web Services. It allows applications, services,"
        " and devices to send and receive notifications via email, SMS, push"
        " notifications, and more."
    )
    api_spec: ClassVar[AwsApiSpec] = AwsApiSpec(service_name, "list-topics", "Topics")
    reference_kinds: ClassVar[ModelReference] = {
        "predecessors": {
            "delete": ["aws_kms_key"],
        },
        "successors": {"default": ["aws_kms_key"]},
    }
    mapping: ClassVar[Dict[str, Bender]] = {
        "id": S("TopicArn"),
        "name": S("DisplayName"),
        "arn": S("TopicArn"),
        "topic_subscriptions_confirmed": S("SubscriptionsConfirmed") >> F(lambda x: int(x)),
        "topic_subscriptions_deleted": S("SubscriptionsDeleted") >> F(lambda x: int(x)),
        "topic_subscriptions_pending": S("SubscriptionsPending") >> F(lambda x: int(x)),
        "topic_policy": S("Policy") >> ParseJson() >> Sorted(sort_list=True),
        "topic_delivery_policy": S("DeliveryPolicy"),
        "topic_effective_delivery_policy": S("EffectiveDeliveryPolicy"),
        "topic_owner": S("Owner"),
        "topic_kms_master_key_id": S("KmsMasterKeyId"),
        "topic_fifo_topic": S("FifoTopic") >> F(lambda x: x == "true"),
        "topic_content_based_deduplication": S("ContentBasedDeduplication") >> F(lambda x: x == "true"),
    }
    topic_subscriptions_confirmed: Optional[int] = field(default=None)
    topic_subscriptions_deleted: Optional[int] = field(default=None)
    topic_subscriptions_pending: Optional[int] = field(default=None)
    topic_policy: Optional[Json] = field(default=None)
    topic_delivery_policy: Optional[str] = field(default=None)
    topic_effective_delivery_policy: Optional[str] = field(default=None)
    topic_owner: Optional[str] = field(default=None)
    topic_kms_master_key_id: Optional[str] = field(default=None)
    topic_fifo_topic: Optional[bool] = field(default=None)
    topic_content_based_deduplication: Optional[bool] = field(default=None)

    @classmethod
    def called_collect_apis(cls) -> List[AwsApiSpec]:
        return [
            cls.api_spec,
            AwsApiSpec(service_name, "get-topic-attributes"),
            AwsApiSpec(service_name, "list-tags-for-resource"),
        ]

    @classmethod
    def collect(cls: Type[AwsResource], json: List[Json], builder: GraphBuilder) -> None:
        def add_tags(topic: AwsSnsTopic) -> None:
            tags = builder.client.list(
                service_name, "list-tags-for-resource", result_name="Tags", ResourceArn=topic.arn
            )
            if tags:
                topic.tags = bend(ToDict(), tags)

        for entry in json:
            topic = builder.client.get(
                service_name, "get-topic-attributes", TopicArn=entry["TopicArn"], result_name="Attributes"
            )
            if topic:
                if topic_instance := cls.from_api(topic, builder):
                    builder.add_node(topic_instance, topic)
                    builder.submit_work(service_name, add_tags, topic_instance)

    def collect_usage_metrics(self, builder: GraphBuilder) -> List[AwsCloudwatchQuery]:
        # Filter out metrics with the 'aws-controltower' dimension value
        if "aws-controltower" in self.safe_name:
            return []
        queries: List[AwsCloudwatchQuery] = []
        delta = builder.metrics_delta
        # SNS metrics are available at a 1-minute interval
        period = timedelta(minutes=1)
        queries.extend(
            [
                AwsCloudwatchQuery.create(
                    query_name=name,
                    namespace="AWS/SNS",
                    period=period,
                    ref_id=self.id,
                    metric_name=metric_name,
                    normalization=normalizer_factory.count_sum(),
                    stat="Sum",
                    unit="Count",
                    TopicName=self.safe_name,
                )
                for name, metric_name in [
                    ("NumberOfMessagesPublished", MetricName.NumberOfMessagesPublished),
                    ("NumberOfNotificationsDelivered", MetricName.NumberOfNotificationsDelivered),
                    ("NumberOfNotificationsFailed", MetricName.NumberOfNotificationsFailed),
                ]
            ]
        )
        queries.extend(
            [
                AwsCloudwatchQuery.create(
                    query_name="PublishSize",
                    namespace="AWS/SNS",
                    period=delta,
                    ref_id=self.id,
                    metric_name=MetricName.PublishSize,
                    normalization=normalizer_factory.bytes,
                    stat=stat,
                    unit="Bytes",
                    TopicName=self.safe_name,
                )
                for stat in ["Minimum", "Average", "Maximum"]
            ]
        )

        return queries

    def connect_in_graph(self, builder: GraphBuilder, source: Json) -> None:
        if self.topic_kms_master_key_id:
            builder.dependant_node(
                self,
                clazz=AwsKmsKey,
                id=AwsKmsKey.normalise_id(self.topic_kms_master_key_id),
            )

    def update_resource_tag(self, client: AwsClient, key: str, value: str) -> bool:
        client.call(
            aws_service=service_name,
            action="tag-resource",
            result_name=None,
            ResourceArn=self.arn,
            Tags=[{"Key": key, "Value": value}],
        )
        return True

    def delete_resource_tag(self, client: AwsClient, key: str) -> bool:
        client.call(
            aws_service=service_name, action="untag-resource", result_name=None, ResourceArn=self.arn, TagKeys=[key]
        )
        return True

    def delete_resource(self, client: AwsClient, graph: Graph) -> bool:
        client.call(aws_service=service_name, action="delete-topic", result_name=None, TopicArn=self.arn)
        return True

    @classmethod
    def called_mutator_apis(cls) -> List[AwsApiSpec]:
        return [
            AwsApiSpec(service_name, "tag-resource"),
            AwsApiSpec(service_name, "untag-resource"),
            AwsApiSpec(service_name, "delete-topic"),
        ]


@define(eq=False, slots=False)
class AwsSnsSubscription(AwsResource):
    kind: ClassVar[str] = "aws_sns_subscription"
    kind_display: ClassVar[str] = "AWS SNS Subscription"
    aws_metadata: ClassVar[Dict[str, Any]] = {"provider_link_tpl": "https://{region_id}.console.aws.amazon.com/sns/v3/home?region={region}#/topic/{arn}", "arn_tpl": "arn:{partition}:sns:{region}:{account}:{name}"}  # fmt: skip
    kind_description: ClassVar[str] = (
        "SNS Subscriptions in AWS allow applications to receive messages from topics"
        " of interest using different protocols such as HTTP, email, SMS, or Lambda"
        " function invocation."
    )
    api_spec: ClassVar[AwsApiSpec] = AwsApiSpec(service_name, "list-subscriptions", "Subscriptions")
    reference_kinds: ClassVar[ModelReference] = {
        "predecessors": {"default": ["aws_sns_topic", "aws_iam_role"], "delete": ["aws_iam_role"]},
    }
    mapping: ClassVar[Dict[str, Bender]] = {
        "id": S("SubscriptionArn"),
        "name": S("SubscriptionArn"),
        "arn": S("SubscriptionArn"),
        "subscription_confirmation_was_authenticated": S("ConfirmationWasAuthenticated") >> F(lambda x: x == "true"),
        "subscription_delivery_policy": S("DeliveryPolicy"),
        "subscription_effective_delivery_policy": S("EffectiveDeliveryPolicy"),
        "subscription_filter_policy": S("FilterPolicy"),
        "subscription_owner": S("Owner"),
        "subscription_pending_confirmation": S("PendingConfirmation") >> F(lambda x: x == "true"),
        "subscription_raw_message_delivery": S("RawMessageDelivery") >> F(lambda x: x == "true"),
        "subscription_redrive_policy": S("RedrivePolicy"),
        "subscription_topic_arn": S("TopicArn"),
        "subscription_role_arn": S("SubscriptionRoleArn"),
    }
    subscription_confirmation_was_authenticated: Optional[bool] = field(default=None)
    subscription_delivery_policy: Optional[str] = field(default=None)
    subscription_effective_delivery_policy: Optional[str] = field(default=None)
    subscription_filter_policy: Optional[str] = field(default=None)
    subscription_owner: Optional[str] = field(default=None)
    subscription_pending_confirmation: Optional[bool] = field(default=None)
    subscription_raw_message_delivery: Optional[bool] = field(default=None)
    subscription_redrive_policy: Optional[str] = field(default=None)
    subscription_topic_arn: Optional[str] = field(default=None)
    subscription_role_arn: Optional[str] = field(default=None)

    @classmethod
    def called_collect_apis(cls) -> List[AwsApiSpec]:
        return [
            cls.api_spec,
            AwsApiSpec(service_name, "get-subscription-attributes"),
        ]

    @classmethod
    def collect(cls: Type[AwsResource], json: List[Json], builder: GraphBuilder) -> None:
        def add_instance(entry: Json) -> None:
            subscription = builder.client.get(
                service_name,
                "get-subscription-attributes",
                SubscriptionArn=entry["SubscriptionArn"],
                result_name="Attributes",
                expected_errors=["InvalidParameter", "NotFound"],
            )
            if subscription:
                if subscription_instance := cls.from_api(subscription, builder):
                    builder.add_node(subscription_instance, subscription)

        for entry in json:
            builder.submit_work(service_name, add_instance, entry)

    def connect_in_graph(self, builder: GraphBuilder, source: Json) -> None:
        if self.subscription_topic_arn:
            builder.add_edge(
                self,
                reverse=True,
                clazz=AwsSnsTopic,
                arn=self.subscription_topic_arn,
            )
        if self.subscription_role_arn:
            builder.dependant_node(
                self, reverse=True, delete_same_as_default=True, clazz=AwsIamRole, arn=self.subscription_role_arn
            )

    def delete_resource(self, client: AwsClient, graph: Graph) -> bool:
        client.call(aws_service=service_name, action="unsubscribe", result_name=None, SubscriptionArn=self.arn)
        return True

    @classmethod
    def called_mutator_apis(cls) -> List[AwsApiSpec]:
        return [AwsApiSpec(service_name, "unsubscribe")]


@define(eq=False, slots=False)
class AwsSnsEndpoint(AwsResource):
    # collection of endpoint resources happens in AwsSnsPlatformApplication.collect()
    kind: ClassVar[str] = "aws_sns_endpoint"
    aws_metadata: ClassVar[Dict[str, Any]] = {"arn_tpl": "arn:{partition}:sns:{region}:{account}:endpoint/{id}"}  # fmt: skip
    kind_display: ClassVar[str] = "AWS SNS Endpoint"
    kind_description: ClassVar[str] = (
        "An endpoint in the AWS Simple Notification Service (SNS), which is used to"
        " send push notifications or SMS messages to mobile devices or other"
        " applications."
    )
    mapping: ClassVar[Dict[str, Bender]] = {
        "id": S("Arn"),
        "arn": S("Arn"),
        "endpoint_enabled": S("Enabled") >> F(lambda x: x == "true"),
        "endpoint_token": S("Token"),
    }
    endpoint_enabled: Optional[bool] = field(default=None)
    endpoint_token: Optional[str] = field(default=None)

    def delete_resource(self, client: AwsClient, graph: Graph) -> bool:
        client.call(aws_service=service_name, action="delete-endpoint", result_name=None, EndpointArn=self.arn)
        return True

    @classmethod
    def called_mutator_apis(cls) -> List[AwsApiSpec]:
        return [AwsApiSpec(service_name, "delete-endpoint")]

    @classmethod
    def service_name(cls) -> str:
        return service_name


@define(eq=False, slots=False)
class AwsSnsPlatformApplication(AwsResource):
    kind: ClassVar[str] = "aws_sns_platform_application"
    kind_display: ClassVar[str] = "AWS SNS Platform Application"
    aws_metadata: ClassVar[Dict[str, Any]] = {"arn_tpl": "arn:{partition}:sns:{region}:{account}:platform-application/{name}"}  # fmt: skip
    kind_description: ClassVar[str] = (
        "AWS SNS Platform Application is a service that allows you to create a"
        " platform application and register it with Amazon SNS so that your"
        " application can receive push notifications."
    )
    api_spec: ClassVar[AwsApiSpec] = AwsApiSpec(
        service_name, "list-platform-applications", "PlatformApplications", expected_errors=["InvalidAction"]
    )
    reference_kinds: ClassVar[ModelReference] = {
        "successors": {
            "default": ["aws_sns_topic", "aws_sns_endpoint"],
        },
    }
    mapping: ClassVar[Dict[str, Bender]] = {
        "id": S("Arn"),
        "arn": S("Arn"),
        "application_apple_certificate_expiry_date": S("AppleCertificateExpiryDate"),
        "application_apple_platform_team_id": S("ApplePlatformTeamID"),
        "application_apple_platform_bundle_id": S("ApplePlatformBundleID"),
        "application_event_endpoint_created": S("EventEndpointCreated"),
        "application_event_endpoint_deleted": S("EventEndpointDeleted"),
        "application_event_endpoint_updated": S("EventEndpointUpdated"),
        "application_event_endpoint_failure": S("EventDeliveryFailure"),
    }
    application_apple_certificate_expiry_date: Optional[str] = field(default=None)
    application_apple_platform_team_id: Optional[str] = field(default=None)
    application_apple_platform_bundle_id: Optional[str] = field(default=None)
    application_event_endpoint_created: Optional[str] = field(default=None)
    application_event_endpoint_deleted: Optional[str] = field(default=None)
    application_event_endpoint_updated: Optional[str] = field(default=None)
    application_event_endpoint_failure: Optional[str] = field(default=None)

    @classmethod
    def called_collect_apis(cls) -> List[AwsApiSpec]:
        return [
            cls.api_spec,
            AwsApiSpec(service_name, "get-platform-application-attributes"),
            AwsApiSpec(service_name, "list-endpoints-by-platform-application"),
        ]

    @classmethod
    def collect(cls: Type[AwsResource], json: List[Json], builder: GraphBuilder) -> None:
        def add_instance(entry: Json) -> None:
            app_arn = entry["PlatformApplicationArn"]
            app = builder.client.get(
                service_name,
                "get-platform-application-attributes",
                PlatformApplicationArn=app_arn,
                result_name="Attributes",
            )
            if app:
                app["Arn"] = app_arn
                if app_instance := cls.from_api(app, builder):
                    builder.add_node(app_instance, app)

                    endpoints = builder.client.list(
                        service_name,
                        "list-endpoints-by-platform-application",
                        PlatformApplicationArn=app_arn,
                        result_name="Endpoints",
                    )
                    for endpoint in endpoints:
                        attributes = endpoint["Attributes"]
                        attributes["Arn"] = endpoint["EndpointArn"]
                        if endpoint_instance := AwsSnsEndpoint.from_api(attributes, builder):
                            builder.add_node(endpoint_instance, attributes)
                            builder.add_edge(app_instance, edge_type=EdgeType.default, node=endpoint_instance)

        for entry in json:
            builder.submit_work(service_name, add_instance, entry)

    def connect_in_graph(self, builder: GraphBuilder, source: Json) -> None:
        for topic in [
            self.application_event_endpoint_created,
            self.application_event_endpoint_deleted,
            self.application_event_endpoint_updated,
            self.application_event_endpoint_failure,
        ]:
            builder.add_edge(self, edge_type=EdgeType.default, clazz=AwsSnsTopic, arn=topic)

    def delete_resource(self, client: AwsClient, graph: Graph) -> bool:
        client.call(
            aws_service=service_name,
            action="delete-platform-application",
            result_name=None,
            PlatformApplicationArn=self.arn,
        )
        return True

    @classmethod
    def called_mutator_apis(cls) -> List[AwsApiSpec]:
        return [AwsApiSpec(service_name, "delete-platform-application")]


resources: List[Type[AwsResource]] = [AwsSnsTopic, AwsSnsSubscription, AwsSnsPlatformApplication, AwsSnsEndpoint]
