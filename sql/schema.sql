  
-- STATS19 Production Application Database Schema
 
-- Model versions
-- Stores information about models that can produce predictions.
 

CREATE TABLE IF NOT EXISTS model_versions (
    model_version_id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL UNIQUE,
    threshold DOUBLE PRECISION NOT NULL,
    macro_f1 DOUBLE PRECISION,
    severe_recall DOUBLE PRECISION,
    severe_precision DOUBLE PRECISION,
    roc_auc DOUBLE PRECISION,
    average_precision DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Prediction Batches
-- It stores information about the batch itself.

CREATE TABLE IF NOT EXISTS prediction_batches (
    batch_id BIGSERIAL PRIMARY KEY,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    source_filename TEXT,

    row_count INTEGER NOT NULL,

    model_version_id BIGINT NOT NULL,

    CONSTRAINT fk_batch_model
        FOREIGN KEY (model_version_id)
        REFERENCES model_versions(model_version_id)
);
 
-- Prediction logs
-- Stores every prediction made through the API.
 

CREATE TABLE IF NOT EXISTS prediction_logs (
    prediction_id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    input_data JSONB NOT NULL,
    severe_probability DOUBLE PRECISION NOT NULL,
    predicted_class SMALLINT NOT NULL,
    api_version TEXT NOT NULL,
    batch_id BIGINT,
    model_version_id BIGINT NOT NULL,

    CONSTRAINT fk_prediction_model
        FOREIGN KEY (model_version_id)
        REFERENCES model_versions(model_version_id),
    CONSTRAINT fk_prediction_batch
    FOREIGN KEY (batch_id)
    REFERENCES prediction_batches(batch_id)
);


 
-- Indexes
 

CREATE INDEX IF NOT EXISTS idx_prediction_logs_created_at
ON prediction_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_prediction_logs_model_version
ON prediction_logs (model_version_id);

CREATE INDEX IF NOT EXISTS idx_prediction_logs_batch_id
ON prediction_logs (batch_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_model
ON model_versions (is_active)
WHERE is_active = TRUE;