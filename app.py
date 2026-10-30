import streamlit as st
import requests
import plotly.express as px

from data import (
    fetch_indicator,
    INDICATORS,
    get_latest_stats
)


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Nepal Economic Dashboard",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# INDICATOR DESCRIPTIONS

INDICATOR_DESCRIPTIONS = {
    "GDP Growth": (
        "Annual percentage growth rate of Nepal's "
        "GDP at constant prices."
    ),

    "Inflation Rate": (
        "Annual percentage change in consumer prices."
    ),

    "Remittances": (
        "Personal remittances received as a percentage "
        "of Nepal's GDP."
    ),

    "Exports": (
        "Exports of goods and services "
        "as a percentage of GDP."
    ),

    "Imports": (
        "Imports of goods and services "
        "as a percentage of GDP."
    )
}


# DATA LOADING

@st.cache_data(ttl=3600)
def load_data(indicator_code):
    """Fetch and cache World Bank data for one hour."""
    return fetch_indicator(indicator_code)


# DASHBOARD HEADER

st.title("🇳🇵 Nepal Economic Dashboard")

st.markdown(
    """
    ### Understanding Nepal's Economy Through Data

    Explore Nepal's key economic indicators through
    interactive visualizations and historical trends.
    """
)

st.caption(
    "Data Source: World Bank Open Data | Country: Nepal"
)

st.divider()


# SIDEBAR FILTERS

with st.sidebar:

    st.title("Dashboard Filters")

    st.markdown(
        "Customize the economic indicators "
        "and visualizations."
    )

    st.divider()

    selected_indicator = st.selectbox(
        "Select Economic Indicator",
        list(INDICATORS.keys())
    )

    chart_type = st.radio(
        "Select Chart Type",
        ["Line Chart", "Bar Chart"],
        horizontal=True
    )

    st.divider()

    st.caption(
        "Data provided by World Bank Open Data."
    )


# ECONOMIC OVERVIEW

st.subheader("Economic Overview")

st.write(
    "Latest available economic indicators for Nepal."
)

overview_indicators = [
    "GDP Growth",
    "Inflation Rate",
    "Remittances"
]

cols = st.columns(3)


for col, indicator_name in zip(cols, overview_indicators):

    with col:

        indicator_code = INDICATORS[indicator_name]

        try:

            overview_df = load_data(indicator_code)

            stats = get_latest_stats(overview_df)

            if stats is None:

                st.warning(
                    f"No data available for {indicator_name}"
                )

                continue

            latest_value = stats["latest_value"]
            latest_year = stats["latest_year"]
            previous_year = stats["previous_year"]
            delta = stats["delta"]

            if delta is not None:

                delta_text = f"{delta:+.2f} pp"

            else:

                delta_text = None

            st.metric(
                label=indicator_name,
                value=f"{latest_value:.2f}%",
                delta=delta_text,
                delta_color="off",
                border=True,
                help=INDICATOR_DESCRIPTIONS[indicator_name]
            )

            if previous_year is not None:

                st.caption(
                    f"Latest: {latest_year} | "
                    f"Change since {previous_year}"
                )

            else:

                st.caption(
                    f"Latest: {latest_year}"
                )

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError
        ):

            st.error(
                f"Unable to load {indicator_name}"
            )


st.divider()


# ECONOMIC TRENDS

st.subheader("Economic Trends")

st.write(
    "Explore historical economic performance "
    "by selecting an indicator and time period."
)

indicator_code = INDICATORS[selected_indicator]


try:

    df = load_data(indicator_code)

    if df.empty:

        st.warning(
            "No data available for this indicator."
        )

    else:

        # ==========================================
        # YEAR RANGE FILTER
        # ==========================================

        min_year = int(df["year"].min())
        max_year = int(df["year"].max())

        with st.sidebar:

            st.subheader("Time Period")

            if min_year < max_year:

                start_year, end_year = st.slider(
                    "Select Year Range",
                    min_value=min_year,
                    max_value=max_year,
                    value=(
                        max(min_year, max_year - 15),
                        max_year
                    )
                )

            else:

                start_year = end_year = min_year

                st.caption(
                    f"Only {min_year} is available."
                )

        # ==========================================
        # FILTER DATA
        # ==========================================

        filtered_df = df[
            (df["year"] >= start_year) &
            (df["year"] <= end_year)
        ].copy()

        if filtered_df.empty:

            st.warning(
                "No observations available "
                "for the selected period."
            )

            st.stop()

        # ==========================================
        # CREATE CHART
        # ==========================================

        if chart_type == "Line Chart":

            fig = px.line(
                filtered_df,
                x="year",
                y="value",
                markers=True,
                title=f"{selected_indicator} in Nepal",
                labels={
                    "year": "Year",
                    "value": "Percentage (%)"
                },
                template="plotly_white"
            )

            fig.update_traces(
                line=dict(
                    color="#2563EB",
                    width=3
                ),
                marker=dict(
                    size=7
                )
            )

        else:

            fig = px.bar(
                filtered_df,
                x="year",
                y="value",
                title=f"{selected_indicator} in Nepal",
                labels={
                    "year": "Year",
                    "value": "Percentage (%)"
                },
                template="plotly_white",
                color_discrete_sequence=["#2563EB"]
            )

        # ==========================================
        # HOVER TOOLTIP
        # ==========================================

        fig.update_traces(
            hovertemplate=(
                "<b>Year:</b> %{x}<br>"
                "<b>Value:</b> %{y:.2f}%"
                "<extra></extra>"
            )
        )

        # ==========================================
        # CHART STYLING
        # ==========================================

        fig.update_layout(
            hovermode="x unified",
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        fig.update_xaxes(
            title_text="Year",
            dtick=(
                1 if end_year - start_year <= 15
                else 5
            ),
            showgrid=False
        )

        fig.update_yaxes(
            title_text="Percentage (%)",
            ticksuffix="%",
            showgrid=True,
            gridcolor="#E5E7EB"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==========================================
        # INDICATOR EXPLANATION
        # ==========================================

        st.info(
            INDICATOR_DESCRIPTIONS[selected_indicator]
        )

        st.divider()

        # ==========================================
        # STATISTICAL SUMMARY
        # ==========================================

        st.subheader("Statistical Summary")

        st.caption(
            f"Summary for the selected period: "
            f"{start_year}–{end_year}"
        )

        average_value = filtered_df["value"].mean()

        highest_row = filtered_df.loc[
            filtered_df["value"].idxmax()
        ]

        lowest_row = filtered_df.loc[
            filtered_df["value"].idxmin()
        ]

        highest_value = highest_row["value"]
        highest_year = int(highest_row["year"])

        lowest_value = lowest_row["value"]
        lowest_year = int(lowest_row["year"])

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                label="Average",
                value=f"{average_value:.2f}%",
                border=True
            )

        with col2:

            st.metric(
                label=f"Highest ({highest_year})",
                value=f"{highest_value:.2f}%",
                border=True
            )

        with col3:

            st.metric(
                label=f"Lowest ({lowest_year})",
                value=f"{lowest_value:.2f}%",
                border=True
            )

        st.divider()

        # ==========================================
        # DATA TABLE
        # ==========================================

        with st.expander("View Economic Data"):

            st.dataframe(
                filtered_df.rename(
                    columns={
                        "year": "Year",
                        "value": "Value (%)"
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

        # ==========================================
        # DATA SOURCE
        # ==========================================

        st.caption(
            f"Source: World Bank Open Data | "
            f"Indicator: {selected_indicator} | "
            f"Period: {start_year}–{end_year}"
        )


except (
    requests.RequestException,
    ValueError,
    KeyError,
    TypeError
) as e:

    st.error(
        f"Unable to load economic data: {e}"
    )