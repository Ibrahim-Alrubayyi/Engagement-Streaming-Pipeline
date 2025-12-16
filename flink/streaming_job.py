from pyflink.datastream import StreamExecutionEnvironment, MapFunction, RuntimeContext
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import WatermarkStrategy

import json
import redis


class EnrichAndWriteToRedis(MapFunction):

    def open(self, runtime_context: RuntimeContext):
        # Redis connection per task
        self.r = redis.Redis(host='peoject_tranning-redis-1', port=6379, db=0)

    def map(self, value):
        try:
            msg = json.loads(value)
            payload = msg.get("payload", msg)

            duration_ms = payload.get("duration_ms")
            length_seconds = payload.get("length_seconds", 60)

            engagement_seconds = round(
                duration_ms / 1000, 2) if duration_ms else None
            engagement_pct = round(
                engagement_seconds / length_seconds, 2) if engagement_seconds else None

            payload["engagement_seconds"] = engagement_seconds
            payload["engagement_pct"] = engagement_pct

            key = f"{payload.get('content_id')}:{payload.get('user_id')}"
            self.r.set(key, json.dumps(payload))

            return json.dumps(payload)

        except Exception as e:
            print("Error in map:", e)
            return None


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(10_000)

    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:9092") \
        .set_topics("pg_engagement.public.engagement_events") \
        .set_group_id("flink-engagement") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    stream = env.from_source(
        kafka_source,
        WatermarkStrategy.no_watermarks(),
        "Kafka Engagement Source"
    )

    enriched = stream.map(EnrichAndWriteToRedis(), output_type=Types.STRING())

    # Also print to logs for debugging
    enriched.print()

    env.execute("Engagement Streaming Job")


if __name__ == "__main__":
    main()
