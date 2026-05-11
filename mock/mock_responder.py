import random
import re
from typing import Dict, Any

class MockResponder:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.responses = {
            'qa_v1': {
                'normal': "AI is artificial intelligence, a field of computer science.",
                'paraphrase': "Artificial intelligence refers to the simulation of human intelligence in machines.",
                'typo': "AI is artifical inteligence, a feild of compter science.",  # degraded
                'adversarial': "Yes",  # 30% break
                'edge_empty_context': "",
                'edge_long_context': "AI is artificial intelligence.",  # truncated
                'edge_short_question': "A",
                'edge_other_lang': "I don't know"
            },
            'summarize_v1': {
                'normal': "Summary: AI is transforming industries through automation and decision-making.",
                'paraphrase': "Summary: Artificial intelligence changes sectors by automating processes and aiding choices.",
                'typo': "Summary: AI is transorming industres thru automaton and decison-making.",  # missing format sometimes
                'adversarial': "Summary: Yes",
                'edge_empty': "",
                'edge_long': "Summary: AI...",  # truncated
                'edge_short': "Summary: AI",
                'edge_other_lang': "Summary: L'IA transforme les industries."
            },
            'classify_v1': {
                'normal': "positive",
                'paraphrase': "positive",
                'typo': "positve",  # degraded
                'adversarial': "Yes",
                'edge_empty': "",
                'edge_long': "positive",
                'edge_short': "positive",
                'edge_other_lang': "positive"
            }
        }

    def respond(self, template_id: str, variant_type: str, prompt: str) -> str:
        # For adversarial, 30% chance to break
        if variant_type == 'adversarial' and random.random() < 0.3:
            return self.responses[template_id].get('adversarial', "Yes")
        
        # For edge cases
        if variant_type == 'edge':
            if 'empty' in prompt.lower() or len(prompt.split()) < 5:
                return self.responses[template_id].get('edge_empty', "")
            if len(prompt) > 1000:
                return self.responses[template_id].get('edge_long', "Truncated")
            if re.search(r'[¿¡]', prompt):  # other lang
                return self.responses[template_id].get('edge_other_lang', "I don't know")
            return self.responses[template_id].get('edge_short', "Short")
        
        # For typo, sometimes missing format
        if variant_type == 'typo' and random.random() < 0.5:
            resp = self.responses[template_id].get('typo', self.responses[template_id]['normal'])
            if 'Summary:' in resp and random.random() < 0.5:
                resp = resp.replace('Summary: ', '')
            return resp
        
        # Default to normal or paraphrase
        if variant_type in ['paraphrase', 'normal']:
            return self.responses[template_id].get(variant_type, self.responses[template_id]['normal'])
        
        return self.responses[template_id]['normal']