import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Google Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD SECRETS SECURELY
# ============================================================================

def load_credentials():
    """Load credentials from Streamlit secrets or environment variables"""
    
    # Try Streamlit secrets first (production - Streamlit Cloud, Codespaces)
    try:
        DEVELOPER_TOKEN = st.secrets.get("DEVELOPER_TOKEN")
        LOGIN_CUSTOMER_ID = st.secrets.get("LOGIN_CUSTOMER_ID")
        OPERATING_CUSTOMER_ID = st.secrets.get("OPERATING_CUSTOMER_ID")
        SERVICE_ACCOUNT_JSON_STR = st.secrets.get("SERVICE_ACCOUNT_JSON")
        
        if all([DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR]):
            return DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR
    except:
        pass
    
    # Fall back to environment variables (local development with .env)
    DEVELOPER_TOKEN = os.getenv("DEVELOPER_TOKEN")
    LOGIN_CUSTOMER_ID = os.getenv("LOGIN_CUSTOMER_ID")
    OPERATING_CUSTOMER_ID = os.getenv("OPERATING_CUSTOMER_ID")
    SERVICE_ACCOUNT_JSON_STR = os.getenv("SERVICE_ACCOUNT_JSON")
    
    return DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR

# Load credentials
DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON_STR = load_credentials()

# ============================================================================
# INITIALIZE GOOGLE ADS CLIENT
# ============================================================================

@st.cache_resource
def init_client():
    """Initialize Google Ads client"""
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
        if not DEVELOPER_TOKEN:
            missing.append("DEVELOPER_TOKEN")
        if not LOGIN_CUSTOMER_ID:
            missing.append("LOGIN_CUSTOMER_ID")
        if not OPERATING_CUSTOMER_ID:
            missing.append("OPERATING_CUSTOMER_ID")
        if not SERVICE_ACCOUNT_JSON_STR:
            missing.append("SERVICE_ACCOUNT_JSON")
        
        status = f"❌ Missing credentials: {', '.join(missing)}"
    
    return client, status

# Initialize client
client, connection_status = init_client()

# ============================================================================
# HEADER
# ============================================================================

st.markdown("# 📊 Google Ads Automation Dashboard")
st.markdown("Monitor your Google Ads campaigns and generate detailed reports")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 📋 About")
    st.markdown("""
    This dashboard connects to your Google Ads account and displays:
    - Campaign performance metrics
    - Detailed reports
    - Campaign data analysis
    """)
    
    st.markdown("### ⚙️ Connection Status")
    if "Connected" in connection_status:
        st.success(connection_status)
    else:
        st.error(connection_status)
    
    st.markdown("### 🔑 How Secrets Work")
    st.markdown("""
    Credentials are loaded from:
    1. **GitHub Codespaces Secrets** (recommended)
    2. **Environment variables** (.env file)
    
    **Never hardcode secrets in code!**
    """)

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["🔍 Status", "📈 Campaigns", "📋 Reports"])

# ============================================================================
# TAB 1: STATUS
# ============================================================================

with tab1:
    st.markdown("### API Connection Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Connection", "✅ Active" if "Connected" in connection_status else "❌ Inactive")
    
    with col2:
        st.metric("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    st.markdown("---")
    
    if "Connected" in connection_status:
        st.success(connection_status)
        st.markdown("""
        ✅ Your Google Ads API connection is working!
        
        You can now:
        - View campaign metrics
        - Generate detailed reports
        - Monitor campaign performance
        """)
    else:
        st.error(connection_status)
        st.markdown("""
        ❌ Connection failed. Please check:
        
        1. **GitHub Codespaces Secrets**: Go to https://github.com/settings/codespaces
           - Add all 4 secrets: DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID, OPERATING_CUSTOMER_ID, SERVICE_ACCOUNT_JSON
           - Select your repository
        
        2. **Or use .env file** (local testing):
           - Create `.env` in repo root
           - Add your credentials
           - Make sure `.env` is in `.gitignore`
        
        3. **Verify credentials**:
           - Tokens are not expired
           - Service account JSON is valid
           - All 4 values are set
        """)

# ============================================================================
# TAB 2: CAMPAIGNS
# ============================================================================

with tab2:
    st.markdown("### Campaign Performance Metrics")
    
    if st.button("🔄 Fetch Campaign Data", use_container_width=True):
        if not client:
            st.error("❌ Client not initialized. Check your credentials in GitHub Codespaces Secrets or .env file.")
        else:
            try:
                with st.spinner("Fetching campaign data..."):
                    service = client.get_service("GoogleAdsService")
                    response = service.search_stream(
                        customer_id=OPERATING_CUSTOMER_ID,
                        query="""
                            SELECT 
                                campaign.name,
                                campaign.status,
                                metrics.impressions,
                                metrics.clicks,
                                metrics.cost_micros,
                                metrics.conversions,
                                metrics.ctr,
                                metrics.average_cpc
                            FROM campaign
                            WHERE campaign.status = 'ENABLED'
                            ORDER BY metrics.cost_micros DESC
                        """
                    )
                    
                    data = []
                    for batch in response:
                        for row in batch.results:
                            cost = row.metrics.cost_micros / 1e6
                            cpc = row.metrics.average_cpc / 1e6 if row.metrics.average_cpc else 0
                            ctr = row.metrics.ctr or 0
                            conversions = row.metrics.conversions or 0
                            
                            data.append({
                                "Campaign Name": row.campaign.name,
                                "Status": row.campaign.status.name,
                                "Impressions": f"{row.metrics.impressions:,}",
                                "Clicks": f"{row.metrics.clicks:,}",
                                "CTR %": f"{ctr:.2f}",
                                "Cost ₹": f"{cost:,.2f}",
                                "CPC ₹": f"{cpc:.2f}",
                                "Conversions": f"{conversions:.0f}",
                            })
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.success(f"✅ Retrieved {len(data)} campaign(s)")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Download as CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ No campaign data found. Campaign may be in learning phase.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================================
# TAB 3: REPORTS
# ============================================================================

with tab3:
    st.markdown("### Generate Campaign Report")
    
    if st.button("📄 Generate Full Report", use_container_width=True):
        if not client:
            st.error("❌ Client not initialized. Check your credentials.")
        else:
            try:
                with st.spinner("Generating report..."):
                    service = client.get_service("GoogleAdsService")
                    response = service.search_stream(
                        customer_id=OPERATING_CUSTOMER_ID,
                        query="""
                            SELECT 
                                campaign.name,
                                metrics.impressions,
                                metrics.clicks,
                                metrics.cost_micros,
                                metrics.conversions,
                                metrics.ctr,
                                metrics.average_cpc
                            FROM campaign
                            WHERE campaign.status = 'ENABLED'
                            ORDER BY metrics.cost_micros DESC
                        """
                    )
                    
                    report = []
                    report.append("=" * 100)
                    report.append("📊 GOOGLE ADS AUTOMATION REPORT")
                    report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    report.append("=" * 100)
                    report.append("")
                    
                    campaigns = []
                    total_impressions = 0
                    total_clicks = 0
                    total_cost = 0
                    total_conversions = 0
                    
                    for batch in response:
                        for row in batch.results:
                            cost = row.metrics.cost_micros / 1e6
                            cpc = row.metrics.average_cpc / 1e6 if row.metrics.average_cpc else 0
                            ctr = row.metrics.ctr or 0
                            conversions = row.metrics.conversions or 0
                            
                            total_impressions += row.metrics.impressions
                            total_clicks += row.metrics.clicks
                            total_cost += cost
                            total_conversions += conversions
                            
                            campaigns.append({
                                "name": row.campaign.name,
                                "impressions": row.metrics.impressions,
                                "clicks": row.metrics.clicks,
                                "ctr": ctr,
                                "cost": cost,
                                "cpc": cpc,
                                "conversions": conversions,
                            })
                    
                    if campaigns:
                        # Summary
                        report.append("📊 SUMMARY METRICS")
                        report.append("-" * 100)
                        report.append(f"Total Campaigns: {len(campaigns)}")
                        report.append(f"Total Impressions: {total_impressions:,}")
                        report.append(f"Total Clicks: {total_clicks:,}")
                        report.append(f"Total Cost: ₹{total_cost:,.2f}")
                        report.append(f"Total Conversions: {total_conversions:.0f}")
                        if total_clicks > 0:
                            avg_cpc = total_cost / total_clicks
                            report.append(f"Average CPC: ₹{avg_cpc:.2f}")
                        report.append("")
                        
                        # Campaigns
                        report.append("=" * 100)
                        report.append("🎯 CAMPAIGN DETAILS")
                        report.append("-" * 100)
                        
                        for i, c in enumerate(campaigns, 1):
                            report.append(f"\n{i}. {c['name']}")
                            report.append(f"   Impressions: {c['impressions']:,}")
                            report.append(f"   Clicks: {c['clicks']:,}")
                            report.append(f"   CTR: {c['ctr']:.2f}%")
                            report.append(f"   Cost: ₹{c['cost']:,.2f}")
                            report.append(f"   CPC: ₹{c['cpc']:.2f}")
                            report.append(f"   Conversions: {c['conversions']:.0f}")
                        
                        report.append("\n" + "=" * 100)
                        
                        report_text = "\n".join(report)
                        
                        st.success("✅ Report generated successfully!")
                        
                        # Display report
                        st.code(report_text, language="text")
                        
                        # Download as text
                        st.download_button(
                            label="📥 Download Report as TXT",
                            data=report_text,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("⚠️ No data found")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
**Google Ads Automation Dashboard**
- Built with Streamlit
- Powered by Google Ads API
- Data refreshes on demand
- Secrets managed securely
""")
