"""
Graphviz State Diagram Visualizer for Mealy and Moore Machines.
Produces publication-quality, interactive state transition diagrams.
"""

from typing import Dict, List, Optional
import graphviz
from converter import MealyMachine, MealyTransition, MooreState, MooreTransition


THEMES = {
    "Indigo / Teal (Default Modern)": {
        "mealy_node_bg": "#EEF2FF",
        "mealy_node_border": "#4F46E5",
        "mealy_init_bg": "#E0E7FF",
        "mealy_edge": "#334155",
        "moore_node_bg": "#ECFDF5",
        "moore_node_border": "#059669",
        "moore_init_bg": "#FEF3C7",
        "moore_init_border": "#D97706",
        "moore_edge": "#334155",
        "font": "Helvetica, Arial, sans-serif"
    },
    "Ocean Blue & Purple": {
        "mealy_node_bg": "#E0F2FE",
        "mealy_node_border": "#0284C7",
        "mealy_init_bg": "#BAE6FD",
        "mealy_edge": "#1E293B",
        "moore_node_bg": "#F3E8FF",
        "moore_node_border": "#7C3AED",
        "moore_init_bg": "#FDE68A",
        "moore_init_border": "#B45309",
        "moore_edge": "#1E293B",
        "font": "Helvetica, Arial, sans-serif"
    },
    "High Contrast (Dark/Light Neutral)": {
        "mealy_node_bg": "#FFFFFF",
        "mealy_node_border": "#1E293B",
        "mealy_init_bg": "#F1F5F9",
        "mealy_edge": "#0F172A",
        "moore_node_bg": "#FFFFFF",
        "moore_node_border": "#0F172A",
        "moore_init_bg": "#FEF08A",
        "moore_init_border": "#854D0E",
        "moore_edge": "#0F172A",
        "font": "Courier, monospace"
    }
}


def create_mealy_graph(
    mealy: MealyMachine,
    direction: str = "LR",
    theme_name: str = "Indigo / Teal (Default Modern)",
    merge_parallel_edges: bool = True
) -> graphviz.Digraph:
    """
    Creates a Graphviz Digraph for a Mealy Machine.
    - Circular states.
    - Arrows with 'Input / Output' labels.
    - Start pointer to the initial state.
    """
    theme = THEMES.get(theme_name, THEMES["Indigo / Teal (Default Modern)"])
    dot = graphviz.Digraph(name="MealyMachine", comment="Mealy State Diagram")

    dot.attr(
        rankdir=direction,
        bgcolor="transparent",
        splines="true",
        overlap="false"
    )

    dot.attr(
        "node",
        shape="circle",
        style="filled",
        fontname=theme["font"],
        fontsize="12",
        penwidth="1.8",
        fixedsize="true",
        width="0.8",
        height="0.8"
    )

    dot.attr(
        "edge",
        fontname=theme["font"],
        fontsize="11",
        color=theme["mealy_edge"],
        fontcolor=theme["mealy_edge"],
        arrowsize="0.8",
        penwidth="1.2"
    )

    # Invisible start anchor node
    dot.node("__start_mealy", shape="point", style="invis", width="0", height="0")
    dot.edge("__start_mealy", mealy.initial_state, label=" start", color=theme["mealy_node_border"], penwidth="1.8")

    # Add states
    for state in mealy.states:
        is_init = (state == mealy.initial_state)
        bg = theme["mealy_init_bg"] if is_init else theme["mealy_node_bg"]
        dot.node(
            state,
            label=state,
            fillcolor=bg,
            color=theme["mealy_node_border"],
            fontcolor="#0F172A"
        )

    # Transitions
    if merge_parallel_edges:
        # Group by (present_state, next_state)
        edge_groups: Dict[tuple, List[str]] = {}
        for t in mealy.transitions:
            key = (t.present_state, t.next_state)
            if key not in edge_groups:
                edge_groups[key] = []
            edge_groups[key].append(f"{t.input_symbol} / {t.output_symbol}")

        for (u, v), labels in edge_groups.items():
            label_text = "\n".join(labels)
            dot.edge(u, v, label=f" {label_text} ")
    else:
        for t in mealy.transitions:
            dot.edge(t.present_state, t.next_state, label=f" {t.input_symbol} / {t.output_symbol} ")

    return dot


def create_moore_graph(
    moore_states: Dict[str, MooreState],
    moore_initial_state: str,
    moore_transitions: List[MooreTransition],
    direction: str = "LR",
    theme_name: str = "Indigo / Teal (Default Modern)",
    merge_parallel_edges: bool = True
) -> graphviz.Digraph:
    """
    Creates a Graphviz Digraph for a Moore Machine.
    - Circular states with Output shown inside: e.g. "State\n(Out: Y)".
    - Arrows labeled with Input symbols.
    - Start pointer to the initial Moore state.
    """
    theme = THEMES.get(theme_name, THEMES["Indigo / Teal (Default Modern)"])
    dot = graphviz.Digraph(name="MooreMachine", comment="Moore State Diagram")

    dot.attr(
        rankdir=direction,
        bgcolor="transparent",
        splines="true",
        overlap="false"
    )

    dot.attr(
        "node",
        shape="circle",
        style="filled",
        fontname=theme["font"],
        fontsize="11",
        penwidth="1.8",
        fixedsize="true",
        width="1.05",
        height="1.05"
    )

    dot.attr(
        "edge",
        fontname=theme["font"],
        fontsize="11",
        color=theme["moore_edge"],
        fontcolor=theme["moore_edge"],
        arrowsize="0.8",
        penwidth="1.2"
    )

    # Invisible start anchor node
    dot.node("__start_moore", shape="point", style="invis", width="0", height="0")
    start_border = theme["moore_init_border"] if moore_states[moore_initial_state].is_initial else theme["moore_node_border"]
    dot.edge("__start_moore", moore_initial_state, label=" start", color=start_border, penwidth="1.8")

    # Add states
    for state_name, m_state in moore_states.items():
        is_init = (state_name == moore_initial_state)
        bg = theme["moore_init_bg"] if is_init else theme["moore_node_bg"]
        border = theme["moore_init_border"] if is_init else theme["moore_node_border"]

        # Label inside circle: State name on line 1, Output on line 2
        label = f"{state_name}\n[y = {m_state.output}]"

        dot.node(
            state_name,
            label=label,
            fillcolor=bg,
            color=border,
            fontcolor="#0F172A",
            penwidth="2.2" if is_init else "1.8"
        )

    # Transitions
    if merge_parallel_edges:
        edge_groups: Dict[tuple, List[str]] = {}
        for t in moore_transitions:
            key = (t.present_state, t.next_state)
            if key not in edge_groups:
                edge_groups[key] = []
            edge_groups[key].append(str(t.input_symbol))

        for (u, v), inputs in edge_groups.items():
            label_text = ", ".join(inputs)
            dot.edge(u, v, label=f" {label_text} ")
    else:
        for t in moore_transitions:
            dot.edge(t.present_state, t.next_state, label=f" {t.input_symbol} ")

    return dot
