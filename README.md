# 📊 Google Ads Automation Dashboard

A Streamlit-based dashboard to monitor and analyze your Google Ads campaigns in real-time.

## ✨ Features

- 🔍 **Status Tab**: Check API connection status
- 📈 **Campaigns Tab**: View all campaign metrics and performance data
- 📋 **Reports Tab**: Generate comprehensive campaign reports
- 📥 **Download**: Export data as CSV or reports as TXT
- 🎯 **Real-time Data**: Fetches latest data on demand
- 🔐 **Secure**: Credentials stored safely in Streamlit Cloud secrets

## 📋 Requirements

- Google Ads account with API access
- 4 required credentials:
  1. `DEVELOPER_TOKEN`
  2. `LOGIN_CUSTOMER_ID`
  3. `OPERATING_CUSTOMER_ID`
  4. `SERVICE_ACCOUNT_JSON`

## 🚀 Deployment to Streamlit Cloud

### Step 1: Prepare Your GitHub Repository

1. Create a new GitHub repository: `google-ads-dashboard`
2. Add these files:
   ```
   streamlit_app.py
   requirements.txt
   README.md
   .gitignore (optional)
   ```

3. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select:
   - Repository: your `google-ads-dashboard` repo
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Click "Deploy"

### Step 3: Add Secrets

1. In Streamlit Cloud dashboard
2. Click your app → **Settings** ⚙️
3. Click **"Secrets"**
4. Paste your secrets in TOML format:

```toml
DEVELOPER_TOKEN = "your_developer_token_here"
LOGIN_CUSTOMER_ID = "your_login_customer_id"
OPERATING_CUSTOMER_ID = "your_operating_customer_id"
SERVICE_ACCOUNT_JSON = """your_complete_json_here"""
```

**Important:** For `SERVICE_ACCOUNT_JSON`, paste the **entire JSON** file content (starts with `{` and ends with `}`)

### Step 4: Done!

Your app will deploy automatically in 2-3 minutes! 🎉

---

## 📱 Usage

### Status Tab
Shows if your Google Ads API connection is working correctly.

### Campaigns Tab
1. Click "🔄 Fetch Campaign Data"
2. View all enabled campaigns
3. See metrics:
   - Impressions
   - Clicks
   - CTR (Click-through rate)
   - Cost (in ₹)
   - CPC (Cost per click)
   - Conversions
4. Download data as CSV

### Reports Tab
1. Click "📄 Generate Full Report"
2. View comprehensive report with:
   - Summary metrics
   - Campaign-by-campaign breakdown
   - Cost analysis
   - Conversion data
3. Download report as TXT file

---

## 🔑 Getting Your Credentials

### 1. DEVELOPER_TOKEN
- Go to: https://ads.google.com/aw/apicenter
- Copy your Developer Token

### 2. LOGIN_CUSTOMER_ID
- Go to: https://ads.google.com/aw/overview
- Click the ID in top right (Manager account ID)
- Remove hyphens if any

### 3. OPERATING_CUSTOMER_ID
- Same location as LOGIN_CUSTOMER_ID
- Use your actual account ID (client ID)
- Remove hyphens if any

### 4. SERVICE_ACCOUNT_JSON
- Go to: https://console.cloud.google.com
- Create a Service Account
- Download the JSON key file
- Copy the entire content
- Paste in Streamlit Cloud Secrets

---

## 🛠️ Local Development

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/google-ads-dashboard.git
cd google-ads-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Create .streamlit/secrets.toml (Local Testing Only)
```toml
DEVELOPER_TOKEN = "your_token"
LOGIN_CUSTOMER_ID = "your_id"
OPERATING_CUSTOMER_ID = "your_id"
SERVICE_ACCOUNT_JSON = """your_json"""
```

### Run Locally
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## 📊 Metrics Explained

- **Impressions**: Number of times your ads were displayed
- **Clicks**: Number of times users clicked your ads
- **CTR (Click-through Rate)**: (Clicks ÷ Impressions) × 100
- **Cost**: Total amount spent (in Indian Rupees)
- **CPC (Cost per Click)**: Total Cost ÷ Clicks
- **Conversions**: Number of tracked conversions from ads

---

## ⚠️ Troubleshooting

### Blank Page
- Hard refresh browser (Ctrl+Shift+R)
- Check Streamlit Cloud console for errors

### "Not configured" Error
- Verify all 4 secrets are added in Streamlit Cloud
- Check secret names are exact
- Service account JSON must include entire content

### "No campaign data found"
- Campaign may be in learning phase (1-2 weeks for new campaigns)
- Ensure campaign is ENABLED in Google Ads
- Check you have the correct OPERATING_CUSTOMER_ID

### Connection Error
- Verify credentials are not expired
- Check service account has proper permissions
- Ensure API is enabled in Google Cloud

---

## 🔐 Security Notes

- Never commit secrets to GitHub
- Use Streamlit Cloud's Secrets management
- Service account should have minimal required permissions
- Regularly rotate your service account keys

---

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Google Ads API Docs](https://developers.google.com/google-ads/api)
- [Streamlit Cloud Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 💬 Support

For issues:
1. Check the troubleshooting section
2. Review Streamlit Cloud logs
3. Check Google Ads API documentation

---

**Happy monitoring! 📊**
