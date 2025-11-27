#!/bin/bash
# Setup script to create .env file with Anthropic API key

cat > .env << 'EOF'
# Anthropic API Key for Claude Sonnet
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API Key for GPT-3.5-turbo (used in generated Streamlit app)
OPENAI_API_KEY=your_openai_api_key_here
EOF

echo ".env file created successfully!"
echo "Note: You still need to add your OpenAI API key if you want to run the generated Streamlit app."

