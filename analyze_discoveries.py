#!/usr/bin/env python3
import json

with open("autonomous_discoveries.jsonl", "r") as f:
    discoveries = []
    for line in f:
        try:
            data = json.loads(line)
            if data.get("pipeline_version") == "V6.0-FIXED-INTEGRATED":
                discoveries.append(data)
        except:
            pass

print(f"Total V6.0-FIXED discoveries: {len(discoveries)}")

best_fc = {"fc": 0, "discovery": None, "gene": None}
best_p = {"p": float("inf"), "discovery": None, "gene": None}
most_genes = {"count": 0, "discovery": None, "de": None}

for discovery in discoveries:
    if "differential_expression" in discovery:
        de = discovery["differential_expression"]

        if "top_upregulated" in de and de["top_upregulated"]:
            for gene in de["top_upregulated"]:
                p_val = gene.get("p_value", float("inf"))
                if p_val < best_p["p"]:
                    best_p = {"p": p_val, "discovery": discovery, "gene": gene}

                fc = gene.get("log2_fold_change", 0)
                if abs(fc) > abs(best_fc["fc"]):
                    best_fc = {"fc": fc, "discovery": discovery, "gene": gene}

        sig_count = de.get("significant_genes", 0)
        if sig_count > most_genes["count"]:
            most_genes = {"count": sig_count, "discovery": discovery, "de": de}

print("\n🏆 MOST SIGNIFICANT DISCOVERIES SINCE UPGRADE:\n")

print("📈 BEST FOLD CHANGE:")
if best_fc["discovery"]:
    d = best_fc["discovery"]
    g = best_fc["gene"]
    print(f"   Discovery ID: {d.get('discovery_id', 'N/A')}")
    print(f"   Gene: {g.get('gene_symbol', 'N/A')}")
    print(f"   Log2FC: {g.get('log2_fold_change', 'N/A')}")
    print(f"   P-value: {g.get('p_value', 'N/A')}")
    print(f"   FDR: {g.get('fdr_p_value', 'N/A')}")
    print(f"   Question: {d.get('question', 'N/A')}")

print("\n🧬 MOST SIGNIFICANT P-VALUE:")
if best_p["discovery"]:
    d = best_p["discovery"]
    g = best_p["gene"]
    print(f"   Discovery ID: {d.get('discovery_id', 'N/A')}")
    print(f"   Gene: {g.get('gene_symbol', 'N/A')}")
    print(f"   P-value: {g.get('p_value', 'N/A')}")
    print(f"   FDR: {g.get('fdr_p_value', 'N/A')}")
    print(f"   Log2FC: {g.get('log2_fold_change', 'N/A')}")
    print(f"   Question: {d.get('question', 'N/A')}")

print("\n📊 HIGHEST GENE COUNT:")
if most_genes["discovery"]:
    d = most_genes["discovery"]
    de = most_genes["de"]
    print(f"   Discovery ID: {d.get('discovery_id', 'N/A')}")
    print(f"   Total genes tested: {de.get('total_genes_tested', 'N/A')}")
    print(f"   Significant genes: {de.get('significant_genes', 'N/A')}")
    print(f"   Upregulated: {de.get('upregulated_genes', 'N/A')}")
    print(f"   Downregulated: {de.get('downregulated_genes', 'N/A')}")
    print(f"   Method: {de.get('method', 'N/A')} with {de.get('correction', 'N/A')}")
    print(f"   Question: {d.get('question', 'N/A')}")

print("\n🎯 OVERALL MOST SIGNIFICANT DISCOVERY:")
# Determine which is most significant overall
# We'll prioritize the combination of fold change and p-value
candidates = []

if best_fc["discovery"]:
    fc_score = abs(best_fc["fc"]) / (1 + abs(best_fc["fc"]))
    p_score = 1 / (1 + best_fc["gene"].get("p_value", 1))
    candidates.append(("Fold Change", best_fc["discovery"], best_fc["gene"], fc_score + p_score))

if best_p["discovery"]:
    fc_score = abs(best_p["gene"].get("log2_fold_change", 0)) / (1 + abs(best_p["gene"].get("log2_fold_change", 0)))
    p_score = 1 / (1 + best_p["p"])
    candidates.append(("P-value", best_p["discovery"], best_p["gene"], fc_score + p_score))

if candidates:
    winner = max(candidates, key=lambda x: x[3])
    print(f"   Winner: {winner[0]} category")
    d = winner[1]
    g = winner[2]
    print(f"   Discovery ID: {d.get('discovery_id', 'N/A')}")
    print(f"   Gene: {g.get('gene_symbol', 'N/A')}")
    print(f"   Log2FC: {g.get('log2_fold_change', 'N/A')}")
    print(f"   P-value: {g.get('p_value', 'N/A')}")
    print(f"   FDR: {g.get('fdr_p_value', 'N/A')}")
    print(f"   Timestamp: {d.get('timestamp', 'N/A')}")
    print(f"   Question: {d.get('question', 'N/A')}")
    print(f"   V6.0 Enhancements: {d.get('v6_enhancements', {})}")
