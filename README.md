# Text to AR/VR: Generating AR/VR Visualization from Textual Description of Numerical Data

Transforming unstructured textual descriptions of numerical data into immersive, interactive Augmented Reality (AR) and Virtual Reality (VR) environments using a sequential AI pipeline of Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

## 🚀 Overview

Unlike standard 2D generative models, creating a spatial computing environment requires translating abstract numbers into a structured format and programmatically placing consistent 3D assets within a coordinate system. This project introduces a novel end-to-end pipeline that bridges natural language parsing directly to AR/VR spatial rendering. 

The system processes unstructured text, converts it into a clean structured layout via an LLM, and uses a custom RAG framework to drive spatial rendering in Unity, restricting visualizations to bar charts and line charts for precise data representation.

## ✨ Key Features

* **Sequential Text-to-Structure Parsing:** Employs an LLM to accurately extract numerical data from free-form text and structure it cleanly.
* **RAG-Driven Visualization Selection:** Uses a custom RAG framework to analyze the structured data and intelligently select the optimal visualization type (bar charts and line charts).
* **Immersive 3D Spatial Rendering:** Programmatically positions 3D assets within a spatial coordinate system inside Unity.
* **Interactive VR Tools:** Enables real-time data editing via JSON fields, spatial zooming, filtering, and hover-triggered tooltips to inspect specific data labels and numerical values in 3D space.

## 🛠️ Tech Stack & Architecture

* **Backend & Processing:** Python, Django
* **AI & Machine Learning:** Large Language Models (LLMs), Retrieval-Augmented Generation (RAG)
* **3D & Spatial Computing:** Unity Engine
* **Prototyping & Web Visualization:** Three.js, D3.js

## 📊 Dataset & Validation

* **Custom Dataset:** Curated specifically for this domain using data sourced from the Open Government Data (OGD) Platform (`data.gov.in`).
* **Accuracy & Evaluation:** Achieved an **88.89% accuracy rate**, validated rigorously against government datasets by measuring successful chart-type selection and precise data-to-axis mapping along spatial X and Y coordinates.

## 👥 Authors
* Chandana Galgali (Project Lead)
* Prachi Gandhi
* Mahek Thakkar
* Harsh Singwi

**Guided by:** Avani Sakhapara (Department of Information Technology)
