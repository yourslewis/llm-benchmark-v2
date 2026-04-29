import json

d = json.load(open("benchmark/results/v3-20260407-194331/scores.json"))
keys = [k for k,v in d.items() if len(v.get("judges",[]))<2 or any(j.get("score") is None for j in v.get("judges",[]))]
for k in keys:
    d.pop(k)
json.dump(d, open("benchmark/results/v3-20260407-194331/scores.json","w"), indent=2)
print(f"Removed {len(keys)} incomplete scores. {len(d)} remain.")