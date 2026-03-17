import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient

st.set_page_config(
    page_title="Google Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load credentials securely
def load_credentials():
    try:
        DEVELOPER_TOKEN = st.secrets.get("DEVELOPER_TOKEN")
        LOGIN_CUSTOMER_ID = st.secrets.get("LOGIN_CUSTOMER_ID")
        OPERATING_CUSTOMER_ID = st.secrets.get("OPERATING_CUSTOMER_ID")
        SERVICE_ACCOUNT_JSON_STR = st.secrets.get("SERVICE_ACCOUNT_JSON")
        
        if all([DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR]):
            return DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR
    except:
        pass
    
    DEVELOPER_TOKEN = os.getenv("DEVELOPER_TOKEN")
    LOGIN_CUSTOMER_ID = os.getenv("LOGIN_CUSTOMER_ID")
    OPERATING_CUSTOMER_ID = os.getenv("OPERATING_CUSTOMER_ID")
    SERVICE_ACCOUNT_JSON_STR = os.getenv("SERVICE_ACCOUNT_JSON")
    
    return DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR

DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR = load_credentials()

@st.cache_resource
def init_client():
    client = None
    status = "❌ Not configured"
    
    if all([DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR]):
        try:
            with open("/tmp/sa.json", "w") as f:
                f.write(SERVICE_ACCOUNT_JSON_STR)
            
            client = GoogleAdsClient.load_from_dict({
                "developer_token": DEVELOPER_TOKEN,
                "json_key_file_path": "/tmp/sa.json",
                "use_proto_plus": True,
                "login_customer_id": LOGIN_CUSTOMER_ID,
            })
            status = "✅ Connected to Google Ads API!"
        except Exception as e:
            status = f"❌ Error: {str(e)[:100]}"
    else:
        missing = []
        if not DEVELOPER_TOKEN: missing.append("DEVELOPER_TOKEN")
        if not LOGIN_CUSTOMER_ID: missing.append("LOGIN_CUSTOMER_ID")
        if not OPERATING_CUSTOMER_ID: missing.append("OPERATING_CUSTOMER_ID")
        if not SERVICE_ACCOUNT_JSON_STR: missing.append("SERVICE_ACCOUNT_JSON")
        status = f"❌ Missing: {', '.join(missing)}"
    
    return client, status

client, connection_status = init_client()

st.markdown("# 📊 Google Ads Automation Dashboard")
st.markdown("Monitor your Google Ads campaigns")
st.markdown("---")

with st.sidebar:
    st.markdown("### Connection Status")
    if "Connected" in connection_status:
        st.success(connection_status)
    else:
        st.error(connection_status)

tab1, tab2, tab3 = st.tabs(["🔍 Status", "📈 Campaigns", "📋 Reports"])

with tab1:
    st.markdown("### API Connection Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Connection", "✅ Active" if "Connected" in connection_status else "❌ Inactive")
    with col2:
        st.metric("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    st.markdown("---")
    if "Connected" in connection_status:
        st.success("✅ Ready to use!")
    else:
        st.error(connection_status)

with tab2:
    st.markdown("### Campaign Performance Metrics")
    if st.button("🔄 Fetch Campaign Data", use_container_width=True):
        if not client:
            st.error("❌ Client not initialized")
        else:
            try:
                with st.spinner("Fetching..."):
                    service = client.get_service("GoogleAdsService")
                    response = service.search_stream(
                        customer_id=OPERATING_CUSTOMER_ID,
                        query="""SELECT campaign.name, metrics.impressions, metrics.clicks, 
                                 metrics.cost_micros, metrics.ctr, metrics.average_cpc
                          FROM campaign WHERE campaign.status = 'ENABLED'"""
                    )
                    
                    data = []
                    for batch in response:
                        for row in batch.results:
                            cost = row.metrics.cost_micros / 1e6
                            cpc = row.metrics.average_cpc / 1e6 if row.metrics.average_cpc else 0
                            data.append({
                                "Campaign": row.campaign.name,
                                "Impressions": f"{row.metrics.impressions:,}",
                                "Clicks": f"{row.metrics.clicks:,}",
                                "CTR %": f"{row.metrics.ctr:.2f}",
                                "Cost ₹": f"{cost:,.2f}",
                                "CPC ₹": f"{cpc:.2f}",
                            })
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.success(f"✅ Retrieved {len(data)} campaign(s)")
                        st.dataframe(df, use_container_width=True)
                        csv = df.to_csv(index=False)
                        st.download_button("📥 Download CSV", csv, f"campaigns_{datetime.now().strftime('%Y%m%d')}.csv")
                    else:
                        st.warning("⚠️ No data")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab3:
    st.markdown("### Generate Report")
    if st.button("📄 Generate Report", use_container_width=True):
        if not client:
            st.error("❌ Client not initialized")
        else:
            try:
                with st.spinner("Generating..."):
                    service = client.get_service("GoogleAdsService")
                    response = service.search_stream(
                        customer_id=OPERATING_CUSTOMER_ID,
                        query="""SELECT campaign.name, metrics.impressions, metrics.clicks, 
                                 metrics.cost_micros FROM campaign WHERE campaign.status = 'ENABLED'"""
                    )
                    
                    report = ["=" * 80, "📊 GOOGLE ADS REPORT", f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 80, ""]
                    
                    for batch in response:
                        for row in batch.results:
                            cost = row.metrics.cost_micros / 1e6
                            report.append(f"{row.campaign.name}")
                            report.append(f"  Impressions: {row.metrics.impressions:,}")
                            report.append(f"  Clicks: {row.metrics.clicks:,}")
                            report.append(f"  Cost: ₹{cost:,.2f}")
                            report.append("")
                    
                    report_text = "\n".join(report)
                    st.success("✅ Report generated!")
                    st.code(report_text, language="text")
                    st.download_button("📥 Download TXT", report_text, f"report_{datetime.now().strftime('%Y%m%d')}.txt")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("**Google Ads Dashboard** | Powered by Streamlit & Google Ads API")
