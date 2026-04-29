import json

d = json.load(open("benchmark/results/v3-20260407-194331/scores.json"))
before = len(d)
# Remove entries with fewer than 2 judges
bad_keys = [k for k,v in d.items() if len(v.get("judges",[]))<2 or any(j.get("score") is None for j in v.get("judges",[]))]
for k in bad_keys:
    d.pop(k)
json.dump(d, open("benchmark/results/v3-20260407-194331/scores.json","w"), indent=2)
print(f"Removed {len(bad_keys)} incomplete. {len(d)} fully valid scores remain. {399 - len(d)} left to judge.")