"""
Custom CSS Styles and UI Enhancement Components for Streamlit.
Supports clean typography, responsive cards, state badges, and seamless dark/light modes.
"""

CUSTOM_CSS = """
<style>
/* Global aesthetics */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, kbd, samp, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hero Header Banner */
.hero-header {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 50%, #06b6d4 100%);
    padding: 2.2rem 2.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.8rem;
    box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25), 0 8px 10px -6px rgba(79, 70, 229, 0.2);
    position: relative;
    overflow: hidden;
}

.hero-header::after {
    content: "";
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.025em;
    color: #ffffff !important;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 0.6rem;
    color: rgba(255, 255, 255, 0.92);
    max-width: 800px;
    line-height: 1.5;
}

.hero-badges {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(8px);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Card Containers */
.custom-card {
    background-color: var(--background-color, rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.custom-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08);
}

.card-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: inherit;
}

/* Theory Comparison Box */
.compare-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
    margin: 1rem 0;
}

@media (max-width: 768px) {
    .compare-container {
        grid-template-columns: 1fr;
    }
}

.compare-box {
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    background: rgba(248, 250, 252, 0.03);
}

.compare-box.mealy {
    border-left: 4px solid #4f46e5;
}

.compare-box.moore {
    border-left: 4px solid #059669;
}

/* Stat badges */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
}

.stat-pill.blue {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.stat-pill.green {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.stat-pill.amber {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Step Accordion / Box */
.step-card {
    border-left: 4px solid #6366f1;
    background: rgba(99, 102, 241, 0.04);
    padding: 1.2rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 1rem;
}

.step-num {
    display: inline-block;
    width: 26px;
    height: 26px;
    line-height: 26px;
    border-radius: 50%;
    background: #6366f1;
    color: white;
    text-align: center;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 0.5rem;
}

/* Simulator trace highlighting */
.trace-highlight {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.06);
    display: inline-block;
    letter-spacing: 0.1em;
}

/* Diagram frame */
.diagram-frame {
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 12px;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    text-align: center;
}

/* Small footer */
.app-footer {
    text-align: center;
    margin-top: 3rem;
    padding: 1.5rem 0;
    font-size: 0.85rem;
    color: #64748b;
    border-top: 1px solid rgba(148, 163, 184, 0.2);
}
</style>
"""


def render_header():
    """Renders the styled hero header banner."""
    return """
    <div class="hero-header">
        <div class="hero-title">
            <span>⚙️</span> Mealy to Moore Machine Converter
        </div>
        <div class="hero-subtitle">
            An interactive educational platform to configure, mathematically convert, visualize, 
            and simulate Finite State Machines with state-splitting algorithms and real-time Graphviz diagrams.
        </div>
        <div class="hero-badges">
            <span class="hero-badge">⚡ Deterministic FSM</span>
            <span class="hero-badge">🔄 Exact State-Splitting Algorithm</span>
            <span class="hero-badge">📊 Side-by-Side Graphviz</span>
            <span class="hero-badge">🧪 Step-by-Step Execution Simulator</span>
            <span class="hero-badge">📥 CSV & DOT Export</span>
        </div>
    </div>
    """


def render_footer():
    """Renders the styled footer."""
    return """
    <div class="app-footer">
        <strong>Mealy to Moore Machine Converter</strong> • Formal Language & Automata Theory Suite<br/>
        Built with Streamlit, Graphviz, and Pandas • Designed for Students, Researchers, and Digital Logic Designers
    </div>
    """
