"""Dashboard interactif d'analyse de sentiment financier."""

import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard import api_client as api
from dashboard.charts import (
    SENT_COLORS,
    candlestick_chart,
    price_line_chart,
    sentiment_pie_chart,
    stats_bar_chart,
)

"""import api_client as api"""
"""from dashboard.charts import (
    price_line_chart,
    sentiment_pie_chart,
    candlestick_chart,
    stats_bar_chart,
    SENT_COLORS,
)"""

# ── Configuration de la page ──────────────────────────────────────────
st.set_page_config(
    page_title="FinSentiment Dashboard",
    page_icon="📈",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎛️ Contrôles")
    st.caption("Configurez votre vue ci-dessous.")

    # Vérification API
    api_ok = api.get_health()
    if api_ok:
        st.success("✅ API connectée")
    else:
        st.error("❌ API injoignable")
        st.info("Lancez 'python -m finapi.app' dans un autre terminal.")
        st.stop()

    # Stats et sélection ticker
    stats = api.get_db_stats()
    available_tickers = stats.get("tickers", [])

    if not available_tickers:
        st.warning("Base vide. Lancez 'python scripts/run_etl.py AAPL MSFT'.")
        st.stop()

    ticker = st.selectbox("📊 Ticker", available_tickers)

    # BONUS: Slider période
    st.divider()
    period = st.select_slider(
        "📅 Période d'historique",
        options=["7d", "1mo", "3mo", "6mo", "1y"],
        value="1mo",
    )

    # BONUS: Type de graphique
    chart_type = st.radio(
        "📈 Type de graphique",
        ["Ligne", "Chandelier"],
        horizontal=True,
    )

    st.divider()

    # Bouton refresh (BONUS)
    if st.button("🔄 Refresh maintenant"):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        f"DB: {stats.get('prices_count', 0)} prix | "
        f"{stats.get('news_count', 0)} news "
        f"({stats.get('news_enriched', 0)} avec sentiment)"
    )

# ── En-tête ───────────────────────────────────────────────────────────
st.title(f"📈 FinSentiment — {ticker}")
st.caption("Dashboard interactif — prix, news, sentiment FinBERT")


# ── Chargement des données avec cache ─────────────────────────────────
@st.cache_data(ttl=60)
def load_prices(t: str) -> list[dict]:
    return api.get_db_prices(t)


@st.cache_data(ttl=60)
def load_news(t: str) -> list[dict]:
    return api.get_db_news(t)


@st.cache_data(ttl=60)
def load_summary(t: str) -> dict:
    return api.get_sentiment_summary(t)


prices = load_prices(ticker)
news = load_news(ticker)
sentiment = load_summary(ticker)

# ── BONUS: Onglets ────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "📰 News détaillées", "📈 Stats"])

# ════════════════════════════════════════════════════════════════════
# ONGLET 1 — Vue d'ensemble
# ════════════════════════════════════════════════════════════════════
with tab1:
    # Métriques en haut
    col1, col2, col3, col4 = st.columns(4)

    if prices:
        last = prices[0]
        prev = prices[1] if len(prices) > 1 else last
        delta = round(last["close"] - prev["close"], 2)
        delta_pct = round(delta / prev["close"] * 100, 2) if prev["close"] else 0

        col1.metric(
            "💰 Dernier cours", f"${last['close']:.2f}", f"{delta:+.2f} ({delta_pct:+.2f}%)"
        )
        col2.metric("📅 Date", last["date"])
    else:
        col1.metric("💰 Dernier cours", "N/A")
        col2.metric("📅 Date", "N/A")

    col3.metric("📰 News stockées", len(news))

    total_sent = sum(sentiment.values()) or 1
    pos_share = round(sentiment.get("positive", 0) / total_sent * 100)
    col4.metric("😊 Sentiment positif", f"{pos_share}%")

    st.divider()

    # Graphiques côte à côte
    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("📈 Évolution du prix")
        if prices:
            if chart_type == "Chandelier":
                st.plotly_chart(candlestick_chart(prices), use_container_width=True)
            else:
                st.plotly_chart(price_line_chart(prices), use_container_width=True)
        else:
            st.info("Aucun prix en base pour ce ticker.")

    with g2:
        st.subheader("🎭 Distribution sentiment")
        if sentiment:
            st.plotly_chart(sentiment_pie_chart(sentiment), use_container_width=True)
        else:
            st.info("Aucun sentiment calculé. Lancez 'enrich_sentiment.py'.")

    st.divider()

    # News colorées (aperçu)
    st.subheader(f"📰 Dernières news — {ticker}")
    if not news:
        st.info("Aucune news en base.")
    else:
        for n in news[:5]:
            sent = n.get("sentiment_label") or "neutral"
            color = SENT_COLORS.get(sent, "#94A3B8")
            score = n.get("sentiment_score")
            score_str = f" ({score:.2f})" if score else ""
            st.markdown(
                f"<div style='border-left: 4px solid {color};"
                f" padding: 8px 14px; margin: 4px 0;"
                f" background: #F8FAFC;'>"
                f"<b>{n['title']}</b><br>"
                f"<small style='color:#64748B'>"
                f"{n.get('publisher', '')} — "
                f"{n['published_at'][:16]} — "
                f"<span style='color:{color}; font-weight:bold;'>"
                f"{sent.upper()}{score_str}"
                f"</span></small>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════
# ONGLET 2 — News détaillées (BONUS)
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"📰 Toutes les news — {ticker}")

    if not news:
        st.info("Aucune news en base.")
    else:
        # Filtre par sentiment
        filter_sent = st.multiselect(
            "Filtrer par sentiment",
            options=["positive", "neutral", "negative"],
            default=["positive", "neutral", "negative"],
        )

        filtered_news = [n for n in news if (n.get("sentiment_label") or "neutral") in filter_sent]

        st.caption(f"{len(filtered_news)} article(s) affiché(s)")

        for n in filtered_news:
            sent = n.get("sentiment_label") or "neutral"
            color = SENT_COLORS.get(sent, "#94A3B8")
            score = n.get("sentiment_score")
            score_str = f" — Score: {score:.2f}" if score else ""

            with st.expander(
                f"{'🟢' if sent == 'positive' else '🔴' if sent == 'negative' else '⚪'} {n['title']}"
            ):
                st.markdown(
                    f"**Publisher:** {n.get('publisher', 'N/A')}  \n"
                    f"**Date:** {n['published_at'][:16]}  \n"
                    f"**Sentiment:** "
                    f"<span style='color:{color}; font-weight:bold;'>"
                    f"{sent.upper()}{score_str}</span>  \n"
                    f"**URL:** [{n.get('url', 'N/A')}]({n.get('url', '#')})",
                    unsafe_allow_html=True,
                )

# ════════════════════════════════════════════════════════════════════
# ONGLET 3 — Stats (BONUS)
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📊 Statistiques de la base")

    # Stats globales
    c1, c2, c3 = st.columns(3)
    c1.metric("Total prix", stats.get("prices_count", 0))
    c2.metric("Total news", stats.get("news_count", 0))
    c3.metric("News enrichies", stats.get("news_enriched", 0))

    st.divider()

    # Distribution sentiment en bar chart
    st.subheader(f"Distribution sentiment — {ticker}")
    if sentiment:
        st.plotly_chart(stats_bar_chart(sentiment), use_container_width=True)
        # Tableau récapitulatif
        st.subheader("Détail")
        total = sum(sentiment.values()) or 1
        for label, count in sentiment.items():
            pct = round(count / total * 100, 1)
            color = SENT_COLORS.get(label, "#94A3B8")
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>"
                f"{label.upper()}</span>: {count} articles ({pct}%)",
                unsafe_allow_html=True,
            )
    else:
        st.info("Aucun sentiment calculé pour ce ticker.")

# Ajoute "À propos" aux onglets existants:
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Vue d'ensemble", "📰 News détaillées", "📈 Stats", "ℹ️ À propos"]
)
with tab4:
    st.subheader("ℹ️ À propos de FinSentiment")
    st.markdown("""
    **FinSentiment** est un dashboard d'analyse de sentiment financier
    construit avec Flask, FinBERT et Streamlit.

    ### Stack technique
    - **Backend:** Flask + SQLAlchemy + SQLite
    - **ML:** FinBERT (ProsusAI/finbert) via Hugging Face Transformers
    - **Frontend:** Streamlit + Plotly
    - **Data:** yfinance (Yahoo Finance)

    ### Parcours
    Ce projet a été construit en 6 labs dans le cadre du cours
    **Coaching M1/M2 Finance Quantitative** à l'ITBS.

    ### Liens
    - 🔗 [Code source GitHub](https://github.com/Nour6715/finapi)
    - 🤗 [Hugging Face Space](https://huggingface.co/spaces/Wiem6715/finsentiment)
    - 👨‍🏫 [Prof. Ahmed Ben Taleb — ITBS](https://www.itbs.tn)

    ### Auteur
    **Wiem** — M2 Finance Quantitative, ITBS
    """)

# ── Footer ────────────────────────────────────────────────────────────
st.divider()
st.caption(f"Mis à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
