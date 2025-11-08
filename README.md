# 📝 README Generator Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-Powered README & API Blueprint Generator** - Automatically generate comprehensive, customizable README files and API documentation from any Git repository using Gemini 2.0 Flash and LangChain agents.

## 🌟 Features

- **🤖 AI-Powered Generation**: Uses Google's Gemini 2.0 Flash model for intelligent documentation
- **🎯 Smart Code Analysis**: AST-based parsing for Python, JavaScript, TypeScript, and more
- **📡 API Endpoint Detection**: Automatically identifies and documents REST API routes
- **📊 Mermaid Diagrams**: Generates sequence diagrams, architecture diagrams, and ER diagrams
- **🎨 Customizable Output**: Control README length, style, sections, and complexity
- **⚡ Real-time Progress**: Track generation progress with live status updates
- **🌐 Web Interface**: Beautiful Streamlit UI for easy interaction
- **🚀 Fast API Backend**: RESTful API for programmatic access
- **📦 Multiple Frameworks**: Supports FastAPI, Flask, Django, Express, and more

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  ← User Interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │  ← REST API Server
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Orchestrator Agent              │  ← Main Coordinator
└──────┬──────────────────────────────┘
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌─────────────┐            ┌──────────────────┐
│  Repo       │            │  README          │
│  Analyzer   │            │  Generator       │
│  Agent      │            │  Agent           │
└──────┬──────┘            └────────┬─────────┘
       │                            │
       ▼                            ▼
┌─────────────┐            ┌──────────────────┐
│  AST Parser │            │  Mermaid         │
│  & Endpoint │            │  Diagram Gen.    │
│  Extractor  │            │                  │
└─────────────┘            └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Gemini API Key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/tanojrahul/Readme_Generator_Agent.git](https://github.com/SRI-VARDHAN-ADIKI/APIBlueprintGeneratorAgent.git)
   cd Readme_Generator_Agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_api_key_here
   ```

### Running the Application

#### Option 1: Using the Startup Script (Windows)

```bash
run.bat
```

This will automatically start both the FastAPI server and Streamlit UI.

#### Option 2: Manual Start

**Terminal 1 - Start FastAPI Server:**
```bash
python run_production.py
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run ui/streamlit_app.py
```

### Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📖 Usage

### Using the Web Interface

1. Open http://localhost:8501 in your browser
2. Enter a GitHub repository URL
3. Customize the following options:
   - **README Length**: Short (100-300 lines), Medium (300-600 lines), or Detailed (600-1000+ lines)
   - **Documentation Style**: Technical, Beginner-Friendly, or Comprehensive
   - **Sections**: Select which sections to include (Overview, Installation, API Docs, etc.)
   - **Diagram Complexity**: Simple or Detailed
   - **Code Examples**: Toggle inclusion of usage examples
4. Click "Generate README"
5. Monitor real-time progress
6. Preview and download your README

### Using the API

#### Generate README

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repository",
    "length": "medium",
    "sections": ["overview", "installation", "api_documentation", "usage_examples"],
    "include_examples": true,
    "diagram_complexity": "detailed",
    "style": "technical"
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "README generation started",
  "estimated_time_seconds": 120
}
```

#### Check Status

```bash
curl "http://localhost:8000/api/status/{job_id}"
```

#### Download README

```bash
curl "http://localhost:8000/api/download/{job_id}" -o README.md
```

## 🎯 Customization Options

### README Length

- **Short** (100-300 lines): Quick overview and essentials
- **Medium** (300-600 lines): Balanced documentation
- **Detailed** (600-1000+ lines): Comprehensive coverage

### Documentation Styles

- **Technical**: Precise terminology for experienced developers
- **Beginner-Friendly**: Clear explanations with context
- **Comprehensive**: Maximum detail and coverage

### Available Sections

- ✅ Project Overview
- ✅ Features List
- ✅ Installation Guide
- ✅ Configuration
- ✅ API Documentation
- ✅ Usage Examples
- ✅ Architecture Overview
- ✅ Contributing Guidelines
- ✅ License Information
- ✅ Troubleshooting
- ✅ FAQ

### Diagram Types

- **Sequence Diagrams**: API request/response flows
- **Architecture Diagrams**: System component interactions
- **ER Diagrams**: Data model relationships
- **Flowcharts**: Process flows

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance REST API framework
- **LangChain**: Agent orchestration and workflow management
- **Gemini 2.0 Flash**: Google's advanced LLM for text generation
- **GitPython**: Git repository operations

### Frontend
- **Streamlit**: Interactive web application framework

### Code Analysis
- **Python AST**: Built-in Abstract Syntax Tree parser
- **Esprima**: JavaScript/TypeScript parser
- **Javalang**: Java code parser

### Utilities
- **Pydantic**: Data validation and settings management
- **Mermaid**: Diagram generation
- **Uvicorn**: ASGI server

## 📁 Project Structure

```
Readme_Generator_Agent/
├── app/
│   ├── agents/              # LangChain agents
│   │   ├── orchestrator.py  # Main coordinator
│   │   ├── repo_analyzer.py # Repository analysis
│   │   └── readme_generator.py # README generation
│   ├── api/
│   │   └── routes.py        # FastAPI endpoints
│   ├── models/              # Pydantic models
│   ├── parsers/             # Code parsers
│   │   ├── python_parser.py # Python AST parser
│   │   └── base_parser.py   # Parser interface
│   ├── services/            # Core services
│   │   ├── git_service.py   # Git operations
│   │   ├── llm_service.py   # Gemini integration
│   │   └── mermaid_service.py # Diagram generation
│   ├── utils/               # Utility functions
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI app
├── ui/
│   └── streamlit_app.py     # Streamlit interface
├── prompts/                 # LLM prompts
├── tests/                   # Unit tests
├── temp/                    # Temporary repos
├── outputs/                 # Generated READMEs
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── run.bat                  # Startup script
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## 📊 Example Output

The agent generates professional README files with:

- **Clear structure** with hierarchical headers
- **Code blocks** with syntax highlighting
- **Tables** for structured data
- **Badges** for technology stack and status
- **Mermaid diagrams** embedded in markdown
- **Complete API documentation** with endpoints, parameters, and examples
- **Usage examples** with practical code snippets

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for a detailed project plan and architecture.

## 🔧 Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
MAX_REPO_SIZE_MB=500
CLONE_TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8000
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language understanding
- LangChain for agent orchestration
- FastAPI for the excellent web framework
- Streamlit for the intuitive UI framework

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing documentation
- Review the [PROJECT_PLAN.md](PROJECT_PLAN.md) for architecture details

## 🗺️ Roadmap

- [ ] Support for more programming languages (Ruby, PHP, C#)
- [ ] GitHub Actions integration
- [ ] Custom template support
- [ ] Multi-language README generation
- [ ] API versioning detection
- [ ] Automatic dependency updates in README
- [ ] Integration with CI/CD pipelines
- [ ] README quality scoring
- [ ] Collaborative editing features

## 🎬 Demo

[Add demo video or screenshots here]

---

**Built with ❤️ using AI and modern Python frameworks**
"# APIBlueprintGeneratorAgent" 
