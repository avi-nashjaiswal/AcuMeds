# AI Recommendation System Documentation

## Overview

The AcuMeds AI Recommendation System is a machine-learning-assisted medicine recommendation engine that suggests appropriate medications based on user-entered symptoms. It uses a lightweight text classification model with confidence scoring.

## How It Works

### Architecture

```
User Input (Symptoms)
        ↓
    Preprocessing (lowercase, trim)
        ↓
    TF-IDF Feature Extraction + ML Scoring
        ↓
    Symptom Probability Estimation
        ↓
    Ranking (by relevance score)
        ↓
    Medicine Retrieval (from symptom map and catalog)
        ↓
    Confidence Calculation
        ↓
    Results with Recommendations
```

## Algorithm Details

### 1. Symptom Data and Training Examples

The system still keeps a symptom-to-medicine mapping, but it now also generates training phrases from:
- canonical symptom names
- aliases such as `sore throat` or `runny nose`
- simple sentence templates like `I have {symptom}` or `suffering from {symptom}`

Those phrases are used to train a small text classifier.

### 2. Feature Extraction

User input is normalized and converted into TF-IDF features using both word and character n-grams. This helps the model handle:
- short symptom phrases
- multi-word symptoms
- spelling variations

### 3. Symptom Probability Estimation

The model predicts a probability for each symptom label. The app then keeps the strongest symptom matches and uses those scores to rank medicines.

### 4. Medicine Recommendation

For each predicted symptom, the system:
- retrieves the medicines mapped to that symptom
- boosts medicines that match the live inventory catalog
- avoids duplicates while combining reasons from multiple symptoms

### 5. Confidence Scoring

Confidence is based on the average probability of the selected symptoms:

Confidence = average(selected symptom probabilities) × 100

- Higher confidence = stronger model certainty
- Range: 0% to 100%

## Recognizable Symptoms

### Cold & Flu
- `cold` → Cough Syrup, Decongestant, Vitamin C
- `cough` → Cough Syrup, Paracetamol
- `fever` → Paracetamol, Ibuprofen, Aspirin
- `congestion` → Decongestant
- `flu` → Cough Syrup, Vitamin C

### Pain-Related
- `headache` → Aspirin, Paracetamol, Ibuprofen
- `migraine` → Ibuprofen, Aspirin
- `muscle pain` → Ibuprofen, Paracetamol
- `body pain` → Aspirin, Ibuprofen
- `back pain` → Ibuprofen, Paracetamol

### Stomach Issues
- `heartburn` → Omeprazole, Ranitidine
- `acid reflux` → Omeprazole, Ranitidine
- `indigestion` → Omeprazole, Ranitidine
- `stomach pain` → Paracetamol, Omeprazole

### Allergies
- `allergy` → Cetirizine, Loratadine
- `itching` → Cetirizine, Loratadine
- `rash` → Cetirizine
- `hay fever` → Loratadine, Cetirizine

### Vitamins & Supplements
- `weakness` → Vitamin B Complex, Vitamin C
- `fatigue` → Vitamin B Complex
- `low energy` → Vitamin B Complex

## Code Implementation

### Main Class: MedicineRecommendationEngine

Located in: `app/ml_recommendation.py`

```python
class MedicineRecommendationEngine:
    """
    ML-backed recommendation engine for medicine suggestions
    """
    
    SYMPTOM_MEDICINE_MAP = {
        # Symptom keyword maps to list of medicines
    }
    
    @staticmethod
    def get_recommendations(symptoms_text):
        """
        Get medicine recommendations based on symptoms
        
        Returns:
        {
            'recommendations': [
                {
                    'name': 'Medicine Name',
                    'category': 'Category',
                    'reasons': ['Reason 1', 'Reason 2'],
                    'match_count': 2
                }
            ],
            'symptoms_matched': ['symptom1', 'symptom2'],
            'confidence': 25.5,
            'message': 'Found X medicine(s) matching your symptoms'
        }
        """
```

### Usage Example

```python
from app.ai_recommendation import recommend_medicines_for_symptoms

# Get recommendations
result = recommend_medicines_for_symptoms("I have a bad cold and fever")

print(result['message'])  # "Found 5 medicine(s) matching your symptoms"
print(result['confidence'])  # 22.2 (2 matched symptoms out of 9 total)
print(result['symptoms_matched'])  # ['cold', 'fever']

for med in result['recommendations']:
    print(f"{med['name']}: {med['reasons']}")
```

## Extending the System

### Adding New Symptoms

1. Open `app/ml_recommendation.py`
2. Find `SYMPTOM_MEDICINE_MAP` dictionary
3. Add new symptom:

```python
'new_symptom': [
    {
        'name': 'Medicine Name',
        'category': 'Existing Category',
        'reason': 'Why this medicine helps'
    },
    {
        'name': 'Another Medicine',
        'category': 'Category',
        'reason': 'Another reason'
    }
]
```

### Adding New Medicine

1. Add the medicine in the Medicines management (Admin Panel)
2. Add symptom mappings in `SYMPTOM_MEDICINE_MAP`

## Integration with Flask Routes

### In `app/routes.py`:

```python
@recommendation_bp.route('/get-recommendation', methods=['POST'])
@login_required
def get_recommendation():
    symptoms = request.form.get('symptoms', '')
    
    # Call AI engine
    result = recommend_medicines_for_symptoms(symptoms)
    
    # Save recommendation to database
    recommendation = Recommendation(
        user_id=current_user.id,
        symptoms=symptoms,
        recommended_medicines=json.dumps(result['recommendations'])
    )
    db.session.add(recommendation)
    db.session.commit()
    
    return render_template('recommendation/results.html', 
                         symptoms=symptoms,
                         result=result,
                         medicines=medicines)
```

## Limitations & Disclaimers

### Current Limitations
1. **Small Training Corpus**: The model is trained from synthetic symptom phrases and aliases.
2. **No Medical Validation**: Recommendations aren't validated by doctors.
3. **No Temporal Analysis**: It doesn't reason about symptom duration or progression.
4. **No Drug Interaction Logic**: It doesn't check drug conflicts, allergies, or contraindications.

### Important Disclaimers
- ⚠️ **NOT a substitute for medical advice**
- ⚠️ Always consult healthcare professionals
- ⚠️ For emergency symptoms, seek immediate medical help
- ⚠️ Recommendations are based on symptom keywords only
- ⚠️ Does not consider drug interactions or allergies

## Future Improvements

### Short Term
1. Add more symptom training phrases and aliases
2. Add drug interaction checking
3. Include severity levels (mild/moderate/severe)
4. Improve confidence calibration

### Medium Term
1. Expand the training corpus with real user examples
2. Add doctor validation of recommendations
3. Add a user feedback loop for learning
4. Pharmaceutical database integration
5. Experiment with embeddings-based ranking

### Long Term
1. Deep learning models (LSTM, BERT, transformers)
2. Multi-language support
3. Integration with medical APIs
4. Prescription drug interaction database
5. Real-time symptom tracking

## Testing the AI System

### Manual Testing

1. Go to `/recommendations/`
2. Enter symptoms like:
   - "I have a fever"
   - "Bad headache and cold"
   - "Stomach pain and heartburn"
3. View recommendations

### Expected Output

For "I have a high fever and cough":
```
Matched Symptoms: ['fever', 'cough']
Confidence: 22.2%
Recommendations:
- Paracetamol (fever reducer)
- Ibuprofen (anti-inflammatory)
- Cough Syrup (cough suppressant)
```

## Performance Considerations

### Complexity Analysis
- Inference time is driven by TF-IDF vectorization and per-symptom probability scoring.
- Training happens once and is cached in memory for subsequent requests.
- Space usage is mainly the cached model, feature transformer, and recommendation output.

### Optimization Tips
1. Cache the trained model and feature transformer in memory
2. Expand the symptom training corpus with real user phrases
3. Calibrate the probability threshold for symptom selection
4. Implement Redis for caching recommendation responses

## Configuration

### Adjusting Confidence Calculation

Current formula:
```python
confidence = average(selected symptom probabilities) * 100
```

To modify, edit the `get_recommendations()` method in `app/ml_recommendation.py`.

### Changing Symptom Keywords

Edit the `SYMPTOM_MEDICINE_MAP` and `SYMPTOM_ALIASES` dictionaries in `app/ml_recommendation.py`.
Those values also seed the training phrases used by the model.

## References

- Symptom database based on common medical conditions
- Medicine information from pharmaceutical databases
- TF-IDF and logistic regression concepts from machine learning and NLP

---

**Last Updated**: 2026  
**Version**: 2.0  
**Maintained By**: AcuMeds Development Team
