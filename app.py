import streamlit as st
import pandas as pd
import plotly.express as px
#import plotly.io as pio
# --- PAGE CONFIG ---
st.set_page_config(page_title="Nigeria CO₂ Emissions Analysis", page_icon="🌍", layout="wide")

# --- CUSTOM CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- HEADER ---
st.title(" Nigeria CO₂ Emissions Analysis")
st.markdown("""
**Hypothesis:** Nigeria’s per‑capita CO₂ emissions have grown more slowly than the global average since 2000, 
but electricity generation mix will be the key driver of future trends.

This app provides interactive visual insights.  
Behind the scenes: deeper analysis with **panel regressions** and **ML pipelines**.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔧 Controls")
year_range = st.sidebar.slider("Select Year Range", 1990, 2023, (2000, 2022))
compare_with = st.sidebar.selectbox("Compare Nigeria with:", ["World", "Ghana", "South Africa", "Kenya"])

# --- LOAD DATA ---
@st.cache_data
def load_co2():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    return pd.read_csv(url)

@st.cache_data
def load_energy():
    url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
    return pd.read_csv(url)

co2 = load_co2()
energy = load_energy()

# --- PREPARE DATA ---
nigeria_co2 = co2[co2["country"] == "Nigeria"][["year", "co2_per_capita"]]
peer_co2 = co2[co2["country"] == compare_with][["year", "co2_per_capita"]]

df_line = nigeria_co2.rename(columns={"co2_per_capita": "Nigeria"}).merge(
    peer_co2.rename(columns={"co2_per_capita": compare_with}), on="year", how="inner"
)
df_line = df_line[(df_line["year"] >= year_range[0]) & (df_line["year"] <= year_range[1])]

nigeria_energy = energy[energy["country"] == "Nigeria"][["year", "fossil_share_elec", "renewables_share_elec"]]
nigeria_energy = nigeria_energy[(nigeria_energy["year"] >= year_range[0]) & (nigeria_energy["year"] <= year_range[1])]

african_countries = [
    "Nigeria","South Africa","Egypt","Kenya","Ghana","Algeria","Morocco","Ethiopia","Tanzania","Uganda"
]
africa = co2[co2["country"].isin(african_countries)]
latest_year = africa["year"].max()
africa_latest = africa[africa["year"] == latest_year][["country","co2_per_capita"]].dropna()
top10_africa = africa_latest.sort_values("co2_per_capita", ascending=False).head(10)
# --- MERGE GDP & CO2 ---
# Merge GDP with CO₂
gdp = pd.read_csv("worldbank_gdp.csv")
gdp_co2 = gdp.merge(
    co2[["country","year","co2_per_capita"]],
    left_on=["Country Name","year"],
    right_on=["country","year"],
    how="inner"
)

st.subheader("GDP vs CO₂ emissions per capita (Nigeria vs peers)")
fig3 = px.scatter(
    gdp_co2[gdp_co2["Country Name"].isin(["Nigeria","South Africa","Ghana","Kenya","World"])],
    x="gdp_per_capita", y="co2_per_capita", color="Country Name",
    size="gdp_per_capita", hover_name="Country Name",
    title="GDP vs CO₂ emissions per capita"
)
# st.plotly_chart(fig3, use_container_width=True)

# --- CHARTS ---
st.header("📊 Charts")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Nigeria vs {compare_with} CO₂ emissions per capita")
    fig1 = px.line(
        df_line, x="year", y=[c for c in ["Nigeria", compare_with] if c in df_line.columns],
        markers=True, labels={"year": "Year", "value": "CO₂ per capita (t)"},
        title=f"CO₂ per capita: Nigeria vs {compare_with}"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Electricity generation mix (%)")
    fig2 = px.area(
        nigeria_energy, x="year",
        y=["fossil_share_elec", "renewables_share_elec"],
        labels={"value": "Share (%)", "year": "Year", "variable": "Source"},
        title="Nigeria electricity generation mix"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Top African countries by CO₂ per capita (latest year)")
fig4 = px.bar(
    top10_africa, x="country", y="co2_per_capita",
    labels={"country": "Country", "co2_per_capita": "CO₂ per capita (t)"},
    title=f"Top African emitters per capita ({latest_year})"
)
st.plotly_chart(fig4, use_container_width=True)


# Merge GDP with CO₂
gdp_co2 = gdp.merge(co2[["country","year","co2_per_capita"]],
                    left_on=["Country Name","year"],
                    right_on=["country","year"],
                    how="inner")

# Scatter plot
st.subheader("GDP vs CO₂ emissions per capita (Nigeria vs peers)")
fig3 = px.scatter(
    gdp_co2[gdp_co2["Country Name"].isin(["Nigeria","South Africa","Ghana","Kenya","World"])],
    x="gdp_per_capita", y="co2_per_capita", color="Country Name",
    size="gdp_per_capita", hover_name="Country Name",
    title="GDP vs CO₂ emissions per capita"
)
st.plotly_chart(fig3, use_container_width=True)

# --- Save chart as PNG ---
#pio.write_image(fig3, "assets/gdp_vs_co2.png", format="png", width=1000, height=600, scale=2)

# --- INSIGHTS ---
st.header("💡 Insights")
st.markdown("""
- Nigeria’s emissions trend is flatter than the global average 🌍  
- Fossil-heavy electricity mix remains the main driver ⚡  
- GDP growth shows weak correlation with emissions 📈  
- Regionally, Nigeria is mid-tier in per-capita emissions 🇳🇬  
""")

# --- CONCLUSION ---
st.header("✅ Conclusion")
st.markdown("""
This app is the interactive front‑end for hypothesis‑driven climate analysis.  
Deeper exploration continues with **panel regressions** and **ML pipelines** to quantify drivers and forecast scenarios.
""")

st.caption("Data sources: Our World in Data (CO₂ & Energy), World Bank (GDP).")
gdp = pd.read_csv("worldbank_gdp.csv")