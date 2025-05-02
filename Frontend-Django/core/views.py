import re
import os
import sys
import json
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Add the parent directory to sys.path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your RAG model
from Rag.rag import determine_visualization_type

import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def is_valid_number(value_str):
    """
    Check if a string can be converted to a valid number.
    """
    try:
        # Handle strings with commas in numbers
        clean_value = value_str.replace(',', '') if isinstance(value_str, str) else value_str
        float(clean_value)
        return True
    except ValueError:
        return False

def extract_numerical_data(text):
    """
    Extract numerical data from text and convert to JSON format.
    Returns a list of dictionaries with context (labels) and values.
    """
    data = []
    
    # Let's try a simple line-by-line approach first
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Basic pattern for "key: $value" format
        match = re.search(r'([^:]+):\s*\$?([0-9,.]+)', line)
        if match:
            context = match.group(1).strip()
            value_str = match.group(2).strip()
            try:
                # Clean up value by removing commas
                clean_value = value_str.replace(',', '')
                value = float(clean_value)
                data.append({
                    "context": context,
                    "value": value
                })
                continue  # Move to next line if we found a match
            except ValueError:
                pass  # Try other patterns if this fails
                
    # If the simple approach failed, try more complex patterns
    if not data:
        # Pattern 1: Look for "key: value" or "key - value" formats
        pattern1 = r'([a-zA-Z0-9\s\-\.,&]+?)[\s]*[:|-][\s]*\$?[\s]*([0-9,]+\.?\d*)'
        matches1 = re.findall(pattern1, text)
        
        # Pattern 2: Look for "value units for key" format (e.g., "10 items for category A")
        pattern2 = r'(\d+\.?\d*)[\s]+([a-zA-Z]+)[\s]+(?:for|in|of)[\s]+([a-zA-Z0-9\s\-\.,&]+)'
        matches2 = re.findall(pattern2, text)
        
        # Combine matches
        all_matches = matches1 + [(key, value) for value, unit, key in matches2]
        
        # Process matches
        for context, value in all_matches:
            try:
                # Clean up value by removing commas
                clean_value = value.replace(',', '')
                numeric_value = float(clean_value)
                data.append({
                    "context": context.strip(),
                    "value": numeric_value
                })
            except ValueError:
                continue
                
    # If we still don't have data, try a very basic approach - find any key-value pairs
    if not data:
        # Simple pattern for key-value pairs
        pattern = r'([A-Za-z]+).*?(\d[\d,.]*)'
        matches = re.findall(pattern, text)
        
        for context, value in matches:
            try:
                clean_value = value.replace(',', '')
                numeric_value = float(clean_value)
                data.append({
                    "context": context.strip(),
                    "value": numeric_value
                })
            except ValueError:
                continue
                
    # Debug output - uncomment if needed
    # print(f"Found {len(data)} data points")
                
    return data

def text_to_json(text):
    """
    Convert text to JSON format suitable for visualization.
    """
    # First check if text is already valid JSON
    try:
        json_data = json.loads(text)
        # If it's already an array of objects with context/value or similar structure
        if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
            return json_data
        # If it's a single object with key-value pairs
        elif isinstance(json_data, dict):
            return [{"context": key, "value": float(str(value).replace(',', ''))} 
                   for key, value in json_data.items() 
                   if is_valid_number(str(value).replace(',', ''))]
    except (json.JSONDecodeError, TypeError):
        # Not valid JSON, continue with extraction
        pass
    
    # Try to extract numerical data
    extracted_data = extract_numerical_data(text)
    
    # If we found data, return it
    if extracted_data:
        # Remove duplicates (keeping first occurrence)
        seen_contexts = set()
        unique_data = []
        for item in extracted_data:
            if item["context"] not in seen_contexts:
                seen_contexts.add(item["context"])
                unique_data.append(item)
        return unique_data
    
    # If still no data found, try one more approach: direct parse of specific formats
    if ":" in text:
        data = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)  # Split only on first colon
                if len(parts) == 2:
                    context = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    # Extract numbers from value part
                    number_match = re.search(r'\$?([0-9,.]+)', value_part)
                    if number_match:
                        try:
                            value_str = number_match.group(1).replace(',', '')
                            value = float(value_str)
                            data.append({
                                "context": context,
                                "value": value
                            })
                        except ValueError:
                            pass
        
        if data:
            return data
    
    # If all else fails, print debug message and return a simple placeholder
    print("Error: No numerical data found in the text")
    return [{"context": "No Data", "value": 0}]


def render_bar_chart(request):
    """
    Render the 3D bar chart page.
    """
    # Default sample data
    sample_data = [
        {"context": "Category A", "value": 10},
        {"context": "Category B", "value": 20},
        {"context": "Category C", "value": 15},
    ]
    
    # Get input text from the request
    input_text = request.GET.get('text', '')
    
    if input_text:
        # Process the input text to extract data
        json_data = text_to_json(input_text)
    else:
        # Use sample data if no input is provided
        json_data = sample_data
    
    # Render the template with the JSON data
    return render(request, '3d_bar_chart.html', {
        'json_data': json.dumps(json_data)
    })


@csrf_exempt
def process_text(request):
    """
    API endpoint to process text and return JSON data.
    """
    if request.method == 'POST':
        try:
            # Get the text from the request
            text = request.POST.get('text', '')
            
            # Process the text
            json_data = text_to_json(text)
            
            # Return the JSON data
            return JsonResponse({
                'success': True,
                'data': json_data
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are supported'
    })


def index(request):
    """Render the form page"""
    return render(request, 'core/index.html')

@csrf_exempt
def process_text(request):
    """Process the submitted text and determine visualization"""
    if request.method == 'POST':
        text = request.POST.get('text', '')
        
        # Extract data from text
        data = extract_numerical_data(text)
        
        if not data:
            return JsonResponse({'error': 'No numerical data found in the text'})
        
        # Use RAG model to determine visualization type
        viz_type = determine_visualization_type(data)
        
        # Store the data in session for the visualization view
        request.session['visualization_data'] = {
            'data': data,
            'type': viz_type
        }
        
        return JsonResponse({
            'success': True, 
            'data': data, 
            'visualization_type': viz_type,
            'redirect_url': f'/core/{viz_type}/'
        })
    
    return JsonResponse({'error': 'Invalid request method'})

def visualize(request, viz_type):
    """Render the visualization based on type"""
    viz_data = request.session.get('visualization_data', {})
    data = viz_data.get('data', [])
    
    # Convert data to JSON string for template
    json_data = json.dumps(data)
    
    if viz_type == 'bar':
        return render(request, 'core/bar_chart.html', {'json_data': json_data})
    elif viz_type == 'line':
        return render(request, 'core/line_chart.html', {'json_data': json_data})
    else:
        # Default to 3D line chart from your pasted template
        return render(request, '3d_line_chart.html', {'json_data': json_data})
