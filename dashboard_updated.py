"""
Workflow Builder - Self-Healing Streamlit Workflow Generator
Multi-page Streamlit application - Home page
"""

import streamlit as st
from pathlib import Path
import subprocess
import sys
import os
from datetime import datetime
import json
import time
import uuid
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our code generation module
from crew_generator import generate_code, fix_code

# Page configuration
st.set_page_config(
    page_title="Workflow Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directories
PAGES_DIR = Path(__file__).parent / "pages"
PAGES_DIR.mkdir(exist_ok=True)

GENERATED_CODE_DIR = Path(__file__).parent / "generated_code"
GENERATED_CODE_DIR.mkdir(exist_ok=True)

# State files
TASKS_FILE = GENERATED_CODE_DIR / "tasks.json"
WORKFLOWS_REGISTRY = PAGES_DIR / ".workflows.json"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background: #fee2e2;
        border-left: 5px solid #ef4444;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #dbeafe;
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def extract_workflow_name(task_description):
    """Extract a clean workflow name from task description"""
    # Try to extract meaningful name from description
    words = task_description.lower().split()
    # Look for key phrases
    if 'create' in words:
        idx = words.index('create')
        if idx + 2 < len(words):
            # Get next few words after "create"
            name_words = words[idx+1:idx+4]
            name = '_'.join([w for w in name_words if len(w) > 3])[:30]
            if name:
                return name
    
    # Default: use first few meaningful words
    meaningful_words = [w for w in words[:5] if len(w) > 3 and w not in ['the', 'that', 'this', 'with']]
    if meaningful_words:
        return '_'.join(meaningful_words[:3])[:30]
    
    return "workflow"


def load_workflows_registry():
    """Load workflows registry"""
    if WORKFLOWS_REGISTRY.exists():
        try:
            with open(WORKFLOWS_REGISTRY, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_workflow_registry(registry):
    """Save workflows registry"""
    with open(WORKFLOWS_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)


def load_tasks():
    """Load saved tasks"""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_task(task_id, task_description, status="pending", page_file=None):
    """Save task"""
    tasks = load_tasks()
    tasks[task_id] = {
        "description": task_description,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "page_file": page_file
    }
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)


def get_next_page_number():
    """Get next page number for naming"""
    registry = load_workflows_registry()
    if not registry:
        return 1
    max_num = max([int(k) for k in registry.keys() if k.isdigit()], default=0)
    return max_num + 1


def save_as_page(code, workflow_name, task_id):
    """Save generated code as a Streamlit page"""
    page_num = get_next_page_number()
    
    # Clean workflow name for filename
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', workflow_name[:30])
    filename = f"{page_num}_{clean_name}.py"
    filepath = PAGES_DIR / filename
    
    # Clean code - remove st.set_page_config and main blocks
    code_lines = code.split('\n')
    cleaned_lines = []
    in_page_config = False
    in_main_block = False
    indent_level = 0
    
    for line in code_lines:
        # Skip st.set_page_config blocks
        if 'st.set_page_config' in line:
            in_page_config = True
            continue
        if in_page_config:
            if ')' in line and line.strip().startswith(')'):
                in_page_config = False
            continue
        
        # Skip if __name__ == "__main__" blocks
        if 'if __name__' in line and '__main__' in line:
            in_main_block = True
            indent_level = len(line) - len(line.lstrip())
            continue
        if in_main_block:
            current_indent = len(line) - len(line.lstrip()) if line.strip() else 0
            if line.strip() and current_indent <= indent_level:
                in_main_block = False
                if line.strip().startswith('if'):
                    continue
        
        if not in_main_block:
            cleaned_lines.append(line)
    
    cleaned_code = '\n'.join(cleaned_lines).strip()
    
    # Write page file
    with open(filepath, 'w') as f:
        f.write(cleaned_code)
    
    # Update registry
    registry = load_workflows_registry()
    registry[str(page_num)] = {
        "filename": filename,
        "workflow_name": workflow_name,
        "task_id": task_id,
        "created_at": datetime.now().isoformat()
    }
    save_workflow_registry(registry)
    
    return filepath, page_num


def test_code_execution(code_path, timeout=15):
    """Test if the code runs without errors"""
    code_path = Path(code_path).resolve()
    
    try:
        if not code_path.exists():
            return False, f"File not found: {code_path}"
        
        # Syntax check
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(code_path)],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore') or result.stdout.decode('utf-8', errors='ignore')
            return False, f"Syntax Error: {error_msg}"
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, "Code validation timed out"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def render_header():
    """Render header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Workflow Builder</h1>
        <p>Describe your workflow in plain English, and we'll build it for you!</p>
        <p style="font-size: 0.9em; opacity: 0.9;">All workflows run as pages in this multi-page app</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application"""
    render_header()
    
    # Initialize session state
    if 'task_id' not in st.session_state:
        st.session_state.task_id = None
    if 'task_description' not in st.session_state:
        st.session_state.task_description = ""
    if 'generation_attempt' not in st.session_state:
        st.session_state.generation_attempt = 0
    if 'current_error' not in st.session_state:
        st.session_state.current_error = None
    
    # Show existing workflows
    registry = load_workflows_registry()
    if registry:
        st.subheader("📋 Your Workflows")
        cols = st.columns(3)
        for idx, (page_num, info) in enumerate(sorted(registry.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)):
            with cols[idx % 3]:
                workflow_name = info.get('workflow_name', 'Unnamed Workflow')
                filename = info.get('filename', '')
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                    <strong>📄 {workflow_name}</strong><br>
                    <small>Page: {filename}</small>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Main input area
    st.subheader("📝 Create New Workflow")
    
    task_description = st.text_area(
        "Tell us what kind of workflow you want to create:",
        height=150,
        placeholder="Example: Create a Streamlit app that takes transaction data and analyzes which transactions are fraudulent using OpenAI GPT-3.5-turbo. Include a header, footer, and modern UI with visual indicators.",
        value=st.session_state.task_description
    )
    
    # Check for API key
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if not api_key_set:
            st.button("✨ Generate Workflow", type="primary", use_container_width=True, disabled=True)
            st.caption("⚠️ API key required")
        else:
            generate_button = st.button("✨ Generate Workflow", type="primary", use_container_width=True)
    with col2:
        if not api_key_set:
            st.warning("⚠️ ANTHROPIC_API_KEY not found. Please set it in your .env file or environment variables.")
    
    # Handle generation
    if generate_button and api_key_set:
        if not task_description.strip():
            st.warning("⚠️ Please enter a task description before generating.")
        else:
            task_id = str(uuid.uuid4())[:8]
            st.session_state.task_id = task_id
            st.session_state.task_description = task_description
            st.session_state.generation_attempt = 1
            st.session_state.current_error = None
            st.session_state.generating = False
            save_task(task_id, task_description, "generating")
            st.rerun()
    
    # Show generation progress
    if st.session_state.task_id:
        task_id = st.session_state.task_id
        attempt = st.session_state.generation_attempt
        
        workflow_name = extract_workflow_name(st.session_state.task_description)
        
        # Check if page already exists
        registry = load_workflows_registry()
        existing_page = None
        for page_info in registry.values():
            if page_info.get('task_id') == task_id:
                existing_page = page_info.get('filename')
                break
        
        if existing_page:
            page_path = PAGES_DIR / existing_page
        else:
            page_path = None
        
        # Generation phase
        if not page_path or not page_path.exists():
            if not st.session_state.get('generating', False):
                st.session_state.generating = True
                
                try:
                    st.info(f"🤖 Generating your workflow (Attempt {attempt})... This may take a few moments.")
                    
                    if st.session_state.current_error:
                        # Fix mode
                        current_code = ""
                        if existing_page and page_path and page_path.exists():
                            current_code = page_path.read_text()
                        
                        with st.spinner("🔧 Fixing code based on error..."):
                            code = fix_code(
                                st.session_state.task_description,
                                st.session_state.current_error,
                                current_code
                            )
                    else:
                        # Initial generation
                        with st.spinner("✨ Creating your workflow from scratch..."):
                            code = generate_code(st.session_state.task_description)
                    
                    if code and len(code.strip()) > 100:
                        # Save as page
                        saved_path, page_num = save_as_page(code, workflow_name, task_id)
                        
                        st.session_state.generating = False
                        st.session_state.current_error = None
                        st.success("✅ Code generated successfully! Testing...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        raise Exception("Generated code is too short or empty. Generation may have failed.")
                        
                except Exception as e:
                    st.session_state.generating = False
                    error_msg = str(e)
                    st.markdown(f"""
                    <div class="error-box">
                        <h3>❌ Generation Failed</h3>
                        <p><strong>Error:</strong> {error_msg}</p>
                        <p>Please try again or check that ANTHROPIC_API_KEY is set correctly.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
                    
                    if st.button("🔄 Try Again", key=f"retry-{task_id}"):
                        st.session_state.generating = False
                        st.session_state.generation_attempt = 1
                        st.rerun()
        
        # Page exists, test it
        elif page_path.exists():
            st.success(f"✅ Code generated! Testing workflow...")
            
            page_path = page_path.resolve()
            
            # Test code execution
            with st.spinner("🧪 Testing workflow for errors..."):
                success, error = test_code_execution(page_path)
            
            if success:
                # Code is valid - show success with navigation instructions
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 Success! Your workflow has been created!</h3>
                    <p><strong>Workflow Name:</strong> {workflow_name}</p>
                    <p><strong>Page File:</strong> {page_path.name}</p>
                    <p>✅ Your workflow is now available as a page in this multi-page app!</p>
                    <p><strong>Navigate to it:</strong> Use the sidebar menu on the left to access your workflow page.</p>
                </div>
                """, unsafe_allow_html=True)
                
                save_task(task_id, st.session_state.task_description, "completed", page_path.name)
                
                if st.button("🔄 Create New Workflow", use_container_width=True):
                    st.session_state.task_id = None
                    st.session_state.task_description = ""
                    st.session_state.generation_attempt = 0
                    st.session_state.current_error = None
                    st.rerun()
            else:
                # Error detected
                st.session_state.current_error = error
                
                st.markdown(f"""
                <div class="error-box">
                    <h3>⚠️ Error Detected in Generated Code</h3>
                    <p><strong>Error details:</strong></p>
                    <pre style="background: white; padding: 1rem; border-radius: 5px; overflow-x: auto;">{error[:500]}</pre>
                    <p>Don't worry! We'll fix this automatically.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🔧 Troubleshoot & Fix (Attempt {attempt})", type="primary", use_container_width=True):
                    st.session_state.generation_attempt += 1
                    # Delete the problematic page file so it can be regenerated
                    if page_path.exists():
                        page_path.unlink()
                    st.rerun()
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ How It Works")
        st.markdown("""
        1. **Describe** your workflow in plain English
        2. **Generate** - AI creates the code for you
        3. **Test** - We automatically test the code
        4. **Fix** - If errors, we fix them automatically
        5. **Navigate** - Access your workflow from the sidebar menu!
        """)
        
        if st.session_state.task_id:
            st.markdown("---")
            st.subheader("Current Task")
            st.info(f"**Task ID:** {st.session_state.task_id}\n\n**Attempt:** {st.session_state.generation_attempt}")


if __name__ == "__main__":
    main()

