#!/usr/bin/env python3
"""
STRING Database Network Analysis for Independent Complexity Metrics
Extracts protein-protein interaction network properties for bacterial cell cycle proteins

Usage: python bacterial_phase2_string_analysis.py
Output: string_network_metrics.csv, string_complexity_scores.json
"""

import requests
import json
import csv
from pathlib import Path
import time
import statistics

# STRING API configuration
STRING_API_URL = "https://string-db.org/api"
STRING_VERSION = "11.5"
OUTPUT_FORMAT = "json"

# Cell cycle proteins for each organism (core set)
CELL_CYCLE_PROTEINS = {
    "Escherichia_coli": {
        "taxid": 511145,
        "proteins": [
            "dnaA", "dnaB", "dnaC", "diaA", "seqA", "dam", "hda",
            "minC", "minD", "minE", "slmA",
            "ftsZ", "ftsA", "zipA", "zapA", "zapB", "zapC",
            "parA", "parB", "smc", "mukB", "mukE", "mukF",
            "lexA", "recA", "sulA", "relA", "spoT"
        ]
    },
    "Bacillus_subtilis": {
        "taxid": 224308,
        "proteins": [
            "dnaA", "dnaB", "dnaD", "dnaI", "yabA",
            "minC", "minD", "divIVA", "minJ", "noc",
            "ftsZ", "ftsA", "ezrA", "sepF", "zapA", "zapB",
            "parA", "parB", "smc", "scpA", "scpB",
            "lexA", "recA", "relA", "spoT"
        ]
    },
    "Caulobacter_crescentus": {
        "taxid": 254295,
        "proteins": [
            "dnaA", "dnaB", "dnaX",
            "ctrA", "cckA", "chpT", "divJ", "pleC", "divK",
            "ftsZ", "ftsA", "mipZ",
            "parA", "parB", "smc",
            "lexA", "recA"
        ]
    },
    "Mycoplasma_pneumoniae": {
        "taxid": 2104,
        "proteins": ["dnaA", "dnaN", "ftsZ"]
    },
    "Pseudomonas_aeruginosa": {
        "taxid": 287,
        "proteins": [
            "dnaA", "dnaB", "dnaC", "diaA", "seqA",
            "minC", "minD", "minE",
            "ftsZ", "ftsA", "zipA", "zapA",
            "parA", "parB", "smc",
            "lexA", "recA", "sulA", "relA", "spoT"
        ]
    },
    "Vibrio_cholerae": {
        "taxid": 243277,
        "proteins": [
            "dnaA", "dnaB", "dnaC", "seqA",
            "minC", "minD", "minE",
            "ftsZ", "ftsA", "zapA",
            "parA1", "parB1", "parA2", "parB2", "smc",
            "lexA", "recA", "relA", "spoT"
        ]
    },
    "Salmonella_enterica": {
        "taxid": 28901,
        "proteins": [
            "dnaA", "dnaB", "dnaC", "diaA", "seqA", "dam", "hda",
            "minC", "minD", "minE", "slmA",
            "ftsZ", "ftsA", "zipA", "zapA",
            "parA", "parB", "smc",
            "lexA", "recA", "sulA", "relA", "spoT"
        ]
    },
    "Streptococcus_pneumoniae": {
        "taxid": 1313,
        "proteins": [
            "dnaA", "dnaB", "dnaX",
            "ftsZ", "ftsA", "ezrA",
            "parA", "parB", "smc",
            "lexA", "recA", "relA", "spoT"
        ]
    },
    "Staphylococcus_aureus": {
        "taxid": 93061,
        "proteins": [
            "dnaA", "dnaB", "dnaD", "dnaX",
            "ftsZ", "ftsA", "ezrA",
            "parA", "parB", "smc",
            "lexA", "recA", "relA", "sigB"
        ]
    },
    "Helicobacter_pylori": {
        "taxid": 210,
        "proteins": ["dnaA", "dnaB", "ftsZ", "lexA", "recA", "hp0958"]
    },
    "Corynebacterium_glutamicum": {
        "taxid": 196627,
        "proteins": [
            "dnaA", "dnaB", "dnaX",
            "ftsZ", "ftsA", "ezrA", "divIVA",
            "parA", "parB", "smc",
            "lexA", "recA", "relA"
        ]
    },
    "Sinorhizobium_meliloti": {
        "taxid": 359292,
        "proteins": [
            "dnaA", "dnaB",
            "ctrA", "cckA", "chpT",
            "ftsZ", "ftsA",
            "parA", "parB", "smc",
            "lexA", "recA", "relA"
        ]
    },
    "Mycoplasma_gallisepticum": {
        "taxid": 2575,
        "proteins": ["dnaA", "ftsZ"]
    }
}

def make_string_request(endpoint, params):
    """Make request to STRING API"""
    params.update({
        "format": OUTPUT_FORMAT,
        "requester": "biodisc_analysis"
    })

    url = f"{STRING_API_URL}/{OUTPUT_FORMAT}/{endpoint}/"
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return None

def get_network_properties(organism_name, organism_data):
    """Extract network properties for cell cycle proteins"""
    taxid = organism_data["taxid"]
    proteins = organism_data["proteins"]

    print(f"\nProcessing {organism_name} (taxid: {taxid})...")

    # Get interaction network
    protein_list = ",".join([f"{taxid}.{p}" for p in proteins])

    # Get interaction scores
    interaction_params = {
        "identifiers": protein_list,
        "required_score": 400,  # Medium confidence threshold
        "network_flavor": "full"
    }

    interactions = make_string_request("network", interaction_params)

    if not interactions:
        print(f"  No interactions found for {organism_name}")
        return None

    # Build adjacency list
    edges = {}
    for interaction in interactions:
        from_protein = interaction.get("preferredName_A", "")
        to_protein = interaction.get("preferredName_B", "")
        score = float(interaction.get("combined_score", 0))

        if from_protein not in edges:
            edges[from_protein] = []
        if to_protein not in edges:
            edges[to_protein] = []

        edges[from_protein].append((to_protein, score))
        edges[to_protein].append((from_protein, score))

    # Calculate network properties
    nodes = list(edges.keys())
    num_nodes = len(nodes)
    num_edges = sum(len(neighbors) for neighbors in edges.values()) // 2

    # Node degrees
    degrees = [len(edges[node]) for node in nodes]
    avg_degree = statistics.mean(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0

    # Clustering coefficient (for nodes with neighbors)
    clustering_coeffs = []
    for node in nodes:
        neighbors = edges[node]
        if len(neighbors) < 2:
            continue

        # Count edges between neighbors
        neighbor_edges = 0
        for i, n1 in enumerate(neighbors):
            for n2 in neighbors[i+1:]:
                if n2 in [n for n, _ in edges.get(n1, [])]:
                    neighbor_edges += 1

        possible_edges = len(neighbors) * (len(neighbors) - 1) / 2
        if possible_edges > 0:
            clustering_coeffs.append(neighbor_edges / possible_edges)

    avg_clustering = statistics.mean(clustering_coeffs) if clustering_coeffs else 0

    # Calculate STRING complexity score
    # STRING_CCS = (nodes × 1) + (edges × 2) + (avg_degree × 5) + (clustering × 3)
    string_ccs = (num_nodes * 1) + (num_edges * 2) + (avg_degree * 5) + (avg_clustering * 3)

    result = {
        "organism": organism_name,
        "taxid": taxid,
        "network_nodes": num_nodes,
        "network_edges": num_edges,
        "avg_degree": round(avg_degree, 3),
        "max_degree": max_degree,
        "clustering_coefficient": round(avg_clustering, 3),
        "string_ccs": round(string_ccs, 2),
        "proteins_found": len(nodes),
        "proteins_queried": len(proteins)
    }

    print(f"  Nodes: {num_nodes}, Edges: {num_edges}")
    print(f"  Avg degree: {avg_degree:.3f}, Clustering: {avg_clustering:.3f}")
    print(f"  STRING CCS: {string_ccs:.2f}")

    return result

def main():
    """Main analysis function"""
    print("="*60)
    print("STRING Database Network Analysis")
    print("Independent Complexity Metrics for Cell Cycle Regulation")
    print("="*60)

    results = []

    for organism_name, organism_data in CELL_CYCLE_PROTEINS.items():
        try:
            result = get_network_properties(organism_name, organism_data)
            if result:
                results.append(result)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"  Error processing {organism_name}: {e}")
            continue

    # Save results to CSV
    output_file = Path("string_network_metrics.csv")
    with open(output_file, 'w', newline='') as f:
        if results:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"\nResults saved to {output_file}")

    # Save as JSON
    json_file = Path("string_complexity_scores.json")
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"JSON saved to {json_file}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF STRING COMPLEXITY SCORES")
    print("="*60)
    print(f"{'Organism':<25} {'Nodes':<7} {'Edges':<7} {'Avg Deg':<8} {'Cluster':<8} {'CCS':<8}")
    print("-"*60)
    for r in sorted(results, key=lambda x: x['string_ccs'], reverse=True):
        print(f"{r['organism']:<25} {r['network_nodes']:<7} {r['network_edges']:<7} "
              f"{r['avg_degree']:<8} {r['clustering_coefficient']:<8} {r['string_ccs']:<8.2f}")

    return results

if __name__ == "__main__":
    main()
