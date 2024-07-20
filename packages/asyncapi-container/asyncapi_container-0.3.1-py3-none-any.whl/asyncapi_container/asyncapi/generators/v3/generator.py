import json
from collections import defaultdict

from attr import define

from asyncapi_container.asyncapi.generators.base import AsyncAPISpecGenerator
from asyncapi_container.asyncapi.spec.v3.root import AsyncAPIV3Root
from asyncapi_container.containers.v3.simple_spec import SimpleSpecV3


@define
class AsyncAPISpecV3Generator(AsyncAPISpecGenerator):
    asyncapi_spec_container: SimpleSpecV3

    def parse_spec_container(self) -> AsyncAPIV3Root:
        channels = defaultdict(dict)
        operations = defaultdict(dict)
        components = defaultdict(dict)
        components["messages"] = defaultdict(dict)
        components["schemas"] = defaultdict()
        messages = components["messages"]
        schemas = components["schemas"]

        for topic, topic_schemas in self.asyncapi_spec_container.sends.items():
            action_name = f"send: {topic}"
            channel_name = f"send: {topic}"

            channels[channel_name]["address"] = topic
            if "messages" not in channels[channel_name].keys():
                channels[channel_name]["messages"] = {}

            send_operation_messages = []
            for topic_schema in topic_schemas:
                schema_name = topic_schema.__name__
                message_name = topic_schema.__name__

                json_schema: str = topic_schema.schema_json()
                json_schema = json_schema.replace(
                    "#/definitions", f"#/components/schemas/{schema_name}/definitions"
                )
                schemas[schema_name] = json.loads(json_schema)
                messages[message_name] = {
                    "payload": {"$ref": f"#/components/schemas/{schema_name}"}
                }

                message_ref = {"$ref": f"#/components/messages/{message_name}"}
                send_operation_messages.append(message_ref)
                send_operation_messages.append(message_ref)
                channels[channel_name]["messages"][message_name] = message_ref

            operations[action_name] = {
                "action": "send",
                "channel": {"$ref": f"#/channels/{channel_name}"},
            }

        for topic, topic_schemas in self.asyncapi_spec_container.receives.items():
            action_name = f"receive: {topic}"
            channel_name = f"receive: {topic}"

            channels[channel_name]["address"] = topic
            if "messages" not in channels[channel_name].keys():
                channels[channel_name]["messages"] = {}

            send_operation_messages = []
            for topic_schema in topic_schemas:
                schema_name = topic_schema.__name__
                message_name = topic_schema.__name__

                json_schema: str = topic_schema.schema_json()
                json_schema = json_schema.replace(
                    "#/definitions", f"#/components/schemas/{schema_name}/definitions"
                )
                schemas[schema_name] = json.loads(json_schema)
                messages[message_name] = {
                    "payload": {"$ref": f"#/components/schemas/{schema_name}"}
                }
                message_ref = {"$ref": f"#/components/messages/{message_name}"}
                send_operation_messages.append(message_ref)
                channels[channel_name]["messages"][message_name] = message_ref

            operations[action_name] = {
                "action": "receive",
                "channel": {"$ref": f"#/channels/{channel_name}"},
            }

        return AsyncAPIV3Root(
            info=self.asyncapi_spec_container.info.dict(),
            channels=channels,
            components=components,
            operations=operations,
        )

    def as_dict(self) -> dict:
        asyncapi_spec_v3_root = self.parse_spec_container()

        return asyncapi_spec_v3_root.dict()

    def as_json(self):
        asyncapi_spec_v3_root = self.parse_spec_container()

        return asyncapi_spec_v3_root.json()
