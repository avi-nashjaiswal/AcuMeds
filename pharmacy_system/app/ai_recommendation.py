"""
AI Recommendation Module
Rule-based symptom-medicine recommendation system with Clinical Dosage Intelligence.

This module provides instant rule-based matching with comprehensive dosage, frequency,
timing, precautions, and multi-lingual symptom support.
"""

from app.ml_recommendation import (
    MedicineRecommendationEngine,
    CLINICAL_DOSAGE_DATABASE,
    DEFAULT_DOSAGE_GUIDE,
    EMERGENCY_SYMPTOMS,
    recommend_medicines_for_symptoms
)

__all__ = [
    'MedicineRecommendationEngine',
    'CLINICAL_DOSAGE_DATABASE',
    'DEFAULT_DOSAGE_GUIDE',
    'EMERGENCY_SYMPTOMS',
    'recommend_medicines_for_symptoms'
]
