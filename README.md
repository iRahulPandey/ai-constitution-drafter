# ⚖️ AI Constitution Drafter

> **Automated Governance System powered by Multi-Agent AI**

The **AI Constitution Drafter** is an agentic system that researches, judges, and drafts binding governance constitutions for AI use cases. Unlike standard content generators, this system employs a **"Check-and-Balance" architecture** where a Researcher gathers legal frameworks, a Judge validates enforceability (acting as a Supreme Court), and a Builder drafts the final machine-readable document.

## 🚀 Key Features

* **🕵️ Legal Research Agent:** Scours real-world frameworks (GDPR, Geneva Convention, HIPAA) to find relevant precedents.
* **👨‍⚖️ Supreme Court Judge Agent:** A strict gatekeeper that approves, rejects, or amends principles based on enforceability and safety.
* **📜 Constitutional Drafter:** Generates formal legalese and **GEO-Optimized (Generative Engine Optimization)** axioms for machine readability.
* **📡 Microservices Architecture:** Distributed agents communicating via the **Agent-to-Agent (A2A)** protocol.

---

## 🏗️ Architecture

The system runs as a distributed set of microservices orchestrated to simulate a governance council.

| Service | Port | Role | Persona |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `8000` | **The Coordinator** | Manages the loop, hosts the Frontend, and enforces the pipeline. |
| **Researcher** | `8001` | **The Specialist** | Forensic legal researcher. Returns structured risks & principles. |
| **Judge** | `8002` | **The Arbiter** | Validates findings. Issues binding verdicts & constraints. |
| **Builder** | `8003` | **The Drafter** | Writes the final `AIConstitution` object with citable axioms. |

**The Workflow:**
1.  User submits a use case (e.g., *"Autonomous Military Drone"*).
2.  **Researcher** finds relevant treaties (e.g., *Geneva Convention*) and risks.
3.  **Judge** reviews every principle. *Rejects* vague ones. *Amends* weak ones.
4.  **Builder** compiles the approved principles into a formal Constitution.

---

## 🛠️ Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Google Cloud Project** (with Vertex AI API enabled)

### Quick Start

We use `make` to handle dependencies and execution.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/iRahulPandey/ai-constitution-drafter.git](https://github.com/iRahulPandey/ai-constitution-drafter.git)
    cd ai-constitution-drafter
    ```

2.  **Install Dependencies:**
    This command automatically installs `uv` (a fast Python package manager) and syncs all dependencies.
    ```bash
    make install
    ```

3.  **Run the System:**
    This starts all 4 agents on ports 8000-8003.
    ```bash
    make run-local
    ```

4.  **Access the Interface:**
    Open your browser and navigate to:
    👉 **http://localhost:8000**

---
