import subprocess
import datetime
import json

now_iso = datetime.datetime.utcnow().isoformat() + "Z"
links = {
    "fr": "https://zamania.fr/blog/accelerez-signatures-propositions-commerciales.html",
    "en": "https://zamania.fr/en/blog/accelerez-signatures-propositions-commerciales.html",
    "ar": "https://zamania.fr/ar/blog/accelerez-signatures-propositions-commerciales.html"
}
links_json = json.dumps(links)

cmd = [
    "python3", "/opt/data/website-zamania/.automation/zamania_topic_guard.py",
    "record-publication",
    "/opt/data/website-zamania/.automation/zamania-proposals-latest.json",
    "2",
    "accelerez-signatures-propositions-commerciales",
    "--published-at", now_iso,
    "--links-json", links_json
]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
