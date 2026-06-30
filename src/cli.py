from __future__ import annotations
import json
import sys
from pathlib import Path
import click
from src.config import load_config
from src.extractors.csv_extractor import extract_from_csv
from src.extractors.resume_extractor import extract_from_resume
from src.merger import merge_candidates
from src.exporter import export_candidate


@click.command()
@click.option("--csv", "-c", "csv_path", help="Path to recruiter CSV file")
@click.option("--resume", "-r", "resume_paths", multiple=True, help="Path to resume file (TXT or PDF)")
@click.option("--config", "-cfg", "config_path", default="config.json", help="Path to config.json")
@click.option("--output", "-o", "output_path", default="output.json", help="Path to write output JSON")
@click.option("--indent", "-i", default=2, help="JSON indentation level")
def main(csv_path, resume_paths, config_path, output_path, indent):
    config = load_config(config_path)

    all_candidates = []

    if csv_path:
        click.echo(f"Reading CSV: {csv_path}")
        csv_file = Path(csv_path)
        if not csv_file.exists():
            click.echo(f"Error: CSV file not found: {csv_path}", err=True)
            sys.exit(1)
        try:
            csv_candidates = extract_from_csv(csv_file)
            all_candidates.extend(csv_candidates)
            click.echo(f"  Found {len(csv_candidates)} candidate(s) from CSV")
        except Exception as e:
            click.echo(f"Error reading CSV: {e}", err=True)
            sys.exit(1)

    for rp in resume_paths:
        click.echo(f"Reading resume: {rp}")
        res_file = Path(rp)
        if not res_file.exists():
            click.echo(f"Error: Resume file not found: {rp}", err=True)
            sys.exit(1)
        try:
            resume_candidate = extract_from_resume(res_file)
            if resume_candidate:
                all_candidates.append(resume_candidate)
                click.echo(f"  Extracted candidate: {resume_candidate.candidate_id}")
            else:
                click.echo(f"  Warning: No data extracted from {rp}", err=True)
        except Exception as e:
            click.echo(f"Error reading resume {rp}: {e}", err=True)
            sys.exit(1)

    if not all_candidates:
        click.echo("Error: No candidates found from any source", err=True)
        sys.exit(1)

    merged = merge_candidates(all_candidates)

    result = export_candidate(merged, config)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=indent, default=str)

    click.echo(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
