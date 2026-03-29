"""
Explainable AI Module — SHAP-based crop recommendation explanations.
Uses TreeExplainer for the scikit-learn RandomForest crop model.
Generates waterfall plots and feature importance bar charts as base64 PNG.
"""
import io
import base64
import traceback
import numpy as np

try:
    import shap
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend — no GUI needed
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP or matplotlib not installed — explainability unavailable")

FEATURE_NAMES = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)',
                 'Temperature', 'Humidity', 'pH', 'Rainfall']
FEATURE_KEYS  = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']
FEATURE_UNITS = ['ppm', 'ppm', 'ppm', '°C', '%', '', 'mm']
# Green palette
COLOR_POS = '#2e7d32'  # dark green — pushes toward prediction
COLOR_NEG = '#c62828'  # dark red — pushes away from prediction
BG_COLOR  = '#f9fbf7'


def _fig_to_b64(fig) -> str:
    """Convert a matplotlib Figure to a base64-encoded PNG data URI."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_b64}"


def _build_waterfall(shap_vals, base_val, prediction, feature_values):
    """Build a SHAP waterfall chart from raw values (no shap.plots dependency)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    sorted_idx = np.argsort(np.abs(shap_vals))[::-1]
    labels, values, raw_vals = [], [], []
    for i in sorted_idx:
        unit = FEATURE_UNITS[i]
        labels.append(f"{FEATURE_NAMES[i]} = {feature_values[i]:.1f}{' ' + unit if unit else ''}")
        values.append(float(shap_vals[i]))
        raw_vals.append(feature_values[i])

    colors = [COLOR_POS if v >= 0 else COLOR_NEG for v in values]

    y_pos = range(len(values))
    bars = ax.barh(list(y_pos), values, color=colors, height=0.6, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, values):
        x = bar.get_width()
        ax.text(x + (0.005 if x >= 0 else -0.005), bar.get_y() + bar.get_height()/2,
                f"{val:+.3f}", va='center', ha='left' if x >= 0 else 'right',
                fontsize=8.5, color='#333')

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels, fontsize=9)
    ax.axvline(0, color='#888', linewidth=0.8, linestyle='--')
    ax.set_xlabel('SHAP Value (impact on model output)', fontsize=9, color='#555')
    ax.set_title(f'Why "{prediction}" was recommended', fontsize=12, fontweight='bold', color='#1b5e20', pad=12)

    pos_patch = mpatches.Patch(color=COLOR_POS, label='Positive influence')
    neg_patch = mpatches.Patch(color=COLOR_NEG, label='Negative influence')
    ax.legend(handles=[pos_patch, neg_patch], fontsize=8, loc='lower right',
              framealpha=0.7, edgecolor='#ccc')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')
    fig.tight_layout()
    return fig


def _build_importance_bar(shap_vals):
    """Build a mean |SHAP| feature importance bar chart."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    abs_vals = np.abs(shap_vals)
    sorted_idx = np.argsort(abs_vals)
    sorted_names = [FEATURE_NAMES[i] for i in sorted_idx]
    sorted_vals  = abs_vals[sorted_idx]

    gradient_colors = plt.cm.Greens(np.linspace(0.35, 0.85, len(sorted_vals)))
    ax.barh(range(len(sorted_vals)), sorted_vals, color=gradient_colors,
            height=0.6, edgecolor='white', linewidth=0.6)

    ax.set_yticks(range(len(sorted_vals)))
    ax.set_yticklabels(sorted_names, fontsize=9)
    ax.set_xlabel('Mean |SHAP Value| — Feature Importance', fontsize=9, color='#555')
    ax.set_title('Soil & Climate Parameter Influence', fontsize=11, fontweight='bold',
                 color='#1b5e20', pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')
    fig.tight_layout()
    return fig


# ── Public API ───────────────────────────────────────────────────────────────
def explain_crop(model, n, p, k, temperature, humidity, ph, rainfall, prediction: str):
    """
    Generate SHAP explanation for a single crop recommendation.

    Returns dict:
        {
          'success': bool,
          'waterfall_plot': str (base64 data URI) | None,
          'importance_chart': str (base64 data URI) | None,
          'shap_values': list[float],
          'feature_contributions': list[{name, value, shap, unit}],
          'base_value': float,
          'error': str | None
        }
    """
    if not SHAP_AVAILABLE:
        return {'success': False, 'error': 'SHAP/matplotlib not installed', 'waterfall_plot': None,
                'importance_chart': None, 'shap_values': [], 'feature_contributions': []}

    if model is None:
        return {'success': False, 'error': 'Model not loaded', 'waterfall_plot': None,
                'importance_chart': None, 'shap_values': [], 'feature_contributions': []}

    try:
        feature_values = np.array([[n, p, k, temperature, humidity, ph, rainfall]], dtype=float)

        # TreeExplainer works with RandomForest and XGBoost
        explainer = shap.TreeExplainer(model)
        shap_explanation = explainer(feature_values)

        # shap_explanation.values shape: (1, n_features) or (1, n_features, n_classes)
        sv = shap_explanation.values[0]
        if sv.ndim > 1:
            # Multi-class: take the class with highest value (predicted class)
            pred_idx = int(np.argmax(shap_explanation.base_values[0] + sv.sum(axis=0)))
            sv = sv[:, pred_idx]

        base_val = float(np.mean(shap_explanation.base_values))
        shap_vals = sv.astype(float)

        # Build charts
        wf_fig = _build_waterfall(shap_vals, base_val, prediction, feature_values[0])
        bar_fig = _build_importance_bar(shap_vals)

        waterfall_b64  = _fig_to_b64(wf_fig)
        importance_b64 = _fig_to_b64(bar_fig)

        feature_contribs = [
            {
                'name': FEATURE_NAMES[i],
                'raw_value': round(float(feature_values[0][i]), 2),
                'unit': FEATURE_UNITS[i],
                'shap': round(float(shap_vals[i]), 4),
                'influence': 'Positive' if shap_vals[i] >= 0 else 'Negative',
                'pct': round(abs(float(shap_vals[i])) / (np.sum(np.abs(shap_vals)) + 1e-9) * 100, 1),
            }
            for i in range(len(FEATURE_NAMES))
        ]
        # Sort by absolute impact descending
        feature_contribs.sort(key=lambda x: abs(x['shap']), reverse=True)

        return {
            'success': True,
            'waterfall_plot': waterfall_b64,
            'importance_chart': importance_b64,
            'shap_values': shap_vals.tolist(),
            'feature_contributions': feature_contribs,
            'base_value': base_val,
            'error': None,
        }

    except Exception as e:
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'waterfall_plot': None,
            'importance_chart': None,
            'shap_values': [],
            'feature_contributions': [],
        }
