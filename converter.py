"""
Core Conversion Logic from Mealy Machine to Moore Machine.
Mathematically sound, robust, and supports various state-splitting scenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
import pandas as pd


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


@dataclass
class MooreState:
    name: str
    base_state: str
    output: str
    is_initial: bool = False
    incoming_sources: List[str] = field(default_factory=list)


class MealyMachine:
    def __init__(
        self,
        states: List[str],
        inputs: List[str],
        initial_state: str,
        transitions: List[MealyTransition]
    ):
        self.states = [str(s).strip() for s in states if str(s).strip()]
        self.inputs = [str(i).strip() for i in inputs if str(i).strip()]
        self.initial_state = str(initial_state).strip()
        self.transitions = transitions

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validates the Mealy machine specification.
        Returns: (is_valid, list_of_errors, list_of_warnings)
        """
        errors = []
        warnings = []

        if not self.states:
            errors.append("States list cannot be empty.")
        if len(self.states) != len(set(self.states)):
            errors.append("Duplicate state names detected in states list.")

        if not self.inputs:
            errors.append("Input alphabet cannot be empty.")
        if len(self.inputs) != len(set(self.inputs)):
            errors.append("Duplicate symbols detected in input alphabet.")

        if self.initial_state not in self.states:
            errors.append(f"Initial state '{self.initial_state}' is not in the states list {self.states}.")

        # Check completeness of transition function (Total function: |Q| * |Sigma| transitions)
        expected_pairs = {(s, inp) for s in self.states for inp in self.inputs}
        defined_pairs = set()

        for idx, t in enumerate(self.transitions):
            if not t.present_state:
                errors.append(f"Transition #{idx+1} has an empty Present State.")
                continue
            if not t.input_symbol:
                errors.append(f"Transition #{idx+1} has an empty Input Symbol.")
                continue
            if not t.next_state:
                errors.append(f"Transition #{idx+1} has an empty Next State.")
                continue
            if not t.output_symbol:
                errors.append(f"Transition #{idx+1} has an empty Output Symbol.")
                continue

            if t.present_state not in self.states:
                errors.append(f"Transition from unknown state '{t.present_state}'.")
            if t.input_symbol not in self.inputs:
                errors.append(f"Transition with unknown input symbol '{t.input_symbol}'.")
            if t.next_state not in self.states:
                errors.append(f"Transition to unknown next state '{t.next_state}'.")

            pair = (t.present_state, t.input_symbol)
            if pair in defined_pairs:
                errors.append(f"Duplicate transition defined for state '{t.present_state}' on input '{t.input_symbol}'.")
            defined_pairs.add(pair)

        missing_pairs = expected_pairs - defined_pairs
        if missing_pairs:
            for p_state, p_inp in sorted(missing_pairs):
                warnings.append(f"Missing transition for State '{p_state}' on Input '{p_inp}'.")

        is_valid = (len(errors) == 0 and len(missing_pairs) == 0)
        return is_valid, errors, warnings

    def to_dataframe(self) -> pd.DataFrame:
        """Returns tabular representation of the Mealy machine."""
        rows = []
        for t in self.transitions:
            rows.append({
                "Present State": t.present_state,
                "Input": t.input_symbol,
                "Next State": t.next_state,
                "Output": t.output_symbol
            })
        return pd.DataFrame(rows)


class MealyToMooreConverter:
    """
    Executes the formal Mealy-to-Moore conversion algorithm.
    """
    def __init__(
        self,
        mealy_machine: MealyMachine,
        initial_state_policy: str = "auto",  # 'auto', 'always_start', 'compact'
        initial_output_symbol: str = "-"
    ):
        self.mealy = mealy_machine
        self.initial_state_policy = initial_state_policy
        self.initial_output_symbol = initial_output_symbol

    def convert(self) -> Dict[str, Any]:
        is_valid, errors, warnings = self.mealy.validate()
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "warnings": warnings
            }

        # Step 1: Analyze incoming transitions for each state
        incoming_outputs: Dict[str, Set[str]] = {s: set() for s in self.mealy.states}
        incoming_transitions: Dict[str, List[Dict[str, str]]] = {s: [] for s in self.mealy.states}

        for t in self.mealy.transitions:
            incoming_outputs[t.next_state].add(t.output_symbol)
            incoming_transitions[t.next_state].append({
                "from_state": t.present_state,
                "input": t.input_symbol,
                "output": t.output_symbol
            })

        # Step 2: Determine if a dedicated start state is needed
        init_state = self.mealy.initial_state
        init_incoming_outputs = incoming_outputs.get(init_state, set())

        needs_start_state = False
        start_state_reason = ""

        if self.initial_state_policy == "always_start":
            needs_start_state = True
            start_state_reason = "Policy set to always create a dedicated start state."
        elif self.initial_state_policy == "compact":
            needs_start_state = False
            start_state_reason = "Compact mode: Reusing split state for initial state."
        else:  # "auto"
            if len(init_incoming_outputs) > 0:
                needs_start_state = True
                start_state_reason = (
                    f"Initial state '{init_state}' has incoming transitions with outputs {sorted(list(init_incoming_outputs))}. "
                    "A dedicated start state is created so no premature output is asserted at t=0."
                )
            else:
                needs_start_state = False
                start_state_reason = f"Initial state '{init_state}' has no incoming transitions, so it directly acts as the Moore start state."

        # Step 3: State splitting & Moore state construction
        moore_states: Dict[str, MooreState] = {}
        state_to_moore_states: Dict[str, List[str]] = {s: [] for s in self.mealy.states}
        split_details: List[Dict[str, Any]] = []

        for s in self.mealy.states:
            outputs = sorted(list(incoming_outputs[s]))
            sources = [
                f"{item['from_state']} (on {item['input']} → {item['output']})"
                for item in incoming_transitions[s]
            ]

            if len(outputs) == 0:
                # Unreachable or start-only state
                # If it's the initial state and no dedicated start state was added, give it initial_output_symbol
                out_val = self.initial_output_symbol if s == init_state else "-"
                m_name = f"{s}_init" if needs_start_state and s == init_state else s
                moore_states[m_name] = MooreState(
                    name=m_name,
                    base_state=s,
                    output=out_val,
                    is_initial=(s == init_state and not needs_start_state),
                    incoming_sources=sources
                )
                state_to_moore_states[s].append(m_name)
                split_details.append({
                    "Original State": s,
                    "Incoming Outputs": "None (No incoming edges)",
                    "Split Count": 1,
                    "Action Taken": "No splitting required. Retained as single state.",
                    "Moore States Generated": m_name,
                    "Assigned Outputs": f"{m_name} → {out_val}"
                })

            elif len(outputs) == 1:
                # Single output associated with all incoming transitions
                out_val = outputs[0]
                m_name = f"{s}_{out_val}"
                moore_states[m_name] = MooreState(
                    name=m_name,
                    base_state=s,
                    output=out_val,
                    is_initial=False,
                    incoming_sources=sources
                )
                state_to_moore_states[s].append(m_name)
                split_details.append({
                    "Original State": s,
                    "Incoming Outputs": f"{{{out_val}}}",
                    "Split Count": 1,
                    "Action Taken": f"All incoming transitions have output '{out_val}'. State maps to '{m_name}'.",
                    "Moore States Generated": m_name,
                    "Assigned Outputs": f"{m_name} → {out_val}"
                })

            else:
                # Multiple incoming outputs: State splitting required!
                m_names = []
                out_assignments = []
                for out_val in outputs:
                    m_name = f"{s}_{out_val}"
                    specific_sources = [
                        f"{item['from_state']} (on {item['input']})"
                        for item in incoming_transitions[s] if item['output'] == out_val
                    ]
                    moore_states[m_name] = MooreState(
                        name=m_name,
                        base_state=s,
                        output=out_val,
                        is_initial=False,
                        incoming_sources=specific_sources
                    )
                    m_names.append(m_name)
                    out_assignments.append(f"{m_name} → {out_val}")
                    state_to_moore_states[s].append(m_name)

                split_details.append({
                    "Original State": s,
                    "Incoming Outputs": f"{{{', '.join(outputs)}}}",
                    "Split Count": len(outputs),
                    "Action Taken": f"Conflicting incoming outputs! Split into {len(outputs)} distinct states.",
                    "Moore States Generated": ", ".join(m_names),
                    "Assigned Outputs": ", ".join(out_assignments)
                })

        # Step 4: Resolve Moore initial state
        if needs_start_state:
            start_name = f"{init_state}_start"
            moore_states[start_name] = MooreState(
                name=start_name,
                base_state=init_state,
                output=self.initial_output_symbol,
                is_initial=True,
                incoming_sources=["(Start of Machine)"]
            )
            moore_initial_state = start_name
        else:
            # Pick first Moore state corresponding to init_state
            moore_initial_state = state_to_moore_states[init_state][0]
            moore_states[moore_initial_state].is_initial = True

        # Step 5: Construct Moore transitions
        # Lookup table for original Mealy: (state, input) -> (next_state, output)
        mealy_lookup: Dict[Tuple[str, str], Tuple[str, str]] = {}
        for t in self.mealy.transitions:
            mealy_lookup[(t.present_state, t.input_symbol)] = (t.next_state, t.output_symbol)

        moore_transitions: List[MooreTransition] = []
        moore_transition_rows = []
        moore_compact_rows = []

        # Order states: initial state first, then alphabetical
        ordered_state_names = [moore_initial_state] + sorted(
            [s for s in moore_states.keys() if s != moore_initial_state]
        )

        for m_name in ordered_state_names:
            m_state = moore_states[m_name]
            base_s = m_state.base_state

            compact_row = {
                "Present State (Moore)": m_name,
                "State Output": m_state.output,
                "Is Initial": "★ Yes" if m_state.is_initial else "No"
            }

            for inp in self.mealy.inputs:
                if (base_s, inp) in mealy_lookup:
                    next_base, out_sym = mealy_lookup[(base_s, inp)]
                    target_moore_name = f"{next_base}_{out_sym}"
                    if target_moore_name not in moore_states:
                        # Fallback if state had 0 incoming transitions and was not renamed
                        target_moore_name = state_to_moore_states[next_base][0]

                    moore_transitions.append(MooreTransition(
                        present_state=m_name,
                        input_symbol=inp,
                        next_state=target_moore_name
                    ))
                    compact_row[f"Next State (Input = {inp})"] = target_moore_name

                    moore_transition_rows.append({
                        "Present State": m_name,
                        "State Output": m_state.output,
                        "Input": inp,
                        "Next State": target_moore_name
                    })
                else:
                    compact_row[f"Next State (Input = {inp})"] = "-"

            moore_compact_rows.append(compact_row)

        moore_compact_df = pd.DataFrame(moore_compact_rows)
        moore_transitions_df = pd.DataFrame(moore_transition_rows)
        split_summary_df = pd.DataFrame(split_details)

        # Generate step-by-step educational explanations
        step_explanations = self._generate_step_explanations(
            incoming_outputs,
            incoming_transitions,
            split_details,
            needs_start_state,
            start_state_reason,
            moore_initial_state,
            moore_states,
            moore_compact_rows
        )

        return {
            "success": True,
            "errors": errors,
            "warnings": warnings,
            "mealy_df": self.mealy.to_dataframe(),
            "moore_compact_df": moore_compact_df,
            "moore_transitions_df": moore_transitions_df,
            "split_summary_df": split_summary_df,
            "moore_states": moore_states,
            "moore_initial_state": moore_initial_state,
            "moore_transitions": moore_transitions,
            "needs_start_state": needs_start_state,
            "start_state_reason": start_state_reason,
            "step_explanations": step_explanations,
            "total_mealy_states": len(self.mealy.states),
            "total_moore_states": len(moore_states)
        }

    def _generate_step_explanations(
        self,
        incoming_outputs: Dict[str, Set[str]],
        incoming_transitions: Dict[str, List[Dict[str, str]]],
        split_details: List[Dict[str, Any]],
        needs_start_state: bool,
        start_state_reason: str,
        moore_initial_state: str,
        moore_states: Dict[str, MooreState],
        moore_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generates detailed, structured educational steps for the conversion."""
        steps = []

        # Step 1: Incoming Transitions Analysis
        step1_text = (
            r"In a **Mealy machine**, outputs are associated with **transitions** ($\lambda(q, a)$). "
            r"In a **Moore machine**, outputs are associated directly with **states** ($\lambda'(q)$). "
            r"Therefore, to convert from Mealy to Moore, we first examine every incoming transition to each state "
            r"and inspect the output symbols carried by those transitions."
        )
        step1_items = []
        for s in self.mealy.states:
            trans = incoming_transitions[s]
            outs = incoming_outputs[s]
            if not trans:
                step1_items.append(f"- **State `{s}`**: Has **no incoming transitions**.")
            else:
                desc = ", ".join([f"`{t['from_state']}` on `{t['input']}` → `{t['output']}`" for t in trans])
                step1_items.append(f"- **State `{s}`**: Received from {desc}. **Distinct outputs:** `{sorted(list(outs))}`")

        steps.append({
            "number": 1,
            "title": "Analyze Incoming Transitions and Outputs",
            "explanation": step1_text,
            "details": "\n".join(step1_items)
        })

        # Step 2: State Splitting Logic
        step2_text = (
            r"If a state $q$ has incoming transitions with **two or more distinct output symbols**, "
            r"a single Moore state cannot satisfy both outputs because a Moore state can emit only one fixed output. "
            r"Hence, the state must be **split** into multiple states: one for each unique output symbol ($q_{y_1}, q_{y_2}, \dots$)."
        )
        step2_items = []
        for d in split_details:
            step2_items.append(
                f"- **State `{d['Original State']}`**: Incoming outputs = `{d['Incoming Outputs']}`. "
                f"**Decision:** {d['Action Taken']} (Generated: `{d['Moore States Generated']}`)."
            )

        steps.append({
            "number": 2,
            "title": "Group Outputs & Split States",
            "explanation": step2_text,
            "details": "\n".join(step2_items)
        })

        # Step 3: Initial State Resolution
        step3_text = (
            r"In a Moore machine, the initial state emits an output **before** any input is read ($t=0$). "
            r"However, in a Mealy machine, no output is generated until the first transition is triggered. "
            r"To preserve strict language and sequence equivalence without falsely indicating a prior transition, "
            r"we inspect the initial state."
        )
        step3_details = (
            f"- **Mealy Initial State:** `{self.mealy.initial_state}`\n"
            f"- **Policy Applied:** `{self.initial_state_policy}`\n"
            f"- **Moore Initial State:** `{moore_initial_state}` (Assigned Output: `{moore_states[moore_initial_state].output}`)\n"
            f"- **Justification:** {start_state_reason}"
        )
        steps.append({
            "number": 3,
            "title": "Initial State & Output Offset Resolution",
            "explanation": step3_text,
            "details": step3_details
        })

        # Step 4: Constructing New Transitions
        step4_text = (
            r"For every Moore state $q_y$ derived from base Mealy state $q$ and for every input symbol $a \in \Sigma$:" "\n\n"
            r"$$\delta'(q_y, a) = p_z$$" "\n\n"
            r"where in the original Mealy machine $\delta(q, a) = p$ and $\lambda(q, a) = z$. "
            r"Because the transition in Mealy produces output $z$, the destination state in Moore must be $p_z$ "
            r"(the state with output $z$)."
        )
        step4_examples = [
            f"- State `{row['Present State (Moore)']}` inherits transitions from base state `{moore_states[row['Present State (Moore)']].base_state}`."
            for row in moore_rows[:min(4, len(moore_rows))]
        ]
        if len(moore_rows) > 4:
            step4_examples.append(f"- ... (applied consistently to all {len(moore_rows)} Moore states)")

        steps.append({
            "number": 4,
            "title": "Reconstruct State Transitions",
            "explanation": step4_text,
            "details": "\n".join(step4_examples)
        })

        # Step 5: Equivalence Theorem
        step5_text = (
            r"**Formal Equivalence:**" "\n\n"
            r"For any input string $w = a_1 a_2 \dots a_k$:" "\n"
            r"- The Mealy machine outputs sequence: $y_1 y_2 \dots y_k$ (length $k$)." "\n"
            r"- The Moore machine outputs sequence: $y_0 y_1 y_2 \dots y_k$ (length $k+1$)." "\n\n"
            r"Disregarding the initial state's output $y_0$ (at time $t=0$), the two output sequences are **strictly identical**. "
            r"Both machines recognize and produce identical responses to all input sequences."
        )
        steps.append({
            "number": 5,
            "title": "Verify Mathematical Equivalence",
            "explanation": step5_text,
            "details": f"Total Mealy States: **{len(self.mealy.states)}** ➔ Total Moore States: **{len(moore_states)}**."
        })

        return steps
