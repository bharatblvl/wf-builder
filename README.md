# CrewAI Streamlit Code Generator

A CrewAI application that uses Claude Sonnet (Anthropic) to generate Streamlit web applications based on natural language descriptions.

## Overview

This application demonstrates how to use CrewAI with Claude Sonnet to automatically generate Streamlit code for web applications. The example task is to create a fraud detection application for transaction analysis.

## Features

- **Claude Sonnet Agent**: Uses Anthropic's Claude Sonnet 3.5 model for intelligent code generation
- **YAML Configuration**: Agents and tasks are defined in separate YAML files for easy customization
- **Streamlit Code Generation**: Automatically generates complete, production-ready Streamlit applications
- **Natural Language Input**: Describe your application in plain English
- **Fraud Detection Example**: Includes a sample task for creating a transaction fraud detection app

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp env_example.txt .env
```

Then edit `.env` and add your API keys:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Get API Keys

- **Anthropic API Key**: Get your key from [Anthropic Console](https://console.anthropic.com/)
- **OpenAI API Key**: Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Usage

### Run the CrewAI Application

```bash
python crew_app.py
```

This will:
1. Initialize the Claude Sonnet agent
2. Execute the task to generate Streamlit code
3. Save the generated code to `generated_streamlit_app.py`

### Customize Agents and Tasks

Agents and tasks are configured in YAML files for easy customization:

- **Edit Agents**: Modify `config/agents.yaml` to change agent roles, goals, backstories, or LLM models
- **Edit Tasks**: Modify `config/tasks.yaml` to change task descriptions and expected outputs

No need to edit Python code - just update the YAML files and rerun the application!

### Run the Generated Streamlit App

After generation, run the Streamlit app:

```bash
streamlit run generated_streamlit_app.py
```

## Sample Application Description

The default task generates a Streamlit application with:
- Header and footer sections
- Transaction data input (file upload or manual entry)
- Fraud detection powered by OpenAI GPT-3.5-turbo
- Visual indicators for fraudulent vs legitimate transactions
- Modern, user-friendly UI

## Project Structure

```
wf-builder/
├── crew_app.py              # Main CrewAI application
├── requirements.txt         # Python dependencies
├── env_example.txt          # Environment variables template
├── README.md               # This file
├── config/
│   ├── agents.yaml         # Agent configurations (roles, goals, backstories)
│   └── tasks.yaml          # Task configurations (descriptions, expected outputs)
└── generated_streamlit_app.py  # Generated Streamlit code (created after running)
```

## Requirements

- Python 3.8+
- Anthropic API key
- OpenAI API key (for the generated Streamlit app to use)

## Configuration Files

### Agents Configuration (`config/agents.yaml`)

Define your agents with:
- `role`: The agent's role/function
- `goal`: What the agent aims to achieve
- `backstory`: Context about the agent's expertise
- `llm`: The LLM model to use (e.g., "claude-3-5-sonnet-20241022")
- `temperature`: LLM temperature setting
- `tools`: List of tools the agent can use
- `verbose`: Enable verbose output
- `allow_delegation`: Whether the agent can delegate tasks

### Tasks Configuration (`config/tasks.yaml`)

Define your tasks with:
- `description`: Detailed description of what the task should accomplish
- `agent`: The agent name assigned to this task (must match an agent in `agents.yaml`)
- `expected_output`: What the task should produce

## Notes

- The generated Streamlit app uses OpenAI GPT-3.5-turbo for fraud detection
- You can modify agents and tasks by editing the YAML files - no code changes needed!
- The CrewAI framework handles the orchestration between the agent and tasks
- All configurations are loaded from YAML files at runtime

## License

MIT License

