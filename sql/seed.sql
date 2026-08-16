INSERT INTO model_versions (
    model_name,
    version,
    threshold,
    macro_f1,
    severe_recall,
    severe_precision,
    roc_auc,
    average_precision,
    is_active
)
VALUES (
    'XGBoost',
    '1.0.0',
    0.5,
    0.619,
    0.649,
    0.361,
    0.739,
    0.43,
    TRUE
)
ON CONFLICT (version) DO NOTHING;