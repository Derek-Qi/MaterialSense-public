"""Run from a project checkout; all paths are explicit in --help."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from .batch import predict_csv
from .data import download_data, load_data, prepare_data
from .experiment import run_experiment
from .external import audit_data
from .study import run_study


def main():
    parser = argparse.ArgumentParser(description="MaterialSense local research benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    download = sub.add_parser(
        "download", help="Fetch pinned official UCI data or convert a manual copy"
    )
    download.add_argument("--destination", type=Path, default=Path("data/raw"))
    download.add_argument("--source", type=Path, help="Manual UCI ZIP or Concrete_Data.xls")
    run = sub.add_parser("run", help="Run the frozen grouped benchmark")
    run.add_argument("--data", type=Path, default=Path("data/raw/concrete.csv"))
    run.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    run.add_argument("--output", type=Path, default=Path("artifacts/run"))
    study = sub.add_parser("study", help="Run prespecified repeated grouped evaluations")
    study.add_argument("--data", type=Path, default=Path("data/raw/concrete.csv"))
    study.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    study.add_argument("--study-config", type=Path, default=Path("configs/study.yaml"))
    study.add_argument("--output", type=Path, required=True)
    predict = sub.add_parser("predict", help="Predict CSV using a trusted local model artifact")
    predict.add_argument("--model", type=Path, required=True, help="Only load trusted joblib files")
    predict.add_argument("--input", type=Path, required=True)
    predict.add_argument("--output", type=Path, required=True)
    audit = sub.add_parser("audit-data", help="Screen canonical CSVs without model evaluation")
    audit.add_argument("--candidate", type=Path, required=True)
    audit.add_argument("--reference", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--tolerance", type=float, default=0.1, help="Per-ingredient kg/m3 tolerance")
    args = parser.parse_args()
    try:
        if args.command == "download":
            path = (
                prepare_data(args.source, args.destination)
                if args.source
                else download_data(args.destination)
            )
            print(f"Validated UCI data: {path.resolve()}")
        elif args.command == "audit-data":
            result = audit_data(args.candidate, args.reference, args.output, args.tolerance)
            print(json.dumps({"status": result["status"], "overlap": result["overlap"]}, indent=2))
        elif args.command == "predict":
            result = predict_csv(args.model, args.input, args.output)
            print(f"Saved {len(result)} predictions to {args.output.resolve()}")
        elif args.command == "study":
            config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
            settings = yaml.safe_load(args.study_config.read_text(encoding="utf-8"))
            result = run_study(load_data(args.data), config, settings, args.output)
            print(json.dumps({"status": result["status"], "seeds": result["seeds"]}, indent=2))
        else:
            config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
            metadata = run_experiment(load_data(args.data), config, args.output)
            print(
                json.dumps(
                    {
                        "selected": metadata["selected"],
                        "split_audit": metadata["split_audit"],
                        "report": str((args.output / "summary.md").resolve()),
                    },
                    indent=2,
                )
            )
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as error:
        print(f"MaterialSense: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
