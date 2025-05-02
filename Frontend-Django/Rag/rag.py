import os
import sys
import json
import importlib.util
from pathlib import Path
import nbformat
from nbconvert import PythonExporter

class RAGClassifier:
    """Wrapper for RAG notebook to classify visualization type"""
    
    def __init__(self):
        self.rag_module = None
        self.rag_path = os.path.join(os.path.dirname(__file__), '..', 'TableToVisualization-RAG', 'RAG', 'RAG.ipynb')
        
        if os.path.exists(self.rag_path):
            try:
                # Convert notebook to python
                with open(self.rag_path) as f:
                    nb = nbformat.read(f, as_version=4)
                
                exporter = PythonExporter()
                source, _ = exporter.from_notebook_node(nb)
                
                # Create a module from the source
                import types
                self.rag_module = types.ModuleType('rag_module')
                exec(source, self.rag_module.__dict__)
            except Exception as e:
                print(f"Error loading RAG notebook: {e}")
    
    def classify_visualization(self, data_json):
        """
        Determine if the data should be visualized as a bar or line chart
        
        Args:
            data_json: The JSON data to classify
            
        Returns:
            'bar' or 'line'
        """
        try:
            if self.rag_module and hasattr(self.rag_module, 'predict_visualization_type'):
                # Adjust this call based on how your RAG model is implemented
                return self.rag_module.predict_visualization_type(data_json)
            else:
                # Fallback implementation
                print("WARNING: Using mock RAG classification - implement actual integration")
                # Simple heuristic for mock purposes
                if isinstance(data_json, list) and len(data_json) > 0:
                    # If data has sequential numeric contexts or time-related contexts, suggest line chart
                    contexts = [item.get('context', '').lower() for item in data_json]
                    values = [item.get('value', 0) for item in data_json]
                    
                    # Check for time patterns
                    time_indicators = ['day', 'month', 'year', 'hour', 'week', 'jan', 'feb', 'mar', 'apr']
                    has_time_context = any(any(t in ctx for t in time_indicators) for ctx in contexts)
                    
                    # Check for sequential numbers in context
                    numeric_pattern = all(item.strip().isdigit() for item in contexts if item.strip())
                    
                    if has_time_context or numeric_pattern:
                        return 'line'
                    else:
                        return 'bar'
                return 'line'  # Default to line
        except Exception as e:
            print(f"Error in visualization classification: {e}")
            return 'line'  # Default to line on error

def determine_visualization_type(data):
    """Interface function to use the RAG classifier"""
    rag = RAGClassifier()
    return rag.classify_visualization(data)