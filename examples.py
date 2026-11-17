"""
Predefined Examples for Mealy to Moore Machine Conversion.
Provides ready-to-load educational test cases covering all edge cases.
"""

from typing import Dict, Any, List
import pandas as pd


PRESET_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "Example 1: Prompt Standard (2 States)": {
        "title": "Prompt Specification Example",
        "description": "Standard 2-state example from the prompt where incoming outputs to each state are uniform (A receives 1s, B receives 0s).",
        "states": ["A", "B"],
        "inputs": ["0", "1"],
        "initial_state": "A",
        "table": [
            {"Present State": "A", "Input": "0", "Next State": "B", "Output": "0"},
            {"Present State": "A", "Input": "1", "Next State": "A", "Output": "1"},
            {"Present State": "B", "Input": "0", "Next State": "A", "Output": "1"},
            {"Present State": "B", "Input": "1", "Next State": "B", "Output": "0"}
        ]
    },
    "Example 2: Textbook State Splitting (3 States)": {
        "title": "Textbook Multi-State Splitting (q0, q1, q2)",
        "description": "Classic textbook problem where states q1 and q2 each receive both 0 and 1 outputs, requiring multiple splits to form q1_0, q1_1, q2_0, and q2_1.",
        "states": ["q0", "q1", "q2"],
        "inputs": ["0", "1"],
        "initial_state": "q0",
        "table": [
            {"Present State": "q0", "Input": "0", "Next State": "q1", "Output": "0"},
            {"Present State": "q0", "Input": "1", "Next State": "q2", "Output": "0"},
            {"Present State": "q1", "Input": "0", "Next State": "q1", "Output": "1"},
            {"Present State": "q1", "Input": "1", "Next State": "q2", "Output": "0"},
            {"Present State": "q2", "Input": "0", "Next State": "q1", "Output": "0"},
            {"Present State": "q2", "Input": "1", "Next State": "q2", "Output": "1"}
        ]
    },
    "Example 3: '101' Sequence Detector (3 States)": {
        "title": "Binary Pattern '101' Sequence Detector",
        "description": "Digital logic circuit model that detects the overlapping sequence '101'. Emits '1' only upon detecting the completed pattern.",
        "states": ["S0", "S1", "S2"],
        "inputs": ["0", "1"],
        "initial_state": "S0",
        "table": [
            {"Present State": "S0", "Input": "0", "Next State": "S0", "Output": "0"},
            {"Present State": "S0", "Input": "1", "Next State": "S1", "Output": "0"},
            {"Present State": "S1", "Input": "0", "Next State": "S2", "Output": "0"},
            {"Present State": "S1", "Input": "1", "Next State": "S1", "Output": "0"},
            {"Present State": "S2", "Input": "0", "Next State": "S0", "Output": "0"},
            {"Present State": "S2", "Input": "1", "Next State": "S1", "Output": "1"}
        ]
    },
    "Example 4: Even/Odd Parity Generator (2 States)": {
        "title": "Even/Odd Parity Generator",
        "description": "Calculates the dynamic parity of '1' bits read so far. Emits 1 when the parity is odd, and 0 when even.",
        "states": ["Even", "Odd"],
        "inputs": ["0", "1"],
        "initial_state": "Even",
        "table": [
            {"Present State": "Even", "Input": "0", "Next State": "Even", "Output": "0"},
            {"Present State": "Even", "Input": "1", "Next State": "Odd", "Output": "1"},
            {"Present State": "Odd", "Input": "0", "Next State": "Odd", "Output": "1"},
            {"Present State": "Odd", "Input": "1", "Next State": "Even", "Output": "0"}
        ]
    },
    "Example 5: Signal Edge Detector (2 States)": {
        "title": "Rising & Falling Signal Edge Detector",
        "description": "Emits 1 on transitions between differing logic levels (0 to 1 and 1 to 0), and 0 when signal stays level.",
        "states": ["Low", "High"],
        "inputs": ["0", "1"],
        "initial_state": "Low",
        "table": [
            {"Present State": "Low", "Input": "0", "Next State": "Low", "Output": "0"},
            {"Present State": "Low", "Input": "1", "Next State": "High", "Output": "1"},
            {"Present State": "High", "Input": "0", "Next State": "Low", "Output": "1"},
            {"Present State": "High", "Input": "1", "Next State": "High", "Output": "0"}
        ]
    }
}


def get_example(key: str) -> Dict[str, Any]:
    """Retrieves an example specification."""
    return PRESET_EXAMPLES.get(key, PRESET_EXAMPLES["Example 1: Prompt Standard (2 States)"])


def get_example_keys() -> List[str]:
    """Returns the list of example titles."""
    return list(PRESET_EXAMPLES.keys())
