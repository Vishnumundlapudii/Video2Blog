# YouTube Analysis Agent

A LangGraph-based agentic application that analyzes YouTube videos by extracting metadata, transcripts, generating summaries, and providing reflections.

## Features

- Extract metadata from YouTube videos (title, author, views, etc.)
- Extract transcripts from YouTube videos
- Summarize video content using LLM
- Generate insightful reflections on summaries
- Sequential workflow with LangGraph
- Robust fallback mechanisms for handling API errors

## Prerequisites

- Python 3.9+
- OpenAI API key (optional - will use mock responses if not provided)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd FastAPI_LangGraph
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):

```bash
cp .env.example .env
```

4. Edit the `.env` file and add your OpenAI API key (optional):

```
OPENAI_API_KEY=your_openai_api_key_here
```

Note: If you don't provide an OpenAI API key, the application will use mock responses for the LLM calls.

## Running the Application

Run the agent with a YouTube URL:

```bash
python main.py https://www.youtube.com/watch?v=VIDEO_ID
```

Or run it without arguments to be prompted for a URL:

```bash
python main.py
```

## LangGraph Workflow

The application uses LangGraph to create a sequential workflow with four main nodes:

1. **Extract Metadata Node**: Extracts metadata from the YouTube video (title, author, views, etc.)
2. **Extract Transcript Node**: Extracts the transcript from the YouTube video
3. **Summarize Node**: Summarizes the video transcript
4. **Reflect Node**: Generates insights and reflections based on the summary

The workflow is defined as a directed graph with edges connecting these nodes in sequence. The state schema is properly defined using TypedDict to ensure type safety.

## Output

The agent outputs:

- **Video Metadata**: Title, author, publish date, views, and length
- **Summary**: A concise summary of the video content
- **Reflection**: Thoughtful insights and reflections on the video content

## Error Handling and Fallbacks

The application includes robust error handling and fallback mechanisms:

- Fallback for metadata extraction when pytube API fails
- Fallback for transcript extraction when no transcript is available
- Mock LLM responses when OpenAI API key is not provided
- Proper error messages and graceful degradation

## License

[MIT License](LICENSE)
