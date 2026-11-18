# Commands

Commands for working on this project. Run all of them from the project folder unless a note says otherwise.

Last updated: 2026-11-18

## 1. Getting started (machine and project folder)

This project has no dev container yet: there is no `.devcontainer/` folder, and Docker only comes in at Milestone 9. For now, "booting up" means opening a terminal, going to the project folder and turning on the venv (section 2).

| Step | Command | Notes |
| --- | --- | --- |
| Go to the project | `cd ~/Local-AI-Project` | |
| Get the latest changes | `git pull` | Then reinstall packages (section 2) |
| Connect to the Ubuntu GPU workstation | `ssh <user>@<workstation-host>` | Not set up yet: fill in the user and host |
| Check that Docker is installed | `docker --version` | Milestone 9 only. Docker is installed outside the venv |

## 2. Virtual environment and packages (uv)

The packages are listed in `requirements.txt` and installed into `.venv`, which uses Python 3.12. Your system `python3` may be a different version, so turn on the venv first.

| Task | Command | Notes |
| --- | --- | --- |
| Create the venv (first time only) | `uv venv --python 3.12` | Creates `.venv/` |
| Turn on the venv | `source .venv/bin/activate` | Your prompt then shows `(.venv)` |
| Turn off the venv | `deactivate` | |
| Install or update packages | `uv pip install -r requirements.txt` | Re-run after every `git pull` |
| Add a new package | `uv pip install <package>` | Then add `<package>==<version>` to `requirements.txt` |
| List installed packages | `uv pip list` | |
| Check which Python is running | `which python` and `python --version` | Should be `.venv/bin/python`, version 3.12 |
| Check that a package imports | `python -c "import pydantic; print(pydantic.VERSION)"` | |

## 3. Running project files

| Task | Command | Notes |
| --- | --- | --- |
| Run the quote search (CLI) | `python main.py` | Asks for a part number, then reads `data/sample_quotes.csv` |
| Run the model experiment | `python model.py` | Needs Ollama running (section 4) |
| Run without activating the venv | `.venv/bin/python main.py` | Same result as activating first |
| Open a Python shell to test ideas | `python` | Type `exit()` to leave |
| Load a file, then stay in the shell | `python -i main.py` | Useful for calling `load_quotes(...)` by hand |

## 4. Ollama (models)

The models run in Ollama at `http://localhost:11434`. `localhost` means the machine that is running Python.

Note (2026-11-18): the `ollama` command was not found in this Mac's terminal. Either install Ollama, or start the Ollama app and make sure its command-line tool is on your `PATH`.

| Task | Command | Notes |
| --- | --- | --- |
| Start the server | `ollama serve` | Not needed if the Ollama app is already running |
| Check that the server is reachable | `curl http://localhost:11434/api/version` | Prints a version number. "Connection refused" means the server is off |
| List downloaded models | `ollama list` | Expected: `qwen3.5:9b`, `qwen3.6:35b`, `local-coder` |
| Show loaded models | `ollama ps` | Lists models currently in memory |
| Download a model | `ollama pull qwen3.5:9b` | |
| Chat with a model in the terminal | `ollama run qwen3.5:9b` | Type `/bye` to exit |
| Show a model's details | `ollama show qwen3.5:9b` | Context length, parameters, template |
| Unload a model from memory | `ollama stop qwen3.5:9b` | |
| Remove a model | `ollama rm <model>` | Deletes the downloaded files |
| Use the workstation's Ollama from Python | `OLLAMA_HOST=http://<workstation-host>:11434 python model.py` | The workstation must listen on all interfaces (next row) |
| Let other machines reach this server | `OLLAMA_HOST=0.0.0.0 ollama serve` | Run this on the workstation |

## 5. Git

| Task | Command |
| --- | --- |
| See what changed | `git status` |
| See the exact line changes | `git diff` |
| Get the latest from GitHub | `git pull` |
| Stage files | `git add <file>` |
| Commit | `git commit -m "message"` |
| Push to GitHub | `git push` |
| See recent history | `git log --oneline -10` |
| Discard changes to one file | `git restore <file>` (cannot be undone) |

## 6. Claude Code learning commands

Type these inside Claude Code. They are defined in `.claude/commands/`.

| Command | Use it to |
| --- | --- |
| `/lesson` or `/lesson 2.2` | Start or continue a curriculum lesson |
| `/checkpoint` | Check and record that a lesson is done |
| `/learn` | Start a short learning session |
| `/hint` | Make a prediction first, then get hints one at a time |
| `/debug` | Debug by testing your own guesses about the cause |
| `/autopsy` | Write up what you learned from a bug you fixed |
| `/read` | Work through unfamiliar code, one question at a time |
| `/explain` | Explain a concept from memory |
| `/api` | Study a library or API (for example, `pydantic`) |
| `/arch` | Design a feature through an interview |
| `/explore` | Compare design options |
| `/test` | Work out tests before you write the code |
| `/learn-review` | Get your code reviewed without it being rewritten |
| `/retrieve` | Do a short review drawn from your learning logs |
| `/model` | Switch the Claude model |
| `! <command>` | Run a shell command from the Claude Code prompt |
