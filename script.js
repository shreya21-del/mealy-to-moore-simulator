/**
 * Mealy to Moore Machine Converter - Modern Vanilla JS Studio
 * Complete Automata Conversion Algorithm, Native Vector SVG State Diagrams,
 * and Synchronous Execution Simulator.
 */

// ============================================================================
// 1. Presets & Example Library
// ============================================================================
const PRESETS = {
  prompt: {
    name: "Prompt Standard (2 States)",
    states: ["A", "B"],
    inputs: ["0", "1"],
    initialState: "A",
    transitions: [
      { presentState: "A", inputSymbol: "0", nextState: "B", outputSymbol: "0" },
      { presentState: "A", inputSymbol: "1", nextState: "A", outputSymbol: "1" },
      { presentState: "B", inputSymbol: "0", nextState: "A", outputSymbol: "1" },
      { presentState: "B", inputSymbol: "1", nextState: "B", outputSymbol: "0" }
    ]
  },
  splitting: {
    name: "Textbook State Splitting (3 States)",
    states: ["q0", "q1", "q2"],
    inputs: ["0", "1"],
    initialState: "q0",
    transitions: [
      { presentState: "q0", inputSymbol: "0", nextState: "q1", outputSymbol: "0" },
      { presentState: "q0", inputSymbol: "1", nextState: "q2", outputSymbol: "0" },
      { presentState: "q1", inputSymbol: "0", nextState: "q1", outputSymbol: "1" },
      { presentState: "q1", inputSymbol: "1", nextState: "q2", outputSymbol: "0" },
      { presentState: "q2", inputSymbol: "0", nextState: "q1", outputSymbol: "0" },
      { presentState: "q2", inputSymbol: "1", nextState: "q2", outputSymbol: "1" }
    ]
  },
  detector101: {
    name: "'101' Sequence Detector (3 States)",
    states: ["S0", "S1", "S2"],
    inputs: ["0", "1"],
    initialState: "S0",
    transitions: [
      { presentState: "S0", inputSymbol: "0", nextState: "S0", outputSymbol: "0" },
      { presentState: "S0", inputSymbol: "1", nextState: "S1", outputSymbol: "0" },
      { presentState: "S1", inputSymbol: "0", nextState: "S2", outputSymbol: "0" },
      { presentState: "S1", inputSymbol: "1", nextState: "S1", outputSymbol: "0" },
      { presentState: "S2", inputSymbol: "0", nextState: "S0", outputSymbol: "0" },
      { presentState: "S2", inputSymbol: "1", nextState: "S1", outputSymbol: "1" }
    ]
  },
  parity: {
    name: "Parity Generator (Even/Odd)",
    states: ["Even", "Odd"],
    inputs: ["0", "1"],
    initialState: "Even",
    transitions: [
      { presentState: "Even", inputSymbol: "0", nextState: "Even", outputSymbol: "0" },
      { presentState: "Even", inputSymbol: "1", nextState: "Odd", outputSymbol: "1" },
      { presentState: "Odd", inputSymbol: "0", nextState: "Odd", outputSymbol: "1" },
      { presentState: "Odd", inputSymbol: "1", nextState: "Even", outputSymbol: "0" }
    ]
  },
  edge: {
    name: "Signal Edge Detector (Low/High)",
    states: ["Low", "High"],
    inputs: ["0", "1"],
    initialState: "Low",
    transitions: [
      { presentState: "Low", inputSymbol: "0", nextState: "Low", outputSymbol: "0" },
      { presentState: "Low", inputSymbol: "1", nextState: "High", outputSymbol: "1" },
      { presentState: "High", inputSymbol: "0", nextState: "Low", outputSymbol: "1" },
      { presentState: "High", inputSymbol: "1", nextState: "High", outputSymbol: "0" }
    ]
  }
};

// ============================================================================
// 2. Application State
// ============================================================================
const appState = {
  states: ["A", "B"],
  inputs: ["0", "1"],
  initialState: "A",
  policy: "auto",
  transitions: [],
  conversionResult: null,
  simulator: {
    activeStep: 0,
    isPlaying: false,
    playTimer: null,
    traceData: []
  }
};

// ============================================================================
// 3. Core Conversion Algorithm (Mealy to Moore)
// ============================================================================
function convertMealyToMoore(states, inputs, initialState, transitions, policy = "auto") {
  // Clean unique states and inputs
  const cleanStates = states.map(s => String(s).trim()).filter(Boolean);
  const cleanInputs = inputs.map(i => String(i).trim()).filter(Boolean);
  const cleanInit = String(initialState).trim();

  // 1. Analyze incoming transitions and outputs
  const incomingOutputs = {};
  const incomingTransitions = {};
  cleanStates.forEach(s => {
    incomingOutputs[s] = new Set();
    incomingTransitions[s] = [];
  });

  transitions.forEach(t => {
    if (incomingOutputs[t.nextState]) {
      incomingOutputs[t.nextState].add(String(t.outputSymbol).trim());
      incomingTransitions[t.nextState].push({
        fromState: t.presentState,
        inputSymbol: t.inputSymbol,
        outputSymbol: t.outputSymbol
      });
    }
  });

  // 2. Initial State Policy Evaluation
  const initIncoming = incomingOutputs[cleanInit] || new Set();
  let needsStartState = false;
  let startStateReason = "";

  if (policy === "always_start") {
    needsStartState = true;
    startStateReason = "Policy set to always create a dedicated initial start state.";
  } else if (policy === "compact") {
    needsStartState = false;
    startStateReason = "Compact Mode: Initial state reused directly without extra start state.";
  } else { // "auto"
    if (initIncoming.size > 0) {
      needsStartState = true;
      startStateReason = `Initial state '${cleanInit}' has incoming transitions with outputs {${Array.from(initIncoming).sort().join(", ")}}. A dedicated start state avoids premature output at t=0.`;
    } else {
      needsStartState = false;
      startStateReason = `Initial state '${cleanInit}' has no incoming transitions, so it directly acts as the Moore start state.`;
    }
  }

  // 3. State Splitting & Moore States Generation
  const mooreStates = {};
  const stateToMooreStates = {};
  const splitDetails = [];
  cleanStates.forEach(s => stateToMooreStates[s] = []);

  cleanStates.forEach(s => {
    const outs = Array.from(incomingOutputs[s] || []).sort();
    const trans = incomingTransitions[s] || [];
    const sources = trans.map(t => `${t.fromState} (on ${t.inputSymbol} → ${t.outputSymbol})`);

    if (outs.length === 0) {
      const outVal = "-";
      const mName = (needsStartState && s === cleanInit) ? `${s}_init` : s;
      mooreStates[mName] = {
        name: mName,
        baseState: s,
        output: outVal,
        isInitial: (s === cleanInit && !needsStartState),
        sources
      };
      stateToMooreStates[s].push(mName);
      splitDetails.push({
        originalState: s,
        incomingOutputs: "None (0 incoming edges)",
        splitCount: 1,
        action: "No incoming transitions. Retained as single state.",
        mooreStates: [mName],
        assignedOutputs: `${mName} → ${outVal}`
      });
    } else if (outs.length === 1) {
      const outVal = outs[0];
      const mName = `${s}_${outVal}`;
      mooreStates[mName] = {
        name: mName,
        baseState: s,
        output: outVal,
        isInitial: false,
        sources
      };
      stateToMooreStates[s].push(mName);
      splitDetails.push({
        originalState: s,
        incomingOutputs: `{${outVal}}`,
        splitCount: 1,
        action: `Uniform incoming output '${outVal}'. Mapped to state '${mName}'.`,
        mooreStates: [mName],
        assignedOutputs: `${mName} → ${outVal}`
      });
    } else {
      // Split required!
      const mNames = [];
      const assignments = [];
      outs.forEach(outVal => {
        const mName = `${s}_${outVal}`;
        const specificSources = trans
          .filter(t => t.outputSymbol === outVal)
          .map(t => `${t.fromState} (on ${t.inputSymbol})`);

        mooreStates[mName] = {
          name: mName,
          baseState: s,
          output: outVal,
          isInitial: false,
          sources: specificSources
        };
        mNames.push(mName);
        assignments.push(`${mName} → ${outVal}`);
        stateToMooreStates[s].push(mName);
      });

      splitDetails.push({
        originalState: s,
        incomingOutputs: `{${outs.join(", ")}}`,
        splitCount: outs.length,
        action: `Conflicting incoming outputs! Split into ${outs.length} distinct states.`,
        mooreStates: mNames,
        assignedOutputs: assignments.join(", ")
      });
    }
  });

  // 4. Resolve Moore Initial State
  let mooreInitialState = "";
  if (needsStartState) {
    const startName = `${cleanInit}_start`;
    mooreStates[startName] = {
      name: startName,
      baseState: cleanInit,
      output: "-",
      isInitial: true,
      sources: ["(Start of Machine)"]
    };
    mooreInitialState = startName;
  } else {
    mooreInitialState = stateToMooreStates[cleanInit][0];
    mooreStates[mooreInitialState].isInitial = true;
  }

  // 5. Construct Moore Transition Table
  const mealyLookup = {};
  transitions.forEach(t => {
    mealyLookup[`${t.presentState}___${t.inputSymbol}`] = {
      nextState: t.nextState,
      outputSymbol: t.outputSymbol
    };
  });

  const mooreTransitions = [];
  const mooreRows = [];

  const orderedMooreNames = [mooreInitialState].concat(
    Object.keys(mooreStates).filter(k => k !== mooreInitialState).sort()
  );

  orderedMooreNames.forEach(mName => {
    const mState = mooreStates[mName];
    const baseS = mState.baseState;

    const rowObj = {
      mooreState: mName,
      baseState: baseS,
      output: mState.output,
      isInitial: mState.isInitial ? "★ Yes" : "No",
      nextStates: {}
    };

    cleanInputs.forEach(inp => {
      const key = `${baseS}___${inp}`;
      if (mealyLookup[key]) {
        const { nextState, outputSymbol } = mealyLookup[key];
        let targetName = `${nextState}_${outputSymbol}`;
        if (!mooreStates[targetName]) {
          targetName = stateToMooreStates[nextState][0];
        }
        mooreTransitions.push({
          presentState: mName,
          inputSymbol: inp,
          nextState: targetName
        });
        rowObj.nextStates[inp] = targetName;
      } else {
        rowObj.nextStates[inp] = "-";
      }
    });

    mooreRows.push(rowObj);
  });

  // 6. Educational Step Breakdown
  const stepExplanations = [
    {
      number: 1,
      title: "Analyze Incoming Transitions and Outputs",
      explanation: "In a Mealy machine, outputs are associated with transitions (λ(q, a)). In a Moore machine, outputs reside on the states (λ'(q)). We begin by inspecting all incoming transitions entering each state.",
      details: cleanStates.map(s => {
        const outs = Array.from(incomingOutputs[s] || []).sort();
        const count = incomingTransitions[s]?.length || 0;
        return `• <strong>State ${s}</strong>: ${count} incoming edges, outputs = {${outs.join(", ") || "none"}}`;
      })
    },
    {
      number: 2,
      title: "Group Outputs & State Splitting",
      explanation: "If a state receives transitions with multiple distinct output symbols, it cannot emit a single fixed output in a Moore machine. Such states must be split into multiple sub-states.",
      details: splitDetails.map(d => {
        return `• <strong>State ${d.originalState}</strong>: ${d.action} ➔ <code>${d.mooreStates.join(", ")}</code>`;
      })
    },
    {
      number: 3,
      title: "Initial State & Timing Resolution",
      explanation: "A Moore machine emits an output immediately at time t=0 before reading any input. If the Mealy initial state has incoming edges, creating an explicit start state ensures language equivalence without premature output.",
      details: [
        `• <strong>Mealy Initial State:</strong> <code>${cleanInit}</code>`,
        `• <strong>Policy Applied:</strong> ${policy}`,
        `• <strong>Moore Initial State:</strong> <code>${mooreInitialState}</code> (Assigned Output: <code>${mooreStates[mooreInitialState].output}</code>)`,
        `• <strong>Justification:</strong> ${startStateReason}`
      ]
    },
    {
      number: 4,
      title: "Reconstruct Transitions",
      explanation: "Every Moore state q_y inherits the transitions of its base state q. On input symbol 'a', if Mealy transitions to p with output z, the Moore state transitions to p_z (δ'(q_y, a) = p_z).",
      details: mooreRows.slice(0, 4).map(r => {
        return `• State <code>${r.mooreState}</code> transitions to: ` +
          cleanInputs.map(inp => `[${inp} ➔ ${r.nextStates[inp]}]`).join(", ");
      })
    },
    {
      number: 5,
      title: "Equivalence Theorem Verification",
      explanation: "For any input word w = a₁a₂...aₖ of length k: Mealy outputs y₁y₂...yₖ (length k), while Moore outputs y₀y₁y₂...yₖ (length k+1). Disregarding initial symbol y₀, the output sequences are strictly identical.",
      details: [
        `• Total Mealy States: <strong>${cleanStates.length}</strong> ➔ Total Moore States: <strong>${Object.keys(mooreStates).length}</strong>`,
        `• Strict Language & Sequence Equivalence: <strong>Guaranteed</strong>`
      ]
    }
  ];

  return {
    success: true,
    mealyStates: cleanStates,
    mealyInputs: cleanInputs,
    mealyInitialState: cleanInit,
    mealyTransitions: transitions,
    mooreStates,
    mooreInitialState,
    mooreTransitions,
    mooreRows,
    splitDetails,
    stepExplanations,
    needsStartState,
    startStateReason
  };
}

// ============================================================================
// 4. Native SVG Vector State Diagram Visualizer
// ============================================================================
function renderNativeSvgGraph(containerId, isMoore, machineData, activeNodeName = null) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.clientWidth || 420;
  const height = 360;

  // Gather nodes and edges
  let nodes = [];
  let edges = [];
  let initialNode = "";

  if (!isMoore) {
    // Mealy Machine
    nodes = machineData.mealyStates.map(s => ({ id: s, label: s, sublabel: "" }));
    initialNode = machineData.mealyInitialState;

    // Group edges between same pair
    const edgeMap = {};
    machineData.mealyTransitions.forEach(t => {
      const key = `${t.presentState}-->${t.nextState}`;
      if (!edgeMap[key]) edgeMap[key] = { from: t.presentState, to: t.nextState, labels: [] };
      edgeMap[key].labels.push(`${t.inputSymbol} / ${t.outputSymbol}`);
    });
    edges = Object.values(edgeMap);
  } else {
    // Moore Machine
    nodes = Object.values(machineData.mooreStates).map(m => ({
      id: m.name,
      label: m.name,
      sublabel: `y = ${m.output}`,
      isInitial: m.isInitial
    }));
    initialNode = machineData.mooreInitialState;

    // Group edges between same pair
    const edgeMap = {};
    machineData.mooreTransitions.forEach(t => {
      const key = `${t.presentState}-->${t.nextState}`;
      if (!edgeMap[key]) edgeMap[key] = { from: t.presentState, to: t.nextState, labels: [] };
      edgeMap[key].labels.push(String(t.inputSymbol));
    });
    edges = Object.values(edgeMap);
  }

  // Calculate layout coordinates (circular layout for optimal node separation)
  const nodeCount = nodes.length;
  const radius = Math.min(width, height) * 0.35;
  const centerX = width / 2;
  const centerY = height / 2;
  const nodeRadius = isMoore ? 28 : 24;

  const nodePositions = {};
  nodes.forEach((n, idx) => {
    // Offset angle to start at top or left
    const angle = (2 * Math.PI * idx / nodeCount) - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    nodePositions[n.id] = { x, y };
  });

  // Build SVG XML
  let svg = `
    <svg class="fsm-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Arrowhead Marker -->
        <marker id="arrowhead-${containerId}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="var(--text-secondary)" />
        </marker>
        <marker id="arrowhead-start-${containerId}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="var(--primary)" />
        </marker>
      </defs>
  `;

  // Draw Initial State Start Pointer
  if (nodePositions[initialNode]) {
    const initPos = nodePositions[initialNode];
    const startX = initPos.x - nodeRadius - 35;
    const startY = initPos.y;
    const targetX = initPos.x - nodeRadius;
    const targetY = initPos.y;

    svg += `
      <g class="svg-start-pointer">
        <line x1="${startX}" y1="${startY}" x2="${targetX}" y2="${targetY}" 
              stroke="var(--primary)" stroke-width="2.5" marker-end="url(#arrowhead-start-${containerId})" />
        <text x="${startX - 6}" y="${startY + 4}" fill="var(--primary)" font-size="11" font-weight="700" text-anchor="end">start</text>
      </g>
    `;
  }

  // Draw Edges
  edges.forEach(edge => {
    const from = nodePositions[edge.from];
    const to = nodePositions[edge.to];
    if (!from || !to) return;

    const labelText = edge.labels.join(", ");

    if (edge.from === edge.to) {
      // Self loop
      const loopRadius = 22;
      const x = from.x;
      const y = from.y - nodeRadius;
      const pathD = `M ${x - 10} ${y} C ${x - 25} ${y - 45}, ${x + 25} ${y - 45}, ${x + 10} ${y}`;

      svg += `
        <g class="svg-edge">
          <path d="${pathD}" stroke="var(--text-secondary)" stroke-width="1.8" fill="none" marker-end="url(#arrowhead-${containerId})" />
          <rect x="${x - 18}" y="${y - 48}" width="36" height="14" rx="3" fill="var(--bg-secondary)" opacity="0.85" />
          <text x="${x}" y="${y - 38}" fill="var(--accent)" font-size="10.5" text-anchor="middle">${labelText}</text>
        </g>
      `;
    } else {
      // Directed edge between distinct nodes
      // Calculate angle and boundary points
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      const angle = Math.atan2(dy, dx);
      const startX = from.x + nodeRadius * Math.cos(angle);
      const startY = from.y + nodeRadius * Math.sin(angle);
      const endX = to.x - nodeRadius * Math.cos(angle);
      const endY = to.y - nodeRadius * Math.sin(angle);

      // Curve offset perpendicular to line
      const normalX = -Math.sin(angle);
      const normalY = Math.cos(angle);
      const curveAmount = 18;

      const midX = (startX + endX) / 2 + normalX * curveAmount;
      const midY = (startY + endY) / 2 + normalY * curveAmount;

      const pathD = `M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`;

      svg += `
        <g class="svg-edge">
          <path d="${pathD}" stroke="var(--text-secondary)" stroke-width="1.8" fill="none" marker-end="url(#arrowhead-${containerId})" />
          <rect x="${midX - 22}" y="${midY - 8}" width="44" height="16" rx="4" fill="var(--bg-secondary)" opacity="0.9" />
          <text x="${midX}" y="${midY + 4}" fill="var(--accent)" font-size="10.5" text-anchor="middle">${labelText}</text>
        </g>
      `;
    }
  });

  // Draw Nodes
  nodes.forEach(node => {
    const pos = nodePositions[node.id];
    if (!pos) return;

    const isActive = (node.id === activeNodeName);
    const isInit = (node.id === initialNode);

    const strokeColor = isActive ? "#f59e0b" : (isInit ? "var(--primary)" : "var(--border-focus)");
    const fillColor = isActive ? "rgba(245, 158, 11, 0.2)" : (isInit ? "var(--primary-light)" : "var(--bg-card)");

    svg += `
      <g class="svg-node ${isActive ? "is-active" : ""}" data-node-id="${node.id}">
        <circle cx="${pos.x}" cy="${pos.y}" r="${nodeRadius}" 
                fill="${fillColor}" stroke="${strokeColor}" stroke-width="${isInit || isActive ? 2.8 : 2}" />
    `;

    if (node.sublabel) {
      svg += `
        <text x="${pos.x}" y="${pos.y - 6}" font-size="11" font-weight="700" fill="var(--text-primary)">${node.label}</text>
        <text x="${pos.x}" y="${pos.y + 8}" font-size="9.5" font-weight="600" fill="var(--success)">${node.sublabel}</text>
      `;
    } else {
      svg += `
        <text x="${pos.x}" y="${pos.y}" font-size="12" font-weight="700" fill="var(--text-primary)">${node.label}</text>
      `;
    }

    svg += `</g>`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

// ============================================================================
// 5. String Simulator Logic
// ============================================================================
function runSimulation(mealyMachine, mooreData, inputString) {
  const raw = String(inputString).trim();
  if (!raw) return { success: false, error: "Input string is empty." };

  const validAlphabet = new Set(mealyMachine.mealyInputs);
  const symbols = raw.includes(" ") ? raw.split(" ").filter(Boolean) : raw.split("");

  const invalid = symbols.filter(s => !validAlphabet.has(s));
  if (invalid.length > 0) {
    return {
      success: false,
      error: `Invalid symbols detected: [${Array.from(new Set(invalid)).join(", ")}]. Allowed alphabet: [${mealyMachine.mealyInputs.join(", ")}].`
    };
  }

  // Mealy transition lookup
  const mealyDelta = {};
  mealyMachine.mealyTransitions.forEach(t => {
    mealyDelta[`${t.presentState}___${t.inputSymbol}`] = { next: t.nextState, out: t.outputSymbol };
  });

  // Moore transition lookup
  const mooreDelta = {};
  mooreData.mooreTransitions.forEach(t => {
    mooreDelta[`${t.presentState}___${t.inputSymbol}`] = t.nextState;
  });

  let mealyCurr = mealyMachine.mealyInitialState;
  let mooreCurr = mooreData.mooreInitialState;

  const trace = [];
  const mealyOutputs = [];
  const mooreOutputs = [];

  // Step 0: Power On
  const initMooreOut = mooreData.mooreStates[mooreCurr]?.output || "-";
  mooreOutputs.push(initMooreOut);

  trace.push({
    step: 0,
    symbol: "— (Start)",
    mealyState: mealyCurr,
    mealyOut: "—",
    mealyNext: "—",
    mooreState: mooreCurr,
    mooreOut: initMooreOut,
    mooreNext: "—"
  });

  // Step 1..k
  for (let i = 0; i < symbols.length; i++) {
    const sym = symbols[i];

    // Mealy
    const mKey = `${mealyCurr}___${sym}`;
    if (!mealyDelta[mKey]) return { success: false, error: `Mealy has no transition from '${mealyCurr}' on '${sym}'.` };
    const mTrans = mealyDelta[mKey];
    mealyOutputs.push(mTrans.out);

    // Moore
    const moKey = `${mooreCurr}___${sym}`;
    if (!mooreDelta[moKey]) return { success: false, error: `Moore has no transition from '${mooreCurr}' on '${sym}'.` };
    const moNext = mooreDelta[moKey];
    const moNextOut = mooreData.mooreStates[moNext]?.output || "-";
    mooreOutputs.push(moNextOut);

    trace.push({
      step: i + 1,
      symbol: sym,
      mealyState: mealyCurr,
      mealyOut: mTrans.out,
      mealyNext: mTrans.next,
      mooreState: mooreCurr,
      mooreOut: moNextOut,
      mooreNext: moNext
    });

    mealyCurr = mTrans.next;
    mooreCurr = moNext;
  }

  const mooreTrimmed = mooreOutputs.slice(1);
  const isEquivalent = (mealyOutputs.join("") === mooreTrimmed.join(""));

  return {
    success: true,
    symbols,
    trace,
    mealyOutputString: mealyOutputs.join(""),
    mooreOutputString: mooreOutputs.join(""),
    mooreInitialOutput: initMooreOut,
    mooreTrimmedString: mooreTrimmed.join(""),
    isEquivalent
  };
}

// ============================================================================
// 6. UI Rendering & DOM Binding
// ============================================================================
function updateConfigPills() {
  const statesContainer = document.getElementById("statesPillContainer");
  const inputsContainer = document.getElementById("inputsPillContainer");
  const initSelect = document.getElementById("selectInitialState");

  if (statesContainer) {
    statesContainer.innerHTML = appState.states.map(s => `<span class="pill-item">${s}</span>`).join("");
  }
  if (inputsContainer) {
    inputsContainer.innerHTML = appState.inputs.map(i => `<span class="pill-item">${i}</span>`).join("");
  }
  if (initSelect) {
    const curr = appState.initialState;
    initSelect.innerHTML = appState.states.map(s => `<option value="${s}" ${s === curr ? "selected" : ""}>${s}</option>`).join("");
    if (!appState.states.includes(curr) && appState.states.length > 0) {
      appState.initialState = appState.states[0];
      initSelect.value = appState.states[0];
    }
  }
}

function renderMealyTable() {
  const tbody = document.getElementById("mealyTableBody");
  if (!tbody) return;

  tbody.innerHTML = appState.transitions.map((t, index) => {
    return `
      <tr data-index="${index}">
        <td>
          <select class="table-select sel-present">
            ${appState.states.map(s => `<option value="${s}" ${s === t.presentState ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </td>
        <td>
          <select class="table-select sel-input">
            ${appState.inputs.map(i => `<option value="${i}" ${i === t.inputSymbol ? "selected" : ""}>${i}</option>`).join("")}
          </select>
        </td>
        <td>
          <select class="table-select sel-next">
            ${appState.states.map(s => `<option value="${s}" ${s === t.nextState ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </td>
        <td>
          <input type="text" class="table-input input-output" value="${t.outputSymbol}" maxlength="5" />
        </td>
        <td>
          <button class="btn btn-ghost btn-xs btn-delete-row" data-index="${index}" title="Remove transition">✕</button>
        </td>
      </tr>
    `;
  }).join("");

  validateCurrentMachine();
}

function syncTableDataFromDOM() {
  const rows = document.querySelectorAll("#mealyTableBody tr");
  const newTransitions = [];

  rows.forEach(r => {
    const p = r.querySelector(".sel-present")?.value.trim();
    const i = r.querySelector(".sel-input")?.value.trim();
    const n = r.querySelector(".sel-next")?.value.trim();
    const o = r.querySelector(".input-output")?.value.trim();
    if (p && i && n) {
      newTransitions.push({
        presentState: p,
        inputSymbol: i,
        nextState: n,
        outputSymbol: o || "0"
      });
    }
  });

  appState.transitions = newTransitions;
  validateCurrentMachine();
}

function validateCurrentMachine() {
  const badge = document.getElementById("validationBadge");
  if (!badge) return;

  const expected = new Set();
  appState.states.forEach(s => {
    appState.inputs.forEach(i => {
      expected.add(`${s}__${i}`);
    });
  });

  const defined = new Set();
  appState.transitions.forEach(t => {
    defined.add(`${t.presentState}__${t.inputSymbol}`);
  });

  const missing = [];
  expected.forEach(key => {
    if (!defined.has(key)) {
      const [s, i] = key.split("__");
      missing.push(`(${s}, ${i})`);
    }
  });

  if (missing.length === 0) {
    badge.className = "status-badge status-valid";
    badge.innerHTML = "<span>● All Transitions Defined</span>";
  } else {
    badge.className = "status-badge status-warning";
    badge.innerHTML = `<span>⚠️ Missing ${missing.length}: ${missing.slice(0, 2).join(", ")}${missing.length > 2 ? "..." : ""}</span>`;
  }
}

function populateResultsUI(result) {
  if (!result || !result.success) return;

  // Metrics
  document.getElementById("valMealyStates").textContent = result.mealyStates.length;
  document.getElementById("valMooreStates").textContent = Object.keys(result.mooreStates).length;
  const delta = Object.keys(result.mooreStates).length - result.mealyStates.length;
  document.getElementById("valDeltaStates").textContent = delta > 0 ? `+${delta}` : "0";
  document.getElementById("valMealyInit").textContent = result.mealyInitialState;
  document.getElementById("valMooreInit").textContent = result.mooreInitialState;

  // Render Moore Table
  const thead = document.querySelector("#mooreResultsTable thead");
  const tbody = document.getElementById("mooreTableBody");

  if (thead && tbody) {
    let headHtml = `
      <tr>
        <th>Moore State</th>
        <th>Output (λ')</th>
        <th>Is Initial</th>
    `;
    result.mealyInputs.forEach(inp => {
      headHtml += `<th>Next State (a = ${inp})</th>`;
    });
    headHtml += `</tr>`;
    thead.innerHTML = headHtml;

    let bodyHtml = "";
    result.mooreRows.forEach(row => {
      bodyHtml += `
        <tr>
          <td><strong>${row.mooreState}</strong></td>
          <td><span class="pill-item">${row.output}</span></td>
          <td>${row.isInitial}</td>
      `;
      result.mealyInputs.forEach(inp => {
        bodyHtml += `<td>${row.nextStates[inp] || "-"}</td>`;
      });
      bodyHtml += `</tr>`;
    });
    tbody.innerHTML = bodyHtml;
  }

  // Render State Splitting Table
  const splitTbody = document.getElementById("splittingTableBody");
  if (splitTbody) {
    splitTbody.innerHTML = result.splitDetails.map(d => `
      <tr>
        <td><strong>${d.originalState}</strong></td>
        <td><code>${d.incomingOutputs}</code></td>
        <td>${d.splitCount}</td>
        <td>${d.action}</td>
        <td>${d.mooreStates.map(m => `<code>${m}</code>`).join(", ")}</td>
      </tr>
    `).join("");
  }

  // Render Step-by-Step Timeline
  const stepsContainer = document.getElementById("stepsTimeline");
  if (stepsContainer) {
    stepsContainer.innerHTML = result.stepExplanations.map(s => `
      <div class="step-card">
        <div class="step-header">
          <span class="step-num">${s.number}</span>
          <h4 class="step-title">${s.title}</h4>
        </div>
        <p class="step-explanation">${s.explanation}</p>
        <div class="step-details-box">
          <ul>${s.details.map(d => `<li>${d}</li>`).join("")}</ul>
        </div>
      </div>
    `).join("");
  }

  // Render State Diagrams
  renderNativeSvgGraph("mealySvgContainer", false, result);
  renderNativeSvgGraph("mooreSvgContainer", true, result);

  // Trigger default simulation
  triggerSimulation();
}

function triggerSimulation() {
  if (!appState.conversionResult) return;

  const simInput = document.getElementById("simInputString").value.trim() || "01011";
  const simRes = runSimulation(appState.conversionResult, appState.conversionResult, simInput);

  const banner = document.getElementById("simEquivalenceBanner");
  const mealySeq = document.getElementById("simMealySeq");
  const mooreSeq = document.getElementById("simMooreSeq");
  const mooreTrimmed = document.getElementById("simMooreTrimmed");
  const matchStatus = document.getElementById("simMatchStatus");
  const tbody = document.getElementById("simTraceTableBody");

  if (!simRes.success) {
    if (banner) {
      banner.className = "equivalence-banner equivalence-warning";
      banner.innerHTML = `<span>⚠️ ${simRes.error}</span>`;
    }
    return;
  }

  appState.simulator.traceData = simRes.trace;
  appState.simulator.activeStep = simRes.trace.length - 1;

  if (mealySeq) mealySeq.textContent = simRes.mealyOutputString;
  if (mooreSeq) mooreSeq.textContent = simRes.mooreOutputString;
  if (mooreTrimmed) mooreTrimmed.textContent = simRes.mooreTrimmedString;

  if (banner) {
    if (simRes.isEquivalent) {
      banner.className = "equivalence-banner equivalence-success";
      banner.innerHTML = `<span>🎉 <strong>Machines are Equivalent!</strong> Disregarding the Moore machine's initial output at t=0, both output sequences match symbol-for-symbol.</span>`;
    } else {
      banner.className = "equivalence-banner equivalence-warning";
      banner.innerHTML = `<span>⚠️ Output sequences differ. Check initial state policy.</span>`;
    }
  }

  if (matchStatus) {
    matchStatus.innerHTML = `Matches Mealy: <strong>${simRes.isEquivalent ? "✅ True" : "❌ False"}</strong>`;
  }

  if (tbody) {
    tbody.innerHTML = simRes.trace.map((r, i) => `
      <tr class="${i === appState.simulator.activeStep ? "sim-row-active" : ""}" data-step="${r.step}">
        <td><strong>${r.step}</strong></td>
        <td><code>${r.symbol}</code></td>
        <td>${r.mealyState}</td>
        <td><span class="pill-item">${r.mealyOut}</span></td>
        <td>${r.mealyNext}</td>
        <td>${r.mooreState}</td>
        <td><span class="pill-item">${r.mooreOut}</span></td>
        <td>${r.mooreNext}</td>
      </tr>
    `).join("");
  }
}

// ============================================================================
// 7. Event Handlers & Initialization
// ============================================================================
function loadPreset(presetKey) {
  const p = PRESETS[presetKey] || PRESETS.prompt;
  appState.states = [...p.states];
  appState.inputs = [...p.inputs];
  appState.initialState = p.initialState;
  appState.transitions = p.transitions.map(t => ({ ...t }));

  document.getElementById("inputStates").value = appState.states.join(", ");
  document.getElementById("inputAlphabet").value = appState.inputs.join(", ");
  updateConfigPills();
  renderMealyTable();

  // Run conversion immediately
  executeConversion();
}

function executeConversion() {
  syncTableDataFromDOM();

  const policyRadio = document.querySelector('input[name="startPolicy"]:checked');
  appState.policy = policyRadio ? policyRadio.value : "auto";

  const result = convertMealyToMoore(
    appState.states,
    appState.inputs,
    appState.initialState,
    appState.transitions,
    appState.policy
  );

  appState.conversionResult = result;
  populateResultsUI(result);
}

// Auto-fill all combinations
function autoFillTransitions() {
  const rows = [];
  appState.states.forEach(s => {
    appState.inputs.forEach(inp => {
      rows.push({
        presentState: s,
        inputSymbol: inp,
        nextState: appState.states[0] || "A",
        outputSymbol: "0"
      });
    });
  });
  appState.transitions = rows;
  renderMealyTable();
}

// Export CSV Helper
function downloadCsv(filename, rows) {
  const processRow = function (row) {
    return row.map(val => `"${String(val).replace(/"/g, '""')}"`).join(",");
  };

  const csvContent = "data:text/csv;charset=utf-8," + rows.map(processRow).join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Export SVG Helper
function downloadSvg(containerId, filename) {
  const container = document.getElementById(containerId);
  const svg = container?.querySelector("svg");
  if (!svg) return;

  const svgData = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  // Theme Toggle
  const btnToggleTheme = document.getElementById("btnToggleTheme");
  const themeIcon = document.getElementById("themeIcon");

  btnToggleTheme?.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);
    themeIcon.textContent = nextTheme === "dark" ? "☀️" : "🌙";
  });

  // Modal Open/Close
  const theoryModal = document.getElementById("theoryModal");
  document.getElementById("btnTheoryModal")?.addEventListener("click", () => {
    theoryModal?.classList.add("open");
  });
  document.getElementById("btnCloseModal")?.addEventListener("click", () => {
    theoryModal?.classList.remove("open");
  });
  theoryModal?.addEventListener("click", (e) => {
    if (e.target === theoryModal) theoryModal.classList.remove("open");
  });

  // States Input Change
  document.getElementById("inputStates")?.addEventListener("input", (e) => {
    const raw = e.target.value;
    appState.states = raw.split(",").map(s => s.trim()).filter(Boolean);
    updateConfigPills();
    renderMealyTable();
  });

  // Inputs Change
  document.getElementById("inputAlphabet")?.addEventListener("input", (e) => {
    const raw = e.target.value;
    appState.inputs = raw.split(",").map(i => i.trim()).filter(Boolean);
    updateConfigPills();
    renderMealyTable();
  });

  // Initial State Change
  document.getElementById("selectInitialState")?.addEventListener("change", (e) => {
    appState.initialState = e.target.value;
  });

  // Table Row Add/Delete/Change Delegation
  document.getElementById("btnAddRow")?.addEventListener("click", () => {
    appState.transitions.push({
      presentState: appState.states[0] || "A",
      inputSymbol: appState.inputs[0] || "0",
      nextState: appState.states[0] || "A",
      outputSymbol: "0"
    });
    renderMealyTable();
  });

  document.getElementById("btnClearRows")?.addEventListener("click", () => {
    appState.transitions = [];
    renderMealyTable();
  });

  document.getElementById("btnAutoFill")?.addEventListener("click", () => {
    autoFillTransitions();
  });

  document.getElementById("mealyTableBody")?.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-delete-row")) {
      const idx = parseInt(e.target.dataset.index, 10);
      appState.transitions.splice(idx, 1);
      renderMealyTable();
    }
  });

  document.getElementById("mealyTableBody")?.addEventListener("change", () => {
    syncTableDataFromDOM();
  });

  // Convert Button
  document.getElementById("btnConvert")?.addEventListener("click", () => {
    executeConversion();
  });

  // Policy Radios
  document.querySelectorAll('input[name="startPolicy"]').forEach(r => {
    r.addEventListener("change", () => {
      executeConversion();
    });
  });

  // Presets
  document.getElementById("btnLoadPreset")?.addEventListener("click", () => {
    const sel = document.getElementById("presetSelect")?.value;
    loadPreset(sel);
  });

  document.getElementById("btnReset")?.addEventListener("click", () => {
    loadPreset("prompt");
  });

  // Results Sub Tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.dataset.tab;
      document.getElementById(tabId)?.classList.add("active");
    });
  });

  // Simulator Controls
  document.getElementById("btnSimRunAll")?.addEventListener("click", () => {
    triggerSimulation();
  });

  document.getElementById("btnSimReset")?.addEventListener("click", () => {
    appState.simulator.activeStep = 0;
    triggerSimulation();
  });

  document.getElementById("btnSimStep")?.addEventListener("click", () => {
    if (!appState.simulator.traceData.length) triggerSimulation();
    const max = appState.simulator.traceData.length - 1;
    appState.simulator.activeStep = (appState.simulator.activeStep + 1) % (max + 1);

    // Update active row highlighting
    document.querySelectorAll("#simTraceTableBody tr").forEach((tr, i) => {
      tr.classList.toggle("sim-row-active", i === appState.simulator.activeStep);
    });

    // Highlight active nodes on SVG
    const stepObj = appState.simulator.traceData[appState.simulator.activeStep];
    if (stepObj) {
      renderNativeSvgGraph("mealySvgContainer", false, appState.conversionResult, stepObj.mealyState);
      renderNativeSvgGraph("mooreSvgContainer", true, appState.conversionResult, stepObj.mooreState);
    }
  });

  document.getElementById("btnSimPlay")?.addEventListener("click", (e) => {
    if (appState.simulator.isPlaying) {
      clearInterval(appState.simulator.playTimer);
      appState.simulator.isPlaying = false;
      e.target.textContent = "▶ Play";
    } else {
      appState.simulator.isPlaying = true;
      e.target.textContent = "⏸ Pause";
      appState.simulator.playTimer = setInterval(() => {
        document.getElementById("btnSimStep")?.click();
      }, 700);
    }
  });

  // Exports
  document.getElementById("btnDownloadMealyCsv")?.addEventListener("click", () => {
    if (!appState.conversionResult) return;
    const rows = [["Present State", "Input", "Next State", "Output"]];
    appState.conversionResult.mealyTransitions.forEach(t => {
      rows.push([t.presentState, t.inputSymbol, t.nextState, t.outputSymbol]);
    });
    downloadCsv("mealy_machine.csv", rows);
  });

  document.getElementById("btnDownloadMooreCsv")?.addEventListener("click", () => {
    if (!appState.conversionResult) return;
    const head = ["Moore State", "Output", "Is Initial", ...appState.conversionResult.mealyInputs.map(i => `Next State (Input ${i})`)];
    const rows = [head];
    appState.conversionResult.mooreRows.forEach(r => {
      const row = [r.mooreState, r.output, r.isInitial];
      appState.conversionResult.mealyInputs.forEach(inp => {
        row.push(r.nextStates[inp] || "-");
      });
      rows.push(row);
    });
    downloadCsv("moore_machine.csv", rows);
  });

  document.getElementById("btnDownloadMealySvg")?.addEventListener("click", () => {
    downloadSvg("mealySvgContainer", "mealy_machine.svg");
  });

  document.getElementById("btnDownloadMooreSvg")?.addEventListener("click", () => {
    downloadSvg("mooreSvgContainer", "moore_machine.svg");
  });

  document.getElementById("btnDownloadDot")?.addEventListener("click", () => {
    if (!appState.conversionResult) return;
    let dot = "digraph MooreMachine {\n  rankdir=LR;\n";
    appState.conversionResult.mooreTransitions.forEach(t => {
      dot += `  "${t.presentState}" -> "${t.nextState}" [label="${t.inputSymbol}"];\n`;
    });
    dot += "}\n";

    const blob = new Blob([dot], { type: "text/vnd.graphviz" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "moore_machine.dot";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  // Initial Load with default preset
  loadPreset("prompt");
});
