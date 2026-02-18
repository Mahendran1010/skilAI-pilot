
# ⚡ Skillpilot AI

An intelligent multi-agent system that analyzes daily task logs and transforms inefficient workflows into optimized, structured schedules.

---

## 📌 Project Description

The Skillpilot AI is designed to act as a personal productivity assistant.
It processes unstructured task logs, identifies inefficiencies, and generates an optimized workflow using intelligent analysis and restructuring strategies.

The application provides an interactive dashboard built with Streamlit, allowing users to input workflows and receive AI-driven optimization results instantly.

---

## 🛠 Tech Stack

* **Python** – Core programming language
* **Streamlit** – Frontend framework for building the interactive web application
* **CrewAI** – Multi-agent orchestration framework
* **Groq LLM** – Large Language Model for workflow analysis
* **Requests** – API handling and external calls

---

## 📂 Project Structure

```
workflow-optimizer-ai/
│
├── main.py              # Streamlit user interface
├── crew.py            # AI workflow optimization logic
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

---

## ⚙ Setup Instructions (Run Locally)

Follow these steps to run the project on your system:

### 1️⃣ Clone the Repository

```bash
git clone https:https://github.com/Mahendran1010/skilAI-pilot.git
```

### 2️⃣ (Optional but Recommended) Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python -m streamlit run main.py
```

The application will open in your browser at:

```
http://localhost:8501
```

---

## 🚀 Features

* Multi-agent workflow analysis
* Bottleneck detection
* Intelligent time-blocking
* Structured optimization output
* Clean and responsive UI

---

## 🔮 Future Improvements

* Calendar API integration
* Predictive workload analytics
* Team-level optimization support
