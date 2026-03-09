#!/usr/bin/env python3
"""
Auto-Test-QA Orchestration Script

Workflow:
1. Build Agent completes → triggers this script
2. Spawn Test Agent → wait for completion
3. If Test PASS → Spawn QA Agent → wait for completion
4. If Test FAIL → Return to Build Agent with feedback
5. If QA REJECT → Return to Build Agent with feedback
6. If QA APPROVE → Done ✅

Usage:
    python3 orchestrate-test-qa.py --build-agent <agent_id> --changed-files <files>
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Paths
HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
AGENTS_DIR = CLAUDE_DIR / "agents"
LOGS_DIR = CLAUDE_DIR / "logs"
STATE_FILE = LOGS_DIR / "test-qa-state.json"

# Ensure logs dir exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class TestQAOrchestrator:
    """Orchestrates the Build → Test → QA chain"""

    def __init__(self, build_agent: str, changed_files: List[str]):
        self.build_agent = build_agent
        self.changed_files = changed_files
        self.state = {
            "build_agent": build_agent,
            "changed_files": changed_files,
            "start_time": datetime.utcnow().isoformat(),
            "status": "initialized",
            "test_agent": None,
            "qa_agent": None,
            "iterations": 0,
            "max_iterations": 3,  # Max feedback loops
        }
        self.save_state()

    def save_state(self):
        """Save current state to file"""
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def spawn_agent(self, agent_type: str, task: str) -> Optional[str]:
        """
        Spawn an agent by writing a task file that the main Claude session will pick up
        Returns: agent_id if successful, None if failed
        """
        self.log(f"Spawning {agent_type} agent...")

        # Generate unique agent ID
        agent_id = f"{agent_type}-{int(time.time())}"
        task_file = LOGS_DIR / f"task-{agent_id}.json"

        # Write task specification
        task_spec = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "task": task,
            "model": "opus" if agent_type in ["test-agent", "qa-reviewer"] else "sonnet",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "changed_files": self.changed_files,
            "build_agent": self.build_agent,
        }

        with open(task_file, "w") as f:
            json.dump(task_spec, f, indent=2)

        self.log(f"✅ Task file created: {task_file}")
        self.log(f"Agent ID: {agent_id}")

        # Signal to main session that there's a new task
        signal_file = LOGS_DIR / "test-qa-pending.signal"
        with open(signal_file, "w") as f:
            f.write(f"{agent_id}\n")

        return agent_id

    def wait_for_agent(self, agent_id: str, timeout: int = 1800) -> Dict:
        """
        Wait for agent to complete by polling task file
        Returns: agent output/result
        """
        self.log(f"Waiting for agent {agent_id} (timeout: {timeout}s)...")

        task_file = LOGS_DIR / f"task-{agent_id}.json"
        start = time.time()

        while time.time() - start < timeout:
            if not task_file.exists():
                self.log(f"❌ Task file disappeared: {task_file}")
                return {"status": "error", "agent_id": agent_id}

            with open(task_file) as f:
                task_data = json.load(f)

            status = task_data.get("status", "pending")

            if status == "completed":
                self.log(f"✅ Agent {agent_id} completed")
                return {"status": "completed", "agent_id": agent_id, "result": task_data.get("result")}
            elif status == "failed":
                self.log(f"❌ Agent {agent_id} failed: {task_data.get('error', 'Unknown error')}")
                return {"status": "failed", "agent_id": agent_id, "error": task_data.get("error")}

            # Still running, wait and check again
            time.sleep(5)

        self.log(f"❌ Agent {agent_id} timeout after {timeout}s")
        return {"status": "timeout", "agent_id": agent_id}

    def run_test_agent(self) -> str:
        """
        Run test agent
        Returns: "PASS" | "FAIL"
        """
        self.log("=== Phase 1: Testing ===")
        self.state["status"] = "testing"
        self.save_state()

        # Prepare task for test agent
        task = f"""
        Test the code changes made by build agent {self.build_agent}.

        Changed files:
        {chr(10).join(f"- {f}" for f in self.changed_files)}

        Read BUILD_REPORT.md if it exists.
        Follow the test-agent briefing (see ~/.claude/agents/test-agent.yaml).
        Create TEST_REPORT.md with your findings.
        """

        # Spawn test agent
        agent_id = self.spawn_agent("test-agent", task)
        if not agent_id:
            self.log("❌ Failed to spawn test agent")
            return "FAIL"

        self.state["test_agent"] = agent_id
        self.save_state()

        # Wait for completion
        result = self.wait_for_agent(agent_id)
        if result["status"] != "completed":
            self.log("❌ Test agent failed or timed out")
            return "FAIL"

        # Check test report
        test_report = Path("TEST_REPORT.md")
        if not test_report.exists():
            self.log("❌ TEST_REPORT.md not found")
            return "FAIL"

        # Parse test result
        content = test_report.read_text()
        if "Test Result:** ✅ PASS" in content:
            self.log("✅ Tests PASSED")
            return "PASS"
        else:
            self.log("❌ Tests FAILED")
            return "FAIL"

    def run_qa_agent(self) -> str:
        """
        Run QA review agent
        Returns: "APPROVE" | "REJECT" | "APPROVE_WITH_NOTES"
        """
        self.log("=== Phase 2: QA Review ===")
        self.state["status"] = "qa_review"
        self.save_state()

        # Prepare task for QA agent
        task = f"""
        Review the code changes made by build agent {self.build_agent}.
        Test agent has already PASSED all tests.

        Changed files:
        {chr(10).join(f"- {f}" for f in self.changed_files)}

        Read BUILD_REPORT.md and TEST_REPORT.md.
        Follow the qa-reviewer briefing (see ~/.claude/agents/qa-reviewer.yaml).
        Create QA_REVIEW.md with your findings.
        """

        # Spawn QA agent
        agent_id = self.spawn_agent("qa-reviewer", task)
        if not agent_id:
            self.log("❌ Failed to spawn QA agent")
            return "REJECT"

        self.state["qa_agent"] = agent_id
        self.save_state()

        # Wait for completion
        result = self.wait_for_agent(agent_id)
        if result["status"] != "completed":
            self.log("❌ QA agent failed or timed out")
            return "REJECT"

        # Check QA report
        qa_report = Path("QA_REVIEW.md")
        if not qa_report.exists():
            self.log("❌ QA_REVIEW.md not found")
            return "REJECT"

        # Parse QA result
        content = qa_report.read_text()
        if "✅ APPROVED — Ready for production" in content:
            self.log("✅ QA APPROVED")
            return "APPROVE"
        elif "⚠️  APPROVED WITH NOTES" in content:
            self.log("⚠️  QA APPROVED WITH NOTES")
            return "APPROVE_WITH_NOTES"
        else:
            self.log("❌ QA REJECTED")
            return "REJECT"

    def send_feedback(self, report_file: str, message: str):
        """Send feedback to build agent via feedback file and task update"""
        self.log(f"📨 Sending feedback to build agent {self.build_agent}")
        self.log(f"Report: {report_file}")
        self.log(f"Message: {message}")

        # Create feedback structure
        feedback = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": "test-qa-orchestrator",
            "to": self.build_agent,
            "report": report_file,
            "message": message,
            "iteration": self.state["iterations"],
            "changed_files": self.changed_files,
        }

        # Save feedback file
        feedback_file = LOGS_DIR / f"feedback-{self.build_agent}.json"
        with open(feedback_file, "w") as f:
            json.dump(feedback, f, indent=2)

        # Update build agent's task file if it exists
        build_task_file = LOGS_DIR / f"task-{self.build_agent}.json"
        if build_task_file.exists():
            with open(build_task_file) as f:
                task_data = json.load(f)

            task_data["status"] = "feedback_received"
            task_data["feedback"] = feedback
            task_data["feedback_file"] = str(feedback_file)

            with open(build_task_file, "w") as f:
                json.dump(task_data, f, indent=2)

            self.log(f"✅ Build agent task updated with feedback")

        # Create human-readable feedback summary
        summary_file = LOGS_DIR / f"feedback-{self.build_agent}.txt"
        with open(summary_file, "w") as f:
            f.write(f"Feedback for Build Agent {self.build_agent}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Iteration: {self.state['iterations']}\n")
            f.write(f"Timestamp: {feedback['timestamp']}\n")
            f.write(f"Report: {report_file}\n\n")
            f.write(f"Message:\n{message}\n\n")
            f.write(f"Changed Files:\n")
            for file in self.changed_files:
                f.write(f"  - {file}\n")
            f.write(f"\nPlease review {report_file} and fix all issues.\n")

        self.log(f"✅ Feedback saved to {feedback_file} and {summary_file}")

    def run(self):
        """Run the complete Build → Test → QA workflow"""
        self.log("=== Auto-Test-QA Orchestration Started ===")
        self.log(f"Build Agent: {self.build_agent}")
        self.log(f"Changed Files: {len(self.changed_files)}")

        while self.state["iterations"] < self.state["max_iterations"]:
            self.state["iterations"] += 1
            self.log(f"\n--- Iteration {self.state['iterations']}/{self.state['max_iterations']} ---")

            # Phase 1: Test
            test_result = self.run_test_agent()
            if test_result == "FAIL":
                self.log("❌ Tests failed — sending feedback to build agent")
                self.send_feedback(
                    "TEST_REPORT.md",
                    "Tests failed. Please review TEST_REPORT.md and fix all issues."
                )
                self.state["status"] = "feedback_sent_test_fail"
                self.save_state()
                return 1  # Exit code 1 = test failure

            # Phase 2: QA Review
            qa_result = self.run_qa_agent()
            if qa_result == "REJECT":
                self.log("❌ QA rejected — sending feedback to build agent")
                self.send_feedback(
                    "QA_REVIEW.md",
                    "QA review rejected. Please review QA_REVIEW.md and fix all critical issues."
                )
                self.state["status"] = "feedback_sent_qa_reject"
                self.save_state()
                return 2  # Exit code 2 = QA rejection

            if qa_result == "APPROVE_WITH_NOTES":
                self.log("⚠️  QA approved with notes — creating follow-up tasks")
                self.state["status"] = "approved_with_notes"
                self.save_state()
                # Don't return — treat as success but log notes
                break

            if qa_result == "APPROVE":
                self.log("✅ QA approved — ready for production")
                self.state["status"] = "approved"
                self.save_state()
                break

        # Final state
        self.state["end_time"] = datetime.utcnow().isoformat()
        self.save_state()

        if self.state["status"] == "approved":
            self.log("\n🎉 SUCCESS — Build passed all quality gates")
            return 0
        elif self.state["status"] == "approved_with_notes":
            self.log("\n✅ SUCCESS WITH NOTES — Build approved, minor issues noted")
            return 0
        else:
            self.log(f"\n❌ FAILED after {self.state['iterations']} iterations")
            return 3


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Test-QA Orchestration Script"
    )
    parser.add_argument(
        "--build-agent",
        required=True,
        help="Build agent ID that completed the work"
    )
    parser.add_argument(
        "--changed-files",
        required=True,
        nargs="+",
        help="List of files that were changed"
    )

    args = parser.parse_args()

    orchestrator = TestQAOrchestrator(
        build_agent=args.build_agent,
        changed_files=args.changed_files
    )

    exit_code = orchestrator.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
