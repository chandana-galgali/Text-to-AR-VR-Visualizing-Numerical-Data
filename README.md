# 👓 Text to AR/VR: Generating AR/VR Visualization from Textual Description of Numerical Data

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Unity](https://img.shields.io/badge/Unity-2023.1.0-black)
![Status](https://img.shields.io/badge/Status-Completed-green)

## 📖 Overview
This project implements an end-to-end spatial computing and generative AI pipeline designed to transform unstructured text into interactive 3D data visualizations. Stepping into the highly constrained domain of spatial computing, the system operates through a sequential architecture:
1.  **Text Parsing (Django UI & LLM):** Users input free-form textual descriptions of numerical data (e.g., year-over-year yield percentages) via a custom Django web interface. An LLM processes this and structures it into a clean JSON/Table format.
2.  **Visualization Selection (RAG):** A custom Retrieval-Augmented Generation (RAG) framework analyzes the structured data to intelligently predict the optimal visualization type (Bar Chart or Line Chart) and logically assign the X and Y axes.
3.  **Spatial Rendering (Unity):** The system programmatically translates the data into interactive 3D assets mapped to spatial coordinates for both Augmented Reality (AR) and Virtual Reality (VR) environments.

## 📂 Custom Dataset Compilation & RAG Training
Because standard datasets for mapping textual descriptions to 3D spatial charts did not exist, a custom dataset was curated from the ground up.

*   **Source:** Data was aggregated from the Open Government Data (OGD) Platform (`data.gov.in`).
*   **Dataset Structure:** The dataset consists of various educational metrics (e.g., student enrollment, school infrastructure) presented as tabular data paired with their corresponding ideal visual representations. 
*   **RAG Functionality:** By training on these table-to-chart pairings, the RAG model learned to evaluate incoming JSON/tabular data and predict whether a Bar Chart or Line Chart is mathematically and logically suited for the data at hand.

## 🏗️ Model & System Architecture

### 1. Natural Language Parsing Module
*   **Input:** Users input textual descriptions of numerical data via a responsive Django frontend.
*   **Processing:** The LLM extracts the numerical values and corresponding categorical labels, outputting a strictly formatted JSON array.

### 2. Visualization & Axis Determination Module
*   **Function:** The RAG framework cross-references the JSON output with its trained OGD dataset.
*   **Evaluation & Accuracy:** Achieved an **88.89% accuracy rate**. A test case was only considered "passed" if the model correctly predicted the chart type *and* logically mapped the variables (e.g., correctly identifying that 'Years' belong on the X-axis and 'Yield %' belongs on the Y-axis).

### 3. Spatial Rendering & Unity Implementation (AR & VR)
*   **Engine Integration:** The RAG's finalized visualization mapping is piped directly into the Unity Engine for both Augmented Reality (AR) and Virtual Reality (VR) rendering.
*   **Dynamic Object Pooling:** To optimize spatial rendering, the Unity environment utilizes a pre-instantiated pool of 3D objects (e.g., a fixed maximum of 10 data points/bars).
    *   **For Bar Charts:** The system dynamically adjusts the height (Y-axis) of the required 3D bars based on the JSON values, automatically zeroing out the scale of any unused bars.
    *   **For Line Charts:** Similar logic is applied by plotting spatial points (nodes) at the correct X and Y coordinates based on the data, dynamically connecting them to form the line chart, and hiding any unused points.
*   **Immersive Interactivity:** The VR interface dynamically generates the 3D assets, enabling real-time user interaction. Users can edit the JSON data directly within the VR environment to see real-time chart updates, zoom, filter, and utilize hover-triggered tooltips to inspect specific 3D labels and numerical values.

## 🛠️ Tech Stack
*   **Backend & Interface:** Python (3.10), Django
*   **AI & Machine Learning:** Large Language Models (LLM), Retrieval-Augmented Generation (RAG)
*   **3D Spatial Computing:** Unity (2023.1.0)
*   **Web Visualization & Prototyping:** Three.js (0.152.0), D3.js (7.8.0), HTML, JavaScript

## 👥 Project Team
* **Authors:** Chandana Galgali, Prachi Gandhi, Mahek Thakkar, Harsh Singwi
* **Guide:** Avani Sakhapara (Department of Information Technology)
* **Institution:** K. J. Somaiya College of Engineering, Somaiya Vidyavihar University