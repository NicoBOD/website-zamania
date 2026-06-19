import subprocess

result = subprocess.run(
    ["python3", "/opt/data/wiki-tech-automation/scripts/detect_selection.py", "--marker", "🗂️ Propositions ZamanIA du jour", "--state-file", "/opt/data/website-zamania/.automation/zamania-selection.json"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)