import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# 1. Assignment Libraries, File Paths and Dashboard Settings 
# First, I define the key file paths and constants which will be used throughout
# the dashboard. Keeping these in one place makes the rest of the code easier to
# update if the dataset, map file, or colour choices change later.

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "kenya_cleaned_data_final.csv"
GEOJSON_PATH = APP_DIR / "kenya.geojson"

VOTED_LABEL = "I voted in the election"
TOO_YOUNG_LABEL = "I was too young to vote"
NO_RESPONSE_LABEL = "Undecided/No Response"
NON_PARTY_RESPONSES = {"Would not vote", NO_RESPONSE_LABEL}
APPROVAL_LABELS = {"Approve", "Strongly approve"}
GENDER_LABELS = {"Man": "Male", "Woman": "Female"}

COUNTY_NAME_FIXES = {
    "Elgeyo Marakwet": "Keiyo-Marakwet",
    "Muranga": "Murang'a",
    "Tharaka Nithi": "Tharaka",
}

COLORS = [
    "#7c3aed",
    "#dc2626",
    "#0891b2",
    "#7570b3",
    "#e7298a",
    "#a6761d",
    "#4f46e5",
    "#be123c",
    "#64748b",
    "#666666",
]

PARTY_COLOR_OVERRIDES = {
    "Agano Party": "#0e7490",
    "Amani National Congress": "#7c3aed",
    "Jubilee Alliance Party": "#06b6d4",
    "KANU": "#8b5cf6",
    "Kenya Social Congress": "#db2777",
    "Maendeleo Chap Chap": "#a16207",
    "NARC": "#0f172a",
    "National Rainbow Coalition": "#be123c",
    "No named party": "#9ca3af",
    "Orange Democratic Movement": "#f97316",
    "Other": "#737373",
    "Restore and Build Kenya": "#475569",
    "Roots Party of Kenya": "#dc2626",
    "Undecided/No Response": "#6366f1",
    "United Democratic Alliance": "#16a34a",
    "Wiper Democratic Movement": "#2563eb",
    "Would not vote": "#92400e",
}

PARTY_MAP_LEGEND_ORDER = [
    "United Democratic Alliance",
    "Orange Democratic Movement",
    "Wiper Democratic Movement",
]

PROFILE_COLUMNS = {
    "Education Level": "education_grouped",
    "Employment Status": "employment_status",
    "Occupation": "occupation_grouped",
}

TAB_LABELS = [
    "County Mapping",
    "Voting Information",
    "Respondent Information",
    "News Information",
    "Data Table",
]

EDUCATION_ORDER = [
    "Informal Schooling",
    "Primary School",
    "Secondary School",
    "Certificate/Diploma",
    "Bachelors Degree",
    "Masters/PhD",
]

NEWS_COLUMNS = {
    "Radio": "news_radio",
    "TV": "news_tv",
    "Newspapers": "news_newspapers",
    "Social Media": "news_social_media",
    "Internet": "news_internet",
}

NEWS_FREQUENCY_COLORS = {
    "Daily use": "#1769aa",
    "At least weekly": "#1b9e77",
}

SETTING_COLOR_MAP = {
    "Urban": "#7c3aed",
    "Rural": "#dc2626",
}

MEDIA_GROUP_COLORS = {
    "Traditional News": "#1769aa",
    "Digital News": "#16a34a",
}

TRADITIONAL_NEWS_COLUMNS = ["news_radio", "news_tv", "news_newspapers"]
DIGITAL_NEWS_COLUMNS = ["news_social_media", "news_internet"]

SCORE_MAPS = {
    "trust_president": (
        "trust_president",
        {"Not at all": 1, "Just a little": 2, "Somewhat": 3, "A lot": 4},
    ),
    "economic_condition": (
        "economic_condition",
        {
            "Very bad": 1,
            "Fairly bad": 2,
            "Neither good nor bad": 3,
            "Fairly good": 4,
            "Very good": 5,
        },
    ),
    "corruption_level": (
        "corruption_level",
        {
            "Decreased a lot": 1,
            "Decreased somewhat": 2,
            "Stayed the same": 3,
            "Increased somewhat": 4,
            "Increased a lot": 5,
        },
    ),
}

MAP_METRICS = [
    "Respondent Distribution",
    "Voter Turnout (%)",
    "Party Popularity",
    "Presidential Approval (%)",
    "Presidential Trust Level",
    "Economic Condition",
    "Corruption Level",
    "Top Daily News Source",
]

MAP_METRIC_ALIASES = {
    "Respondent Distribution": "respondents",
    "Respondents": "respondents",
    "Voter Turnout (%)": "turnout",
    "Reported turnout (%)": "turnout",
    "Party Popularity": "leading_party",
    "Leading party": "leading_party",
    "Presidential Approval (%)": "approval",
    "Presidential approval (%)": "approval",
    "Presidential Trust Level": "trust_president",
    "Trust in president": "trust_president",
    "Economic Condition": "economic_condition",
    "Economic condition": "economic_condition",
    "Corruption Level": "corruption_level",
    "Corruption level": "corruption_level",
    "Top Daily News Source": "top_daily_news_source",
    "Top Daily Source of News": "top_daily_news_source",
    "Top daily news source": "top_daily_news_source",
}

# 2. Page Configuration and Styling 
# This section controls the overall Streamlit page layout

st.set_page_config(
    page_title="Mapping Public Opinion, Voting Behaviour, and News Consumption in Kenya",
    page_icon=APP_DIR / "kenya_flag_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1240px;
            padding-top: 1.3rem;
            padding-bottom: 2rem;
        }

        .metric-note {
            color: #536172;
            font-size: 0.84rem;
            margin-top: -0.65rem;
            margin-bottom: 0.75rem;
        }

        .small-note {
            color: #536172;
            font-size: 0.9rem;
        }

        .dashboard-title {
            text-align: center;
            margin-bottom: 0.4rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# 3. Dashboard Title and Other Elements

def main():
    df = load_data()
    kenya_geojson = load_geojson()

    st.markdown(
        '<h1 class="dashboard-title">Interactive Dashboards Assignment: ' \
        'Mapping Public Opinion, Voting Behaviour, and News Consumption in Kenya</h1>',
        unsafe_allow_html=True,
    )
    st.caption(
        "As Kenya approaches the 2027 general election, there is a lot of debate on the current political climate in the country. This dashboard, which is based on data from 2024, " \
        "attempts to cut through the noise and show how a section of Kenyans actually feel about the current presidency, their voting patterns in the 2022 elections, how they consume their news "
        "and their general sentiments towards things such as corruption and the direction in which the country is headed."
    )

    # Using sidebar filters
    filtered_df = build_sidebar_filters(df)

    if filtered_df.empty:
        st.warning("No respondents match the current filters.")
        st.stop()

    # The summary metrics update whenever a user changes the filters. Respondent count
    # remains a total figure, while popular political party and presidential approval rating are displayed as averages
    # if a user selects multiple counties.
    render_metrics(filtered_df)

    # Streamlit reruns the script whenever a filter changes to ensure that a user stays on the page they were in,
    # instead of going back to the first tab (County Mapping)
    active_tab = st.segmented_control(
        "Dashboard section",
        TAB_LABELS,
        default=TAB_LABELS[0],
        key="active_tab",
        label_visibility="collapsed",
        width="stretch",
    )
    if active_tab is None:
        active_tab = TAB_LABELS[0]

    if active_tab == "County Mapping":
        st.subheader("How Various Respondent Metrics Compare Across Kenyan Counties")
        control_col1, control_col2 = st.columns(2)
        with control_col1:
            left_metric = st.selectbox("Select Left Map Metric", MAP_METRICS, index=2)
        with control_col2:
            right_metric = st.selectbox("Select Right Map Metric", MAP_METRICS, index=3)

        map_col1, map_col2 = st.columns(2)
        with map_col1:
            kenya_map(filtered_df, kenya_geojson, left_metric, height=590)
        with map_col2:
            kenya_map(filtered_df, kenya_geojson, right_metric, height=590)

    elif active_tab == "Voting Information":
        render_voting(filtered_df)

    elif active_tab == "Respondent Information":
        render_profile(filtered_df)

    elif active_tab == "News Information":
        render_news(filtered_df)

    elif active_tab == "Data Table":
        render_data_table(filtered_df)

    st.markdown(
        '<p class="small-note">Please note that this dashboard does not represent the entire Kenyan population.</p>',
        unsafe_allow_html=True,
    )


# 4. Data Loading
# My cleaned dataset and the Kenya GeoJSON are loaded here. I cache both files so that
# Streamlit does not reload them every time a filter is changed.

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    data["age"] = pd.to_numeric(data["age"], errors="coerce")
    data["region"] = data["region"].astype(str).str.strip()
    data["county_map"] = data["region"].replace(COUNTY_NAME_FIXES)

    text_columns = data.select_dtypes(include="object").columns
    data[text_columns] = data[text_columns].fillna("Not stated")
    return data


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    with GEOJSON_PATH.open("r", encoding="utf-8") as source:
        return json.load(source)


# 5. Sidebar Filters

def build_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    setting_options = sorted_values(df, "urban_rural")
    selected_settings = st.sidebar.multiselect(
        "Select Urban or Rural Setting",
        setting_options,
        default=setting_options,
    )

    filter_base = (
        df[df["urban_rural"].isin(selected_settings)]
        if selected_settings
        else df.iloc[0:0]
    )

    county_options = sorted_values(filter_base, "region") if not filter_base.empty else []
    select_all_counties = st.sidebar.checkbox("Select all Counties", value=True)
    if select_all_counties:
        selected_counties = county_options
        st.sidebar.caption(f"All {len(county_options)} available counties selected.")
    else:
        selected_counties = st.sidebar.multiselect(
            "County",
            county_options,
            default=county_options[: min(6, len(county_options))],
            help="County options update after the urban/rural filter.",
        )

    filter_base = (
        filter_base[filter_base["region"].isin(selected_counties)]
        if selected_counties
        else filter_base.iloc[0:0]
    )

    gender_options = sorted_values(filter_base, "gender") if not filter_base.empty else []
    selected_genders = st.sidebar.multiselect(
        "Select Gender",
        gender_options,
        default=gender_options,
        format_func=lambda value: GENDER_LABELS.get(value, value),
    )

    filtered_df = (
        filter_base[filter_base["gender"].isin(selected_genders)]
        if selected_genders
        else filter_base.iloc[0:0]
    )

    # Additional Filters for Education, Employment Status and Occupation
    with st.sidebar.expander("Education, Employment Status, and Occupation Filters"):
        education_options = (
            sorted_values(filtered_df, "education_grouped")
            if not filtered_df.empty
            else []
        )
        selected_education = st.multiselect(
            "Education Level",
            education_options,
            default=education_options,
        )

        employment_options = (
            sorted_values(filtered_df, "employment_status")
            if not filtered_df.empty
            else []
        )
        selected_employment = st.multiselect(
            "Employment Status",
            employment_options,
            default=employment_options,
        )

        occupation_options = (
            sorted_values(filtered_df, "occupation_grouped")
            if not filtered_df.empty
            else []
        )
        selected_occupations = st.multiselect(
            "Occupation",
            occupation_options,
            default=occupation_options,
        )

    filtered_df = filtered_df[
        filtered_df["education_grouped"].isin(selected_education)
        & filtered_df["employment_status"].isin(selected_employment)
        & filtered_df["occupation_grouped"].isin(selected_occupations)
    ]

    min_age = int(df["age"].min())
    max_age = int(df["age"].max())
    age_range = st.sidebar.slider("Select Age Range", min_age, max_age, (min_age, max_age))
    return filtered_df[
        filtered_df["age"].between(age_range[0], age_range[1], inclusive="both")
    ]


# 6. Summary Metrics
# These functions calculate the summary metrics at the top of my dashboard.

def render_metrics(data: pd.DataFrame):
    county_count = data["county_map"].nunique()
    average_party, average_party_share = county_average_party(data)
    average_approval = county_average_approval(data)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("No. of Respondents", f"{len(data):,}")

    with metric_cols[1]:
        st.metric("Voted in the Last Election", format_pct(turnout_rate(data)))

    with metric_cols[2]:
        st.metric("Popular Political Party", party_acronym(average_party))

    with metric_cols[3]:
        st.metric("President's Approval Rating", format_pct(average_approval))

def turnout_rate(data: pd.DataFrame) -> float | None:
    eligible = data[
        ~data["voted_last_election"].isin([TOO_YOUNG_LABEL, NO_RESPONSE_LABEL])
    ]
    if eligible.empty:
        return None
    return eligible["voted_last_election"].eq(VOTED_LABEL).mean() * 100


def county_average_party(data: pd.DataFrame) -> tuple[str, float | None]:
    named = data[~data["party_voted_for"].isin(NON_PARTY_RESPONSES)].copy()
    if named.empty:
        return "N/A", None

    county_party_counts = (
        named.groupby(["county_map", "party_voted_for"], as_index=False)
        .size()
        .rename(columns={"size": "respondents"})
    )
    county_totals = (
        named.groupby("county_map", as_index=False)
        .size()
        .rename(columns={"size": "county_named_total"})
    )
    county_party_counts = county_party_counts.merge(county_totals, on="county_map")
    county_party_counts["county_share"] = (
        county_party_counts["respondents"]
        / county_party_counts["county_named_total"]
        * 100
    )

    average_shares = (
        county_party_counts.groupby("party_voted_for", as_index=False)["county_share"]
        .mean()
        .sort_values("county_share", ascending=False)
    )
    top_row = average_shares.iloc[0]
    return top_row["party_voted_for"], top_row["county_share"]


def county_average_approval(data: pd.DataFrame) -> float | None:
    temp = data[data["presidents_performance"] != NO_RESPONSE_LABEL].copy()
    if temp.empty:
        return None

    temp["approve"] = temp["presidents_performance"].isin(APPROVAL_LABELS)
    county_rates = temp.groupby("county_map")["approve"].mean().mul(100).dropna()
    if county_rates.empty:
        return None
    return county_rates.mean()


# 7. County Map Comparison
# The map tab lets users compare two county-level metrics side by side.

def kenya_map(
    data: pd.DataFrame,
    kenya_geojson: dict,
    metric: str,
    height: int = 560,
):
    map_data, color_column, is_numeric = county_metric_data(data, metric)
    # These are chart labels for the map hover text and legends. 
    map_chart_labels = {
        "respondents": "Respondent Distribution",
        "turnout": "Voter Turnout (%)",
        "approval": "Presidential Approval (%)",
        "score": "Mean score",
        "leading_party": "Party Popularity",
        "daily_share": "Daily News Use (%)",
        "top_daily_news_source": "Top Daily News Source",
    }

    common_args = dict(
        data_frame=map_data,
        geojson=kenya_geojson,
        locations="county_map",
        featureidkey="properties.COUNTY",
        color=color_column,
        hover_name="county_map",
        hover_data={"respondents": True, color_column: ":.1f" if is_numeric else True},
        labels=map_chart_labels,
        title=metric,
    )

    if is_numeric:
        fig = px.choropleth(**common_args, color_continuous_scale="YlGnBu")
    else:
        category_orders = None
        if color_column == "leading_party":
            category_orders = {
                color_column: ordered_party_legend_values(map_data[color_column])
            }
        fig = px.choropleth(
            **common_args,
            category_orders=category_orders,
            color_discrete_map=color_map_for(map_data[color_column]),
        )

    fig.update_geos(
        visible=False,
        projection_type="mercator",
        lonaxis_range=[33.5, 42.5],
        lataxis_range=[-5.2, 5.6],
        domain=dict(x=[0.0, 1.0], y=[0.22, 1.0]),
    )
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=46, b=120),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="middle",
            y=0.065,
            xanchor="center",
            x=0.5,
            entrywidth=0.38,
            entrywidthmode="fraction",
            itemsizing="constant",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=12, color="#f8fafc"),
        ),
        coloraxis_colorbar=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=0.065,
            yanchor="middle",
            len=0.72,
            thickness=12,
            title=dict(side="top", font=dict(size=12, color="#f8fafc")),
        tickfont=dict(size=12, color="#f8fafc"),
        ),
        font=dict(size=12),
    )
    if color_column == "leading_party":
        fig.update_layout(
            legend=dict(
                orientation="v",
                x=0.08,
                xanchor="left",
                y=0.16,
                yanchor="top",
                itemsizing="constant",
                itemwidth=30,
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                font=dict(size=12, color="#f8fafc"),
            )
        )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )


def county_metric_data(data: pd.DataFrame, metric: str) -> tuple[pd.DataFrame, str, bool]:
    metric_key = MAP_METRIC_ALIASES.get(metric, metric)

    if metric_key == "respondents":
        output = (
            data.groupby("county_map", as_index=False)
            .size()
            .rename(columns={"size": "respondents"})
        )
        return output, "respondents", True

    if metric_key == "turnout":
        temp = data.copy()
        temp["eligible"] = ~temp["voted_last_election"].isin(
            [TOO_YOUNG_LABEL, NO_RESPONSE_LABEL]
        )
        temp["voted"] = temp["voted_last_election"].eq(VOTED_LABEL)
        output = (
            temp.groupby("county_map", as_index=False)
            .agg(
                respondents=("county_map", "size"),
                eligible=("eligible", "sum"),
                voted=("voted", "sum"),
            )
        )
        output["turnout"] = output["voted"] / output["eligible"].replace(0, pd.NA) * 100
        return output, "turnout", True

    if metric_key == "approval":
        temp = data.copy()
        temp["valid"] = temp["presidents_performance"] != NO_RESPONSE_LABEL
        temp["approve"] = temp["presidents_performance"].isin(APPROVAL_LABELS)
        output = (
            temp.groupby("county_map", as_index=False)
            .agg(
                respondents=("county_map", "size"),
                valid=("valid", "sum"),
                approve=("approve", "sum"),
            )
        )
        output["approval"] = output["approve"] / output["valid"].replace(0, pd.NA) * 100
        return output, "approval", True

    if metric_key in SCORE_MAPS:
        column, mapping = SCORE_MAPS[metric_key]
        temp = data.copy()
        temp["score"] = temp[column].map(mapping)
        output = (
            temp.groupby("county_map", as_index=False)
            .agg(respondents=("county_map", "size"), score=("score", "mean"))
        )
        return output, "score", True

    if metric_key == "top_daily_news_source":
        rows = []
        for county, group in data.groupby("county_map"):
            shares = {
                source_name: group[column].eq("Every day").mean()
                for source_name, column in NEWS_COLUMNS.items()
            }
            rows.append(
                {
                    "county_map": county,
                    "respondents": len(group),
                    "top_daily_news_source": max(shares, key=shares.get),
                }
            )
        return pd.DataFrame(rows), "top_daily_news_source", False

    named = data[~data["party_voted_for"].isin(NON_PARTY_RESPONSES)]
    leading_party = (
        named.groupby("county_map")["party_voted_for"].agg(top_value).reset_index()
        if not named.empty
        else pd.DataFrame(columns=["county_map", "party_voted_for"])
    )
    leading_party = leading_party.rename(columns={"party_voted_for": "leading_party"})
    counts = (
        data.groupby("county_map", as_index=False)
        .size()
        .rename(columns={"size": "respondents"})
    )
    output = counts.merge(leading_party, on="county_map", how="left")
    output["leading_party"] = output["leading_party"].fillna("No named party")
    return output, "leading_party", False


# 8. Voting, Profile, News and Data Tabs

def render_voting(data: pd.DataFrame):
    st.subheader("Voter Distribution Across Political Parties in Kenya")
    compare_labels = {"gender": "Gender", "urban_rural": "Setting"}
    compare_by = st.selectbox(
        "Compare the Respondents' Party Choice By:",
        ["gender", "urban_rural"],
        format_func=lambda value: compare_labels.get(value, value.replace("_", " ").title()),
    )
    compare_label = compare_labels.get(compare_by, compare_by.replace("_", " ").title())

    left, right = st.columns([1, 1])
    with left:
        fig = bar_chart(
            data,
            "party_voted_for",
            "Party Voted For",
            top_n=10,
            horizontal=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        stacked = (
            data.groupby([compare_by, "party_voted_for"], as_index=False)
            .size()
            .rename(columns={"size": "respondents"})
        )
        stacked["share"] = stacked.groupby(compare_by)["respondents"].transform(
            lambda values: values / values.sum() * 100
        )
        compare_display = f"{compare_by}_display"
        stacked[compare_display] = (
            stacked[compare_by].replace(GENDER_LABELS)
            if compare_by == "gender"
            else stacked[compare_by]
        )

        fig = px.bar(
            stacked,
            x=compare_display,
            y="share",
            color="party_voted_for",
            title=f"Party Choice By: {compare_label}",
            labels={
                compare_display: compare_label,
                "share": "Share within group (%)",
                "party_voted_for": "Party Response",
            },
            category_orders={compare_display: ["Male", "Female"]} if compare_by == "gender" else None,
            color_discrete_map=color_map_for(stacked["party_voted_for"]),
            custom_data=["party_voted_for", "respondents", "share"],
        )
        fig.update_traces(
            hovertemplate=(
                f"{compare_label}: %{{x}}<br>"
                "Party response: %{customdata[0]}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Share within group: %{customdata[2]:.1f}%<extra></extra>"
            )
        )
        st.plotly_chart(standard_layout(fig), use_container_width=True)


def render_profile(data: pd.DataFrame):
    st.subheader("Respondent Information")
    profile_choice = st.selectbox("Information to View:", list(PROFILE_COLUMNS.keys()))
    profile_column = PROFILE_COLUMNS[profile_choice]

    left, right = st.columns([1, 1])
    with left:
        fig = bar_chart(
            data,
            profile_column,
            profile_choice,
            top_n=12,
            horizontal=profile_choice == "Occupation",
            share=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.box(
            data,
            x="urban_rural",
            y="age",
            color="urban_rural",
            title="Age Distribution by Setting",
            labels={"urban_rural": "Setting", "age": "Age"},
            color_discrete_sequence=COLORS,
        )
        st.plotly_chart(standard_layout(fig), use_container_width=True)


def render_news(data: pd.DataFrame):
    st.subheader("How are Kenyans Consuming News?")

    # This section summarises the different news sources and keeps respondent
    # counts beside the percentages so that the charts remain easy to interpret.
    summary_rows = []
    for source_name, column in NEWS_COLUMNS.items():
        daily_count = data[column].eq("Every day").sum()
        weekly_count = data[column].isin(["Every day", "A few times a week"]).sum()
        daily_share = daily_count / len(data) * 100
        weekly_share = weekly_count / len(data) * 100
        summary_rows.append(
            {
                "source": source_name,
                "column": column,
                "Daily use": daily_share,
                "At least weekly": weekly_share,
                "Daily respondents": daily_count,
                "Weekly respondents": weekly_count,
            }
        )

    news_summary = pd.DataFrame(summary_rows).sort_values("Daily use", ascending=False)
    top_daily = news_summary.sort_values("Daily use", ascending=False).iloc[0]

    # Digital news sources refers to social media or the internet.
    # Traditional news refers to radio, TV or newspapers.
    digital_daily = data[DIGITAL_NEWS_COLUMNS].eq("Every day").any(axis=1)
    digital_daily_count = int(digital_daily.sum())
    digital_daily_share = digital_daily_count / len(data) * 100

    source_by_setting_rows = []
    media_group_rows = []
    digital_setting_shares = {}
    for setting, group in data.groupby("urban_rural"):
        setting_name = str(setting)
        for source_name, column in NEWS_COLUMNS.items():
            daily_count = group[column].eq("Every day").sum()
            source_by_setting_rows.append(
                {
                    "urban_rural": setting_name,
                    "source": source_name,
                    "respondents": daily_count,
                    "share": daily_count / len(group) * 100,
                }
            )

        traditional_count = group[TRADITIONAL_NEWS_COLUMNS].eq("Every day").any(axis=1).sum()
        digital_count = group[DIGITAL_NEWS_COLUMNS].eq("Every day").any(axis=1).sum()
        digital_setting_shares[setting_name] = digital_count / len(group) * 100

        media_group_rows.extend(
            [
                {
                    "urban_rural": setting_name,
                    "Media group": "Traditional News",
                    "respondents": traditional_count,
                    "share": traditional_count / len(group) * 100,
                },
                {
                    "urban_rural": setting_name,
                    "Media group": "Digital News",
                    "respondents": digital_count,
                    "share": digital_count / len(group) * 100,
                },
            ]
        )

    source_by_setting = pd.DataFrame(source_by_setting_rows)
    media_group_summary = pd.DataFrame(media_group_rows)

    digital_gap = None
    if {"Urban", "Rural"}.issubset(digital_setting_shares):
        digital_gap = digital_setting_shares["Urban"] - digital_setting_shares["Rural"]

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Top Daily News Source", top_daily["source"])
    with metric_col2:
        st.metric("Daily Usage of Top News Source", format_pct(top_daily["Daily use"]))
    with metric_col3:
        st.metric("Daily Digital News Reach", format_pct(digital_daily_share))


    chart_data = pd.DataFrame(
        [
            {
                "source": row["source"],
                "Frequency": "Daily use",
                "Share": row["Daily use"],
                "respondents": row["Daily respondents"],
            }
            for _, row in news_summary.iterrows()
        ]
        + [
            {
                "source": row["source"],
                "Frequency": "At least weekly",
                "Share": row["At least weekly"],
                "respondents": row["Weekly respondents"],
            }
            for _, row in news_summary.iterrows()
        ]
    )

    left, right = st.columns([1.05, 1])
    with left:
        fig = px.bar(
            chart_data,
            x="Share",
            y="source",
            color="Frequency",
            orientation="h",
            barmode="group",
            title="Daily and Weekly News Reach",
            labels={"source": "News source", "Share": "Share of respondents (%)"},
            category_orders={
                "source": news_summary["source"].tolist()[::-1],
                "Frequency": ["Daily use", "At least weekly"],
            },
            color_discrete_map=NEWS_FREQUENCY_COLORS,
            custom_data=["Frequency", "respondents", "Share"],
        )
        fig.update_traces(
            hovertemplate=(
                "News source: %{y}<br>"
                "Frequency: %{customdata[0]}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Share: %{customdata[2]:.1f}%<extra></extra>"
            )
        )
        fig.update_xaxes(range=[0, 100])
        st.plotly_chart(standard_layout(fig, height=410), use_container_width=True)

    with right:
        fig = px.bar(
            source_by_setting,
            x="source",
            y="share",
            color="urban_rural",
            barmode="group",
            title="Daily News Use by Setting",
            labels={
                "source": "News source",
                "share": "Share of respondents (%)",
                "urban_rural": "Setting",
            },
            color_discrete_map=SETTING_COLOR_MAP,
            custom_data=["urban_rural", "respondents", "share"],
        )
        fig.update_traces(
            hovertemplate=(
                "News source: %{x}<br>"
                "Setting: %{customdata[0]}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Daily use: %{customdata[2]:.1f}%<extra></extra>"
            )
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(standard_layout(fig, height=410), use_container_width=True)

    left, right = st.columns([1.05, 1])
    with left:
        fig = px.bar(
            media_group_summary,
            x="urban_rural",
            y="share",
            color="Media group",
            barmode="group",
            title="Traditional vs Digital Daily Reach",
            labels={
                "urban_rural": "Setting",
                "share": "Share of respondents (%)",
                "Media group": "Media group",
            },
            color_discrete_map=MEDIA_GROUP_COLORS,
            custom_data=["Media group", "respondents", "share"],
        )
        fig.update_traces(
            hovertemplate=(
                "Setting: %{x}<br>"
                "Media group: %{customdata[0]}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Daily reach: %{customdata[2]:.1f}%<extra></extra>"
            )
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(standard_layout(fig, height=390), use_container_width=True)

    with right:
        county_rows = []
        for county, group in data.groupby("county_map"):
            county_digital = group[DIGITAL_NEWS_COLUMNS].eq("Every day").any(axis=1)
            county_rows.append(
                {
                    "county": county,
                    "respondents": int(county_digital.sum()),
                    "share": county_digital.mean() * 100,
                    "sample": len(group),
                }
            )
        county_news = (
            pd.DataFrame(county_rows)
            .sort_values("share", ascending=False)
            .head(12)
            .sort_values("share")
        )

        fig = px.bar(
            county_news,
            x="share",
            y="county",
            orientation="h",
            title="Highest Daily Digital News Reach by County",
            labels={"county": "County", "share": "Share of respondents (%)"},
            custom_data=["respondents", "sample", "share"],
        )
        fig.update_traces(
            marker_color=MEDIA_GROUP_COLORS["Digital News"],
            hovertemplate=(
                "County: %{y}<br>"
                "Daily digital news respondents: %{customdata[0]:,}<br>"
                "Filtered county respondents: %{customdata[1]:,}<br>"
                "Daily digital reach: %{customdata[2]:.1f}%<extra></extra>"
            ),
        )
        fig.update_xaxes(range=[0, 100])
        st.plotly_chart(standard_layout(fig, height=390), use_container_width=True)


def render_data_table(data: pd.DataFrame):
    st.subheader("Filtered Data Table")
    st.dataframe(
        data.drop(columns=["county_map"]),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.download_button(
        "Download filtered data",
        data.drop(columns=["county_map"]).to_csv(index=False).encode("utf-8"),
        file_name="kenya_dashboard_filtered_data.csv",
        mime="text/csv",
    )


# 9. General Helper Functions
# These helper functions are used by several different charts and keep repeated
# formatting or calculations code out of the main dashboard flow.

def sorted_values(data: pd.DataFrame, column: str) -> list[str]:
    return sorted(data[column].dropna().astype(str).unique().tolist())


def format_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def format_pp(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} pp"


def short_text(value: str, limit: int = 28) -> str:
    if not isinstance(value, str):
        return "N/A"
    return value if len(value) <= limit else value[: limit - 3] + "..."


def party_acronym(value: str) -> str:
    if not isinstance(value, str) or value == "N/A":
        return "N/A"

    known_acronyms = {
        "Amani National Congress": "ANC",
        "Maendeleo Chap Chap": "MCC",
        "National Rainbow Coalition": "NARC",
        "NARC": "NARC-K",
    }

    if "(" in value and ")" in value:
        return value.split("(")[-1].split(")")[0].replace("–", "-")

    for party_name, acronym in known_acronyms.items():
        if value.startswith(party_name):
            return acronym

    return short_text(value, limit=12)


def category_color(value: str, fallback_index: int = 0) -> str:
    text = str(value)
    for party_name, color in PARTY_COLOR_OVERRIDES.items():
        if text.startswith(party_name):
            return color
    return COLORS[fallback_index % len(COLORS)]


def color_map_for(values: pd.Series | list[str]) -> dict[str, str]:
    unique_values = pd.Series(values).dropna().astype(str).unique().tolist()
    return {
        value: category_color(value, index)
        for index, value in enumerate(sorted(unique_values))
    }


def ordered_party_legend_values(values: pd.Series | list[str]) -> list[str]:
    unique_values = pd.Series(values).dropna().astype(str).unique().tolist()
    ordered = []
    for party_name in PARTY_MAP_LEGEND_ORDER:
        ordered.extend(
            value
            for value in unique_values
            if value.startswith(party_name) and value not in ordered
        )
    ordered.extend(sorted(value for value in unique_values if value not in ordered))
    return ordered


def top_value(values: pd.Series) -> str:
    counts = values.dropna().value_counts()
    return counts.index[0] if not counts.empty else "N/A"


def standard_layout(fig, height: int = 390):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=48, b=10),
        legend_title_text="",
        colorway=COLORS,
        font=dict(size=13),
    )
    return fig


def count_table(data: pd.DataFrame, column: str, top_n: int | None = None) -> pd.DataFrame:
    table = (
        data[column]
        .value_counts(dropna=False)
        .rename_axis(column)
        .reset_index(name="respondents")
    )
    if column == "education_grouped":
        extra_categories = sorted(
            value for value in table[column].astype(str).unique()
            if value not in EDUCATION_ORDER
        )
        education_sort_order = {
            value: index
            for index, value in enumerate(EDUCATION_ORDER + extra_categories)
        }
        table = table.sort_values(
            by=column,
            key=lambda values: values.astype(str).map(education_sort_order),
        )
    if top_n:
        table = table.head(top_n)
    total = table["respondents"].sum()
    table["share"] = table["respondents"] / total * 100 if total else 0
    return table


def bar_chart(
    data: pd.DataFrame,
    column: str,
    title: str,
    top_n: int | None = None,
    horizontal: bool = False,
    share: bool = False,
):
    table = count_table(data, column, top_n)
    value_col = "share" if share else "respondents"
    value_label = "Share (%)" if share else "Respondents"

    if horizontal:
        table = table.sort_values(value_col, ascending=True)
        fig = px.bar(
            table,
            x=value_col,
            y=column,
            color=column,
            orientation="h",
            title=title,
            labels={value_col: value_label, column: ""},
            color_discrete_map=color_map_for(table[column]),
            custom_data=[column, "respondents", "share"],
        )
        fig.update_traces(
            hovertemplate=(
                f"{column.replace('_', ' ').title()}: %{{customdata[0]}}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Share: %{customdata[2]:.1f}%<extra></extra>"
            )
        )
    else:
        fig = px.bar(
            table,
            x=column,
            y=value_col,
            color=column,
            title=title,
            labels={value_col: value_label, column: ""},
            color_discrete_map=color_map_for(table[column]),
            custom_data=[column, "respondents", "share"],
        )
        fig.update_xaxes(tickangle=-25)
        fig.update_traces(
            hovertemplate=(
                f"{column.replace('_', ' ').title()}: %{{customdata[0]}}<br>"
                "Respondents: %{customdata[1]:,}<br>"
                "Share: %{customdata[2]:.1f}%<extra></extra>"
            )
        )

    fig.update_layout(showlegend=False)
    return standard_layout(fig)


if __name__ == "__main__":
    main()
