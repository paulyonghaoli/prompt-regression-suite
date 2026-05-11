import pytest
from variants.variant_generator import generate_variants

def test_variant_counts():
    base_inputs = [{'question': 'What is AI?', 'context': 'AI is intelligence'}]
    variants = generate_variants('qa_v1', base_inputs)
    assert len(variants['paraphrase']) == 5  # 5 per base
    assert len(variants['typo']) == 3
    assert len(variants['adversarial']) == 3
    assert len(variants['edge']) == 4  # fixed

def test_adversarial_injections():
    base_inputs = [{'question': 'What is AI?', 'context': 'AI is intelligence'}]
    variants = generate_variants('qa_v1', base_inputs)
    for v in variants['adversarial']:
        question = v.get('question', '')
        assert 'Ignore previous' in question or 'irrelevant' in v.get('context', '') or 'capital of France' in question

def test_variant_types():
    base_inputs = [{'question': 'What is AI?', 'context': 'AI is intelligence'}]
    variants = generate_variants('qa_v1', base_inputs)
    for typ in ['paraphrase', 'typo', 'adversarial', 'edge']:
        for v in variants[typ]:
            assert v['variant_type'] == typ