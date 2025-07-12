# Demo Video Link
https://www.loom.com/share/726e133046a9469c8e3282af8735e123?sid=5ef66ec9-3e65-4974-8b68-fa56e1e52357

#  AI-Powered UGC Video Platform – Backend

This is the backend scode for a **buzzly** that takes structured product data and outputs a marketing video with a realistic avatar. It leverages OpenAI agents, HeyGen, DALL·E, RunwayML, and other state-of-the-art tools for dynamic content generation.

---

## 🚀 Key Features

-  **Agentic Workflow with OpenAI Agents SDK**
  - A **research agent** performs market research using the `WebSearchTool`.
  - An **outline agent** generates and refines a script structure via an iterative **checker agent**.
  - A final **script agent** creates the full marketing video script.

-  **AI Avatar Generation**
  - The final script is passed to **HeyGen API** to generate an avatar delivering the script using specified `avatar_id` and `voice_id`.

-  **Audio Processing & Transcription**
  - Audio is extracted using **FFmpeg**.
  - Transcription with timestamps is generated using **OpenAI Whisper**.

-  **B-Roll Generation**
  - **Timestamp selection & b-roll description** done by OpenAI.
  - Two-tiered descriptions:
    - **Static descriptions** for image generation with **DALL·E**.
    - **Dynamic descriptions** optimized via **prompt engineering** for **RunwayML**.

-  **Video Composition**
  - DALL·E images animated with **RunwayML**.
  - B-roll and A-roll stitched into final video using **FFmpeg**.

-  **Captioning**
  - Final video is sent to **ZapCap** for automatic caption generation.

---

## 🛠️ Tech Stack

- **AI Models & APIs:** OpenAI GPT-4, Whisper, DALL·E, HeyGen API, RunwayML, ZapCap
- **Multimedia Tools:** FFmpeg
- **Infrastructure:** Docker, Render.com
- **Storage:** Firebase Storage, Firestore
- **Other:** Python, UUID for file-safe temporary paths

---

## 📦 System Architecture

```plaintext
[ Product Info ]
      ↓
[ OpenAI Agent System ]
  ↳ Research Agent
  ↳ Outline Agent
  ↳ Script Agent
      ↓
[ Script ]
      ↓
[ HeyGen API (Avatar + Voice) ]
      ↓
[ FFmpeg (Extract Audio) ]
      ↓
[ Whisper (Transcription + Timestamps) ]
      ↓
[ OpenAI (B-roll Planning + Descriptions) ]
      ↳ Static Description → DALL·E
      ↳ Dynamic Description → RunwayML
      ↓
[ B-roll + A-roll ]
      ↓
[ FFmpeg (Final Video) ]
      ↓
[ ZapCap (Captioning) ]
      ↓
[ Firebase Upload + Firestore Save ]
