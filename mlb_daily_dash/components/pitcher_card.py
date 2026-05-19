"""Streamlit component that renders a starting pitcher profile card."""

import streamlit as st


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _warn(col, message: str) -> None:
    """Append a small red warning line beneath a metric tile."""
    col.markdown(f":red[⚠ {message}]")


def _split_metrics(col, label: str, split: dict) -> None:
    """Render OPS / HR / TB tiles inside a column for one handedness split."""
    col.markdown(f"**{label}**")
    pa    = split.get("pa") or 0
    ops   = split.get("ops", 0.0)
    hr    = split.get("hr", 0)
    tb    = split.get("tb", 0)
    games = split.get("games", 0)

    m1, m2, m3 = col.columns(3)
    m1.metric("OPS",        f"{ops:.3f}")
    m2.metric("HR allowed", str(hr))
    m3.metric("TB allowed", str(tb))

    if pa:
        g_label = f", {games} G" if games else ""
        col.caption(f"({pa} BF{g_label})")


# ---------------------------------------------------------------------------
# Public component
# ---------------------------------------------------------------------------

def render_pitcher_card(
    pitcher: dict,
    splits: dict,
    workload: dict,
    split_window: str,
) -> None:
    """Render a pitcher profile card with workload flags and platoon splits.

    Args:
        pitcher: Pitcher dict with at minimum "name" and "hand" keys.
        splits: Full splits dict {"vsLeft": {...}, "vsRight": {...}} from
            get_pitcher_splits(). Pass an empty dict when unavailable.
        workload: Dict from get_pitcher_workload() with days_rest,
            last_pitch_count, last_3_ip. Pass an empty dict when unavailable.
        split_window: "season" or "rolling30" — shown as a caption label.
    """
    if not pitcher or not splits:
        st.info("Probable pitcher TBD.")
        return

    name: str = pitcher.get("name") or "Unknown"
    hand: str = pitcher.get("hand") or "R"
    hand_label = "LHP" if hand == "L" else "RHP"

    st.subheader(f"{name} · {hand_label}")

    # ── Workload row ─────────────────────────────────────────────────────────
    days_rest:    int   = workload.get("days_rest", 0)
    pitch_count:  int   = workload.get("last_pitch_count", 0)
    last_3_ip:    float = workload.get("last_3_ip", 0.0)

    wc1, wc2, wc3 = st.columns(3)

    wc1.metric("Rest", f"{days_rest} day{'s' if days_rest != 1 else ''}")
    if days_rest < 4:
        _warn(wc1, "Short rest")

    wc2.metric("Last start", f"{pitch_count} pitches")

    wc3.metric("L3 starts", f"{last_3_ip:.1f} IP")

    # ── Platoon splits ───────────────────────────────────────────────────────
    st.divider()

    vs_l = splits.get("vsLeft")  or {}
    vs_r = splits.get("vsRight") or {}

    sc1, sc2 = st.columns(2)
    _split_metrics(sc1, "vs LHB", vs_l)
    _split_metrics(sc2, "vs RHB", vs_r)

    st.caption(f"Split window: {split_window}")
