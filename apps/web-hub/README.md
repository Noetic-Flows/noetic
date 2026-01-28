# Noetic Web Hub

**Role:** Universal Access Portal
**Topology:** Reference Client (Hub)
**Stack:** Next.js + FastUI + ASP

The **Web Hub** is the browser-based entry point into your Noetic Network. It adheres to the **"Software 3.0"** paradigm: it contains almost no business logic. Instead, it is a high-performance **Remote Renderer** for the Agents running on your Workhorse (Engine).

## 🌟 Capabilities

1.  **Universal Access:** Log in from any browser (Desktop, Tablet, Phone) to access your Study.
2.  **Optimistic UI:** Interactions feel instant (Local-First), ensuring 60fps responsiveness even when the Agent is "Thinking."
3.  **Agent Server Protocol (ASP):** Connects to your Noetic Engine via Secure WebSockets (mTLS).

## 🏗 Architecture

The Hub is a "Thin Client" that implements the **Noetic Stage** protocol.

*   **ASP Client:** Manages the secure tunnel to your Engine.
*   **Canvas Renderer:** Dynamically renders the `A2UI` (Abstract Agent UI) JSON tree sent by the Agent.
*   **Local State:** Handles transient interactions (typing, scrolling) locally before syncing "Committed Intents" to the Engine.

## 🚀 Getting Started

1.  **Configure ASP Connection:**
    *   Set `NOETIC_ENGINE_URL` (e.g., `wss://home-desktop.tailscale.net:8080`)
    *   Set `NOETIC_CLIENT_CERT` (Your User Identity)

2.  **Run Development Server:**
    ```bash
    npm run dev
    ```

## 🔒 Security

*   **Zero-Trust:** Uses **mTLS** authentication. The Hub cannot connect to the Engine without a valid User Certificate.
*   **Sovereignty:** All data remains on your Engine (Workhorse). The Web Hub caches strictly what is needed for the current session.
