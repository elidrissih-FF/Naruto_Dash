# === Naruto Chapter 2 Streamlit Dashboard ===
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------
# Page setup
st.set_page_config(page_title="Naruto Chapter 2 Campaign Dashboard",
                   layout="wide",
                   page_icon="🎮")

st.title("🎮 Naruto Chapter 2 – Interactive Dashboard")
st.markdown("Compare **multi‑year campaign performance** for each region and user metric.")

# ---------------------------------------------------------------
# Load & clean data
@st.cache_data
def load_data(csv):
    df = pd.read_csv(csv, skipinitialspace=True, thousands=",", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    pct_cols = [c for c in df.columns if df[c].astype(str).str.contains("%").any()]
    for c in pct_cols:
        df[c] = df[c].str.replace("%", "", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce") / 100
    num_cols = df.columns.drop(["Date", "Region"])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["MonthDay"] = pd.to_datetime(
        "2000-" + df["Date"].dt.strftime("%m-%d"), errors="coerce"
    )
    return df

df = load_data("nb2.csv")
st.write("✅ Data loaded:", df.shape)
st.dataframe(df, use_container_width=True, height=600)

# ---------------------------------------------------------------
# Selectors
regions = st.multiselect("Select Regions", options=df["Region"].unique(),
                         default=list(df["Region"].unique()))
metrics = [
    "A1", "A7", "A30", "AR2", "AR7", "AR30",
    "New User", "New User A7", "New User A30", "Retained 30", "Retained 7", "Revival 30 A30",
    "NU R2", "NU R7", "NU R30", "C7", "C30",
    "Revival7", "Revival30",
    "Revival7 R7", "Revival30 R7", "Revival30 R30",
    "C7 Rate", "Revival7 R2", "Revival7 R30", "C30 Rate"
]

years = st.multiselect("Select Year(s)",
                       sorted(df["Year"].unique()),
                       default=sorted(df["Year"].unique()))
metric = st.selectbox("Select Metric", metrics)

# ---------------------------------------------------------------
# Plot function
def make_plot(metric, label=None):
    dff = df[df["Region"].isin(regions) & df["Year"].isin(years)].copy()
    fig = px.line(
        dff, x="MonthDay", y=metric, color="Year",
        facet_col="Region", facet_col_wrap=1,
        hover_name="Date",
        title=label or metric,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        height=600 * len(regions)
    )
    fig.update_xaxes(dtick="M1", tickformat="%b", title=None)
    fig.update_yaxes(title=label or metric)
    fig.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        margin=dict(l=60, r=200, t=60, b=60),
        legend=dict(
            x=1.02, y=1, xanchor="left",
            font=dict(color="white")
        ),
        hovermode="closest"
    )
    # make every label/text white
    fig.update_layout(
        font=dict(color="white"),
        title_font_color="white",
        legend_font=dict(color="white"),
        paper_bgcolor="#111111",
        plot_bgcolor="#111111"
    )

    # axis labels & ticks
    fig.update_xaxes(title_font_color="white", tickfont_color="white")
    fig.update_yaxes(title_font_color="white", tickfont_color="white")

    # facet / subplot annotations (e.g. "Match Mode = Ranking Match")
    for ann in fig.layout.annotations:
        ann.font.color = "white"

    # shading annotation text (optional; safer in case theme defaulted to black)
    fig.update_annotations(font_color="white")
    fig.add_vrect(x0="2000-07-30", x1="2000-08-31",
                fillcolor="orange", opacity=0.15, line_width=0,
              annotation_text="NB2 Period", annotation_position="top left")
    fig.add_vrect(
    x0="2000-01-10", x1="2000-02-09",
    fillcolor="royalblue", opacity=0.2, line_width=0,
    annotation_text="NB1 Period", annotation_position="top left",
    annotation_font_color="white"
    )
    return fig

# ---------------------------------------------------------------
# Display
st.plotly_chart(make_plot(metric, f"{metric}‑Year‑over‑Year Overlay"), use_container_width=True)

st.caption("Data visualized by month (Jan → Dec) with an orange highlight for the 2025 Naruto Chapter 2 campaign.")