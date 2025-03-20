from typing import Dict, Any, List, Optional
import os
import re
from dotenv import load_dotenv
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable
from langgraph.graph import StateGraph
import requests
from pytube import YouTube
from IPython.display import Image, display

# Load environment variables from .env file
load_dotenv()

# Check if OpenAI API key is properly set
openai_api_key = os.getenv("OPENAI_API_KEY")
use_mock_llm = openai_api_key is None or openai_api_key == "your_openai_api_key_here"

# Initialize language model or mock
if not use_mock_llm:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
else:
    print("Warning: Using mock LLM because OpenAI API key is not properly set.")
    
    # Create a mock LLM class
    class MockLLM:
        async def ainvoke(self, messages: List[Dict[str, Any]]) -> AIMessage:
            """Mock implementation of LLM that returns predefined responses."""
            # Check if it's a summarization request
            if any("summarizing" in msg.content for msg in messages if hasattr(msg, "content")):
                return AIMessage(content="This is a mock summary of the video transcript. The video appears to be about technology, science, or education. The speaker discusses important concepts and provides examples to illustrate their points. The content is informative and engaging, with clear explanations of complex topics.")
            # Check if it's a reflection request
            elif any("reflection" in msg.content.lower() for msg in messages if hasattr(msg, "content")):
                return AIMessage(content="This is a mock reflection on the video content. The video presents valuable information that could be applied in various contexts. Key insights include the importance of clear communication, the value of examples in learning, and the interconnectedness of different concepts. This content could be particularly useful for students, educators, and professionals looking to expand their knowledge in this area.")
            # Default response
            else:
                return AIMessage(content="This is a mock response from the LLM.")
    
    llm = MockLLM()

output_parser = StrOutputParser()

# Helper function to extract YouTube video ID from URL
def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL."""
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid YouTube URL format")

# Define LangGraph nodes
async def extract_video_metadata(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata from a YouTube video."""
    url = state["url"]
    print(f"URL is {url} ")
    video_id = extract_video_id(url)
    print(video_id)
    
    try:
        # First attempt: Use pytube to get video metadata
        try:
            yt = YouTube(url)
            
            metadata = {
                "title": yt.title,
                "author": yt.author,
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "views": yt.views,
                "length": yt.length,
                "description": yt.description,
                "video_id": video_id
            }
        except Exception as pytube_error:
            # Fallback: Use a simpler approach with basic metadata
            print(f"Warning: Pytube error: {str(pytube_error)}. Using fallback metadata extraction.")
            
            metadata = {
                "title": f"YouTube Video {video_id}",
                "author": "Unknown",
                "publish_date": None,
                "views": 0,
                "length": 0,
                "description": "No description available",
                "video_id": video_id
            }
        
        return {"url": url, "video_id": video_id, "metadata": metadata}
    except Exception as e:
        raise Exception(f"Error extracting video metadata: {str(e)}")

async def extract_transcript(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch the transcript of a YouTube video."""
    video_id = state["video_id"]
    metadata = state["metadata"]
    
    try:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry["text"] for entry in transcript_list])
        except (NoTranscriptFound, VideoUnavailable) as e:
            print(f"Warning: Transcript not available: {str(e)}. Using mock transcript.")
            # Use a mock transcript when the real one is not available
            transcript = "This is a mock transcript for the video. It simulates the content that would normally be extracted from the YouTube video's closed captions or subtitles. In a real scenario, this would contain the actual spoken content of the video, which would then be summarized and analyzed."
        
        return {"video_id": video_id, "metadata": metadata, "transcript": transcript}
    except Exception as e:
        raise Exception(f"Error processing transcript: {str(e)}")

async def summarize_transcript(state: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize the transcript of a YouTube video."""
    transcript = state["transcript"]
    metadata = state["metadata"]
    
    # Use LLM to summarize the transcript
    summarization_prompt = [
        SystemMessage(content="You are an expert at summarizing video content. Create a concise but comprehensive summary of the following transcript."),
        HumanMessage(content=f"Video Title: {metadata['title']}\nTranscript: {transcript}\n\nSummary:")
    ]
    
    summary = await llm.ainvoke(summarization_prompt)
    summary_text = output_parser.invoke(summary)
    
    return {"metadata": metadata, "transcript": transcript, "summary": summary_text}

async def reflect_on_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate reflections and insights based on the summary."""
    summary = state["summary"]
    metadata = state["metadata"]
    
    # Use LLM to reflect on the summary
    reflection_prompt = [
        SystemMessage(content="You are an insightful analyst. Provide thoughtful reflections, key insights, and potential applications based on the following summary."),
        HumanMessage(content=f"Video Title: {metadata['title']}\nSummary: {summary}\n\nReflection:")
    ]
    
    reflection = await llm.ainvoke(reflection_prompt)
    reflection_text = output_parser.invoke(reflection)
    
    return {"metadata": metadata, "summary": summary, "reflection": reflection_text}

# Build LangGraph workflow
def build_workflow():
    # Define the state schema as a TypedDict
    from typing_extensions import TypedDict
    
    class State(TypedDict, total=False):
        url: str
        video_id: str
        metadata: dict
        transcript: str
        summary: str
        reflection: str
    
    # Create the workflow with the state schema
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("extract_metadata", extract_video_metadata)
    workflow.add_node("extract_transcript", extract_transcript)
    workflow.add_node("summarize", summarize_transcript)
    workflow.add_node("reflect", reflect_on_summary)

    # Add edges to create sequential flow
    workflow.add_edge("extract_metadata", "extract_transcript")
    workflow.add_edge("extract_transcript", "summarize")
    workflow.add_edge("summarize", "reflect")
    
    # Set entry and exit points
    workflow.set_entry_point("extract_metadata")
    workflow.set_finish_point("reflect")

    # Compile the graph
    return workflow.compile()

# Main function to run the agent
async def run_youtube_analysis_agent(youtube_url: str):
    # Build the workflow
    workflow = build_workflow()

    #display(Image(workflow.get_graph().draw_mermaid_png()))
    
    # Run the workflow with the YouTube URL
    try:
        result = await workflow.ainvoke({"url": youtube_url})
        
        # Print results in a formatted way
        print("\n" + "="*50)
        print(f"VIDEO ANALYSIS RESULTS")
        print("="*50)
        
        print(f"\nVIDEO METADATA:")
        print(f"Title: {result['metadata']['title']}")
        print(f"Author: {result['metadata']['author']}")
        print(f"Publish Date: {result['metadata']['publish_date']}")
        print(f"Views: {result['metadata']['views']}")
        print(f"Length: {result['metadata']['length']} seconds")
        
        print("\nSUMMARY:")
        print(result["summary"])
        
        print("\nREFLECTION:")
        print(result["reflection"])
        
        return result
    except Exception as e:
        print(f"Error running YouTube analysis agent: {str(e)}")
        raise e

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input("Enter YouTube URL: ")
    
    asyncio.run(run_youtube_analysis_agent(youtube_url))
