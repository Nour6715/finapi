"""Graphiques Plotly pour le dashboard."""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

NAVY = "#0A1F44"
GOLD = "#C9A961"
SENT_COLORS = {
    "positive": "#16A34A",
    "neutral":  "#94A3B8",
    "negative": "#DC2626",
}


def price_line_chart(prices: list[dict]) -> go.Figure:
    """Graphique en ligne des prix de cloture."""
    if not prices:
        return go.Figure()
    df = pd.DataFrame(prices).sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["close"],
        mode="lines+markers",
        line=dict(color=NAVY, width=2),
        marker=dict(size=4, color=GOLD),
        name="Close",
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=320,
        xaxis_title="Date", yaxis_title="Close ($)",
        plot_bgcolor="white",
        hovermode="x unified",
    )
    return fig


def sentiment_pie_chart(distribution: dict[str, int]) -> go.Figure:
    """Pie chart (donut) de la distribution des sentiments."""
    if not distribution:
        return go.Figure()
    df = pd.DataFrame(
        [{"label": k, "count": v} for k, v in distribution.items()]
    )
    fig = px.pie(
        df, values="count", names="label",
        color="label", color_discrete_map=SENT_COLORS, hole=0.55,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=320,
        showlegend=True,
    )
    return fig


# ── BONUS: graphique en chandelier (OHLC) ────────────────────────────
def candlestick_chart(prices: list[dict]) -> go.Figure:
    """Graphique en chandelier. Nécessite open/high/low/close.
    Si seulement close disponible, simule OHLC avec variation ±0.5%.
    """
    if not prices:
        return go.Figure()
    df = pd.DataFrame(prices).sort_values("date")

    # Simulation OHLC si seulement close disponible
    if "open" not in df.columns:
        df["open"] = df["close"].shift(1).fillna(df["close"])
        df["high"] = df[["open", "close"]].max(axis=1) * 1.005
        df["low"] = df[["open", "close"]].min(axis=1) * 0.995

    fig = go.Figure(data=[go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color=SENT_COLORS["positive"],
        decreasing_line_color=SENT_COLORS["negative"],
    )])
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=350,
        xaxis_title="Date", yaxis_title="Prix ($)",
        plot_bgcolor="white",
        xaxis_rangeslider_visible=False,
    )
    return fig


# ── BONUS: graphique des stats ────────────────────────────────────────
def stats_bar_chart(distribution: dict[str, int]) -> go.Figure:
    """Bar chart de la distribution des sentiments."""
    if not distribution:
        return go.Figure()
    labels = list(distribution.keys())
    values = list(distribution.values())
    colors = [SENT_COLORS.get(l, "#94A3B8") for l in labels]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=values,
        textposition="auto",
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=280,
        plot_bgcolor="white",
        yaxis_title="Nombre d'articles",
    )
    return fig
