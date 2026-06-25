import json
d = json.load(open("/opt/data/sessions/sessions.json"))
for k, v in d.items():
    if not isinstance(v, dict):
        print(f"Key {k} has value of type {type(v)}")
