import click
import json
import os
from runner.runner import Runner
from scoring.brittleness_report import save_report
from versioning.differ import save_diff

# First, need to load catalog
def load_variant_catalog():
    with open('variants/variant_catalog.json', 'r') as f:
        return json.load(f)

@click.group()
def cli():
    pass

@cli.command()
@click.option('--template', 'template_id', required=True, help='Template ID to run')
@click.option('--variants', default='all', help='Variant types to run: all or comma-separated')
@click.option('--use-mock', is_flag=True, default=True, help='Use mock responder')
def run(template_id, variants, use_mock):
    runner = Runner(use_mock=use_mock)
    template_path = f"templates/template_{template_id.split('_')[0]}.yaml"  # e.g., qa_v1 -> template_qa.yaml
    catalog = load_variant_catalog()
    if template_id not in catalog:
        click.echo(f"Template {template_id} not in catalog")
        return
    all_variants = []
    variant_types = variants.split(',') if variants != 'all' else list(catalog[template_id].keys())
    for typ in variant_types:
        if typ in catalog[template_id]:
            all_variants.extend(catalog[template_id][typ])
    
    results = runner.run(template_path, all_variants)
    # Save results
    os.makedirs('results', exist_ok=True)
    with open(f'results/results_{template_id}.json', 'w') as f:
        json.dump(results, f, indent=2)
    click.echo(f"Run complete, results saved to results/results_{template_id}.json")

@cli.command()
@click.option('--use-mock', is_flag=True, default=True)
def run_all(use_mock):
    catalog = load_variant_catalog()
    for template_id in catalog:
        click.echo(f"Running {template_id}")
        run.callback(template_id, 'all', use_mock)

@cli.command()
@click.option('--template', 'template_id', required=True)
def report(template_id):
    with open(f'results/results_{template_id}.json', 'r') as f:
        results = json.load(f)
    template_path = f"templates/template_{template_id.split('_')[0]}.yaml"
    save_report(template_path, results)
    click.echo("Report generated: results/brittleness_report.md")

@cli.command()
@click.option('--v1', required=True, help='Version 1 template ID')
@click.option('--v2', required=True, help='Version 2 template ID')
def diff(v1, v2):
    with open(f'results/results_{v1}.json', 'r') as f:
        results_v1 = json.load(f)
    with open(f'results/results_{v2}.json', 'r') as f:
        results_v2 = json.load(f)
    save_diff(results_v1, results_v2, v1, v2)
    click.echo(f"Diff generated: results/version_diff_{v1}_vs_{v2}.md")

@cli.command()
def mock():
    # Perhaps run all with mock
    run_all.callback(use_mock=True)

if __name__ == '__main__':
    cli()
