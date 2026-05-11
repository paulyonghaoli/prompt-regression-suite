import json
from variant_generator import generate_variants

# Base inputs for each template
base_inputs = {
    'qa_v1': [
        {'context': 'AI is artificial intelligence, a field of computer science that focuses on creating machines capable of intelligent behavior.', 'question': 'What is AI?'},
        {'context': 'Python is a programming language.', 'question': 'What is Python?'},
    ],
    'summarize_v1': [
        {'text': 'Artificial intelligence is transforming various industries by automating tasks and improving decision-making processes.'},
        {'text': 'Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed.'},
    ],
    'classify_v1': [
        {'text': 'I absolutely love this new feature!'},
        {'text': 'This product is terrible and I hate it.'},
        {'text': 'The weather is okay today.'},
    ]
}

catalog = {}
for template_id, bases in base_inputs.items():
    print(f"Generating for {template_id}")
    catalog[template_id] = generate_variants(template_id, bases)

print("Saving catalog")
with open('variants/variant_catalog.json', 'w') as f:
    json.dump(catalog, f, indent=2)
print("Done")