"""
CrewAI Code Generator Module
Functions to generate code using CrewAI, with error feedback and fixing capabilities
"""

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration file paths
CONFIG_DIR = Path(__file__).parent / "config"
AGENTS_CONFIG_FILE = CONFIG_DIR / "agents.yaml"
GENERATED_CODE_DIR = Path(__file__).parent / "generated_code"
GENERATED_CODE_DIR.mkdir(exist_ok=True)


def create_llm_from_config(model_name="anthropic/claude-sonnet-4-20250514", temperature=0.7):
    """Create an LLM instance based on the model name."""
    return LLM(
        model=model_name,
        temperature=temperature
    )


def create_streamlit_agent():
    """Create the Streamlit code generator agent"""
    tools_map = {
        "file_read": FileReadTool()
    }
    
    llm = create_llm_from_config()
    
    return Agent(
        role="Streamlit Code Generator",
        goal="Generate production-ready Streamlit applications based on natural language descriptions, ensuring code quality, best practices, and complete functionality.",
        backstory="""You are an expert Streamlit developer with deep knowledge of:
    - Streamlit framework and best practices
    - UI/UX design principles for data applications
    - Python programming and data visualization
    - Integration with LLMs (OpenAI, Anthropic, etc.)
    - Creating modern, responsive web applications
    - Error handling and debugging
    
    You excel at translating business requirements into clean, maintainable Streamlit code.""",
        verbose=False,
        allow_delegation=False,
        llm=llm,
        tools=[tools_map["file_read"]]
    )


def create_fix_agent():
    """Create an agent specialized in fixing code errors"""
    tools_map = {
        "file_read": FileReadTool()
    }
    
    llm = create_llm_from_config()
    
    return Agent(
        role="Code Fixer & Debugger",
        goal="Analyze error messages and fix code issues to ensure the generated Streamlit application runs without errors.",
        backstory="""You are an expert Python and Streamlit debugger with extensive experience in:
    - Analyzing error messages and stack traces
    - Identifying and fixing code issues
    - Streamlit-specific error resolution
    - Python syntax and runtime errors
    - Import and dependency issues
    - Best practices for error-free code
    
    You systematically analyze errors and provide complete, working solutions.""",
        verbose=False,
        allow_delegation=False,
        llm=llm,
        tools=[tools_map["file_read"]]
    )


def extract_python_code(text):
    """Extract Python code from agent response, removing markdown formatting."""
    text = str(text)
    
    # Remove markdown code block markers
    if "```python" in text:
        start = text.find("```python")
        end = text.find("```", start + 9)
        if end != -1:
            text = text[start + 9:end].strip()
    elif "```" in text:
        start = text.find("```")
        end = text.find("```", start + 3)
        if end != -1:
            text = text[start + 3:end].strip()
    
    # Remove explanatory text at the beginning
    lines = text.split('\n')
    code_lines = []
    skip_until_code = True
    
    for line in lines:
        if skip_until_code:
            if (line.strip().startswith('"""') or 
                line.strip().startswith("'''") or
                line.strip().startswith('import ') or
                line.strip().startswith('from ') or
                line.strip().startswith('#') or
                ('=' in line and not line.strip().startswith('Here'))):
                skip_until_code = False
        
        if not skip_until_code or not line.strip().startswith("Here's"):
            code_lines.append(line)
    
    result = '\n'.join(code_lines).strip()
    
    if result.startswith("Here's"):
        lines = result.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(('"""', "'''", 'import ', 'from ', '#')):
                result = '\n'.join(lines[i:])
                break
    
    return result


def generate_code(task_description):
    """Generate Streamlit page code from a task description"""
    agent = create_streamlit_agent()
    
    task = Task(
        description=f"""Create a complete Streamlit PAGE (not a standalone app) that will be part of a multi-page Streamlit application. The code you generate should:

{task_description}

CRITICAL REQUIREMENTS FOR MULTI-PAGE APPS:
- DO NOT use st.set_page_config() - pages don't need this
- DO NOT create a main() function with if __name__ == "__main__"
- The code should run directly when imported (all code at module level)
- Use Streamlit commands directly (st.title, st.write, etc.)
- Include proper error handling
- Make the UI modern and user-friendly
- Include data validation where needed
- Follow Python PEP 8 standards
- Ensure all imports are correct and available
- Include all necessary dependencies

Generate the complete Streamlit PAGE code. The code should execute when the page is loaded in a multi-page Streamlit app.""",
        agent=agent,
        expected_output="A complete Streamlit page code that can be used in a multi-page Streamlit application. No st.set_page_config() or main() function."
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    result = crew.kickoff()
    return extract_python_code(result)


def fix_code(task_description, error_message, current_code):
    """Fix code based on error message"""
    fix_agent = create_fix_agent()
    
    task = Task(
        description=f"""Fix the following Streamlit PAGE code (part of a multi-page app) that has errors.

IMPORTANT: This is a Streamlit PAGE, not a standalone app. Do NOT add st.set_page_config() or main() function.

Original Task Description:
{task_description}

Error Message:
{error_message}

Current Code (with errors):
```python
{current_code}
```

Please fix all errors in the code to make it run successfully. Remember: this is a PAGE in a multi-page app, not a standalone application.""",
        agent=fix_agent,
        expected_output="Complete fixed Streamlit page code that runs without errors as part of a multi-page Streamlit application."
    )
    
    crew = Crew(
        agents=[fix_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    result = crew.kickoff()
    return extract_python_code(result)


def save_generated_code(code, task_id, attempt=1, workflow_name=None):
    """Save generated code as a Streamlit page file"""
    # Use pages directory for multi-page app structure
    pages_dir = Path(__file__).parent / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    # Clean workflow name for filename (remove special chars, limit length)
    if workflow_name:
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', workflow_name[:30])
        filename = f"{clean_name}.py"
    else:
        filename = f"workflow_{task_id}.py"
    
    filepath = pages_dir / filename
    
    # Remove st.set_page_config() if present (pages don't need it)
    code_lines = code.split('\n')
    cleaned_lines = []
    skip_next = False
    in_page_config = False
    
    for i, line in enumerate(code_lines):
        if 'st.set_page_config' in line:
            in_page_config = True
            continue
        if in_page_config:
            # Skip until we find the closing parenthesis
            if ')' in line and line.strip().startswith(')'):
                in_page_config = False
            continue
        
        # Remove if __name__ == "__main__" blocks
        if 'if __name__' in line and '__main__' in line:
            skip_next = True
            continue
        if skip_next and line.strip() and not line.startswith((' ', '\t')):
            skip_next = False
        
        if not skip_next:
            cleaned_lines.append(line)
    
    cleaned_code = '\n'.join(cleaned_lines)
    
    with open(filepath, 'w') as f:
        f.write(cleaned_code)
    
    return filepath

