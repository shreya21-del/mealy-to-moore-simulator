"""
Interactive Execution Simulator for Mealy and Moore Machines.
Executes an arbitrary input sequence synchronously on both machines and validates equivalence.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
from converter import MealyMachine, MooreState, MooreTransition


class MachineSimulator:
    def __init__(
        self,
        mealy: MealyMachine,
        moore_states: Dict[str, MooreState],
        moore_initial_state: str,
        moore_transitions: List[MooreTransition]
    ):
        self.mealy = mealy
        self.moore_states = moore_states
        self.moore_initial_state = moore_initial_state
        self.moore_transitions = moore_transitions

        # Quick lookup for Mealy: (current_state, input_symbol) -> (next_state, output_symbol)
        self.mealy_delta: Dict[Tuple[str, str], Tuple[str, str]] = {
            (t.present_state, t.input_symbol): (t.next_state, t.output_symbol)
            for t in self.mealy.transitions
        }

        # Quick lookup for Moore: (current_state, input_symbol) -> next_state
        self.moore_delta: Dict[Tuple[str, str], str] = {
            (t.present_state, t.input_symbol): t.next_state
            for t in self.moore_transitions
        }

    def simulate(self, input_string: str) -> Dict[str, Any]:
        """
        Runs the input string through both machines.
        """
        # Clean and parse symbols
        raw = input_string.strip()
        if not raw:
            return {
                "success": False,
                "error": "Input string is empty. Please provide at least one input symbol."
            }

        # Determine symbols: support space/comma-delimited or single-char string
        if " " in raw:
            symbols = [s.strip() for s in raw.split(" ") if s.strip()]
        elif "," in raw:
            symbols = [s.strip() for s in raw.split(",") if s.strip()]
        else:
            symbols = list(raw)

        # Validate that all symbols belong to the input alphabet
        valid_inputs = set(self.mealy.inputs)
        invalid_symbols = [s for s in symbols if s not in valid_inputs]
        if invalid_symbols:
            return {
                "success": False,
                "error": f"Invalid symbols detected: {set(invalid_symbols)}. Expected symbols from alphabet: {sorted(list(valid_inputs))}."
            }

        # Trace Mealy Machine
        mealy_curr = self.mealy.initial_state
        mealy_trace = []
        mealy_output_seq = []

        # Step 0 (Before any input)
        mealy_trace.append({
            "Step": 0,
            "Input Symbol": "— (Initial)",
            "Mealy State": mealy_curr,
            "Mealy Output": "—",
            "Mealy Next": "—"
        })

        for idx, sym in enumerate(symbols):
            if (mealy_curr, sym) not in self.mealy_delta:
                return {
                    "success": False,
                    "error": f"Mealy Machine has no transition defined from state '{mealy_curr}' on input '{sym}'."
                }
            next_state, out_sym = self.mealy_delta[(mealy_curr, sym)]
            mealy_output_seq.append(out_sym)
            mealy_trace.append({
                "Step": idx + 1,
                "Input Symbol": sym,
                "Mealy State": mealy_curr,
                "Mealy Output": out_sym,
                "Mealy Next": next_state
            })
            mealy_curr = next_state

        # Trace Moore Machine
        moore_curr = self.moore_initial_state
        moore_trace = []
        moore_output_seq = []

        # Step 0 (Initial state has an initial output)
        init_output = self.moore_states[moore_curr].output
        moore_output_seq.append(init_output)
        moore_trace.append({
            "Step": 0,
            "Input Symbol": "— (Initial)",
            "Moore State": moore_curr,
            "Moore Output": init_output,
            "Moore Next": "—"
        })

        for idx, sym in enumerate(symbols):
            if (moore_curr, sym) not in self.moore_delta:
                return {
                    "success": False,
                    "error": f"Moore Machine has no transition defined from state '{moore_curr}' on input '{sym}'."
                }
            next_moore = self.moore_delta[(moore_curr, sym)]
            next_output = self.moore_states[next_moore].output
            moore_output_seq.append(next_output)
            moore_trace.append({
                "Step": idx + 1,
                "Input Symbol": sym,
                "Moore State": moore_curr,
                "Moore Output": next_output,
                "Moore Next": next_moore
            })
            moore_curr = next_moore

        # Build Combined Side-by-Side Comparison DataFrame
        combined_rows = []
        for i in range(len(symbols) + 1):
            m_row = mealy_trace[i]
            mo_row = moore_trace[i]
            combined_rows.append({
                "Step": i,
                "Input": m_row["Input Symbol"],
                "Mealy State": m_row["Mealy State"],
                "Mealy Output": m_row["Mealy Output"],
                "Mealy Next": m_row["Mealy Next"],
                "Moore State": mo_row["Moore State"],
                "Moore Output": mo_row["Moore Output"],
                "Moore Next": mo_row["Moore Next"]
            })

        # Equivalence Check:
        # Ignore Moore's 0-th output. The remaining outputs (1..k) must equal Mealy's outputs (0..k-1).
        moore_trimmed = moore_output_seq[1:]
        is_equivalent = (mealy_output_seq == moore_trimmed)

        return {
            "success": True,
            "symbols": symbols,
            "mealy_outputs": "".join(mealy_output_seq),
            "moore_outputs": "".join(moore_output_seq),
            "moore_initial_output": init_output,
            "is_equivalent": is_equivalent,
            "trace_df": pd.DataFrame(combined_rows)
        }
