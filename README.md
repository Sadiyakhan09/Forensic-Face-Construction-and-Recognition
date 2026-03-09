
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
<img width="714" height="401" alt="Screenshot 2026-03-09 175942" src="https://github.com/user-attachments/assets/7035dc83-c874-4872-848f-6729071875ad" />
<img width="730" height="429" alt="Screenshot 2026-03-09 180042" src="https://github.com/user-attachments/assets/ef7883ea-d1e0-4026-910d-7e5a82979702" />

<img width="743" height="381" alt="Screenshot 2026-03-09 180224" src="https://github.com/user-attachments/assets/85620148-3ed4-4113-9087-1ef768f5f6b2" />

Generated Face from Sketch
<img width="735" height="407" alt="Screenshot 2026-03-09 180101" src="https://github.com/user-attachments/assets/00956dd5-d1cc-43e0-94de-cb338f730d1d" />
<img width="731" height="400" alt="Screenshot 2026-03-09 180121" src="https://github.com/user-attachments/assets/1deec1ae-67b2-455e-a578-dae60aea4acd" /> Real time face sketch scanning through Web cam
<img width="744" height="402" alt="Screenshot 2026-03-09 180251" src="https://github.com/user-attachments/assets/61b3b36a-17a9-468a-8124-08c3dadfabd1" />


Face Recognition Analytics
<img width="719" height="407" alt="Screenshot 2026-03-09 180328" src="https://github.com/user-attachments/assets/017e0015-c7bb-45cf-989b-2d4a2f1d1eaa" />
<img width="726" height="396" alt="Screenshot 2026-03-09 180310" src="https://github.com/user-attachments/assets/05cbe891-0a2d-4caf-9fa6-779eb84cb3c7" />
<img width="735" height="403" alt="Screenshot 2026-03-09 180347" src="https://github.com/user-attachments/assets/83c3d492-b5ae-4a8a-9513-579da5d633e5" />


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
