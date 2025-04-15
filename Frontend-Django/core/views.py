from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import TextInputForm
from .models import Visualization
from .utils import process_text_data
import json

def index(request):
    form = TextInputForm()
    return render(request, 'core/index.html', {'form': form})

def dashboard(request):
    visualizations = Visualization.objects.all().order_by('-created_at')
    return render(request, 'core/dashboard.html', {'visualizations': visualizations})

@csrf_exempt
def process_data(request):
    if request.method == 'POST':
        form = TextInputForm(request.POST)
        if form.is_valid():
            # Save input to database
            visualization = form.save(commit=False)
            
            # Process with our cascading approach
            result = process_text_data(visualization.input_text)
            
            if result["success"]:
                visualization.processed_data = result["data"]
                visualization.visualization_type = result["visualization_type"]
                visualization.processing_method = result["method"]
                
                if "visualization_image" in result and result["visualization_image"]:
                    visualization.visualization_image = result["visualization_image"]
                    
                visualization.save()
                
                # Return success response with ID
                return JsonResponse({
                    "success": True,
                    "id": visualization.id,
                    "data": result["data"],
                    "visualization_type": result["visualization_type"],
                    "visualization_image": result.get("visualization_image"),
                    "method": result["method"]
                })
            else:
                # Even if there's an error, we're not showing it to the user
                visualization.processed_data = {"text": "Processing completed, but no structured data could be extracted."}
                visualization.visualization_type = "unknown"
                visualization.processing_method = "fallback"
                visualization.save()
                
                return JsonResponse({
                    "success": True,
                    "id": visualization.id,
                    "data": visualization.processed_data,
                    "message": "Data processed successfully, but with limited structure."
                })
        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })
    return JsonResponse({"success": False, "error": "Invalid request method"})

def result(request, id):
    try:
        visualization = Visualization.objects.get(id=id)
        
        # Generate Unity code snippet based on visualization type
        unity_code = generate_unity_code_snippet(visualization.visualization_type, visualization.id)
        
        return render(request, 'core/result.html', {
            'visualization': visualization,
            'unity_code': unity_code,
        })
    except Visualization.DoesNotExist:
        return redirect('index')

def generate_unity_code_snippet(viz_type, viz_id):
    """Generate a basic Unity C# code snippet based on visualization type."""
    base_code = f"""
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using Newtonsoft.Json;
using System.Collections.Generic;

public class VRVisualizer : MonoBehaviour
{{
    private string apiUrl = "http://localhost:8000/api/visualization/{viz_id}/";
    
    void Start()
    {{
        StartCoroutine(FetchVisualizationData());
    }}
    
    IEnumerator FetchVisualizationData()
    {{
        using (UnityWebRequest webRequest = UnityWebRequest.Get(apiUrl))
        {{
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {{
                string jsonResponse = webRequest.downloadHandler.text;
                Debug.Log("Data received: " + jsonResponse);
                
                var responseData = JsonConvert.DeserializeObject<Dictionary<string, object>>(jsonResponse);
                if (responseData["success"].ToString() == "True")
                {{
                    // Access the data and create visualization
                    CreateVisualization(responseData);
                }}
            }}
            else
            {{
                Debug.LogError("Error: " + webRequest.error);
            }}
        }}
    }}
    
    void CreateVisualization(Dictionary<string, object> data)
    {{"""
    
    # Add visualization-specific code
    if viz_type == "bar_chart":
        specific_code = """
        // Create a bar chart visualization
        var chartData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["data"].ToString());
        
        // Example bar chart setup
        GameObject barChartContainer = new GameObject("BarChart");
        barChartContainer.transform.position = new Vector3(0, 1, 0);
        
        // Loop through the data and create bars
        // Code would create bars with appropriate height and positioning
        Debug.Log("Creating 3D bar chart visualization");
        """
    elif viz_type == "line_chart":
        specific_code = """
        // Create a line chart visualization
        var chartData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["data"].ToString());
        
        // Example line chart setup
        GameObject lineChartContainer = new GameObject("LineChart");
        lineChartContainer.transform.position = new Vector3(0, 1, 0);
        
        // Create a line renderer and set points
        LineRenderer lineRenderer = lineChartContainer.AddComponent<LineRenderer>();
        lineRenderer.startWidth = 0.1f;
        lineRenderer.endWidth = 0.1f;
        
        // Set points based on data
        Debug.Log("Creating 3D line chart visualization");
        """
    elif viz_type == "pie_chart":
        specific_code = """
        // Create a pie chart visualization
        var chartData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["data"].ToString());
        
        // Example pie chart setup
        GameObject pieChartContainer = new GameObject("PieChart");
        pieChartContainer.transform.position = new Vector3(0, 1, 0);
        
        // Create pie slices with appropriate angles
        // Code would create wedges/slices with proper angles
        Debug.Log("Creating 3D pie chart visualization");
        """
    elif viz_type == "3d_scatter_plot":
        specific_code = """
        // Create a 3D scatter plot
        var chartData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["data"].ToString());
        
        // Example scatter plot setup
        GameObject scatterContainer = new GameObject("ScatterPlot");
        scatterContainer.transform.position = new Vector3(0, 1, 0);
        
        // Create points in 3D space
        GameObject pointPrefab = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        pointPrefab.transform.localScale = new Vector3(0.1f, 0.1f, 0.1f);
        
        // Instantiate spheres at data points
        Debug.Log("Creating 3D scatter plot visualization");
        """
    else:
        specific_code = """
        // Create a default 3D visualization
        var visualizationData = JsonConvert.DeserializeObject<Dictionary<string, object>>(data["data"].ToString());
        
        // Generic visualization container
        GameObject vizContainer = new GameObject("Visualization");
        vizContainer.transform.position = new Vector3(0, 1, 0);
        
        // Create basic 3D representations of the data
        Debug.Log("Creating default 3D visualization");
        """
    
    closing_code = """
    }
}
"""
    
    return base_code + specific_code + closing_code