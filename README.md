
# Forensic Face Construction & Recognition using Deep Learning

AI-powered forensic system that **matches suspect sketches with real facial images** using deep learning and similarity search.

This project automates the traditional forensic sketch identification process by converting sketches into facial embeddings and comparing them with a photo database to identify potential suspects.

The system uses **InsightFace for feature extraction and FAISS for high-speed similarity search**, enabling investigators to retrieve matches within **milliseconds instead of hours**. 

---

# Project Overview

In many criminal investigations, there is **no photographic evidence** of the suspect. Investigators rely on **forensic sketches created from eyewitness descriptions**.

Traditional sketch comparison methods are:

* Manual
* Time-consuming
* Subjective
* Often inaccurate

This project introduces an **AI-based forensic sketch recognition system** that can automatically match sketches with real images in a database. 

The system:

* Extracts **facial embeddings using deep learning**
* Searches for similar faces using **FAISS vector search**
* Returns **Top-3 possible matches with similarity scores**

This reduces suspect identification time from **2-4 hours to under 1 second**. 

---

# Key Features

### Sketch-to-Face Recognition

Upload a forensic sketch and automatically identify similar faces from a database.

### Deep Learning Face Embeddings

Uses **InsightFace models** to generate **512-dimensional facial feature vectors** for accurate matching. 

### Multi-Model Ensemble

Combines multiple models to improve recognition accuracy by **~15% compared to a single model**. 

### High-Speed Similarity Search

Uses **FAISS (Facebook AI Similarity Search)** to perform vector comparison in **50-100ms**. 

### Interactive Web Interface

A React-based UI provides:

* Sketch upload
* Webcam capture
* Drawing canvas
* Search history
* Analytics dashboard

### Gender Filtering

Investigators can filter search results by **Male / Female / General** to narrow suspects.

---

# System Architecture

The system follows a **three-layer architecture**.

### 1️⃣ Presentation Layer (Frontend)

Built using **React.js**

Provides:

* Sketch upload
* Webcam capture
* Drawing canvas
* Search result visualization
* Analytics dashboard

### 2️⃣ Application Layer (Backend)

Built using **FastAPI**

Handles:

* Image preprocessing
* Face detection
* Feature extraction
* Ensemble processing
* Similarity search

### 3️⃣ Data Layer

Stores:

* Photo database
* Facial embeddings
* FAISS vector index

This architecture ensures **scalability, modularity, and high performance**. 

---

# System Workflow

```
User Uploads Sketch
        │
        ▼
Image Preprocessing
(resize + RGB conversion)
        │
        ▼
Face Detection
(InsightFace)
        │
        ▼
Embedding Extraction
(512-D facial vector)
        │
        ▼
FAISS Similarity Search
        │
        ▼
Top-3 Matching Faces
        │
        ▼
Results + Confidence Scores
```

---

# Technology Stack

## Backend

* Python
* FastAPI
* InsightFace
* FAISS
* NumPy
* OpenCV

## Frontend

* React.js
* JavaScript
* HTML
* CSS

## Machine Learning

* Deep Convolutional Neural Networks
* Multi-Model Ensemble
* Face Embedding Models

---

# Project Structure

```
Forensic-Face-Construction-and-Recognition
│
├── backend
│   ├── models
│   │   └── sketch2photo.pth
│   ├── services
│   ├── utils
│   └── app.py
│
├── frontend
│   ├── src
│   ├── components
│   ├── pages
│   └── App.js
│
├── dataset
│   └── face_images
│
├── requirements.txt
└── README.md
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/Sadiyakhan09/Forensic-Face-Construction-and-Recognition.git
cd Forensic-Face-Construction-and-Recognition
```

---

## Create Virtual Environment

```
python -m venv venv
```

Activate environment

Windows

```
venv\Scripts\activate
```

Linux / Mac

```
source venv/bin/activate
```

---

## Install Dependencies

```
pip install -r requirements.txt
```

---

# Run the Backend

```
cd backend
python app.py
```

Server will start at:

```
http://localhost:8000
```

---

# Run the Frontend

```
cd frontend
npm install
npm start
```

Open in browser:

```
http://localhost:3000
```

---
Output Demonstration
Sketch Input
<img src="images/sketch_input.png" width="350">
Generated Face from Sketch
<img src="images/generated_face.png" width="350">
Face Recognition Results
<img src="images/recognition_results.png" width="700">

The system retrieves the most similar faces from the database.

Example output:

Rank	Suspect ID	Similarity
1	Suspect_01	92.4%
2	Suspect_02	88.7%
3	Suspect_03	85.1%

# Performance Results

The system was tested on **188 sketch-photo pairs**.

### Accuracy

| Metric             | Result |
| ------------------ | ------ |
| Top-1 Accuracy     | ~90%   |
| Top-3 Accuracy     | ~97%   |
| Average Confidence | 0.85   |

### Performance

| Metric              | Result     |
| ------------------- | ---------- |
| FAISS Search Time   | 50-100 ms  |
| Total Response Time | 300-600 ms |
| Manual Method       | 2-4 hours  |

This demonstrates a **90% reduction in identification time**. 

---

# Applications

* Criminal suspect identification
* Law enforcement investigations
* Missing person identification
* Digital forensics
* Security systems

---

# Advantages

* High accuracy (85-95%)
* Real-time identification
* Automated suspect retrieval
* Scalable architecture
* Reduced investigation time

---

# Future Improvements

* Larger criminal database
* Mobile application
* Explainable AI for forensic transparency
* Integration with national crime databases
* Real-time CCTV sketch matching

---

# Author
* **BiBi Sadiya**


ATME College of Engineering
Visvesvaraya Technological University



This project is developed for **educational and research purposes**.

---

If you want, I can also give you **3 improvements that will make this repository look like a top-tier AI project for recruiters (with demo images, architecture diagrams, and badges)**.
