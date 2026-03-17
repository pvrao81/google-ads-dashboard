# 🚀 STREAMLIT CLOUD DEPLOYMENT GUIDE

## Complete Step-by-Step Instructions

---

## PART 1: Prepare Files for GitHub

### Files You Need:
1. `streamlit_app.py` - Main application code
2. `requirements.txt` - Python dependencies
3. `README.md` - Documentation

### Copy These Exact File Contents:

#### File 1: streamlit_app.py
Copy the entire content from `streamlit_app_GITHUB.py`

#### File 2: requirements.txt
```
streamlit==1.40.0
google-ads==29.2.0
pandas>=2.0.0
```

#### File 3: README.md
Copy from `README_GITHUB.md`

---

## PART 2: Create GitHub Repository

### Step 1: Create GitHub Account
1. Go to https://github.com/signup
2. Create free account
3. Verify email

### Step 2: Create New Repository
1. Go to https://github.com/new
2. Fill in:
   ```
   Repository name: google-ads-dashboard
   Description: Google Ads Automation Dashboard
   Public or Private: Public (recommended for free)
   ```
3. Click "Create repository"

### Step 3: Add Files to Repository
**Option A: Upload via Browser (Easiest)**
1. Go to your new repo
2. Click "Add file" → "Upload files"
3. Select 3 files:
   - streamlit_app.py
   - requirements.txt
   - README.md
4. Click "Commit changes"

**Option B: Use Git Commands**
```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/google-ads-dashboard.git
cd google-ads-dashboard

# Create files
# (Create streamlit_app.py, requirements.txt, README.md)

# Push to GitHub
git add .
git commit -m "Initial commit: Google Ads Dashboard"
git push origin main
```

---

## PART 3: Deploy to Streamlit Cloud

### Step 1: Sign Up for Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click "Sign up"
3. Choose "Sign up with GitHub"
4. Authorize Streamlit

### Step 2: Deploy Your App
1. In Streamlit Cloud dashboard
2. Click "New app" button
3. Fill in:
   ```
   Repository: YOUR-USERNAME/google-ads-dashboard
   Branch: main
   Main file path: streamlit_app.py
   ```
4. Click "Deploy"

**Wait 2-3 minutes for deployment...**

Your app URL will be: `https://google-ads-dashboard-YOUR-USERNAME.streamlit.app`

### Step 3: Add Your Secrets

⚠️ **IMPORTANT: Do this BEFORE testing the app!**

1. In Streamlit Cloud dashboard
2. Click your app name
3. Click **Settings** ⚙️ (top right)
4. Click **"Secrets"** in sidebar
5. Paste your secrets in this format:

```toml
DEVELOPER_TOKEN = "abc123xyz789..."
LOGIN_CUSTOMER_ID = "1234567890"
OPERATING_CUSTOMER_ID = "9876543210"
SERVICE_ACCOUNT_JSON = """{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}"""
```

6. Click "Save"

---

## PART 4: Get Your Credentials

### Step 1: DEVELOPER_TOKEN
1. Go to: https://ads.google.com/aw/apicenter
2. Copy your "Developer Token"
3. Paste in secrets as `DEVELOPER_TOKEN`

### Step 2: LOGIN_CUSTOMER_ID & OPERATING_CUSTOMER_ID
1. Go to: https://ads.google.com/aw/overview
2. In top right, click the ID (shown as "ID: 1234-5678-9012")
3. Note the full ID
4. For LOGIN_CUSTOMER_ID: Use manager account ID (no hyphens)
5. For OPERATING_CUSTOMER_ID: Use your client account ID (no hyphens)

**Example:**
```
Manager ID: 1234567890 (LOGIN_CUSTOMER_ID)
Client ID: 9876543210 (OPERATING_CUSTOMER_ID)
```

### Step 3: SERVICE_ACCOUNT_JSON
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create a new service account:
   - Name: `google-ads-api`
   - Description: "For Google Ads API access"
   - Click "Create and Continue"
3. Grant roles:
   - Select role: "Editor" (or "Viewer" if available)
   - Click "Continue"
4. Create a JSON key:
   - Click "Create Key"
   - Select "JSON"
   - Click "Create"
5. A JSON file downloads
6. Open the file in Notepad
7. Copy the **entire content** (from `{` to `}`)
8. Paste in Streamlit secrets as `SERVICE_ACCOUNT_JSON`

---

## PART 5: Test Your Dashboard

### Step 1: Refresh Your App
1. Go to your app URL
2. Press Ctrl+Shift+R (hard refresh)
3. Wait 10 seconds

### Step 2: Check Status Tab
1. Click "🔍 Status" tab
2. Should show: "✅ Connected to Google Ads API!"
3. If not, check your secrets

### Step 3: Fetch Campaign Data
1. Click "📈 Campaigns" tab
2. Click "🔄 Fetch Campaign Data"
3. Your campaigns should appear! 🎉

### Step 4: Generate Report
1. Click "📋 Reports" tab
2. Click "📄 Generate Full Report"
3. Full report appears!

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] GitHub account created
- [ ] Repository created: `google-ads-dashboard`
- [ ] 3 files uploaded to GitHub:
  - [ ] streamlit_app.py
  - [ ] requirements.txt
  - [ ] README.md
- [ ] Streamlit Cloud account created
- [ ] App deployed from GitHub
- [ ] 4 secrets added:
  - [ ] DEVELOPER_TOKEN
  - [ ] LOGIN_CUSTOMER_ID
  - [ ] OPERATING_CUSTOMER_ID
  - [ ] SERVICE_ACCOUNT_JSON
- [ ] Status tab shows "Connected"
- [ ] Campaign data loads
- [ ] Report generates

---

## 🎉 YOU'RE DONE!

Your Google Ads Dashboard is now live on Streamlit Cloud! 🚀

**Your app URL:** `https://google-ads-dashboard-YOUR-USERNAME.streamlit.app`

---

## 📞 Quick Troubleshooting

### "Not configured" error
→ Check all 4 secrets are added exactly

### "No campaign data"
→ Campaign may be learning (1-2 weeks for new campaigns)

### Blank page
→ Hard refresh (Ctrl+Shift+R)

### Can't see app
→ Wait 3-5 minutes, refresh browser

---

## 🔗 Useful Links

- GitHub: https://github.com
- Streamlit Cloud: https://streamlit.io/cloud
- Google Cloud Console: https://console.cloud.google.com
- Google Ads: https://ads.google.com

---

**Happy monitoring! Your dashboard is live!** 📊✨
