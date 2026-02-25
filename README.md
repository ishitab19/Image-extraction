# Project Documentation - Intelligent Image Text & Graph Data Extraction System

---

# Project Overview

This project is an AI-powered extraction system that:

- Extracts structured text and tables from document images  
- Extracts structured numerical data from graph images  
- Uses a fallback mechanism for improved accuracy  
- Returns structured, machine-readable output  

The system combines:

- OpenCV for preprocessing  
- Unstructured Library for table extraction  
- Mistral OCR as a fallback OCR engine  
- Google Gemini (Structured Output) for graph understanding  

---

# System Architecture

The project consists of two independent but related modules:

- Text & Table Extraction Module  
- Graph Data Extraction Module  

---

# MODULE 1: TEXT & TABLE EXTRACTION

## Objective

To extract text and structured table data from document images using:

- Local parsing (Unstructured library)  
- AI fallback (Mistral OCR)  
- Quality validation mechanism  

---

## Step 1: Image Preprocessing (OpenCV)

The image is enhanced before OCR to improve accuracy.

### Operations Performed:

- Convert to Grayscale  
- Sharpen Image using Kernel  
- Resize (Minimum width = 2000px)  
- Noise Reduction (Gaussian Blur optional)  

### Why Preprocessing is Important?

- Improves OCR accuracy  
- Enhances faint text  
- Removes noise  
- Improves number recognition  

---

## Step 2: Local Extraction (Unstructured Library)

```python
elements = partition_image(filename=image_path, strategy="hi_res")
```

This library:

- Detects document elements  
- Classifies content (Table, Title, NarrativeText)  
- Extracts table content as HTML  

---

## Step 3: Quality Gate System

You implemented a validation system that checks:

✔ At least one table detected  
✔ Minimum 2 rows  
✔ Less than 50% empty cells  

If any condition fails → It triggers fallback.

This prevents:

- Broken tables  
- Empty extraction  
- Poor structure  

---

## Step 4: Mistral OCR Fallback

If local extraction fails:

- Image is converted to base64  
- Sent to Mistral OCR API  
- Returns Markdown output  

This ensures:

- High accuracy  
- Better number recognition  
- Graph/table detection support  

---

# Evaluation of Current Approach

## Images Handled Well by Unstructured (Local Extraction)

The current local approach performs well when:

- Tables are clearly structured with visible grid lines  
- Text is high contrast and well-aligned  
- Image resolution is sufficient  
- Tables follow standard row-column format  
- No heavy background noise is present  

In such cases:

- Extraction is fast  
- Structure is preserved  
- No external API cost is incurred  
- Output remains consistent  

---

## Cases Where Mistral OCR Is Required

Fallback to Mistral OCR is necessary when:

- Tables lack visible grid lines  
- Image contains shadows or lighting issues  
- Text is faint or slightly blurred  
- Cells contain dense numerical values  
- Local extraction produces incomplete HTML  
- More than 50% empty cells are detected  
- Rows are misaligned or merged  

In these cases, Unstructured may:

- Miss tables completely  
- Return fragmented rows  
- Produce structurally inconsistent output  

Mistral OCR handles these inconsistencies more effectively.

---
## Output

The system provides the following outputs after processing:

- Extracted text and tables printed in the terminal  
- Processed image displayed using OpenCV  
- Returns structured textual output

---

# MODULE 2: GRAPH DATA EXTRACTION

## Objective

To extract structured technical metadata and numerical data points from graph images using:

- Multimodal AI understanding (Gemini Vision Model)
- Schema-enforced structured output (Pydantic)
- Deterministic configuration for higher numerical accuracy

---

## Step 1: Image Input & Encoding

The graph image is read as binary data before being sent to the AI model.

### Operations Performed:

- Open image in binary mode  
- Convert image into byte stream  
- Attach image bytes to Gemini request  
- Provide extraction instruction prompt  

### Why is this Step Important?

- Ensures model receives full visual data  
- Preserves graph clarity  
- Maintains high-resolution details  
- Prepares image for multimodal processing  

---

## Step 2: Multimodal Graph Understanding (Gemini Model)

```python
client.models.generate_content(...)
```

The Gemini Vision model analyzes:

- Graph structure (Line, Bar, Pie, etc.)  
- Axis titles  
- Axis scales (Linear, Logarithmic, Dates)  
- Legend items  
- Visual plot elements  
- Data point positions  

This is not a traditional OCR.

The model performs visual reasoning + semantic interpretation.

---

## Step 3: Schema Enforcement (Structured Output)

The system enforces structured output using:

```python
response_schema = GraphMetadata
```

### Schema Includes:

- Graph type  
- X-axis title  
- Y-axis title  
- X-axis scale  
- Y-axis scale  
- Legend items  
- Extracted data points  

### Why is Schema Enforcement Important?

- Prevents free-text responses  
- Prevents hallucinated explanations  
- Forces correct data types  
- Improves reliability and consistency  

---

## Step 4: Data Point Structuring

Each extracted data point is mapped into:

```
DataPoint:
- x_value
- y_value
- series_name
```

The model performs:

- Visual coordinate detection  
- Mapping pixel positions to axis values  
- Associating color/marker with legend series  
- Numeric value extraction  

This converts visual graph representation into structured dataset format.

---

# Model Configuration

The system uses:

Model: gemini-3-flash-preview  

Configuration:

- Low temperature (0.1) → reduces randomness  
- response_mime_type = "application/json"  
- response_schema = GraphMetadata  

### Why Low Temperature?

- Improves numerical precision  
- Reduces inconsistent outputs  
- Ensures deterministic extraction  

---

## Step 5: Parsed Output Handling

```python
data = response.parsed
```

The response is automatically parsed into validated Python objects.

### Operations Performed:

- Type validation  
- Field validation  
- JSON-to-object conversion  
- Structured table formatting  

---

# Output

The system outputs:

- Graph type  
- Axis scale information  
- Legend items  
- Structured data table  

The extracted data is:

- Machine-readable  
- Cleanly formatted  
- Ready for CSV/DataFrame conversion  
- Suitable for analytics pipelines  

---

# Final Result

The Graph Extraction Module transforms graphical information into structured, analyzable data through:

- Visual understanding  
- Semantic interpretation  
- Coordinate reasoning  
- Strict schema enforcement  

It bridges the gap between visual data representation and machine-readable structured datasets.
