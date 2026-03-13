"""
Smart Home Network Analytics — Data Simulation
Generates 4 CSV files mimicking eero smart home router telemetry data.
Designed with realistic noise so models produce non-trivial results.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

N_HOUSEHOLDS = 5000
OBSERVATION_DAYS = 180
START_DATE = datetime(2024, 1, 1)


def generate_households():
    print("[1/4] Generating households.csv ...")

    device_models = ["eero 6", "eero 6+", "eero Pro 6E", "eero Max"]
    firmware_versions = ["6.1.0", "6.2.0", "6.3.0", "6.4.0", "6.4.2", "6.5.0"]
    plan_types = ["Basic", "eero Plus", "eero Secure+"]
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]

    models = np.random.choice(device_models, N_HOUSEHOLDS, p=[0.30, 0.30, 0.25, 0.15])
    firmwares = np.random.choice(firmware_versions, N_HOUSEHOLDS,
                                  p=[0.08, 0.12, 0.18, 0.22, 0.25, 0.15])
    plans = np.random.choice(plan_types, N_HOUSEHOLDS, p=[0.45, 0.35, 0.20])
    region = np.random.choice(regions, N_HOUSEHOLDS, p=[0.22, 0.24, 0.20, 0.16, 0.18])
    num_nodes = np.random.choice([1, 2, 3, 4, 5], N_HOUSEHOLDS,
                                  p=[0.25, 0.30, 0.25, 0.13, 0.07])
    connected_devices = np.clip(
        np.random.poisson(lam=12, size=N_HOUSEHOLDS) + num_nodes * 3, 3, 60
    )
    tenure_days = np.random.randint(30, 1100, N_HOUSEHOLDS)
    signup_dates = [START_DATE - timedelta(days=int(t)) for t in tenure_days]

    # --- Churn logic: additive probability with moderate weights ---
    firmware_churn_weight = np.array([
        {"6.1.0": 0.12, "6.2.0": 0.09, "6.3.0": 0.06,
         "6.4.0": 0.04, "6.4.2": 0.03, "6.5.0": 0.02}[fw]
        for fw in firmwares
    ])
    node_churn_weight = np.where(num_nodes == 1, 0.08, np.where(num_nodes == 2, 0.03, 0.01))
    plan_churn_weight = np.array([
        {"Basic": 0.07, "eero Plus": 0.03, "eero Secure+": 0.01}[p] for p in plans
    ])
    churn_prob = np.clip(
        firmware_churn_weight + node_churn_weight + plan_churn_weight
        + np.random.normal(0, 0.04, N_HOUSEHOLDS),
        0.03, 0.45
    )
    churned = np.random.binomial(1, churn_prob)

    df = pd.DataFrame({
        "household_id": [f"HH-{i:05d}" for i in range(N_HOUSEHOLDS)],
        "device_model": models,
        "firmware_version": firmwares,
        "plan_type": plans,
        "region": region,
        "num_nodes": num_nodes,
        "connected_devices": connected_devices,
        "tenure_days": tenure_days,
        "signup_date": signup_dates,
        "churned": churned,
    })

    df.to_csv(os.path.join(DATA_DIR, "households.csv"), index=False)
    print(f"   -> {len(df)} rows | churn rate = {churned.mean():.2%}")
    return df


def generate_network_events(households_df):
    print("[2/4] Generating network_events.csv ...")

    dates = pd.date_range(START_DATE, periods=OBSERVATION_DAYS, freq="D")
    sample_size = min(len(dates), 90)
    rows = []

    for _, hh in households_df.iterrows():
        hh_dates = np.sort(np.random.choice(dates, size=sample_size, replace=False))
        is_churned = hh["churned"]

        # Moderate difference — churned households have slightly worse metrics
        # but with large overlap in distributions
        base_drops = 2.0 + is_churned * 1.5 + np.random.normal(0, 0.8)
        base_latency = 25.0 + is_churned * 8.0 + np.random.normal(0, 6)

        for d in hh_dates:
            d_ts = pd.Timestamp(d)
            dow = d_ts.dayofweek
            hour_weight = 1.0 + 0.15 * (dow >= 5)
            evening_weight = 1.0 + 0.1 * np.random.random()

            drops = max(0, int(np.random.poisson(max(0.5, base_drops * hour_weight * evening_weight))))
            latency = max(5, np.random.normal(base_latency * evening_weight, 10))
            bandwidth = max(50, np.random.normal(320 - is_churned * 30, 90))
            offline = max(0, np.random.exponential(4 + is_churned * 3))
            pkt_loss = max(0, np.random.normal(0.8 + is_churned * 0.5, 0.6))

            rows.append({
                "household_id": hh["household_id"],
                "date": d_ts.strftime("%Y-%m-%d"),
                "connection_drops": drops,
                "avg_latency_ms": round(latency, 1),
                "peak_bandwidth_mbps": round(bandwidth, 1),
                "offline_duration_minutes": round(offline, 1),
                "packet_loss_pct": round(pkt_loss, 3),
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "network_events.csv"), index=False)
    print(f"   -> {len(df):,} rows")
    return df


def generate_user_sessions(households_df):
    print("[3/4] Generating user_sessions.csv ...")

    features = ["speed_test", "parental_controls", "device_management",
                 "guest_network", "security_scan"]
    dates = pd.date_range(START_DATE, periods=OBSERVATION_DAYS, freq="D")
    rows = []

    for _, hh in households_df.iterrows():
        is_churned = hh["churned"]
        n_sessions = np.random.randint(30, 120)
        session_dates = np.sort(np.random.choice(dates, size=n_sessions, replace=True))

        for i, d in enumerate(session_dates):
            d_ts = pd.Timestamp(d)
            if is_churned:
                app_opens = max(0, int(np.random.poisson(2.5) - i * 0.015))
                feat_probs = [0.35, 0.12, 0.25, 0.13, 0.15]
                duration = max(10, np.random.normal(120, 50) - i * 0.3)
                ticket_prob = 0.06
            else:
                app_opens = max(1, int(np.random.poisson(3.5)))
                feat_probs = [0.22, 0.20, 0.22, 0.18, 0.18]
                duration = max(10, np.random.normal(160, 60))
                ticket_prob = 0.025

            rows.append({
                "household_id": hh["household_id"],
                "date": d_ts.strftime("%Y-%m-%d"),
                "app_opens": app_opens,
                "feature_used": np.random.choice(features, p=feat_probs),
                "session_duration_seconds": round(duration),
                "support_ticket_raised": int(np.random.random() < ticket_prob),
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "user_sessions.csv"), index=False)
    print(f"   -> {len(df):,} rows")
    return df


def generate_firmware_updates(households_df):
    print("[4/4] Generating firmware_updates.csv ...")

    candidates = households_df[
        households_df["firmware_version"].isin(["6.4.0", "6.4.2"])
    ].copy()

    rows = []
    for _, hh in candidates.iterrows():
        old_fw = hh["firmware_version"]
        updated = np.random.random() < 0.55
        new_fw = "6.5.0" if updated else old_fw
        update_date = START_DATE + timedelta(days=np.random.randint(30, 150))
        success = 1 if updated else 0

        pre_drops = max(0, int(np.random.poisson(4)))
        if updated and success:
            post_drops = max(0, int(np.random.poisson(4 * 0.70)))  # ~30% reduction
        else:
            post_drops = max(0, int(np.random.poisson(4)))

        rows.append({
            "household_id": hh["household_id"],
            "old_firmware": old_fw,
            "new_firmware": new_fw,
            "update_date": update_date.strftime("%Y-%m-%d"),
            "update_success": success,
            "post_update_drops_7day": post_drops,
            "pre_update_drops_7day": pre_drops,
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "firmware_updates.csv"), index=False)
    print(f"   -> {len(df):,} rows")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("Smart Home Analytics — Data Generation")
    print("=" * 60)
    hh = generate_households()
    generate_network_events(hh)
    generate_user_sessions(hh)
    generate_firmware_updates(hh)
    print("=" * 60)
    print("All datasets saved to data/")
    print("=" * 60)
