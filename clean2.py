import json

d = json.load(open("benchmark/results/v3-20260407-194331/scores.json"))
gold_keys = [k for k in d if "goldeneye" in k]
for k in gold_keys:
    d.pop(k)
# Also remove any with incomplete judges
bad_keys = [k for k,v in d.items() if len(v.get("judges",[]))<2 or any(j.get("score") is None for j in v.get("judges",[]))]
for k in bad_keys:
    d.pop(k)
json.dump(d, open("benchmark/results/v3-20260407-194331/scores.json","w"), indent=2)
print(f"Removed {len(gold_keys)} goldeneye + {len(bad_keys)} incomplete. {len(d)} valid scores remain.")