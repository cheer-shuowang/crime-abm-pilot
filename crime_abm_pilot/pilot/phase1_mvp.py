"""
Phase 1: Minimum Viable Product (MVP) Test

This tests the absolute basics:
1. Can we create agents?
2. Can we call the LLM?
3. Can we run a deliberation?
4. Can we measure silence?

Configuration:
- 3 agents (2 collectivist, 1 individualist for contrast)
- 1 event (wrongful arrest)
- 1 institution response (blaming)
- 1 deliberation round
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model import CommunityModel
from src.utils import cost_tracker, logger
from rich.console import Console
from rich.table import Table

console = Console()

def print_banner(text):
    """Print formatted banner"""
    console.print(f"\n{'='*60}", style="bold blue")
    console.print(f"{text:^60}", style="bold blue")
    console.print(f"{'='*60}", style="bold blue")

def test_1_agent_creation():
    """Test 1: Can we create agents?"""
    
    print_banner("TEST 1: AGENT CREATION")
    
    try:
        model = CommunityModel(n_agents=3, culture_type="collectivism")
        
        console.print(f"✓ Created model with {len(model.schedule.agents)} agents", 
                     style="green")
        
        for agent in model.schedule.agents:
            console.print(f"  Agent {agent.unique_id}: {agent.culture}, "
                         f"self-censorship={agent.self_censorship:.1f}", 
                         style="cyan")
        
        return True, model
    
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="red")
        return False, None

def test_2_llm_call(model):
    """Test 2: Can we call the LLM?"""
    
    print_banner("TEST 2: LLM CONNECTION")
    
    try:
        from src.utils import llm_call
        
        response = llm_call("Say 'Hello, I am working!' in one sentence.")
        
        console.print(f"✓ LLM responded: {response}", style="green")
        
        return True
    
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="red")
        return False

def test_3_deliberation(model):
    """Test 3: Can we run a deliberation?"""
    
    print_banner("TEST 3: DELIBERATION EXECUTION")
    
    try:
        outcomes = model.run_deliberation(
            event_type="wrongful_arrest",
            response_type="blaming"
        )
        
        console.print("✓ Deliberation completed", style="green")
        console.print(f"\nOutcomes:", style="bold")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Total agents", str(outcomes['total_agents']))
        table.add_row("Attended", str(outcomes['attended']))
        table.add_row("Spoke", str(outcomes['spoke']))
        table.add_row("Attendance rate", f"{outcomes['attendance_rate']:.2%}")
        table.add_row("Speech rate", f"{outcomes['speech_rate']:.2%}")
        table.add_row("Attend-Speech Gap", f"{outcomes['attendance_speech_gap']:.2f}")
        
        console.print(table)
        
        return True, outcomes
    
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="red")
        logger.exception("Deliberation failed")
        return False, None

def test_4_inspect_content(model):
    """Test 4: Inspect deliberation content quality"""
    
    print_banner("TEST 4: CONTENT INSPECTION")
    
    try:
        console.print("\nAgent Private Opinions:", style="bold")
        
        for agent in model.schedule.agents:
            if agent.private_opinion:
                console.print(f"\n[cyan]Agent {agent.unique_id} ({agent.culture}):[/cyan]")
                console.print(f"  Private: {agent.private_opinion[:150]}...")
                
                if agent.public_statement:
                    console.print(f"  Public: {agent.public_statement[:150]}...")
                else:
                    console.print(f"  Public: [red][SILENT][/red]")
                    if agent.silence_reason:
                        console.print(f"  Reason: {agent.silence_reason}")
        
        return True
    
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="red")
        return False

def test_5_silence_measurement(outcomes):
    """Test 5: Can we measure silence?"""
    
    print_banner("TEST 5: SILENCE METRICS")
    
    try:
        gap = outcomes['attendance_speech_gap']
        
        console.print(f"\nAttendance-Speech Gap: {gap:.2f}", style="bold")
        
        if gap > 0.2:
            console.print("✓ Significant silence detected (gap > 0.2)", style="green")
        elif gap > 0:
            console.print("⚠ Some silence present", style="yellow")
        else:
            console.print("⚠ No silence gap detected", style="yellow")
        
        return True
    
    except Exception as e:
        console.print(f"✗ Failed: {e}", style="red")
        return False

def main():
    """Run all MVP tests"""
    
    console.print("\n🚀 PHASE 1: MVP TEST SUITE", style="bold magenta")
    console.print("Testing core functionality with 3 agents\n")
    
    results = {}
    
    # Test 1: Agent creation
    success, model = test_1_agent_creation()
    results['agent_creation'] = success
    if not success:
        console.print("\n❌ Cannot proceed without agents", style="red")
        return
    
    # Test 2: LLM connection
    success = test_2_llm_call(model)
    results['llm_connection'] = success
    if not success:
        console.print("\n❌ Cannot proceed without LLM", style="red")
        return
    
    # Test 3: Deliberation
    success, outcomes = test_3_deliberation(model)
    results['deliberation'] = success
    if not success:
        console.print("\n❌ Deliberation failed", style="red")
        return
    
    # Test 4: Content inspection
    success = test_4_inspect_content(model)
    results['content_inspection'] = success
    
    # Test 5: Silence measurement
    success = test_5_silence_measurement(outcomes)
    results['silence_measurement'] = success
    
    # Summary
    print_banner("TEST SUMMARY")
    
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Status", justify="center")
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        style = "green" if passed else "red"
        summary_table.add_row(test_name.replace('_', ' ').title(), f"[{style}]{status}[/{style}]")
    
    console.print(summary_table)
    
    # Cost report
    cost_tracker.report()
    cost_tracker.save()
    
    # Final verdict
    all_passed = all(results.values())
    
    if all_passed:
        console.print("\n🎉 ALL TESTS PASSED!", style="bold green")
        console.print("✓ Ready to proceed to Phase 2", style="green")
    else:
        console.print("\n⚠️  SOME TESTS FAILED", style="bold yellow")
        console.print("→ Review logs and fix issues before proceeding", style="yellow")
    
    console.print(f"\nLogs saved to: outputs/logs/", style="dim")
    console.print(f"Deliberation saved to: outputs/deliberations/", style="dim")

if __name__ == "__main__":
    main()