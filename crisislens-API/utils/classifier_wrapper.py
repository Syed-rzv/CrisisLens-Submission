import sys
import logging
import numpy as np
import os

classifier_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Classifier', 'production')
if os.path.exists(classifier_path):
    sys.path.append(classifier_path)
else:
    sys.path.append('/app/Classifier/production')

from classifier_service import EmergencyClassifier

logger = logging.getLogger(__name__)

class BatchClassifier:
    def __init__(self):
        self.main_classifier = EmergencyClassifier()
        logger.info("batch classifier loaded")
    
    def classify_batch(self, descriptions):
        if not isinstance(descriptions, list):
            descriptions = descriptions.tolist()
        
        results = []
        
        for desc in descriptions:
            try:
                main_pred = self.main_classifier.main_model.predict([desc])[0]
                main_proba = self.main_classifier.main_model.predict_proba([desc])[0]
                confidence = float(np.max(main_proba))
                
                subtype = self.main_classifier.classify_subtype(desc, main_pred)
                
                results.append({
                    'emergency_type': main_pred,
                    'emergency_subtype': subtype,
                    'confidence': round(confidence, 4)})
            except Exception as e:
                logger.error(f"classification failed: {desc[:50]}... {str(e)}")
                results.append({
                    'emergency_type': 'Unknown',
                    'emergency_subtype': 'Classification Failed',
                    'confidence': 0.0})
        
        return results
    
    def classify_dataframe(self, df):
        if 'description' not in df.columns:
            raise ValueError("need description column")
        
        logger.info(f"classifying {len(df)} records")
        
        classifications = self.classify_batch(df['description'].tolist())
        
        df['emergency_type'] = [c['emergency_type'] for c in classifications]
        df['emergency_subtype'] = [c['emergency_subtype'] for c in classifications]
        df['classification_confidence'] = [c['confidence'] for c in classifications]
        df['classification_method'] = 'ML_Classified'
        
        df['needs_review'] = df['classification_confidence'] < 0.7
        
        high_conf = (df['classification_confidence'] >= 0.7).sum()
        logger.info(f"done. high confidence: {high_conf}/{len(df)}")
        
        return df