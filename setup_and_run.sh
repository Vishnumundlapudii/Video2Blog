#!/bin/bash
# Setup and run script for YouTube Analysis Agent

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up YouTube Analysis Agent...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please install venv package and try again.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please check requirements.txt and try again.${NC}"
    exit 1
fi

# Set up .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Setting up .env file...${NC}"
    cp .env.example .env
    
    # Prompt for OpenAI API key
    echo -e "${YELLOW}Please enter your OpenAI API key (or press Enter to use mock responses):${NC}"
    read -r api_key
    
    if [ -n "$api_key" ]; then
        # Update .env file with API key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your_openai_api_key_here/$api_key/g" .env
        else
            # Linux
            sed -i "s/your_openai_api_key_here/$api_key/g" .env
        fi
        echo -e "${GREEN}API key set successfully.${NC}"
    else
        echo -e "${YELLOW}No API key provided. The application will use mock responses.${NC}"
    fi
    
    echo -e "${GREEN}Environment file created successfully.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping setup.${NC}"
fi

# Prompt for YouTube URL
echo -e "${YELLOW}Please enter a YouTube URL to analyze (or press Enter to be prompted by the script):${NC}"
read -r youtube_url

# Run the agent
echo -e "${GREEN}Running YouTube Analysis Agent...${NC}"
if [ -z "$youtube_url" ]; then
    python main.py
else
    python main.py "$youtube_url"
fi

# Deactivate virtual environment on exit
deactivate
