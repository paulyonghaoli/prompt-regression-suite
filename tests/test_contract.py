import pytest
from scoring.contract_checker import check_contract

def test_must_not_contain():
    contract = {'must_not_contain': ['I think']}
    assert check_contract("I believe", {}, contract)['score'] == 'pass'
    assert check_contract("I think it's true", {}, contract)['score'] == 'fail'

def test_must_use_context():
    contract = {'must_use_context': True}
    inputs = {'context': 'The sky is blue'}
    assert check_contract("The sky is blue", inputs, contract)['score'] == 'pass'
    assert check_contract("The grass is green", inputs, contract)['score'] == 'fail'

def test_max_length():
    contract = {'max_length_tokens': 10}
    assert check_contract("Short", {}, contract)['score'] == 'pass'
    assert check_contract("This is a very long sentence that exceeds the token limit", {}, contract)['score'] == 'fail'

def test_refusal_trigger():
    contract = {'refusal_trigger': "I don't know"}
    inputs = {'question': 'What is AI?', 'context': 'Unrelated text'}
    assert check_contract("I don't know", inputs, contract)['score'] == 'pass'
    inputs2 = {'question': 'What is AI?', 'context': 'AI is artificial intelligence'}
    assert check_contract("AI is...", inputs2, contract)['score'] == 'pass'

def test_must_be_one_of():
    contract = {'must_be_one_of': ['positive', 'negative']}
    assert check_contract("positive", {}, contract)['score'] == 'pass'
    assert check_contract("neutral", {}, contract)['score'] == 'fail'

def test_must_start_with():
    contract = {'must_start_with': 'Summary:'}
    assert check_contract("Summary: text", {}, contract)['score'] == 'pass'
    assert check_contract("text", {}, contract)['score'] == 'fail'