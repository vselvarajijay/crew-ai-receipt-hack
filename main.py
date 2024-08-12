import sys
import json
import warnings
from pathlib import Path
from PIL import Image
from crewai import Agent, Task, Crew, Process
from crewai_tools import VisionTool

# Suppress UserWarnings temporarily
warnings.filterwarnings("ignore", category=UserWarning)

# Agent Definitions
# ------------------
# Agents represent different roles in the processing pipeline, each with a specific goal and backstory.

# Agent responsible for loading images
image_loading_agent = Agent(
    role='Image Loader',
    goal='Load the specified image file.',
    verbose=True,
    backstory="""
    You are an LLM agent that specializes in image processing and data extraction.
    """,
    tools=[]  # No tool needed for direct image loading
)

# Agent responsible for processing the image and extracting text data
llm_processing_agent = Agent(
    role='LLM Processor',
    goal='Process the receipt image using the VisionTool to extract text data such as business name, line items, tax, and total.',
    verbose=True,
    backstory="""
    You are an LLM agent that specializes in processing loaded images to extract text data using the VisionTool.
    """,
    tools=[VisionTool()]
)

# Agent responsible for summarizing the extracted data into a JSON object
json_summary_agent = Agent(
    role='JSON Summarizer',
    goal='Compile extracted information into a JSON object. Only return a JSON object; do not return any other data.',
    verbose=True,
    backstory="""
    You are a JSON Summarizer agent that specializes in compiling extracted information into a JSON object. Only return JSON, do not return any other data.
    """
)

# Task Definitions
# ----------------
# Tasks define the actions that each agent will perform. These are dynamically generated based on the input file.

def get_tasks_for_file(file_path):
    """Generate a list of tasks to process a given image file."""
    tasks = [
        Task(
            description=f"Load the image from the file {file_path}.",
            agent=image_loading_agent,
            expected_output="Loaded image.",
            action=lambda: Image.open(file_path)  # Open the image file using PIL
        ),
        Task(
            description="Use VisionTool to extract relevant data from the image.",
            agent=llm_processing_agent,
            expected_output="Extracted text data from the receipt.",
            action=lambda image: llm_processing_agent.tools[0].query_image(
                image=image,
                query="Extract the business name, line items with prices, tax, and total from this receipt image."
            )
        ),
        Task(
            description="Summarize the extracted information into a JSON object.",
            agent=json_summary_agent,
            expected_output="JSON object with receipt data.",
            action=lambda extracted_data: json.loads(extracted_data.text.strip("```json\n"))
        )
    ]
    return tasks

# Main Function
# -------------
# This function orchestrates the entire process, from loading the image file to saving the processed data.

def main(file_path):
    """Main function to process the receipt image and save the extracted data as a JSON file."""
    # Check if the file exists
    if not Path(file_path).is_file():
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

    # Define the crew and process
    crew = Crew(
        agents=[
            image_loading_agent,
            llm_processing_agent,
            json_summary_agent
        ],
        tasks=get_tasks_for_file(file_path),
        process=Process.sequential,  # Define the process flow as sequential
        verbose=True
    )

    # Run the crew to process the image and extract data
    result = crew.kickoff()

    # Save the results to a JSON file
    output_file = Path(file_path).with_suffix('.json')
    with open(output_file, 'w') as f:
        json.dump(result.raw, f, indent=4)

    print(f"Receipt data has been processed and saved to {output_file}")

# Entry Point
# -----------
# This script requires a file path to be passed as a command-line argument.

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_receipts.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
