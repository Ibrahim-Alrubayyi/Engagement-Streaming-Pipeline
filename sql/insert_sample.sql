INSERT INTO
    content (slug, title, content_type, length_seconds)
VALUES
    ('podcast-001', 'Learning Kafka', 'podcast', 300),
    ('video-001', 'Flink Basics', 'video', 600);

INSERT INTO
    engagement_events (
        content_id,
        user_id,
        event_type,
        event_ts,
        duration_ms,
        device,
        raw_payload
    )
VALUES
    (
        (
            SELECT
                id
            FROM
                content
            WHERE
                slug = 'podcast-001'
        ),
        gen_random_uuid(),
        'play',
        now(),
        45000,
        'web-chrome',
        '{"source":"manual_test"}'
    ),
    (
        (
            SELECT
                id
            FROM
                content
            WHERE
                slug = 'video-001'
        ),
        gen_random_uuid(),
        'play',
        now(),
        60000,
        'mobile-ios',
        '{"source":"manual_test"}'
    );