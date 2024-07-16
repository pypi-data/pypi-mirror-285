ALTER TABLE event DROP CONSTRAINT unique_event_type_domain_search_uid_created;
ALTER TABLE event ALTER COLUMN search_uid DROP NOT NULL;
