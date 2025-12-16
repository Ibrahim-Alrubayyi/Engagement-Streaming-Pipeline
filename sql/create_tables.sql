-- Table: content
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content_type TEXT CHECK (
        content_type IN ('podcast', 'newsletter', 'video')
    ),
    length_seconds INTEGER,
    publish_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: engagement_events
CREATE TABLE engagement_events (
    id BIGSERIAL PRIMARY KEY,
    content_id UUID REFERENCES content(id),
    user_id UUID,
    event_type TEXT CHECK (
        event_type IN ('play', 'pause', 'finish', 'click')
    ),
    event_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER,
    device TEXT,
    raw_payload JSONB,
    processed_at TIMESTAMPTZ
);

-- Index for fast CDC read
CREATE INDEX idx_engagement_event_ts ON engagement_events(event_ts);