import streamlit as st
import pandas as pd
from data_fetcher import DataReaderMt,DataReaderGT,read_target_audience
from utils import slugify
import plotly.graph_objects as go
from services import fetch_report,run_backend_sync
import json
import base64



def check_credentials(username, password):
    """
    Validate user credentials.
    Replace this with your actual authentication logic (database, API, etc.)
    """
    valid_users = {
        'admin': 'admin123',
        'user': 'password',
        'pwani': 'pwani2024'
    }
    return username in valid_users and valid_users[username] == password

def login_page():
    """Display login form with modern design"""
    st.set_page_config(
        page_title="Login - Market Discovery",
        page_icon="watermark.png",
        layout="wide"
    )
    
   
    try:
        with open("pwani.jpeg", "rb") as f:
            left_logo_data = base64.b64encode(f.read()).decode()
        
        with open("algo.jpeg", "rb") as f:
            right_logo_data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
            <style>
            .logo-container {{
                padding: 40px 20px 20px 20px;
                position: fixed;
                top: 0;
                left: 0;
                z-index: 999;
                background: white;   
                display: flex;
                align-items: center;
                gap: 40px;
                border-bottom: 1px solid #E5E7EB;
                width: 100%;
                justify-content: space-between;
            }}
            </style>
            
            <div class="logo-container">
                <img src="data:image/jpeg;base64,{left_logo_data}" alt="Pwani Logo" style="height:60px;width:auto;">
                <img src="data:image/jpeg;base64,{right_logo_data}" alt="Algo Logo" style="height:50px;width:auto;">
            </div>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        pass
    
    # Custom CSS for modern login page
    st.markdown("""
        <style>
        /* Remove default padding */
        .main .block-container {
            padding-top: 120px;
            padding-bottom: 2rem;
            max-width: 100%;
        }
        
        /* Login card styling */
        .login-card {
            background: white;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #E5E7EB;
        }
        
        /* Input field styling */
        .stTextInput input {
            border-radius: 8px;
            border: 1px solid #D1D5DB;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        .stTextInput input:focus {
            border-color: #3B82F6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        /* Welcome section */
        .welcome-section {
            padding: 3rem 2rem;
        }
        
        .welcome-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1F2937;
            margin-bottom: 1rem;
        }
        
        .welcome-subtitle {
            font-size: 1.125rem;
            color: #6B7280;
            line-height: 1.75;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 0;
            color: #374151;
        }
        
        .feature-icon {
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2, col3 = st.columns([1.5, 0.8, 1.5])
    
    # Left side - Welcome section
    with col1:

        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Right side - Login form
    with col2:

        st.markdown('### Sign In')
        
        username = st.text_input(
            'Username',
            key='username_input',
            placeholder='Enter your username',
            label_visibility='visible'
        )
        
        password = st.text_input(
            'Password',
            key='password_input',
            type='password',
            placeholder='Enter your password',
            label_visibility='visible'
        )
        
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        
        if st.button('Sign In', type='primary', use_container_width=True):
            if not username or not password:
                st.error('⚠️ Please enter both username and password')
            elif check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success('✅ Login successful! Redirecting...')
                st.rerun()
            else:
                st.error('❌ Invalid username or password')
        
        st.markdown('</div>', unsafe_allow_html=True)
        # st.markdown('</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        

        
def logout():
    """Handle logout"""
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.rerun()


def main_app():
    

    MAP_CENTER = {"lat": -0.5, "lon": 36.5}
    MAP_ZOOM = 4

    gt_reader = DataReaderGT()
    mt_reader = DataReaderMt()

    @st.cache_data(show_spinner=True)
    def load_rtm_data():
        try:
            gt_fetcher = DataReaderGT()  
            rtm_data = gt_fetcher.read_rtm_data()
            return rtm_data
        except Exception as e:
            st.warning(f"⚠️ Failed to load RTM data due to: {e}. Please try again.")
            return None


    @st.cache_data(show_spinner=False)
    def load_brand_data(data):
        """Load brand data with expected columns: brandName, category, market, marketShare, competitorStrength, whiteSpaceScore"""
        try:
            if data == 'MT':
                df = mt_reader.read_mt_pwani_data()
            elif data == "GT":
                df = gt_reader.read_gt_pwani_data()
            else:
                raise ValueError("Invalid data type. Expected 'MT' or 'GT'.")
            return df
        except Exception as e:
            st.warning(f"⚠️ Could not load brand data ({data}). Error: {e}. Please try again.")
            return None


    @st.cache_data(show_spinner=False)
    def load_competitor_data(data):
        """Load competitor data for MT or GT"""
        try:
            if data == 'MT':
                df = mt_reader.read_mt_competitor_data()
            elif data == "GT":
                df = gt_reader.read_gt_competitor_data()
            else:
                raise ValueError("Invalid data type. Expected 'MT' or 'GT'.")
            return df
        except Exception as e:
            st.warning(f"⚠️ Failed to load competitor data ({data}). Error: {e}. Please try again.")
            return None


    @st.cache_data(show_spinner=True)
    def load_gt_data():
        try:
            gt_fetcher = DataReaderGT()
            gt_data = gt_fetcher.read_gt_pwani_data()
            return gt_data
        except Exception as e:
            st.warning(f"⚠️ Could not load GT data due to: {e}. Please try again.")
            return None
    @st.cache_data(show_spinner=True)
    def load_target_audience():
        try:
            df=read_target_audience()
            return df
        except Exception as e:
            st.warning(f"⚠️ Could not load GT data due to: {e}. Please try again.")
            


    
    

    def markdown_container(color,container_name,score,dist_factor,span):  
        mk=st.markdown(f"""
            <div class="metric-container {color}-metric" >
                <h3>{container_name}</h3>
                <h1>{score:.1f} % </h1>
                <p>Across {dist_factor} brands</p>
                <span class = "tooltip-text">
                        {span}
                </span>
            </div>
            """, unsafe_allow_html=True) 
        return mk 
    st.set_page_config(
        page_title="Market Discovery Dashboard",
        page_icon="watermark.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # -------------------- CSS --------------------
    st.markdown("""
    <style>
    .css-18e3th9 {
        padding: 0rem !important;
        margin: 0rem !important;
    }

    /* Remove padding and margin from the sidebar */
    .css-1d391kg {
        padding: 0rem !important;
        margin: 0rem !important;
    }

    /* Remove spacing from all divs, headers, sections globally */
    div, section, header, main {
        margin: 0 !important;
        padding: 0 !important;
    }


    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        padding: 10px !important;
        text-align: center;
        justify-content: center;
    }

        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 0.5rem 0;
        }
        .metric-container {
            cursor: pointer;
        }

        .metric-container .tooltip-text {
            visibility: hidden;
            width: 220px;
            background-color: #333;
            color: #000;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 110%; /* Position above the div */
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .metric-container:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
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


    </>
    """, unsafe_allow_html=True)

    # -------------------- Load and Display Logos --------------------
    try:
        with open("pwani.jpeg", "rb") as f:
            left_logo_data = base64.b64encode(f.read()).decode()
        
        with open("algo.jpeg", "rb") as f:
            right_logo_data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
                <style>
                .logo-container {{
                padding:90px 10px 0px 30px !important;
                position:fixed;
                top:-35px;
                z-index: 999;
                width: 100%;
                background: white;   
                display: flex;
                justify-content: flex-start;
                gap: 60vw; /* optional space between logos if needed */
                border-bottom: 2px solid #E5E7EB;
                }}
                </style>
                
    <div class="logo-container">
        <img src="data:image/jpeg;base64,{left_logo_data}" alt="Pwani Logo" style="height:100px;width:auto;">
        <img src="data:image/jpeg;base64,{right_logo_data}" alt="Algo Logo" style="height:80px;width:auto;">
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
    st.sidebar.title("Navigation")
    data = st.sidebar.selectbox(options=("MT","GT"), label="Select the data", key="sidebar_data_selector")

    if st.sidebar.button("Summary Dashboard", use_container_width=True):
        st.session_state.page = "summary"
        st.session_state.selected_brand = None
        st.session_state.prefilters = None

    if st.sidebar.button("Market Discovery", use_container_width=True):
        st.session_state.page = "detail"

    if st.sidebar.button("Content Generation", use_container_width=True):
        st.session_state.page = "content_generation"  
        
    if st.sidebar.button("Logout", use_container_width=True):
        logout()


    rtm_data=load_rtm_data()
    BRAND_DF = load_brand_data(data)
    COMP_DF=load_competitor_data(data)

    # -------------------- Summary Page --------------------
    if st.session_state.page == "summary":
        st.markdown(
            """
            <style>
            .block-container {
                padding: 120px 40px !important;
            }
            .main [data-testid="stTitle"] {
                margin-top: 0 !important;
                margin-bottom: 6px !important;
                padding-bottom: 0 !important;
            }
            
            .main [data-testid="stTitle"] h1 {
                margin-top: 0 !important;
                margin-bottom: 6px !important;
                padding-bottom: 0 !important;
            }

            .main [data-testid="stSubheader"] {
                margin-top: 2px !important;
                margin-bottom: 2px !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
            
            .main [data-testid="stSubheader"] h2 {
                margin-top: 2px !important;
                margin-bottom: 2px !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
          
            </style>
            <div class="summary-container">
            """,
            unsafe_allow_html=True
        )
     
        st.title("Market Discovery Summary")


        
        st.subheader("Key Performance Indicators")
        date=BRAND_DF["date"].max().strftime("%b %Y")
        st.write(f"Last Update {date}")
        agg_data = BRAND_DF.groupby(['brandName','category','market']).agg({
            'whiteSpaceScore':'mean',
            'marketShare':'sum',
            'competitorStrength':'sum'
        }).reset_index()
        
        avg_ws_score = agg_data['whiteSpaceScore'].mean()
        total_brands = len(agg_data[['brandName','category']].drop_duplicates())
        total_markets = len(agg_data['market'].unique())
       

            
        if data=="MT":
            
            grouped_df = COMP_DF.groupby('brandName')['totalQuantity'].sum().reset_index()
            top_3_sales = grouped_df['totalQuantity'].sort_values(ascending=False).head(3).sum()
            cci = (top_3_sales / grouped_df['totalQuantity'].sum()) * 100
            tMshare_p = BRAND_DF['quantity'].sum()
            tMshare_c= COMP_DF['quantity'].sum()
            market_share=(tMshare_p/(tMshare_c+tMshare_c))*100


        elif data =="GT":
            grouped_df = COMP_DF.groupby('brandName')['brandTotalVolume'].sum().reset_index()
            top_3_sales = grouped_df['brandTotalVolume'].sort_values(ascending=False).head(3).sum()
            cci = (top_3_sales / grouped_df['brandTotalVolume'].sum()) * 100
            tMshare_p = BRAND_DF['brandTotalVolume'].sum()
            tMshare_c= COMP_DF['brandTotalVolume'].sum()
            market_share=(tMshare_p/(tMshare_c+tMshare_c))*100
                

        c1, c2, c3 = st.columns(3)
        with c1:
            span_message="Score (out of 100) showing overall untapped market potential — higher means more growth opportunity."
            markdown_container('blue','White Space Score',avg_ws_score,total_brands,span_message)

        with c2:
            span_message="Percentage of total market sales captured by your brand."
            markdown_container('purple','Market Share',market_share.round(1),total_markets,span_message)
        
        with c3:
            span_message="% of top 3 competitors’ sales. Lower (≤50%) = fragmented market, more opportunity."
            markdown_container('orange',"Market Competitor Index",round(cci,2),"", span_message)

        st.markdown("---")

        # -------- Geographic Analysis --------
        st.subheader("Geographic Analysis")

        col1, col2 = st.columns(2)



        with col1:
      
            st.markdown("**Kenya Brand Performance Data**")
            if data=='GT':
                with open("storage/kenya_territories_lake.geojson") as f:
                    geo = json.load(f)
                feautre_id="properties.TERRITORY"
          
            elif data =="MT":
                with open("storage/kenya.geojson") as f:
                    geo= json.load(f)
                feautre_id="properties.COUNTY_NAM"
            metric = BRAND_DF.groupby("market", as_index=False).agg({'whiteSpaceScore': 'mean','marketShare': 'mean'}).reset_index()


            metrics = {
                "WSS": list(metric["whiteSpaceScore"].unique()),
                "MS": list(metric["marketShare"])
            }

            colorbar_titles = {
            "WSS": "WSS",
            "MS": "MS"
            }
            default_metric = "WSS"
    

            fig_prov = go.Figure(go.Choroplethmapbox(
                geojson=geo,
                featureidkey=feautre_id,
                locations=metric["market"],
                z=metrics[default_metric],
                colorscale="Viridis",
                marker_opacity=0.7,
                marker_line_width=0.5,
                text=metric["market"],  # hover name
                hovertemplate="<b>%{text}</b><br>Score: %{z}<extra></extra>",
                colorbar=dict(title=colorbar_titles[default_metric])
            ))

            fig_prov.update_layout(
                mapbox_style="open-street-map",
                mapbox_center=MAP_CENTER,
                mapbox_zoom=MAP_ZOOM,
                height=400,
                margin=dict(r=0, t=0, l=0, b=0)
            )

            fig_json = fig_prov.to_json()


            html = f"""
            <style>
            .wrap {{
                position: relative;
                height: 400px;
                border-radius: 16px;
                overflow: hidden;
                background: #eef2f7;
                border: 1px solid #e5e7eb;
                box-shadow: 0 12px 28px rgba(0,0,0,.08);
            }}
            #plotA {{
                position: absolute;
                inset: 0;
            }}
            .fab {{
                position: absolute;
                top: 25px;
                right: 12px;
                z-index: 10;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                border: none;
                background: #fff;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                font: 700 18px/44px system-ui, sans-serif;
                cursor: pointer;
            }}
            .menu {{
                position: absolute;
                top: 60px;
                right: 12px;
                z-index: 11;
                width: 180px;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                border: 1px solid #eef0f4;
                display: none;
            }}
            .menu.open {{
                display: block;
            }}
            .menu div {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #e5e5e5;
            }}
            .menu div:last-child {{
                border-bottom: none;
            }}
            .menu div:hover {{
                background: #f3f6fb;
            }}
        .item{{ padding:10px 14px; cursor:pointer; font:500 14px/1.2 system-ui, sans-serif;}} .item:hover{{ background:#f3f6fb; }}

            </style>

            <div class="wrap">
                <div id="plotA"></div>
                <button id="fabA" class="fab">☰</button>
                <div id="menuA" class="menu">
                    <div class="item" data-metric="WSS">White Space Score</div>
                    <div class="item" data-metric="MS">Market Share</div>
                </div>
            </div>

            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
            <script>
                const fig = {fig_json};
                const METRICS = {json.dumps(metrics)};
                const COLORBARS = {json.dumps(colorbar_titles)};
                const div = document.getElementById("plotA");
                Plotly.newPlot(div, fig.data, fig.layout, {{responsive:true, displayModeBar:false}});

                const fab = document.getElementById("fabA");
                const menu = document.getElementById("menuA");

                fab.addEventListener("click", () => {{
                    menu.classList.toggle("open");
                }});

                document.querySelectorAll(".item").forEach(el => {{
                    el.addEventListener("click", () => {{
                        const metric = el.dataset.metric;
                        Plotly.restyle(div, {{z: [METRICS[metric]]}}, [0]);
                        Plotly.restyle(div, {{
                                z: [METRICS[metric]],
                'colorbar.title.text': COLORBARS[metric]
                        }}, [0]);
                        menu.classList.remove("open");
                    }});
                }});
            </script>
            """

            st.components.v1.html(html, height=420, scrolling=False)
            
        with col2:
            with open("storage/kenya.geojson") as f:
                geo= json.load(f)
                feautre_id="properties.COUNTY_NAM"
            st.markdown("**Kenya – Demographic Index**")
            metrics=pd.read_csv('storage/demographic_data.csv')    
            metrics = metrics.to_dict(orient="list")

       
            colorbar_titles = {
    "WSS": "WSS",
    "MS": "MS",
    "GDP": "GDP",
    "POP": "POP",
    "MPOP": "MPOP",
    "FPOP": "FPOP",
    "HH": "HH",
    "AREA": "AREA",
    "DENSITY": "DENSITY",
    "PCI": "PCI",
    "STUDENTS": "STUDENTS",
    "HDI": "HDI",
    "AGRI": "AGRI",
    "MINING": "MINING",
    "MANUF": "MANUF",
    "ELEC": "ELEC",
    "WATER": "WATER",
    "CONST": "CONST",
    "RETAIL": "RETAIL",
    "TRANS": "TRANS",
    "ACCOM": "ACCOM",
    "INFO": "INFO",
    "FIN": "FIN",
    "ESTATE": "ESTATE",
    "PROF": "PROF",
    "ADMIN": "ADMIN",
    "PUBLIC": "PUBLIC",
    "EDU": "EDU",
    "HEALTH": "HEALTH",
    "OTHER": "OTHER",
    "FISM": "FISM",
    "GCP": "GCP",
    "INTERNET": "INTERNET",
    "CATH": "CATH",
    "PROT": "PROT",
    "EVAN": "EVAN",
    "AIC": "AIC",
    "ORTH": "ORTH",
    "OTHREL": "OTHREL",
    "MUSLIM": "MUSLIM",
    "POV": "POV",
    "PURCH": "PURCH",
    "OWN": "OWN",
    "GIFT": "GIFT",
    "ELEC_ACC": "ELEC_ACC",
    "SANIT": "SANIT"
}

            default_metric = "Total Population"
            
            fig = go.Figure(go.Choroplethmapbox(
            geojson=geo,
                featureidkey="properties.COUNTY_NAM",
                locations=metrics["Location"],
                z=metrics["Total Population"],
                colorscale="Viridis",
                marker_opacity=0.7,
                marker_line_width=0.5,
                text=metrics["Location"],  # hover name
                hovertemplate="<b>%{text}</b><br>Score: %{z}<extra></extra>"
                ))
 
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_center=MAP_CENTER,
                mapbox_zoom=MAP_ZOOM,
                height=400,
                margin=dict(r=0, t=0, l=0, b=0)
           
            )
            
      

            # Convert Plotly figure to JSON
            fig_json = fig.to_json()

            # Minimal HTML with floating hamburger
            html = f"""
            <style>
            .wrap {{
                position: relative;
                height: 400px;
                border-radius: 16px;
                overflow: hidden;
                background: #eef2f7;
                border: 1px solid #e5e7eb;
                box-shadow: 0 12px 28px rgba(0,0,0,.08);
            }}
            #plotA {{
                position: absolute;
                inset: 0;
            }}
            .fab {{
                position: absolute;
                top: 25px;
                right: 12px;
                z-index: 10;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                border: none;
                background: #fff;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                font: 700 18px/44px system-ui, sans-serif;
                cursor: pointer;
            }}
            .menu {{
                position: absolute;
                top: 60px;
                right: 12px;
                z-index: 11;
                width: 180px;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                border: 1px solid #eef0f4;
                display: none;
                overflow-y: auto;
                max-height: 250px;
            }}
            .menu.open {{
                display: block;
            }}
            .menu div {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #e5e5e5;
            }}
            .menu div:last-child {{
                border-bottom: none;
            }}
            .menu div:hover {{
                background: #f3f6fb;
            }}
        .item{{ padding:10px 14px; cursor:pointer; font:500 14px/1.2 system-ui, sans-serif;}} .item:hover{{ background:#f3f6fb; }}

            </style>

            <div class="wrap">
                <div id="plotA"></div>
                <button id="fabA" class="fab">☰</button>
                <div id="menuA" class="menu">
  <div class="item" data-metric="GDP 2022">GDP 2022</div>
  <div class="item" data-metric="Total Population">Total Population</div>
  <div class="item" data-metric="Male Population">Male Population</div>
  <div class="item" data-metric="Female population">Female population</div>
  <div class="item" data-metric="Households-Total">Households-Total</div>
  <div class="item" data-metric="Sq Km">Sq Km</div>
  <div class="item" data-metric="Persons per Sq. Km">Persons per Sq. Km</div>
  <div class="item" data-metric="PCI 2022">PCI 2022</div>
  <div
    class="item"
    data-metric="number of students enrolled in secondary schools"
  >
    number of students enrolled in secondary schools
  </div>
  <div class="item" data-metric="HDI">HDI</div>
  <div class="item" data-metric="Agriculture, Forestry & Fishing">
    Agriculture, Forestry & Fishing
  </div>
  <div class="item" data-metric="Mining & Quarrying">Mining & Quarrying</div>
  <div class="item" data-metric="Manufacturing">Manufacturing</div>
  <div class="item" data-metric="Electricity Supply">Electricity Supply</div>
  <div class="item" data-metric="Water Supply; Waste Collection">
    Water Supply; Waste Collection
  </div>
  <div class="item" data-metric="Construction">Construction</div>
  <div class="item" data-metric="Wholesale & Retail (Motor Repair)">
    Wholesale & Retail (Motor Repair)
  </div>
  <div class="item" data-metric="Transport & Storage">Transport & Storage</div>
  <div class="item" data-metric="Accommodation & Food Service">
    Accommodation & Food Service
  </div>
  <div class="item" data-metric="Information & Communication">
    Information & Communication
  </div>
  <div class="item" data-metric="Financial & Insurance Activities">
    Financial & Insurance Activities
  </div>
  <div class="item" data-metric="Real Estate Activities">
    Real Estate Activities
  </div>
  <div class="item" data-metric="Professional & Technical Services">
    Professional & Technical Services
  </div>
  <div class="item" data-metric="Administrative Support Services">
    Administrative Support Services
  </div>
  <div class="item" data-metric="Public Administration & Defense">
    Public Administration & Defense
  </div>
  <div class="item" data-metric="Education">Education</div>
  <div class="item" data-metric="Human Health & Social Work">
    Human Health & Social Work
  </div>
  <div class="item" data-metric="Other Service Activities">
    Other Service Activities
  </div>
  <div class="item" data-metric="Financial Services Indirectly Measured">
    Financial Services Indirectly Measured
  </div>
  <div class="item" data-metric="GCP">GCP</div>
  <div class="item" data-metric="Internet Penetration">
    Internet Penetration
  </div>
  <div class="item" data-metric="Catholic">Catholic</div>
  <div class="item" data-metric="Protestant">Protestant</div>
  <div class="item" data-metric="Evangelicals">Evangelicals</div>
  <div class="item" data-metric="AIC">AIC</div>
  <div class="item" data-metric="Orthodox">Orthodox</div>
  <div class="item" data-metric="Others">Others</div>
  <div class="item" data-metric="Muslims">Muslims</div>
  <div class="item" data-metric="Poverty">Poverty</div>
  <div class="item" data-metric="Purchase Stock (%)">Purchase Stock (%)</div>
  <div class="item" data-metric="Own Production (%)">Own Production (%)</div>
  <div class="item" data-metric="Gifts (%)">Gifts (%)</div>
  <div class="item" data-metric="electricity access Percentage">
    electricity access Percentage
  </div>
  <div class="item" data-metric="access to sanitation">
    access to sanitation
  </div>
</div>

            </div>

            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
            <script>
                const fig = {fig_json};
                const METRICS = {json.dumps(metrics)};
                const COLORBARS = {json.dumps(colorbar_titles)};
                const div = document.getElementById("plotA");
                Plotly.newPlot(div, fig.data, fig.layout, {{responsive:true, displayModeBar:false}});

                const fab = document.getElementById("fabA");
                const menu = document.getElementById("menuA");

                fab.addEventListener("click", () => {{
                    menu.classList.toggle("open");
                }});

                document.querySelectorAll(".item").forEach(el => {{
                    el.addEventListener("click", () => {{
                        const metric = el.dataset.metric;
                        Plotly.restyle(div, {{z: [METRICS[metric]]}}, [0]);
                        Plotly.restyle(div, {{
                                z: [METRICS[metric]],
                'colorbar.title.text': COLORBARS[metric]
                        }}, [0]);
                        menu.classList.remove("open");
                    }});
                }});
            </script>
            """

            st.components.v1.html(html, height=420, scrolling=False)


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
                
                if st.button(f"{row['brandName']} - WS Score: {row['whiteSpaceScore']:.1f} %", 
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
                            <style>
                            .brand-card{{
                                padding:10px !important;
                                background: #eee;
                            }}
                            </style>
                <div class="brand-card">
                    <strong>{row['brandName']} {row['category']}</strong> - <em>{row['market']}</em> | 
                    Category: {row['category']}<br>
                    White Space Score: <strong>{row['whiteSpaceScore']:.1f}%</strong> | 
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
                
                if st.button(f"{row['brandName']} - WS Score: {row['whiteSpaceScore']:.1f}%",
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
                    <strong>{row['brandName']} {row['category']}</strong> - <em>{row['market']}</em> | 
                    Category: {row['category']}<br>
                    White Space Score: <strong>{row['whiteSpaceScore']:.1f}%</strong> |
                    Market Share: <strong>{row['marketShare']:.1f}%</strong>
                    <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                        <div style="background: linear-gradient(to right, #EF4444, #DC2626);
                                    height: 8px; width: {max(0,min(100,100-float(row['whiteSpaceScore'])))}%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.page == "detail":
        st.markdown(
            """
            <style>
            .block-container {
                padding: 120px 40px !important;
            }
            </style>
            <div class="summary-container">
            """,
            unsafe_allow_html=True
        )
     
        
   
 
        if data == "MT":
            st.sidebar.markdown("---")
            st.sidebar.header("Filters & Controls")
        
            # Category selection (first)
            category_options = sorted(BRAND_DF["category"].dropna().unique())
        
            # Check if there are prefilters from the button click
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_category = st.session_state.prefilters.get("category")
                if default_category in category_options:
                    default_category_index = category_options.index(default_category)
                else:
                    default_category_index = 0
            else:
                default_category_index = 0
        
            category = st.sidebar.selectbox("Select Report Category", ["All Categories"]+category_options, index=default_category_index)
        
            # Brand selection (filtered by category)
            brand_options = sorted(BRAND_DF[BRAND_DF["category"] == category]["brandName"].dropna().unique())
        
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_brand = st.session_state.prefilters.get("brandName")
                if default_brand in brand_options:
                    default_brand_index = brand_options.index(default_brand)
                else:
                    default_brand_index = 0
            else:
                default_brand_index = 0
        
            brand = st.sidebar.selectbox("Select Report Brand",['All Brands'] + brand_options, index=default_brand_index)
        
            # Territory selection (filtered by category and brand)
            territory_options = sorted(BRAND_DF[(BRAND_DF["category"] == category) & (BRAND_DF["brandName"] == brand)]["territory"].dropna().unique())
        
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_territory = st.session_state.prefilters.get("market")
                if default_territory in territory_options:
                    default_territory_index = territory_options.index(default_territory)
                else:
                    default_territory_index = 0
            else:
                default_territory_index = 0
        
            territory = st.sidebar.selectbox("Select Report Territory",["All Markets"]+ territory_options, index=default_territory_index)
        
            # Clear prefilters after first use
            if "prefilters" in st.session_state:
                st.session_state.prefilters = None
    
        elif data == "GT":
            st.sidebar.markdown("---")
        
            # Load rtm_data first
           
            show_volume = st.sidebar.checkbox("Show RTM Data", value=True)

        
            
            # Category selection (first) - intersection logic
            category_gt = BRAND_DF["category"].dropna().unique()
            category_rtm = rtm_data["category"].dropna().unique()
            category_options = sorted(set(category_gt).intersection(category_rtm))
        
            # Check if there are prefilters from the button click
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_category = st.session_state.prefilters.get("category")
                if default_category in category_options:
                    default_category_index = category_options.index(default_category)
                else:
                    default_category_index = 0
            else:
                default_category_index = 0
        
            category = st.sidebar.selectbox("Select Report Category",['All Categories']+ category_options, index=default_category_index)
        
            # Brand selection (filtered by category) - intersection logic
            brand_gt = BRAND_DF[BRAND_DF["category"] == category]["brandName"].dropna().unique()
            brand_rtm = rtm_data[rtm_data["category"] == category]["brand"].dropna().unique()
            brand_options = sorted(set(brand_gt).intersection(brand_rtm))
        
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_brand = st.session_state.prefilters.get("brandName")
                if default_brand in brand_options:
                    default_brand_index = brand_options.index(default_brand)
                else:
                    default_brand_index = 0
            else:
                default_brand_index = 0
        
            brand = st.sidebar.selectbox("Select Report Brand", ['All Brands']+brand_options, index=default_brand_index)
        
            # Territory selection (filtered by category and brand) - intersection logic
            gt_territory = BRAND_DF[(BRAND_DF["category"] == category) & (BRAND_DF["brandName"] == brand)]["market"].dropna().unique()
            rtm_territories = rtm_data[(rtm_data["category"] == category) & (rtm_data["brand"] == brand)]["territory"].dropna().unique()
            territory_options = sorted(set(gt_territory).intersection(rtm_territories))
        
            if "prefilters" in st.session_state and st.session_state.prefilters:
                default_territory = st.session_state.prefilters.get("market")
                if default_territory in territory_options:
                    default_territory_index = territory_options.index(default_territory)
                else:
                    default_territory_index = 0
            else:
                default_territory_index = 0
        
            territory = st.sidebar.selectbox("Select Report Territory",['All Markets'] + territory_options, index=default_territory_index)
        
            # Clear prefilters after first use
            if "prefilters" in st.session_state:
                st.session_state.prefilters = None
    

    
        st.title("Market Discovery Dashboard")
      
    
        filtered_df = BRAND_DF.copy()
        if not (
            category == "All Categories"
            and brand == "All Brands"
            and territory == "All Markets"
        ):
            if category != "All Categories":
                filtered_df = filtered_df[filtered_df["category"] == category]
            if brand != "All Brands":
                filtered_df = filtered_df[filtered_df["brandName"] == brand]
            if territory != "All Markets":
                filtered_df = filtered_df[filtered_df["territory"] == territory]

    
        st.subheader("Filtered Performance Indicators")
    
        if not filtered_df.empty:
            ws_mean = filtered_df['whiteSpaceScore'].mean()

            if pd.isna(ws_mean):
                ws_mean = BRAND_DF['whiteSpaceScore'].mean() 
            
            ms_mean = filtered_df.groupby('county').agg({'marketShare':'mean'})['marketShare'].mean()
   
            ped = filtered_df['ped'].mean().round(2)
            z_score= filtered_df['brandZVol'].mean().round(2)
            cluster = filtered_df['cluster'].iloc[0]  # first value
            cluster = cluster.split("|")[0] if "|" in cluster else cluster

        else:
            ws_mean = ms_mean = 0

        tg_audience = load_target_audience()

        import math

        def human_format(num):
            # Handle None or NaN
            if num is None or (isinstance(num, float) and math.isnan(num)):
                return "N/A"

            try:
                num = float(num)
            except (ValueError, TypeError):
                return "N/A"

            if num >= 1_000_000_000:
                return f"{num/1_000_000_000:.1f}B"
            elif num >= 1_000_000:
                return f"{num/1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num/1_000:.1f}K"
            else:
                return f"{num:.0f}"


        if tg_audience is not None and not tg_audience.empty:
            mask = pd.Series(True, index=tg_audience.index)

            if territory != "All Markets":
                mask &= tg_audience["market"] == territory
            if category != "All Categories":
                mask &= tg_audience["category"] == category
            if brand != "All Brands":
                mask &= tg_audience["brandName"] == brand

            ta_number = tg_audience[mask]

            # Step 1 & 2: Average population by market
            avg_population_per_market = ta_number.groupby("market")["provincePopulation"].mean()


            # Step 3: Sum of averages
            sum_avg_population = avg_population_per_market.sum()
  

            # Step 4: Mean percent
            mean_percent = ta_number["percentOfProvince"].mean() / 100  # convert % to decimal

            # Step 5: Final target audience
            target_au = sum_avg_population * mean_percent
            target_au = human_format(target_au)

        else:
            ta_number = pd.DataFrame()
            target_au = 0

        
        kc1, kc2, kc3, kc4, kc5,kc6 = st.columns(6)
        with kc1:
            st.markdown(f"""
                        <div class="metric-container blue-metric"><h4>White Space Score</h4><h2>{ws_mean:.1f}%</h2>
                        <span class="tooltip-text">Score (out of 100) showing untapped market potential - higher means more growth opportunity.</span>
                        
                        </div>
                        """, unsafe_allow_html=True)
        with kc2:
            st.markdown(f"""<div class="metric-container purple-metric"><h4>Market Share</h4><h2>{ms_mean:.1f}%</h2>
                        <span class="tooltip-text">
                        Percentage of total market sales captured by your brand.
                        </span>
                        </div>
                        """, unsafe_allow_html=True)

        with kc3:
            st.markdown(f"""<div class="metric-container green-metric"><h4>PED</h4><h2>{ped}</h2>
                        <span class = "tooltip-text">(Price Elasticity of Demand): Indicates price sensitivity. Low (< 1) = stable demand; high (> 1) = price-sensitive.</span>
                        </div>""", unsafe_allow_html=True)
        with kc4:
            st.markdown(f"""<div class="metric-container orange-metric"><h4>Z Score</h4><h2>{z_score}</h2>
                        <span class = "tooltip-text">
                        Shows deviation from market average. 0 = average; positive = above market; negative = below.
                        </span>
                        </div>""", unsafe_allow_html=True)
    
        with kc5:
            st.markdown(f"""<div class="metric-container red-metric"><h4>Cluster</h4><h2>{cluster}</h2>
                        <span class = "tooltip-text">
                        Groups regions with similar sales patterns and performance.
                        </span>
                        </div>""", unsafe_allow_html=True)
            
        with kc6:

            st.markdown(f"""
                <div class="metric-container teal-metric">
                    <h4>Target Audience Data</h4>
                    <h2>{target_au}</h2>
                    <span class="tooltip-text">Target Audience Data.</span>
                
                </div>
                """, unsafe_allow_html=True)

        
    
        st.markdown("---")
    
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Geographic Performance")

        with col2:
            st.subheader("Top 5 Competitors")
        left, right = st.columns(2)
    
        with left:

            if data=='GT':
                with open("storage/kenya_territories_lake.geojson") as f:
                    geo = json.load(f)
                feautre_id="properties.TERRITORY"
                if territory == "All Markets" and category == "All Categories" and brand == "All Brands":
                    df = BRAND_DF.copy()
                else:
                    df = BRAND_DF[
                        (BRAND_DF["territory"] == territory if territory != "All Markets" else True) &
                        (BRAND_DF["category"] == category if category != "All Categories" else True) &
                        (BRAND_DF["brandName"] == brand if brand != "All Brands" else True)
                    ]
                metric = df.copy()
                if show_volume:
                    with open("storage/kenya-subcounties-simplified.geojson") as f:
                        geo_rtm = json.load(f)
                    feautre_id_rtm = "properties.shapeName"
                
                    if territory == "All Markets" and category == "All Categories" and brand == "All Brands":
                        df_rtm = rtm_data.copy()
                    else:
                        df_rtm = rtm_data[
                            (rtm_data["territory"] == territory if territory != "All Markets" else True) &
                            (rtm_data["category"] == category if category != "All Categories" else True) &
                            (rtm_data["brand"] == brand if brand != "All Brands" else True)
                        ]
                    metric_rtm = df_rtm.copy()


                
            elif data =="MT":
                with open("storage/kenya.geojson") as f:
                    geo= json.load(f)
                feautre_id="properties.COUNTY_NAM"
                if territory == "All Markets" and category == "All Categories" and brand == "All Brands":
                    df = BRAND_DF.copy()
                else:
                    df = BRAND_DF[
                        (BRAND_DF["territory"] == territory if territory != "All Markets" else True) &
                        (BRAND_DF["category"] == category if category != "All Categories" else True) &
                        (BRAND_DF["brandName"] == brand if brand != "All Brands" else True)
                    ]
                metric = df.groupby("market", as_index=False).agg({'whiteSpaceScore': 'mean','marketShare': 'mean'}).reset_index()




           
            metrics = {
                "WSS": list(metric["whiteSpaceScore"].unique()),
                "MS": list(metric["marketShare"]),
            }

            colorbar_titles = {
            "WSS": "WSS",
            "MS": "MS",
            }
            default_metric = "WSS"

            fig_prov = go.Figure(go.Choroplethmapbox(
                geojson=geo,
                featureidkey=feautre_id,
                locations=metric["market"],
                z=metrics[default_metric],
                colorscale="Viridis",
                marker_opacity=0.7,
                marker_line_width=0.5,
                text=metric["market"],  # hover name
                hovertemplate="<b>%{text}</b><br>Score: %{z}<extra></extra>",
                colorbar=dict(title=colorbar_titles[default_metric])
            ))
            
            if data=='GT' and show_volume:
                fig_prov = go.Figure(go.Choroplethmapbox(
                    geojson=geo_rtm,
                    featureidkey=feautre_id_rtm,
                    locations=metric_rtm["subcounty"],
                    z=metric_rtm["aws"],
                    colorscale="Reds",
                    marker_opacity=0.8,
                    marker_line_width=0.8,
                    text=metric_rtm["subcounty"],
                    hovertemplate="<b>%{text}</b><br>AWS: %{z}<extra></extra>",
                    colorbar=dict(title="AWS")
                ))

            fig_prov.update_layout(
                mapbox_style="open-street-map",
                mapbox_center=MAP_CENTER,
                mapbox_zoom=MAP_ZOOM,
                height=400,
                margin=dict(r=0, t=0, l=0, b=0)
            )

            # Convert Plotly figure to JSON
            fig_json = fig_prov.to_json()

            # Prepare the metrics dictionary for JS

            html = f"""
            <style>
            .wrap {{
                position: relative;
                height: 400px;
                border-radius: 16px;
                overflow: hidden;
                background: #eef2f7;
                border: 1px solid #e5e7eb;
                box-shadow: 0 12px 28px rgba(0,0,0,.08);
            }}
            #plotA {{
                position: absolute;
                inset: 0;
            }}
            .fab {{
                position: absolute;
                top: 25px;
                right: 12px;
                z-index: 10;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                border: none;
                background: #fff;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                font: 700 18px/44px system-ui, sans-serif;
                cursor: pointer;
            }}
            .menu {{
                position: absolute;
                top: 60px;
                right: 12px;
                z-index: 11;
                width: 180px;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 8px 22px rgba(0,0,0,.12);
                border: 1px solid #eef0f4;
                display: none;
            }}
            .menu.open {{
                display: block;
            }}
            .menu div {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #e5e5e5;
            }}
            .menu div:last-child {{
                border-bottom: none;
            }}
            .menu div:hover {{
                background: #f3f6fb;
            }}
        .item{{ padding:10px 14px; cursor:pointer; font:500 14px/1.2 system-ui, sans-serif;}} .item:hover{{ background:#f3f6fb; }}

            </style>

            <div class="wrap">
                <div id="plotA"></div>
                <button id="fabA" class="fab">☰</button>
                <div id="menuA" class="menu">
                    <div class="item" data-metric="WSS">White Space Score</div>
                    <div class="item" data-metric="MS">Market Share</div>
                </div>
            </div>

            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
            <script>
                const fig = {fig_json};
                const METRICS = {json.dumps(metrics)};
                const COLORBARS = {json.dumps(colorbar_titles)};
                const div = document.getElementById("plotA");
                Plotly.newPlot(div, fig.data, fig.layout, {{responsive:true, displayModeBar:false}});

                const fab = document.getElementById("fabA");
                const menu = document.getElementById("menuA");

                fab.addEventListener("click", () => {{
                    menu.classList.toggle("open");
                }});

                document.querySelectorAll(".item").forEach(el => {{
                    el.addEventListener("click", () => {{
                        const metric = el.dataset.metric;
                        Plotly.restyle(div, {{z: [METRICS[metric]]}}, [0]);
                        Plotly.restyle(div, {{
                                z: [METRICS[metric]],
                'colorbar.title.text': COLORBARS[metric]
                        }}, [0]);
                        menu.classList.remove("open");
                    }});
                }});
            </script>
            """

            st.components.v1.html(html, height=420, scrolling=False)
            

            
        with right:
    # Choose geo path based on data type
            if data == 'MT':
                geo_path = "storage/kenya.geojson"
                feature_id = "properties.COUNTY_NAM"
            elif data == 'GT':
                geo_path = "storage/kenya_territories_lake.geojson"
                feature_id = "properties.TERRITORY"

            with open(geo_path) as f:
                geo = json.load(f)

            # Base dataset
            df = COMP_DF.copy()
            if category != "All Categories":
                df = df[df["category"] == category]
            if territory != "All Markets":
                df = df[df["territory"] == territory]
                
                
           
            # Build data per brand
            brands = (
                df.groupby("brandName")["marketShare"]
                .sum()
                .sort_values(ascending=False)
                .head(5)  # Take top 5
                .reset_index()
            )
            top_brands = brands["brandName"].tolist()

            METRICS = {}

            for brand_name in top_brands:
                subset = df[df["brandName"] == brand_name]
                brand_metric = subset.groupby("market", as_index=False)["marketShare"].sum()
                METRICS[brand_name] = brand_metric["marketShare"].tolist()


            default_brand = top_brands[0]
          

            # Build initial map
            fig = go.Figure(go.Choroplethmapbox(
                geojson=geo,
                featureidkey=feature_id,
                locations=df["market"].unique(),
                z=METRICS[default_brand],
                colorscale="Viridis",
                marker_opacity=0.7,
                marker_line_width=0.5,
                text=df["market"].unique(),
                hovertemplate="<b>%{text}</b><br>Market Share: %{z}<extra></extra>",
                colorbar=dict(title=f"{default_brand}")
            ))

            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_center=MAP_CENTER,
                mapbox_zoom=MAP_ZOOM,
                height=400,
                margin=dict(r=0, t=0, l=0, b=0)
            )

            fig_json = fig.to_json()

            # --- HTML + CSS + JS using your bar chart hamburger styling ---
            html = f"""
            <style>
                .wrap {{
                    position: relative;
                    height: 400px;
                    border-radius: 16px;
                    overflow: hidden;
                    background: #eef2f7;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 12px 28px rgba(0,0,0,.08);
                }}
                #plotA {{
                    position: absolute;
                    inset: 0;
                }}
                .fab {{
                    position: absolute;
                    top: 25px;
                    right: 12px;
                    z-index: 10;
                    width: 44px;
                    height: 44px;
                    border-radius: 50%;
                    border: none;
                    background: #fff;
                    box-shadow: 0 8px 22px rgba(0,0,0,.12);
                    font: 700 18px/44px system-ui, sans-serif;
                    cursor: pointer;
                }}
                .menu {{
                    position: absolute;
                    top: 90px;
                    right: 12px;
                    z-index: 11;
                    width: 180px;
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 8px 22px rgba(0,0,0,.12);
                    border: 1px solid #eef0f4;
                    display: none;
                    overflow-y: auto;
                    max-height: 150px;
                }}
                .menu.open {{
                    display: block;
                }}
                .menu div {{
                    padding: 10px;
                    cursor: pointer;
                    border-bottom: 1px solid #e5e5e5;
                }}
                .menu div:last-child {{
                    border-bottom: none;
                }}
                .menu div:hover {{
                    background: #f3f6fb;
                }}
                .item {{
                    padding:10px 14px;
                    cursor:pointer;
                    font:500 14px/1.2 system-ui, sans-serif;
                }}
                .item:hover {{
                    background:#f3f6fb;
                }}
            </style>

            <div style="position:relative; height:400px; border-radius:16px; overflow:hidden; background:#fff; box-shadow:0 12px 28px rgba(0,0,0,0.12);">
                <div id="plotA" style="position:absolute; inset:0;"></div>
                <button id="fabA" class="fab">☰</button>
                <div id="menuA" class="menu">
                    {''.join([f'<div class="item" data-brand="{b}">{b}</div>' for b in top_brands])}
                </div>
            </div>

            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
            <script>
                const fig = {fig_json};
                const METRICS = {json.dumps(METRICS)};
                const div = document.getElementById("plotA");

                Plotly.newPlot(div, fig.data, fig.layout, {{responsive:true, displayModeBar:false}});

                const fab = document.getElementById("fabA");
                const menu = document.getElementById("menuA");

                fab.addEventListener("click", () => {{
                    menu.style.display = menu.style.display === "block" ? "none" : "block";
                }});

                document.querySelectorAll(".item").forEach(el => {{
                    el.addEventListener("click", () => {{
                        const brand = el.dataset.brand;
                        Plotly.restyle(div, {{
                            z: [METRICS[brand]],
                            'colorbar.title.text': brand
                        }}, [0]);
                        menu.style.display = "none";
                    }});
                }});
            </script>
            """

            st.components.v1.html(html, height=480, scrolling=False)
            
            
        st.markdown("---")
    
        st.subheader("Detailed Brand Data")
    
     
        filtered_rtm = rtm_data.copy()
    
        if category != "All Categories":
            filtered_rtm = filtered_rtm[filtered_rtm['category'] == category]
        
        if brand != "All Brands":
            filtered_rtm = filtered_rtm[filtered_rtm['brand'] == brand]
        
        if territory != "All Markets":
            filtered_rtm = filtered_rtm[filtered_rtm['territory'] == territory]
    
        county_data = filtered_rtm.groupby('county').agg({
            'qtyKgRtm': 'sum',
            'aws': 'mean'
        }).reset_index()
      
    
        top_counties = county_data.sort_values('qtyKgRtm', ascending=False).head(5)

       
    
        distributor_data = filtered_rtm.groupby(['distributorName','territory']).agg({
            'valueSold': 'sum',
            'customerName': 'nunique'
        }).reset_index()
    
        top_distributors = distributor_data.dropna().nlargest(5, 'valueSold').sort_values('valueSold', ascending=False)
    
        if len(top_counties) > 0:
            max_qty = top_counties['qtyKgRtm'].max()
            top_counties['score_normalized'] = (top_counties['qtyKgRtm'] / max_qty * 100)
           
        if len(top_distributors) > 0:
            max_sales = top_distributors['valueSold'].max()
            top_distributors['sales_normalized'] = (top_distributors['valueSold'] / max_sales * 100)
    
        c1, c2, c3 = st.columns(3)
    
        with c1:
            st.markdown("**Top 5 Counties**")
            for i, (idx, county) in enumerate(top_counties.iterrows()):
                st.markdown(f"""
                <div style="background: #eee; padding: 12px !important; margin: 8px 0; border-radius: 8px;
                            border-left: 4px solid #3B82F6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: linear-gradient(to right, #3B82F6, #06B6D4); color: white;
                                    padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{i+1}</span>
                        <div style="flex-grow: 1; margin-left: 12px;">
                            <strong>{county['county']}</strong><br>
                            <small>Volume: {county['qtyKgRtm']:.2f} Kg • AWS: {county['aws']:.1f}%</small>
                            <div style="background: #E5E7EB; height: 4px; border-radius: 2px; margin-top: 4px;">
                                <div style="background: linear-gradient(to right, #3B82F6, #06B6D4); height: 4px; width: {county['score_normalized']:.1f}%; border-radius: 2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
        with c2:
            st.markdown("**Top Distributor Performance**")
            for idx, d in top_distributors.iterrows():
                st.markdown(f"""
                            <style>
                            .distributor-card {{
                            padding:10px !important  
                            }}
                            </style>
                <div class="distributor-card">
                    <strong>{d['distributorName']}</strong> <small>({d['territory']})</small><br>
                    <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                        <span>Sales: <strong style="color: #059669;">KES {d['valueSold']:,.0f}</strong></span>
                        <span>Coverage: <strong style="color: #3B82F6;">{d['customerName']} customers</strong></span>
                    </div>
                    <div style="background: #E5E7EB; height: 4px; border-radius: 2px; margin-top: 4px;">
                        <div style="background: linear-gradient(to right, #10B981, #059669); height: 4px; width: {d['sales_normalized']:.1f}%; border-radius: 2px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
     
        with c3:
            st.markdown("**Reports Page**")

            if data == "MT":
                if brand != "All Brands" and category != "All Categories" and territory != "All Markets":
                    if st.button("Generate MT Executive Report"):
                        try:
                            payload = {"brand": brand, "category": category}
                            pdf_bytes = fetch_report("mt_executive_summary", payload)
                            st.download_button(
                                "Download MT Executive Summary PDF",
                                pdf_bytes,
                                f"mt_executive_{brand}_{category}.pdf",
                                "application/pdf"
                            )
                        except Exception:
                            st.warning("Something went wrong while generating the report. Please click the button again.")

                    if st.button("Generate MT Territory Report"):
                        try:
                            payload = {"brand": brand, "category": category, "territory": territory}
                            pdf_bytes = fetch_report("mt_territory_report", payload)
                            st.download_button(
                                "Download MT Territory PDF",
                                pdf_bytes,
                                f"mt_territory_{brand}_{category}_{territory}.pdf",
                                "application/pdf"
                            )
                        except Exception:
                            st.warning("Unable to generate the territory report. Please try clicking again in a moment.")
                else:
                        st.warning("Please Select a brand")                                 
                            

            elif data == "GT":
                if brand != "All Brands" and category != "All Categories" and territory != "All Markets":
                    if st.button("Generate GT Executive Report"):
                        try:
                            payload = {"brand": brand, "category": category}
                            pdf_bytes = fetch_report("gt_executive_summary", payload)
                            st.download_button(
                                "Download GT Executive Summary Report",
                                pdf_bytes,
                                f"gt_executive_{brand}_{category}.pdf",
                                "application/pdf"
                            )
                        except Exception:
                            st.warning("There was a small issue generating the GT Executive Report. Please try again.")
      

                    if st.button("Generate GT Territory Report"):
                        try:
                            payload = {"brand": brand, "category": category, "territory": territory}
                            pdf_bytes = fetch_report("gt_territory_report", payload)
                            st.download_button(
                                "Download GT Territory Report",
                                pdf_bytes,
                                f"gt_territory_{brand}_{category}_{territory}.pdf",
                                "application/pdf"
                            )
                        except Exception:
                            st.warning("Something went wrong while creating the GT Territory Report. Please click again.")
                else:
                        st.warning("Please Select a brand")  
            

    elif st.session_state.page == "content_generation":
        st.markdown(
            """
            <style>
            .block-container {
                padding: 120px 40px !important;
            }
            </style>
            <div class="summary-container">
            """,
            unsafe_allow_html=True
        )
        st.subheader("Content Generation (GT LLM Input)")
        
        # Load data only when on content generation page
    # --- Safe GT Content Generation Filters ---

        gt_data = load_gt_data()

        # 1. Build brand list safely
        gt_brands = sorted(set(gt_data['brandName'].unique()).intersection(rtm_data['brand'].unique()))
        if not gt_brands:
            st.warning("⚠️ No GT brands available for content generation.")
            st.stop()

        brand = st.sidebar.selectbox("Select Brand", gt_brands, key="content_gen_brand")

        # 2. Build category list safely
        category_gt = gt_data.loc[gt_data["brandName"] == brand, 'category'].unique()
        category_rtm = rtm_data.loc[rtm_data['brand'] == brand, 'category'].unique()
        category_S = sorted(set(category_rtm).intersection(category_gt))

        if not category_S:
            st.warning(f"⚠️ No categories found for brand '{brand}'.")
            st.write("Brands:", gt_brands)
            st.write("Categories (GT):", category_gt)
            st.write("Categories (RTM):", category_rtm)
            st.write("Intersection:", category_S)
            st.write("Territories (GT):", gt_territory)
            st.write("Territories (RTM):", rtm_territories)
            st.write("Intersection:", territories)
            st.stop()

        category = st.sidebar.selectbox("Select Category", category_S, key="content_gen_category")

        # 3. Build territory list safely
        gt_territory = gt_data.loc[gt_data['brandName'] == brand, 'market'].unique()
        rtm_territories = rtm_data.loc[rtm_data['brand'] == brand, 'territory'].unique()
        territories = sorted(set(gt_territory).intersection(rtm_territories))

        if not territories:
            st.warning(f"⚠️ No territories found for brand '{brand}' and category '{category}'.")
            st.stop()

        territory = st.sidebar.selectbox("Select Territory", territories, key="content_gen_territory")


        if st.button("Generate LLM JSON"):
            payload = {"brand": brand, "category": category, "territory": territory}
            st.write(payload)
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
                    with st.spinner("Generating image..."):
                        run_backend_sync(llm_data, image_base64)
        else:
            st.info("Click 'Generate LLM JSON' to start.")
        st.markdown("</div>", unsafe_allow_html=True)
        
if __name__ == "__main__":
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    
    # Route based on login status
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()
