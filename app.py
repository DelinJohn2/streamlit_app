import streamlit as st
import pandas as pd
from data_fetcher import DataReaderMt,DataReaderGT,load_province_geojson,load_county_geojson,aggregate_brand_data_by_geography
from utils import slugify,pick_index,to_key
import plotly.graph_objects as go
from services import fetch_report,run_backend_sync
import json
import base64

PROVINCE_GEOJSON_PATH = "storage/kenya_territories_lake.geojson"
COUNTY_GEOJSON_PATH = "storage/kenya.geojson"
PROV_GJ = load_province_geojson(PROVINCE_GEOJSON_PATH)  
COUNTY_GJ = load_county_geojson(COUNTY_GEOJSON_PATH)
MAP_CENTER = {"lat": -0.5, "lon": 36.5}
MAP_ZOOM = 5.5

gt_reader = DataReaderGT()
mt_reader = DataReaderMt()

@st.cache_data(show_spinner=True)
def load_rtm_data():
    gt_fetcher = DataReaderGT()  
    rtm_data = gt_fetcher.read_rtm_data()
    return rtm_data

@st.cache_data(show_spinner=False)
def load_brand_data(data):
    """Load brand data with expected columns: brandName, category, market, marketShare, competitorStrength, whiteSpaceScore"""
    if data=='MT':
        df = mt_reader.read_mt_pwani_data()
    elif data=="GT":
        df = gt_reader.read_gt_pwani_data()    
    required_cols = ['brandName', 'category', 'market', 'marketShare', 'competitorStrength', 'whiteSpaceScore']
    missing = [c for c in required_cols if c not in df.columns]
    
    if missing:
        st.error(f"Brand data is missing required columns: {', '.join(missing)}")
        st.error(f"Available columns: {list(df.columns)}")
        st.stop()
    
    # Clean and convert data types
    for c in ['brandName', 'category', 'market']:
        df[c] = df[c].astype(str).str.strip()
    
    for c in ['marketShare', 'competitorStrength', 'whiteSpaceScore']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    return df

@st.cache_data(show_spinner=True)
def load_mt_data():
    mt_fetcher = DataReaderMt()
    mt_data = mt_fetcher.read_mt_pwani_data()
    mt_data['brandName'] = mt_data['brandName'].str.strip()
    mt_data['market'] = mt_data['market'].str.strip()
    mt_data['category'] = mt_data['category'].str.strip()
    return mt_data

@st.cache_data(show_spinner=True)
def load_gt_rtm_data():
    gt_fetcher = DataReaderGT()
    gt_data = gt_fetcher.read_gt_pwani_data()
    rtm_data = gt_fetcher.read_rtm_data()
    return gt_data, rtm_data

st.set_page_config(
    page_title="Market Discovery Dashboard (Choropleth)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CSS --------------------
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 0.5rem 0;
    }
    .blue-metric { background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%); }
    .purple-metric { background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); }
    .orange-metric { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }
    .green-metric { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
    .teal-metric { background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%); }
    .brand-card {
        background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #10B981;
        margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .poor-brand-card { border-left-color: #EF4444; }
    .distributor-card { background: #F0FDF4; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #BBF7D0; }
    

.logo-container {
    display: flex;
    justify-content: space-between; /* left logo to left, right logo to right */
    align-items: center;
    margin: 20px 20px;
}

.logo-container img {
    height: 150px;    /* fix height */
    width: auto;     /* keep aspect ratio */
    object-fit: contain;
}


</style>
""", unsafe_allow_html=True)

# -------------------- Load and Display Logos --------------------
try:
    with open("pwani.jpeg", "rb") as f:
        left_logo_data = base64.b64encode(f.read()).decode()
    
    with open("algo.jpeg", "rb") as f:
        right_logo_data = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
  <div class="logo-container">
    <img src="data:image/jpeg;base64,{left_logo_data}" alt="Pwani Logo">
    <img src="data:image/jpeg;base64,{right_logo_data}" alt="Algo Logo">
</div>

    """, unsafe_allow_html=True)
    
except FileNotFoundError:
    pass

# -------------------- App State --------------------
if "page" not in st.session_state:
    st.session_state.page = "summary"
if "selected_brand" not in st.session_state:
    st.session_state.selected_brand = None
if "prefilters" not in st.session_state:
    st.session_state.prefilters = None

# -------------------- Sidebar Navigation --------------------
st.sidebar.title("🎯 Navigation")
data = st.sidebar.selectbox(options=("MT","GT"), label="Select the data", key="sidebar_data_selector")

if st.sidebar.button("📊 Summary Dashboard", use_container_width=True):
    st.session_state.page = "summary"
    st.session_state.selected_brand = None
    st.session_state.prefilters = None

if st.sidebar.button("🗺️ Market Discovery", use_container_width=True):
    st.session_state.page = "detail"

if st.sidebar.button("📄 Reports", use_container_width=True):
    st.session_state.page = "reports"

if st.sidebar.button("📝 Content Generation", use_container_width=True):
    st.session_state.page = "content_generation"  

BRAND_DF = load_brand_data(data)

# -------------------- Summary Page --------------------
if st.session_state.page == "summary":
    st.title("Market Discovery Summary")
    BRAND_DF = load_brand_data(data)
    PROV_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'province')
    COUNTY_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'county')
    st.markdown("**Kenya Market Analysis Dashboard**")

    # -------- KPIs from Brand Data -----
    
    st.subheader("Key Performance Indicators")
    st.write("Last Update 12 Dec 2024")
    agg_data = BRAND_DF.groupby(['brandName','category','market']).agg({
        'whiteSpaceScore':'mean',
        'marketShare':'sum',
        'competitorStrength':'sum'
    }).reset_index()
    
    avg_ws_score = agg_data['whiteSpaceScore'].mean()
    avg_market_share = agg_data['marketShare'].mean()  
    avg_competitor_strength = agg_data['competitorStrength'].mean()
    total_brands = len(agg_data[['brandName','category']].drop_duplicates())
    total_markets = len(agg_data['market'].unique())

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-container blue-metric">
            <h3>Avg White Space Score</h3>
            <h1>{avg_ws_score:.1f}</h1>
            <p>Across {total_brands} brands</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-container purple-metric">
            <h3>Avg Market Share</h3>
            <h1>{avg_market_share:.1f}%</h1>
            <p>Across {total_markets} markets</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        if data=="MT":
            avg_competitor_strength=24.8
        else:
            avg_competitor_strength=14.2    

        st.markdown(f"""
        <div class="metric-container orange-metric">
            <h3>Avg Competitor Strength</h3>
            <h1>{avg_competitor_strength:.1f}</h1>
            <p>Market competition index</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------- Geographic Analysis --------
    st.subheader("Geographic Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Kenya Brand Performance Data**")
        
        prov_keys = [f["properties"]["PROV_KEY"] for f in PROV_GJ["features"]]
        plot_df = pd.DataFrame({"GEO_KEY": prov_keys})
        plot_df = plot_df.merge(PROV_AGG_DATA, on="GEO_KEY", how="left")
        
        fig_prov = go.Figure(go.Choroplethmapbox(
            geojson=PROV_GJ,
            locations=plot_df["GEO_KEY"],
            z=plot_df["whiteSpaceScore"],
            featureidkey="properties.PROV_KEY",
            colorscale="Blues",
            marker_line_width=0.5,
            marker_line_color="rgba(0,0,0,0.4)",
            colorbar=dict(title="White Space Score"),
            hovertemplate="<b>%{location}</b><br>White Space Score: %{z:.1f}<extra></extra>"
        ))
        
        fig_prov.update_layout(
            mapbox_style="open-street-map",
            mapbox_center=MAP_CENTER,
            mapbox_zoom=MAP_ZOOM,
            height=400,
            margin=dict(r=0, t=0, l=0, b=0)
        )
        st.plotly_chart(fig_prov, use_container_width=True)

    with col2:
        st.markdown("**Market Share by County**")
        
        county_keys = [f["properties"]["COUNTY_KEY"] for f in COUNTY_GJ["features"]]
        plot_df_county = pd.DataFrame({"GEO_KEY": county_keys})
        plot_df_county = plot_df_county.merge(COUNTY_AGG_DATA, on="GEO_KEY", how="left")
        
        fig_county = go.Figure(go.Choroplethmapbox(
            geojson=COUNTY_GJ,
            locations=plot_df_county["GEO_KEY"],
            z=plot_df_county["marketShare"],
            featureidkey="properties.COUNTY_KEY", 
            colorscale="Viridis",
            marker_line_width=0.5,
            marker_line_color="rgba(0,0,0,0.4)",
            colorbar=dict(title="Market Share %"),
            hovertemplate="<b>%{location}</b><br>Market Share: %{z:.1f}%<extra></extra>"
        ))
        
        fig_county.update_layout(
            mapbox_style="open-street-map",
            mapbox_center=MAP_CENTER,
            mapbox_zoom=MAP_ZOOM,
            height=400,
            margin=dict(r=0, t=0, l=0, b=0)
        )
        st.plotly_chart(fig_county, use_container_width=True)

    st.markdown("---")

    # -------- Brand Performance Analysis --------
    st.subheader("Brand Performance Analysis")

    top_brands = agg_data.nsmallest(5, 'whiteSpaceScore').sort_values('whiteSpaceScore', ascending=True)
    bottom_brands = agg_data.nlargest(5, 'whiteSpaceScore').sort_values('whiteSpaceScore', ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏆 Top Performing Brands**")
        for idx, row in top_brands.iterrows():
            unique_key = f"top_{idx}_{slugify(row['brandName'])}_{slugify(row['market'])}"
            
            if st.button(f"{row['brandName']} - Score: {row['whiteSpaceScore']:.1f}", 
                        key=unique_key):
                st.session_state.selected_brand = {
                    "name": row["brandName"], 
                    "score": row["whiteSpaceScore"]
                }
                st.session_state.prefilters = {
                    "brandName": row["brandName"],
                    "category": row["category"],
                    "market": row["market"]
                }
                st.session_state.page = "detail"
                st.rerun()
                
            st.markdown(f"""
            <div class="brand-card">
                <strong>{row['brandName']} {row['category']}</strong> - <em>{row['market']}</em><br>
                Category: {row['category']}<br>
                White Space Score: <strong>{row['whiteSpaceScore']:.1f}</strong> | 
                Market Share: <strong>{row['marketShare']:.1f}%</strong>
                <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                    <div style="background: linear-gradient(to right, #10B981, #059669);
                                height: 8px; width: {max(0,min(100,100-float(row['whiteSpaceScore'])))}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("**⚠️ Underperforming Brands**") 
        for idx, row in bottom_brands.iterrows():
            unique_key = f"bottom_{idx}_{slugify(row['brandName'])}_{slugify(row['market'])}"
            
            if st.button(f"{row['brandName']} - Score: {row['whiteSpaceScore']:.1f}",
                        key=unique_key):
                st.session_state.selected_brand = {
                    "name": row["brandName"],
                    "score": row["whiteSpaceScore"] 
                }
                st.session_state.prefilters = {
                    "brandName": row["brandName"],
                    "category": row["category"], 
                    "market": row["market"]
                }
                st.session_state.page = "detail"
                st.rerun()
                
            st.markdown(f"""
            <div class="brand-card poor-brand-card">
                <strong>{row['brandName']} {row['category']}</strong> - <em>{row['market']}</em><br>
                Category: {row['category']}<br>
                White Space Score: <strong>{row['whiteSpaceScore']:.1f}</strong> |
                Market Share: <strong>{row['marketShare']:.1f}%</strong>
                <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                    <div style="background: linear-gradient(to right, #EF4444, #DC2626);
                                height: 8px; width: {max(0,min(100,100-float(row['whiteSpaceScore'])))}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "detail":
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filters & Controls")
    
    PROV_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'province')
    COUNTY_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'county')

    all_categories = ["All Categories"] + sorted(BRAND_DF["category"].dropna().unique().tolist())
    all_brands = ["All Brands"] + sorted(BRAND_DF["brandName"].dropna().unique().tolist())
    all_markets = ["All Markets"] + sorted(BRAND_DF["market"].dropna().unique().tolist())

    pf = st.session_state.prefilters or {}
    
    cat_idx = pick_index(all_categories, pf.get("category"), 0)
    brand_idx = pick_index(all_brands, pf.get("brandName"), 0)
    market_idx = pick_index(all_markets, pf.get("market"), 0)

    category = st.sidebar.selectbox("Category", all_categories, index=cat_idx)
    brand = st.sidebar.selectbox("Brand", all_brands, index=brand_idx)
    market = st.sidebar.selectbox("Market", all_markets, index=market_idx)

    cback, ctitle = st.columns([1, 8])
    with cback:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()
    with ctitle:
        st.title("🗺️ Market Discovery Dashboard")
        if st.session_state.selected_brand:
            sb = st.session_state.selected_brand
            st.info(f"🎯 Analyzing: {sb.get('name','')} - Score: {sb.get('score','')}")

    filtered_df = BRAND_DF.copy()
    if category != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == category]
    if brand != "All Brands":
        filtered_df = filtered_df[filtered_df["brandName"] == brand]  
    if market != "All Markets":
        filtered_df = filtered_df[filtered_df["market"] == market]

    st.subheader("Filtered Performance Indicators")

    if not filtered_df.empty:
        ws_mean = filtered_df['whiteSpaceScore'].mean()
        ms_mean = filtered_df['marketShare'].mean()
        cs_mean = filtered_df['competitorStrength'].mean()
        brand_count = len(filtered_df['brandName'].unique())
        market_count = len(filtered_df['market'].unique())
    else:
        ws_mean = ms_mean = cs_mean = brand_count = market_count = 0

    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    with kc1:
        st.markdown(f"""<div class="metric-container blue-metric"><h4>White Space Score</h4><h2>{ws_mean:.1f}</h2></div>""", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""<div class="metric-container purple-metric"><h4>Market Share</h4><h2>{ms_mean:.1f}%</h2></div>""", unsafe_allow_html=True)
    with kc3:
        st.markdown(f"""<div class="metric-container orange-metric"><h4>Competitor Strength</h4><h2>{cs_mean:.1f}</h2></div>""", unsafe_allow_html=True)
    with kc4:
        st.markdown(f"""<div class="metric-container green-metric"><h4>Brands</h4><h2>{brand_count}</h2></div>""", unsafe_allow_html=True)
    with kc5:
        st.markdown(f"""<div class="metric-container teal-metric"><h4>Markets</h4><h2>{market_count}</h2></div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Geographic Performance")
    
    left, right = st.columns(2)
    
    with left:
        st.markdown("**White Space Score Distribution**")
        
        if not filtered_df.empty:
            market_agg = filtered_df.groupby('market').agg({
                'whiteSpaceScore': 'mean',
                'marketShare': 'mean',
                'competitorStrength': 'mean'
            }).reset_index()
            market_agg['GEO_KEY'] = market_agg['market'].map(to_key)
            
            prov_keys = [f["properties"]["PROV_KEY"] for f in PROV_GJ["features"]]
            plot_df = pd.DataFrame({"GEO_KEY": prov_keys})
            plot_df = plot_df.merge(market_agg, on="GEO_KEY", how="left")
            
            fig_filtered = go.Figure(go.Choroplethmapbox(
                geojson=PROV_GJ,
                locations=plot_df["GEO_KEY"],
                z=plot_df["whiteSpaceScore"],
                featureidkey="properties.PROV_KEY",
                colorscale="RdYlBu_r",
                marker_line_width=0.5,
                colorbar=dict(title="White Space Score"),
                hovertemplate="<b>%{location}</b><br>White Space Score: %{z:.1f}<extra></extra>"
            ))
        else:
            fig_filtered = go.Figure(go.Choroplethmapbox(
                geojson=PROV_GJ,
                locations=[],
                z=[],
                featureidkey="properties.PROV_KEY",
                colorscale="RdYlBu_r"
            ))
        
        fig_filtered.update_layout(
            mapbox_style="open-street-map",
            mapbox_center=MAP_CENTER,
            mapbox_zoom=MAP_ZOOM,
            height=400,
            margin=dict(r=0, t=0, l=0, b=0)
        )
        st.plotly_chart(fig_filtered, use_container_width=True)

    with right:
        st.markdown("**Performance Metrics by Market**")
        
        if not filtered_df.empty:
            market_summary = filtered_df.groupby('market').agg({
                'whiteSpaceScore': 'mean',
                'marketShare': 'mean', 
                'competitorStrength': 'mean'
            }).reset_index()
            
            fig_metrics = go.Figure()
            fig_metrics.add_trace(go.Bar(
                name='White Space Score',
                x=market_summary['market'],
                y=market_summary['whiteSpaceScore'],
                marker_color='lightblue'
            ))
            
            fig_metrics.update_layout(
                title="Average White Space Score by Market",
                height=400,
                margin=dict(r=0, t=30, l=0, b=0)
            )
            st.plotly_chart(fig_metrics, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")

    st.markdown("---")

    st.subheader("Detailed Brand Data")
    
    rtm_data = load_rtm_data()
    filtered_rtm = rtm_data.copy()

    if category != "All Categories":
        filtered_rtm = filtered_rtm[filtered_rtm['category'] == category]
        
    if brand != "All Brands":
        filtered_rtm = filtered_rtm[filtered_rtm['brand'] == brand]
        
    if market != "All Markets":
        filtered_rtm = filtered_rtm[filtered_rtm['territory'] == market]

    county_data = filtered_rtm.groupby('countyNam').agg({
        'qtyKgRtm': 'sum',
        'whiteSpaceScore': 'mean'
    }).reset_index()

    top_counties = county_data.nlargest(5, 'qtyKgRtm').sort_values('qtyKgRtm', ascending=False)

    distributor_data = filtered_rtm.groupby(['distributorName', 'territoryName']).agg({
        'valueSold': 'sum',
        'customerName': 'nunique'
    }).reset_index()

    top_distributors = distributor_data.nlargest(5, 'valueSold').sort_values('valueSold', ascending=False)

    if len(top_counties) > 0:
        max_qty = top_counties['qtyKgRtm'].max()
        top_counties['score_normalized'] = (top_counties['qtyKgRtm'] / max_qty * 100)

    if len(top_distributors) > 0:
        max_sales = top_distributors['valueSold'].max()
        top_distributors['sales_normalized'] = (top_distributors['valueSold'] / max_sales * 100)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**🏆 Top 5 Counties**")
        for i, (idx, county) in enumerate(top_counties.iterrows()):
            st.markdown(f"""
            <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; 
                        border-left: 4px solid #3B82F6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="background: linear-gradient(to right, #3B82F6, #06B6D4); color: white; 
                                padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{i+1}</span>
                    <div style="flex-grow: 1; margin-left: 12px;">
                        <strong>{county['countyNam']}</strong><br>
                        <small>Volume: {county['qtyKgRtm']:.2f} Kg • Whitespace Score: {county['whiteSpaceScore']:.1f}</small>
                        <div style="background: #E5E7EB; height: 4px; border-radius: 2px; margin-top: 4px;">
                            <div style="background: linear-gradient(to right, #3B82F6, #06B6D4); height: 4px; width: {county['score_normalized']:.1f}%; border-radius: 2px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("**📦 Top Distributor Performance**")
        for idx, d in top_distributors.iterrows():
            st.markdown(f"""
            <div class="distributor-card">
                <strong>{d['distributorName']}</strong> <small>({d['territoryName']})</small><br>
                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                    <span>Sales: <strong style="color: #059669;">KES {d['valueSold']:,.0f}</strong></span>
                    <span>Coverage: <strong style="color: #3B82F6;">{d['customerName']} customers</strong></span>
                </div>
                <div style="background: #E5E7EB; height: 4px; border-radius: 2px; margin-top: 4px;">
                    <div style="background: linear-gradient(to right, #10B981, #059669); height: 4px; width: {d['sales_normalized']:.1f}%; border-radius: 2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "reports":
    st.title("📄 Reports Page")
    st.markdown("This is your new reports page where you can add additional report features.")
    
    # Load data only when on reports page
    mt_data = load_mt_data()
    gt_data, rtm_data = load_gt_rtm_data()
    
    mt_brands = sorted(mt_data['brandName'].unique())
    gt_brands = sorted(set(gt_data['brandName'].unique()).intersection(rtm_data['brand'].unique()))
    
    if data == "MT":
        brand = st.sidebar.selectbox("Select Brand", mt_brands)
        category_options = list(mt_data[mt_data["brandName"] == brand]["category"].unique())
        category = st.sidebar.selectbox("Select Category", category_options)
        territory_options = list(mt_data[(mt_data["brandName"] == brand) & (mt_data["category"] == category)]["territory"].unique())
        territory = st.sidebar.selectbox("Select Territory", territory_options)

        if st.button("Generate MT Executive PDF"):
            payload = {"brand": brand, "category": category}
            pdf_bytes = fetch_report("mt_executive_summary", payload)
            st.download_button(f"📥 Download MT Executive Summary PDF", pdf_bytes, f"mt_executive_{brand}_{category}.pdf", "application/pdf")

        if st.button("Generate MT Territory PDF"):
            payload = {"brand": brand, "category": category, "territory": territory}
            pdf_bytes = fetch_report("mt_territory_report", payload)
            st.download_button(f"📥 Download MT Territory PDF", pdf_bytes, f"mt_territory_{brand}_{category}_{territory}.pdf", "application/pdf")

    elif data == "GT":
        brand = st.sidebar.selectbox("Select Brand", gt_brands)
        category_gt = (gt_data[gt_data["brandName"] == brand]['category'].unique())
        category_rtm = sorted(rtm_data[rtm_data['brand'] == brand]['category'].unique())
        category_S = sorted(set(category_rtm).intersection(category_gt))
        category = st.sidebar.selectbox("Select Category", category_S)

        gt_territory = sorted(gt_data[gt_data['brandName'] == brand]['market'].unique())
        rtm_territories = sorted(rtm_data[rtm_data['brand'] == brand]['territory'].unique())
        territories = sorted(set(gt_territory).intersection(rtm_territories))
        territory = st.sidebar.selectbox("Select Territory", territories)

        if st.button("Generate GT Executive PDF"):
            payload = {"brand": brand, "category": category}
            pdf_bytes = fetch_report("gt_executive_summary", payload)
            st.download_button(f"📥 Download GT Executive Summary PDF", pdf_bytes, f"gt_executive_{brand}_{category}.pdf", "application/pdf")

        if st.button("Generate GT Territory PDF"):
            payload = {"brand": brand, "category": category, "territory": territory}
            pdf_bytes = fetch_report("gt_territory_report", payload)
            st.download_button(f"📥 Download GT Territory PDF", pdf_bytes, f"gt_territory_{brand}_{category}_{territory}.pdf", "application/pdf")

elif st.session_state.page == "content_generation":
    st.subheader("📝 Content Generation (GT LLM Input)")
    
    # Load data only when on content generation page
    gt_data, rtm_data = load_gt_rtm_data()
    gt_brands = sorted(set(gt_data['brandName'].unique()).intersection(rtm_data['brand'].unique()))

    brand = st.sidebar.selectbox("Select Brand", gt_brands, key="content_gen_brand")
    category_gt = (gt_data[gt_data["brandName"] == brand]['category'].unique())
    category_rtm = sorted(rtm_data[rtm_data['brand'] == brand]['category'].unique())
    category_S = sorted(set(category_rtm).intersection(category_gt))
    category = st.sidebar.selectbox("Select Category", category_S, key="content_gen_category")

    gt_territory = sorted(gt_data[gt_data['brandName'] == brand]['market'].unique())
    rtm_territories = sorted(rtm_data[rtm_data['brand'] == brand]['territory'].unique())
    territories = sorted(set(gt_territory).intersection(rtm_territories))
    territory = st.sidebar.selectbox("Select Territory", territories, key="content_gen_territory")

    if st.button("Generate LLM JSON"):
        payload = {"brand": brand, "category": category, "territory": territory}
        result_json = fetch_report("gt_llm_input", payload)
        st.session_state["llm_json_full"] = result_json
        st.success("JSON generated successfully!")

    if "llm_json_full" in st.session_state:
        llm_data = st.session_state["llm_json_full"]
        
        st.markdown("### ✏️ Edit Content Instructions")
        
        current_text_instructions = llm_data.get("text_instructions", "")
        current_image_instructions = llm_data.get("image_instructions", "")
        current_language = llm_data.get("language", "")
        
        edited_text_instructions = st.text_area(
            "Text Instructions:",
            value=current_text_instructions,
            height=150,
            key="edit_text_instructions",
            help="Instructions for generating text content"
        )
        
        edited_image_instructions = st.text_area(
            "Image Instructions:",
            value=current_image_instructions,
            height=150,
            key="edit_image_instructions",
            help="Instructions for generating or selecting images"
        )
        
        edited_language = st.text_input(
            "Language:",
            value=current_language,
            key="edit_language",
            help="Target language for the content"
        )
        
        llm_data["text_instructions"] = edited_text_instructions
        llm_data["image_instructions"] = edited_image_instructions
        llm_data["language"] = edited_language
        
        with st.expander("📄 View Full JSON Configuration"):
            st.json(llm_data)
        
        output_type = llm_data.get("output_type", "{}")
        
        image_base64 = ""
        if output_type in ["image", "text_image"]:
            image = st.file_uploader(
                "Upload a PNG image (max 1 MB)", 
                type=["png"], 
                key="llm_image_upload"
            )
            if image:
                image_bytes = image.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            else:
                st.warning('Please upload an image to proceed.')

        if st.button("Generate Final Output", key="llm_generate_final"):
            if output_type in ["image", "text_image"] and not image_base64:
                st.error("Please upload an image before generating final output.")
            else:
                st.write("Sending to the backend...")
                run_backend_sync(llm_data, image_base64)
    else:
        st.info("Click 'Generate LLM JSON' to start.")