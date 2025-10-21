# === MEA‑Wide Users – Naruto Chapter 2 Streamlit Dashboard ===
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MEA Users Dashboard",
                   layout="wide",
                   page_icon="🌍")

st.title("🌍 Overall MEA Users – Naruto Chapter 2 Dashboard")
st.markdown("""
Analyze **aggregate user activity and retention** for the whole MEA region,
without sub‑region breakdowns.
""")

# ---------------------------------------------------------------
# Load & clean data
# ---------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, skipinitialspace=True, thousands=",", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert percent columns
    pct_cols = [c for c in df.columns if df[c].astype(str).str.contains("%").any()]
    for c in pct_cols:
        df[c] = df[c].str.replace("%", "", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce") / 100

    # Numeric conversions
    num_cols = [c for c in df.columns if c not in ["Date"]]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

    # Year + pseudo date to overlay seasons
    df["Year"] = df["Date"].dt.year
    df["MonthDay"] = pd.to_datetime("2000-" + df["Date"].dt.strftime("%m-%d"),
                                    errors="coerce")
    return df

df = load_data("ME_Users.csv")    # 👉 use the filename of your new dataset
st.write("✅ Data loaded:", df.shape)
st.dataframe(df, use_container_width=True, height=500)

# auto‑detect usable metric columns (non‑datetime, non‑object categories)
# exclude helper columns like 'Year', 'MonthDay' if you added them
# build metrics list automatically
drop_cols = ["Year", "MonthDay", "EO Month"]
metrics = [c for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c]) and c not in drop_cols]

metric = st.selectbox("Select Metric", metrics)

# ---------------------------------------------------------------
# Main plot
# ---------------------------------------------------------------
fig = px.line(
    df,
    x="MonthDay", y=metric, color="Year",
    hover_name="Date",
    title=f"{metric} – Year‑over‑Year Trend (Overall MEA)",
    template="plotly_dark",
    color_discrete_sequence=px.colors.qualitative.Vivid,
    height=600
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
for ann in fig.layout.annotations:
    ann.font.color = "white"

fig.add_vrect(
x0="2000-01-10", x1="2000-02-09",
fillcolor="royalblue", opacity=0.2, line_width=0,
annotation_text="NB1 Period", annotation_position="top left",
annotation_font_color="white"
)

fig.add_vrect(x0="2000-07-30", x1="2000-08-31",
              fillcolor="orange", opacity=0.15, line_width=0,
              annotation_text="NB2 Period", annotation_position="top left")

st.plotly_chart(fig, use_container_width=True)
st.caption("Jan → Dec overlay by year; orange zone = 2025 Naruto Chapter 2 campaign.")