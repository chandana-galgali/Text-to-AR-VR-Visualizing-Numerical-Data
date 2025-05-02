import json
import pandas as pd
import numpy as np
import re
from io import StringIO
import sys
import os
import subprocess
from django.conf import settings

def extract_numerical_data(text_data):
    """
    Extract numerical data from text and convert it to JSON.
    """
    # Try to detect tabular data with commas or tabs
    lines = text_data.strip().split('\n')
    
    # Check if it looks like CSV data
    if ',' in text_data:
        try:
            df = pd.read_csv(StringIO(text_data))
            return {
                'success': True,
                'data': df.to_dict('records'),
                'table_html': df.head().to_html(classes='table table-striped')
            }
        except Exception:
            pass
    
    # Check if it's tab-separated
    if '\t' in text_data:
        try:
            df = pd.read_csv(StringIO(text_data), sep='\t')
            return {
                'success': True,
                'data': df.to_dict('records'),
                'table_html': df.head().to_html(classes='table table-striped')
            }
        except Exception:
            pass
    
    # Try to extract numerical patterns with labels
    data = {}
    
    # Pattern for key-value pairs like "Q1: $10,000"
    kv_pattern = r'([A-Za-z0-9_\s]+):[\s]*([\$£€]?[\d,\.]+)'
    kv_matches = re.findall(kv_pattern, text_data)
    
    if kv_matches:
        for key, value in kv_matches:
            # Clean up the key and value
            clean_key = key.strip()
            clean_value = value.replace('$', '').replace('£', '').replace('€', '').replace(',', '')
            
            try:
                data[clean_key] = float(clean_value)
            except ValueError:
                data[clean_key] = clean_value
        
        df = pd.DataFrame([data])
        return {
            'success': True,
            'data': data,
            'format': 'key_value'
        }
    
    # Fallback to just extracting numbers with surrounding context
    number_pattern = r'([A-Za-z0-9_\s]+)?[\s]*([\$£€]?[\d,\.]+)([A-Za-z0-9_\s]+)?'
    number_matches = re.findall(number_pattern, text_data)
    
    if number_matches:
        extracted = []
        for prefix, number, suffix in number_matches:
            clean_number = number.replace('$', '').replace('£', '').replace('€', '').replace(',', '')
            try:
                extracted.append({
                    'context': (prefix + suffix).strip(),
                    'value': float(clean_number)
                })
            except ValueError:
                pass
        
        if extracted:
            return {
                'success': True,
                'data': extracted,
                'format': 'numerical_extraction'
            }
    
    # If all else fails, return failure
    return {
        'success': False,
        'error': 'Could not extract structured data'
    }

def determine_visualization_type_with_rag(data):
    """
    Use RAG model to determine the appropriate visualization type.
    """
    try:
        # Save the data to a temporary file
        temp_file_path = os.path.join(settings.BASE_DIR, 'temp_data.json')
        with open(temp_file_path, 'w') as f:
            json.dump(data, f)
        
        # Path to the RAG.ipynb
        rag_notebook_path = os.path.join(settings.BASE_DIR, 'RAG', 'RAG.ipynb')
        
        # Execute the notebook with the data
        result = subprocess.run([
            'jupyter', 'nbconvert', 
            '--to', 'notebook', 
            '--execute', 
            '--output', 'rag_output.ipynb', 
            '--ExecutePreprocessor.timeout=60',
            '--ExecutePreprocessor.kernel_name=python3',
            f'--param "data_path={temp_file_path}"',
            rag_notebook_path
        ], capture_output=True, text=True)
        
        # Read the output - this assumes the notebook saves its output to a file
        output_file_path = os.path.join(settings.BASE_DIR, 'rag_output.txt')
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as f:
                viz_type = f.read().strip()
                # Clean up
                os.remove(output_file_path)
            
            # Clean up temp data file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
            return viz_type
        
        # Clean up temp data file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        # Default to bar chart if RAG fails
        return 'bar_chart'
        
    except Exception as e:
        print(f"Error in RAG visualization determination: {e}")
        # Default to bar chart if there's an error
        return 'bar_chart'

def process_text_data(text_data):
    """
    Process text data by extracting structured data and determining visualization type.
    """
    # Extract numerical data
    extraction_result = extract_numerical_data(text_data)
    
    if not extraction_result.get('success', False):
        return {
            "success": False,
            "error": "Could not extract structured data from input"
        }
    
    # Get the extracted data
    extracted_data = extraction_result['data']
    
    # Determine visualization type using RAG
    viz_type = determine_visualization_type_with_rag(extracted_data)
    
    return {
        "success": True,
        "data": extracted_data,
        "visualization_type": viz_type
    }