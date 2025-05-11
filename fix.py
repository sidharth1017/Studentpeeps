import json

with open("pgdata.json") as f:
    data = json.load(f)

exclude_models = [
    "contenttypes.contenttype",
    "auth.permission",
    "auth.user",
    "sessions.session",
    "social_django.usersocialauth",
    "admin.logentry",  # <- this line fixes your current error
]

filtered_data = [obj for obj in data if obj["model"].lower() not in exclude_models]

with open("filtered_pgdata_final.json", "w") as f:
    json.dump(filtered_data, f, indent=2)
