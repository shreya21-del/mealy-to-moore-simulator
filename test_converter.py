"""
Test script for Mealy to Moore Machine Conversion Logic.
"""
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional

@dataclass
class MealyTransition:
    present_state: str
    input_symbol: str
    next_state: str
    output_symbol: str

@dataclass
class MooreTransition:
    present_state: str
    input_symbol: str
    next_state: str

class MealyToMooreConverter:
    def __init__(
        self,
        states: List[str],
        inputs: List[str],
        initial_state: str,
        transitions: List[MealyTransition],
        initial_state_policy: str = "auto"  # "auto", "always_new", "preserve"
    ):
        self.states = [s.strip() for s in states]
        self.inputs = [str(i).strip() for i in inputs]
        self.initial_state = initial_state.strip()
        self.transitions = transitions
        self.initial_state_policy = initial_state_policy

    def convert(self):
        # 1. Map incoming transitions for each state
        incoming_outputs: Dict[str, Set[str]] = {s: set() for s in self.states}
        incoming_details: Dict[str, List[Dict[str, str]]] = {s: [] for s in self.states}

        for t in self.transitions:
            incoming_outputs[t.next_state].add(t.output_symbol)
            incoming_details[t.next_state].append({
                "from_state": t.present_state,
                "input": t.input_symbol,
                "output": t.output_symbol
            })

        # 2. Identify state splits and create Moore states
        # Each Moore state has a name, base_state, and state_output
        moore_states: Dict[str, Dict[str, str]] = {}
        split_explanations: List[Dict] = []
        state_to_moore_states: Dict[str, List[str]] = {s: [] for s in self.states}

        # Check if initial state needs a special start state
        init_incoming = incoming_outputs.get(self.initial_state, set())
        needs_start_state = False
        if self.initial_state_policy == "always_new":
            needs_start_state = True
        elif self.initial_state_policy == "auto":
            # If initial state has incoming transitions, or if incoming transitions have >1 outputs
            # Having a dedicated start state guarantees zero initial-transition ambiguity
            if len(init_incoming) > 0:
                needs_start_state = True
        elif self.initial_state_policy == "preserve":
            needs_start_state = False

        # Create split states for all states based on incoming outputs
        for s in self.states:
            outputs = sorted(list(incoming_outputs[s]))
            if len(outputs) == 0:
                # No incoming transitions
                # If it's the initial state and no start state needed, assign default output (e.g. '-' or '0')
                m_state_name = f"{s}_init" if needs_start_state else s
                out_val = "-"
                moore_states[m_state_name] = {
                    "base_state": s,
                    "output": out_val,
                    "is_initial": (s == self.initial_state)
                }
                state_to_moore_states[s].append(m_state_name)
                split_explanations.append({
                    "state": s,
                    "incoming_outputs": [],
                    "action": "No incoming transitions. Retained as single state.",
                    "split_states": [m_state_name]
                })
            elif len(outputs) == 1:
                # Single incoming output
                out_val = outputs[0]
                m_state_name = f"{s}_{out_val}"
                moore_states[m_state_name] = {
                    "base_state": s,
                    "output": out_val,
                    "is_initial": False
                }
                state_to_moore_states[s].append(m_state_name)
                split_explanations.append({
                    "state": s,
                    "incoming_outputs": outputs,
                    "action": f"Single incoming output '{out_val}'. Mapped to state '{m_state_name}' with output '{out_val}'.",
                    "split_states": [m_state_name]
                })
            else:
                # Multiple incoming outputs: SPLIT REQUIRED
                m_names = []
                for out_val in outputs:
                    m_state_name = f"{s}_{out_val}"
                    moore_states[m_state_name] = {
                        "base_state": s,
                        "output": out_val,
                        "is_initial": False
                    }
                    m_names.append(m_state_name)
                    state_to_moore_states[s].append(m_state_name)
                split_explanations.append({
                    "state": s,
                    "incoming_outputs": outputs,
                    "action": f"Conflicting incoming outputs {outputs}. Split into {len(outputs)} states: {', '.join(m_names)}.",
                    "split_states": m_names
                })

        # Handle Initial Moore State
        if needs_start_state:
            start_state_name = f"{self.initial_state}_start"
            # Start state output is conventionally '-' (undefined/dummy at t=0) or '0'
            moore_states[start_state_name] = {
                "base_state": self.initial_state,
                "output": "-",
                "is_initial": True
            }
            moore_initial_state = start_state_name
        else:
            # If no special start state, pick the initial state corresponding to self.initial_state
            # If it split, pick the one or default
            possible_inits = state_to_moore_states[self.initial_state]
            moore_initial_state = possible_inits[0]
            moore_states[moore_initial_state]["is_initial"] = True

        # 3. Build Moore Transitions
        # Fast lookup for Mealy transition: (from_state, input_symbol) -> (next_state, output_symbol)
        mealy_lookup: Dict[Tuple[str, str], Tuple[str, str]] = {}
        for t in self.transitions:
            mealy_lookup[(t.present_state, t.input_symbol)] = (t.next_state, t.output_symbol)

        moore_transitions: List[MooreTransition] = []
        moore_table_rows = []

        for m_state, m_info in moore_states.items():
            base_s = m_info["base_state"]
            row = {
                "Moore State": m_state,
                "Base State": base_s,
                "Output": m_info["output"],
                "Is Initial": "Yes" if m_state == moore_initial_state else "No"
            }

            for inp in self.inputs:
                if (base_s, inp) in mealy_lookup:
                    next_base, out_sym = mealy_lookup[(base_s, inp)]
                    target_moore_state = f"{next_base}_{out_sym}"
                    # Verify target state exists in moore_states
                    if target_moore_state not in moore_states:
                        # Fallback if next_base had no incoming transitions or was named differently
                        target_moore_state = state_to_moore_states[next_base][0]

                    moore_transitions.append(MooreTransition(
                        present_state=m_state,
                        input_symbol=inp,
                        next_state=target_moore_state
                    ))
                    row[f"Next State (Input {inp})"] = target_moore_state
                else:
                    row[f"Next State (Input {inp})"] = "-"

            moore_table_rows.append(row)

        return {
            "moore_states": moore_states,
            "moore_initial_state": moore_initial_state,
            "incoming_outputs": incoming_outputs,
            "incoming_details": incoming_details,
            "split_explanations": split_explanations,
            "moore_transitions": moore_transitions,
            "moore_table_rows": moore_table_rows,
            "needs_start_state": needs_start_state
        }

if __name__ == "__main__":
    # Test example 1: The example from user prompt
    transitions = [
        MealyTransition("A", "0", "B", "0"),
        MealyTransition("A", "1", "A", "1"),
        MealyTransition("B", "0", "A", "1"),
        MealyTransition("B", "1", "B", "0"),
    ]
    conv = MealyToMooreConverter(["A", "B"], ["0", "1"], "A", transitions, "auto")
    res = conv.convert()
    print("Example 1 (Prompt):")
    print("Moore Initial State:", res["moore_initial_state"])
    for r in res["moore_table_rows"]:
        print(r)

    # Test example 2: State splitting required
    transitions2 = [
        MealyTransition("q0", "0", "q1", "0"),
        MealyTransition("q0", "1", "q2", "0"),
        MealyTransition("q1", "0", "q1", "1"),
        MealyTransition("q1", "1", "q2", "0"),
        MealyTransition("q2", "0", "q1", "0"),
        MealyTransition("q2", "1", "q2", "1"),
    ]
    conv2 = MealyToMooreConverter(["q0", "q1", "q2"], ["0", "1"], "q0", transitions2, "auto")
    res2 = conv2.convert()
    print("\nExample 2 (Split States):")
    print("Moore Initial State:", res2["moore_initial_state"])
    for r in res2["moore_table_rows"]:
        print(r)
