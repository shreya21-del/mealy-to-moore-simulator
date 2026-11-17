"""
Mealy to Moore Machine Converter - Streamlit Web Application
A modern, interactive, and educational tool for automata theory and digital design.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from converter import (
    MealyMachine,
    MealyTransition,
    MealyToMooreConverter,
)
from visualizer import (
    create_mealy_graph,
    create_moore_graph,
    THEMES
)
from simulator import MachineSimulator
from examples import PRESET_EXAMPLES, get_example, get_example_keys
from styles import CUSTOM_CSS, render_header, render_footer


# Page configuration
st.set_page_config(
    page_title="Mealy to Moore Machine Converter",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def initialize_session_state():
    default_ex = PRESET_EXAMPLES["Example 1: Prompt Standard (2 States)"]
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True
        st.session_state["states_list"] = default_ex["states"]
        st.session_state["inputs_list"] = default_ex["inputs"]
        st.session_state["initial_state"] = default_ex["initial_state"]
        st.session_state["transitions_df"] = pd.DataFrame(default_ex["table"])
        st.session_state["initial_state_policy"] = "auto"
        st.session_state["conversion_result"] = None
        st.session_state["active_example_name"] = "Example 1: Prompt Standard (2 States)"


initialize_session_state()


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def load_preset_example(example_key: str):
    """Loads a preset example into session state."""
    ex = get_example(example_key)
    st.session_state["states_list"] = ex["states"]
    st.session_state["inputs_list"] = ex["inputs"]
    st.session_state["initial_state"] = ex["initial_state"]
    st.session_state["transitions_df"] = pd.DataFrame(ex["table"])
    st.session_state["active_example_name"] = example_key
    st.session_state["conversion_result"] = None


def reset_to_default():
    """Resets the machine to the default prompt example."""
    load_preset_example("Example 1: Prompt Standard (2 States)")


def generate_empty_table(states: List[str], inputs: List[str]) -> pd.DataFrame:
    """Generates an empty or skeleton transition table based on states and inputs."""
    rows = []
    for s in states:
        for inp in inputs:
            rows.append({
                "Present State": s,
                "Input": inp,
                "Next State": states[0] if states else "",
                "Output": "0"
            })
    return pd.DataFrame(rows)


def parse_and_convert():
    """Parses current table, validates, and runs the conversion algorithm."""
    states = st.session_state["states_list"]
    inputs = st.session_state["inputs_list"]
    init_state = st.session_state["initial_state"]
    df = st.session_state["transitions_df"]
    policy = st.session_state.get("initial_state_policy", "auto")

    # Build MealyTransition objects from dataframe
    transitions: List[MealyTransition] = []
    for _, row in df.iterrows():
        p_state = str(row.get("Present State", "")).strip()
        inp = str(row.get("Input", "")).strip()
        n_state = str(row.get("Next State", "")).strip()
        out = str(row.get("Output", "")).strip()
        transitions.append(MealyTransition(p_state, inp, n_state, out))

    mealy = MealyMachine(
        states=states,
        inputs=inputs,
        initial_state=init_state,
        transitions=transitions
    )

    converter = MealyToMooreConverter(
        mealy_machine=mealy,
        initial_state_policy=policy,
        initial_output_symbol="-"
    )

    result = converter.convert()
    st.session_state["conversion_result"] = result
    st.session_state["current_mealy"] = mealy
    return result


# -----------------------------------------------------------------------------
# Sidebar: Controls, Presets, and Global Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Machine Controls")

    # Preset selection
    st.markdown("#### 📚 Load Preset Example")
    selected_example = st.selectbox(
        "Choose a real-world or textbook example:",
        options=get_example_keys(),
        index=get_example_keys().index(st.session_state.get("active_example_name", get_example_keys()[0]))
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📥 Load Example", use_container_width=True, type="primary"):
            load_preset_example(selected_example)
            st.rerun()

    with col_btn2:
        if st.button("🔄 Reset Default", use_container_width=True):
            reset_to_default()
            st.rerun()

    st.markdown("---")

    # Algorithm Settings
    st.markdown("#### ⚙️ Conversion Policy")
    policy_choice = st.radio(
        "Initial State Resolution:",
        options=[
            ("auto", "Standard Automata (Dedicated Start state if initial has incoming edges)"),
            ("always_start", "Always add dedicated start state (q0_start)"),
            ("compact", "Compact Mode (Reuse state, omit extra start state)")
        ],
        format_func=lambda x: x[1],
        index=0,
        help="Automata theory requires accounting for the initial output at t=0 when no input has been processed."
    )
    st.session_state["initial_state_policy"] = policy_choice[0]

    st.markdown("---")

    # State Diagram Visual Settings
    st.markdown("#### 🎨 Diagram Styling")
    diagram_dir = st.selectbox(
        "Graph Direction:",
        options=["LR", "TB"],
        format_func=lambda x: "Left to Right (LR)" if x == "LR" else "Top to Bottom (TB)",
        index=0
    )
    theme_choice = st.selectbox(
        "Color Palette:",
        options=list(THEMES.keys()),
        index=0
    )
    merge_arrows = st.checkbox("Merge parallel transitions", value=True, help="Combines multiple transitions between same states into one arrow.")

    st.markdown("---")
    st.caption("Mealy to Moore Machine Suite v2.0 • Antigravity Edition")


# -----------------------------------------------------------------------------
# Main Application Content
# -----------------------------------------------------------------------------
st.markdown(render_header(), unsafe_allow_html=True)

# Top Tabs Navigation
tab_intro, tab_input, tab_results, tab_diagrams, tab_steps, tab_sim = st.tabs([
    "🏠 Introduction & Theory",
    "⚙️ Input Mealy Machine",
    "📊 Conversion Results",
    "📈 State Diagrams",
    "📘 Step-by-Step Explanation",
    "🧪 String Simulator"
])


# =============================================================================
# TAB 1: INTRODUCTION & THEORY
# =============================================================================
with tab_intro:
    st.markdown("### 📖 Understanding Mealy and Moore Machines")
    st.markdown(
        """
        Finite State Machines (FSMs) with output are mathematical models of computation used extensively in 
        **digital logic design**, **compiler construction**, **protocol verification**, and **sequential circuits**. 
        They are categorized based on how their outputs are generated:
        """
    )

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(
            r"""
            <div class="compare-box mealy">
                <h4 style="color: #4f46e5; margin-top: 0;">🔵 Mealy Machine</h4>
                <p>An FSM where <strong>outputs depend on both the present state AND the current input</strong>.</p>
                <ul>
                    <li><strong>Formal Definition:</strong> 6-tuple $(Q, \Sigma, \Delta, \delta, \lambda, q_0)$</li>
                    <li><strong>Output Function:</strong> $\lambda: Q \times \Sigma \to \Delta$</li>
                    <li><strong>Transition Edge:</strong> Labeled as <code>Input / Output</code> (e.g. <code>0 / 1</code>)</li>
                    <li><strong>State Count:</strong> Often requires fewer states than a Moore machine.</li>
                    <li><strong>Timing:</strong> Output changes immediately when input changes (asynchronous to clock edge if input glitches).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_t2:
        st.markdown(
            r"""
            <div class="compare-box moore">
                <h4 style="color: #059669; margin-top: 0;">🟢 Moore Machine</h4>
                <p>An FSM where <strong>outputs depend solely on the present state</strong>.</p>
                <ul>
                    <li><strong>Formal Definition:</strong> 6-tuple $(Q, \Sigma, \Delta, \delta, \lambda', q_0)$</li>
                    <li><strong>Output Function:</strong> $\lambda': Q \to \Delta$</li>
                    <li><strong>State Node:</strong> Output is written inside the state circle (e.g. <code>S / 0</code>)</li>
                    <li><strong>State Count:</strong> May require more states due to output state splitting.</li>
                    <li><strong>Timing:</strong> Output is fully synchronized with the state transitions, offering higher glitch immunity.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### ⚖️ Equivalence & The Initial Output Property")
    st.markdown(
        r"""
        > **Equivalence Theorem:** For every Mealy machine, there exists an equivalent Moore machine, and vice-versa.
        
        However, there is an important timing nuance:
        - When a Mealy machine is powered on, **no output is produced** until the first input symbol arrives. If input string length is $k$, Mealy produces $k$ output symbols.
        - A Moore machine emits an output **immediately upon entering the initial state** (at time $t=0$, before reading any input). For an input string of length $k$, Moore produces $k+1$ output symbols.
        - Therefore, the two machines are equivalent if, when we **discard the initial Moore output symbol**, the remaining output sequence matches the Mealy output sequence exactly:
        $$\text{Output}_{Moore}(w) = y_0 \cdot \text{Output}_{Mealy}(w)$$
        """
    )

    st.markdown("#### 🔄 How the Conversion Works (At a Glance)")
    st.markdown(
        """
        1. **Collect Incoming Transitions:** For each state $q$, find all output symbols associated with transitions that enter $q$.
        2. **Identify State Splitting:** If a state receives incoming transitions with differing outputs (e.g. both `0` and `1`), it cannot be assigned a single Moore output. It is split into $q_0$ (output 0) and $q_1$ (output 1).
        3. **Resolve Initial State:** If the initial state has incoming transitions, create an extra start state $q_{start}$ with output `-` so that no spurious output is emitted before reading input.
        4. **Map New Transitions:** Every split state inherits the outgoing transitions of its base state.
        """
    )


# =============================================================================
# TAB 2: INPUT MEALY MACHINE
# =============================================================================
with tab_input:
    st.markdown("### ⚙️ Define Your Mealy Machine")
    st.markdown("Specify the states, input alphabet, initial state, and transition table.")

    # High-level configuration row
    c_states, c_inputs, c_init = st.columns([2, 2, 2])

    with c_states:
        states_str = st.text_input(
            "States (comma-separated):",
            value=", ".join(st.session_state["states_list"]),
            help="Example: A, B or q0, q1, q2"
        )
        parsed_states = [s.strip() for s in states_str.split(",") if s.strip()]

    with c_inputs:
        inputs_str = st.text_input(
            "Input Alphabet (comma-separated):",
            value=", ".join(st.session_state["inputs_list"]),
            help="Example: 0, 1"
        )
        parsed_inputs = [i.strip() for i in inputs_str.split(",") if i.strip()]

    with c_init:
        # Validate initial state dropdown
        current_init = st.session_state.get("initial_state", parsed_states[0] if parsed_states else "A")
        if current_init not in parsed_states and parsed_states:
            current_init = parsed_states[0]

        init_state_val = st.selectbox(
            "Initial State:",
            options=parsed_states if parsed_states else ["A"],
            index=parsed_states.index(current_init) if current_init in parsed_states else 0
        )

    # Sync parsed states to session state
    st.session_state["states_list"] = parsed_states
    st.session_state["inputs_list"] = parsed_inputs
    st.session_state["initial_state"] = init_state_val

    # Table sync: check if user added or removed states/inputs
    current_df = st.session_state["transitions_df"]

    # Table generation tools
    col_t_action1, col_t_action2 = st.columns([3, 1])
    with col_t_action1:
        st.markdown("#### 📝 Editable Transition Table")
        st.caption(r"You can edit cells directly in the table below. Each row defines $\delta(Present, Input) = Next$ and $\lambda(Present, Input) = Output$.")
    with col_t_action2:
        if st.button("🔄 Auto-Populate All Rows", help="Generates rows for all (State, Input) combinations"):
            st.session_state["transitions_df"] = generate_empty_table(parsed_states, parsed_inputs)
            st.rerun()

    # Editable transition table with selectbox column configuration
    editor_df = st.data_editor(
        st.session_state["transitions_df"],
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Present State": st.column_config.SelectboxColumn(
                "Present State",
                help="Source state of the transition",
                width="medium",
                options=parsed_states,
                required=True
            ),
            "Input": st.column_config.SelectboxColumn(
                "Input",
                help="Input alphabet symbol",
                width="small",
                options=parsed_inputs,
                required=True
            ),
            "Next State": st.column_config.SelectboxColumn(
                "Next State",
                help="Destination state of the transition",
                width="medium",
                options=parsed_states,
                required=True
            ),
            "Output": st.column_config.TextColumn(
                "Output",
                help="Output symbol emitted during transition",
                width="small",
                required=True
            )
        },
        key="data_editor_mealy"
    )

    st.session_state["transitions_df"] = editor_df

    # Quick Validation Box
    validation_mealy = MealyMachine(
        states=parsed_states,
        inputs=parsed_inputs,
        initial_state=init_state_val,
        transitions=[
            MealyTransition(
                str(r.get("Present State", "")).strip(),
                str(r.get("Input", "")).strip(),
                str(r.get("Next State", "")).strip(),
                str(r.get("Output", "")).strip()
            )
            for _, r in editor_df.iterrows()
        ]
    )
    is_valid, val_errors, val_warnings = validation_mealy.validate()

    if not is_valid:
        for err in val_errors:
            st.error(f"❌ {err}")
    if val_warnings:
        for warn in val_warnings:
            st.warning(f"⚠️ {warn}")

    st.markdown("---")

    # Big Convert Button
    c_btn, _ = st.columns([2, 4])
    with c_btn:
        convert_clicked = st.button("🚀 Convert to Moore Machine", type="primary", use_container_width=True)

    if convert_clicked:
        res = parse_and_convert()
        if res["success"]:
            st.success("✅ Conversion successful! Navigate to **📊 Conversion Results** or **📈 State Diagrams** to inspect the Moore machine.")
        else:
            st.error("Conversion failed. Please resolve the validation errors above.")


# Auto-convert if not already converted so user has immediate preview
if st.session_state["conversion_result"] is None and is_valid:
    parse_and_convert()

res = st.session_state.get("conversion_result")


# =============================================================================
# TAB 3: CONVERSION RESULTS
# =============================================================================
with tab_results:
    st.markdown("### 📊 Conversion Results")

    if not res or not res.get("success"):
        st.info("👈 Please define a valid Mealy machine and click **Convert to Moore Machine** in the Input tab.")
    else:
        # Metrics summary row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Original Mealy States", res["total_mealy_states"])
        m2.metric("Resulting Moore States", res["total_moore_states"], delta=f"+{res['total_moore_states'] - res['total_mealy_states']} states" if res['total_moore_states'] > res['total_mealy_states'] else "0 states")
        m3.metric("Mealy Initial State", st.session_state['initial_state'])
        m4.metric("Moore Initial State", res["moore_initial_state"])

        st.markdown("---")

        # 1. Original Mealy Machine Table
        st.markdown("#### 1️⃣ Original Mealy Transition Table")
        st.dataframe(res["mealy_df"], use_container_width=True)

        # 2. State Splitting Breakdown
        st.markdown("#### 2️⃣ State Splitting Analysis")
        st.caption("States with multiple incoming outputs are split so each resulting Moore state has a single unique output.")
        st.dataframe(res["split_summary_df"], use_container_width=True)

        # 3. Moore States and Assigned Outputs
        st.markdown("#### 3️⃣ Generated Moore States & Output Assignments")
        moore_states_info = []
        for name, m_state in res["moore_states"].items():
            moore_states_info.append({
                "Moore State": name,
                "Base State": m_state.base_state,
                "Assigned Output": m_state.output,
                "Is Initial State": "★ Initial" if name == res["moore_initial_state"] else "—",
                "Incoming Transitions Source": ", ".join(m_state.incoming_sources) if m_state.incoming_sources else "(None)"
            })
        st.dataframe(pd.DataFrame(moore_states_info), use_container_width=True)

        # 4. Final Moore Transition Table
        st.markdown("#### 4️⃣ Final Moore Transition Table")
        st.dataframe(res["moore_compact_df"], use_container_width=True)

        # Download Buttons for CSVs
        st.markdown("##### 📥 Export Transition Tables")
        c_csv1, c_csv2 = st.columns(2)
        with c_csv1:
            mealy_csv = res["mealy_df"].to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download Mealy Table (CSV)",
                data=mealy_csv,
                file_name="mealy_machine.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_csv2:
            moore_csv = res["moore_compact_df"].to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download Moore Table (CSV)",
                data=moore_csv,
                file_name="moore_machine.csv",
                mime="text/csv",
                use_container_width=True
            )


# =============================================================================
# TAB 4: STATE DIAGRAMS (GRAPHVIZ)
# =============================================================================
with tab_diagrams:
    st.markdown("### 📈 Visual State Transition Diagrams")

    if not res or not res.get("success"):
        st.info("👈 Please define and convert a machine first to view state diagrams.")
    else:
        current_mealy = st.session_state["current_mealy"]

        # Generate Graphviz Digraphs
        g_mealy = create_mealy_graph(
            mealy=current_mealy,
            direction=diagram_dir,
            theme_name=theme_choice,
            merge_parallel_edges=merge_arrows
        )

        g_moore = create_moore_graph(
            moore_states=res["moore_states"],
            moore_initial_state=res["moore_initial_state"],
            moore_transitions=res["moore_transitions"],
            direction=diagram_dir,
            theme_name=theme_choice,
            merge_parallel_edges=merge_arrows
        )

        # Side by Side State Diagrams
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("#### 🔵 Mealy Machine Diagram")
            st.markdown(
                """
                - **States:** Circular nodes.
                - **Transitions:** Arrows labeled `Input / Output`.
                - **Start:** Arrow pointing to initial state.
                """
            )
            st.graphviz_chart(g_mealy, use_container_width=True)

            # Download Mealy DOT
            st.download_button(
                "📥 Download Mealy DOT Source",
                data=g_mealy.source,
                file_name="mealy_machine.dot",
                mime="text/vnd.graphviz",
                use_container_width=True
            )

        with col_g2:
            st.markdown("#### 🟢 Moore Machine Diagram")
            st.markdown(
                """
                - **States:** Circular nodes with output inside: `[y = Output]`.
                - **Transitions:** Arrows labeled with `Input`.
                - **Start:** Arrow pointing to initial state.
                """
            )
            st.graphviz_chart(g_moore, use_container_width=True)

            # Download Moore DOT
            st.download_button(
                "📥 Download Moore DOT Source",
                data=g_moore.source,
                file_name="moore_machine.dot",
                mime="text/vnd.graphviz",
                use_container_width=True
            )

        st.markdown("---")
        with st.expander("🔍 View Raw Graphviz (DOT) Specifications"):
            col_dot1, col_dot2 = st.columns(2)
            with col_dot1:
                st.code(g_mealy.source, language="dot")
            with col_dot2:
                st.code(g_moore.source, language="dot")


# =============================================================================
# TAB 5: STEP-BY-STEP EXPLANATION
# =============================================================================
with tab_steps:
    st.markdown("### 📘 Step-by-Step Educational Walkthrough")
    st.markdown(
        "A formal mathematical explanation of every transformation step applied to the current machine:"
    )

    if not res or not res.get("success"):
        st.info("👈 Please define and convert a machine first to view the step-by-step walkthrough.")
    else:
        for step in res["step_explanations"]:
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #4338ca; margin-bottom: 0.5rem;">
                        <span class="step-num">{step['number']}</span> {step['title']}
                    </div>
                    <p style="margin-bottom: 0.6rem;">{step['explanation']}</p>
                    <div style="background: rgba(255,255,255,0.05); padding: 0.8rem; border-radius: 6px;">
                        {step['details']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# =============================================================================
# TAB 6: STRING SIMULATOR
# =============================================================================
with tab_sim:
    st.markdown("### 🧪 Interactive String Simulator")
    st.markdown(
        """
        Run an input string synchronously through both the **Mealy** and **Moore** machines. 
        Observe the step-by-step state transitions and compare the emitted output sequences in real time.
        """
    )

    if not res or not res.get("success"):
        st.info("👈 Please define and convert a machine first to use the simulator.")
    else:
        current_mealy = st.session_state["current_mealy"]
        simulator = MachineSimulator(
            mealy=current_mealy,
            moore_states=res["moore_states"],
            moore_initial_state=res["moore_initial_state"],
            moore_transitions=res["moore_transitions"]
        )

        default_test_str = "01011" if set(current_mealy.inputs) >= {"0", "1"} else "".join(current_mealy.inputs * 2)

        col_sim_in, col_sim_btn = st.columns([4, 1])
        with col_sim_in:
            test_string = st.text_input(
                "Enter test input string:",
                value=default_test_str,
                help=f"Valid symbols from alphabet: {current_mealy.inputs}"
            )
        with col_sim_btn:
            st.write("")
            st.write("")
            run_sim = st.button("▶️ Run Simulation", use_container_width=True, type="primary")

        sim_output = simulator.simulate(test_string)

        if not sim_output["success"]:
            st.error(f"❌ {sim_output['error']}")
        else:
            # Equivalence Banner
            if sim_output["is_equivalent"]:
                st.success(
                    "🎉 **Machines are Equivalent!** Disregarding the Moore machine's initial output at $t=0$, "
                    "both machines produce identically matched output sequences."
                )
            else:
                st.warning("⚠️ Sequences differ. Check initial state policy.")

            # Output comparison cards
            c_out1, c_out2, c_out3 = st.columns(3)
            with c_out1:
                st.markdown(
                    f"""
                    <div class="custom-card">
                        <div class="card-title">🔵 Mealy Output</div>
                        <div class="trace-highlight">{sim_output['mealy_outputs']}</div>
                        <div style="font-size: 0.8rem; margin-top: 0.4rem; color: #64748b;">
                            Length: {len(sim_output['mealy_outputs'])} symbols
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c_out2:
                st.markdown(
                    f"""
                    <div class="custom-card">
                        <div class="card-title">🟢 Moore Output</div>
                        <div class="trace-highlight">{sim_output['moore_outputs']}</div>
                        <div style="font-size: 0.8rem; margin-top: 0.4rem; color: #64748b;">
                            Length: {len(sim_output['moore_outputs'])} symbols (includes initial: <code>{sim_output['moore_initial_output']}</code>)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c_out3:
                trimmed = sim_output['moore_outputs'][1:]
                st.markdown(
                    f"""
                    <div class="custom-card">
                        <div class="card-title">🔍 Moore (Trimmed t=0)</div>
                        <div class="trace-highlight">{trimmed}</div>
                        <div style="font-size: 0.8rem; margin-top: 0.4rem; color: #64748b;">
                            Matches Mealy: <strong>{'✅ True' if sim_output['is_equivalent'] else '❌ False'}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Step-by-Step Synchronous Trace Table
            st.markdown("#### 📋 Step-by-Step Execution Trace")
            st.dataframe(sim_output["trace_df"], use_container_width=True)


# Render Footer
st.markdown(render_footer(), unsafe_allow_html=True)
