import pytest
from versioning.differ import compare_versions

def test_changed_scores():
    results_v1 = [
        {'input_hash': 'hash1', 'contract_score': {'score': 'pass'}, 'inputs': {'q': 'test'}, 'output': 'ok'}
    ]
    results_v2 = [
        {'input_hash': 'hash1', 'contract_score': {'score': 'fail'}, 'inputs': {'q': 'test'}, 'output': 'bad'}
    ]
    diff = compare_versions(results_v1, results_v2, 'v1', 'v2')
    assert 'pass -> fail' in diff

def test_added_removed():
    results_v1 = [{'input_hash': 'hash1', 'contract_score': {'score': 'pass'}, 'inputs': {}, 'output': ''}]
    results_v2 = [{'input_hash': 'hash2', 'contract_score': {'score': 'pass'}, 'inputs': {}, 'output': ''}]
    diff = compare_versions(results_v1, results_v2, 'v1', 'v2')
    assert 'removed in v2' in diff
    assert 'added in v2' in diff