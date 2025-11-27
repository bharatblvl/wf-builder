"""
Workflows Application - Multi-page Streamlit app for running all generated workflows
This is a separate application that runs on its own port and displays all workflows as pages.
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Workflows",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directories
PAGES_DIR = Path(__file__).parent / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)
WORKFLOWS_REGISTRY = PAGES_DIR / ".workflows.json"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .workflow-card {
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
        transition: all 0.3s;
    }
    .workflow-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)


def load_workflows_registry():
    """Load workflows registry"""
    if WORKFLOWS_REGISTRY.exists():
        try:
            with open(WORKFLOWS_REGISTRY, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def get_available_workflows():
    """Get list of available workflow pages"""
    registry = load_workflows_registry()
    workflows = []
    
    for page_num, info in sorted(registry.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        filename = info.get('filename', '')
        page_path = PAGES_DIR / filename
        
        if page_path.exists():
            workflows.append({
                'page_num': page_num,
                'filename': filename,
                'workflow_name': info.get('workflow_name', 'Unnamed Workflow'),
                'created_at': info.get('created_at', ''),
                'page_path': page_path
            })
    
    return workflows


def main():
    """Home page for workflows application"""
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Workflows Application</h1>
        <p>Run and interact with all your generated workflows</p>
        <p style="font-size: 0.9em; opacity: 0.9;">Navigate to any workflow using the sidebar menu</p>
    </div>
    """, unsafe_allow_html=True)
    
    workflows = get_available_workflows()
    
    if not workflows:
        st.info("""
        📭 **No workflows available yet!**
        
        To create workflows:
        1. Open the **Workflow Builder** application
        2. Generate your workflows
        3. They will automatically appear here
        """)
        
        st.markdown("---")
        st.subheader("🚀 Launch Workflow Builder")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.info("Run the Workflow Builder on a separate port to create new workflows:")
            st.code("streamlit run dashboard.py --server.port 8501", language="bash")
        
        return
    
    st.subheader(f"📋 Available Workflows ({len(workflows)})")
    st.markdown("Select a workflow from the sidebar to run it, or browse below:")
    
    # Display workflow cards
    cols = st.columns(3)
    for idx, workflow in enumerate(workflows):
        with cols[idx % 3]:
            created_date = ""
            if workflow['created_at']:
                try:
                    dt = datetime.fromisoformat(workflow['created_at'])
                    created_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    created_date = workflow['created_at']
            
            st.markdown(f"""
            <div class="workflow-card">
                <h4>⚙️ {workflow['workflow_name']}</h4>
                <p><small>📄 {workflow['filename']}</small></p>
                <p><small>🕒 {created_date}</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Tip:** Use the sidebar menu on the left to navigate directly to any workflow page.")


if __name__ == "__main__":
    main()

