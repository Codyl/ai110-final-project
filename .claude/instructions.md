# AI110 Final Project TODO List

## Official Requirements (from the assignment)

- **Required files are present:** runnable functional code, a comprehensive `README.md`, a `model_card.md` for reflections, and a System Architecture Diagram saved as a Mermaid source file (`.mmd`, or `.md` with a Mermaid code block) in a `diagrams/` folder.
- **Reproducible execution evidence:** instead of demo screenshots, include reproducible command outputs or interaction logs in Markdown or `.txt` files. Diagram source and any optional supplementary images go in dedicated `/assets` or `/diagrams` folders.
- **Commit history** shows multiple meaningful commits.
- **Standardized documentation:** `README.md` must identify the base project; `model_card.md` must answer all reflection prompts on AI collaboration, biases, and testing results.
- **Demo evidence:** `README.md` contains at least 2-3 example inputs with their outputs pasted as fenced code blocks that demonstrate the system's behavior without relying on a video. A Loom walkthrough is optional; if included, add the link to the README.
- **Final changes are committed and pushed before the deadline.**

## Status Summary (updated 2026-11-08)

Done so far:

- Repo set up and pushed to `github.com/Codyl/ai110-final-project`; 24 commits so far.
- Base project: the Module 1-3 Music Recommender Simulation (content-based scoring of `data/songs.csv`).
- Modular code in `src/`: `song.py`, `user_profile.py`, `song_loader.py`, `scoring.py`, `ranking.py`, `recommender.py`, `player.py`, `song_api.py`, plus CLI (`main.py`) and Streamlit UI (`app.py`).
- Features added: YouTube IDs and embedded player, song lookup/add via API, "All songs" modal table, artist de-duplication, small random bonus.
- Tests in `tests/` (scoring, recommend, recommender, YouTube); `pytest.ini` configured. Last recorded result in the model card: 75 pass, 3 fail.
- `model_card.md` drafted (intended use, how it works, data, strengths, limitations/bias, evaluation of 7 profiles, future work, personal reflection).
- `.venv` created; `assets/` and `diagrams/` folders exist (both still empty).

Still open (blocking submission):

- Mermaid architecture diagram in `diagrams/`.
- README is still mostly the starter template; sample output is stale (from an older catalog).
- Model card needs explicit AI-collaboration answers (helpful and flawed AI suggestions) and testing-results wording; fix or document the 3 failing tests.
- Reproducible evidence file (command outputs / logs) and 2-3 fenced example input/output pairs in the README.
- Push, and confirm the repo is public.

## Project Setup

- [x] Choose one of your previous projects from Modules 1–3 to extend into a complete applied AI system.
- [x] Create a new public GitHub repository.
- [x] Name it something professional (e.g., `applied-ai-system-project`).
- [x] Do **not** initialize the repository with a README, license, or `.gitignore`.
- [x] Copy the URL of the new repository.
- [x] Clone your original repository into a new folder.
- [x] Enter the cloned project folder.
- [x] Update the Git remote to point to the new repository.
- [x] Push the project to the new repository.
- [x] Verify the code and commit history appear in the new GitHub repository.

## Folder Structure

- [x] Create an `assets` folder for system architecture images.
- [x] Create a `diagrams` folder.
- [ ] Save the System Architecture Diagram as a Mermaid source file (must be in `diagrams/`).
- [ ] Store the diagram as either:
  - [ ] `diagrams/architecture.mmd`, or
  - [ ] a `.md` file containing a Mermaid code block.
- [ ] Ensure the Mermaid source file is included (a PNG alone is not sufficient).
- [ ] Optionally export a PNG for embedding in the README.

## Environment Setup

- [x] Create and initialize a project virtual environment (`venv`).
- [x] Navigate to the cloned repository.
- [x] Create a virtual environment if one does not already exist.
- [x] Activate the virtual environment.
- [ ] Upgrade `pip`.
- [x] Install dependencies from `requirements.txt`.

## Functionality

- [x] Extend a previous project into a complete applied AI system.
- [x] Implement modular components such as retrieval, logic, or agentic planning using Python.

## Design and Architecture

- [x] Design how the system components fit together.
- [ ] Create and include a System Architecture Diagram.

## Documentation

- [x] Create a comprehensive `README.md`.
- [ ] Clearly explain how the AI works.
- [ ] Clearly explain why the system is trustworthy.
- [ ] Identify the base project used for the final project.

## Reliability and Evaluation

- [ ] Test system reliability and guardrails through structured experiments.
- [ ] Document testing results.
- [ ] Include reproducible command outputs or interaction logs in Markdown or `.txt` files.

## Reflection and Ethics

- [x] Create a `model_card.md`.
- [ ] Answer all reflection prompts regarding AI collaboration.
- [ ] Answer all reflection prompts regarding biases.
- [ ] Answer all reflection prompts regarding testing results.

## Demo Evidence

- [ ] Include at least 2–3 example inputs and outputs in `README.md`.
- [ ] Paste examples as fenced code blocks.
- [ ] Demonstrate the system's behavior without relying on a video.
- [ ] Optionally record a Loom walkthrough and add the link to the README.

## Repository Requirements

- [ ] Ensure the repository is public.
- [x] Include runnable functional code.
- [x] Include a comprehensive `README.md`.
- [x] Include `model_card.md`.
- [ ] Include the System Architecture Diagram source file.
- [ ] Store diagram source files in `/diagrams`.
- [ ] Store supplementary images in `/assets` or `/diagrams`.
- [x] Maintain multiple meaningful commits in commit history.

## Final Submission Checklist

- [x] Code is pushed to the correct GitHub repository.
- [ ] Repository is public.
- [ ] All required files are present.
- [ ] Documentation is complete and standardized.
- [ ] Demo evidence is included.
- [ ] Final changes are committed.
- [ ] Final changes are pushed before the deadline.
