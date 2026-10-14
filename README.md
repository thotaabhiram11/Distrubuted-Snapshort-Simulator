# 📸 Chandy-Lamport Distributed Snapshot Simulator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Subject](https://img.shields.io/badge/Subject-Distributed%20Computing-purple.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20External-success.svg)]()
[![Build Status](https://img.shields.io/badge/Tests-5%2F5%20Passed-brightgreen.svg)]()

An interactive, zero-dependency simulator and visualization platform implementing the **Chandy-Lamport Distributed Snapshot Algorithm** for the university subject **Distributed Computing / Distributed Systems**.

Includes an **Interactive Animated Web Dashboard**, a **Command-Line Terminal Interface**, an **Automated Consistent Cut Validator**, **Unit Test Suites**, and a **Complete 10-Slide Academic PowerPoint Presentation (`.pptx`)**.

---

## 🌟 Key Highlights

- **🎯 Canonical Algorithm Implementation**: Strict adherence to the Chandy-Lamport Marker-Sending and Marker-Receiving rules.
- **⚡ Zero External Dependencies**: Runs entirely on the Python Standard Library (`http.server`, `json`, `unittest`, `zipfile`, `xml`). No `pip install` required!
- **🌐 Real-Time Interactive Web Dashboard**:
  - Live animated SVG network graph (Ring, Mesh, and Star topologies).
  - Floating token transfers ($25🪙$) and moving snapshot markers ($🚩 \text{MARKER}$).
  - Live Channel Recording indicators (pulsing amber glow during in-transit capture).
  - Instant Consistent Cut Inspection table with mathematical token conservation verification.
- **💻 Interactive CLI Mode**: Terminal dashboard with step-by-step clock ticking and canned demo scenarios.
- **📊 Presentation Deck Included**: Ready-to-present PowerPoint slide deck (`presentation/Distributed_Snapshot_Algorithm.pptx`) + Slide-by-slide speaker notes and Viva Voce Q&A guide (`presentation/PRESENTATION_NOTES.md`).
- **🧪 Comprehensive Test Suite**: 5 unit and integration tests verifying FIFO delivery, in-flight message capture, and global conservation laws.

---

## 🧠 Theoretical Background

In an asynchronous distributed system:
1. There is **no shared physical memory**.
2. There is **no globally synchronized physical clock**.
3. Messages between processes experience unpredictable network delays and remain **in transit**.

A **Global State** consists of the local states of all processes plus the states of all communication channels:
$$\text{GlobalState} = \bigcup_{i=1}^{N} \text{LocalState}(P_i) \;\cup\; \bigcup_{i,j} \text{ChannelState}(C_{ij})$$

### The Consistent Cut Property
A cut is **consistent** if for every message $m$:
$$\text{receive}(m) \in \text{Cut} \implies \text{send}(m) \in \text{Cut}$$
No message can be recorded as received unless its corresponding send event has already been recorded (i.e., **no orphan messages**).

### Chandy-Lamport Protocol Rules (FIFO Channels)
```
       [ Initiator P0 ] ───────────── MARKER ────────────> [ Receiver P1 ]
             │                                                    │
  1. Record local state.                                1. If first marker:
  2. Send MARKER on all out-channels.                      - Record local state.
  3. Start recording all in-channels.                      - Record C_01 as EMPTY.
                                                           - Send MARKER on all out-channels.
                                                           - Start recording other in-channels.
                                                        2. If subsequent marker:
                                                           - Stop recording on C_01.
                                                           - Channel state = messages recorded
                                                             between snapshot and marker arrival.
```

---

## 📁 Project Directory Structure

```text
├── simulator/                      # Core distributed simulator package
│   ├── __init__.py                 # Module exports
│   ├── models.py                   # Data schemas (Message, ChannelState, GlobalSnapshot)
│   ├── channel.py                  # FIFO channel with latency & in-transit recording buffers
│   ├── process.py                  # Process state machine & Chandy-Lamport marker rules
│   ├── topology.py                 # Topology builders (Ring, Mesh, Star, Custom)
│   ├── validator.py                # Consistent cut & token conservation oracle
│   └── engine.py                   # Discrete-event simulation runner & clock coordinator
│
├── web/                            # Interactive GUI Web Dashboard
│   ├── index.html                  # HTML5 layout & responsive panels
│   ├── styles.css                  # Modern dark glassmorphic styling
│   └── app.js                      # SVG graph renderer, animations & REST client
│
├── presentation/                   # Academic Presentation & Viva Materials
│   ├── Distributed_Snapshot_Algorithm.pptx  # 10-slide PowerPoint presentation deck
│   ├── generate_pptx.py            # Standalone generator to rebuild presentation anytime
│   └── PRESENTATION_NOTES.md       # Slide-by-slide speaker script & Viva Voce Q&A
│
├── tests/                          # Automated test suites
│   ├── __init__.py
│   └── test_simulation.py          # Unit & integration tests
│
├── cli.py                          # Interactive terminal interface
├── server.py                       # Zero-dependency Python REST API & static server
├── run.bat                         # One-click Windows runner (starts server + opens browser)
├── run.sh                          # One-click Linux/macOS runner
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
└── README.md                       # Project documentation
```

---

## 🚀 Quick Start Guide

### Option 1: One-Click Launch (Windows)
Double-click `run.bat` or run:
```powershell
.\run.bat
```
This automatically launches the HTTP server and opens your browser at `http://localhost:8080`.

### Option 2: Python Command (Any OS)
Start the web dashboard server:
```bash
python server.py 8080
```
Then navigate to: **`http://localhost:8080`** in your web browser.

### Option 3: Interactive CLI Terminal Mode
If you prefer running inside the terminal:
```bash
python cli.py
```

---

## 🧪 Running Automated Unit Tests

Run the full verification test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected output:
```text
test_chandy_lamport_with_in_flight_messages (test_simulation.TestDistributedSnapshot.test_chandy_lamport_with_in_flight_messages) ... ok
test_fully_connected_mesh_snapshot (test_simulation.TestDistributedSnapshot.test_fully_connected_mesh_snapshot) ... ok
test_initial_state (test_simulation.TestDistributedSnapshot.test_initial_state) ... ok
test_no_orphan_messages (test_simulation.TestDistributedSnapshot.test_no_orphan_messages) ... ok
test_simple_transfer (test_simulation.TestDistributedSnapshot.test_simple_transfer) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.005s

OK
```

---

## 🎬 How to Demonstrate for Viva / Evaluation

1. Open `http://localhost:8080`.
2. Click **"Run Classic Demo"**:
   - The simulator initializes 4 nodes ($P_0, P_1, P_2, P_3$) with $100$ tokens each ($\text{Total} = 400$).
   - $P_0$ dispatches $25$ tokens to $P_1$, and $P_2$ dispatches $15$ tokens to $P_3$.
   - While both transfers are **in flight** inside the network channels, $P_0$ initiates the snapshot.
   - Click **Step (Tick)** or **Fast-Forward Snapshot**.
   - Watch the red markers ($🚩$) travel through the channels.
3. Observe the **Consistent Cut Inspection** table:
   - Process states recorded: $P_0: 75, P_1: 100, P_2: 85, P_3: 100 \implies \mathbf{360\text{ tokens}}$.
   - Channel states recorded: $C_{01}: [25], C_{23}: [15] \implies \mathbf{40\text{ in-transit tokens}}$.
   - Total recorded: $360 + 40 = \mathbf{400\text{ tokens}}$.
   - Green banner displays: **"CONSISTENT CUT VERIFIED! Invariant Conserved."**

---

## 📊 Presentation Deck (.pptx)

The PowerPoint presentation is located at:
📁 **`presentation/Distributed_Snapshot_Algorithm.pptx`**

To regenerate or modify the slides at any time:
```bash
python presentation/generate_pptx.py
```

Refer to [presentation/PRESENTATION_NOTES.md](presentation/PRESENTATION_NOTES.md) for speaker talking points and viva answers for each slide!

---

## 🐙 How to Push this Project to GitHub

Follow these steps to push this code and presentation to your GitHub account:

### 1. Create a New Repository on GitHub
1. Go to [GitHub.com](https://github.com/new).
2. Enter a repository name (e.g., `distributed-snapshot-simulator`).
3. Leave **"Initialize this repository with a README"** **UNCHECKED** (we already have a complete README).
4. Click **Create repository**.
5. Copy your repository URL (e.g., `https://github.com/<your-username>/distributed-snapshot-simulator.git`).

### 2. Push from your Terminal
Open your terminal in this project folder and run:
```bash
# Add your GitHub remote repository (replace with your actual URL)
git remote add origin https://github.com/<your-username>/distributed-snapshot-simulator.git

# Rename default branch to main (if not already main)
git branch -M main

# Push the code and presentation files to GitHub
git push -u origin main
```

---

## 🎓 Viva Voce Cheat Sheet

| Question | Core Concept & Answer |
| :--- | :--- |
| **Why must channels be FIFO?** | FIFO ensures markers act as an impenetrable boundary dividing pre-snapshot and post-snapshot messages. |
| **Does Chandy-Lamport freeze computation?** | No! Application transfers continue seamlessly during marker propagation. |
| **What is an orphan message?** | A message recorded as received whose sending event is outside the cut. Chandy-Lamport prevents this. |
| **What is the marker message complexity?** | $O(\|E\|)$ where $\|E\|$ is the total number of directed communication channels. |
| **How does it handle concurrent initiators?** | Markers carry snapshot IDs $(P_i, \text{seq})$, enabling multiple independent snapshots. |

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
