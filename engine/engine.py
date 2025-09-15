import sys
import os
import subprocess
import requests
import json

# Configuration
AGENT_BRAIN_URL = "http://127.0.0.1:8000/get_plan"
MLOPS_LOG_FILE = os.path.expanduser("~/agentic-shell/engine/interaction_log.jsonl")

# ANSI Color Codes
class Colors:
    BLUE, CYAN, GREEN, YELLOW, RED, ENDC, BOLD = '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m'

# Agent's Brain Communication
class AgentBrain:
    def get_plan(self, query: str):
        try:
            response = requests.post(AGENT_BRAIN_URL, json={"query": query}, timeout=30)
            response.raise_for_status()
            data = response.json()
            plan_steps = data.get("plan", [])
            if plan_steps:
                return [(step["command"], step["explanation"]) for step in plan_steps]
        except Exception as e:
            print(f"{Colors.RED}Error contacting brain or parsing plan: {e}{Colors.ENDC}")
        return None

# MLOps Data Logger
class DataLogger:
    def __init__(self, filepath):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def log_full_interaction(self, initial_prompt, executed_steps):
        log_entry = {"prompt": initial_prompt, "executed_plan": executed_steps}
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# Terminal Execution Engine
class TerminalEngine:
    def run_command_and_capture(self, command: str):
        try:
            print(f"{Colors.YELLOW}===== Executing ====={Colors.ENDC}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=os.getcwd())
            print(result.stdout, end="")
            print(result.stderr, end="")
            print(f"{Colors.GREEN}===== Done ====={Colors.ENDC}")
            return result.stdout, result.stderr, result.returncode
        except subprocess.CalledProcessError as e:
            print(e.stdout, end="")
            print(e.stderr, end="")
            print(f"{Colors.RED}===== Command Failed (Exit Code: {e.returncode}) ====={Colors.ENDC}")
            return e.stdout, e.stderr, e.returncode

# Main Application
def main():
    if len(sys.argv) < 2:
        print("Usage: agent <your prompt>")
        return
    initial_prompt = " ".join(sys.argv[1:])
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 Agent activated. Goal:{Colors.ENDC} {initial_prompt}")

    brain, terminal, logger = AgentBrain(), TerminalEngine(), DataLogger(MLOPS_LOG_FILE)
    plan = brain.get_plan(initial_prompt)

    if not plan:
        print(f"{Colors.RED}Agent could not form a plan.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}{Colors.YELLOW}📝 Agent's Plan:{Colors.ENDC}")
    for i, (command, explanation) in enumerate(plan, 1):
        print(f"  {Colors.BOLD}Step {i}:{Colors.ENDC}")
        print(f"    {Colors.CYAN}{command}{Colors.ENDC}")
        print(f"    {Colors.BLUE}↳ {explanation}{Colors.ENDC}")

    confirm = input("\nExecute this plan? [y/n] ").lower().strip()
    if confirm not in ['y', '']:
        print("Execution cancelled.")
        return
    
    executed_steps = []
    
    for command, explanation in plan:
        print(f"\n{Colors.CYAN}▶️  Executing Step: {command}{Colors.ENDC}")
        
        stdout, stderr, exit_code = "", "", 1 # Default to failure
        
        if command.startswith("cd "):
            try:
                directory = command.split(" ", 1)[1]
                os.chdir(os.path.expanduser(directory))
                stdout = f"Changed directory to {os.getcwd()}"
                exit_code = 0
                print(f"{Colors.GREEN}{stdout}{Colors.ENDC}")
            except Exception as e:
                stderr = str(e)
                print(f"{Colors.RED}Failed to change directory: {e}{Colors.ENDC}")
        else:
            stdout, stderr, exit_code = terminal.run_command_and_capture(command)
        
        executed_steps.append({
            "command": command, "explanation": explanation,
            "result": {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}
        })
        
        if exit_code != 0:
            print(f"\n{Colors.BOLD}{Colors.RED}❌ A step failed. Aborting the plan.{Colors.ENDC}")
            break 
    else: 
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Agent finished successfully.{Colors.ENDC}")
        
    logger.log_full_interaction(initial_prompt, executed_steps)


if __name__ == "__main__":
    main()