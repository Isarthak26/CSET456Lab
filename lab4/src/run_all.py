"""Run every Lab 4 experiment and save one reproducible console transcript."""

from __future__ import annotations

import subprocess
import sys

from common import LAB_DIR, OUTPUT_DIR, REPO_ROOT


SCRIPTS = [
    "select_tokens.py",
    "feature_embedding.py",
    "cooccurrence_embedding.py",
    "word2vec_embedding.py",
    "code2vec_embedding.py",
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript: list[str] = []

    for script_name in SCRIPTS:
        script = LAB_DIR / "src" / script_name
        heading = f"===== {script_name} ====="
        print(heading)
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        section = "\n".join(
            part.rstrip() for part in (heading, result.stdout, result.stderr) if part.strip()
        )
        transcript.append(section)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.returncode != 0:
            raise SystemExit(f"{script_name} failed with exit code {result.returncode}")

    output_path = OUTPUT_DIR / "run_summary.txt"
    output_path.write_text("\n\n".join(transcript) + "\n", encoding="utf-8")
    print(f"Saved combined transcript to {output_path}")


if __name__ == "__main__":
    main()
