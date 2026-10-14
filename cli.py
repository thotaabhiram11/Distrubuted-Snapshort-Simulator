"""
Interactive CLI for Chandy-Lamport Distributed Snapshot Simulator.
Provides a terminal dashboard, step-by-step stepping, automated scenarios,
and consistent cut inspection.
"""

import sys
import time
from simulator.topology import NetworkTopology
from simulator.engine import SimulationEngine
from simulator.models import MessageType


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def render_banner():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 68)
    print("    DISTRIBUTED SNAPSHOT SIMULATOR (Chandy-Lamport Algorithm)")
    print("      Distributed Computing Project & Consistent Cut Engine   ")
    print("=" * 68)
    print(f"{Colors.RESET}")


def render_dashboard(engine: SimulationEngine):
    state = engine.get_state()
    step = state["current_step"]
    init_tok = state["initial_total_tokens"]
    live_tok = state["current_live_tokens"]
    
    status_color = Colors.GREEN if live_tok == init_tok else Colors.FAIL
    print(f"\n{Colors.BOLD}--- Logical Step: {step} | System Invariant: {status_color}{live_tok}/{init_tok} Tokens{Colors.RESET} ---")

    # Render Process States
    print(f"\n{Colors.BOLD}[Processes / Local States]:{Colors.RESET}")
    for pid, p in state["processes"].items():
        snap_badge = ""
        if p["has_recorded_state"]:
            snap_badge = f"{Colors.GREEN}[SNAPSHOT SAVED: {p['recorded_balance']} tokens]{Colors.RESET}"
        else:
            snap_badge = f"{Colors.DIM}[No Snapshot]{Colors.RESET}"

        done_badge = f"{Colors.CYAN}(Done){Colors.RESET}" if p["is_snapshot_complete"] else ""
        print(f"  • {Colors.BOLD}{pid:<4}{Colors.RESET}: Balance = {p['balance']:>3} tokens  {snap_badge} {done_badge}")

    # Render Active Channels & In-Transit Messages
    active_channels = [ch for ch in state["channels"].values() if ch["in_flight"] or ch["ready_messages"] or ch["is_recording"]]
    print(f"\n{Colors.BOLD}[Channels & In-Transit Messages]:{Colors.RESET}")
    if not active_channels:
        print(f"  {Colors.DIM}(All channels currently quiescent / idle){Colors.RESET}")
    else:
        for ch in active_channels:
            rec_badge = f"{Colors.WARNING}[RECORDING]{Colors.RESET}" if ch["is_recording"] else ""
            closed_badge = f"{Colors.BLUE}[CLOSED BY MARKER]{Colors.RESET}" if ch["closed_by_marker"] else ""
            in_flight_desc = []
            for item in ch["in_flight"]:
                m_type = item["type"]
                amt = item["payload"].get("amount", "")
                ticks = item["remaining_ticks"]
                in_flight_desc.append(f"{m_type}({amt}) in {ticks}t")
            desc = ", ".join(in_flight_desc) if in_flight_desc else "empty"
            print(f"  • {ch['channel_id']:<10} {rec_badge}{closed_badge} => In-Flight: [{desc}]")

    # Render Active Snapshot Status
    if state["active_snapshot"]:
        snap = state["active_snapshot"]
        if snap["is_complete"]:
            val = snap["validation_report"]
            verdict_color = Colors.GREEN if snap["is_consistent"] else Colors.FAIL
            print(f"\n{verdict_color}{Colors.BOLD}>>> SNAPSHOT {snap['snapshot_id']} COMPLETE: {val['summary_verdict']}{Colors.RESET}")
            print(f"    Recorded Processes: {snap['process_snapshots']}")
            print(f"    Recorded Channels : {snap['channel_snapshots']}")
            print(f"    Total Recorded    : {snap['recorded_total_tokens']} tokens (Expected: {init_tok})")
        else:
            print(f"\n{Colors.WARNING}>>> SNAPSHOT IN PROGRESS (Initiator: {snap['initiator']}, Started at Step {snap['initiated_at_step']}){Colors.RESET}")


def run_interactive_cli():
    render_banner()
    print("Initializing 4-node Ring Network (P0, P1, P2, P3)...")
    engine = SimulationEngine(NetworkTopology.create_ring(node_count=4, initial_balance=100, latency=2))
    
    while True:
        render_dashboard(engine)
        print(f"\n{Colors.BOLD}Choose an action:{Colors.RESET}")
        print(" [1] Advance 1 step (Tick clock)")
        print(" [2] Send transfer (e.g. P0 -> P1, 20 tokens)")
        print(" [3] Initiate Chandy-Lamport Snapshot")
        print(" [4] Run automated classic scenario (Transfer + Mid-flight Snapshot)")
        print(" [5] Reset simulation topology (Ring / Mesh / Star)")
        print(" [6] Run until snapshot completes")
        print(" [q] Quit")

        choice = input(f"\n{Colors.CYAN}Enter choice [1-6, q]: {Colors.RESET}").strip().lower()

        if choice == '1':
            engine.step()
        elif choice == '2':
            sender = input("Sender ID (e.g. P0): ").strip()
            receiver = input("Receiver ID (e.g. P1): ").strip()
            try:
                amount = int(input("Amount to transfer: ").strip())
                engine.send_transfer(sender, receiver, amount)
            except ValueError:
                print(f"{Colors.FAIL}Invalid amount!{Colors.RESET}")
        elif choice == '3':
            initiator = input("Initiator Process ID (e.g. P0): ").strip()
            engine.initiate_snapshot(initiator)
        elif choice == '4':
            run_automated_scenario(engine)
        elif choice == '5':
            topo_choice = input("Topology (ring / mesh / star) [default: ring]: ").strip().lower() or "ring"
            nodes = int(input("Node count [default: 4]: ").strip() or "4")
            engine.reset(topology_type=topo_choice, node_count=nodes, initial_balance=100)
            print(f"{Colors.GREEN}Reset complete!{Colors.RESET}")
        elif choice == '6':
            engine.run_until_snapshot_complete(max_steps=50)
        elif choice in ('q', 'quit', 'exit'):
            print("Exiting simulator. Happy Distributed Computing!")
            break
        else:
            print("Invalid command. Please try again.")


def run_automated_scenario(engine: SimulationEngine):
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== RUNNING AUTOMATED CANONICAL SCENARIO ==={Colors.RESET}")
    print("Scenario: Concurrent in-flight transfers with Chandy-Lamport snapshot")
    print("----------------------------------------------------------------------")
    engine.reset("ring", node_count=4, initial_balance=100)

    # Step 0: Transfers initiated
    print(f"{Colors.CYAN}Step 0: P0 transfers 30 to P1; P2 transfers 20 to P3 (Latency=2){Colors.RESET}")
    engine.send_transfer("P0", "P1", 30, latency=2)
    engine.send_transfer("P2", "P3", 20, latency=2)
    render_dashboard(engine)
    time.sleep(1)

    # Step 1: Clock advances, messages are in flight!
    print(f"\n{Colors.CYAN}Step 1: Clock ticks. Messages are in flight. P0 initiates Snapshot!{Colors.RESET}")
    engine.step()
    engine.initiate_snapshot("P0")
    render_dashboard(engine)
    time.sleep(1)

    # Run until complete
    print(f"\n{Colors.CYAN}Stepping forward until all markers are received...{Colors.RESET}")
    step_num = 1
    while engine.active_snapshot and not engine.active_snapshot.is_complete and step_num < 15:
        engine.step()
        render_dashboard(engine)
        time.sleep(0.8)
        step_num += 1

    print(f"\n{Colors.GREEN}{Colors.BOLD}=== SCENARIO EXECUTION FINISHED ==={Colors.RESET}\n")


if __name__ == "__main__":
    run_interactive_cli()
