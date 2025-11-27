# Two-Application Architecture

This project uses **two separate Streamlit applications**:

## 1. Workflow Builder (`dashboard.py`)

**Purpose**: Create and generate workflows using AI

**Port**: 8501 (default)

**Launch**:
```bash
streamlit run dashboard.py --server.port 8501
```

**Features**:
- Describe workflows in natural language
- AI generates Streamlit code for workflows
- Automatic error detection and fixing
- Self-healing code generation

**What it does**:
- Generates workflow code based on your descriptions
- Saves generated workflows to `pages/` directory
- Tests code for errors
- Auto-fixes and regenerates if needed

---

## 2. Workflows Application (`workflows_app.py`)

**Purpose**: Run and interact with all generated workflows

**Port**: 8502 (recommended)

**Launch**:
```bash
streamlit run workflow_app/workflows_app.py --server.port 8502
```

**Features**:
- Multi-page Streamlit application
- Shows all generated workflows as pages
- Navigate between workflows using sidebar
- Each workflow runs independently

**What it does**:
- Automatically discovers workflows in `pages/` directory
- Displays them as pages in the sidebar
- Provides a home page showing all available workflows

---

## Workflow

1. **Create Workflows**: Use Workflow Builder (dashboard.py) to generate workflows
2. **Run Workflows**: Use Workflows App (workflows_app.py) to interact with them

## File Structure

```
wf-builder/
├── dashboard.py          # Application 1: Workflow Builder
├── workflow_app/         # Application 2: Workflows Runner
│   ├── workflows_app.py  # Main workflows app file
│   └── pages/            # Generated workflow pages stored here
│       ├── 1_Workflow1.py
│       ├── 2_Workflow2.py
│       └── ...
└── ...
```

## Quick Start

**Terminal 1** - Workflow Builder:
```bash
streamlit run dashboard.py --server.port 8501
```

**Terminal 2** - Workflows App:
```bash
streamlit run workflow_app/workflows_app.py --server.port 8502
```

Then:
1. Create workflows in the Builder (port 8501)
2. Run workflows in the Workflows App (port 8502)

