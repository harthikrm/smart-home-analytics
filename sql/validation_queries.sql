-- ============================================================================
-- Smart Home Analytics: Validation Queries
-- Compatible with PostgreSQL / SQLite
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. Churn rate by firmware version
--    Groups households by firmware_version and computes the proportion that
--    churned, ordered from highest to lowest churn rate.
-- ----------------------------------------------------------------------------
SELECT
    firmware_version,
    COUNT(*)                                          AS total_households,
    SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END)    AS churned_count,
    ROUND(
        SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) * 1.0
        / COUNT(*), 4
    )                                                 AS churn_rate
FROM households
GROUP BY firmware_version
ORDER BY churn_rate DESC;


-- ----------------------------------------------------------------------------
-- 2. Average connection drops by plan type
--    Joins households with network_events and reports the mean number of
--    connection drops for each plan tier.
-- ----------------------------------------------------------------------------
SELECT
    h.plan_type,
    COUNT(DISTINCT h.household_id)   AS household_count,
    ROUND(AVG(ne.connection_drops), 2) AS avg_connection_drops
FROM households h
JOIN network_events ne
    ON h.household_id = ne.household_id
GROUP BY h.plan_type
ORDER BY avg_connection_drops DESC;


-- ----------------------------------------------------------------------------
-- 3. Top 10 households by support ticket volume
--    Sums all support tickets raised per household and returns the ten
--    most frequent ticket-raisers.
-- ----------------------------------------------------------------------------
SELECT
    household_id,
    SUM(support_ticket_raised) AS total_tickets
FROM user_sessions
GROUP BY household_id
ORDER BY total_tickets DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- 4. Monthly trend of average latency by region
--    Joins households with network_events, extracts the month from each
--    event date, and computes mean latency per region per month.
-- ----------------------------------------------------------------------------
SELECT
    h.region,
    CAST(strftime('%m', ne.date) AS INTEGER) AS month,
    ROUND(AVG(ne.avg_latency_ms), 2)        AS avg_latency_ms
FROM households h
JOIN network_events ne
    ON h.household_id = ne.household_id
GROUP BY h.region, month
ORDER BY h.region, month;


-- ----------------------------------------------------------------------------
-- 5. Feature adoption rate by plan type
--    Counts the average number of distinct features used per household
--    within each plan type.
-- ----------------------------------------------------------------------------
SELECT
    h.plan_type,
    COUNT(DISTINCT h.household_id)  AS household_count,
    COUNT(DISTINCT us.feature_used) AS distinct_features_total,
    ROUND(
        COUNT(DISTINCT us.household_id || '|' || us.feature_used) * 1.0
        / COUNT(DISTINCT h.household_id), 2
    )                               AS avg_features_per_household
FROM households h
JOIN user_sessions us
    ON h.household_id = us.household_id
GROUP BY h.plan_type
ORDER BY avg_features_per_household DESC;


-- ----------------------------------------------------------------------------
-- 6. Households flagged as anomalies with their churn outcome
--    Uses a CTE to compute per-household averages of connection drops and
--    latency, then flags any household whose values exceed 2 standard
--    deviations above the global mean as an anomaly.
-- ----------------------------------------------------------------------------
WITH household_stats AS (
    SELECT
        ne.household_id,
        AVG(ne.connection_drops)  AS avg_drops,
        AVG(ne.avg_latency_ms)    AS avg_latency
    FROM network_events ne
    GROUP BY ne.household_id
),
global_stats AS (
    SELECT
        AVG(avg_drops)                        AS mean_drops,
        AVG(avg_drops * avg_drops)
            - AVG(avg_drops) * AVG(avg_drops) AS var_drops,
        AVG(avg_latency)                      AS mean_latency,
        AVG(avg_latency * avg_latency)
            - AVG(avg_latency) * AVG(avg_latency) AS var_latency
    FROM household_stats
)
SELECT
    hs.household_id,
    ROUND(hs.avg_drops, 2)   AS avg_drops,
    ROUND(hs.avg_latency, 2) AS avg_latency,
    h.churned,
    CASE
        WHEN hs.avg_drops   > gs.mean_drops   + 2 * SQRT(gs.var_drops)
          OR hs.avg_latency > gs.mean_latency + 2 * SQRT(gs.var_latency)
        THEN 1
        ELSE 0
    END AS is_anomaly
FROM household_stats hs
CROSS JOIN global_stats gs
JOIN households h
    ON hs.household_id = h.household_id
WHERE hs.avg_drops   > gs.mean_drops   + 2 * SQRT(gs.var_drops)
   OR hs.avg_latency > gs.mean_latency + 2 * SQRT(gs.var_latency)
ORDER BY hs.avg_drops DESC;


-- ----------------------------------------------------------------------------
-- 7. A/B test pre/post drop comparison per household
--    For each firmware update record, computes the average pre-update and
--    post-update drops and the percentage change.
-- ----------------------------------------------------------------------------
SELECT
    household_id,
    old_firmware,
    new_firmware,
    update_date,
    update_success,
    pre_update_drops_7day,
    post_update_drops_7day,
    ROUND(
        (post_update_drops_7day - pre_update_drops_7day) * 100.0
        / NULLIF(pre_update_drops_7day, 0), 2
    ) AS pct_change_drops
FROM firmware_updates
ORDER BY pct_change_drops DESC;


-- ----------------------------------------------------------------------------
-- 8. 30-day rolling churn risk score per household
--    Uses window functions to compute a 30-day rolling average of connection
--    drops and combines it with a rolling support ticket count to produce a
--    simple composite risk score (higher = riskier).
-- ----------------------------------------------------------------------------
WITH daily_metrics AS (
    SELECT
        ne.household_id,
        ne.date,
        ne.connection_drops,
        COALESCE(SUM(us.support_ticket_raised), 0) AS daily_tickets
    FROM network_events ne
    LEFT JOIN user_sessions us
        ON ne.household_id = us.household_id
       AND ne.date = us.date
    GROUP BY ne.household_id, ne.date, ne.connection_drops
),
rolling AS (
    SELECT
        household_id,
        date,
        connection_drops,
        daily_tickets,
        AVG(connection_drops) OVER (
            PARTITION BY household_id
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_drops_30d,
        SUM(daily_tickets) OVER (
            PARTITION BY household_id
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_tickets_30d
    FROM daily_metrics
)
SELECT
    household_id,
    date,
    ROUND(rolling_avg_drops_30d, 2)  AS rolling_avg_drops_30d,
    rolling_tickets_30d,
    ROUND(
        rolling_avg_drops_30d * 0.6 + rolling_tickets_30d * 0.4,
        2
    ) AS churn_risk_score
FROM rolling
ORDER BY household_id, date;
