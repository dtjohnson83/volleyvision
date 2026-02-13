# 🏐 VolleyVision — Volleyball Video Analytics

AI-powered volleyball video analysis: player tracking, ball trajectory, rally detection, shot classification, and court heatmaps.

## Stack
- **Backend:** Python 3.11 + FastAPI + supervision + ByteTrack + Roboflow/YOLO
- **Frontend:** Next.js 14 + Tailwind CSS + Recharts
- **Database:** SQLite
- **Deployment:** Docker Compose

## Quick Start (Docker)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## Manual Setup

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Features

- **Video Upload** — Drag & drop MP4/MOV files
- **Player Tracking** — Multi-object tracking with ByteTrack, distance/speed per player
- **Ball Tracking** — Trajectory, speed, serve/spike detection
- **Rally Detection** — Automatic rally start/end, duration
- **Shot Classification** — Serves, spikes, blocks, digs
- **Court Heatmap** — 3x3 zone grid showing player/ball activity
- **Annotated Video** — Bounding boxes, labels, traces overlaid
- **Export** — CSV download of all stats

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload video for processing |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{id}` | Job status + progress |
| GET | `/api/jobs/{id}/stats` | Full analytics JSON |
| GET | `/api/health` | Health check |

## Detection Models

1. **Roboflow** (primary) — `volleyball-tracking/2` from Roboflow Universe (free)
2. **YOLOv8 nano** (fallback) — Detects persons + sports balls, remapped to player/ball classes

No API keys needed — uses open source models only.

## Project Structure

```
volleyvision/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── database.py          # SQLite via aiosqlite
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── routers/upload.py    # Upload + job endpoints
│   │   └── services/
│   │       ├── detector.py      # Roboflow/YOLO detection
│   │       ├── tracker.py       # ByteTrack tracking
│   │       ├── analytics.py     # Volleyball analytics engine
│   │       └── processor.py     # Video processing pipeline
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   └── lib/api.ts           # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
