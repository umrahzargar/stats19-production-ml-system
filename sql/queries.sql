-- STATS19 Prediction Database - Example Analytical Queries

-- 1. View the most recent predictions
SELECT
    p.prediction_id,
    p.created_at,
    p.severe_probability,
    p.predicted_class,
    m.model_name,
    m.version
FROM prediction_logs AS p
JOIN model_versions AS m
    ON p.model_version_id = m.model_version_id
ORDER BY p.created_at DESC
LIMIT 20;


-- 2. Count all predictions
SELECT
    COUNT(*) AS total_predictions
FROM prediction_logs;


-- 3. Count predictions by predicted class
SELECT
    predicted_class,
    COUNT(*) AS prediction_count
FROM prediction_logs
GROUP BY predicted_class
ORDER BY predicted_class;


-- 4. Average predicted severe probability
SELECT
    AVG(severe_probability) AS average_severe_probability
FROM prediction_logs;


-- 5. Highest-risk predictions
SELECT
    prediction_id,
    created_at,
    severe_probability,
    predicted_class
FROM prediction_logs
ORDER BY severe_probability DESC
LIMIT 10;


-- 6. Predictions by model version
SELECT
    m.model_name,
    m.version,
    COUNT(*) AS prediction_count,
    AVG(p.severe_probability) AS average_severe_probability
FROM prediction_logs AS p
JOIN model_versions AS m
    ON p.model_version_id = m.model_version_id
GROUP BY
    m.model_name,
    m.version
ORDER BY prediction_count DESC;


-- 7. Extract a feature stored inside the JSONB input
SELECT
    prediction_id,
    input_data ->> 'age_of_casualty' AS age_of_casualty,
    input_data ->> 'speed_limit' AS speed_limit,
    severe_probability
FROM prediction_logs
ORDER BY prediction_id DESC;