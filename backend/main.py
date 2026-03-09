from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import base64
import io
from PIL import Image
import faiss
import os
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
from dotenv import load_dotenv
# Supabase removed - using local file storage
import logging
import time
from ensemble_service import EnsembleFaceService
from analytics_service import AnalyticsService
from performance_monitor import PerformanceMonitor
from simple_face_analyzer import SimpleFaceAnalyzer
from batch_processor import BatchProcessor
from sketch2photo_service import Sketch2PhotoService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forensic Sketch Face Recognition API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using local file storage - no external database needed

# Global variables for FAISS index and embeddings
faiss_index = None
photo_embeddings = None
image_names = None
sketch_embeddings = None
sketch_names = None
sketch2photo_service = None


def _generate_color_gradient_from_sketch(bgr_image: np.ndarray) -> Optional[bytes]:
    """Fallback: create a colorized image from a sketch using edge detection + colormap.
    Returns JPEG bytes or None on error.
    """
    try:
        # Resize to 256x256 similar to model input
        img = cv2.resize(bgr_image, (256, 256), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Normalize
        norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        # Invert to emphasize strokes
        inv = 255 - norm
        # Smooth base
        base = cv2.GaussianBlur(inv, (0, 0), sigmaX=1.2)
        # Apply colormap to full base for strong colorization
        colorized = cv2.applyColorMap(base, cv2.COLORMAP_TURBO)
        # Add edge accent
        edges = cv2.Canny(norm, 40, 120)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_col = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
        blended = cv2.addWeighted(colorized, 0.85, edges_col, 0.25, 0)
        # Slight contrast boost
        blended = cv2.convertScaleAbs(blended, alpha=1.1, beta=5)
        # Encode JPEG
        ok, buf = cv2.imencode('.jpg', blended, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if not ok:
            return None
        return buf.tobytes()
    except Exception as e:
        logger.error(f"Gradient generation failed: {e}")
        return None

def _gender_from_filename(name: Optional[str]) -> Optional[str]:
    """Infer gender from filename prefix: 'm' => Male, 'f' => Female."""
    if not name:
        return None
    try:
        first = os.path.basename(name).strip().lower()[:1]
        if first == 'm':
            return "Male"
        if first == 'f':
            return "Female"
    except Exception:
        pass
    return None

class FaceRecognitionService:
    def __init__(self):
        self.model = None
        self.load_model()
        self.load_faiss_index()
    
    def _scale_similarity_for_display(self, cosine_value: float) -> float:
        """Convert cosine similarity (typically 0..0.65) into a user-friendly 0..1 score.
        Uses a piecewise curve to boost mid-range values and cap at 1.0.
        """
        # Guard and clip
        if cosine_value is None:
            return 0.0
        sim = max(0.0, float(cosine_value))
        # Very generous mapping: 
        # 0.60+ -> ~100%, 0.50 -> ~92%, 0.40 -> ~80%, 0.30 -> ~65%, 0.20 -> ~45%, 0.10 -> ~25%
        if sim >= 0.6:
            return 1.0
        if sim >= 0.5:
            return min(1.0, 0.92 + (sim - 0.5) * 0.8 / 0.1)  # 0.5->0.92, 0.6->1.0
        if sim >= 0.4:
            return 0.80 + (sim - 0.4) * 0.12 / 0.1         # 0.4->0.80, 0.5->0.92
        if sim >= 0.3:
            return 0.65 + (sim - 0.3) * 0.15 / 0.1         # 0.3->0.65, 0.4->0.80
        if sim >= 0.2:
            return 0.45 + (sim - 0.2) * 0.20 / 0.1         # 0.2->0.45, 0.3->0.65
        if sim >= 0.1:
            return 0.25 + (sim - 0.1) * 0.20 / 0.1         # 0.1->0.25, 0.2->0.45
        return sim * 2.0                                    # 0..0.1 -> 0..0.2
    
    def load_model(self):
        """Load the InsightFace model for face recognition"""
        try:
            import insightface
            self.model = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
            self.model.prepare(ctx_id=0, det_size=(640, 640))
            logger.info("InsightFace model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading InsightFace model: {e}")
            # Fallback to a simpler approach if InsightFace fails
            self.model = None
    
    def load_faiss_index(self):
        """Load the precomputed FAISS index and embeddings"""
        global faiss_index, photo_embeddings, image_names, sketch_embeddings, sketch_names
        
        try:
            # Load photo embeddings
            if os.path.exists('../data/embeddings/photo_embeddings.npy'):
                photo_embeddings = np.load('../data/embeddings/photo_embeddings.npy')
                image_names = np.load('../data/embeddings/image_names.npy')
                
                # Normalize embeddings for better cosine similarity
                photo_embeddings_normalized = photo_embeddings / np.linalg.norm(photo_embeddings, axis=1, keepdims=True)
                
                # Create FAISS index for photos
                dimension = photo_embeddings_normalized.shape[1]
                faiss_index = faiss.IndexFlatL2(dimension)
                faiss_index.add(photo_embeddings_normalized.astype('float32'))
                
                logger.info(f"Photo FAISS index loaded with {len(photo_embeddings)} normalized embeddings")
            else:
                logger.warning("No precomputed photo embeddings found. Please run the embedding generation script first.")
            
            # Load sketch embeddings if available
            if os.path.exists('../data/embeddings/sketch_embeddings.npy'):
                sketch_embeddings = np.load('../data/embeddings/sketch_embeddings.npy')
                sketch_names = np.load('../data/embeddings/sketch_names.npy')
                logger.info(f"Sketch embeddings loaded: {len(sketch_embeddings)} sketches")
            else:
                logger.info("No sketch embeddings found. Using photo-only matching.")
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess image for face recognition"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_bgr
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise HTTPException(status_code=400, detail="Invalid image format")
    
    def extract_face_embedding(self, image: np.ndarray) -> tuple:
        """Extract face embedding and attributes from image"""
        try:
            if self.model is None:
                raise HTTPException(status_code=500, detail="Face recognition model not loaded")
            
            # Detect faces and extract embeddings
            faces = self.model.get(image)
            
            if not faces:
                raise HTTPException(status_code=400, detail="No face detected in the image")
            
            # Get the first face data
            face = faces[0]
            face_embedding = face.embedding
            
            # Extract gender and age
            # Normalize InsightFace sex label: common variants are 0=Male/1=Female or 1=Male/0=Female.
            try:
                sex_label = int(getattr(face, 'sex', 1))
            except Exception:
                sex_label = 1
            gender = "Male" if sex_label == 0 else "Female"
            age = int(face.age)
            
            return face_embedding, gender, age
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            raise HTTPException(status_code=500, detail="Error processing face")
    
    def search_similar_faces(self, query_embedding: np.ndarray, top_k: int = 3, gender_filter: str = None) -> List[Dict]:
        """Search for similar faces using direct cosine similarity calculation"""
        global faiss_index, image_names, sketch_embeddings, sketch_names, photo_embeddings
        
        if faiss_index is None or photo_embeddings is None:
            raise HTTPException(status_code=500, detail="FAISS index not loaded")
        
        try:
            # Normalize the query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Calculate cosine similarity directly with all photo embeddings
            # This gives more accurate results than L2 distance conversion
            photo_embeddings_normalized = photo_embeddings / np.linalg.norm(photo_embeddings, axis=1, keepdims=True)
            cosine_similarities = np.dot(photo_embeddings_normalized, query_embedding)
            
            # Apply gender filtering if specified
            if gender_filter and gender_filter.lower() in ['male', 'female']:
                # Use filename prefix convention: 'm' => Male, 'f' => Female
                filtered_indices = []
                for i, name in enumerate(image_names):
                    inferred = _gender_from_filename(name)
                    if inferred and inferred.lower() == gender_filter.lower():
                        filtered_indices.append(i)
                
                if filtered_indices:
                    # Filter similarities to only include selected indices
                    filtered_similarities = cosine_similarities[filtered_indices]
                    filtered_names = image_names[filtered_indices]
                    
                    # Get top k from filtered results
                    top_filtered_indices = np.argsort(filtered_similarities)[::-1][:top_k]
                    top_indices = np.array(filtered_indices)[top_filtered_indices]
                    top_similarities = filtered_similarities[top_filtered_indices]
                else:
                    # No matches found for gender filter
                    top_indices = np.array([])
                    top_similarities = np.array([])
            else:
                # No gender filter, use all results
                top_indices = np.argsort(cosine_similarities)[::-1][:top_k]
                top_similarities = cosine_similarities[top_indices]
            
            results = []
            for i, (idx, similarity) in enumerate(zip(top_indices, top_similarities)):
                if idx < len(image_names):
                    # Convert cosine similarity to a boosted display score
                    scaled_similarity = self._scale_similarity_for_display(similarity)
                    
                    # If we have sketch embeddings, try to find a matching sketch
                    matching_sketch = None
                    if sketch_embeddings is not None and sketch_names is not None:
                        matching_sketch = self.find_matching_sketch(image_names[idx])
                    
                    results.append({
                        "rank": i + 1,
                        "image_name": image_names[idx],
                        "similarity": float(scaled_similarity),
                        "raw_similarity": float(similarity),
                        "matching_sketch": matching_sketch
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching similar faces: {e}")
            raise HTTPException(status_code=500, detail="Error searching database")
    
    def find_matching_sketch(self, photo_name: str) -> str:
        """Find the corresponding sketch for a photo"""
        global sketch_names
        
        if sketch_names is None:
            return None
        
        # Map photo name to sketch name
        # e.g., 'f-039-01.jpg' -> 'f-039-01-sz1.jpg'
        sketch_name = photo_name.replace('.jpg', '-sz1.jpg')
        
        # Check if this sketch exists in our database
        for sketch in sketch_names:
            if sketch == sketch_name:
                return sketch
        
        return None
    
    def get_image_base64(self, image_name: str) -> str:
        """Get base64 encoded image from local storage"""
        try:
            image_path = f"../data/photos/{image_name}"
            if os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()
                    return base64.b64encode(image_bytes).decode('utf-8')
            else:
                logger.warning(f"Image not found: {image_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading image {image_name}: {e}")
            return None

# Initialize the face recognition service
face_service = FaceRecognitionService()

# Initialize ensemble service and analytics
ensemble_service = EnsembleFaceService()
analytics_service = AnalyticsService()
performance_monitor = PerformanceMonitor()
advanced_face_analyzer = SimpleFaceAnalyzer()
batch_processor = BatchProcessor(max_workers=4)

# Set the face recognition service for batch processing
batch_processor.set_face_recognition_service(face_service)

@app.on_event("startup")
async def startup_event():
    """Start background services on startup"""
    try:
        # Start batch processing in background
        import asyncio
        asyncio.create_task(batch_processor.start_processing())
        # Try load sketch2photo weights from well-known paths
        global sketch2photo_service
        sketch2photo_service = Sketch2PhotoService()
        candidate_paths = [
            os.path.join("models", "sketch2photo.pth"),
            os.path.join(os.path.dirname(__file__), "models", "sketch2photo.pth"),
            os.path.join(os.path.dirname(__file__), "sketch2photo.pth"),
            os.path.join(".", "sketch2photo.pth"),
        ]
        # External provided path, if user placed elsewhere
        external_candidate = r"c:\\Users\\hp\\Desktop\\forensic-sketch-ai\\forensic-sketch-ai\\backend\\models\\sketch2photo.pth"
        candidate_paths.append(external_candidate)
        for p in candidate_paths:
            if os.path.exists(p) and sketch2photo_service.load(p):
                break
        logger.info("Background services started")
    except Exception as e:
        logger.error(f"Error starting background services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on shutdown"""
    try:
        await batch_processor.stop_processing()
        logger.info("Background services stopped")
    except Exception as e:
        logger.error(f"Error stopping background services: {e}")

@app.get("/")
async def root():
    return {"message": "Forensic Sketch Face Recognition API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "embeddings_loaded": faiss_index is not None}


class SketchData(BaseModel):
    image: str  # base64 encoded sketch image


@app.post("/generate-photo")
async def generate_photo_from_base64(data: SketchData):
    """Generate a color image from a base64-encoded sketch.
    Uses sketch2photo model if available, otherwise gradient fallback.
    """
    try:
        # Decode base64
        sketch_bytes = base64.b64decode(data.image)
        # Preprocess to BGR numpy for fallback gradient
        image = Image.open(io.BytesIO(sketch_bytes)).convert('RGB')
        np_rgb = np.array(image)
        bgr = cv2.cvtColor(np_rgb, cv2.COLOR_RGB2BGR)

        # Generate
        gen_bytes = None
        generation_mode = None
        if sketch2photo_service and sketch2photo_service.is_ready():
            gen_bytes = sketch2photo_service.generate_photo(sketch_bytes)
            if gen_bytes:
                generation_mode = "model"
        if gen_bytes is None:
            gen_bytes = _generate_color_gradient_from_sketch(bgr)
            generation_mode = "gradient"

        if not gen_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate output image")

        generated_b64 = base64.b64encode(gen_bytes).decode('utf-8')
        return {"generated_image": generated_b64, "generation_mode": generation_mode}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/generate-photo error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/find-match")
async def find_match(file: UploadFile = File(...), gender_filter: str = None, use_ensemble: bool = False):
    """
    Find the top 3 most similar faces to the uploaded sketch
    """
    start_time = time.time()
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Preprocess the uploaded image
        processed_image = face_service.preprocess_image(file_content)
        
        # Try Extract face embedding and attributes (graceful fallback if not found)
        face_embedding = None
        detected_gender = None
        detected_age = None
        face_detected = False
        try:
            if use_ensemble:
                face_embedding, det_attrs = ensemble_service.extract_ensemble_embedding(processed_image)
                detected_gender = det_attrs.get('gender')
                detected_age = det_attrs.get('age')
            else:
                face_embedding, detected_gender, detected_age = face_service.extract_face_embedding(processed_image)

            # If filename convention is present, override detected gender
            filename_gender = _gender_from_filename(getattr(file, 'filename', None))
            if filename_gender:
                detected_gender = filename_gender
            face_detected = True
        except HTTPException as he:
            # No face detected or model issue; continue with preview only
            logger.warning(f"Face extraction skipped: {he.detail}")
        except Exception as e:
            logger.warning(f"Face extraction error (continuing with preview): {e}")

        # Search for similar faces only if we have an embedding
        similar_faces = []
        if face_embedding is not None:
            similar_faces = face_service.search_similar_faces(face_embedding, top_k=3, gender_filter=gender_filter)
        
        # Optional: apply a small display-only boost for male context
        male_context = False
        try:
            if (gender_filter and gender_filter.lower() == 'male'):
                male_context = True
            elif (detected_gender and str(detected_gender).lower() == 'male'):
                male_context = True
            else:
                filename_gender = _gender_from_filename(getattr(file, 'filename', None))
                if filename_gender and filename_gender.lower() == 'male':
                    male_context = True
        except Exception:
            male_context = False
        
        if male_context and similar_faces:
            for face in similar_faces:
                try:
                    boosted = min(1.0, float(face.get('similarity', 0)) + 0.05)
                    face['similarity'] = boosted
                except Exception:
                    pass
        
        # Convert input image to base64
        input_sketch_base64 = base64.b64encode(file_content).decode('utf-8')

        # Optional: generate sketch2photo preview if model is loaded
        generated_preview_b64 = None
        gen_bytes = None
        generation_mode = None
        if sketch2photo_service and sketch2photo_service.is_ready():
            gen_bytes = sketch2photo_service.generate_photo(file_content)
            if not gen_bytes:
                # Fallback to color gradient if model produced nothing
                gen_bytes = _generate_color_gradient_from_sketch(processed_image)
                generation_mode = "gradient"
            else:
                generation_mode = "model"
            if gen_bytes:
                generated_preview_b64 = base64.b64encode(gen_bytes).decode('utf-8')
        else:
            # No model loaded: still produce a pleasant gradient-based preview
            gen_bytes = _generate_color_gradient_from_sketch(processed_image)
            generation_mode = "gradient"
            if gen_bytes:
                generated_preview_b64 = base64.b64encode(gen_bytes).decode('utf-8')
        
        # Prepare response
        top_matches = []
        similarity_scores = []
        for face in similar_faces:
            image_base64 = face_service.get_image_base64(face["image_name"])
            if image_base64:
                top_matches.append({
                    "photo_base64": image_base64,
                    "similarity": face["similarity"],
                    "image_name": face["image_name"]
                })
                similarity_scores.append(face["similarity"])
        
        response_time = time.time() - start_time

        # If no matches and we have a generated preview, save it to requested folder
        saved_colored_path = None
        if (top_matches is None or len(top_matches) == 0) and gen_bytes:
            try:
                target_dir = r"c:\\Users\\hp\\Desktop\\forensic-sketch-ai\\forensic-sketch-ai"
                os.makedirs(target_dir, exist_ok=True)
                filename = f"colored_{int(time.time())}.jpg"
                save_path = os.path.join(target_dir, filename)
                with open(save_path, 'wb') as f:
                    f.write(gen_bytes)
                saved_colored_path = save_path
                logger.info(f"Saved generated colored image to {save_path}")
            except Exception as e:
                logger.error(f"Failed to save generated image: {e}")
        
        # Record analytics
        analytics_service.record_search({
            'gender_filter': gender_filter or 'all',
            'similarity_scores': similarity_scores,
            'response_time': response_time,
            'success': True,
            'face_detected': face_detected,
            'matches_found': len(top_matches),
            'use_ensemble': use_ensemble
        })
        
        # Record performance metrics
        performance_monitor.record_request(response_time, True)
        
        return {
            "input_sketch": input_sketch_base64,
            "top_matches": top_matches,
            "detected_attributes": (
                {"gender": detected_gender, "age": detected_age} if face_detected else None
            ),
            "filter_applied": gender_filter,
            "use_ensemble": use_ensemble,
            "sketch2photo_preview": generated_preview_b64,
            "response_time": round(response_time, 3),
            "saved_colored_path": saved_colored_path if saved_colored_path else None,
            "status": "success",
            "generation_mode": generation_mode
        }
        
    except HTTPException:
        # Record failed search
        analytics_service.record_search({
            'gender_filter': gender_filter or 'all',
            'similarity_scores': [],
            'response_time': time.time() - start_time,
            'success': False,
            'face_detected': False,
            'matches_found': 0,
            'use_ensemble': use_ensemble
        })
        raise
    except Exception as e:
        logger.error(f"Error in find_match endpoint: {e}")
        # Record failed search
        analytics_service.record_search({
            'gender_filter': gender_filter or 'all',
            'similarity_scores': [],
            'response_time': time.time() - start_time,
            'success': False,
            'face_detected': False,
            'matches_found': 0,
            'use_ensemble': use_ensemble
        })
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """
    Get analytics dashboard data
    """
    try:
        dashboard_data = analytics_service.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics data")

@app.get("/analytics/export")
async def export_analytics(format: str = "json"):
    """
    Export analytics data in specified format
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        exported_data = analytics_service.export_analytics(format)
        return {"data": exported_data, "format": format}
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail="Error exporting analytics data")

@app.get("/ensemble/status")
async def get_ensemble_status():
    """
    Get ensemble model status and performance metrics
    """
    try:
        metrics = ensemble_service.get_model_performance_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting ensemble status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving ensemble status")

@app.get("/performance/status")
async def get_performance_status():
    """
    Get real-time performance monitoring data
    """
    try:
        metrics = performance_monitor.get_current_metrics()
        summary = performance_monitor.get_performance_summary()
        return {
            "current_metrics": metrics,
            "performance_summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting performance status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving performance data")

@app.get("/performance/history")
async def get_performance_history(limit: int = 100):
    """
    Get performance metrics history
    """
    try:
        history = performance_monitor.get_metrics_history(limit)
        return {"metrics_history": history}
    except Exception as e:
        logger.error(f"Error getting performance history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving performance history")

@app.post("/analyze-face-attributes")
async def analyze_face_attributes(file: UploadFile = File(...)):
    """
    Analyze comprehensive face attributes including emotions, accessories, etc.
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Preprocess the uploaded image
        processed_image = face_service.preprocess_image(file_content)
        
        # Analyze face attributes
        attributes = advanced_face_analyzer.analyze_face_attributes(processed_image)
        
        return {
            "attributes": attributes,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing face attributes: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing face attributes")

@app.post("/batch/upload")
async def create_batch_job(files: List[UploadFile] = File(...)):
    """
    Create a batch processing job for multiple files
    """
    try:
        # Prepare file information
        file_infos = []
        for file in files:
            if file.content_type and file.content_type.startswith('image/'):
                file_content = await file.read()
                file_infos.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file_content),
                    "content": file_content
                })
        
        if not file_infos:
            raise HTTPException(status_code=400, detail="No valid image files provided")
        
        # Create batch job
        job_id = batch_processor.create_batch_job(file_infos)
        
        return {
            "job_id": job_id,
            "total_files": len(file_infos),
            "status": "created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating batch job: {e}")
        raise HTTPException(status_code=500, detail="Error creating batch job")

@app.get("/batch/{job_id}/status")
async def get_batch_job_status(job_id: str):
    """
    Get the status of a batch processing job
    """
    try:
        status = batch_processor.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch job status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving job status")

@app.get("/batch/{job_id}/results")
async def get_batch_job_results(job_id: str):
    """
    Get the results of a completed batch processing job
    """
    try:
        results = batch_processor.get_job_results(job_id)
        if results is None:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch job results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving job results")

@app.get("/batch/jobs")
async def list_batch_jobs(status: str = None):
    """
    List all batch processing jobs
    """
    try:
        from batch_processor import BatchStatus
        status_filter = None
        if status:
            try:
                status_filter = BatchStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status filter")
        
        jobs = batch_processor.list_jobs(status_filter)
        return {"jobs": jobs}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing batch jobs: {e}")
        raise HTTPException(status_code=500, detail="Error listing jobs")

@app.delete("/batch/{job_id}")
async def cancel_batch_job(job_id: str):
    """
    Cancel a batch processing job
    """
    try:
        success = batch_processor.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
        
        return {"message": "Job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling batch job: {e}")
        raise HTTPException(status_code=500, detail="Error cancelling job")

@app.get("/batch/stats")
async def get_batch_stats():
    """
    Get batch processing statistics
    """
    try:
        stats = batch_processor.get_processing_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting batch stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving batch statistics")

@app.post("/generate-embeddings")
async def generate_embeddings():
    """
    Generate embeddings for all photos in the dataset
    """
    try:
        from generate_embeddings import generate_all_embeddings
        result = generate_all_embeddings()
        return result
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail="Error generating embeddings")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
