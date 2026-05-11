from typing import List, Dict, Any
from collections import defaultdict, Counter
from scoring.consistency import check_consistency
from scoring.contract_checker import check_contract
import yaml

def generate_report(template_path: str, results: List[Dict[str, Any]]) -> str:
    with open(template_path, 'r') as f:
        template = yaml.safe_load(f)
    template_id = template['id']
    
    # Score contracts
    for r in results:
        r['contract_score'] = check_contract(r['output'], r['inputs'], template['contract'])
    
    # Consistency
    consistency = check_consistency(results, template_id)
    
    # Pass rates
    total = len(results)
    pass_count = sum(1 for r in results if r['contract_score']['score'] == 'pass')
    pass_rate = pass_count / total if total > 0 else 0
    
    # Fail rate by variant type
    fail_by_type = defaultdict(int)
    for r in results:
        if r['contract_score']['score'] != 'pass':
            fail_by_type[r.get('variant_type', 'unknown')] += 1
    
    # Worst variant type
    worst_type = max(fail_by_type, key=fail_by_type.get) if fail_by_type else 'none'
    
    # Top 5 damaging variants
    failed_results = [r for r in results if r['contract_score']['score'] != 'pass']
    # Sort by some damage score, e.g., number of reasons
    failed_results.sort(key=lambda r: len(r['contract_score']['reasons']), reverse=True)
    top_damaging = failed_results[:5]
    
    # Verdict
    if consistency['consistency_score'] > 0.9 and pass_rate > 0.9:
        verdict = 'robust'
    elif consistency['consistency_score'] > 0.7 and pass_rate > 0.7:
        verdict = 'moderate'
    else:
        verdict = 'brittle'
    
    # Recommendations
    recs = []
    if consistency['is_brittle']:
        recs.append("Improve consistency by adding more explicit instructions in the prompt.")
    if fail_by_type.get('typo', 0) > total * 0.1:
        recs.append("Add typo normalization preprocessing to handle input errors.")
    if fail_by_type.get('adversarial', 0) > total * 0.1:
        recs.append("Implement input sanitization to prevent prompt injection.")
    if not recs:
        recs.append("No major issues detected.")
    
    # Generate markdown
    md = f"# Brittleness Report for {template_id}\n\n"
    md += f"## Consistency Score: {consistency['consistency_score']:.3f}\n"
    md += f"## Contract Pass Rate: {pass_rate:.3f} ({pass_count}/{total})\n"
    md += f"## Fail Rate by Variant Type:\n"
    for typ, count in fail_by_type.items():
        md += f"- {typ}: {count} ({count/total:.3f})\n"
    md += f"## Worst Variant Type: {worst_type}\n"
    md += f"## Brittleness Verdict: {verdict}\n"
    md += f"## Recommended Hardening Actions:\n"
    for rec in recs:
        md += f"- {rec}\n"
    md += f"\n## Top 5 Most Damaging Variants:\n"
    for i, r in enumerate(top_damaging, 1):
        md += f"### {i}. Variant Type: {r.get('variant_type')}\n"
        md += f"Input: {r['inputs']}\n"
        md += f"Output: {r['output']}\n"
        md += f"Reasons: {', '.join(r['contract_score']['reasons'])}\n\n"
    
    return md

def save_report(template_path: str, results: List[Dict[str, Any]], output_path: str = 'results/brittleness_report.md'):
    report = generate_report(template_path, results)
    with open(output_path, 'w') as f:
        f.write(report)