# 🚀 Quick Setup Guide

## Step-by-Step Installation

### 1. Get Your Gemini API Key

1. Visit https://ai.google.dev/
2. Click "Get API Key" or "Get Started"
3. Sign in with your Google account
4. Create a new project or select existing one
5. Generate an API key
6. Copy the API key (starts with `AIza...`)

### 2. Configure the Application

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in a text editor and add your API key:
   ```env
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Run the Application

**Option A: Using the batch script (Windows)**
```bash
run.bat
```

**Option B: Manual start**

Terminal 1 (FastAPI):
```bash
venv\Scripts\activate
python main.py
```

Terminal 2 (Streamlit):
```bash
venv\Scripts\activate
streamlit run ui\streamlit_app.py
```

### 5. Access the Application

- **Web UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## Testing the Installation

1. Open http://localhost:8501
2. Enter a test repository: `https://github.com/tiangolo/fastapi`
3. Click "Generate README"
4. Wait for completion
5. Download the generated README

## Common Issues

### Issue: "Module not found" errors
**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "API key not configured" error
**Solution**: Check your `.env` file contains `GEMINI_API_KEY=your_key_here`

### Issue: Port already in use
**Solution**: Change ports in `.env`:
```env
FASTAPI_PORT=8001
STREAMLIT_PORT=8502
```

### Issue: Repository clone fails
**Solution**: Ensure you have:
- Active internet connection
- Valid repository URL
- Git installed on your system

## Next Steps

1. Read the full [README.md](README.md)
2. Check the [PROJECT_PLAN.md](PROJECT_PLAN.md)
3. Try generating READMEs for your own repositories
4. Customize the prompt templates in `prompts/` directory

## Support

If you encounter any issues:
1. Check the logs in `app.log`
2. Review error messages in the terminal
3. Ensure all prerequisites are met
4. Check the GitHub issues page

Happy README generating! 🎉
