import json
import openai
import pandas as pd
import numpy as np
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO, StringIO
from django.conf import settings

def extract_numerical_data(text_data):
    """
    Extract numerical data from text and attempt to convert it to a structured format.
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
                'visualization_type': suggest_visualization(df),
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
                'visualization_type': suggest_visualization(df),
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
            'visualization_type': suggest_visualization_from_dict(data),
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
                'visualization_type': 'bar_chart',  # Default for simple numerical data
                'format': 'numerical_extraction'
            }
    
    # If all else fails, return None to indicate fallback to OpenAI API
    return None

def suggest_visualization(df):
    """Suggest a visualization type based on the DataFrame structure."""
    columns = df.columns.tolist()
    
    # If we have time-based column names
    time_indicators = ['date', 'year', 'month', 'quarter', 'day', 'time']
    has_time_column = any(time_col in ' '.join(columns).lower() for time_col in time_indicators)
    
    # Check for numeric columns
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    # Simple logic for suggestions
    if has_time_column and len(numeric_columns) > 0:
        return 'line_chart'
    elif len(numeric_columns) == 1 and len(columns) == 2:
        return 'bar_chart'
    elif len(numeric_columns) > 1 and len(columns) <= 5:
        return 'radar_chart'
    elif len(numeric_columns) == 1:
        return 'bar_chart'
    elif len(numeric_columns) > 3:
        return '3d_scatter_plot'
    else:
        return 'bar_chart'

def suggest_visualization_from_dict(data_dict):
    """Suggest visualization based on key-value dictionary."""
    keys = list(data_dict.keys())
    
    # Look for time indicators in keys
    time_indicators = ['q1', 'q2', 'q3', 'q4', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                      'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'year', 'month', 'quarter']
    
    time_keys = any(time_ind in ' '.join(keys).lower() for time_ind in time_indicators)
    
    # Basic suggestions
    if time_keys:
        return 'line_chart'
    elif len(keys) <= 10:
        return 'bar_chart'
    elif len(keys) > 10 and len(keys) <= 20:
        return 'pie_chart'
    else:
        return '3d_bar_chart'

def generate_2d_visualization(data, viz_type):
    """Generate a 2D matplotlib visualization based on data and visualization type."""
    plt.figure(figsize=(10, 6))
    plt.style.use('ggplot')
    
    try:
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Handle list of dictionaries
            if 'context' in data[0] and 'value' in data[0]:
                # Handle extracted numerical data
                contexts = [item['context'] if item['context'] else f"Item {i}" for i, item in enumerate(data)]
                values = [item['value'] for item in data]
                
                if viz_type == 'bar_chart':
                    plt.bar(contexts, values, color='skyblue')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                elif viz_type == 'pie_chart':
                    plt.pie(values, labels=contexts, autopct='%1.1f%%', startangle=90)
                    plt.axis('equal')
                else:
                    plt.bar(contexts, values, color='skyblue')  # Default to bar chart
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
            else:
                # Handle records with columns
                df = pd.DataFrame(data)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) == 0:
                    return None
                
                if viz_type == 'line_chart' and len(df) > 1:
                    for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                        plt.plot(df.index, df[col], marker='o', label=col)
                    plt.legend()
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                elif viz_type == 'bar_chart':
                    df[numeric_cols[0]].plot(kind='bar', color='skyblue')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                elif viz_type == 'pie_chart' and len(numeric_cols) > 0:
                    data_to_plot = df[numeric_cols[0]].abs()  # Use absolute values for pie chart
                    plt.pie(data_to_plot, labels=df.index, autopct='%1.1f%%', startangle=90)
                    plt.axis('equal')
                elif viz_type == 'scatter_plot' and len(numeric_cols) >= 2:
                    plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
                    plt.xlabel(numeric_cols[0])
                    plt.ylabel(numeric_cols[1])
                else:
                    # Default to bar chart
                    df[numeric_cols[0]].plot(kind='bar', color='skyblue')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
        else:
            # Handle dictionary data
            keys = list(data.keys())
            values = list(data.values())
            
            # Filter out non-numeric values
            numeric_data = [(k, v) for k, v in zip(keys, values) if isinstance(v, (int, float))]
            if not numeric_data:
                return None
                
            keys, values = zip(*numeric_data)
            
            if viz_type == 'bar_chart':
                plt.bar(keys, values, color='skyblue')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
            elif viz_type == 'line_chart':
                plt.plot(keys, values, marker='o', color='skyblue')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
            elif viz_type == 'pie_chart':
                plt.pie([abs(v) for v in values], labels=keys, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
            else:
                plt.bar(keys, values, color='skyblue')  # Default to bar chart
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error generating visualization: {e}")
        plt.close()
        return None

def process_text_data(text_data):
    """Process text data using script-based approach first, then fallback to OpenAI API."""
    
    # First try script-based numerical data extraction
    script_result = extract_numerical_data(text_data)
    
    if script_result and script_result.get('success', False):
        # Generate 2D visualization
        viz_type = script_result.get('visualization_type', 'bar_chart')
        viz_image = generate_2d_visualization(script_result['data'], viz_type)
        
        if viz_image:
            script_result['visualization_image'] = viz_image
        
        return {
            "success": True,
            "data": script_result['data'],
            "visualization_type": viz_type,
            "visualization_image": viz_image,
            "method": "script"
        }
    
    # Fallback to OpenAI API
    try:
        openai_result = process_with_openai(text_data)
        
        if openai_result.get('success', False):
            # Try to generate 2D visualization from OpenAI data
            viz_type = openai_result.get('data', {}).get('visualization_type', 'bar_chart')
            viz_data = openai_result.get('data', {}).get('data', openai_result.get('data', {}))
            viz_image = generate_2d_visualization(viz_data, viz_type)
            
            if viz_image:
                openai_result['visualization_image'] = viz_image
            
            return {
                "success": True,
                "data": openai_result['data'],
                "visualization_type": viz_type,
                "visualization_image": viz_image,
                "method": "openai"
            }
    except Exception as e:
        # Silently fail and return a default response
        pass
    
    # If both approaches fail, return a basic response with no error
    return {
        "success": True,
        "data": {"text": "Unable to extract structured data. Please try reformatting your input."},
        "visualization_type": "unknown",
        "method": "fallback"
    }

def process_with_openai(text_data):
    """Process text data using OpenAI API to extract numerical data and suggest visualization."""
    try:
        openai.api_key = settings.OPENAI_API_KEY
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst assistant. Extract numerical data from the given text and format it as a structured JSON with two main keys: 'data' (containing the extracted data) and 'visualization_type' (suggesting one of: bar_chart, line_chart, pie_chart, scatter_plot, 3d_bar_chart, 3d_scatter_plot)."},
                {"role": "user", "content": text_data}
            ]
        )
        
        result = response.choices[0].message.content
        
        # Try to parse the response as JSON
        try:
            data = json.loads(result)
            return {
                "success": True,
                "data": data
            }
        except json.JSONDecodeError:
            # If response isn't in JSON format, return it as-is
            return {
                "success": True,
                "data": {"text": result}
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }