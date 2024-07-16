CREATE TABLE IF NOT EXISTS search  (
    id SERIAL PRIMARY KEY,
	uid INTEGER UNIQUE NOT NULL,
    meta JSONB,
    label VARCHAR(255) UNIQUE,
    client_domain VARCHAR(255),
    inclusion JSONB DEFAULT '{}'::jsonb,
    exclusion JSONB DEFAULT '{}'::jsonb,
    sort JSONB DEFAULT '{}'::jsonb,
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    uid INTEGER UNIQUE,
    domain VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    description TEXT,
    source VARCHAR(255),
    meta JSONB DEFAULT '{}'::jsonb, 
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE TABLE IF NOT EXISTS actor (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW())),
    updated BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

-- wait this probably alreaady exists
-- CREATE INDEX idx_actor_key ON actor(key);


CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    search_uid INTEGER REFERENCES search(uid),
    domain VARCHAR(255) REFERENCES company(domain),
    actor_key VARCHAR(255) NOT NULL REFERENCES actor(key),
    type VARCHAR(255) NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE INDEX idx_event_actor_key ON event(actor_key);
CREATE INDEX idx_event_search_uid ON event(search_uid);
-- ALTER TABLE event ADD CONSTRAINT unique_event_type_domain_search_uid_created UNIQUE (type, domain, search_uid, created); # 240523-alter.sql


-- Pretty sure I am no longer using this? 
CREATE TABLE IF NOT EXISTS checkpoint (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
    created BIGINT NOT NULL DEFAULT FLOOR(EXTRACT(EPOCH FROM NOW()))
);

CREATE MATERIALIZED VIEW IF NOT EXISTS rating AS
WITH RankedRatings AS (
    SELECT *,
           ROW_NUMBER() OVER(PARTITION BY search_uid, domain ORDER BY created DESC) AS rr
    FROM event
    WHERE 
        type = 'rating'       
)
SELECT 
	r.rr,
    r.search_uid, 
    r.domain,
    (r.data->>'rating') AS rating
FROM RankedRatings r
WHERE 
    rr = 1
;

CREATE INDEX idx_rating_search_uid_domain ON rating(search_uid, domain);


CREATE MATERIALIZED VIEW IF NOT EXISTS comment AS
SELECT 
    e.search_uid, 
    e.domain,
    to_jsonb(ARRAY_AGG(jsonb_build_object(
        'id', e.id,
        'actor_key', e.actor_key,
        'created', e.created,
        'author', a.name,
        'comment', e.data->>'comment',
        'data', e.data
    ))) AS comments
FROM event e
LEFT JOIN actor a ON e.actor_key = a.key
WHERE 
    e.type = 'comment'
GROUP BY e.search_uid, e.domain;

CREATE INDEX idx_comment_search_uid_domain ON comment(search_uid, domain);


