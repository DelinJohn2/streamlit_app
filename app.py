import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
from data_fetcher import DataReaderMt,DataReaderGT,load_province_geojson,load_county_geojson,aggregate_brand_data_by_geography
from utils import slugify,pick_index,to_key
import plotly.graph_objects as go


PROVINCE_GEOJSON_PATH = "storage/kenya_territories_lake.geojson"
COUNTY_GEOJSON_PATH = "storage/kenya.geojson"
PROV_GJ = load_province_geojson(PROVINCE_GEOJSON_PATH)  
COUNTY_GJ = load_county_geojson(COUNTY_GEOJSON_PATH)
MAP_CENTER = {"lat": -0.5, "lon": 36.5}
MAP_ZOOM = 5.5



gt_reader=DataReaderGT()
mt_reader=DataReaderMt()

@st.cache_data(show_spinner=False)
def load_brand_data(data):
    """Load brand data with expected columns: brandName, category, market, marketShare, competitorStrength, whiteSpaceScore"""
    if data=='MT':
        df=mt_reader.read_mt_pwani_data()
    elif data=="GT":
        df=gt_reader.read_gt_pwani_data()    
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



# -------------------- App State --------------------
if "page" not in st.session_state:
    st.session_state.page = "summary"
if "selected_brand" not in st.session_state:
    st.session_state.selected_brand = None
if "prefilters" not in st.session_state:
    st.session_state.prefilters = None

# -------------------- Sidebar Navigation --------------------
# -------------------- Sidebar Navigation --------------------
st.sidebar.title("🎯 Navigation")

if st.sidebar.button("📊 Summary Dashboard", use_container_width=True):
    st.session_state.page = "summary"
    st.session_state.selected_brand = None
    st.session_state.prefilters = None

if st.sidebar.button("🗺️ Market Discovery", use_container_width=True):
    st.session_state.page = "detail"

if st.sidebar.button("📄 Reports", use_container_width=True):
    st.session_state.page = "reports"

# -------------------- Summary Page --------------------
if st.session_state.page == "summary":
    st.title("📈 Market Discovery Summary")
    data=st.selectbox(options=("MT","GT"),label="Select the data")
    BRAND_DF = load_brand_data(data)
    PROV_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'province')
    COUNTY_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'county')
    st.markdown("**Kenya Market Analysis Dashboard**")

    # -------- KPIs from Brand Data --------
    st.subheader("Key Performance Indicators")
    
    # Calculate overall KPIs from brand data
    avg_ws_score = BRAND_DF['whiteSpaceScore'].mean()
    avg_market_share = BRAND_DF['marketShare'].mean()  
    avg_competitor_strength = BRAND_DF['competitorStrength'].mean()
    
    # Calculate growth (mock growth for demo - you'd need historical data for real growth)
    total_brands = len(BRAND_DF['brandName'].unique())
    total_markets = len(BRAND_DF['market'].unique())

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

    # Province-level choropleth
    with col1:
        st.markdown("**White Space Score by Province**")
        
        # Merge aggregated data with province geojson
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

    # County-level choropleth  
    with col2:
        st.markdown("**Market Share by County**")
        
        # Merge aggregated data with county geojson
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

    # Get top and bottom performing brands
    top_brands = BRAND_DF.nlargest(5, 'whiteSpaceScore')
    bottom_brands = BRAND_DF.nsmallest(5, 'whiteSpaceScore')

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏆 Top Performing Brands**")
        for idx, row in top_brands.iterrows():
            # Create unique key using index and brand name and market
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
                <strong>{row['brandName']}</strong> - <em>{row['market']}</em><br>
                Category: {row['category']}<br>
                White Space Score: <strong>{row['whiteSpaceScore']:.1f}</strong> | 
                Market Share: <strong>{row['marketShare']:.1f}%</strong>
                <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                    <div style="background: linear-gradient(to right, #10B981, #059669);
                                height: 8px; width: {max(0,min(100,float(row['whiteSpaceScore'])))}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("**⚠️ Underperforming Brands**") 
        for idx, row in bottom_brands.iterrows():
            # Create unique key using index and brand name and market
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
                <strong>{row['brandName']}</strong> - <em>{row['market']}</em><br>
                Category: {row['category']}<br>
                White Space Score: <strong>{row['whiteSpaceScore']:.1f}</strong> |
                Market Share: <strong>{row['marketShare']:.1f}%</strong>
                <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                    <div style="background: linear-gradient(to right, #EF4444, #DC2626);
                                height: 8px; width: {max(0,min(100,float(row['whiteSpaceScore'])))}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------- Detail Page --------------------

elif st.session_state.page == "detail":
    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filters & Controls")
    data=st.selectbox(options=("MT","GT"),label="Select the data")
    BRAND_DF = load_brand_data(data)
    PROV_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'province')
    COUNTY_AGG_DATA = aggregate_brand_data_by_geography(BRAND_DF, 'county')

    # Build filter options from actual data
    all_categories = ["All Categories"] + sorted(BRAND_DF["category"].dropna().unique().tolist())
    all_brands = ["All Brands"] + sorted(BRAND_DF["brandName"].dropna().unique().tolist())
    all_markets = ["All Markets"] + sorted(BRAND_DF["market"].dropna().unique().tolist())

    # Get prefilter values
    pf = st.session_state.prefilters or {}
    
    cat_idx = pick_index(all_categories, pf.get("category"), 0)
    brand_idx = pick_index(all_brands, pf.get("brandName"), 0)
    market_idx = pick_index(all_markets, pf.get("market"), 0)

    # Filter controls
    category = st.sidebar.selectbox("Category", all_categories, index=cat_idx)
    brand = st.sidebar.selectbox("Brand", all_brands, index=brand_idx)
    market = st.sidebar.selectbox("Market", all_markets, index=market_idx)

    # Page header
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

    # Apply filters
    filtered_df = BRAND_DF.copy()
    if category != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == category]
    if brand != "All Brands":
        filtered_df = filtered_df[filtered_df["brandName"] == brand]  
    if market != "All Markets":
        filtered_df = filtered_df[filtered_df["market"] == market]

    # -------- Filtered KPIs --------
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

    # -------- Filtered Geographic Analysis --------
    st.subheader("Geographic Performance")
    
    left, right = st.columns(2)
    
    with left:
        st.markdown("**White Space Score Distribution**")
        
        if not filtered_df.empty:
            # Aggregate filtered data by market
            market_agg = filtered_df.groupby('market').agg({
                'whiteSpaceScore': 'mean',
                'marketShare': 'mean',
                'competitorStrength': 'mean'
            }).reset_index()
            market_agg['GEO_KEY'] = market_agg['market'].map(to_key)
            
            # Merge with province geography
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
            # Empty map if no data
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
            # Create market comparison chart
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

    # -------- Detailed Data Table --------
    st.subheader("Detailed Brand Data")
    
    if not filtered_df.empty:
        # Display filtered data
        display_df = filtered_df[['brandName', 'category', 'market', 'whiteSpaceScore', 'marketShare', 'competitorStrength']].copy()
        display_df = display_df.round(2)
        st.dataframe(display_df, use_container_width=True)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name="filtered_brand_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No data matches the selected filters.")

# -------------------- Footer --------------------
st.markdown("---")
st.markdown("**Market Discovery Dashboard** — Real Data Integration")

from services import fetch_report,run_backend_sync
import json
import base64



@st.cache_data(show_spinner=True)
def load_mt_data():
    mt_fetcher = DataReaderMt()
    mt_data = mt_fetcher.read_mt_pwani_data()
    mt_data['brandName'] = mt_data['brandName'].str.strip()
    mt_data['market'] = mt_data['market'].str.strip()
    mt_data['category'] = mt_data['category'].str.strip()
    return mt_data

# -------------------- Caching GT and RTM Data --------------------
@st.cache_data(show_spinner=True)
def load_gt_rtm_data():
    gt_fetcher = DataReaderGT()
    gt_data = gt_fetcher.read_gt_pwani_data()
    rtm_data = gt_fetcher.read_rtm_data()
    return gt_data, rtm_data

# -------------------- Load Data --------------------
mt_data = load_mt_data()
gt_data, rtm_data = load_gt_rtm_data()

mt_brands = sorted(mt_data['brandName'].unique())
gt_brands = sorted(set(gt_data['brandName'].unique()).intersection(rtm_data['BRAND'].unique()))

# -------------------------------
# Streamlit UI
# -------------------------------
# -------------------- Reports Page --------------------
if st.session_state.page == "reports":
    st.title("📄 Reports Page")
    st.markdown("This is your new reports page where you can add additional report features.")
    
   

    # Dropdown to select MT or GT or Content Generation
    report_type = st.selectbox("Select Report Type", ["MT", "GT", "Content Generation"])

    if report_type == "MT":
        # MT Brand selection
        brand = st.selectbox("Select Brand", mt_brands)
        category_options = list(mt_data[mt_data["brandName"] == brand]["category"].unique())
        category = st.selectbox("Select Category", category_options)
        territory_options = list(mt_data[(mt_data["brandName"] == brand) & (mt_data["category"] == category)]["territory"].unique())
        territory = st.selectbox("Select Territory", territory_options)

        if st.button("Generate MT Executive PDF"):
            payload = {"brand": brand, "category": category}
            pdf_bytes = fetch_report("mt_executive_summary", payload)
            st.download_button(f"📥 Download MT Executive Summary PDF", pdf_bytes, f"mt_executive_{brand}_{category}.pdf", "application/pdf")

        if st.button("Generate MT Territory PDF"):
            payload = {"brand": brand, "category": category, "territory": territory}
            pdf_bytes = fetch_report("mt_territory_report", payload)
            st.download_button(f"📥 Download MT Territory PDF", pdf_bytes, f"mt_territory_{brand}_{category}_{territory}.pdf", "application/pdf")

    elif report_type == "GT":
        # GT Brand selection
        brand = st.selectbox("Select Brand", gt_brands)
        category_gt = (gt_data[gt_data["brandName"] == brand]['category'].unique())
        category_rtm = sorted(rtm_data[rtm_data['BRAND'] == brand]['CATEGORY'].unique())
        category_S = sorted(set(category_rtm).intersection(category_gt))
        category = st.selectbox("Select Category", category_S)

        gt_territory = sorted(gt_data[gt_data['brandName'] == brand]['market'].unique())
        rtm_territories = sorted(rtm_data[rtm_data['BRAND'] == brand]['TERRITORY'].unique())
        territories = sorted(set(gt_territory).intersection(rtm_territories))
        territory = st.selectbox("Select Territory", territories)

        if st.button("Generate GT Executive PDF"):
            payload = {"brand": brand, "category": category}
            pdf_bytes = fetch_report("gt_executive_summary", payload)
            st.download_button(f"📥 Download GT Executive Summary PDF", pdf_bytes, f"gt_executive_{brand}_{category}.pdf", "application/pdf")

        if st.button("Generate GT Territory PDF"):
            payload = {"brand": brand, "category": category, "territory": territory}
            pdf_bytes = fetch_report("gt_territory_report", payload)
            st.download_button(f"📥 Download GT Territory PDF", pdf_bytes, f"gt_territory_{brand}_{category}_{territory}.pdf", "application/pdf")

    elif report_type == "Content Generation":
        st.subheader("📝 Content Generation (GT LLM Input)")

        # Brand, category, territory selection
        brand = st.selectbox("Select Brand", gt_brands)
        category_gt = (gt_data[gt_data["brandName"] == brand]['category'].unique())
        category_rtm = sorted(rtm_data[rtm_data['BRAND'] == brand]['CATEGORY'].unique())
        category_S = sorted(set(category_rtm).intersection(category_gt))
        category = st.selectbox("Select Category", category_S)

        gt_territory = sorted(gt_data[gt_data['brandName'] == brand]['market'].unique())
        rtm_territories = sorted(rtm_data[rtm_data['BRAND'] == brand]['TERRITORY'].unique())
        territories = sorted(set(gt_territory).intersection(rtm_territories))
        territory = st.selectbox("Select Territory", territories)

        # Step 1: Generate JSON from backend
        if st.button("Generate LLM JSON"):
            payload = {"brand": brand, "category": category, "territory": territory}
            result_json = fetch_report("gt_llm_input", payload)
            st.session_state["llm_json"] = json.dumps(result_json, indent=4)

        # Step 2: Editable JSON area
        editable_json_str = st.text_area(
            "Edit JSON Output:",
            value=st.session_state.get("llm_json", "{}"),
            height=400,
            key="llm_json_editor"
        )

        # Step 3: Parse edited JSON
        try:
            edited_json = json.loads(editable_json_str)
            output_type = edited_json.get("output_type", "")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
            edited_json = None
            output_type = None

        # Step 4: Image location input if required
        image = ""
        if output_type in ["image", "text_image"]:
            image = st.file_uploader(
                    "Upload a PNG image (max 1 MB)", 
                    type=["png"], 
                    key="llm_image_upload"
                )
            if image:
                image_bytes=image.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            else:
                st.error('Upload Image')    

        # Step 5: Final generate button
        if st.button("Generate Final Output", key="llm_generate_final"):
            if edited_json is None:
                st.error("Cannot send invalid JSON to backend.")
            else:
                st.write("Sending to the backend...")
                run_backend_sync(edited_json, image_base64)
