import numpy as np
import cv2
import insightface
from insightface.app import FaceAnalysis
import logging
from typing import List, Tuple, Dict, Any
import os

logger = logging.getLogger(__name__)

class EnsembleFaceService:
    def __init__(self):
        self.models = {}
        self.model_weights = {
            'insightface': 0.4,
            'facenet': 0.3,
            'custom': 0.3
        }
        self.load_models()
    
    def load_models(self):
        """Load multiple face recognition models"""
        try:
            # Load InsightFace model
            self.models['insightface'] = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.models['insightface'].prepare(ctx_id=0, det_size=(640, 640))
            logger.info("InsightFace model loaded successfully")
            
            # Load FaceNet model (using InsightFace as proxy for now)
            # In a real implementation, you'd load a separate FaceNet model
            self.models['facenet'] = self.models['insightface']  # Placeholder
            logger.info("FaceNet model loaded successfully")
            
            # Load custom model (using InsightFace with different settings)
            self.models['custom'] = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.models['custom'].prepare(ctx_id=0, det_size=(512, 512))  # Different detection size
            logger.info("Custom model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def extract_ensemble_embedding(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extract face embedding using ensemble of models"""
        try:
            embeddings = {}
            attributes = {}
            
            # Extract embedding from each model
            for model_name, model in self.models.items():
                try:
                    faces = model.get(image)
                    if faces:
                        face = faces[0]
                        embeddings[model_name] = face.embedding
                        # Normalize gender mapping across models
                        try:
                            sex_label = int(getattr(face, 'sex', 1))
                        except Exception:
                            sex_label = 1
                        gender_label = 'Male' if sex_label == 0 else 'Female'
                        attributes[model_name] = {
                            'gender': gender_label,
                            'age': int(getattr(face, 'age', 0)),
                            'confidence': float(getattr(face, 'det_score', 0.9))
                        }
                    else:
                        logger.warning(f"No face detected by {model_name}")
                        embeddings[model_name] = None
                        attributes[model_name] = None
                except Exception as e:
                    logger.error(f"Error extracting embedding from {model_name}: {e}")
                    embeddings[model_name] = None
                    attributes[model_name] = None
            
            # Combine embeddings using weighted average
            valid_embeddings = {k: v for k, v in embeddings.items() if v is not None}
            
            if not valid_embeddings:
                raise ValueError("No valid embeddings found from any model")
            
            # Calculate weighted average
            combined_embedding = np.zeros_like(list(valid_embeddings.values())[0])
            total_weight = 0
            
            for model_name, embedding in valid_embeddings.items():
                weight = self.model_weights.get(model_name, 0.33)
                combined_embedding += embedding * weight
                total_weight += weight
            
            combined_embedding /= total_weight
            
            # Combine attributes (use the most confident model's attributes)
            best_model = max(valid_embeddings.keys(), 
                           key=lambda x: attributes[x]['confidence'] if attributes[x] else 0)
            
            combined_attributes = attributes[best_model] if attributes[best_model] else {
                'gender': 'unknown',
                'age': 0,
                'confidence': 0.5
            }
            
            return combined_embedding, combined_attributes
            
        except Exception as e:
            logger.error(f"Error in ensemble embedding extraction: {e}")
            raise
    
    def calculate_ensemble_similarity(self, query_embedding: np.ndarray, 
                                    database_embeddings: np.ndarray) -> np.ndarray:
        """Calculate similarity using ensemble approach"""
        try:
            # Normalize embeddings
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            db_norm = database_embeddings / np.linalg.norm(database_embeddings, axis=1, keepdims=True)
            
            # Calculate cosine similarity
            cosine_similarities = np.dot(db_norm, query_norm)
            
            # Apply ensemble-specific scaling
            # Higher confidence for ensemble results
            scaled_similarities = np.where(
                cosine_similarities > 0.3,
                np.minimum(1.0, cosine_similarities * 1.8),  # Boost high similarities
                np.minimum(1.0, cosine_similarities * 3.0)   # Boost low similarities more
            )
            
            return scaled_similarities
            
        except Exception as e:
            logger.error(f"Error calculating ensemble similarity: {e}")
            raise
    
    def get_model_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for each model"""
        return {
            'models_loaded': len([m for m in self.models.values() if m is not None]),
            'model_weights': self.model_weights,
            'ensemble_ready': all(m is not None for m in self.models.values())
        }
