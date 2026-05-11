from typing import Dict, Any, List
import re
from collections import Counter

def get_ngrams(text: str, n: int) -> List[str]:
    words = text.lower().split()
    return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]

def check_must_not_contain(output: str, forbidden: List[str]) -> bool:
    for phrase in forbidden:
        if phrase.lower() in output.lower():
            return False
    return True

def check_must_use_context(output: str, context: str, threshold: int = 1) -> bool:
    if not context:
        return True  # if no context, can't check
    output_4grams = set(get_ngrams(output, 4))
    context_4grams = set(get_ngrams(context, 4))
    overlap = len(output_4grams & context_4grams)
    return overlap >= threshold

def check_max_length(output: str, max_tokens: int) -> bool:
    # Approximate tokens as words / 0.75
    approx_tokens = len(output.split()) / 0.75
    return approx_tokens <= max_tokens

def check_refusal_trigger(output: str, trigger: str, should_appear: bool) -> bool:
    appears = trigger.lower() in output.lower()
    return appears == should_appear

def check_must_be_one_of(output: str, options: List[str]) -> bool:
    output_lower = output.lower().strip()
    return output_lower in [opt.lower() for opt in options]

def check_must_start_with(output: str, prefix: str) -> bool:
    return output.lower().startswith(prefix.lower())

def check_contract(output: str, inputs: Dict[str, str], contract: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []
    score = 'pass'
    
    if 'must_not_contain' in contract:
        if not check_must_not_contain(output, contract['must_not_contain']):
            reasons.append("Contains forbidden phrase")
            score = 'fail'
    
    if 'must_use_context' in contract and contract['must_use_context']:
        context = inputs.get('context', '')
        if not check_must_use_context(output, context):
            reasons.append("Does not use context sufficiently")
            score = 'fail'
    
    if 'max_length_tokens' in contract:
        if not check_max_length(output, contract['max_length_tokens']):
            reasons.append("Exceeds max length")
            score = 'fail'
    
    if 'refusal_trigger' in contract:
        trigger = contract['refusal_trigger']
        # Should appear if context is irrelevant (simple check: if context doesn't contain question keywords)
        question = inputs.get('question', '')
        context = inputs.get('context', '')
        should_appear = not any(word in context.lower() for word in question.lower().split() if len(word) > 3)
        if not check_refusal_trigger(output, trigger, should_appear):
            reasons.append(f"Refusal trigger {'missing' if should_appear else 'unexpected'}")
            score = 'partial' if score == 'pass' else 'fail'
    
    if 'must_be_one_of' in contract:
        if not check_must_be_one_of(output, contract['must_be_one_of']):
            reasons.append("Output not in allowed options")
            score = 'fail'
    
    if 'must_start_with' in contract:
        if not check_must_start_with(output, contract['must_start_with']):
            reasons.append("Does not start with required prefix")
            score = 'fail'
    
    return {
        'score': score,
        'reasons': reasons
    }