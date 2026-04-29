#!/usr/bin/env python3
"""
Benchmark Report Generator v4
Produces HTML + text report with: overall ranking, speed leaderboard,
cost-adjusted leaderboard, per-category breakdown, routing table.
New columns: Quality (median), tok/s (mean), TTFT p50, Total latency p50,
Cost/task (mean), Quality/$, Quality/sec.
"""

import json, sys, statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BENCHMARK_DIR = Path(__file__).parent
VERSION_PREFIX = "v4"

def load_results(results_dir):
    raw_dir = results_dir / "raw"
    scores_file = results_dir / "scores.json"
    results = []
    for task_dir in sorted(raw_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        for result_file in sorted(task_dir.glob("*.json")):
            data = json.loads(result_file.read_text())
            results.append(data)
    scores = {}
    if scores_file.exists():
        scores = json.loads(scores_file.read_text())
    return results, scores

def compute_model_stats(results, scores):
    model_data = defaultdict(lambda: {
        "scores": [], "code_pass_rates": [], "latencies": [],
        "ttfts": [], "tokens_per_sec": [], "costs": [],
        "input_tokens": [], "output_tokens": [],
        "errors": 0, "total": 0, "category_scores": defaultdict(list),
    })
    for r in results:
        if r.get("status") != "ok":
            model_data[r["model_id"]]["errors"] += 1
            model_data[r["model_id"]]["total"] += 1
            continue
        mid = r["model_id"]
        m = r.get("metrics", {})
        model_data[mid]["total"] += 1
        if m.get("total_latency_ms"):
            model_data[mid]["latencies"].append(m["total_latency_ms"])
        if m.get("ttft_ms"):
            model_data[mid]["ttfts"].append(m["ttft_ms"])
        if m.get("tokens_per_sec"):
            model_data[mid]["tokens_per_sec"].append(m["tokens_per_sec"])
        if m.get("cost_usd"):
            model_data[mid]["costs"].append(m["cost_usd"])
        if m.get("input_tokens"):
            model_data[mid]["input_tokens"].append(m["input_tokens"])
        if m.get("output_tokens"):
            model_data[mid]["output_tokens"].append(m["output_tokens"])
        if m.get("code_pass_rate") is not None:
            model_data[mid]["code_pass_rates"].append(m["code_pass_rate"])
        category = r.get("category", "unknown")
        score_key = f"{r['task_id']}/{mid}"
        if score_key in scores:
            s = scores[score_key].get("median_score")
            if s is not None:
                model_data[mid]["scores"].append(s)
                model_data[mid]["category_scores"][category].append(s)
        if m.get("code_pass_rate") is not None:
            model_data[mid]["category_scores"]["code"].append(m["code_pass_rate"] / 10)

    stats = {}
    for mid, d in model_data.items():
        all_quality = d["scores"] + [r / 10 for r in d["code_pass_rates"]]
        median_quality = round(statistics.median(all_quality), 2) if all_quality else 0
        mean_tps = round(statistics.mean(d["tokens_per_sec"]), 1) if d["tokens_per_sec"] else None
        p50_ttft = round(statistics.median(d["ttfts"]), 1) if d["ttfts"] else None
        p50_latency = round(statistics.median(d["latencies"]), 1) if d["latencies"] else None
        mean_cost = round(statistics.mean(d["costs"]), 6) if d["costs"] else 0
        total_cost = round(sum(d["costs"]), 4) if d["costs"] else 0
        quality_per_dollar = round(median_quality / mean_cost, 2) if mean_cost > 0 else None
        quality_per_sec = round(median_quality / (p50_latency / 1000), 3) if p50_latency and p50_latency > 0 else None

        stats[mid] = {
            "model_id": mid,
            "median_quality": median_quality,
            "avg_quality": round(statistics.mean(all_quality), 2) if all_quality else 0,
            "avg_judge_score": round(statistics.mean(d["scores"]), 2) if d["scores"] else None,
            "avg_code_pass_rate": round(statistics.mean(d["code_pass_rates"]), 1) if d["code_pass_rates"] else None,
            "mean_tokens_per_sec": mean_tps,
            "p50_ttft_ms": p50_ttft,
            "p50_latency_ms": p50_latency,
            "avg_latency_ms": round(statistics.mean(d["latencies"])) if d["latencies"] else None,
            "mean_cost_per_task": mean_cost,
            "total_cost": total_cost,
            "quality_per_dollar": quality_per_dollar,
            "quality_per_sec": quality_per_sec,
            "error_rate": round(d["errors"] / d["total"] * 100, 1) if d["total"] > 0 else 0,
            "total_runs": d["total"],
            "category_scores": {cat: round(statistics.mean(sl), 2) for cat, sl in d["category_scores"].items()},
        }
    return stats

# Composite routing weights
ROUTING_WEIGHTS = {
    "grounding": 0.30,
    "relevance": 0.30,
    "quality": 0.30,
    "speed": 0.09,
    "cost_efficiency": 0.01,
}

def _normalize(values):
    """Min-max normalize a list of values to [0, 1]."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]

def compute_routing_table(stats, config, extra_scores=None, extra_per_cat=None):
    """Compute routing table using composite score:
    Grounding 30%, Relevance 30%, Quality 25%, Speed 10%, Cost Efficiency 5%.
    Uses per-category grounding/relevance when available.
    """
    if extra_scores is None:
        extra_scores = {"grounding": {}, "relevance": {}}
    if extra_per_cat is None:
        extra_per_cat = {"grounding": {}, "relevance": {}}
    categories = set()
    for s in stats.values():
        categories.update(s["category_scores"].keys())
    routing = []
    for cat in sorted(categories):
        # Gather candidates with all metrics
        candidates = []
        for mid, s in stats.items():
            if cat not in s.get("category_scores", {}):
                continue
            # Prefer per-category grounding/relevance, fall back to model-level
            grnd = extra_per_cat["grounding"].get(cat, {}).get(mid)
            if grnd is None:
                grnd = extra_scores["grounding"].get(mid, 0)
            relv = extra_per_cat["relevance"].get(cat, {}).get(mid)
            if relv is None:
                relv = extra_scores["relevance"].get(mid, 0)
            candidates.append({
                "model_id": mid,
                "quality": s["category_scores"][cat],
                "grounding": grnd,
                "relevance": relv,
                "speed": s.get("mean_tokens_per_sec") or 0,
                "cost_efficiency": s.get("quality_per_dollar") or 0,
            })
        if not candidates:
            continue
        # Normalize each dimension to [0, 1]
        for dim in ["quality", "grounding", "relevance", "speed", "cost_efficiency"]:
            raw = [c[dim] for c in candidates]
            normed = _normalize(raw)
            for c, n in zip(candidates, normed):
                c[f"{dim}_norm"] = n
        # Compute composite score
        w = ROUTING_WEIGHTS
        for c in candidates:
            c["composite"] = (
                w["grounding"] * c["grounding_norm"] +
                w["relevance"] * c["relevance_norm"] +
                w["quality"] * c["quality_norm"] +
                w["speed"] * c["speed_norm"] +
                w["cost_efficiency"] * c["cost_efficiency_norm"]
            )
        candidates.sort(key=lambda c: c["composite"], reverse=True)
        recommended = candidates[0]
        fallback = candidates[1] if len(candidates) > 1 else candidates[0]
        routing.append({
            "category": cat,
            "recommended": recommended["model_id"],
            "recommended_composite": round(recommended["composite"], 3),
            "recommended_quality": recommended["quality"],
            "recommended_speed": recommended["speed"],
            "fallback": fallback["model_id"],
            "fallback_composite": round(fallback["composite"], 3),
            "fallback_quality": fallback["quality"],
            "all_ranked": [{"model_id": c["model_id"], "composite": round(c["composite"], 3),
                            "quality": c["quality"], "grounding": c["grounding"],
                            "relevance": c["relevance"]} for c in candidates],
        })
    return routing

def load_extra_scores(results_dir):
    """Load grounding and relevance scores (model-level averages for display)."""
    extra = {"grounding": {}, "relevance": {}}
    for kind in ["grounding", "relevance"]:
        f = results_dir / f"{kind}_scores.json"
        if f.exists():
            data = json.loads(f.read_text())
            model_scores = {}
            for task_id, models in data.items():
                for model_id, info in models.items():
                    if isinstance(info, dict) and "score" in info:
                        model_scores.setdefault(model_id, []).append(info["score"])
            for mid, sl in model_scores.items():
                extra[kind][mid] = round(sum(sl)/len(sl), 1)
    return extra


def load_extra_scores_per_category(results_dir):
    """Load grounding and relevance scores broken down by category.
    Returns {kind: {category: {model_id: avg_score}}}.
    """
    # Build task_id -> category map from raw results
    raw_dir = results_dir / "raw"
    task_cats = {}
    if raw_dir.exists():
        for task_dir in sorted(raw_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            for f in task_dir.glob("*.json"):
                d = json.loads(f.read_text())
                task_cats[d.get("task_id", task_dir.name)] = d.get("category", "unknown")
                break

    result = {"grounding": defaultdict(dict), "relevance": defaultdict(dict)}
    for kind in ["grounding", "relevance"]:
        f = results_dir / f"{kind}_scores.json"
        if not f.exists():
            continue
        data = json.loads(f.read_text())
        # Accumulate per (category, model)
        cat_model_scores = defaultdict(lambda: defaultdict(list))
        for task_id, models in data.items():
            cat = task_cats.get(task_id, "unknown")
            for model_id, info in models.items():
                if isinstance(info, dict) and "score" in info:
                    cat_model_scores[cat][model_id].append(info["score"])
        for cat, model_scores in cat_model_scores.items():
            for mid, sl in model_scores.items():
                result[kind][cat][mid] = round(sum(sl) / len(sl), 1)
    return result

def generate_html(stats, routing, scores, results_dir, extra_scores=None):
    ranked = sorted(stats.values(), key=lambda x: x["median_quality"], reverse=True)
    speed_ranked = sorted(stats.values(), key=lambda x: x.get("mean_tokens_per_sec") or 0, reverse=True)
    cost_ranked = sorted([s for s in stats.values() if s.get("quality_per_dollar")], key=lambda x: x["quality_per_dollar"], reverse=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Model Benchmark Report v4</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.6; }}
  h1 {{ border-bottom: 3px solid #2563eb; padding-bottom: 8px; }}
  h2 {{ color: #2563eb; margin-top: 2em; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.85em; }}
  th, td {{ border: 1px solid #d1d5db; padding: 5px 8px; text-align: left; }}
  th {{ background: #f3f4f6; font-weight: 600; }}
  tr:nth-child(even) {{ background: #f9fafb; }}
  .meta {{ color: #6b7280; font-size: 0.9em; margin-bottom: 2em; }}
  .best {{ background: #d1fae5 !important; font-weight: 600; }}
  .routing {{ background: #eff6ff; padding: 16px; border-radius: 8px; margin: 12px 0; }}
</style>
</head>
<body>
<h1>📊 Model Benchmark Report v4</h1>
<div class="meta">
  <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")} &nbsp;|&nbsp;
  <strong>Models:</strong> {len(stats)} &nbsp;|&nbsp;
  <strong>Results:</strong> {results_dir}
</div>

<h2>Overall Ranking</h2>
"""
    # Compute overall composite for each model
    overall_data = []
    for s in stats.values():
        mid = s['model_id']
        grnd = extra_scores['grounding'].get(mid, 0) if extra_scores else 0
        relv = extra_scores['relevance'].get(mid, 0) if extra_scores else 0
        overall_data.append({
            'stats': s,
            'grounding': grnd,
            'relevance': relv,
            'quality': s['median_quality'],
            'speed': s.get('mean_tokens_per_sec') or 0,
            'cost_efficiency': s.get('quality_per_dollar') or 0,
        })
    # Normalize each dimension
    for dim in ['quality', 'grounding', 'relevance', 'speed', 'cost_efficiency']:
        raw = [d[dim] for d in overall_data]
        normed = _normalize(raw)
        for d, n in zip(overall_data, normed):
            d[f'{dim}_norm'] = n
    w = ROUTING_WEIGHTS
    for d in overall_data:
        d['overall'] = (
            w['grounding'] * d['grounding_norm'] +
            w['relevance'] * d['relevance_norm'] +
            w['quality'] * d['quality_norm'] +
            w['speed'] * d['speed_norm'] +
            w['cost_efficiency'] * d['cost_efficiency_norm']
        )
    overall_data.sort(key=lambda d: d['overall'], reverse=True)

    html += '<table>\n'
    html += '<tr><th>#</th><th>Model</th><th>Overall</th><th>Grounding</th><th>Relevance</th><th>Quality</th><th>Tok/s</th><th>Cost/task</th><th>Q/$</th><th>Code%</th><th>TTFT p50</th><th>Lat p50</th><th>Errors</th></tr>\n'
    for i, d in enumerate(overall_data, 1):
        s = d['stats']
        rc = ' class="best"' if i == 1 else ''
        tps = f"{s['mean_tokens_per_sec']:.0f}" if s['mean_tokens_per_sec'] else "—"
        ttft = f"{s['p50_ttft_ms']:.0f}" if s['p50_ttft_ms'] else "—"
        lat = f"{s['p50_latency_ms']:.0f}" if s['p50_latency_ms'] else "—"
        cpt = f"${s['mean_cost_per_task']:.4f}" if s['mean_cost_per_task'] else "—"
        qpd = f"{s['quality_per_dollar']:.1f}" if s.get('quality_per_dollar') else "—"
        code_pct = f"{s['avg_code_pass_rate']:.0f}%" if s.get('avg_code_pass_rate') is not None else "—"
        html += f'<tr{rc}><td>{i}</td><td>{s["model_id"]}</td><td>{d["overall"]:.3f}</td>'
        html += f'<td>{d["grounding"]:.1f}</td><td>{d["relevance"]:.1f}</td><td>{s["median_quality"]:.2f}</td>'
        html += f'<td>{tps}</td><td>{cpt}</td><td>{qpd}</td>'
        html += f'<td>{code_pct}</td><td>{ttft}</td><td>{lat}</td><td>{s["error_rate"]:.0f}%</td></tr>\n'
    html += "</table>\n"

    # Speed leaderboard
    html += "<h2>🚀 Speed Leaderboard (by tok/s)</h2>\n<table>\n"
    html += "<tr><th>#</th><th>Model</th><th>Tok/s</th><th>TTFT p50</th><th>Latency p50</th><th>Quality</th></tr>\n"
    for i, s in enumerate(speed_ranked, 1):
        rc = ' class="best"' if i == 1 else ''
        tps = f"{s['mean_tokens_per_sec']:.0f}" if s['mean_tokens_per_sec'] else "—"
        ttft = f"{s['p50_ttft_ms']:.0f}" if s['p50_ttft_ms'] else "—"
        lat = f"{s['p50_latency_ms']:.0f}" if s['p50_latency_ms'] else "—"
        html += f'<tr{rc}><td>{i}</td><td>{s["model_id"]}</td><td>{tps}</td><td>{ttft}</td><td>{lat}</td><td>{s["median_quality"]:.2f}</td></tr>\n'
    html += "</table>\n"

    # Cost-adjusted leaderboard
    html += "<h2>💰 Cost-Adjusted Leaderboard (by Quality/$)</h2>\n<table>\n"
    html += "<tr><th>#</th><th>Model</th><th>Quality/$</th><th>Quality</th><th>Cost/task</th></tr>\n"
    for i, s in enumerate(cost_ranked, 1):
        rc = ' class="best"' if i == 1 else ''
        html += f'<tr{rc}><td>{i}</td><td>{s["model_id"]}</td><td>{s["quality_per_dollar"]:.1f}</td>'
        html += f'<td>{s["median_quality"]:.2f}</td><td>${s["mean_cost_per_task"]:.4f}</td></tr>\n'
    html += "</table>\n"

    # Per-category breakdown
    html += "<h2>Per-Category Breakdown</h2>\n"
    # Build routing lookup for composite scores
    routing_by_cat = {r["category"]: r for r in routing}
    categories = set()
    for s in stats.values():
        categories.update(s["category_scores"].keys())
    for cat in sorted(categories):
        r = routing_by_cat.get(cat)
        if r and r.get("all_ranked"):
            # Use composite-ranked data from routing
            html += f"<h3>{cat.title()}</h3>\n<table>\n<tr><th>#</th><th>Model</th><th>Composite</th><th>Grounding</th><th>Relevance</th><th>Quality</th><th>Speed</th><th>Cost/task</th></tr>\n"
            for i, c in enumerate(r["all_ranked"][:10], 1):
                rc = ' class="best"' if i == 1 else ""
                spd = stats.get(c["model_id"], {}).get("mean_tokens_per_sec") or 0
                cpt = stats.get(c["model_id"], {}).get("mean_cost_per_task") or 0
                cpt_str = f"${cpt:.4f}" if cpt else "\u2014"
                html += f'<tr{rc}><td>{i}</td><td>{c["model_id"]}</td><td>{c["composite"]:.3f}</td><td>{c["grounding"]:.1f}</td><td>{c["relevance"]:.1f}</td><td>{c["quality"]:.2f}</td><td>{spd:.0f} tok/s</td><td>{cpt_str}</td></tr>\n'
            html += "</table>\n"
        else:
            cat_models = [(mid, s["category_scores"].get(cat, 0), s.get("mean_tokens_per_sec", 0) or 0)
                           for mid, s in stats.items() if cat in s.get("category_scores", {})]
            cat_models.sort(key=lambda x: x[1], reverse=True)
            if not cat_models:
                continue
            html += f"<h3>{cat.title()}</h3>\n<table>\n<tr><th>#</th><th>Model</th><th>Score</th><th>Speed</th></tr>\n"
            for i, (mid, score, speed) in enumerate(cat_models[:10], 1):
                rc = ' class="best"' if i == 1 else ""
                html += f'<tr{rc}><td>{i}</td><td>{mid}</td><td>{score:.2f}</td><td>{speed:.0f} tok/s</td></tr>\n'
            html += "</table>\n"

    # Routing table
    html += '<h2>Routing Table</h2>\n<div class="routing">\n'
    html += "<table>\n<tr><th>Category</th><th>Recommended</th><th>Quality</th><th>Speed</th><th>Fallback</th></tr>\n"
    for r in routing:
        html += f'<tr><td><strong>{r["category"].title()}</strong></td>'
        html += f'<td>{r["recommended"]}</td><td>{r["recommended_quality"]:.1f}</td>'
        html += f'<td>{r["recommended_speed"]:.0f} tok/s</td><td>{r["fallback"]}</td></tr>\n'
    html += "</table>\n</div>\n"

    # Flagged disagreements
    flagged = [v for v in scores.values() if isinstance(v, dict) and v.get("flagged")]
    if flagged:
        html += "<h2>⚠️ Flagged Disagreements</h2>\n<table>\n"
        html += "<tr><th>Task</th><th>Model</th><th>Scores</th><th>Spread</th></tr>\n"
        for f in flagged:
            scores_str = ", ".join([f"{j['judge']}={j.get('score', '?')}" for j in f.get("judges", [])])
            html += f'<tr><td>{f["task_id"]}</td><td>{f["model_id"]}</td><td>{scores_str}</td><td>{f["spread"]}</td></tr>\n'
        html += "</table>\n"

    html += "</body>\n</html>"
    return html

def generate_text(stats, routing, results_dir, extra_scores=None):
    """Generate plain text report."""
    if extra_scores is None:
        extra_scores = {"grounding": {}, "relevance": {}}
    # Compute overall composite
    overall_data = []
    for s in stats.values():
        mid = s['model_id']
        overall_data.append({
            'stats': s,
            'grounding': extra_scores['grounding'].get(mid, 0),
            'relevance': extra_scores['relevance'].get(mid, 0),
            'quality': s['median_quality'],
            'speed': s.get('mean_tokens_per_sec') or 0,
            'cost_efficiency': s.get('quality_per_dollar') or 0,
        })
    for dim in ['quality', 'grounding', 'relevance', 'speed', 'cost_efficiency']:
        raw = [d[dim] for d in overall_data]
        normed = _normalize(raw)
        for d, n in zip(overall_data, normed):
            d[f'{dim}_norm'] = n
    w = ROUTING_WEIGHTS
    for d in overall_data:
        d['overall'] = (
            w['grounding'] * d['grounding_norm'] +
            w['relevance'] * d['relevance_norm'] +
            w['quality'] * d['quality_norm'] +
            w['speed'] * d['speed_norm'] +
            w['cost_efficiency'] * d['cost_efficiency_norm']
        )
    overall_data.sort(key=lambda d: d['overall'], reverse=True)

    lines = [f"Model Benchmark Report v4 — {datetime.now().strftime('%Y-%m-%d %H:%M')}", f"Results: {results_dir}", ""]
    lines.append(f"{'#':>2} {'Model':<30} {'Overall':>7} {'Grnd':>5} {'Relv':>5} {'Quality':>8} {'tok/s':>7} {'Cost/t':>9} {'Q/$':>7} {'Code%':>6} {'TTFT':>7} {'Lat p50':>8}")
    lines.append("-" * 120)
    for i, d in enumerate(overall_data, 1):
        s = d['stats']
        tps = f"{s['mean_tokens_per_sec']:.0f}" if s['mean_tokens_per_sec'] else "—"
        ttft = f"{s['p50_ttft_ms']:.0f}" if s['p50_ttft_ms'] else "—"
        lat = f"{s['p50_latency_ms']:.0f}" if s['p50_latency_ms'] else "—"
        cpt = f"${s['mean_cost_per_task']:.4f}" if s['mean_cost_per_task'] else "—"
        qpd = f"{s['quality_per_dollar']:.1f}" if s.get('quality_per_dollar') else "—"
        code_pct = f"{s['avg_code_pass_rate']:.0f}%" if s.get('avg_code_pass_rate') is not None else "—"
        lines.append(f"{i:>2} {s['model_id']:<30} {d['overall']:>7.3f} {d['grounding']:>5.1f} {d['relevance']:>5.1f} {s['median_quality']:>8.2f} {tps:>7} {cpt:>9} {qpd:>7} {code_pct:>6} {ttft:>7} {lat:>8}")
    lines.append("")
    lines.append("Routing Table:")
    for r in routing:
        lines.append(f"  {r['category']:12} → {r['recommended']:30} (fallback: {r['fallback']})")
    return "\n".join(lines)

def diff_routing(v4_routing, v3_dir):
    """Compare v4 routing to v3."""
    try:
        v3_results, v3_scores = load_results(v3_dir)
        from collections import defaultdict
        v3_stats = compute_model_stats(v3_results, v3_scores)
        v3_config = json.loads((BENCHMARK_DIR / "config" / "models.json").read_text())
        v3_routing = compute_routing_table(v3_stats, v3_config)
        v3_map = {r["category"]: r["recommended"] for r in v3_routing}
        v4_map = {r["category"]: r["recommended"] for r in v4_routing}
        diffs = []
        all_cats = sorted(set(list(v3_map.keys()) + list(v4_map.keys())))
        for cat in all_cats:
            v3m = v3_map.get(cat, "—")
            v4m = v4_map.get(cat, "—")
            if v3m != v4m:
                diffs.append(f"  {cat}: {v3m} → {v4m}")
        if diffs:
            return "Routing changes v3→v4:\n" + "\n".join(diffs)
        return "Routing unchanged from v3."
    except Exception as e:
        return f"Could not diff v3 routing: {e}"

def main():
    results_parent = BENCHMARK_DIR / "results"
    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        results_dir = Path(sys.argv[idx + 1])
    else:
        existing = sorted([d for d in results_parent.iterdir() if d.name.startswith(f"{VERSION_PREFIX}-")], reverse=True)
        if not existing:
            print(f"No {VERSION_PREFIX} results found.")
            sys.exit(1)
        results_dir = existing[0]

    config = json.loads((BENCHMARK_DIR / "config" / "models.json").read_text())

    print(f"Loading results from: {results_dir}")
    results, scores = load_results(results_dir)
    print(f"  {len(results)} result files, {len(scores)} judge scores")

    stats = compute_model_stats(results, scores)
    extra_scores = load_extra_scores(results_dir)
    extra_per_cat = load_extra_scores_per_category(results_dir)
    routing = compute_routing_table(stats, config, extra_scores, extra_per_cat)
    html = generate_html(stats, routing, scores, results_dir, extra_scores)
    report_html = results_dir / "report.html"
    report_html.write_text(html)
    print(f"HTML report: {report_html}")

    txt = generate_text(stats, routing, results_dir, extra_scores)
    # Append v3 diff
    v3_dir = results_parent / "v3-20260407-194331"
    if v3_dir.exists():
        txt += "\n\n" + diff_routing(routing, v3_dir)
    report_txt = results_dir / "report.txt"
    report_txt.write_text(txt)
    print(f"Text report: {report_txt}")

    print(f"\nRouting Table:")
    for r in routing:
        print(f"  {r['category']:12} → {r['recommended']:30} (fallback: {r['fallback']})")

if __name__ == "__main__":
    main()
