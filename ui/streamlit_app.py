"""
Streamlit UI for README Generator Agent.
"""
import streamlit as st
import requests
import time
from typing import Dict, Optional
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="README Generator Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def generate_readme(request_data: Dict) -> Optional[str]:
    """Submit README generation request."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=request_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['job_id']
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None


def get_job_status(job_id: str) -> Optional[Dict]:
    """Get job status."""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{job_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_preview(job_id: str) -> Optional[Dict]:
    """Get README preview."""
    try:
        response = requests.get(f"{API_BASE_URL}/preview/{job_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def download_readme(job_id: str) -> Optional[str]:
    """Download README file."""
    try:
        response = requests.get(f"{API_BASE_URL}/download/{job_id}", timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">README Generator Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered API Documentation & README Generator</div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API server is not running! Please start the FastAPI server first.")
        st.code("python app/main.py", language="bash")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Repository URL
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/user/repository",
            help="Enter the full URL of the GitHub repository"
        )
        
        st.markdown("---")
        
        # README Length
        length = st.selectbox(
            "README Length",
            options=["short", "medium", "detailed"],
            index=1,
            help="Select the desired length of the README"
        )
        
        # Documentation Style
        style = st.selectbox(
            "Documentation Style",
            options=["technical", "beginner_friendly", "comprehensive"],
            index=0,
            help="Choose the writing style for the documentation"
        )
        
        # Sections to include
        st.subheader("Sections to Include")
        sections = []
        
        col1, col2 = st.columns(2)
        with col1:
            if st.checkbox("Overview", value=True):
                sections.append("overview")
            if st.checkbox("Features", value=True):
                sections.append("features")
            if st.checkbox("Installation", value=True):
                sections.append("installation")
            if st.checkbox("Configuration", value=False):
                sections.append("configuration")
            if st.checkbox("API Documentation", value=True):
                sections.append("api_documentation")
        
        with col2:
            if st.checkbox("Usage Examples", value=True):
                sections.append("usage_examples")
            if st.checkbox("Architecture", value=False):
                sections.append("architecture")
            if st.checkbox("Contributing", value=False):
                sections.append("contributing")
            if st.checkbox("License", value=False):
                sections.append("license")
            if st.checkbox("Troubleshooting", value=False):
                sections.append("troubleshooting")
        
        # Additional options
        st.markdown("---")
        include_examples = st.checkbox("Include Code Examples", value=True)
        diagram_complexity = st.selectbox(
            "Diagram Complexity",
            options=["simple", "detailed"],
            index=1
        )
        
        # Custom instructions
        custom_instructions = st.text_area(
            "Custom Instructions (Optional)",
            placeholder="Any specific requirements or customizations..."
        )
        
        st.markdown("---")
        
        # Generate button
        generate_button = st.button("Generate README", type="primary", use_container_width=True)
    
    # Main content area
    if generate_button:
        if not repo_url:
            st.error("Please enter a repository URL")
            return
        
        if not sections:
            st.error("Please select at least one section to include")
            return
        
        # Prepare request
        request_data = {
            "repo_url": repo_url,
            "length": length,
            "sections": sections,
            "include_examples": include_examples,
            "diagram_complexity": diagram_complexity,
            "style": style,
            "custom_instructions": custom_instructions if custom_instructions else None
        }
        
        # Submit request
        with st.spinner("Submitting request..."):
            job_id = generate_readme(request_data)
        
        if job_id:
            st.session_state['job_id'] = job_id
            st.success(f"✅ Job created! Job ID: {job_id}")
    
    # Show job progress
    if 'job_id' in st.session_state:
        job_id = st.session_state['job_id']
        
        st.markdown("---")
        st.header("Generation Progress")
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            message_placeholder = st.empty()
            
            # Poll for status
            max_polls = 60  # 5 minutes max
            for i in range(max_polls):
                status = get_job_status(job_id)
                
                if status:
                    progress = status.get('progress', 0)
                    message = status.get('message', '')
                    job_status = status.get('status', 'pending')
                    
                    status_placeholder.info(f"**Status:** {job_status.upper()}")
                    progress_bar.progress(progress / 100)
                    message_placeholder.text(message)
                    
                    if job_status == 'completed':
                        st.balloons()
                        break
                    elif job_status == 'failed':
                        error = status.get('error', 'Unknown error')
                        st.error(f"Generation failed: {error}")
                        break
                
                time.sleep(5)
            
            # Show preview if completed
            if status and status.get('status') == 'completed':
                st.markdown("---")
                st.header("README Preview")
                
                preview_data = get_preview(job_id)
                
                if preview_data:
                    # Repository info
                    repo_info = preview_data.get('repository_info', {})
                    st.subheader("Repository Information")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Files", repo_info.get('total_files', 0))
                    with col2:
                        st.metric("Total Lines", repo_info.get('total_lines', 0))
                    with col3:
                        st.metric("API Endpoints", repo_info.get('endpoints_found', 0))
                    with col4:
                        languages = ', '.join(repo_info.get('languages', []))
                        st.metric("Languages", len(repo_info.get('languages', [])))
                    
                    st.markdown(f"**Languages:** {languages}")
                    st.markdown(f"**Frameworks:** {', '.join(repo_info.get('frameworks', []))}")
                    
                    # Statistics
                    stats = preview_data.get('statistics', {})
                    st.subheader("README Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Lines", stats.get('line_count', 0))
                    with col2:
                        st.metric("Words", stats.get('word_count', 0))
                    with col3:
                        st.metric("Characters", stats.get('character_count', 0))
                    
                    # README content
                    st.markdown("---")
                    st.subheader("Generated README")
                    
                    readme_content = preview_data.get('readme_content', '')
                    st.markdown(readme_content)
                    
                    # Download button
                    st.markdown("---")
                    st.download_button(
                        label="⬇️ Download README.md",
                        data=readme_content,
                        file_name="README.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    # Clear job button
                    if st.button("🔄 Generate Another", use_container_width=True):
                        del st.session_state['job_id']
                        st.rerun()


if __name__ == "__main__":
    main()
