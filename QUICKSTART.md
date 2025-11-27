# Quick Start Guide

## Step 1: Install Dependencies

```bash
cd /Users/bharatmadan/projects/wf-builder
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

### Option A: Create .env file manually

```bash
cp env_example.txt .env
```

Then edit `.env` file and replace the placeholder values with your actual API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
OPENAI_API_KEY=sk-your-actual-key-here
```

### Option B: Set environment variables directly

```bash
export ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"
export OPENAI_API_KEY="sk-your-actual-key-here"
```

**Where to get API keys:**
- **Anthropic API Key**: https://console.anthropic.com/
- **OpenAI API Key**: https://platform.openai.com/api-keys

## Step 3: Run the Application

```bash
python crew_app.py
```

This will:
1. Load agent and task configurations from `config/agents.yaml` and `config/tasks.yaml`
2. Initialize the Claude Sonnet agent
3. Generate Streamlit code based on the task description
4. Save the generated code to `generated_streamlit_app.py`

## Step 4: Run the Generated Streamlit App (Optional)

After code generation completes:

```bash
streamlit run generated_streamlit_app.py
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY environment variable is not set"
- Make sure you've created the `.env` file with your API key
- Or export it as an environment variable

### Error: "ModuleNotFoundError: No module named 'crewai'"
- Run: `pip install -r requirements.txt`

### Error: "FileNotFoundError: config/agents.yaml"
- Make sure you're running from the project root directory
- Verify that `config/agents.yaml` and `config/tasks.yaml` exist

