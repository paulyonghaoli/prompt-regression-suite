from typing import List, Dict, Any
from collections import defaultdict

def compare_versions(results_v1: List[Dict[str, Any]], results_v2: List[Dict[str, Any]], v1_id: str, v2_id: str) -> str:
    # Index by input_hash
    index_v1 = {r['input_hash']: r for r in results_v1}
    index_v2 = {r['input_hash']: r for r in results_v2}
    
    all_hashes = set(index_v1.keys()) | set(index_v2.keys())
    
    deltas = []
    for h in all_hashes:
        r1 = index_v1.get(h)
        r2 = index_v2.get(h)
        if r1 and r2:
            score1 = r1.get('contract_score', {}).get('score', 'unknown')
            score2 = r2.get('contract_score', {}).get('score', 'unknown')
            if score1 != score2:
                deltas.append({
                    'input_hash': h,
                    'change': f"{score1} -> {score2}",
                    'inputs': r1['inputs'],
                    'output_v1': r1['output'],
                    'output_v2': r2['output'],
                    'reasons_v1': r1.get('contract_score', {}).get('reasons', []),
                    'reasons_v2': r2.get('contract_score', {}).get('reasons', [])
                })
        elif r1:
            deltas.append({
                'input_hash': h,
                'change': f"removed in {v2_id}",
                'inputs': r1['inputs'],
                'output_v1': r1['output'],
                'reasons_v1': r1.get('contract_score', {}).get('reasons', [])
            })
        elif r2:
            deltas.append({
                'input_hash': h,
                'change': f"added in {v2_id}",
                'inputs': r2['inputs'],
                'output_v2': r2['output'],
                'reasons_v2': r2.get('contract_score', {}).get('reasons', [])
            })
    
    # Generate markdown
    md = f"# Version Diff: {v1_id} vs {v2_id}\n\n"
    md += f"Total test cases: {len(all_hashes)}\n"
    md += f"Changed behaviors: {len(deltas)}\n\n"
    
    for d in deltas:
        md += f"## Input Hash: {d['input_hash']}\n"
        md += f"Change: {d['change']}\n"
        md += f"Inputs: {d['inputs']}\n"
        if 'output_v1' in d:
            md += f"Output {v1_id}: {d['output_v1']}\n"
            md += f"Reasons {v1_id}: {d['reasons_v1']}\n"
        if 'output_v2' in d:
            md += f"Output {v2_id}: {d['output_v2']}\n"
            md += f"Reasons {v2_id}: {d['reasons_v2']}\n"
        md += "\n"
    
    return md

def save_diff(results_v1: List[Dict[str, Any]], results_v2: List[Dict[str, Any]], v1_id: str, v2_id: str, output_path: str = None):
    if not output_path:
        output_path = f"results/version_diff_{v1_id}_vs_{v2_id}.md"
    diff = compare_versions(results_v1, results_v2, v1_id, v2_id)
    with open(output_path, 'w') as f:
        f.write(diff)