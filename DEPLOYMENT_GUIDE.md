# BankNifty App Deployment Guide

## 🚀 Deploy to Render (24/7 Hosting)

### Step 1: Prepare Your GitHub Repository

1. **Create a GitHub repository:**
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it something like `banknifty-option-chain`
   - Make it public (or private if you prefer)

2. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - BankNifty Option Chain App"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/banknifty-option-chain.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Sign up for Render:**
   - Go to [render.com](https://render.com)
   - Sign up using your GitHub account

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository you just created

3. **Configure the deployment:**
   - **Name:** `banknifty-app` (or any name you prefer)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python start_services.py`
   - **Instance Type:** Choose "Free" for testing, "Starter" for production

4. **Set Environment Variables:**
   - In the Render dashboard, go to your service
   - Click "Environment" tab
   - Add any environment variables if needed

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically deploy your app
   - You'll get a URL like `https://your-app-name.onrender.com`

### Step 3: Verify Deployment

1. **Check health endpoint:**
   - Visit `https://your-app-name.onrender.com/health`
   - Should return JSON with status "healthy"

2. **Check main app:**
   - Visit `https://your-app-name.onrender.com`
   - Your BankNifty option chain should load

## 📁 GitHub CSV Storage Setup

### Step 1: Create GitHub Personal Access Token

1. **Go to GitHub Settings:**
   - Click your profile picture → Settings
   - Scroll down to "Developer settings"
   - Click "Personal access tokens" → "Tokens (classic)"

2. **Generate new token:**
   - Click "Generate new token (classic)"
   - Give it a name like "BankNifty CSV Storage"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

### Step 2: Add Token to Your App

1. **Update token.txt file:**
   - Open `token.txt` in your project
   - Add your GitHub token:
   ```
   # Your existing Fyers token stays here
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Add your GitHub token below
   github_token=ghp_your_github_token_here
   ```

2. **Create a repository for CSV storage:**
   - Create another GitHub repository called `banknifty-data`
   - This will store your CSV files

### Step 3: Test CSV Storage

1. **Run the GitHub storage test:**
   ```bash
   python github_storage.py
   ```

2. **Use in your app:**
   ```python
   from github_storage import save_csv_to_github, save_option_chain_to_github
   
   # Save any CSV file
   success, message = save_csv_to_github("path/to/your/file.csv")
   
   # Save option chain data directly
   success, message = save_option_chain_to_github(option_chain_data)
   ```

## 🔧 Files Added for Deployment

### New Files Created:

1. **`requirements.txt`** - Python dependencies
2. **`Procfile`** - Tells Render how to start your app
3. **`runtime.txt`** - Specifies Python version
4. **`start_services.py`** - Startup script for background services
5. **`github_storage.py`** - GitHub integration for CSV storage
6. **`.gitignore`** - Excludes unnecessary files from Git

### Modified Files:

1. **`web_app.py`** - Added health check endpoints and Render compatibility
2. **`token.txt`** - Added placeholder for GitHub token

## 🌐 Accessing Your App

Once deployed, your app will be available at:
- **Main App:** `https://your-app-name.onrender.com`
- **Health Check:** `https://your-app-name.onrender.com/health`
- **API Status:** `https://your-app-name.onrender.com/api/status`

## 📊 Features Available 24/7

Your deployed app will have:
- ✅ Real-time option chain data
- ✅ Multiple trading views (Index, OI-LTP, Trade, etc.)
- ✅ Futures details and charts
- ✅ Automatic data updates
- ✅ CSV export to GitHub
- ✅ Health monitoring
- ✅ Background services running

## 🔄 Updating Your App

To update your deployed app:
1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Render will automatically redeploy your app

## 💡 Tips for Production

1. **Monitor your app:**
   - Check the health endpoint regularly
   - Monitor Render logs for any issues

2. **Backup important data:**
   - CSV files are automatically backed up to GitHub
   - Keep your token.txt file safe

3. **Scale if needed:**
   - Upgrade to paid Render plan for better performance
   - Consider using environment variables for sensitive data

## 🆘 Troubleshooting

### Common Issues:

1. **App not starting:**
   - Check Render logs for errors
   - Verify all dependencies in requirements.txt

2. **GitHub storage not working:**
   - Verify your GitHub token is correct
   - Check repository permissions

3. **Data not updating:**
   - Check if Fyers API token is valid
   - Verify market hours and data availability

### Getting Help:

- Check Render logs in the dashboard
- Visit health endpoint to see app status
- Review GitHub repository for any issues

## 🎉 Success!

Your BankNifty Option Chain app is now running 24/7 on Render with automatic CSV backup to GitHub!

**Your app URL:** `https://your-app-name.onrender.com`
**CSV Storage:** `https://github.com/YOUR_USERNAME/banknifty-data`