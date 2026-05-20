import json, pathlib, sys
if len(sys.argv) < 2:
    print('Usage: python generate_report.py <summary.json>')
    raise SystemExit(2)
summary_path = pathlib.Path(sys.argv[1])
summary = json.loads(summary_path.read_text(encoding='utf-8'))
print(summary_path.with_name('review_report.md'))
