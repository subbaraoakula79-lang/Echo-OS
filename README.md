# ECHO OS ◈

> A JARVIS-inspired, voice-first AI Operating System and Command Center.

![ECHO OS Interface](https://github.com/user-attachments/assets/echo-placeholder.png) <!-- Note: Replace with actual screenshot later -->

ECHO OS is a premium desktop and mobile AI assistant ecosystem. It replaces traditional interfaces with a conversational, cyberpunk-styled dashboard that acts as a central hub for web searches, memory management, task execution, and system control.

## 🚀 Key Features

*   **Cyberpunk Command Center:** A highly immersive, high-performance UI featuring a 60fps 2D Canvas Hologram energy core, glowing scanlines, and a split-panel modular dashboard.
*   **Voice-First Interaction:** Integrated with OpenAI Realtime WebSockets for ultra-low latency conversational flow, bypassing traditional turn-based STT/TTS latency.
*   **Persistent Memory Core:** The backend retains context over time, storing user preferences and historical data using PostgreSQL and Redis.
*   **Extensible Modules:** Modular sidebar architecture ready to support Calendar sync, Email routing, Web Scanning (via Serper), and local file vault operations.

## 🛠️ Technology Stack

**Frontend (Client)**
*   React 19 + Vite
*   TypeScript
*   Pure Canvas 2D Rendering (High-performance animations)
*   Lucide React / Custom Cyberpunk CSS

**Backend (API + Logic)**
*   FastAPI (Python)
*   LangChain / OpenAI SDK
*   SQLAlchemy (PostgreSQL) + Redis (Caching & WebSockets)

## ⚙️ Local Development Setup

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your API keys (OpenAI, Serper, etc.).
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### 2. Frontend Setup (React/Vite)

1. Open a new terminal tab and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open the provided `localhost` URL in your browser to view the ECHO OS Command Center.

## 📜 License
MIT License. See `LICENSE` for details.
