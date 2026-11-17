# ⚙️ Mealy to Moore Machine Converter Website

An interactive, educational, and modern web application built with **Python**, **Streamlit**, **Pandas**, and **Graphviz** for converting **Mealy Machines** into equivalent **Moore Machines** using formal automata theory and state-splitting algorithms.

---

## 🌟 Key Features

1. **Modern, Responsive Web Interface**:
   - Clean, professional design with dark and light mode compatibility.
   - Theoretical introduction to Mealy and Moore machines with formal definitions and timing comparisons.

2. **Interactive Input Section**:
   - Flexible definition of states, input alphabet, and initial state.
   - Dynamic and editable transition table powered by `st.data_editor` with validation dropdowns.
   - Auto-population tool for generating all combinations of state-input transitions.

3. **Accurate Mathematical Conversion Algorithm**:
   - Identifies incoming transitions and categorizes output symbols for each state.
   - Performs state splitting whenever a state receives conflicting outputs ($q_{y_1}, q_{y_2}, \dots$).
   - Reconstructs transitions mapping each Moore state to its corresponding target Moore state.
   - Handles the initial state with configurable resolution policies:
     - **Standard Automata (Auto):** Adds a dedicated start state $q_{start}$ when the initial state has incoming edges.
     - **Always Start:** Always introduces $q_{start}$ with output `-`.
     - **Compact Mode:** Reuses existing split states.
   - Formally accounts for the initial-output offset between Mealy and Moore machines.

4. **Comprehensive Results Display**:
   - Original Mealy transition table.
   - State-splitting analysis detailing incoming transitions, unique outputs, and decisions.
   - List of newly generated Moore states and their assigned outputs.
   - Final Moore transition table (compact input-column format and transition-row format).
   - Prominently highlighted Moore initial state.

5. **Side-by-Side Graphical State Diagrams**:
   - Visualized using **Graphviz** (`st.graphviz_chart`).
   - **Mealy Machine Diagram:** Circular states with transitions labeled as `Input / Output` and start indicator.
   - **Moore Machine Diagram:** Circular states with output displayed inside (`[y = Output]`) and transitions labeled with input symbols.
   - Custom color themes (Indigo/Teal, Ocean Blue & Purple, High Contrast) and direction toggle (LR vs TB).
   - One-click DOT source download and inspection.

6. **Step-by-Step Educational Walkthrough**:
   - Breaks down the complete conversion process into sequential mathematical steps.
   - Explains state splitting, output assignment, and equivalence theorem with KaTeX formulas.

7. **Synchronous String Simulator**:
   - Test any arbitrary input sequence (e.g. `01011`).
   - Runs the string through both machines in lock-step.
   - Displays a side-by-side execution trace verifying that $\text{Output}_{Moore}(w) = y_0 \cdot \text{Output}_{Mealy}(w)$.

8. **Export & Preset Management**:
   - Download transition tables as **CSV**.
   - Download state diagrams as **DOT** files.
   - 5 built-in presets covering basic mapping, sequence detectors, multi-state splitting, and parity generators.

---

## 📁 Project Architecture

```
mealy to moore/
├── app.py              # Main Streamlit web application & UI tabs
├── converter.py        # Core automata conversion algorithm & mathematical validations
├── visualizer.py       # Graphviz diagram generation & visual themes
├── simulator.py        # Step-by-step string execution & equivalence verification
├── examples.py         # 5 preset test machines
├── styles.py           # Custom CSS styling, headers, and UI cards
├── test_converter.py   # Unit & integration tests for conversion logic
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 📖 Theoretical Background

### Formal Definitions
- **Mealy Machine:** A 6-tuple $M_1 = (Q, \Sigma, \Delta, \delta, \lambda, q_0)$, where:
  - $Q$: Finite set of states
  - $\Sigma$: Input alphabet
  - $\Delta$: Output alphabet
  - $\delta: Q \times \Sigma \to Q$: State transition function
  - $\lambda: Q \times \Sigma \to \Delta$: Output function
  - $q_0 \in Q$: Initial state

- **Moore Machine:** A 6-tuple $M_2 = (Q', \Sigma, \Delta, \delta', \lambda', q_0')$, where:
  - $Q'$: Finite set of states
  - $\lambda': Q' \to \Delta$: Output function associated with states

### Equivalence Relation
For an input sequence $w = a_1 a_2 \dots a_k$:
- Mealy Machine emits: $y_1 y_2 \dots y_k$ (length $k$)
- Moore Machine emits: $y_0 y_1 y_2 \dots y_k$ (length $k+1$)

When the initial output symbol $y_0$ (produced at time $t=0$ before reading any input) is ignored, both output sequences are identical:
$$\text{Output}_{Moore}(w) = y_0 \cdot \text{Output}_{Mealy}(w)$$
