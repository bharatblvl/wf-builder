"""
CrewAI Application: Streamlit Code Generator using Claude Sonnet
This application uses CrewAI to generate Streamlit code based on natural language descriptions.
Agents and tasks are loaded from YAML configuration files.
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
TASKS_CONFIG_FILE = CONFIG_DIR / "tasks.yaml"


def load_yaml_config(file_path):
    """Load and parse a YAML configuration file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def create_llm_from_config(model_name, temperature=0.7):
    """Create an LLM instance based on the model name."""
    if "claude" in model_name.lower():
        # Use CrewAI's LLM class which handles model configuration automatically
        return LLM(
            model=model_name,
            temperature=temperature
        )
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def create_agent_from_config(agent_config, agent_name):
    """Create an Agent instance from YAML configuration."""
    # Create tools mapping
    tools_map = {
        "file_read": FileReadTool()
    }
    
    # Get LLM configuration
    llm_model = agent_config.get("llm", "anthropic/claude-sonnet-4-20250514")
    temperature = agent_config.get("temperature", 0.7)
    llm = create_llm_from_config(llm_model, temperature)
    
    # Get tools
    tool_names = agent_config.get("tools", [])
    tools = [tools_map[tool] for tool in tool_names if tool in tools_map]
    
    # Create and return Agent
    return Agent(
        role=agent_config.get("role", ""),
        goal=agent_config.get("goal", ""),
        backstory=agent_config.get("backstory", ""),
        verbose=agent_config.get("verbose", True),
        allow_delegation=agent_config.get("allow_delegation", False),
        llm=llm,
        tools=tools
    )


def create_task_from_config(task_config, task_name, agents_dict):
    """Create a Task instance from YAML configuration."""
    agent_name = task_config.get("agent")
    if agent_name not in agents_dict:
        raise ValueError(f"Agent '{agent_name}' not found in agents dictionary")
    
    return Task(
        description=task_config.get("description", ""),
        agent=agents_dict[agent_name],
        expected_output=task_config.get("expected_output", "")
    )


# Load configurations from YAML files
agents_config = load_yaml_config(AGENTS_CONFIG_FILE)
tasks_config = load_yaml_config(TASKS_CONFIG_FILE)

# Create agents from configuration
agents_dict = {}
for agent_name, agent_config in agents_config.items():
    agents_dict[agent_name] = create_agent_from_config(agent_config, agent_name)

# Create tasks from configuration
tasks_list = []
for task_name, task_config in tasks_config.items():
    tasks_list.append(create_task_from_config(task_config, task_name, agents_dict))

# Create the crew
crew = Crew(
    agents=list(agents_dict.values()),
    tasks=tasks_list,
    process=Process.sequential,
    verbose=True
)

def run_crew():
    """Execute the CrewAI crew to generate Streamlit code."""
    print("Starting CrewAI Streamlit Code Generator...")
    print("=" * 60)
    
    result = crew.kickoff()
    
    print("\n" + "=" * 60)
    print("Code Generation Complete!")
    print("=" * 60)
    
    return result

def extract_python_code(text):
    """Extract Python code from agent response, removing markdown formatting."""
    text = str(text)
    
    # Remove markdown code block markers
    if "```python" in text:
        # Extract code between ```python and ```
        start = text.find("```python")
        end = text.find("```", start + 9)
        if end != -1:
            text = text[start + 9:end].strip()
    elif "```" in text:
        # Try generic code block
        start = text.find("```")
        end = text.find("```", start + 3)
        if end != -1:
            text = text[start + 3:end].strip()
    
    # Remove any explanatory text at the beginning
    lines = text.split('\n')
    code_lines = []
    skip_until_code = True
    
    for line in lines:
        # Skip lines that are clearly not code (explanatory text)
        if skip_until_code:
            # Look for Python code indicators
            if (line.strip().startswith('"""') or 
                line.strip().startswith("'''") or
                line.strip().startswith('import ') or
                line.strip().startswith('from ') or
                line.strip().startswith('#') or
                '=' in line and not line.strip().startswith('Here')):
                skip_until_code = False
        
        if not skip_until_code or not line.strip().startswith("Here's"):
            code_lines.append(line)
    
    result = '\n'.join(code_lines).strip()
    
    # Clean up any remaining markdown artifacts
    if result.startswith("Here's"):
        # Find the first Python line
        lines = result.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(('"""', "'''", 'import ', 'from ', '#')):
                result = '\n'.join(lines[i:])
                break
    
    return result

def save_generated_code(result, task_name, agent_name):
    """Save generated code with proper naming and metadata"""
    # Create generated code directory
    generated_code_dir = Path(__file__).parent / "generated_code"
    generated_code_dir.mkdir(exist_ok=True)
    
    # Extract clean Python code from the response
    clean_code = extract_python_code(result)
    
    # Create filename: agent_name_task_name.py
    filename = f"{agent_name}_{task_name}.py"
    output_file = generated_code_dir / filename
    
    # Save the code
    with open(output_file, "w") as f:
        f.write(clean_code)
    
    # Update metadata
    metadata_file = generated_code_dir / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    metadata[task_name] = {
        "agent_name": agent_name,
        "filename": filename,
        "generated_at": datetime.now().isoformat(),
        "code_length": len(clean_code),
        "status": "generated"
    }
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return output_file

if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        exit(1)
    
    result = run_crew()
    
    # Save the generated code to a file
    if result:
        # Get task and agent names from config
        tasks_config = load_yaml_config(TASKS_CONFIG_FILE)
        
        # Find the task that was executed (assuming single task for now)
        task_name = list(tasks_config.keys())[0] if tasks_config else "streamlit_code_task"
        task_config = tasks_config.get(task_name, {})
        agent_name = task_config.get("agent", "streamlit_code_agent")
        
        output_file = save_generated_code(result, task_name, agent_name)
        
        print(f"\nGenerated code saved to: {output_file}")
        print(f"Code length: {len(extract_python_code(result))} characters")
        print(f"\nTo view in dashboard, run: streamlit run dashboard.py")

