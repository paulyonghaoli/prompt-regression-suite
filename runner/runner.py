import hashlib
import json
import time
from typing import Dict, List, Any
import yaml

from mock.mock_responder import MockResponder

class Runner:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        if use_mock:
            self.responder = MockResponder()
        else:
            # TODO: OpenAI responder
            pass

    def load_template(self, template_path: str) -> Dict[str, Any]:
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)

    def fill_template(self, template: str, inputs: Dict[str, str]) -> str:
        return template.format(**inputs)

    def hash_input(self, inputs: Dict[str, str]) -> str:
        # Sort keys for consistent hash
        input_str = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(input_str.encode()).hexdigest()

    def run_variants(self, template_id: str, template: Dict[str, Any], variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for variant in variants:
            inputs = {k: v for k, v in variant.items() if k not in ['variant_type']}
            prompt = self.fill_template(template['template'], inputs)
            if self.use_mock:
                output = self.responder.respond(template_id, variant.get('variant_type', 'normal'), prompt)
            else:
                # TODO: call OpenAI
                output = "TODO: OpenAI response"
            
            result = {
                'template_id': template_id,
                'variant_type': variant.get('variant_type', 'base'),
                'input_hash': self.hash_input(inputs),
                'inputs': inputs,
                'prompt': prompt,
                'output': output,
                'timestamp': time.time()
            }
            results.append(result)
        return results

    def run(self, template_path: str, variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        template_data = self.load_template(template_path)
        template_id = template_data['id']
        return self.run_variants(template_id, template_data, variants)