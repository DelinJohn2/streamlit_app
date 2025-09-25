import streamlit as st
import json
import os
import pandas as pd

from utils import get_first_present,to_key,slugify

@st.cache_data(show_spinner=False)
def load_province_geojson(path: str):
    """Load province GeoJSON and standardize properties"""
    if not os.path.exists(path):
        st.error(f"Province GeoJSON file not found: {path}")
        st.stop()
        
    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)
    
    for feat in gj.get("features", []):
        props = feat.get("properties", {}) or {}
        name = get_first_present(props, [
            "TERRITORY","Territory","territory",
            "PROVINCE","Province","province",
            "NAME_1","ADM1_EN","NAME","Name","name",
            "COUNTY","County","county"
        ], "")
        props["PROV_KEY"] = to_key(name)
        props["__prov_id"] = slugify(props["PROV_KEY"])
        feat["properties"] = props
    return gj

@st.cache_data(show_spinner=False)
def load_county_geojson(path: str):
    """Load county GeoJSON and standardize properties"""
    if not os.path.exists(path):
        st.error(f"County GeoJSON file not found: {path}")
        st.stop()
        
    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)
    
    for feat in gj.get("features", []):
        props = feat.get("properties", {}) or {}
        cnt = get_first_present(props, [
            "COUNTY_NAM","COUNTY","County","county",
            "ADM1_EN","NAME","NAME_1","Name","name"
        ], "")
        props["COUNTY_KEY"] = to_key(cnt)
        feat["properties"] = props
    return gj

@st.cache_data(show_spinner=False)
def aggregate_brand_data_by_geography(df: pd.DataFrame, geo_level='province'):
    """Aggregate brand data by geographic region (province/county level)"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by market (assuming 'market' maps to geographic regions)
    agg_data = df.groupby('market').agg({
        'whiteSpaceScore': 'mean',
        'marketShare': 'mean', 
        'competitorStrength': 'mean',
        'brandName': 'count'  # Count of brands per market
    }).reset_index()
    
    agg_data.rename(columns={'brandName': 'brandCount'}, inplace=True)
    agg_data['GEO_KEY'] = agg_data['market'].map(to_key)
    
    return agg_data