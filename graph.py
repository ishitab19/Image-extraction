import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any

# Try to load a .env file if python-dotenv is installed; otherwise rely on the
# environment already being set.
try:
    import importlib
    spec = importlib.util.find_spec("dotenv")
    if spec is not None:
        load_dotenv = importlib.import_module("dotenv").load_dotenv
        load_dotenv()
except Exception:
    pass

# 1. Define the Schema for Structured Output
class DataPoint(BaseModel):
    x_value: str
    y_value: float
    series_name: str = "default"

class GraphMetadata(BaseModel):
    graph_type: str  # e.g., Line, Bar, Pie
    x_axis_title: str
    y_axis_title: str
    x_axis_scale: str  # e.g., Linear, Logarithmic, Dates
    y_axis_scale: str
    legend_items: List[str]
    extracted_data: List[DataPoint]

# 2. Initialize the Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY not set. Add GEMINI_API_KEY=your_key to a .env file at the project root or set the environment variable."
    )

client = genai.Client(api_key=api_key)

DEFAULT_IMAGE = "cars_graph.png"

def analyze_graph(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # 3. Request with Structured Config
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Extract all technical details and data points from this graph."
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GraphMetadata, # Forces the AI to follow our Pydantic class
            temperature=0.1 # Low temperature for higher accuracy in data extraction
        )
    )

    # 4. Access the parsed result
    data = response.parsed
    
    print(f"Graph Type: {data.graph_type}")
    print(f"X-Axis Scale: {data.x_axis_scale}")
    print(f"Legends found: {', '.join(data.legend_items)}")
    
    # Print the table
    print("\n--- Extracted Data Table ---")
    print(f"{'Series':<15} | {data.x_axis_title:<10} | {data.y_axis_title:<10}")
    print("-" * 40)
    for point in data.extracted_data:
        print(f"{point.series_name:<15} | {point.x_value:<10} | {point.y_value:<10}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_graph(sys.argv[1])
    else:
        # If a default image exists in the project root, run analysis on it.
        if os.path.exists(DEFAULT_IMAGE):
            print(f"Found default image {DEFAULT_IMAGE}; running analysis.")
            analyze_graph(DEFAULT_IMAGE)
        else:
            # Safe fallback when no image is provided
            print("No image path provided. To run: python graph.py path_to_image.jpg")
            print("GEMINI_API_KEY loaded:", bool(os.getenv("GEMINI_API_KEY")))