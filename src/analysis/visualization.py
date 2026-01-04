"""
Visualization Tools for QKD Analysis.

This module provides visualization utilities for analyzing and
presenting QKD protocol results, including:

- Protocol comparison charts
- QBER vs key rate plots
- Attack impact visualization
- Noise channel effects
- Security metric dashboards

All visualizations are designed to be publication-quality.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import seaborn as sns


class QKDVisualizer:
    """
    Visualization toolkit for QKD protocol analysis.
    
    Provides methods for creating publication-quality figures
    for protocol comparison, security analysis, and more.
    
    Attributes:
        style: Matplotlib style to use
        figsize: Default figure size
        
    Example:
        >>> viz = QKDVisualizer()
        >>> fig = viz.plot_qber_vs_key_rate()
        >>> fig.savefig('results/qber_analysis.pdf')
    """
    
    # Color palette for protocols
    PROTOCOL_COLORS = {
        'BB84': '#2E86AB',
        'B92': '#A23B72',
        'E91': '#F18F01',
        'SARG04': '#C73E1D'
    }
    
    # Color palette for attacks
    ATTACK_COLORS = {
        'Intercept-Resend': '#E63946',
        'PNS': '#457B9D',
        'Trojan Horse': '#2A9D8F'
    }
    
    def __init__(
        self,
        style: str = 'seaborn-v0_8-whitegrid',
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = 150
    ):
        """
        Initialize visualizer.
        
        Args:
            style: Matplotlib style
            figsize: Default figure size (width, height)
            dpi: Resolution for saved figures
        """
        self.style = style
        self.figsize = figsize
        self.dpi = dpi
        
        # Set style
        try:
            plt.style.use(style)
        except:
            plt.style.use('seaborn-v0_8-whitegrid')
        
        # Set font sizes
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10
        })
    
    def plot_qber_vs_key_rate(
        self,
        protocols: List[str] = None,
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Plot theoretical QBER vs secret key rate for multiple protocols.
        
        Args:
            protocols: List of protocol names to include
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        if protocols is None:
            protocols = ['BB84', 'B92', 'SARG04']
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        qber_range = np.linspace(0, 0.15, 100)
        
        for protocol in protocols:
            if protocol == 'BB84':
                sifting = 0.5
            elif protocol == 'B92':
                sifting = 0.25
            elif protocol == 'SARG04':
                sifting = 0.25
            else:
                sifting = 0.5
            
            # Calculate key rate
            key_rates = []
            for q in qber_range:
                if q >= 0.11:
                    rate = 0
                elif q == 0:
                    rate = sifting
                else:
                    h = -q * np.log2(q) - (1-q) * np.log2(1-q)
                    rate = sifting * max(0, 1 - 2*h)
                key_rates.append(rate)
            
            color = self.PROTOCOL_COLORS.get(protocol, '#333333')
            ax.plot(qber_range * 100, key_rates, 
                   label=protocol, color=color, linewidth=2)
        
        # Add security threshold
        ax.axvline(x=11, color='red', linestyle='--', alpha=0.7, 
                   label='Security threshold (11%)')
        
        ax.set_xlabel('Quantum Bit Error Rate (%)')
        ax.set_ylabel('Secret Key Rate (bits/transmitted qubit)')
        ax.set_title('QKD Protocol Comparison: QBER vs Key Rate')
        ax.legend(loc='upper right')
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 0.55)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_attack_comparison(
        self,
        attack_results: Dict[str, Dict[str, float]],
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Compare different attacks on a protocol.
        
        Args:
            attack_results: Dict mapping attack names to metrics
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(1, 3, figsize=(14, 5))
        
        attacks = list(attack_results.keys())
        colors = [self.ATTACK_COLORS.get(a, '#333333') for a in attacks]
        
        # QBER induced
        qbers = [attack_results[a].get('induced_qber', 0) * 100 for a in attacks]
        axes[0].barh(attacks, qbers, color=colors)
        axes[0].set_xlabel('Induced QBER (%)')
        axes[0].set_title('Error Rate Impact')
        axes[0].set_xlim(0, max(qbers) * 1.2 if max(qbers) > 0 else 30)
        
        # Information gained
        info = [attack_results[a].get('eve_information', 0) for a in attacks]
        axes[1].barh(attacks, info, color=colors)
        axes[1].set_xlabel('Information Gained (bits)')
        axes[1].set_title('Information Leakage')
        
        # Detection probability
        detect = [attack_results[a].get('detection_probability', 0) * 100 for a in attacks]
        axes[2].barh(attacks, detect, color=colors)
        axes[2].set_xlabel('Detection Probability (%)')
        axes[2].set_title('Detectability')
        axes[2].set_xlim(0, 105)
        
        plt.suptitle('Attack Comparison Analysis', fontsize=14, y=1.02)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_noise_analysis(
        self,
        distances: np.ndarray,
        qbers: np.ndarray,
        key_rates: np.ndarray,
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Plot QBER and key rate vs transmission distance.
        
        Args:
            distances: Array of distances in km
            qbers: Array of QBER values
            key_rates: Array of key rates
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax1 = plt.subplots(figsize=self.figsize)
        
        color1 = '#2E86AB'
        ax1.set_xlabel('Distance (km)')
        ax1.set_ylabel('QBER (%)', color=color1)
        ax1.plot(distances, qbers * 100, color=color1, linewidth=2, label='QBER')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.axhline(y=11, color='red', linestyle='--', alpha=0.7)
        ax1.set_ylim(0, 15)
        
        ax2 = ax1.twinx()
        color2 = '#F18F01'
        ax2.set_ylabel('Key Rate (bits/s)', color=color2)
        ax2.plot(distances, key_rates, color=color2, linewidth=2, label='Key Rate')
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_yscale('log')
        
        ax1.set_title('QKD Performance vs Transmission Distance')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_protocol_comparison_radar(
        self,
        protocol_metrics: Dict[str, Dict[str, float]],
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Create radar chart comparing protocol characteristics.
        
        Args:
            protocol_metrics: Dict mapping protocols to metric dicts
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        categories = ['Sifting Efficiency', 'Noise Resilience', 
                     'Implementation Simplicity', 'PNS Resistance',
                     'Key Rate', 'Security Proof Strength']
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop
        
        for protocol, metrics in protocol_metrics.items():
            values = [metrics.get(cat, 0.5) for cat in categories]
            values += values[:1]  # Complete the loop
            
            color = self.PROTOCOL_COLORS.get(protocol, '#333333')
            ax.plot(angles, values, 'o-', linewidth=2, label=protocol, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
        ax.set_title('Protocol Comparison', y=1.08)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_key_distribution_histogram(
        self,
        alice_key: np.ndarray,
        bob_key: np.ndarray,
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Plot bit distribution histograms for Alice and Bob's keys.
        
        Args:
            alice_key: Alice's key bits
            bob_key: Bob's key bits
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        
        # Alice's key distribution
        axes[0].hist(alice_key, bins=[-0.5, 0.5, 1.5], 
                    color=self.PROTOCOL_COLORS['BB84'], alpha=0.7,
                    edgecolor='black', rwidth=0.8)
        axes[0].set_xticks([0, 1])
        axes[0].set_xlabel('Bit Value')
        axes[0].set_ylabel('Count')
        axes[0].set_title("Alice's Key Distribution")
        
        # Bob's key distribution
        axes[1].hist(bob_key, bins=[-0.5, 0.5, 1.5],
                    color=self.PROTOCOL_COLORS['E91'], alpha=0.7,
                    edgecolor='black', rwidth=0.8)
        axes[1].set_xticks([0, 1])
        axes[1].set_xlabel('Bit Value')
        axes[1].set_ylabel('Count')
        axes[1].set_title("Bob's Key Distribution")
        
        # Error positions
        errors = alice_key != bob_key
        error_positions = np.where(errors)[0]
        
        axes[2].scatter(error_positions, np.ones_like(error_positions),
                       c='red', alpha=0.5, s=10)
        axes[2].set_xlabel('Bit Position')
        axes[2].set_ylabel('')
        axes[2].set_title(f'Error Positions (QBER: {100*np.mean(errors):.2f}%)')
        axes[2].set_yticks([])
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def plot_bell_inequality(
        self,
        measurements: Dict[Tuple[int, int], List[int]],
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize Bell inequality test results for E91.
        
        Args:
            measurements: Dict mapping (alice_basis, bob_basis) to outcomes
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Correlation matrix
        corr_matrix = np.zeros((3, 3))
        for (a, b), outcomes in measurements.items():
            if len(outcomes) > 0:
                corr_matrix[a, b] = np.mean([2*o - 1 for o in outcomes])
        
        sns.heatmap(corr_matrix, ax=axes[0], annot=True, fmt='.2f',
                   cmap='RdBu_r', vmin=-1, vmax=1,
                   xticklabels=['B1 (45°)', 'B2 (90°)', 'B3 (135°)'],
                   yticklabels=['A1 (0°)', 'A2 (45°)', 'A3 (90°)'])
        axes[0].set_title('Correlation Matrix E(a,b)')
        axes[0].set_xlabel("Bob's Basis")
        axes[0].set_ylabel("Alice's Basis")
        
        # CHSH value
        S_values = [2.0]  # Classical limit
        S_values.append(2.82)  # Quantum maximum
        
        # Calculate actual S from measurements
        E = lambda a, b: corr_matrix[a, b]
        S_actual = abs(E(0, 0) - E(0, 1) + E(1, 0) + E(1, 1))
        S_values.append(S_actual)
        
        bars = axes[1].bar(['Classical\nLimit', 'Quantum\nMaximum', 'Measured'],
                          S_values, color=['gray', 'blue', 'green'])
        axes[1].axhline(y=2, color='red', linestyle='--', label='Bell limit')
        axes[1].set_ylabel('CHSH Parameter S')
        axes[1].set_title('Bell Inequality Test')
        axes[1].set_ylim(0, 3)
        axes[1].legend()
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def create_security_dashboard(
        self,
        metrics: Dict[str, Any],
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Create a comprehensive security metrics dashboard.
        
        Args:
            metrics: Dictionary of security metrics
            save_path: Optional path to save figure
            
        Returns:
            Matplotlib Figure object
        """
        fig = plt.figure(figsize=(14, 10))
        
        # Layout: 2x3 grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. QBER gauge
        ax1 = fig.add_subplot(gs[0, 0])
        qber = metrics.get('qber', 0) * 100
        self._plot_gauge(ax1, qber, 'QBER (%)', max_val=15, 
                        threshold=11, good_below=True)
        
        # 2. Key rate gauge
        ax2 = fig.add_subplot(gs[0, 1])
        key_rate = metrics.get('key_rate', 0) * 100
        self._plot_gauge(ax2, key_rate, 'Key Rate (%)', max_val=50,
                        threshold=10, good_below=False)
        
        # 3. Security status
        ax3 = fig.add_subplot(gs[0, 2])
        is_secure = metrics.get('is_secure', False)
        color = '#2ECC71' if is_secure else '#E74C3C'
        ax3.add_patch(plt.Circle((0.5, 0.5), 0.4, color=color))
        ax3.text(0.5, 0.5, 'SECURE' if is_secure else 'INSECURE',
                ha='center', va='center', fontsize=14, color='white',
                fontweight='bold')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis('off')
        ax3.set_title('Security Status')
        
        # 4. Key length breakdown
        ax4 = fig.add_subplot(gs[1, 0])
        lengths = [
            metrics.get('raw_key_length', 0),
            metrics.get('sifted_key_length', 0),
            metrics.get('final_key_length', 0)
        ]
        bars = ax4.bar(['Raw', 'Sifted', 'Final'], lengths,
                      color=['#3498DB', '#2ECC71', '#9B59B6'])
        ax4.set_ylabel('Key Length (bits)')
        ax4.set_title('Key Length Progression')
        
        # 5. Information diagram
        ax5 = fig.add_subplot(gs[1, 1])
        iab = metrics.get('mutual_info_ab', 0.8)
        iae = metrics.get('mutual_info_ae', 0.2)
        ax5.bar(['I(A:B)', 'I(A:E)'], [iab, iae],
               color=['#2ECC71', '#E74C3C'])
        ax5.set_ylabel('Mutual Information (bits)')
        ax5.set_title('Information Analysis')
        ax5.set_ylim(0, 1.1)
        
        # 6. Summary text
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')
        summary_text = (
            f"Protocol: {metrics.get('protocol', 'BB84')}\n"
            f"Raw bits: {metrics.get('raw_key_length', 0):,}\n"
            f"Sifted bits: {metrics.get('sifted_key_length', 0):,}\n"
            f"Final key: {metrics.get('final_key_length', 0):,}\n"
            f"QBER: {metrics.get('qber', 0)*100:.2f}%\n"
            f"Security margin: {metrics.get('security_margin', 0)*100:.2f}%"
        )
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
                fontsize=12, verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax6.set_title('Summary')
        
        plt.suptitle('QKD Security Dashboard', fontsize=16, y=0.98)
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig
    
    def _plot_gauge(
        self,
        ax,
        value: float,
        label: str,
        max_val: float = 100,
        threshold: float = None,
        good_below: bool = True
    ):
        """Helper to plot a gauge chart."""
        # Determine color based on threshold
        if threshold is not None:
            if good_below:
                color = '#2ECC71' if value < threshold else '#E74C3C'
            else:
                color = '#2ECC71' if value > threshold else '#E74C3C'
        else:
            color = '#3498DB'
        
        # Draw arc
        theta1, theta2 = 180, 0
        wedge = mpatches.Wedge((0.5, 0), 0.4, theta1, theta2, 
                               facecolor='#EEEEEE', edgecolor='black')
        ax.add_patch(wedge)
        
        # Draw value arc
        value_angle = 180 - (value / max_val) * 180
        value_wedge = mpatches.Wedge((0.5, 0), 0.4, value_angle, 180,
                                     facecolor=color, edgecolor='black')
        ax.add_patch(value_wedge)
        
        # Add text
        ax.text(0.5, 0.1, f'{value:.1f}', ha='center', va='center',
               fontsize=20, fontweight='bold')
        ax.text(0.5, -0.15, label, ha='center', va='center', fontsize=12)
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.3, 0.5)
        ax.axis('off')
