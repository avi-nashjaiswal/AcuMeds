"""
AI Recommendation Module
Machine-learning-assisted symptom-medicine recommendation system with Clinical Dosage Intelligence.

This module combines:
1. TF-IDF + Classifier ML model for deep symptom and intent recognition
2. Comprehensive multi-lingual / Hinglish symptom vocabulary (English + Hindi/Hinglish terms)
3. Evidence-based Clinical Dosage & Safety Guidelines (Dose, Frequency, Timing, Max limits, Precautions)
4. Live Catalog & Verified Vendor stock matching
5. Red-flag / Emergency symptom detection
"""

import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion


# Master Clinical Dosage & Safety Database
CLINICAL_DOSAGE_DATABASE = {
    'paracetamol': {
        'standard_dosage': '1 Tablet (500mg - 650mg)',
        'frequency': 'Every 6 to 8 hours as needed (Max 3-4 times daily)',
        'timing': 'After food with a glass of water (खाने के बाद)',
        'max_daily_dose': 'Max 4000mg (4 to 6 tablets) in 24 hours',
        'duration': '3 to 5 days. If fever persists > 3 days, consult a physician.',
        'instructions': 'Do not take with other medicines containing paracetamol/acetaminophen. Stay well hydrated.',
        'precautions': 'Use with caution in chronic liver or kidney disease. Avoid alcohol consumption.',
        'side_effects': 'Nausea, mild allergic skin rash (rare). Safe for most adults when taken as directed.'
    },
    'ibuprofen': {
        'standard_dosage': '1 Tablet (200mg - 400mg)',
        'frequency': 'Every 6 to 8 hours after meals (Max 3 times daily)',
        'timing': 'Strictly after food or with milk (खाने के बाद)',
        'max_daily_dose': 'Max 1200mg (over-the-counter) or 2400mg under prescription in 24 hours',
        'duration': '3 to 5 days for acute pain/inflammation.',
        'instructions': 'Always take after food to prevent stomach irritation or gastric acidity.',
        'precautions': 'Avoid in active peptic ulcers, severe asthma, heart disease, or during third-trimester pregnancy.',
        'side_effects': 'Stomach upset, mild heartburn, nausea, dizziness.'
    },
    'aspirin': {
        'standard_dosage': '1 Tablet (75mg - 325mg)',
        'frequency': 'Once daily (for cardiovascular support) or every 6-8 hrs for acute pain as advised',
        'timing': 'With or after food (खाने के बाद)',
        'max_daily_dose': 'Max 3000mg in 24 hours for pain; 75-150mg daily for antiplatelet therapy',
        'duration': 'As prescribed by doctor for chronic use; max 3 days for acute pain.',
        'instructions': 'Swallow whole with plenty of water. Do not take on an empty stomach.',
        'precautions': 'Contraindicated in children/teens (risk of Reye\'s syndrome), bleeding disorders, or ulcers.',
        'side_effects': 'Gastric irritation, increased bleeding tendency, nausea.'
    },
    'cough syrup': {
        'standard_dosage': '10ml to 15ml (2 to 3 teaspoons)',
        'frequency': '2 to 3 times a day (morning, afternoon, bedtime)',
        'timing': 'After meals or before sleep (खाने के बाद / सोते समय)',
        'max_daily_dose': 'Max 30ml to 40ml in 24 hours',
        'duration': '5 to 7 days.',
        'instructions': 'Use the provided measuring cup. Avoid drinking water immediately after syrup to let it coat the throat.',
        'precautions': 'Some formulations cause drowsiness. Avoid driving or operating machinery.',
        'side_effects': 'Mild drowsiness, dry mouth, slight dizziness.'
    },
    'decongestant': {
        'standard_dosage': '1 Tablet or 2-3 nasal drops/sprays per nostril',
        'frequency': 'Every 8 to 12 hours (Max 2-3 times daily)',
        'timing': 'After meals; nasal spray as needed',
        'max_daily_dose': 'Max 240mg pseudoephedrine/day or max 3-5 consecutive days for nasal sprays',
        'duration': 'Max 3 to 5 days to prevent rebound nasal congestion (rhinitis medicamentosa).',
        'instructions': 'Drink plenty of warm fluids. Blow nose before applying nasal spray.',
        'precautions': 'Use with caution if you have high blood pressure, thyroid disorder, or glaucoma.',
        'side_effects': 'Restlessness, mild insomnia, dry nasal passages, elevated heart rate.'
    },
    'cetirizine': {
        'standard_dosage': '1 Tablet (10mg) or 5mg for mild symptoms',
        'frequency': 'Once daily, preferably at bedtime',
        'timing': 'At night after dinner (रात को सोने से पहले)',
        'max_daily_dose': 'Max 10mg in 24 hours',
        'duration': '3 to 7 days for acute allergy or seasonal flare-ups.',
        'instructions': 'Take with water at night. It provides 24-hour continuous allergy relief.',
        'precautions': 'May cause mild drowsiness. Avoid alcohol and sedatives while on this medication.',
        'side_effects': 'Drowsiness, dry mouth, mild headache, fatigue.'
    },
    'loratadine': {
        'standard_dosage': '1 Tablet (10mg)',
        'frequency': 'Once daily in the morning',
        'timing': 'With or without food (non-drowsy formulation)',
        'max_daily_dose': 'Max 10mg in 24 hours',
        'duration': '5 to 10 days for allergic rhinitis, sneezing, and skin itching.',
        'instructions': 'Ideal daytime allergy medicine as it is non-sedating.',
        'precautions': 'Dose adjustment recommended for patients with severe liver impairment.',
        'side_effects': 'Headache, dry mouth (rare), gastrointestinal comfort.'
    },
    'omeprazole': {
        'standard_dosage': '1 Capsule (20mg)',
        'frequency': 'Once daily in the morning',
        'timing': '30 to 60 minutes BEFORE breakfast on an empty stomach (खाली पेट)',
        'max_daily_dose': 'Max 40mg daily under medical supervision',
        'duration': '7 to 14 days for acidity, heartburn, or GERD symptoms.',
        'instructions': 'Swallow whole with water. Do not crush or chew the capsule.',
        'precautions': 'Do not take prolonged courses without doctor advice. Maintain healthy dietary habits.',
        'side_effects': 'Mild headache, abdominal discomfort, flatulence (rare).'
    },
    'pantoprazole': {
        'standard_dosage': '1 Tablet (40mg)',
        'frequency': 'Once daily in the morning',
        'timing': '30 minutes before first meal of the day (सुबह खाली पेट)',
        'max_daily_dose': 'Max 40mg - 80mg daily under physician guidance',
        'duration': '7 to 14 days for acid reflux and stomach ulcers.',
        'instructions': 'Swallow whole. Avoid spicy, oily, and highly acidic foods during recovery.',
        'precautions': 'Consult doctor if symptoms include severe vomiting or unexplained weight loss.',
        'side_effects': 'Mild nausea, headache, joint pain (very rare).'
    },
    'ranitidine': {
        'standard_dosage': '1 Tablet (150mg)',
        'frequency': 'Twice daily (morning and evening) or once at bedtime (300mg)',
        'timing': '30 minutes before meals or at bedtime with water',
        'max_daily_dose': 'Max 300mg in 24 hours',
        'duration': '5 to 10 days.',
        'instructions': 'Provides fast relief from heartburn and acid indigestion.',
        'precautions': 'Consult physician if you have chronic kidney disease.',
        'side_effects': 'Headache, constipation or diarrhea (mild).'
    },
    'antacid': {
        'standard_dosage': '10ml to 15ml Liquid Gel or 1-2 Chewable Tablets',
        'frequency': '1 to 2 hours after meals and at bedtime (as needed, max 4 times/day)',
        'timing': 'After meals when acidity symptoms arise',
        'max_daily_dose': 'Max 60ml liquid or 8 chewable tablets per 24 hours',
        'duration': 'As needed for immediate symptom relief (1-3 days).',
        'instructions': 'Shake suspension well before use. Chew tablets thoroughly before swallowing.',
        'precautions': 'Do not take other medicines within 2 hours of antacids as they reduce absorption.',
        'side_effects': 'Constipation (aluminum-based) or loose stools (magnesium-based).'
    },
    'vitamin c': {
        'standard_dosage': '1 Chewable Tablet (500mg)',
        'frequency': 'Once or twice daily',
        'timing': 'After breakfast or lunch (दिन में खाने के बाद)',
        'max_daily_dose': 'Max 1000mg - 2000mg daily from all sources',
        'duration': '10 to 30 days for immune recovery and antioxidant support.',
        'instructions': 'Chew thoroughly or let dissolve in mouth. Drink plenty of water throughout the day.',
        'precautions': 'High doses may cause mild stomach upset or diarrhea in sensitive individuals.',
        'side_effects': 'Mild stomach cramps or loose stools if taken in excess.'
    },
    'vitamin b complex': {
        'standard_dosage': '1 Capsule or Tablet daily',
        'frequency': 'Once daily in the morning after breakfast',
        'timing': 'After morning meal with a glass of water',
        'max_daily_dose': '1 tablet/capsule per day unless prescribed otherwise',
        'duration': '15 to 30 days for fatigue, weakness, mouth ulcers, or nerve recovery.',
        'instructions': 'Best taken in the morning because B-vitamins support cellular energy production.',
        'precautions': 'May cause harmless bright yellow urine discoloration due to Riboflavin (Vitamin B2).',
        'side_effects': 'Mild nausea if taken on empty stomach, characteristic urine color.'
    },
    'amoxicillin': {
        'standard_dosage': '1 Capsule (500mg) - PRESCRIPTION ONLY',
        'frequency': 'Every 8 hours (3 times daily) or every 12 hours',
        'timing': 'At equal intervals with or after food (खाने के बाद)',
        'max_daily_dose': 'Max 1500mg - 2000mg daily strictly under doctor supervision',
        'duration': 'Complete the full 5 to 7 days prescribed course even if feeling better.',
        'instructions': 'Do NOT stop midway to prevent antibiotic resistance. Must be prescribed by a doctor.',
        'precautions': 'Contraindicated in penicillin allergy. Report any rash or severe diarrhea immediately.',
        'side_effects': 'Diarrhea, mild nausea, stomach upset, yeast infection.'
    },
    'azithromycin': {
        'standard_dosage': '1 Tablet (500mg) - PRESCRIPTION ONLY',
        'frequency': 'Once daily for 3 to 5 days',
        'timing': '1 hour before food or 2 hours after food with water',
        'max_daily_dose': 'Max 500mg once daily',
        'duration': 'Strictly 3 to 5 days as prescribed by your doctor.',
        'instructions': 'Complete the full course. Must be prescribed by a certified physician.',
        'precautions': 'Inform doctor if you have cardiac arrhythmias or liver disease.',
        'side_effects': 'Stomach cramps, nausea, diarrhea, headache.'
    },
    'ors': {
        'standard_dosage': '1 Sachet dissolved in 1 Litre of clean drinking water',
        'frequency': 'Sip continuously throughout the day after every loose stool / vomiting episode',
        'timing': 'Anytime, drink in small frequent sips',
        'max_daily_dose': '1 to 2 Litres daily depending on fluid loss',
        'duration': '1 to 3 days until hydration and bowel movements normalize.',
        'instructions': 'Use boiled and cooled water. Discard any prepared solution remaining after 24 hours.',
        'precautions': 'Essential for preventing dehydration during loose motions and diarrhea.',
        'side_effects': 'None when prepared in proper dilution.'
    },
    'domperidone': {
        'standard_dosage': '1 Tablet (10mg)',
        'frequency': '2 to 3 times daily as needed',
        'timing': '15 to 30 minutes BEFORE meals (खाने से पहले)',
        'max_daily_dose': 'Max 30mg daily',
        'duration': '3 to 5 days for nausea and vomiting relief.',
        'instructions': 'Take before meals to promote stomach emptying and curb nausea sensation.',
        'precautions': 'Avoid in cardiac conduction disorders. Consult doctor if pregnant.',
        'side_effects': 'Dry mouth, mild headache, drowsiness.'
    },
    'diclofenac': {
        'standard_dosage': '1 Tablet (50mg) or Apply Gel 3-4 times daily locally',
        'frequency': 'Twice daily after food (Tablet) or 3-4 times daily (Gel)',
        'timing': 'Strictly after food with water (खाने के बाद) / Topical application',
        'max_daily_dose': 'Max 100mg - 150mg daily (Oral)',
        'duration': '3 to 5 days for acute muscle and joint aches.',
        'instructions': 'Wash hands after applying gel. Do not apply on broken or wounded skin.',
        'precautions': 'Avoid in patients with gastric ulcer, kidney disease, or uncontrolled hypertension.',
        'side_effects': 'Gastric burning, local redness (for gel), nausea.'
    },
    'strepsils': {
        'standard_dosage': '1 Lozenge (Throat drop)',
        'frequency': 'Dissolve 1 lozenge slowly in the mouth every 2 to 3 hours as needed',
        'timing': 'After food or whenever throat irritation occurs',
        'max_daily_dose': 'Max 8 to 12 lozenges in 24 hours',
        'duration': '3 to 5 days for sore throat and vocal strain.',
        'instructions': 'Do not chew or swallow whole; let it dissolve slowly for soothing local effect.',
        'precautions': 'Not recommended for children under 6 years due to choking hazard.',
        'side_effects': 'Temporary tongue numbness or altered taste.'
    },
}

# Generic Fallback Dosage Template
DEFAULT_DOSAGE_GUIDE = {
    'standard_dosage': '1 Tablet / 10ml as directed on packaging',
    'frequency': '2 to 3 times daily as needed',
    'timing': 'After food with a glass of water (खाने के बाद)',
    'max_daily_dose': 'Do not exceed manufacturer stated maximum daily dose',
    'duration': '3 to 5 days. Consult doctor if symptoms persist.',
    'instructions': 'Read medicine package label carefully. Stay hydrated and get adequate rest.',
    'precautions': 'Consult a licensed physician before starting any new medication, especially during pregnancy or chronic illness.',
    'side_effects': 'Mild digestive upset or drowsiness depending on individual sensitivity.'
}


# Emergency Red Flag Keywords
EMERGENCY_SYMPTOMS = {
    'chest pain': 'Severe chest pain or pressure may indicate a cardiac emergency.',
    'shortness of breath': 'Severe breathing difficulty requires immediate medical attention.',
    'breathlessness': 'Acute difficulty breathing requires urgent hospital evaluation.',
    'coughing blood': 'Blood in sputum or cough is a critical symptom requiring prompt clinical workup.',
    'blood in stool': 'Gastrointestinal bleeding requires urgent clinical care.',
    'unconscious': 'Loss of consciousness or fainting is a medical emergency.',
    'seizure': 'Seizures require immediate emergency care.',
    'paralysis': 'Sudden numbness, weakness, or face drooping may indicate a stroke.',
    'speech difficulty': 'Sudden difficulty speaking or slurred speech requires emergency care.',
    'severe burn': 'Severe burns require immediate emergency medical care.',
}


class MedicineRecommendationEngine:
    """ML-backed recommendation engine for medicine suggestions with clinical dosage intelligence."""

    # Define comprehensive symptom-medicine mappings (aligned with seeded DB names & clinical best practices)
    SYMPTOM_MEDICINE_MAP = {
        # Cold & Flu symptoms
        'cold': [
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Relieves cold-related fever, headache, and body aches'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Reduces inflammation, sore throat, and muscular discomfort'},
            {'name': 'Cough Syrup', 'category': 'Cold & Cough', 'reason': 'Soothes throat irritation and suppresses persistent coughing'},
            {'name': 'Decongestant', 'category': 'Cold & Cough', 'reason': 'Clears blocked nasal passages and sinus congestion'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Strengthens immune response and speeds up recovery'},
        ],
        'cough': [
            {'name': 'Cough Syrup', 'category': 'Cold & Cough', 'reason': 'Effective soothing agent for productive and dry cough'},
            {'name': 'Strepsils', 'category': 'Cold & Cough', 'reason': 'Provides antibacterial and soothing relief for throat irritation'},
            {'name': 'Decongestant', 'category': 'Cold & Cough', 'reason': 'Helps when cough is triggered by post-nasal drip or congestion'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Relieves accompanying chest soreness and throat pain'},
        ],
        'fever': [
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'First-line antipyretic for fast fever reduction and body ache relief'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Strong anti-inflammatory and fever reducer for high temperatures'},
            {'name': 'ORS', 'category': 'Electrolytes', 'reason': 'Prevents dehydration caused by sweating and elevated body temperature'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Supports immune defense during active fever and infection'},
        ],
        'congestion': [
            {'name': 'Decongestant', 'category': 'Cold & Cough', 'reason': 'Opens blocked nasal airways and relieves sinus pressure'},
            {'name': 'Cough Syrup', 'category': 'Cold & Cough', 'reason': 'Helps clear mucus buildup and eases breathing discomfort'},
            {'name': 'Cetirizine', 'category': 'Antihistamines', 'reason': 'Reduces allergic nasal swelling and runny discharge'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Relieves sinus-induced facial pain and headache'},
        ],
        'flu': [
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Combats flu fever, chills, and full-body aches'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Targeted relief for severe joint and muscle pains'},
            {'name': 'Cough Syrup', 'category': 'Cold & Cough', 'reason': 'Eases flu-associated coughing fits'},
            {'name': 'ORS', 'category': 'Electrolytes', 'reason': 'Replenishes vital salts lost during weakness and sweating'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Essential antioxidant support for immune recovery'},
        ],
        'throat pain': [
            {'name': 'Strepsils', 'category': 'Cold & Cough', 'reason': 'Direct topical soothing for burning and scratchy throat'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Reduces painful swallowing and throat inflammation'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Potent anti-inflammatory action on swollen throat tissues'},
            {'name': 'Cough Syrup', 'category': 'Cold & Cough', 'reason': 'Coats mucosal lining to reduce coughing friction'},
        ],

        # Pain-related symptoms
        'headache': [
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Gentle, fast-acting first-line pain reliever for tension headaches'},
            {'name': 'Aspirin', 'category': 'Painkillers', 'reason': 'Effective relief for throbbing vascular headaches'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Anti-inflammatory pain relief for persistent headache'},
        ],
        'migraine': [
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Targeted anti-inflammatory action for moderate migraine attacks'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Provides baseline analgesic support with minimal stomach distress'},
            {'name': 'Aspirin', 'category': 'Painkillers', 'reason': 'Helps alleviate vascular throbbing and sensitivity'},
        ],
        'muscle pain': [
            {'name': 'Diclofenac', 'category': 'Painkillers', 'reason': 'Topical/oral targeted action for sore muscles and sprains'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Reduces muscular inflammation, stiffness, and soreness'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'General pain relief for post-workout or strain aches'},
        ],
        'body pain': [
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Relieves widespread fatigue aches and feverish body soreness'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Effective against deep muscular and joint aches'},
            {'name': 'Vitamin B Complex', 'category': 'Vitamins', 'reason': 'Supports nerve and cellular muscle recovery'},
        ],
        'back pain': [
            {'name': 'Diclofenac', 'category': 'Painkillers', 'reason': 'Effective topical gel and oral relief for spinal muscle strain'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Reduces lumbar inflammation and stiffness'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Provides supplementary pain control'},
        ],
        'joint pain': [
            {'name': 'Diclofenac', 'category': 'Painkillers', 'reason': 'Fast-acting anti-inflammatory relief for swollen joints'},
            {'name': 'Ibuprofen', 'category': 'Painkillers', 'reason': 'Reduces stiffness and inflammatory flare-ups in joints'},
            {'name': 'Paracetamol', 'category': 'Painkillers', 'reason': 'Mild daily analgesic for chronic joint discomfort'},
        ],

        # Stomach & Digestion issues
        'stomach pain': [
            {'name': 'Omeprazole', 'category': 'Antacids', 'reason': 'Inhibits excessive gastric acid production and calms stomach lining'},
            {'name': 'Pantoprazole', 'category': 'Antacids', 'reason': 'Provides long-lasting relief from acid-induced gastric pain'},
            {'name': 'Antacid', 'category': 'Antacids', 'reason': 'Immediate neutralizing relief for burning sensation in the stomach'},
        ],
        'indigestion': [
            {'name': 'Antacid', 'category': 'Antacids', 'reason': 'Quickly neutralizes stomach acid to relieve bloating and fullness'},
            {'name': 'Omeprazole', 'category': 'Antacids', 'reason': 'Sustained relief for persistent indigestion and heavy stomach feeling'},
            {'name': 'Ranitidine', 'category': 'Antacids', 'reason': 'Reduces acid secretion to promote comfortable digestion'},
        ],
        'heartburn': [
            {'name': 'Antacid', 'category': 'Antacids', 'reason': 'Instant cooling relief for burning in the chest and food pipe'},
            {'name': 'Omeprazole', 'category': 'Antacids', 'reason': 'Heals esophageal irritation from acid reflux'},
            {'name': 'Pantoprazole', 'category': 'Antacids', 'reason': 'Long-acting acid suppression for GERD symptoms'},
        ],
        'acidity': [
            {'name': 'Antacid', 'category': 'Antacids', 'reason': 'Fast liquid/chewable acid neutralizer for immediate comfort'},
            {'name': 'Omeprazole', 'category': 'Antacids', 'reason': 'Prevents recurrent acid spikes throughout the day'},
            {'name': 'Pantoprazole', 'category': 'Antacids', 'reason': 'Proton pump inhibitor for severe gastric acidity'},
        ],
        'nausea': [
            {'name': 'Domperidone', 'category': 'Digestive', 'reason': 'Calms the vomiting center and accelerates healthy gastric emptying'},
            {'name': 'Antacid', 'category': 'Antacids', 'reason': 'Relieves nausea caused by excess acid and gastric reflux'},
            {'name': 'ORS', 'category': 'Electrolytes', 'reason': 'Maintains hydration and electrolyte balance during nausea'},
        ],
        'diarrhea': [
            {'name': 'ORS', 'category': 'Electrolytes', 'reason': 'Critical WHO-formula rehydration solution to replace lost electrolytes'},
            {'name': 'Pantoprazole', 'category': 'Antacids', 'reason': 'Protects gastrointestinal tract from hyperacidity'},
            {'name': 'Vitamin B Complex', 'category': 'Vitamins', 'reason': 'Aids gut lining repair and energy restoration'},
        ],

        # Allergy & Skin symptoms
        'allergy': [
            {'name': 'Cetirizine', 'category': 'Antihistamines', 'reason': 'Comprehensive antihistamine for itching, hives, and runny nose'},
            {'name': 'Loratadine', 'category': 'Antihistamines', 'reason': 'Non-drowsy daytime allergy and pollen reaction relief'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Natural antihistaminic antioxidant support'},
        ],
        'skin rash': [
            {'name': 'Cetirizine', 'category': 'Antihistamines', 'reason': 'Stops histamine release to calm itchy red bumps and urticaria'},
            {'name': 'Loratadine', 'category': 'Antihistamines', 'reason': 'Maintains daytime skin itch control without sedation'},
        ],

        # Weakness, Fatigue & Recovery
        'weakness': [
            {'name': 'Vitamin B Complex', 'category': 'Vitamins', 'reason': 'Replenishes essential B-vitamins for cellular energy and stamina'},
            {'name': 'ORS', 'category': 'Electrolytes', 'reason': 'Instantly restores hydration, sodium, and potassium balance'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Combats oxidative stress and enhances recovery vitality'},
        ],
        'fatigue': [
            {'name': 'Vitamin B Complex', 'category': 'Vitamins', 'reason': 'Optimizes metabolic energy production to combat lethargy'},
            {'name': 'Vitamin C', 'category': 'Vitamins', 'reason': 'Boosts physical resilience and cellular vitality'},
        ],
        'mouth ulcers': [
            {'name': 'Vitamin B Complex', 'category': 'Vitamins', 'reason': 'Addresses riboflavin and folic acid deficiency causing mouth sores'},
            {'name': 'Strepsils', 'category': 'Cold & Cough', 'reason': 'Provides mild antiseptic soothing effect in the oral cavity'},
        ],
    }

    # Comprehensive multilingual aliases (English, Hindi, Hinglish, Colloquial)
    SYMPTOM_ALIASES = {
        # Sore throat & Throat
        'sore throat': 'throat pain',
        'throat ache': 'throat pain',
        'throat infection': 'throat pain',
        'scratchy throat': 'throat pain',
        'throat irritation': 'throat pain',
        'gala kharab': 'throat pain',
        'gala dard': 'throat pain',
        'gale me dard': 'throat pain',
        'gale me kharash': 'throat pain',
        'gale me jalan': 'throat pain',

        # Cold & Congestion
        'runny nose': 'cold',
        'running nose': 'cold',
        'watery nose': 'cold',
        'sardi': 'cold',
        'jukam': 'cold',
        'zukam': 'cold',
        'nazla': 'cold',
        'blocked nose': 'congestion',
        'stuffy nose': 'congestion',
        'sinus': 'congestion',
        'sinus pressure': 'congestion',
        'nasal congestion': 'congestion',
        'band naak': 'congestion',
        'naak band': 'congestion',

        # Cough
        'dry cough': 'cough',
        'wet cough': 'cough',
        'persistent cough': 'cough',
        'chest cough': 'cough',
        'khasi': 'cough',
        'khansi': 'cough',
        'sukhi khasi': 'cough',
        'balgam': 'cough',
        'balgam wali khasi': 'cough',

        # Fever & Chills
        'feverish': 'fever',
        'high fever': 'fever',
        'high temperature': 'fever',
        'mild fever': 'fever',
        'temperature': 'fever',
        'bukhar': 'fever',
        'tez bukhar': 'fever',
        'halka bukhar': 'fever',
        'chills': 'flu',
        'shivering': 'flu',
        'thand lagna': 'flu',
        'kapkapi': 'flu',

        # Headache & Migraine
        'head pain': 'headache',
        'tension headache': 'headache',
        'sir dard': 'headache',
        'sar dard': 'headache',
        'sar me dard': 'headache',
        'matha dard': 'headache',
        'adha sirdard': 'migraine',
        'aadha sar dard': 'migraine',

        # Stomach & Digestion
        'stomach': 'stomach pain',
        'stomach ache': 'stomach pain',
        'stomachache': 'stomach pain',
        'abdominal pain': 'stomach pain',
        'belly pain': 'stomach pain',
        'tummy pain': 'stomach pain',
        'tummy ache': 'stomach pain',
        'cramps in stomach': 'stomach pain',
        'upset stomach': 'stomach pain',
        'stomach upset': 'stomach pain',
        'pet dard': 'stomach pain',
        'pet me dard': 'stomach pain',
        'pet kharab': 'stomach pain',
        'pet marod': 'stomach pain',
        'gas': 'indigestion',
        'bloating': 'indigestion',
        'gastric pain': 'indigestion',
        'flatulence': 'indigestion',
        'pet me gas': 'indigestion',
        'pet phoolna': 'indigestion',
        'bhari pet': 'indigestion',
        'acidity': 'acidity',
        'acid reflux': 'heartburn',
        'heart burn': 'heartburn',
        'chest burning': 'heartburn',
        'seene me jalan': 'heartburn',
        'khatti dakar': 'acidity',
        'jalan': 'heartburn',
        'vomiting': 'nausea',
        'nauseous': 'nausea',
        'feel like throwing up': 'nausea',
        'ulti': 'nausea',
        'ulti aana': 'nausea',
        'ji ghabrana': 'nausea',
        'loose motions': 'diarrhea',
        'loose motion': 'diarrhea',
        'loose stools': 'diarrhea',
        'watery stool': 'diarrhea',
        'dast': 'diarrhea',
        'pet chalna': 'diarrhea',

        # Pain & Aches
        'body ache': 'body pain',
        'body aches': 'body pain',
        'body hurts': 'body pain',
        'badan dard': 'body pain',
        'pure badan me dard': 'body pain',
        'muscle ache': 'muscle pain',
        'muscle soreness': 'muscle pain',
        'muscles pain': 'muscle pain',
        'kamar dard': 'back pain',
        'lower back pain': 'back pain',
        'peeth dard': 'back pain',
        'joint ache': 'joint pain',
        'knee pain': 'joint pain',
        'arthritis pain': 'joint pain',
        'jodon me dard': 'joint pain',
        'ghutne me dard': 'joint pain',

        # Allergies & Itching
        'itch': 'allergy',
        'itchy': 'allergy',
        'itching': 'allergy',
        'rash': 'skin rash',
        'rashes': 'skin rash',
        'skin allergy': 'skin rash',
        'hives': 'skin rash',
        'sneezing': 'allergy',
        'chheenk': 'allergy',
        'chheenko': 'allergy',
        'khujli': 'allergy',
        'daane': 'skin rash',

        # Weakness & Fatigue
        'tired': 'fatigue',
        'tiredness': 'fatigue',
        'tired all the time': 'fatigue',
        'exhaustion': 'fatigue',
        'sleepy': 'fatigue',
        'low energy': 'fatigue',
        'thakan': 'fatigue',
        'sust': 'fatigue',
        'susti': 'fatigue',
        'light headed': 'weakness',
        'lightheaded': 'weakness',
        'dizzy': 'weakness',
        'dizziness': 'weakness',
        'weak feeling': 'weakness',
        'kamjori': 'weakness',
        'kamzori': 'weakness',
        'chakkar': 'weakness',
        'chakkar aana': 'weakness',

        # Mouth Ulcers
        'mouth ulcer': 'mouth ulcers',
        'canker sore': 'mouth ulcers',
        'muh me chhale': 'mouth ulcers',
        'chhale': 'mouth ulcers',
    }

    # Generic phrases that are too vague to trigger a recommendation on their own
    VAGUE_PHRASES = (
        'not feeling well',
        'feeling unwell',
        'feel unwell',
        'feel sick',
        'feeling sick',
        'just unwell',
        'no specific symptom',
        'no specific symptoms',
        'nothing specific',
        'a little sick',
        'general unwellness',
        'theek nahi lag raha',
        'tabiyat theek nahi hai',
    )

    # Fix common typos before matching
    COMMON_TYPO_FIXES = {
        'stomatch': 'stomach',
        'stomache': 'stomach',
        'alergy': 'allergy',
        'headeche': 'headache',
        'feveer': 'fever',
        'feverr': 'fever',
        'dairrhea': 'diarrhea',
        'diarhea': 'diarrhea',
        'coughh': 'cough',
        'bukhar': 'bukhar',
        'chakar': 'chakkar',
        'khansi': 'khasi',
    }

    # Cached ML model state
    _feature_transformer = None
    _symptom_models = None
    _model_ready = False
    _model_version = 'tfidf-logreg-v2-clinical'
    MAX_RECOMMENDATIONS = 4

    @classmethod
    def _aliases_for_symptom(cls, symptom_key):
        """Return known aliases that map to one symptom class."""
        return sorted(
            alias for alias, canonical in cls.SYMPTOM_ALIASES.items()
            if canonical == symptom_key
        )

    @classmethod
    def _build_training_phrases(cls, symptom_key):
        """Create rich synthetic training data for one symptom label."""
        seed_phrases = [symptom_key] + cls._aliases_for_symptom(symptom_key)
        templates = [
            '{phrase}',
            'i have {phrase}',
            'i have a {phrase}',
            'i am having {phrase}',
            'i am feeling {phrase}',
            'i have been having {phrase}',
            'having {phrase}',
            'suffering from {phrase}',
            'i am suffering from {phrase}',
            'experiencing {phrase}',
            'i am experiencing {phrase}',
            'feeling {phrase}',
            'feeling very {phrase}',
            'with {phrase}',
            'my symptoms are {phrase}',
            'my main symptom is {phrase}',
            'severe {phrase}',
            'mild {phrase}',
            'strong {phrase}',
            'symptoms of {phrase}',
            'signs of {phrase}',
            'possible {phrase}',
            'possible signs of {phrase}',
            'bad {phrase}',
            'persistent {phrase}',
            'ongoing {phrase}',
            '{phrase} for 3 days',
            '{phrase} since yesterday',
            '{phrase} since last night',
            'doctor said {phrase}',
            'sudden {phrase}',
            'mujhe {phrase} hai',
            'bahut {phrase} ho raha hai',
            '{phrase} ki dawai',
        ]

        phrases = set()
        for phrase in seed_phrases:
            normalized_phrase = cls._normalize_text(phrase)
            if not normalized_phrase:
                continue

            phrases.add(normalized_phrase)
            for template in templates:
                phrases.add(cls._normalize_text(template.format(phrase=normalized_phrase)))

        return sorted(phrases)

    @classmethod
    def _build_training_dataset(cls):
        """Create training rows from symptom phrases and aliases."""
        texts = []
        labels = []

        for symptom_key in cls.SYMPTOM_MEDICINE_MAP.keys():
            for phrase in cls._build_training_phrases(symptom_key):
                texts.append(phrase)
                labels.append(symptom_key)

        return texts, labels

    @classmethod
    def _ensure_model(cls):
        """Train the ML model once and keep it cached in memory."""
        if cls._model_ready and cls._feature_transformer is not None and cls._symptom_models:
            return

        training_texts, training_labels = cls._build_training_dataset()
        cls._feature_transformer = FeatureUnion([
            (
                'word',
                TfidfVectorizer(
                    analyzer='word',
                    ngram_range=(1, 2),
                    lowercase=False,
                    min_df=1,
                ),
            ),
            (
                'char',
                TfidfVectorizer(
                    analyzer='char_wb',
                    ngram_range=(3, 5),
                    lowercase=False,
                    min_df=1,
                ),
            ),
        ])

        features = cls._feature_transformer.fit_transform(training_texts)
        cls._symptom_models = {}

        for symptom_key in cls.SYMPTOM_MEDICINE_MAP.keys():
            y = [1 if label == symptom_key else 0 for label in training_labels]
            model = LogisticRegression(
                max_iter=2500,
                class_weight='balanced',
                solver='liblinear',
            )
            model.fit(features, y)
            cls._symptom_models[symptom_key] = model

        cls._model_ready = True

    @classmethod
    def _predict_symptom_scores(cls, symptoms_text):
        """Return symptom probabilities from the trained ML model."""
        cls._ensure_model()

        normalized_text = cls._normalize_text(symptoms_text)
        if not normalized_text:
            return []

        features = cls._feature_transformer.transform([normalized_text])
        symptom_scores = []

        for symptom_key, model in cls._symptom_models.items():
            try:
                probability = float(model.predict_proba(features)[0][1])
            except Exception:
                probability = 0.0
            symptom_scores.append((symptom_key, probability))

        symptom_scores.sort(key=lambda item: (-item[1], item[0]))
        return symptom_scores

    @staticmethod
    def _select_symptoms(symptom_scores, max_selected=4):
        """Select the most likely symptoms from model scores."""
        if not symptom_scores:
            return []

        top_probability = symptom_scores[0][1]
        if top_probability < 0.25:
            return []

        threshold = max(0.20, top_probability - 0.25)
        selected = [item for item in symptom_scores if item[1] >= threshold]
        if not selected:
            selected = symptom_scores[:1]

        return selected[:max_selected]

    @classmethod
    def _extract_supported_symptoms(cls, symptoms_text):
        """Return the supported symptom labels explicitly mentioned in the text."""
        normalized_text = cls._normalize_text(symptoms_text)
        supported_symptoms = []
        seen = set()

        for symptom_key in list(cls.SYMPTOM_MEDICINE_MAP.keys()) + list(cls.SYMPTOM_ALIASES.keys()):
            if not cls._has_phrase(normalized_text, symptom_key):
                continue

            canonical_key = cls.SYMPTOM_ALIASES.get(symptom_key, symptom_key)
            if canonical_key in seen:
                continue

            seen.add(canonical_key)
            supported_symptoms.append(canonical_key)

        return supported_symptoms

    @classmethod
    def _detect_emergency(cls, symptoms_text):
        """Check for critical/red-flag emergency keywords in symptoms text."""
        normalized_text = cls._normalize_text(symptoms_text)
        matched_emergencies = []
        for keyword, warning_msg in EMERGENCY_SYMPTOMS.items():
            if cls._has_phrase(normalized_text, keyword):
                matched_emergencies.append({
                    'keyword': keyword,
                    'warning': warning_msg
                })
        return matched_emergencies

    @classmethod
    def _has_explicit_symptom_hint(cls, symptoms_text):
        """Check whether the text contains an explicit symptom keyword or alias."""
        return bool(cls._extract_supported_symptoms(symptoms_text))

    @classmethod
    def _is_vague_symptom_text(cls, symptoms_text):
        """Detect symptom descriptions that are too vague to recommend medicine safely."""
        normalized_text = cls._normalize_text(symptoms_text)
        return any(phrase in normalized_text for phrase in cls.VAGUE_PHRASES)

    @classmethod
    def get_dosage_guide(cls, medicine_name):
        """Retrieve accurate clinical dosage and safety details for a medicine name."""
        name_clean = (medicine_name or '').lower().strip()
        
        # Look for exact or substring matches in CLINICAL_DOSAGE_DATABASE
        for key, guide in CLINICAL_DOSAGE_DATABASE.items():
            if key in name_clean or name_clean in key:
                return dict(guide)

        # Look for category-based matches
        if 'pain' in name_clean or 'paracetamol' in name_clean:
            return dict(CLINICAL_DOSAGE_DATABASE['paracetamol'])
        if 'cough' in name_clean or 'syrup' in name_clean:
            return dict(CLINICAL_DOSAGE_DATABASE['cough syrup'])
        if 'vitamin' in name_clean:
            return dict(CLINICAL_DOSAGE_DATABASE['vitamin c'])
        if 'antacid' in name_clean or 'acid' in name_clean:
            return dict(CLINICAL_DOSAGE_DATABASE['antacid'])

        return dict(DEFAULT_DOSAGE_GUIDE)

    @staticmethod
    def _normalize_catalog_medicine(medicine):
        """Normalize ORM objects or dicts into a common catalog record."""
        if isinstance(medicine, dict):
            name = medicine.get('name') or ''
            category = medicine.get('category') or ''
            description = medicine.get('description') or ''
            usage_instructions = medicine.get('usage_instructions') or ''
            side_effects = medicine.get('side_effects') or ''
            price = medicine.get('price')
            stock_quantity = medicine.get('stock_quantity') or 0
            requires_prescription = bool(medicine.get('requires_prescription', False))
            verified = bool(medicine.get('verified') or medicine.get('shopkeeper_verified'))
            medicine_id = medicine.get('id')
            shopkeeper_id = medicine.get('shopkeeper_id')
        else:
            name = getattr(medicine, 'name', '') or ''
            category = getattr(medicine, 'category', '') or ''
            description = getattr(medicine, 'description', '') or ''
            usage_instructions = getattr(medicine, 'usage_instructions', '') or ''
            side_effects = getattr(medicine, 'side_effects', '') or ''
            price = getattr(medicine, 'price', None)
            stock_quantity = getattr(medicine, 'stock_quantity', 0) or 0
            requires_prescription = bool(getattr(medicine, 'requires_prescription', False))
            shopkeeper = getattr(medicine, 'shopkeeper', None)
            verified = bool(getattr(shopkeeper, 'verified', False))
            medicine_id = getattr(medicine, 'id', None)
            shopkeeper_id = getattr(medicine, 'shopkeeper_id', None)

        search_text = MedicineRecommendationEngine._normalize_text(
            ' '.join(part for part in [
                name,
                category,
                description,
                usage_instructions,
                side_effects,
            ] if part)
        )

        try:
            price_value = float(price) if price is not None else None
        except (TypeError, ValueError):
            price_value = None

        try:
            stock_value = int(stock_quantity or 0)
        except (TypeError, ValueError):
            stock_value = 0

        return {
            'id': medicine_id,
            'name': name,
            'category': category,
            'description': description,
            'usage_instructions': usage_instructions,
            'side_effects': side_effects,
            'price': price_value,
            'stock_quantity': stock_value,
            'requires_prescription': requires_prescription,
            'verified': verified,
            'shopkeeper_id': shopkeeper_id,
            'search_text': search_text,
        }

    @staticmethod
    def _get_symptom_hints(symptom_key):
        """Return preferred medicine names and categories for a symptom."""
        preferred_medicines = MedicineRecommendationEngine.SYMPTOM_MEDICINE_MAP.get(symptom_key, [])
        preferred_names = []
        preferred_categories = []

        for medicine in preferred_medicines:
            medicine_name = (medicine.get('name') or '').strip()
            medicine_category = (medicine.get('category') or '').strip()

            if medicine_name and medicine_name.lower() not in [name.lower() for name in preferred_names]:
                preferred_names.append(medicine_name)

            if medicine_category and medicine_category.lower() not in [category.lower() for category in preferred_categories]:
                preferred_categories.append(medicine_category)

        return preferred_names, preferred_categories

    @classmethod
    def _score_catalog_medicine(cls, medicine, symptom_scores):
        """Score a catalog medicine against ML symptom probabilities."""
        name_text = MedicineRecommendationEngine._normalize_text(medicine['name'] or '')
        category_text = MedicineRecommendationEngine._normalize_text(medicine['category'] or '')
        search_text = medicine['search_text']

        signal_score = 0.0
        reasons = []
        matched_symptoms = set()

        for symptom_key, symptom_probability in symptom_scores.items():
            if symptom_probability <= 0:
                continue

            preferred_names, preferred_categories = cls._get_symptom_hints(symptom_key)
            matched = False

            for preferred_name in preferred_names:
                preferred_text = cls._normalize_text(preferred_name)
                if preferred_text and (
                    cls._has_phrase(name_text, preferred_text)
                    or cls._has_phrase(search_text, preferred_text)
                ):
                    signal_score += symptom_probability * 8
                    reasons.append(
                        f"Targeted for {symptom_key.title()} (Match {round(symptom_probability * 100)}%): {medicine['name']}"
                    )
                    matched_symptoms.add(symptom_key)
                    matched = True
                    break

            if matched:
                continue

            for preferred_category in preferred_categories:
                preferred_text = cls._normalize_text(preferred_category)
                if preferred_text and (
                    cls._has_phrase(category_text, preferred_text)
                    or cls._has_phrase(search_text, preferred_text)
                ):
                    signal_score += symptom_probability * 4
                    reasons.append(
                        f"Fits {symptom_key.title()} category: {medicine['category']}"
                    )
                    matched_symptoms.add(symptom_key)
                    matched = True
                    break

            if not matched and cls._has_phrase(search_text, symptom_key):
                signal_score += symptom_probability * 2
                reasons.append(f"Indicated for {symptom_key.title()} in medicine catalog details")
                matched_symptoms.add(symptom_key)

        if signal_score <= 0:
            return 0, [], set()

        score = signal_score

        if medicine['stock_quantity'] > 0:
            score += 2
            reasons.append('In stock and ready to dispatch')
        else:
            score -= 2
            reasons.append('Currently out of stock')

        if not medicine['requires_prescription']:
            score += 1
            reasons.append('Over-the-Counter (No prescription required)')

        if medicine['verified']:
            score += 1
            reasons.append('Verified pharmacy inventory')

        return score, reasons, matched_symptoms

    @classmethod
    def _recommend_from_catalog(cls, symptom_scores, medicine_catalog):
        """Build recommendations from the live medicine catalog with clinical dosage attachment."""
        matched_medicines = {}

        for medicine in medicine_catalog or []:
            catalog_medicine = cls._normalize_catalog_medicine(medicine)
            score, reasons, matched_symptoms = cls._score_catalog_medicine(catalog_medicine, symptom_scores)
            if score <= 0:
                continue

            medicine_key = catalog_medicine['id'] if catalog_medicine['id'] is not None else f"{catalog_medicine['name'].lower()}::{catalog_medicine['category'].lower()}"
            if medicine_key not in matched_medicines:
                dosage_guide = cls.get_dosage_guide(catalog_medicine['name'])
                
                # If the DB has custom usage_instructions, incorporate them into the dosage guide
                if catalog_medicine.get('usage_instructions'):
                    dosage_guide['instructions'] = catalog_medicine['usage_instructions']
                if catalog_medicine.get('side_effects'):
                    dosage_guide['side_effects'] = catalog_medicine['side_effects']

                matched_medicines[medicine_key] = {
                    'medicine_id': catalog_medicine['id'],
                    'name': catalog_medicine['name'],
                    'category': catalog_medicine['category'],
                    'price': catalog_medicine['price'],
                    'stock_quantity': catalog_medicine['stock_quantity'],
                    'requires_prescription': catalog_medicine['requires_prescription'],
                    'dosage_guide': dosage_guide,
                    'dosage': dosage_guide.get('standard_dosage'),
                    'dosage_frequency': dosage_guide.get('frequency'),
                    'dosage_timing': dosage_guide.get('timing'),
                    'reasons': [],
                    'match_count': 0,
                    'matched_symptoms': set(),
                    'score': 0.0,
                }

            entry = matched_medicines[medicine_key]
            entry['score'] += score
            entry['matched_symptoms'].update(matched_symptoms)
            entry['match_count'] = len(entry['matched_symptoms'])
            entry['reasons'] = list(dict.fromkeys(entry['reasons'] + reasons))

        sorted_recommendations = sorted(
            matched_medicines.values(),
            key=lambda item: (
                -item['score'],
                -item['match_count'],
                -(item['stock_quantity'] or 0),
                item['price'] if item['price'] is not None else float('inf'),
                item['name'].lower(),
            )
        )

        return cls._finalize_recommendations(sorted_recommendations)

    @classmethod
    def _recommend_from_model(cls, symptom_scores):
        """Build recommendations from the ML symptom predictions with full clinical dosage metadata."""
        matched_medicines = {}

        for symptom_key, symptom_probability in symptom_scores.items():
            medicine_list = cls.SYMPTOM_MEDICINE_MAP.get(symptom_key, [])
            for medicine in medicine_list:
                med_name = medicine['name']

                if med_name not in matched_medicines:
                    dosage_guide = cls.get_dosage_guide(med_name)
                    matched_medicines[med_name] = {
                        'medicine_id': None,
                        'name': medicine['name'],
                        'category': medicine['category'],
                        'price': None,
                        'stock_quantity': 0,
                        'requires_prescription': False,
                        'dosage_guide': dosage_guide,
                        'dosage': dosage_guide.get('standard_dosage'),
                        'dosage_frequency': dosage_guide.get('frequency'),
                        'dosage_timing': dosage_guide.get('timing'),
                        'reasons': [],
                        'match_count': 0,
                        'matched_symptoms': set(),
                        'score': 0.0,
                    }

                entry = matched_medicines[med_name]
                entry['score'] += symptom_probability * 10
                entry['matched_symptoms'].add(symptom_key)
                entry['match_count'] = len(entry['matched_symptoms'])
                entry['reasons'] = list(dict.fromkeys(entry['reasons'] + [
                    f"AI Match for {symptom_key.title()} ({round(symptom_probability * 100)}%)",
                    medicine['reason'],
                ]))

        sorted_recommendations = sorted(
            matched_medicines.values(),
            key=lambda item: (
                -item['score'],
                -item['match_count'],
                item['name'].lower(),
            )
        )

        return cls._finalize_recommendations(sorted_recommendations)

    @classmethod
    def _finalize_recommendations(cls, sorted_recommendations, limit=None):
        """Trim recommendations, attach per-medicine confidence scores and dosage details."""
        if not sorted_recommendations:
            return []

        limit = max(1, limit or cls.MAX_RECOMMENDATIONS)
        limited_recommendations = []
        top_score = max(float(item.get('score') or 0.0) for item in sorted_recommendations[:limit])
        previous_confidence = None

        for index, item in enumerate(sorted_recommendations[:limit]):
            recommendation = dict(item)
            matched_symptoms = recommendation.pop('matched_symptoms', set())
            score = float(recommendation.pop('score', 0.0) or 0.0)

            confidence = 0
            if top_score > 0 and score > 0:
                confidence = int(round((score / top_score) * 100))
                confidence = max(1, min(confidence, 100))

                if index == 0:
                    confidence = 100
                elif previous_confidence is not None and confidence >= previous_confidence:
                    confidence = max(previous_confidence - 1, 1)

            recommendation['confidence'] = confidence
            recommendation['symptoms_matched'] = sorted(matched_symptoms)
            
            # Ensure dosage_guide is present
            if 'dosage_guide' not in recommendation or not recommendation['dosage_guide']:
                recommendation['dosage_guide'] = cls.get_dosage_guide(recommendation.get('name'))
                recommendation['dosage'] = recommendation['dosage_guide'].get('standard_dosage')
                recommendation['dosage_frequency'] = recommendation['dosage_guide'].get('frequency')
                recommendation['dosage_timing'] = recommendation['dosage_guide'].get('timing')

            limited_recommendations.append(recommendation)
            previous_confidence = confidence

        return limited_recommendations

    @staticmethod
    def _normalize_text(text):
        """Normalize input text for reliable matching"""
        normalized = (text or '').lower()
        for typo, correct in MedicineRecommendationEngine.COMMON_TYPO_FIXES.items():
            normalized = normalized.replace(typo, correct)
        normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    @staticmethod
    def _has_phrase(text, phrase):
        """Check if a keyword/phrase exists as a whole word match"""
        if not phrase:
            return False
        pattern = r'\b' + re.escape(phrase) + r'\b'
        return re.search(pattern, text) is not None

    @classmethod
    def get_recommendations(cls, symptoms_text, medicine_catalog=None, age_group=None):
        """
        Get comprehensive medicine recommendations with clinical dosage guidance.

        Args:
            symptoms_text (str): User-entered symptoms as text
            medicine_catalog (list, optional): Database medicine objects
            age_group (str, optional): 'adult', 'child', 'senior'

        Returns:
            dict: Recommendations list with dosage guides, matched symptoms, confidence, and safety alerts.
        """

        if not symptoms_text or len(symptoms_text.strip()) == 0:
            return {
                'recommendations': [],
                'symptoms_matched': [],
                'confidence': 0,
                'emergency_alerts': [],
                'message': 'Please describe your symptoms to receive AI medicine and dosage recommendations.'
            }

        normalized_text = cls._normalize_text(symptoms_text)
        emergency_alerts = cls._detect_emergency(normalized_text)
        explicit_symptoms = cls._extract_supported_symptoms(normalized_text)

        if cls._is_vague_symptom_text(normalized_text) and not explicit_symptoms:
            return {
                'recommendations': [],
                'symptoms_matched': [],
                'confidence': 0,
                'emergency_alerts': emergency_alerts,
                'message': 'Please describe specific symptoms (e.g. fever, cough, acidity, headache, body pain) for accurate medicine & dosage advice.'
            }

        symptom_scores = cls._predict_symptom_scores(normalized_text)
        if explicit_symptoms:
            symptom_score_map = {
                symptom_key: max(probability, 0.85)
                for symptom_key, probability in symptom_scores
                if symptom_key in explicit_symptoms
            }
            # Add any explicitly mentioned symptoms that might have low model probability
            for sym in explicit_symptoms:
                if sym not in symptom_score_map:
                    symptom_score_map[sym] = 0.90
        else:
            selected_symptoms = cls._select_symptoms(symptom_scores)
            symptom_score_map = {
                symptom_key: probability
                for symptom_key, probability in selected_symptoms
            }

        if not symptom_score_map:
            return {
                'recommendations': [],
                'symptoms_matched': [],
                'confidence': 0,
                'emergency_alerts': emergency_alerts,
                'message': 'No matching medicines found for the described symptoms. Please consult a doctor.'
            }

        selected_symptoms = sorted(
            symptom_score_map.items(),
            key=lambda item: (-item[1], item[0])
        )[:4]

        catalog_recommendations = []
        if medicine_catalog:
            catalog_recommendations = cls._recommend_from_catalog(symptom_score_map, medicine_catalog)

        if catalog_recommendations:
            recommendations = catalog_recommendations
        else:
            recommendations = cls._recommend_from_model(symptom_score_map)

        # Adjust dosage advisory notes if child or senior age group specified
        if age_group == 'child':
            for rec in recommendations:
                rec['age_warning'] = 'Pediatric Warning: Dosage for children should be calculated by body weight (mg/kg). Consult a pediatrician.'
        elif age_group == 'senior':
            for rec in recommendations:
                rec['age_warning'] = 'Senior Citizen Advice: Start with lowest effective dose. Monitor kidney/liver parameters.'

        confidence = round(
            sum(probability for _, probability in selected_symptoms) / len(selected_symptoms) * 100,
            1,
        )
        confidence = min(max(confidence, 40.0), 98.0) if recommendations else 0.0

        response = {
            'recommendations': recommendations,
            'symptoms_matched': sorted(symptom_score_map.keys()),
            'confidence': confidence,
            'emergency_alerts': emergency_alerts,
            'message': (
                f'Found {len(recommendations)} clinically recommended medicine(s) with dosage guidelines matching your symptoms.'
                if recommendations else 'No matching medicines found.'
            )
        }

        return response

    @staticmethod
    def get_all_symptom_keywords():
        """Return the canonical symptom keywords shown in the UI."""
        return sorted(MedicineRecommendationEngine.SYMPTOM_MEDICINE_MAP.keys())


def recommend_medicines_for_symptoms(symptoms, medicine_catalog=None, age_group=None):
    """
    Standalone function to get recommendations with complete clinical dosage details.

    Args:
        symptoms (str): Symptoms described by user
        medicine_catalog (list, optional): Medicine database records
        age_group (str, optional): 'adult', 'child', 'senior'

    Returns:
        dict: Recommendation results including dosage, timing, precautions, and confidence.
    """
    engine = MedicineRecommendationEngine()
    return engine.get_recommendations(symptoms, medicine_catalog=medicine_catalog, age_group=age_group)
