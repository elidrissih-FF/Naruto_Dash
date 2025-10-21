# === Naruto Chapter 2 – Playtime / Match Mode Insights ===
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Playtime Dashboard", layout="wide", page_icon="🕹️")

st.title("🕹️ Game‑Mode Playtime Dashboard")
st.markdown("Explore **daily playtime and activity trends** for Battle Royale Ranked (BR) and Clash Squad Ranked (CS) during the Naruto Chapter 2 event.")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, skipinitialspace=True, thousands=",", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    pct_cols = [c for c in df.columns if df[c].astype(str).str.contains('%').any()] 
    for c in pct_cols:
        df[c] = df[c].str.replace('%','',regex=False).astype(float)/100
    num_cols = [c for c in df.columns if c not in ["Date","Region","Game Mode","Match Mode",
                                                   "Game Mode Id","Match Mode Id","Is Ugc"]]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["DisplayDate"] = pd.to_datetime("2000-" + df["Date"].dt.strftime("%m-%d"), errors="coerce")
    return df

df = load_data("modes_playtime.csv")
st.write("✅ Data loaded:", df.shape)
st.dataframe(df, use_container_width=True, height=600)
# Filters
regions = st.multiselect("Select Region(s)", df["Region"].unique(),
                         default=list(df["Region"].unique()))
modes = st.multiselect("Select Match Mode(s)", df["Match Mode"].unique(),
                       default=["Ranking Match","CS Ranking"])
metric = st.selectbox("Select Metric",
                      ["Avg Match Survival Time","Avg Survival Time",
                       "Avg Match Cnt","Participate Rate","Real Participate Rate","R2","R7"])

# Filter the dataframe
dff = df[(df["Region"].isin(regions)) & (df["Match Mode"].isin(modes))]

# Plot
fig = px.line(
    dff, x="DisplayDate", y=metric, color="Year",
    facet_col="Match Mode", facet_col_wrap=1,
    hover_name="Date", template="plotly_dark",
    color_discrete_sequence=px.colors.qualitative.Vivid,
    height=700 * len(regions),
    title=f"{metric} – Year‑over‑Year Overlay by Match Mode"
)
fig.update_xaxes(dtick="M1", tickformat="%b")
fig.update_layout(
    plot_bgcolor="#111111", paper_bgcolor="#111111",
    legend=dict(
            x=1.02, y=1, xanchor="left",
            font=dict(color="white")
        ),
    hovermode="closest"
)

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

st.plotly_chart(fig, use_container_width=True)
st.caption("Monthly overlay (Jan–Dec). Orange highlight = Naruto Chapter 2 campaign.")