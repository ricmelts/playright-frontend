from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import structlog
import os

logger = structlog.get_logger()

class EmbeddingModel:
    _instance = None
    _model = None
    _model_loaded = False
    
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EmbeddingModel()
            cls._instance.load_model()
        return cls._instance
    
    @classmethod
    def load_model(cls):
        """Load the sentence transformer model"""
        if not cls._model_loaded:
            try:
                instance = cls.get_instance() if cls._instance else EmbeddingModel()
                logger.info("Loading embedding model", model=instance.model_name)
                
                cls._model = SentenceTransformer(
                    instance.model_name,
                    cache_folder=instance.cache_dir
                )
                cls._model_loaded = True
                
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error("Failed to load embedding model", error=str(e))
                raise
    
    @classmethod
    def is_loaded(cls):
        return cls._model_loaded and cls._model is not None
    
    def create_athlete_embedding(self, athlete_data: Dict, metrics: List[Dict]) -> np.ndarray:
        """Create embedding vector for athlete profile"""
        if not self._model:
            raise RuntimeError("Model not loaded")
        
        # Build comprehensive athlete profile text
        profile_components = []
        
        # Basic info
        sport = athlete_data.get("sport", "")
        position = athlete_data.get("position", "")
        school = athlete_data.get("school", "")
        location = athlete_data.get("location", "")
        bio = athlete_data.get("bio", "")
        
        profile_components.extend([
            f"Sport: {sport}",
            f"Position: {position}" if position else "",
            f"School: {school}",
            f"Location: {location}",
            f"Biography: {bio}" if bio else ""
        ])
        
        # Social media metrics
        if metrics:
            total_followers = sum(m.get("followers", 0) for m in metrics)
            avg_engagement = np.mean([m.get("engagement_rate", 0) for m in metrics])
            platforms = [m.get("platform", "") for m in metrics]
            
            profile_components.extend([
                f"Social media reach: {total_followers} total followers",
                f"Engagement rate: {avg_engagement:.1f}%",
                f"Active platforms: {', '.join(platforms)}"
            ])
            
            # Content categories
            all_categories = []
            for m in metrics:
                categories = m.get("content_categories", [])
                all_categories.extend(categories)
            unique_categories = list(set(all_categories))
            
            if unique_categories:
                profile_components.append(f"Content focus: {', '.join(unique_categories)}")
        
        # Combine all components
        profile_text = " | ".join([comp for comp in profile_components if comp])
        
        # Generate embedding
        embedding = self._model.encode([profile_text])[0]
        
        logger.debug("Athlete embedding created", 
                    athlete_id=athlete_data.get("id"),
                    profile_length=len(profile_text),
                    embedding_dim=len(embedding))
        
        return embedding
    
    def create_brand_embedding(self, brand_data: Dict) -> np.ndarray:
        """Create embedding vector for brand profile"""
        if not self._model:
            raise RuntimeError("Model not loaded")
        
        # Build comprehensive brand profile text
        profile_components = []
        
        # Basic info
        company_name = brand_data.get("company_name", "")
        industry = brand_data.get("industry", "")
        description = brand_data.get("description", "")
        location = brand_data.get("location", "")
        
        profile_components.extend([
            f"Company: {company_name}",
            f"Industry: {industry}",
            f"Description: {description}" if description else "",
            f"Location: {location}"
        ])
        
        # Preferences and targeting
        preferred_sports = brand_data.get("preferred_sports", [])
        target_demographics = brand_data.get("target_demographics", {})
        
        if preferred_sports:
            profile_components.append(f"Target sports: {', '.join(preferred_sports)}")
        
        if target_demographics:
            demo_text = []
            age_groups = target_demographics.get("age_groups", {})
            if age_groups:
                primary_age = max(age_groups.items(), key=lambda x: x[1])[0]
                demo_text.append(f"Primary age group: {primary_age}")
            
            gender = target_demographics.get("gender", {})
            if gender:
                primary_gender = max(gender.items(), key=lambda x: x[1])[0]
                demo_text.append(f"Primary gender: {primary_gender}")
            
            if demo_text:
                profile_components.append(f"Target demographics: {', '.join(demo_text)}")
        
        # Budget information
        budget_min = brand_data.get("budget_min", 0)
        budget_max = brand_data.get("budget_max", 0)
        if budget_max > 0:
            profile_components.append(f"Budget range: ${budget_min:,.0f} - ${budget_max:,.0f}")
        
        # Combine all components
        profile_text = " | ".join([comp for comp in profile_components if comp])
        
        # Generate embedding
        embedding = self._model.encode([profile_text])[0]
        
        logger.debug("Brand embedding created",
                    brand_id=brand_data.get("id"),
                    profile_length=len(profile_text),
                    embedding_dim=len(embedding))
        
        return embedding
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return float(similarity)
    
    def find_similar_athletes(self, target_athlete_embedding: np.ndarray, 
                            candidate_embeddings: List[np.ndarray], 
                            threshold: float = 0.7) -> List[int]:
        """Find athletes similar to target athlete"""
        if not candidate_embeddings:
            return []
        
        similarities = cosine_similarity([target_athlete_embedding], candidate_embeddings)[0]
        similar_indices = np.where(similarities >= threshold)[0]
        
        # Sort by similarity score
        sorted_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]]
        
        return sorted_indices.tolist()
    
    def batch_similarity_calculation(self, 
                                   athlete_embeddings: List[np.ndarray], 
                                   brand_embeddings: List[np.ndarray]) -> np.ndarray:
        """Calculate similarity matrix for batch processing"""
        if not athlete_embeddings or not brand_embeddings:
            return np.array([])
        
        # Calculate similarity matrix: athletes x brands
        similarity_matrix = cosine_similarity(athlete_embeddings, brand_embeddings)
        
        logger.info("Batch similarity calculation completed",
                   athletes_count=len(athlete_embeddings),
                   brands_count=len(brand_embeddings),
                   matrix_shape=similarity_matrix.shape)
        
        return similarity_matrix