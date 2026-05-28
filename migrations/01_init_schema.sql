-- Create an ingestion table to act as our staging area
CREATE TABLE IF NOT EXISTS raw_clickstream (
    id SERIAL PRIMARY KEY,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    raw_payload JSONB NOT NULL
);

-- Create optimized performance indexes on the JSONB column
-- GIN (Generalized Inverted Index) allows lightning-fast searches inside the JSON keys
CREATE INDEX idx_raw_payload_gin ON raw_clickstream USING GIN (raw_payload);

-- Create a specific B-Tree index on a deeply nested JSON attribute (e.g., event_type)
-- This speeds up specific filtering for analytics queries
CREATE INDEX idx_raw_payload_event_type ON raw_clickstream ((raw_payload->>'event_type'));