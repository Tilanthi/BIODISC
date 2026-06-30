#!/usr/bin/env python3
"""
Generate CV vs. CCGC graph for the bacterial cell cycle review manuscript.
This script creates Figure 6 showing the relationship between Cell Cycle Gene Count (CCGC)
and division timing Coefficient of Variation (CV) for syn3.0 and E. coli.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# Set up figure parameters for publication quality
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 10
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['axes.linewidth'] = 1.0

# Data points
# syn3.0: CCGC ≈ 16, CV = 0.35-0.45
# E. coli Core: CCGC ≈ 98, CV = 0.10-0.15
# E. coli Extended: CCGC ≈ 150, CV = 0.10-0.15

syn30_ccgc = 16
syn30_cv_mean = 0.40
syn30_cv_range = (0.35, 0.45)

ecoli_core_ccgc = 98
ecoli_extended_ccgc = 150
ecoli_cv_mean = 0.125
ecoli_cv_range = (0.10, 0.15)

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Plot schematic curve (hypothetical inverse relationship)
# This represents the Molecular Complexity Threshold hypothesis
x = np.linspace(10, 160, 200)
# Schematic curve showing decreasing CV with increasing CCGC
# Using a function that levels off at higher CCGC values
y_schematic = 0.15 + 0.30 * np.exp(-(x - 16) / 40)  # Exponential decay from syn3.0

ax.plot(x, y_schematic, '--', color='gray', alpha=0.5, linewidth=2,
        label='Hypothetical relationship\n(Molecular Complexity Threshold)')

# Plot data points with error bars
# syn3.0
ax.errorbar(syn30_ccgc, syn30_cv_mean,
            yerr=[[syn30_cv_mean - syn30_cv_range[0]], [syn30_cv_range[1] - syn30_cv_mean]],
            fmt='o', color='red', markersize=10, capsize=5, linewidth=2,
            label='JCVI-syn3.0 (CCGC ≈ 16, CV = 0.35-0.45)')

# E. coli Core
ax.errorbar(ecoli_core_ccgc, ecoli_cv_mean,
            yerr=[[ecoli_cv_mean - ecoli_cv_range[0]], [ecoli_cv_range[1] - ecoli_cv_mean]],
            fmt='s', color='blue', markersize=10, capsize=5, linewidth=2,
            label='E. coli Core CCGC (≈ 98, CV = 0.10-0.15)')

# E. coli Extended
ax.errorbar(ecoli_extended_ccgc, ecoli_cv_mean,
            yerr=[[ecoli_cv_mean - ecoli_cv_range[0]], [ecoli_cv_range[1] - ecoli_cv_mean]],
            fmt='^', color='green', markersize=10, capsize=5, linewidth=2,
            label='E. coli Extended CCGC (≈ 150, CV = 0.10-0.15)')

# Threshold annotation (hypothetical)
ax.axvline(x=45, color='purple', linestyle=':', linewidth=2, alpha=0.7)
ax.text(47, 0.38, 'Hypothetical\nthreshold\n(CCGC ≈ 45 ± 10)',
        fontsize=9, color='purple', style='italic')

# Annotations
ax.annotate('', xy=(syn30_ccgc + 5, syn30_cv_mean),
            xytext=(syn30_ccgc + 30, syn30_cv_mean + 0.05),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            fontsize=8)
ax.text(syn30_ccgc + 5, syn30_cv_mean + 0.06,
        'High variability:\nPhysical tendencies\ndominant',
        fontsize=9, style='italic')

ax.annotate('', xy=(ecoli_core_ccgc - 5, ecoli_cv_mean),
            xytext=(ecoli_core_ccgc - 40, ecoli_cv_mean + 0.05),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
            fontsize=8)
ax.text(ecoli_core_ccgc - 45, ecoli_cv_mean + 0.06,
        'Low variability:\nMolecular regulation\ndominant',
        fontsize=9, style='italic')

# Critical caveats
caveat_text = 'CRITICAL: This comparison is hypothesis-generating ONLY.\nMultiple confounding variables (geometry, growth rate, phylogeny)\nprevent attribution of CV differences to CCGC alone.'
ax.text(0.5, 0.02, caveat_text, transform=ax.transAxes,
        fontsize=8, style='italic', ha='center',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# Labels and formatting
ax.set_xlabel('Cell Cycle Gene Count (CCGC)', fontsize=12, fontweight='bold')
ax.set_ylabel('Division Timing Coefficient of Variation (CV)', fontsize=12, fontweight='bold')
ax.set_title('Figure 6. Molecular Complexity Threshold: CCGC vs. CV Relationship',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlim(0, 170)
ax.set_ylim(0, 0.55)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

# Add explanatory note
explanatory_text = ('Note: The schematic curve represents a hypothetical inverse relationship\n'
                     'between CCGC and CV based on the Molecular Complexity Threshold hypothesis.\n'
                     'Current data (2 points) cannot validate this relationship - intermediate\n'
                     'organisms with CCGC values between syn3.0 and E. coli are required.')
ax.text(0.5, 0.95, explanatory_text, transform=ax.transAxes,
        fontsize=8, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

plt.tight_layout()
plt.savefig('/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures/fig6_molecular_complexity_threshold.png',
            dpi=300, bbox_inches='tight')
plt.savefig('/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures/fig6_molecular_complexity_threshold.pdf',
            bbox_inches='tight')
print("Figure 6 generated successfully!")
print("Saved as: figures/fig6_molecular_complexity_threshold.png")
print("Saved as: figures/fig6_molecular_complexity_threshold.pdf")
plt.close()
