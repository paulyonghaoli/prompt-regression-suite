from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')  # Small model for speed

def compute_consistency_score(outputs: List[str]) -> float:
    if len(outputs) < 2:
        return 1.0  # Perfect if only one
    embeddings = model.encode(outputs)
    similarities = cosine_similarity(embeddings)
    # Mean of upper triangle (excluding diagonal)
    n = len(outputs)
    mean_sim = (np.sum(similarities) - n) / (n * (n - 1) / 2)
    return mean_sim

def check_consistency(results: List[Dict[str, Any]], template_id: str) -> Dict[str, Any]:
    paraphrase_results = [r for r in results if r.get('variant_type') == 'paraphrase']
    if not paraphrase_results:
        return {'consistency_score': 1.0, 'is_brittle': False}
    
    # Group by base_id
    groups = {}
    for r in paraphrase_results:
        base_id = r.get('base_id', 0)
        if base_id not in groups:
            groups[base_id] = []
        groups[base_id].append(r['output'])
    
    scores = []
    for outputs in groups.values():
        score = compute_consistency_score(outputs)
        scores.append(score)
    
    overall_score = np.mean(scores) if scores else 1.0
    is_brittle = overall_score < 0.8
    
    return {
        'consistency_score': overall_score,
        'is_brittle': is_brittle,
        'per_base_scores': scores
    }