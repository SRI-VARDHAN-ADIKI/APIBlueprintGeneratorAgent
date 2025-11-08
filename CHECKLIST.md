# ✅ Getting Started Checklist

Follow these steps to get your README Generator Agent up and running!

## Prerequisites Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] Internet connection (for cloning repos and API calls)
- [ ] Google account (for Gemini API key)

## Setup Checklist

### 1. Get API Key
- [ ] Visit https://ai.google.dev/
- [ ] Sign in with Google account
- [ ] Create or select a project
- [ ] Generate API key
- [ ] Copy the API key (save it somewhere safe)

### 2. Project Setup
- [ ] Navigate to project directory: `cd Readme_Generator_Agent`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`

### 3. Configuration
- [ ] Copy `.env.example` to `.env`: `copy .env.example .env`
- [ ] Open `.env` in a text editor
- [ ] Paste your Gemini API key: `GEMINI_API_KEY=your_key_here`
- [ ] Save the file

### 4. Verify Installation
- [ ] Check if all packages installed: `pip list`
- [ ] Verify FastAPI: `python -c "import fastapi; print('FastAPI OK')"`
- [ ] Verify Streamlit: `python -c "import streamlit; print('Streamlit OK')"`
- [ ] Verify LangChain: `python -c "import langchain; print('LangChain OK')"`

## Running the Application

### Option 1: Quick Start (Windows)
- [ ] Run the batch file: `run.bat`
- [ ] Wait for both servers to start
- [ ] Browser should open automatically

### Option 2: Manual Start
- [ ] Terminal 1: Start FastAPI
  - [ ] Activate venv: `venv\Scripts\activate`
  - [ ] Run: `python main.py`
  - [ ] Verify: http://localhost:8000
  - [ ] Check docs: http://localhost:8000/docs

- [ ] Terminal 2: Start Streamlit
  - [ ] Activate venv: `venv\Scripts\activate`
  - [ ] Run: `streamlit run ui\streamlit_app.py`
  - [ ] Verify: http://localhost:8501

## First Test

- [ ] Open Streamlit UI: http://localhost:8501
- [ ] Check that API is connected (green status)
- [ ] Enter test repository: `https://github.com/tiangolo/fastapi`
- [ ] Select options:
  - [ ] Length: Medium
  - [ ] Style: Technical
  - [ ] Check: Overview, Installation, API Documentation
  - [ ] Include examples: Yes
- [ ] Click "Generate README"
- [ ] Wait for completion (1-2 minutes)
- [ ] Preview the generated README
- [ ] Download the file

## Verification

### Backend Checks
- [ ] FastAPI running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns OK: http://localhost:8000/api/health
- [ ] No error messages in terminal

### Frontend Checks
- [ ] Streamlit UI loads correctly
- [ ] All customization options visible
- [ ] API connection indicator shows "connected"
- [ ] No error messages

### Functionality Checks
- [ ] Can submit a repository URL
- [ ] Progress bar updates
- [ ] Status messages appear
- [ ] Preview shows content
- [ ] Download button works
- [ ] README file downloads correctly

## Troubleshooting Checklist

If something doesn't work:

### API Key Issues
- [ ] API key is correctly copied in `.env`
- [ ] No extra spaces in the API key
- [ ] API key starts with `AIza`
- [ ] Quota not exceeded on Google AI Studio

### Import Errors
- [ ] Virtual environment is activated
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Using correct Python version: `python --version`
- [ ] No conflicting package versions

### Port Issues
- [ ] Ports 8000 and 8501 are not in use
- [ ] No firewall blocking the ports
- [ ] Can access http://localhost:8000 in browser

### Repository Clone Issues
- [ ] Internet connection is active
- [ ] Repository URL is correct and public
- [ ] Git is installed and accessible
- [ ] Sufficient disk space

## Common Issues & Solutions

### "Module not found"
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

### "API key not configured"
```bash
# Solution: Check .env file
cat .env  # Linux/Mac
type .env  # Windows
```

### "Port already in use"
```bash
# Solution: Change port in .env
FASTAPI_PORT=8001
STREAMLIT_PORT=8502
```

### "Connection refused"
```bash
# Solution: Ensure FastAPI is running
# Check if you can access http://localhost:8000/api/health
```

## Success Criteria

You know everything is working when:
- [✓] Both servers start without errors
- [✓] UI loads and shows "API Connected"
- [✓] You can submit a repository URL
- [✓] Progress updates appear
- [✓] README is generated successfully
- [✓] You can preview and download the README

## Next Steps After Setup

- [ ] Read the full [README.md](README.md)
- [ ] Review [PROJECT_PLAN.md](PROJECT_PLAN.md)
- [ ] Try different repository types
- [ ] Experiment with customization options
- [ ] Modify prompts in `prompts/` directory
- [ ] Add your own parsers for other languages
- [ ] Deploy to production (Heroku, AWS, etc.)

## Need Help?

1. Check the logs: `app.log`
2. Read error messages carefully
3. Review documentation files
4. Ensure all prerequisites are met
5. Try the troubleshooting steps above

---

**Once all checkboxes are complete, you're ready to generate amazing READMEs! 🎉**
