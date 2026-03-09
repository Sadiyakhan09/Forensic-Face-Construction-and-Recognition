import cv2
import numpy as np
import logging
from typing import Dict, Any
from insightface.app import FaceAnalysis
from insightface.app import FaceAnalysis

logger = logging.getLogger(__name__)

class SimpleFaceAnalyzer:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the InsightFace model for face analysis"""
        try:
            self.model = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.model.prepare(ctx_id=0, det_size=(640, 640))
            logger.info("Simple face analyzer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading simple face analyzer model: {e}")
            self.model = None
    
    def analyze_face_attributes(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze basic face attributes"""
        if self.model is None:
            raise ValueError("Face analyzer model not loaded")
        
        try:
            faces = self.model.get(image)
            if not faces:
                return {"error": "No face detected"}
            
            face = faces[0]
            
            # Basic attributes
            # Some InsightFace builds use 0=Male, 1=Female. Invert mapping accordingly.
            try:
                sex_label = int(getattr(face, 'sex', 1))
            except Exception:
                sex_label = 1
            gender = "Male" if sex_label == 0 else "Female"
            age = int(face.age)
            confidence = float(getattr(face, 'det_score', 0.9))
            
            # Simple facial analysis
            bbox = face.bbox
            width = float(bbox[2] - bbox[0])
            height = float(bbox[3] - bbox[1])
            aspect_ratio = float(width / height)
            
            # Determine face shape based on aspect ratio
            if aspect_ratio > 0.85:
                face_shape = "round"
            elif aspect_ratio < 0.75:
                face_shape = "oval"
            else:
                face_shape = "square"
            
            # Simple emotion analysis (placeholder)
            emotions = {
                "happiness": 0.3,
                "sadness": 0.1,
                "anger": 0.1,
                "surprise": 0.1,
                "fear": 0.1,
                "neutral": 0.3
            }
            
            # Simple accessory detection (placeholder)
            accessories = {
                "glasses": {
                    "detected": False,
                    "confidence": 0.0
                },
                "mask": {
                    "detected": False,
                    "confidence": 0.0
                }
            }
            
            return {
                "basic": {
                    "gender": gender,
                    "age": age,
                    "confidence": confidence
                },
                "facial_features": {
                    "face_ratio": aspect_ratio,
                    "face_width": width,
                    "face_height": height,
                    "face_shape": face_shape
                },
                "emotions": {
                    "emotions": emotions,
                    "dominant_emotion": "neutral",
                    "confidence": 0.3
                },
                "accessories": accessories,
                "face_shape": {
                    "shape": face_shape,
                    "aspect_ratio": aspect_ratio
                },
                "skin_tone": {
                    "tone": "medium",
                    "confidence": 0.5
                },
                "facial_hair": {
                    "beard": {"detected": False, "confidence": 0.0},
                    "mustache": {"detected": False, "confidence": 0.0}
                },
                "eye_characteristics": {
                    "eye_color": "brown",
                    "eye_size": "normal"
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face attributes: {e}")
            return {"error": str(e)}



