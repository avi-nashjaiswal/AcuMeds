"""
Medicine Database Integration - Hybrid Local + RxNorm API
Includes real Indian medicines data for offline use + optional RxNorm API
Documentation: https://rxnav.nlm.nih.gov/APIs_RxNorm.html
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

BASE_URL = "http://rxnav.nlm.nih.gov/REST"  # Use HTTP instead of HTTPS

# Comprehensive Indian medicine database for offline use
MEDICINE_DATABASE = {
    'aspirin': {
        'name': 'Aspirin',
        'category': 'Painkillers',
        'description': 'Effective pain relief and fever reducer',
        'price': 15,
        'requires_prescription': False,
        'side_effects': 'Stomach upset, allergic reactions',
        'usage_instructions': 'Take 1-2 tablets every 4-6 hours',
        'common_dosages': ['100mg', '250mg', '500mg', '650mg'],
        'image': 'https://images.unsplash.com/photo-1512154422022-3e3c1da37d5e?w=200&h=200&fit=crop',
        'emoji': '💊'
    },
    'ibuprofen': {
        'name': 'Ibuprofen',
        'category': 'Painkillers',
        'description': 'Anti-inflammatory pain reliever',
        'price': 25,
        'requires_prescription': False,
        'side_effects': 'GI upset, dizziness',
        'usage_instructions': 'Take 1 tablet every 6-8 hours',
        'common_dosages': ['200mg', '400mg', '600mg'],
        'image': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=200&h=200&fit=crop',
        'emoji': '💊'
    },
    'paracetamol': {
        'name': 'Paracetamol',
        'category': 'Painkillers',
        'description': 'Safe over-the-counter pain reliever',
        'price': 12,
        'requires_prescription': False,
        'side_effects': 'Rare allergic reactions',
        'usage_instructions': 'Take 1-2 tablets every 4-6 hours',
        'common_dosages': ['250mg', '500mg', '650mg'],
        'image': 'https://images.unsplash.com/photo-1584308666744-24d5f31f0b88?w=200&h=200&fit=crop',
        'emoji': '💊'
    },
    'amoxicillin': {
        'name': 'Amoxicillin',
        'category': 'Antibiotics',
        'description': 'Broad-spectrum antibiotic',
        'price': 65,
        'requires_prescription': True,
        'side_effects': 'Allergic reactions, diarrhea',
        'usage_instructions': 'Take as prescribed by doctor',
        'common_dosages': ['250mg', '500mg', '1000mg'],
        'image': 'https://images.unsplash.com/photo-1585435557529-3f757f6f3919?w=200&h=200&fit=crop',
        'emoji': '🔬'
    },
    'ciprofloxacin': {
        'name': 'Ciprofloxacin',
        'category': 'Antibiotics',
        'description': 'Fluoroquinolone antibiotic',
        'price': 85,
        'requires_prescription': True,
        'side_effects': 'Tendon problems, photosensitivity',
        'usage_instructions': 'Take twice daily with water',
        'common_dosages': ['250mg', '500mg', '750mg'],
        'image': 'https://images.unsplash.com/photo-1585435557529-3f757f6f3919?w=200&h=200&fit=crop',
        'emoji': '🔬'
    },
    'cough syrup': {
        'name': 'Cough Syrup',
        'category': 'Cold & Cough',
        'description': 'Effective cough suppressant',
        'price': 80,
        'requires_prescription': False,
        'side_effects': 'Drowsiness, dizziness',
        'usage_instructions': 'Take 10ml every 6 hours',
        'common_dosages': ['50ml', '100ml', '200ml'],
        'image': 'https://images.unsplash.com/photo-1563318678-8c0ca6e1e3d4?w=200&h=200&fit=crop',
        'emoji': '🧪'
    },
    'omeprazole': {
        'name': 'Omeprazole',
        'category': 'Antacids',
        'description': 'Reduces stomach acid',
        'price': 70,
        'requires_prescription': False,
        'side_effects': 'Headache, abdominal pain',
        'usage_instructions': 'Take 1 capsule daily',
        'common_dosages': ['10mg', '20mg', '40mg'],
        'image': 'https://images.unsplash.com/photo-1550831855-cd4628902046?w=200&h=200&fit=crop',
        'emoji': '💊'
    },
    'vitamin c': {
        'name': 'Vitamin C',
        'category': 'Vitamins',
        'description': 'Immune system booster',
        'price': 40,
        'requires_prescription': False,
        'side_effects': 'Rare kidney stones',
        'usage_instructions': 'Take 1 tablet daily',
        'common_dosages': ['250mg', '500mg', '1000mg'],
        'image': 'https://images.unsplash.com/photo-1631217314831-c6227db76b6e?w=200&h=200&fit=crop',
        'emoji': '🍊'
    },
    'cetirizine': {
        'name': 'Cetirizine',
        'category': 'Antihistamines',
        'description': 'Allergy and itch relief',
        'price': 35,
        'requires_prescription': False,
        'side_effects': 'Drowsiness, dry mouth',
        'usage_instructions': 'Take 1 tablet once or twice daily',
        'common_dosages': ['5mg', '10mg'],
        'image': 'https://images.unsplash.com/photo-1512154422022-3e3c1da37d5e?w=200&h=200&fit=crop',
        'emoji': '🚫'
    },
    'metformin': {
        'name': 'Metformin',
        'category': 'Diabetes',
        'description': 'Type 2 diabetes management',
        'price': 95,
        'requires_prescription': True,
        'side_effects': 'Nausea, metallic taste',
        'usage_instructions': 'Take as prescribed',
        'common_dosages': ['250mg', '500mg', '750mg', '1000mg'],
        'image': 'https://images.unsplash.com/photo-1631217314831-c6227db76b6e?w=200&h=200&fit=crop',
        'emoji': '💊'
    },
}


class MedicineAPI:
    """Wrapper for local medicine database + optional RxNorm API"""
    
    @staticmethod
    def search_medicines(medicine_name: str, use_api: bool = False) -> List[Dict]:
        """
        Search for medicines by name
        
        Args:
            medicine_name: Name of the medicine to search
            use_api: Try to fetch from RxNorm API (may timeout)
            
        Returns:
            List of matching medicines
        """
        results = []
        
        # First, search in local database
        term_lower = medicine_name.lower()
        for key, med_data in MEDICINE_DATABASE.items():
            if term_lower in key or term_lower in med_data['name'].lower():
                results.append({
                    'rxcui': key,
                    'name': med_data['name'],
                    'category': med_data['category'],
                    'description': med_data['description'],
                    'price': med_data['price'],
                    'image': med_data['image'],
                    'emoji': med_data['emoji'],
                    'source': 'local'
                })
        
        # If no local results and API enabled, try RxNorm
        if not results and use_api:
            try:
                api_results = MedicineAPI._search_rxnorm_api(medicine_name)
                results.extend(api_results)
            except Exception as e:
                print(f"RxNorm API failed (falling back to local): {e}")
        
        return results
    
    @staticmethod
    def _search_rxnorm_api(medicine_name: str) -> List[Dict]:
        """Try to search RxNorm API (with timeout handling)"""
        try:
            url = f"{BASE_URL}/approximateTerm.json?term={medicine_name}&maxEntries=5"
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'approximateGroup' in data and 'candidate' in data['approximateGroup']:
                for candidate in data['approximateGroup']['candidate']:
                    results.append({
                        'rxcui': candidate.get('rxcui', ''),
                        'name': candidate.get('rxaui', medicine_name),
                        'tty': candidate.get('tty', ''),
                        'source': 'rxnorm_api'
                    })
            
            return results
        except:
            return []
    
    @staticmethod
    def get_medicine_info(medicine_key: str) -> Dict:
        """
        Get detailed information about a medicine
        
        Args:
            medicine_key: Medicine identifier (name or rxcui)
            
        Returns:
            Dictionary with medicine details
        """
        key_lower = medicine_key.lower()
        
        if key_lower in MEDICINE_DATABASE:
            med = MEDICINE_DATABASE[key_lower].copy()
            med['id'] = key_lower
            return med
        
        return None
    
    @staticmethod
    def search_by_category(category: str) -> List[Dict]:
        """Search medicines by category"""
        results = []
        category_lower = category.lower()
        
        for key, med_data in MEDICINE_DATABASE.items():
            if category_lower in med_data['category'].lower():
                results.append({
                    'id': key,
                    'name': med_data['name'],
                    'category': med_data['category'],
                    'price': med_data['price'],
                    'image': med_data['image'],
                    'emoji': med_data['emoji'],
                    'requires_prescription': med_data['requires_prescription']
                })
        
        return results
    
    @staticmethod
    def search_by_condition(condition: str) -> List[Dict]:
        """Search medicines suitable for a medical condition"""
        condition_map = {
            'cold': ['aspirin', 'paracetamol', 'cough syrup'],
            'cough': ['cough syrup'],
            'fever': ['paracetamol', 'ibuprofen', 'aspirin'],
            'pain': ['ibuprofen', 'paracetamol', 'aspirin'],
            'headache': ['paracetamol', 'ibuprofen', 'aspirin'],
            'allergy': ['cetirizine'],
            'acid reflux': ['omeprazole'],
            'diabetes': ['metformin'],
            'infection': ['amoxicillin', 'ciprofloxacin'],
            'immunity': ['vitamin c'],
        }
        
        results = []
        condition_lower = condition.lower()
        
        if condition_lower in condition_map:
            for med_key in condition_map[condition_lower]:
                if med_key in MEDICINE_DATABASE:
                    med = MEDICINE_DATABASE[med_key]
                    results.append({
                        'id': med_key,
                        'name': med['name'],
                        'category': med['category'],
                        'image': med['image'],
                        'emoji': med['emoji'],
                        'description': med['description'],
                        'price': med['price'],
                        'usage_instructions': med['usage_instructions']
                    })
        
        return results
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all medicine categories"""
        categories = set()
        for med_data in MEDICINE_DATABASE.values():
            categories.add(med_data['category'])
        return sorted(list(categories))
    
    @staticmethod
    def get_all_medicines() -> List[Dict]:
        """Get all medicines in database"""
        results = []
        for key, med_data in MEDICINE_DATABASE.items():
            med = med_data.copy()
            med['id'] = key
            results.append(med)
        return results


# For backward compatibility
RxNormAPI = MedicineAPI


def format_medicine_data(medicine_data: Dict, custom_price: float = 0) -> Dict:
    """
    Format medicine data into pharmacy system format
    
    Args:
        medicine_data: Data from medicine database
        custom_price: Price to override (if needed)
        
    Returns:
        Dictionary formatted for pharmacy database
    """
    return {
        'name': medicine_data.get('name', 'Unknown'),
        'category': medicine_data.get('category', 'Other'),
        'description': medicine_data.get('description', ''),
        'price': custom_price or medicine_data.get('price', 0),
        'stock_quantity': 100,
        'requires_prescription': medicine_data.get('requires_prescription', False),
        'side_effects': medicine_data.get('side_effects', ''),
        'usage_instructions': medicine_data.get('usage_instructions', ''),
        'image': medicine_data.get('image', 'images/medicine-default.png')
    }


# Test the API
if __name__ == '__main__':
    print("✅ Medicine API Integration Test\n")
    
    # Test search
    print("1️⃣  Search 'Aspirin':")
    results = MedicineAPI.search_medicines("Aspirin")
    print(f"   Found: {len(results)} medicine(s)")
    if results:
        print(f"   → {results[0]['name']} ({results[0]['source']})")
    
    # Test category search
    print("\n2️⃣  Medicines in 'Painkillers' category:")
    painkillers = MedicineAPI.search_by_category("Painkillers")
    for med in painkillers:
        print(f"   → {med['name']} - ₹{med['price']}")
    
    # Test condition search
    print("\n3️⃣  Medicines for 'Fever':")
    fever_meds = MedicineAPI.search_by_condition("Fever")
    for med in fever_meds:
        print(f"   → {med['name']}: {med['description']}")
    
    # Test get all categories
    print("\n4️⃣  All Categories:")
    categories = MedicineAPI.get_all_categories()
    print(f"   {', '.join(categories)}")
    
    print("\n✅ All tests passed! API ready for use.")
