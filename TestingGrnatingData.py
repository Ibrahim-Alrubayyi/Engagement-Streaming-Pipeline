import psycopg2, uuid, random, json
from datetime import datetime, timedelta

conn = psycopg2.connect(
    dbname="engagement_db", user="admin", password="secret", host="localhost"
)
cur = conn.cursor()

# Insert sample content
content_types = ['podcast', 'newsletter', 'video']
for i in range(5):
    cur.execute(
        "INSERT INTO content (slug, title, content_type, length_seconds) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        (f"content-{i}", f"Title {i}", random.choice(content_types), random.randint(60, 3600))
    )

conn.commit()

# Fetch content IDs
cur.execute("SELECT id FROM content")
content_ids = [row[0] for row in cur.fetchall()]

# Insert random engagement events
devices = ['ios', 'web-safari', 'android']
event_types = ['play', 'pause', 'finish', 'click']

for _ in range(20):
    cur.execute(
        "INSERT INTO engagement_events (content_id, user_id, event_type, event_ts, duration_ms, device, raw_payload) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (
            random.choice(content_ids),
            str(uuid.uuid4()),
            random.choice(event_types),
            datetime.now() - timedelta(minutes=random.randint(0, 60)),
            random.randint(1000, 60000),
            random.choice(devices),
            json.dumps({"extra": "data"})
        )
    )

conn.commit()
cur.close()
conn.close()
print("Sample data inserted ✅")
