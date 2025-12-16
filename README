# Engagement Streaming Pipeline

## Overview

This project demonstrates a real-time streaming pipeline for **user engagement events**. It integrates:

1. **PostgreSQL** as the source database.
2. **Debezium** for CDC (Change Data Capture) from PostgreSQL to **Kafka**.
3. **Apache Kafka** as the streaming message bus.
4. **Apache Flink** for real-time processing and enrichment of engagement events.
5. **Redis** as the storage for enriched, fast-access data.

The pipeline flow:

```
PostgreSQL (engagement_events table)
          │
          ▼
   Debezium CDC connector
          │
          ▼
        Kafka topic
          │
          ▼
      Flink job (Python)
          │
          ▼
        Redis (enriched events)
```

---

## Architecture

* **PostgreSQL**: stores content and engagement events.
* **Debezium**: monitors the `engagement_events` table and publishes changes to Kafka.
* **Kafka**: serves as a durable, real-time message broker.
* **Flink**: consumes Kafka messages, computes engagement metrics, and writes to Redis.
* **Redis**: stores enriched engagement metrics for fast retrieval.

---

## Project Structure

```
flink_project/
│
├─ docker-compose.yml         # Defines PostgreSQL, Kafka, Zookeeper, Flink, Redis, Debezium services
├─ streaming_job.py           # Flink Python job
├─ sql/
│   ├─ create_tables.sql      # PostgreSQL schema
│   └─ insert_sample.sql      # Sample inserts
├─ README.md
└─ jars/
    └─ flink-connector-kafka_2.12-1.18.1.jar
```

---

## Setup

1. **Install prerequisites**:

   * Docker & Docker Compose
   * Python 3.10+ with PyFlink
   * Redis CLI (optional, for testing)

2. **Build Docker environment**:

```bash
docker compose up -d
```

This will start:

* PostgreSQL
* Kafka + Zookeeper
* Flink JobManager & TaskManager
* Redis
* Debezium connector

---

## PostgreSQL Schema

**Create `content` and `engagement_events` tables:**

```sql
-- content table
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content_type TEXT CHECK (content_type IN ('podcast','newsletter','video')),
    length_seconds INTEGER,
    publish_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- engagement_events table
CREATE TABLE engagement_events (
    id BIGSERIAL PRIMARY KEY,
    content_id UUID REFERENCES content(id),
    user_id UUID,
    event_type TEXT CHECK (event_type IN ('play','pause','finish','click')),
    event_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER,
    device TEXT,
    raw_payload JSONB,
    processed_at TIMESTAMPTZ
);
```

Insert sample content:

```sql
INSERT INTO content (slug, title, content_type, length_seconds)
VALUES ('video-1', 'My First Video', 'video', 300)
RETURNING id;
```

Insert sample engagement events:

```sql
INSERT INTO engagement_events (content_id, user_id, event_type, duration_ms, device, raw_payload)
VALUES ('<content_id_from_previous>', gen_random_uuid(), 'play', 45000, 'web-chrome', '{"source":"manual_test"}');
```

> **Note:** Always use valid UUIDs for `content_id` and `user_id`.

---

## Flink Streaming Job

`streaming_job.py` is the Python Flink job that:

1. Reads messages from Kafka topic `pg_engagement.public.engagement_events`.
2. Parses JSON and computes:

   * `engagement_seconds`
   * `engagement_pct`
3. Writes enriched payloads to Redis with keys: `<content_id>:<user_id>`.

Example snippet:

```python
key = f"{payload.get('content_id')}:{payload.get('user_id')}"
r.set(key, json.dumps(payload))
```

---

## Running the Flink Job

```bash
docker exec -it peoject_tranning-flink-jobmanager-1 bash
python3 /opt/flink/streaming_job.py
```

* The job continuously consumes messages from Kafka.
* Writes enriched events into Redis.

---

## Testing / Debugging

1. **Check Kafka messages:**

```bash
docker exec -it peoject_tranning-kafka-1 kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic pg_engagement.public.engagement_events \
  --from-beginning
```

2. **Check Redis data:**

```bash
docker exec -it peoject_tranning-redis-1 redis-cli
127.0.0.1:6379> KEYS "*"
127.0.0.1:6379> GET "<content_id>:<user_id>"
```

3. **Check Flink logs**:

```bash
docker logs -f peoject_tranning-flink-jobmanager-1
docker logs -f peoject_tranning-flink-taskmanager-1
```

---

## Notes

* Redis connections are handled per Flink task via `RichMapFunction.open()`.
* Kafka offsets are initialized to `earliest` to process all historical events.
* Ensure UUID values are valid when inserting into PostgreSQL to avoid errors.

---

## References

* [Debezium PostgreSQL Connector](https://debezium.io/documentation/reference/connectors/postgresql.html)
* [Apache Flink Python API](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/python/overview/)
* [Redis Python Client](https://pypi.org/project/redis/)
