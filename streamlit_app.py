import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
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

# B2B Benchmarks
BENCHMARKS = {
    "ctr": 2.5,  # 2-3% range, target 3%
    "cpc": 100,  # ₹50-150 range, target ₹100
    "conversion_rate": 2.0,  # 1-3% range, target 2%
    "cost_per_conversion": 5000  # ₹3000-10000, target ₹5000
}

# Helper Functions
def calculate_metrics(impressions, clicks, cost, conversions):
    """Calculate key metrics"""
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cpc = (cost / clicks) if clicks > 0 else 0
    conv_rate = (conversions / clicks * 100) if clicks > 0 else 0
    cost_per_conv = (cost / conversions) if conversions > 0 else 0
    
    return {
        "ctr": ctr,
        "cpc": cpc,
        "conv_rate": conv_rate,
        "cost_per_conv": cost_per_conv
    }

def get_color_status(metric_name, value):
    """Return color based on metric performance"""
    if metric_name == "ctr":
        if value >= 3: return "green"
        elif value >= 2: return "yellow"
        else: return "red"
    elif metric_name == "cpc":
        if value <= 100: return "green"
        elif value <= 150: return "yellow"
        else: return "red"
    elif metric_name == "conv_rate":
        if value >= 2: return "green"
        elif value >= 1: return "yellow"
        else: return "red"
    elif metric_name == "cost_per_conv":
        if value <= 5000: return "green"
        elif value <= 7500: return "yellow"
        else: return "red"
    return "gray"

def calculate_performance_score(metrics):
    """Calculate A-F grade"""
    ctr_score = min((metrics["ctr"] / BENCHMARKS["ctr"]) * 100, 100)
    cpc_score = min((BENCHMARKS["cpc"] / metrics["cpc"]) * 100, 100) if metrics["cpc"] > 0 else 0
    conv_score = min((metrics["conv_rate"] / BENCHMARKS["conversion_rate"]) * 100, 100)
    
    overall_score = (ctr_score + cpc_score + conv_score) / 3
    
    if overall_score >= 85: return "A", "Excellent", "green"
    elif overall_score >= 70: return "B", "Good", "lightgreen"
    elif overall_score >= 55: return "C", "Fair", "yellow"
    elif overall_score >= 40: return "D", "Poor", "orange"
    else: return "F", "Critical", "red"

def get_campaign_list():
    """Get all campaigns"""
    try:
        service = client.get_service("GoogleAdsService")
        response = service.search_stream(
            customer_id=OPERATING_CUSTOMER_ID,
            query="SELECT campaign.id, campaign.name, campaign.status FROM campaign ORDER BY campaign.name"
        )
        
        campaigns = {}
        for batch in response:
            for row in batch.results:
                campaigns[row.campaign.name] = row.campaign.id
        return campaigns
    except Exception as e:
        st.error(f"Error fetching campaigns: {str(e)}")
        return {}

def get_campaign_data(campaign_id, start_date, end_date):
    """Fetch campaign data for date range"""
    try:
        service = client.get_service("GoogleAdsService")
        
        query = f"""
            SELECT
                segments.date,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign
            WHERE campaign.id = {campaign_id}
            AND segments.date >= '{start_date.strftime('%Y-%m-%d')}'
            AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
            ORDER BY segments.date
        """
        
        response = service.search_stream(customer_id=OPERATING_CUSTOMER_ID, query=query)
        
        data = []
        for batch in response:
            for row in batch.results:
                data.append({
                    "date": row.segments.date,
                    "campaign_name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost": row.metrics.cost_micros / 1e6,
                    "conversions": row.metrics.conversions or 0
                })
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching campaign data: {str(e)}")
        return pd.DataFrame()

def generate_recommendations(metrics, daily_data):
    """Generate top 3 recommendations"""
    recommendations = []
    
    # Check CPC
    cpc_gap = ((metrics["cpc"] - BENCHMARKS["cpc"]) / BENCHMARKS["cpc"]) * 100
    if cpc_gap > 10:
        recommendations.append({
            "title": "High Cost Per Click",
            "priority": "HIGH",
            "current": f"₹{metrics['cpc']:.2f}",
            "benchmark": f"₹{BENCHMARKS['cpc']:.2f}",
            "gap": f"+{cpc_gap:.1f}%",
            "root_cause": "Quality score may be low or bid amount too aggressive. Keywords may not be well-targeted.",
            "actions": [
                "1. Review & improve Quality Score - Target 7+ on all keywords",
                "2. Reduce bid by 10-15% - Monitor for 1 week and adjust",
                "3. Audit keyword relevance - Pause low-relevance keywords, add negatives"
            ],
            "impact": f"Potential CPC reduction: 15-20%. New CPC: ₹{metrics['cpc'] * 0.85:.2f}. Monthly savings: ₹{(metrics['cpc'] * 0.15) * 100:.0f} (assuming 100 clicks)",
            "expected_outcome": ["✅ Maintain or increase clicks", "✅ Reduce overall spend", "✅ Improve ROI"]
        })
    
    # Check CTR
    ctr_gap = ((BENCHMARKS["ctr"] - metrics["ctr"]) / BENCHMARKS["ctr"]) * 100
    if ctr_gap > 15:
        recommendations.append({
            "title": "Low Click-Through Rate",
            "priority": "MEDIUM",
            "current": f"{metrics['ctr']:.2f}%",
            "benchmark": "2-3%",
            "gap": f"-{ctr_gap:.1f}%",
            "root_cause": "Ad copy not compelling enough. Missing ad extensions. Poor keyword-ad relevance.",
            "actions": [
                "1. Test new ad copy variations - Focus on unique value proposition",
                "2. Add all available ad extensions - Sitelinks, callouts, structured snippets",
                "3. Refine keyword-to-ad relevance - Group similar keywords, create specific ads"
            ],
            "impact": f"Potential CTR improvement: 20-30%. New CTR: {metrics['ctr'] * 1.25:.2f}%. More clicks with same budget.",
            "expected_outcome": ["✅ Better ad performance", "✅ Higher quality traffic", "✅ Better conversion rates"]
        })
    
    # Check Conversion Rate
    conv_gap = ((BENCHMARKS["conversion_rate"] - metrics["conv_rate"]) / BENCHMARKS["conversion_rate"]) * 100
    if conv_gap > 20:
        recommendations.append({
            "title": "Low Conversion Rate",
            "priority": "HIGH",
            "current": f"{metrics['conv_rate']:.2f}%",
            "benchmark": "2%+",
            "gap": f"-{conv_gap:.1f}%",
            "root_cause": "Landing page not optimized for conversions. Ad message doesn't match landing page. Form friction too high.",
            "actions": [
                "1. Audit landing page experience - Check load time, mobile responsiveness",
                "2. Improve message-match alignment - Ensure ad promise matches landing page",
                "3. Simplify conversion process - Reduce form fields, clear CTA"
            ],
            "impact": f"Potential conversion rate improvement: 25-40%. New rate: {metrics['conv_rate'] * 1.30:.2f}%. More conversions from same traffic.",
            "expected_outcome": ["✅ Better ROI on ad spend", "✅ Lower cost per conversion", "✅ More qualified leads"]
        })
    
    # Sort by priority
    priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: priority_map.get(x["priority"], 3))
    
    return recommendations[:3]

# Main App
st.markdown("# 📊 Google Ads Automation Dashboard")
st.markdown("Monitor your Google Ads campaigns")
st.markdown("---")

with st.sidebar:
    st.markdown("### Connection Status")
    if "Connected" in connection_status:
        st.success(connection_status)
    else:
        st.error(connection_status)

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Status", "📈 Campaigns", "📊 Campaign Analysis", "📋 Reports"])

# TAB 1: Status
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

# TAB 2: Campaigns
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

# TAB 3: Campaign Analysis (NEW)
with tab3:
    st.markdown("### 🎯 Detailed Campaign Analysis")
    
    if not client:
        st.error("❌ Client not initialized. Check your credentials.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Campaign Search
            campaigns = get_campaign_list()
            if not campaigns:
                st.error("❌ No campaigns found")
            else:
                selected_campaign = st.selectbox(
                    "Search & Select Campaign",
                    options=list(campaigns.keys()),
                    help="Select a campaign to analyze"
                )
        
        with col2:
            # Date range selector
            st.markdown("**Date Range**")
            date_range = st.radio(
                "Select period",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"],
                horizontal=True
            )
            
            if date_range == "Last 7 days":
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
            elif date_range == "Last 30 days":
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            elif date_range == "Last 90 days":
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
            else:
                col_s, col_e = st.columns(2)
                with col_s:
                    start_date = st.date_input("From", datetime.now() - timedelta(days=30))
                with col_e:
                    end_date = st.date_input("To", datetime.now())
        
        st.markdown("---")
        
        # Fetch data
        campaign_id = campaigns[selected_campaign]
        daily_data = get_campaign_data(campaign_id, start_date, end_date)
        
        if daily_data.empty:
            st.warning("⚠️ No data available for selected period")
        else:
            # Calculate aggregate metrics
            total_impressions = daily_data["impressions"].sum()
            total_clicks = daily_data["clicks"].sum()
            total_cost = daily_data["cost"].sum()
            total_conversions = daily_data["conversions"].sum()
            
            metrics = calculate_metrics(total_impressions, total_clicks, total_cost, total_conversions)
            grade, grade_text, grade_color = calculate_performance_score(metrics)
            
            # SECTION 1: Campaign Status Card
            st.markdown("### 📋 Campaign Status")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Campaign", selected_campaign[:20])
            with col2:
                st.metric("Status", daily_data["status"].iloc[0])
            with col3:
                st.metric("Period", f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}")
            with col4:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: {grade_color}; border-radius: 10px; color: white;'>
                <h3>{grade}</h3>
                <p>{grade_text}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # SECTION 2: Performance Metrics Grid
            st.markdown("### 📊 Performance Metrics")
            
            metric_cols = st.columns(3)
            metrics_info = [
                ("Impressions", f"{total_impressions:,}", "-", "daily_impressions"),
                ("Clicks", f"{total_clicks:,}", "-", "daily_clicks"),
                ("CTR", f"{metrics['ctr']:.2f}%", f"{BENCHMARKS['ctr']:.1f}%", "ctr"),
                ("CPC", f"₹{metrics['cpc']:.2f}", f"₹{BENCHMARKS['cpc']:.0f}", "cpc"),
                ("Conv. Rate", f"{metrics['conv_rate']:.2f}%", f"{BENCHMARKS['conversion_rate']:.1f}%", "conv_rate"),
                ("Cost/Conv.", f"₹{metrics['cost_per_conv']:.0f}", f"₹{BENCHMARKS['cost_per_conversion']:.0f}", "cost_per_conv"),
            ]
            
            for idx, (metric_name, current_val, benchmark_val, metric_key) in enumerate(metrics_info):
                col = metric_cols[idx % 3]
                
                with col:
                    color = get_color_status(metric_key, metrics.get(metric_key, 0)) if metric_key != "daily_impressions" and metric_key != "daily_clicks" else "gray"
                    color_circle = "🟢" if color == "green" else "🟡" if color == "yellow" else "🔴" if color == "red" else "⚫"
                    
                    st.markdown(f"""
                    <div style='padding: 15px; border: 2px solid #ddd; border-radius: 8px; text-align: center;'>
                    <p style='margin: 0; font-size: 14px; color: #666;'>{metric_name} {color_circle}</p>
                    <h4 style='margin: 10px 0; color: #333;'>{current_val}</h4>
                    <p style='margin: 0; font-size: 12px; color: #999;'>Benchmark: {benchmark_val}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # SECTION 3: Trend Charts
            st.markdown("### 📈 Daily Trends")
            
            daily_data["date"] = pd.to_datetime(daily_data["date"])
            daily_data = daily_data.sort_values("date")
            
            chart_cols = st.columns(2)
            
            # CTR Trend
            with chart_cols[0]:
                daily_data["daily_ctr"] = (daily_data["clicks"] / daily_data["impressions"] * 100).fillna(0)
                fig_ctr = go.Figure()
                fig_ctr.add_trace(go.Scatter(
                    x=daily_data["date"], y=daily_data["daily_ctr"],
                    mode='lines', name='Daily CTR', line=dict(color='#1f77b4', width=2)
                ))
                fig_ctr.add_hline(y=BENCHMARKS["ctr"], line_dash="dash", line_color="green", 
                                 annotation_text=f"Benchmark: {BENCHMARKS['ctr']}%")
                fig_ctr.update_layout(title="CTR Trend", height=400, hovermode='x unified')
                st.plotly_chart(fig_ctr, use_container_width=True)
            
            # CPC Trend
            with chart_cols[1]:
                daily_data["daily_cpc"] = (daily_data["cost"] / daily_data["clicks"]).fillna(0)
                fig_cpc = go.Figure()
                fig_cpc.add_trace(go.Scatter(
                    x=daily_data["date"], y=daily_data["daily_cpc"],
                    mode='lines', name='Daily CPC', line=dict(color='#ff7f0e', width=2)
                ))
                fig_cpc.add_hline(y=BENCHMARKS["cpc"], line_dash="dash", line_color="green",
                                 annotation_text=f"Benchmark: ₹{BENCHMARKS['cpc']:.0f}")
                fig_cpc.update_layout(title="CPC Trend", height=400, hovermode='x unified')
                st.plotly_chart(fig_cpc, use_container_width=True)
            
            # Impressions & Clicks Trend
            chart_cols2 = st.columns(2)
            
            with chart_cols2[0]:
                fig_imp = go.Figure()
                fig_imp.add_trace(go.Bar(
                    x=daily_data["date"], y=daily_data["impressions"],
                    name='Impressions', marker_color='#2ca02c'
                ))
                fig_imp.update_layout(title="Daily Impressions", height=400, hovermode='x unified')
                st.plotly_chart(fig_imp, use_container_width=True)
            
            with chart_cols2[1]:
                fig_click = go.Figure()
                fig_click.add_trace(go.Bar(
                    x=daily_data["date"], y=daily_data["clicks"],
                    name='Clicks', marker_color='#d62728'
                ))
                fig_click.update_layout(title="Daily Clicks", height=400, hovermode='x unified')
                st.plotly_chart(fig_click, use_container_width=True)
            
            st.markdown("---")
            
            # SECTION 4: Top 3 Recommendations
            st.markdown("### 💡 Top 3 Optimization Recommendations")
            
            recommendations = generate_recommendations(metrics, daily_data)
            
            if not recommendations:
                st.success("✅ Campaign is performing well! Keep monitoring.")
            else:
                for idx, rec in enumerate(recommendations, 1):
                    priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                    
                    with st.expander(f"{priority_color[rec['priority']]} #{idx}: {rec['title']} ({rec['priority']} Priority})", expanded=(idx==1)):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **Current Value:** {rec['current']}
                            
                            **Benchmark:** {rec['benchmark']}
                            
                            **Gap:** {rec['gap']}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **Root Cause:**
                            
                            {rec['root_cause']}
                            """)
                        
                        st.markdown("---")
                        
                        st.markdown("**Recommended Actions:**")
                        for action in rec["actions"]:
                            st.markdown(f"• {action}")
                        
                        st.markdown("---")
                        
                        st.markdown(f"""
                        **Expected Impact:**
                        
                        {rec['impact']}
                        
                        **Expected Outcomes:**
                        """)
                        for outcome in rec["expected_outcome"]:
                            st.markdown(outcome)

# TAB 4: Reports
with tab4:
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
