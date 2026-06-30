#!/usr/bin/env python3
"""
Create high-quality PNG figures for bacterial cell cycle review manuscript.

Creates professional scientific figures replacing ASCII art:
- Figure 1: Hierarchical Framework Schematic
- Figure 2: Min System Hierarchical Integration
- Figure 3: Nucleoid Occlusion
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import numpy as np

# Set up professional figure style
plt.style.use('default')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5

def create_figure1_hierarchical_framework():
    """Create Figure 1: Hierarchical Framework Schematic"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Color scheme (professional scientific colors)
    color_override = '#E74C3C'  # Red for molecular override
    color_sensing = '#3498DB'   # Blue for molecular sensing
    color_physical = '#27AE60'  # Green for physical foundation
    color_arrow = '#7F8C8D'     # Gray for arrows

    # TOP LAYER: Molecular Override Layers
    top_y = 10.5
    override_box = FancyBboxPatch((1.5, top_y - 0.4), 9, 0.8,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color_override, alpha=0.2,
                                   edgecolor=color_override, linewidth=2)
    ax.add_patch(override_box)
    ax.text(6, top_y, 'MOLECULAR OVERRIDE LAYERS',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color=color_override)

    # Override sub-boxes
    override_y = top_y - 1.2
    checkpoint_box = FancyBboxPatch((1, override_y - 0.3), 2.8, 0.6,
                                     boxstyle="round,pad=0.05",
                                     facecolor='white', edgecolor=color_override,
                                     linewidth=1.5)
    ax.add_patch(checkpoint_box)
    ax.text(2.4, override_y, 'Checkpoint\nSystems\n(SOS, etc.)',
            ha='center', va='center', fontsize=8)

    developmental_box = FancyBboxPatch((4.6, override_y - 0.3), 2.8, 0.6,
                                        boxstyle="round,pad=0.05",
                                        facecolor='white', edgecolor=color_override,
                                        linewidth=1.5)
    ax.add_patch(developmental_box)
    ax.text(6, override_y, 'Developmental\nSwitches\n(Caulobacter)',
            ha='center', va='center', fontsize=8)

    precision_box = FancyBboxPatch((8.2, override_y - 0.3), 2.8, 0.6,
                                    boxstyle="round,pad=0.05",
                                    facecolor='white', edgecolor=color_override,
                                    linewidth=1.5)
    ax.add_patch(precision_box)
    ax.text(9.6, override_y, 'Precision\nTiming\nSystems',
            ha='center', va='center', fontsize=8)

    # MIDDLE LAYER: Molecular Sensing & Intervention
    sensing_y = override_y - 1.5
    sensing_box = FancyBboxPatch((2.5, sensing_y - 0.4), 7, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color_sensing, alpha=0.2,
                                  edgecolor=color_sensing, linewidth=2)
    ax.add_patch(sensing_box)
    ax.text(6, sensing_y, 'MOLECULAR SENSING & INTERVENTION LAYER',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color=color_sensing)

    # BOTTOM LAYER: Physical Foundation
    physical_y = sensing_y - 1.5
    physical_box = FancyBboxPatch((1.5, physical_y - 1.2), 9, 1.4,
                                  boxstyle="round,pad=0.1",
                                  facecolor=color_physical, alpha=0.2,
                                  edgecolor=color_physical, linewidth=2)
    ax.add_patch(physical_box)
    ax.text(6, physical_y - 0.5, 'PHYSICAL FOUNDATION LAYER',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color=color_physical)

    # Physical sub-boxes
    phys_sub_y = physical_y - 1.2
    nucleoid_box = FancyBboxPatch((1.5, phys_sub_y - 0.4), 2.5, 0.5,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white', edgecolor=color_physical,
                                   linewidth=1.2)
    ax.add_patch(nucleoid_box)
    ax.text(2.75, phys_sub_y - 0.15, 'Nucleoid\nGeometry\n(strong)',
            ha='center', va='center', fontsize=7)

    topology_box = FancyBboxPatch((4.75, phys_sub_y - 0.4), 2.5, 0.5,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white', edgecolor=color_physical,
                                   linewidth=1.2)
    ax.add_patch(topology_box)
    ax.text(6, phys_sub_y - 0.15, 'DNA\nTopology\n(strong)',
            ha='center', va='center', fontsize=7)

    turgor_box = FancyBboxPatch((8, phys_sub_y - 0.4), 2.5, 0.5,
                                 boxstyle="round,pad=0.05",
                                 facecolor='white', edgecolor=color_physical,
                                 linewidth=1.2, linestyle='--')
    ax.add_patch(turgor_box)
    ax.text(9.25, phys_sub_y - 0.15, 'Turgor\nPressure\n(speculative)',
            ha='center', va='center', fontsize=7)

    # Arrows showing information flow
    # Downward arrows (Physical → Molecular)
    for x in [2.4, 6, 9.6]:
        arrow = FancyArrowPatch((x, override_y + 0.3), (x, sensing_y + 0.5),
                                arrowstyle='->', mutation_scale=20,
                                color=color_arrow, linewidth=2, alpha=0.6)
        ax.add_patch(arrow)

    for x in [3.5, 6, 8.5]:
        arrow = FancyArrowPatch((x, sensing_y - 0.3), (x, physical_y + 0.2),
                                arrowstyle='->', mutation_scale=20,
                                color=color_arrow, linewidth=2, alpha=0.6)
        ax.add_patch(arrow)

    # Legend for information flow
    legend_y = phys_sub_y - 1.2
    ax.text(6, legend_y, 'INFORMATION FLOW', ha='center', fontsize=10,
            fontweight='bold')
    ax.text(6, legend_y - 0.4, 'Physical → Molecular: Molecular systems detect physical states',
            ha='center', fontsize=8, style='italic')
    ax.text(6, legend_y - 0.7, 'Molecular → Physical: Molecular systems intervene to override',
            ha='center', fontsize=8, style='italic')
    ax.text(6, legend_y - 1.0, 'Physical → Molecular (reverse): Does NOT occur',
            ha='center', fontsize=8, style='italic', color='red')

    # Add note at bottom
    ax.text(6, legend_y - 1.6, '*Turgor pressure included for conceptual completeness',
            ha='center', fontsize=7, style='italic')

    plt.tight_layout()
    plt.savefig('/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures/fig1_hierarchical_framework.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created Figure 1: Hierarchical Framework Schematic")

def create_figure2_min_system():
    """Create Figure 2: Min System Hierarchical Integration"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Color scheme
    color_physical = '#27AE60'   # Green
    color_molecular = '#3498DB'  # Blue
    color_override = '#E74C3C'   # Red
    color_arrow = '#7F8C8D'      # Gray

    # TOP: Physical Constraint
    physical_box = FancyBboxPatch((2, 10.5), 8, 0.8,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color_physical, alpha=0.2,
                                   edgecolor=color_physical, linewidth=2.5)
    ax.add_patch(physical_box)
    ax.text(6, 10.9, 'PHYSICAL CONSTRAINT', ha='center', va='center',
            fontsize=13, fontweight='bold', color=color_physical)
    ax.text(6, 10.5, 'Cell Geometry (Length)', ha='center', va='center',
            fontsize=11, color=color_physical)

    # Arrow down
    arrow1 = FancyArrowPatch((6, 10.5), (6, 9.8),
                             arrowstyle='->', mutation_scale=25,
                             color=color_arrow, linewidth=2.5)
    ax.add_patch(arrow1)

    # MIDDLE: Min Oscillation System
    min_box = FancyBboxPatch((1, 6.5), 10, 3.3,
                              boxstyle="round,pad=0.15",
                              facecolor=color_molecular, alpha=0.15,
                              edgecolor=color_molecular, linewidth=2.5)
    ax.add_patch(min_box)
    ax.text(6, 9.5, 'MIN OSCILLATION SYSTEM (Molecular)',
            ha='center', fontsize=12, fontweight='bold', color=color_molecular)

    # Cell representation
    cell_y = 8.5
    cell = FancyBboxPatch((2, cell_y - 0.4), 8, 0.8,
                           boxstyle="round,pad=0.1",
                           facecolor='#ECF0F1', edgecolor='#2C3E50',
                           linewidth=2)
    ax.add_patch(cell)

    # Poles
    pole_a = Circle((2, cell_y), 0.15, color='#2C3E50', zorder=10)
    pole_b = Circle((10, cell_y), 0.15, color='#2C3E50', zorder=10)
    ax.add_patch(pole_a)
    ax.add_patch(pole_b)
    ax.text(1.5, cell_y, 'Pole A', ha='right', va='center', fontsize=9, fontweight='bold')
    ax.text(10.5, cell_y, 'Pole B', ha='left', va='center', fontsize=9, fontweight='bold')

    # Oscillation dynamics visualization
    # MinD gradient
    for i in range(20):
        x = 2 + i * 0.4
        intensity = 0.3 + 0.7 * np.sin(i * 0.5)
        color = plt.cm.Blues(intensity)
        rect = Rectangle((x, cell_y - 0.3), 0.35, 0.6,
                          facecolor=color, edgecolor='none', alpha=0.6)
        ax.add_patch(rect)

    # Labels for components
    ax.text(3.5, cell_y - 0.8, 'MinE', ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#3498DB', linewidth=1))
    ax.text(6, cell_y - 0.8, 'MinD\n(ATP-dependent)', ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#3498DB', linewidth=1))
    ax.text(8.5, cell_y - 0.8, 'MinE', ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#3498DB', linewidth=1))

    # Oscillation dynamics text
    ax.text(6, 7.8, 'OSCILLATION DYNAMICS:', ha='center', fontsize=10,
            fontweight='bold', color=color_molecular)
    ax.text(6, 7.5, 'MinD-ATP binds membrane → recruits MinC → inhibits Z-ring',
            ha='center', fontsize=8)
    ax.text(6, 7.25, 'MinE stimulates MinD-ATP hydrolysis → releases MinD',
            ha='center', fontsize=8)
    ax.text(6, 7.0, 'Result: Pole-to-pole oscillation of MinC inhibition zone',
            ha='center', fontsize=8)

    # Arrow down
    arrow2 = FancyArrowPatch((6, 6.5), (6, 5.8),
                             arrowstyle='->', mutation_scale=25,
                             color=color_arrow, linewidth=2.5)
    ax.add_patch(arrow2)

    # MOLECULAR OVERRIDE box
    override_box = FancyBboxPatch((2, 4.8), 8, 0.8,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color_override, alpha=0.2,
                                   edgecolor=color_override, linewidth=2)
    ax.add_patch(override_box)
    ax.text(6, 5.2, 'MOLECULAR OVERRIDE', ha='center', va='center',
            fontsize=11, fontweight='bold', color=color_override)
    ax.text(6, 4.85, 'Z-ring forms at midcell (low MinC)', ha='center',
            va='center', fontsize=9, color=color_override)

    # Arrow down
    arrow3 = FancyArrowPatch((6, 4.8), (6, 4.1),
                             arrowstyle='->', mutation_scale=25,
                             color=color_arrow, linewidth=2.5)
    ax.add_patch(arrow3)

    # FUNCTIONAL OUTCOME
    outcome_box = FancyBboxPatch((2, 3.1), 8, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor='#F39C12', alpha=0.2,
                                  edgecolor='#F39C12', linewidth=2)
    ax.add_patch(outcome_box)
    ax.text(6, 3.5, 'FUNCTIONAL OUTCOME', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#F39C12')
    ax.text(6, 3.15, 'Precise division site positioning', ha='center',
            va='center', fontsize=9, color='#F39C12')

    # Information flow legend
    legend_y = 2.3
    ax.text(6, legend_y, 'INFORMATION FLOW IN MIN SYSTEM:',
            ha='center', fontsize=10, fontweight='bold')

    ax.text(6, legend_y - 0.4, 'Physical → Molecular: Cell geometry influences Min oscillation period',
            ha='center', fontsize=8, style='italic')
    ax.text(6, legend_y - 0.7, 'Molecular → Physical: MinC pattern determines Z-ring formation',
            ha='center', fontsize=8, style='italic')

    # Key question
    question_y = legend_y - 1.2
    ax.text(6, question_y, 'Key Question: Does Min "actively sense" geometry or',
            ha='center', fontsize=9, fontweight='bold')
    ax.text(6, question_y - 0.3, '"passively respond" to changing volume?',
            ha='center', fontsize=9, fontweight='bold')
    ax.text(6, question_y - 0.6, 'Current status: DEBATED',
            ha='center', fontsize=9, color='#E74C3C', fontweight='bold')

    plt.tight_layout()
    plt.savefig('/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures/fig2_min_system.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created Figure 2: Min System Hierarchical Integration")

def create_figure3_nucleoid_occlusion():
    """Create Figure 3: Nucleoid Occlusion"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Nucleoid Occlusion: Physical Constraint Translated to Molecular Regulation',
                 fontsize=14, fontweight='bold', y=0.98)

    # Common elements
    nucleoid_color = '#3498DB'  # Blue
    cell_color = '#ECF0F1'      # Light gray
    zring_color = '#E74C3C'     # Red
    blocked_color = '#E74C3C'   # Red
    permitted_color = '#27AE60' # Green

    titles = ['BEFORE SEGREGATION\n(Division blocked)',
              'DURING SEGREGATION\n(Division blocked)',
              'AFTER SEGREGATION\n(Division permitted)']
    statuses = ['Nucleoid blocks midcell\nZ-ring cannot form',
                'Nucleoid blocks midcell\nZ-ring cannot form',
                'Nucleoid segregated\nMidcell available for Z-ring']
    status_colors = [blocked_color, blocked_color, permitted_color]

    for i, ax in enumerate(axes):
        ax.set_xlim(-1, 11)
        ax.set_ylim(-2, 3)
        ax.set_aspect('equal')
        ax.axis('off')

        # Cell boundary
        cell = FancyBboxPatch((0, -1.5), 10, 3,
                               boxstyle="round,pad=0.2",
                               facecolor=cell_color, edgecolor='#2C3E50',
                               linewidth=2)
        ax.add_patch(cell)

        # Poles
        pole_left = Circle((0.3, 0), 0.3, color='#2C3E50', zorder=10)
        pole_right = Circle((9.7, 0), 0.3, color='#2C3E50', zorder=10)
        ax.add_patch(pole_left)
        ax.add_patch(pole_right)

        # Nucleoid (changes position across stages)
        if i == 0:  # Before segregation
            nucleoid = FancyBboxPatch((3, -0.6), 4, 1.2,
                                      boxstyle="round,pad=0.3",
                                      facecolor=nucleoid_color, alpha=0.7,
                                      edgecolor='#2980B9', linewidth=2)
            ax.add_patch(nucleoid)
            ax.text(5, 0, 'DNA', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            # Blocked Z-ring marker
            ax.text(5, -1.3, '╳', ha='center', va='center',
                   fontsize=24, color=blocked_color, fontweight='bold')

        elif i == 1:  # During segregation
            # Two nucleoids
            nuc1 = FancyBboxPatch((2, -0.6), 3, 1.2,
                                   boxstyle="round,pad=0.3",
                                   facecolor=nucleoid_color, alpha=0.7,
                                   edgecolor='#2980B9', linewidth=2)
            nuc2 = FancyBboxPatch((5, -0.6), 3, 1.2,
                                   boxstyle="round,pad=0.3",
                                   facecolor=nucleoid_color, alpha=0.7,
                                   edgecolor='#2980B9', linewidth=2)
            ax.add_patch(nuc1)
            ax.add_patch(nuc2)
            ax.text(3.5, 0, 'DNA', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            ax.text(6.5, 0, 'DNA', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            # Still blocked at center
            ax.text(5, -1.3, '╳', ha='center', va='center',
                   fontsize=24, color=blocked_color, fontweight='bold')

        else:  # After segregation
            # Segregated nucleoids
            nuc1 = FancyBboxPatch((1, -0.6), 2.5, 1.2,
                                   boxstyle="round,pad=0.3",
                                   facecolor=nucleoid_color, alpha=0.7,
                                   edgecolor='#2980B9', linewidth=2)
            nuc2 = FancyBboxPatch((6.5, -0.6), 2.5, 1.2,
                                   boxstyle="round,pad=0.3",
                                   facecolor=nucleoid_color, alpha=0.7,
                                   edgecolor='#2980B9', linewidth=2)
            ax.add_patch(nuc1)
            ax.add_patch(nuc2)
            ax.text(2.25, 0, 'DNA', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            ax.text(7.75, 0, 'DNA', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            # Permitted Z-ring at center
            zring = Rectangle((4.8, -0.2), 0.4, 0.4,
                              facecolor='none', edgecolor=zring_color,
                              linewidth=3, linestyle='-')
            ax.add_patch(zring)
            ax.text(5, -1.3, '✓', ha='center', va='center',
                   fontsize=24, color=permitted_color, fontweight='bold')

        # Stage label
        ax.text(5, 2.2, titles[i], ha='center', fontsize=11, fontweight='bold')
        ax.text(5, -2, statuses[i], ha='center', fontsize=9,
               color=status_colors[i], style='italic')

    # Add molecular sensing explanation at bottom
    fig.text(0.5, 0.02, 'MOLECULAR SENSING & RESPONSE: Physical Constraint (nucleoid at midcell) → '
                        'Molecular Detection (SlmA/Noc/Min) → Functional Outcome (division at proper time/place)',
             ha='center', fontsize=9, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF5E7',
                      edgecolor='#F39C12', linewidth=1))

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures/fig3_nucleoid_occlusion.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Created Figure 3: Nucleoid Occlusion")

if __name__ == '__main__':
    print("=" * 60)
    print("Creating High-Quality PNG Figures")
    print("=" * 60)
    print()

    create_figure1_hierarchical_framework()
    create_figure2_min_system()
    create_figure3_nucleoid_occlusion()

    print()
    print("=" * 60)
    print("All figures created successfully!")
    print("=" * 60)
    print()
    print("Output files:")
    print("  - figures/fig1_hierarchical_framework.png")
    print("  - figures/fig2_min_system.png")
    print("  - figures/fig3_nucleoid_occlusion.png")
