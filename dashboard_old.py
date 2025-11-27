"""
Workflow Builder - Self-Healing Streamlit Workflow Generator
Create, generate, and run Streamlit workflows from natural language descriptions
"""

import streamlit as st
from pathlib import Path
import subprocess
import sys
import os
from datetime import datetime
import json
import socket
import time
import uuid
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our code generation module
from crew_generator import generate_code, fix_code, save_generated_code

# Page configuration
st.set_page_config(
    page_title="Workflow Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Directories
GENERATED_CODE_DIR = Path(__file__).parent / "generated_code"
GENERATED_CODE_DIR.mkdir(exist_ok=True)

# State files
RUNNING_APPS_FILE = GENERATED_CODE_DIR / "running_apps.json"
TASKS_FILE = GENERATED_CODE_DIR / "tasks.json"

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


def get_available_port(start_port=8502, max_attempts=10):
    """Find an available port"""
    for i in range(max_attempts):
        port = start_port + i
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None


def load_running_apps():
    """Load running apps info"""
    if RUNNING_APPS_FILE.exists():
        try:
            with open(RUNNING_APPS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_running_apps(running_apps):
    """Save running apps info"""
    with open(RUNNING_APPS_FILE, 'w') as f:
        json.dump(running_apps, f, indent=2)


def load_tasks():
    """Load saved tasks"""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_task(task_id, task_description, status="pending"):
    """Save task"""
    tasks = load_tasks()
    tasks[task_id] = {
        "description": task_description,
        "status": status,
        "created_at": datetime.now().isoformat()
    }
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)


def capture_streamlit_errors(process):
    """Capture errors from Streamlit subprocess"""
    errors = []
    stdout_lines = []
    stderr_lines = []
    
    # Read from stdout and stderr
    try:
        for line in iter(process.stdout.readline, b''):
            if line:
                line_str = line.decode('utf-8', errors='ignore')
                stdout_lines.append(line_str)
                # Look for error patterns
                if any(keyword in line_str.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                    errors.append(line_str)
    except:
        pass
    
    try:
        for line in iter(process.stderr.readline, b''):
            if line:
                line_str = line.decode('utf-8', errors='ignore')
                stderr_lines.append(line_str)
                if any(keyword in line_str.lower() for keyword in ['error', 'exception', 'traceback']):
                    errors.append(line_str)
    except:
        pass
    
    return '\n'.join(errors), '\n'.join(stdout_lines), '\n'.join(stderr_lines)


def test_code_execution(code_path, timeout=15):
    """Test if the code runs without errors"""
    # Ensure we have absolute paths
    code_path = Path(code_path).resolve()
    
    try:
        # First, check if file exists
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
        
        # Try to actually validate the code
        # Use absolute paths in the test script
        code_path_abs = str(code_path.absolute())
        code_dir_abs = str(code_path.parent.absolute())
        
        # Escape paths for use in Python string
        code_path_escaped = code_path_abs.replace('\\', '\\\\').replace("'", "\\'")
        code_dir_escaped = code_dir_abs.replace('\\', '\\\\').replace("'", "\\'")
        
        test_script = f"""
import sys
import traceback
import os

# Add directory to path
sys.path.insert(0, r'{code_dir_escaped}')

try:
    # Read and parse the code using absolute path
    code_path = r'{code_path_escaped}'
    
    if not os.path.exists(code_path):
        print(f"FILE_NOT_FOUND: {{code_path}}")
        sys.exit(1)
    
    with open(code_path, 'r') as f:
        code_content = f.read()
    
    # Compile to check for syntax errors
    compile(code_content, code_path, 'exec')
    
    # Try to import required modules (just check they're available, don't execute streamlit)
    try:
        import streamlit
        import pandas
    except ImportError as ie:
        print(f"IMPORT_WARNING: {{ie}}")
    
    print("SUCCESS: Code is valid")
    sys.exit(0)
except SyntaxError as e:
    print(f"SYNTAX_ERROR: {{str(e)}}")
    traceback.print_exc()
    sys.exit(1)
except ImportError as e:
    print(f"IMPORT_ERROR: {{str(e)}}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    traceback.print_exc()
    sys.exit(1)
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            timeout=timeout,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode != 0:
            error_output = result.stderr.decode('utf-8', errors='ignore') or result.stdout.decode('utf-8', errors='ignore')
            # Extract meaningful error
            if "SUCCESS" not in error_output:
                return False, error_output
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, "Code validation timed out"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def launch_app(code_path, task_id):
    """Launch Streamlit app and return port and process info"""
    port = get_available_port()
    if not port:
        return None, None, "Could not find an available port"
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(code_path),
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(code_path.parent.parent)
        )
        
        # Wait a moment and check if process is still alive
        time.sleep(5)  # Give Streamlit more time to start
        if process.poll() is not None:
            # Process died, get error
            try:
                stdout, stderr = process.communicate(timeout=2)
            except:
                stdout, stderr = b"", b""
            error_msg = stderr.decode('utf-8', errors='ignore') or stdout.decode('utf-8', errors='ignore')
            if not error_msg:
                error_msg = "Application failed to start (process terminated immediately)"
            return None, None, error_msg
        
        # Save running app info
        running_apps = load_running_apps()
        running_apps[task_id] = {
            "port": port,
            "process_id": process.pid,
            "started_at": datetime.now().isoformat(),
            "code_path": str(code_path)
        }
        save_running_apps(running_apps)
        
        return port, process, None
        
    except Exception as e:
        return None, None, str(e)


def render_header():
    """Render header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Workflow Builder</h1>
        <p>Describe your workflow in plain English, and we'll build it for you!</p>
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
    
    # Main input area
    st.subheader("📝 Describe Your Workflow")
    
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
            st.session_state.generating = False  # Reset generating flag
            save_task(task_id, task_description, "generating")
            st.rerun()
    
    # Show generation progress
    if st.session_state.task_id:
        task_id = st.session_state.task_id
        attempt = st.session_state.generation_attempt
        
        # Check current status
        tasks = load_tasks()
        task_info = tasks.get(task_id, {})
        
        code_path = GENERATED_CODE_DIR / f"app_{task_id}_attempt_{attempt}.py"
        
        # Generation phase
        if not code_path.exists() and not st.session_state.get('generating', False):
            st.session_state.generating = True
            
            try:
                st.info(f"🤖 Generating your workflowlication (Attempt {attempt})... This may take a few moments.")
                
                if st.session_state.current_error:
                    # Fix mode
                    current_code = ""
                    if attempt > 1:
                        prev_code_path = GENERATED_CODE_DIR / f"app_{task_id}_attempt_{attempt-1}.py"
                        if prev_code_path.exists():
                            current_code = prev_code_path.read_text()
                    
                    with st.spinner("🔧 Fixing code based on error..."):
                        code = fix_code(
                            st.session_state.task_description,
                            st.session_state.current_error,
                            current_code
                        )
                else:
                    # Initial generation
                    with st.spinner("✨ Creating your workflowlication from scratch..."):
                        code = generate_code(st.session_state.task_description)
                
                if code and len(code.strip()) > 100:  # Basic validation
                    code_path.write_text(code)
                    st.session_state.generating = False
                    st.session_state.current_error = None
                    st.success("✅ Code generated successfully! Testing...")
                    time.sleep(1)  # Brief pause to show success message
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
                
                # Show traceback in expander for debugging
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
                
                # Allow retry
                if st.button("🔄 Try Again", key=f"retry-{task_id}"):
                    st.session_state.generating = False
                    st.session_state.generation_attempt = 1
                    st.rerun()
        
        # Code exists, test it
        elif code_path.exists():
            st.success(f"✅ Code generated! Testing workflow...")
            
            # Ensure absolute path
            code_path = code_path.resolve()
            
            # Test code execution
            with st.spinner("🧪 Testing workflow for errors..."):
                success, error = test_code_execution(code_path)
            
            if success:
                # Code is valid, try to launch
                st.success("✅ Code validation passed! Launching application...")
                
                port, process, launch_error = launch_app(code_path, task_id)
                
                if port:
                    url = f"http://localhost:{port}"
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>🎉 Success! Your workflow is running!</h3>
                        <p><strong>Open your workflow:</strong> <a href="{url}" target="_blank">{url}</a></p>
                        <p>Attempt {attempt} - Workflow is ready to use.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    save_task(task_id, st.session_state.task_description, "running")
                    
                    if st.button("🔗 Open Workflow", use_container_width=True):
                        import webbrowser
                        webbrowser.open_new_tab(url)
                    
                    if st.button("🔄 Create New Workflow", use_container_width=True):
                        st.session_state.task_id = None
                        st.session_state.task_description = ""
                        st.session_state.generation_attempt = 0
                        st.session_state.current_error = None
                        st.rerun()
                else:
                    st.session_state.current_error = launch_error or "Failed to launch application"
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
                    st.rerun()
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ How It Works")
        st.markdown("""
        1. **Describe** your workflow in plain English
        2. **Generate** - AI creates the code for you
        3. **Test** - We automatically test the code
        4. **Fix** - If errors, we fix them automatically
        5. **Run** - Your app launches successfully!
        """)
        
        if st.session_state.task_id:
            st.markdown("---")
            st.subheader("Current Task")
            st.info(f"**Task ID:** {st.session_state.task_id}\n\n**Attempt:** {st.session_state.generation_attempt}")


if __name__ == "__main__":
    main()
