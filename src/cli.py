from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
import click
from src.config import load_config
from src.extractors.csv_extractor import extract_from_csv
from src.extractors.resume_extractor import extract_from_resume
from src.merger import merge_candidates
from src.exporter import export_candidate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--csv", "-c", "csv_path", help="Path to recruiter CSV file")
@click.option("--resume", "-r", "resume_paths", multiple=True, help="Path to resume file (TXT or PDF)")
@click.option("--config", "-cfg", "config_path", default="config.json", help="Path to config.json")
@click.option("--output", "-o", "output_path", default="output.json", help="Path to write output JSON")
@click.option("--indent", "-i", default=2, help="JSON indentation level")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging")
def main(csv_path, resume_paths, config_path, output_path, indent, verbose):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config(config_path)
    logger.info("Loaded config from %s (default_region=%s)", config_path, config.default_region)

    all_candidates = []

    if csv_path:
        logger.info("Reading CSV: %s", csv_path)
        csv_file = Path(csv_path)
        if not csv_file.exists():
            logger.error("CSV file not found: %s", csv_path)
            sys.exit(1)
        try:
            csv_candidates = extract_from_csv(csv_file, config.default_region)
            all_candidates.extend(csv_candidates)
            logger.info("Found %d candidate(s) from CSV", len(csv_candidates))
        except Exception as e:
            logger.error("Error reading CSV: %s", e)
            sys.exit(1)

    for rp in resume_paths:
        logger.info("Reading resume: %s", rp)
        res_file = Path(rp)
        if not res_file.exists():
            logger.error("Resume file not found: %s", rp)
            sys.exit(1)
        try:
            resume_candidate = extract_from_resume(res_file, config.default_region)
            if resume_candidate:
                all_candidates.append(resume_candidate)
                logger.info("Extracted candidate: %s", resume_candidate.candidate_id)
            else:
                logger.warning("No data extracted from %s", rp)
        except Exception as e:
            logger.error("Error reading resume %s: %s", rp, e)
            sys.exit(1)

    if not all_candidates:
        logger.error("No candidates found from any source")
        sys.exit(1)

    merged = merge_candidates(all_candidates)
    logger.info("Merged %d source(s) into candidate %s", len(all_candidates), merged.candidate_id)

    result = export_candidate(merged, config)
    logger.info("Exported candidate data")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=indent, default=str)

    logger.info("Output written to %s", output_path)


if __name__ == "__main__":
    main()
