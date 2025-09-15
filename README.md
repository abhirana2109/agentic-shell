# Agentic Shell

Agentic Shell is a powerful, AI-powered terminal agent that lives in your native shell. It understands natural language and translates your intent into executable shell commands.

Simply tell the agent what you want to accomplish, it will formulate a plan, show it to you for confirmation, and execute it step-by-step.

## Planned System Architecture to implement
<img width="2980" height="1778" alt="picture" src="https://github.com/user-attachments/assets/1598f103-02c7-4a90-a68c-c56dd2e24a85" />

## Current Features

- **Natural Language to Command:** Convert plain English prompts into accurate shell commands.
- **Multi-Step Task Execution:** Handles complex workflows by breaking them down into logical, sequential steps.
- **Interactive Confirmation:** Always shows you the plan before executing anything, giving you full control to proceed, edit, or cancel.
- **Data Collection:** Captures interaction data locally, building a dataset for future fine-tuning and MLOps.

## Current Installation Process

### 1. Clone the repository

```bash
git clone https://github.com/abhirana2109/agentic-shell.git
cd agentic-shell
```

### 2. System Prerequisites

Ensure your system has the necessary base tools.
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip curl
```
Next, install `uv`, a fast Python package manager that will be used for setting up environments.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Configure Your API Key

The agent requires a Google Gemini API key to communicate with the AI model.

1.  Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Add the key to your shell's configuration file. This makes it securely available to the agent.
    ```bash
    # For bash users (default on Ubuntu)
    echo 'export GEMINI_API_KEY="YOUR_API_KEY_HERE"' >> ~/.bashrc

    # For zsh users, use ~/.zshrc instead
    # echo 'export GEMINI_API_KEY="YOUR_API_KEY_HERE"' >> ~/.zshrc
    ```
    Replace `YOUR_API_KEY_HERE` with your actual key.

3.  Apply the change to your current terminal session:
    ```bash
    # For bash
    source ~/.bashrc

    # For zsh
    # source ~/.zshrc
    ```

### 4. Set Up Python Environments

Now the dependencies for both the "Brain" (the AI server) and the "Engine" (the command-line tool) will be installed.

**A. Set up the Brain:**
```bash
cd agent_brain
uv venv
uv pip install -r requirements.txt
cd ..
```

**B. Set up the Engine:**
```bash
cd engine
uv venv
uv pip install -r requirements.txt
cd ..
```

### 5. Create the `agent` Command

The final step is to create the `agent` command that you'll use to interact with the shell.

1.  Open your shell's configuration file with a text editor.
    ```bash
    # For bash
    nano ~/.bashrc

    # For zsh
    # nano ~/.zshrc
    ```

2.  Scroll to the very end of the file and add the following code block:
    ```bash
    # Terminal Agent Engine Ignition
    agent() {
        # Check if a prompt was provided
        if [ -z "$1" ]; then
            echo "Usage: agent <your prompt>"
            return 1
        fi
        
        # Define the absolute path to your project
        # IMPORTANT: Replace the path below with your actual project path.
        # (run 'pwd' inside the 'agentic-shell' folder to get the path)
        local agent_dir="/path/to/your/agentic-shell"
        
        # Execute the engine with the provided prompt
        "$agent_dir/engine/.venv/bin/python" "$agent_dir/engine/engine.py" "$@"
    }
    ```
    **Crucially, replace `/path/to/your/agentic-shell` with the real, absolute path to your project folder.**

3.  Save the file and exit (`Ctrl+X`, `Y`, `Enter`).

## Current way to run the Agent

The agent operates with two terminal windows: one for the AI Brain and one for you to use the agent.

**Terminal 1 (Start the Brain):**
This terminal will run the AI server. You must keep it running in the background.
```bash
# Navigate to the brain directory
cd ~/agentic-shell/agent_brain

# Activate its environment
source .venv/bin/activate

# Start the server
uvicorn main:app --reload
```
You should see a message that the server is running on `http://127.0.0.1:8000`. **Leave this terminal open.**

**Terminal 2 (Use the Agent):**
Open a **new** terminal window.

1.  First, activate the new `agent` command:
    ```bash
    # For bash
    source ~/.bashrc

    # For zsh
    # source ~/.zshrc
    ```
    (You only need to do this once per new terminal, or it will be available automatically in any future terminals you open.)


2.  Now, you can use the agent! An example below:-
```bash
    $ agent move all files less than ten mb into the files folder
	🤖 Agent activated. Goal: move all files less than ten mb into the files folder
	
	📝 Agents Plan:
	  Step 1:
	    mkdir -p files
	    ↳ Ensures the 'files' directory exists, creating it if necessary.
	  Step 2:
	    find . -maxdepth 1 -type f -size -10M -exec mv {} files/ \;
	    ↳ Finds all files smaller than 10 megabytes in the current directory and moves them into the 'files' directory.
	
	Execute this plan? [y/n] y
	
	▶️  Executing Step: mkdir -p files
	===== Executing =====
	===== Done =====
	
	▶️  Executing Step: find . -maxdepth 1 -type f -size -10M -exec mv {} files/ \;
	===== Executing =====
	===== Done =====
	
	✅ Agent finished successfully.  
```
