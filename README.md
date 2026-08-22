# 🎬 CineX — AI/ML Movie Recommendation Platform

![CineX Banner](https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&h=400&fit=crop&auto=format)

> A modern, AI-powered movie discovery and recommendation platform featuring a TF-IDF + K-Nearest Neighbors (KNN) content-based recommendation engine, smart typo-tolerant fuzzy search, rich TMDB metadata integration, 16:9 trailer player modal, interactive community reviews, and persistent watchlists.

---

## ✨ Key Features

- 🧠 **Machine Learning Recommendation Engine**: 
  - Weighted **TF-IDF Vectorizer** (60,000 max features, sublinear term frequency scaling, n-gram range `(1, 2)`).
  - Cosine distance **K-Nearest Neighbors (`NearestNeighbors`)** with balanced feature weights: Title (3x), Genres (4x), Director (3x), Lead Cast (2x), and Plot Overview (2x).
  - Dynamic fallback for newly released / TMDB-only movies without full model retraining.
- 🔍 **Smart Fuzzy Search**: Handles spelling mistakes, typos, phonetic approximations, actor names, and director names.
- 🎬 **TMDB-Styled Trailer Player**: Centered 16:9 trailer modal with smooth backdrop, keyboard shortcuts (`Esc`), and browser history back button navigation.
- ⭐ **Accurate Ratings**: Real IMDb / TMDB ratings displayed dynamically.
- 🏷️ **Watchlist & Favorites**: Client-side persistent watchlist and liked movie collections.
- 💬 **Community Reviews**: Star rating system with full review CRUD support (add, edit, delete).
- 📱 **Mobile Optimized UI**: Seamless bottom navigation bar and responsive layouts.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Bundler**: Vite
- **Styling**: Tailwind CSS v4 + Custom Glassmorphism Design System
- **Deployment**: Netlify

### Backend & Machine Learning
- **Framework**: FastAPI (Python 3.10+)
- **ML / NLP**: Scikit-learn (`NearestNeighbors`, `TfidfVectorizer`), Pandas, NumPy
- **Metadata API**: The Movie Database (TMDB) API + YouTube Embed Integration
- **Deployment**: Render / Railway / Heroku

---

## 📁 Project Structure

```
cinex-movie-recommendation/
├── backend/                      # FastAPI & Machine Learning Backend
│   ├── main.py                   # FastAPI REST endpoints & CORS
│   ├── recommender.py            # KNN recommendation algorithm & search
│   ├── tmdb.py                   # TMDB API client & dynamic enricher
│   ├── prepare_features.py       # Weighted TF-IDF feature pipeline
│   ├── models.py                 # Pydantic schema models
│   ├── requirements.txt          # Python dependencies
│   └── data/                     # Seed fallback data
├── dataset/                      # Dataset & ML Model Artifacts
│   ├── create_master_dataset.py  # Ingestion & cleaning script
│   ├── master_movies.csv         # Clean master dataset (20,074 movies)
│   ├── movies_features.csv       # Preprocessed weighted text features
│   ├── tfidf_matrix.pkl          # Sparse TF-IDF matrix
│   └── tfidf_vectorizer.pkl      # Fitted Scikit-learn vectorizer
├── src/                          # React + TypeScript Frontend
│   ├── components/               # UI components
│   ├── services/                 # API client & fallback data
│   ├── App.tsx                   # Main application root
│   ├── main.tsx                  # Vite entry point
│   └── index.css                 # Global design system & theme
├── public/                       # Static public assets & _redirects
│   └── _redirects                # Netlify SPA redirect rule
├── netlify.toml                  # Netlify build configuration
├── index.html                    # HTML template
├── package.json                  # Node.js dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite build & proxy configuration
└── .env.example                  # Environment template
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.10+)
- [Git](https://git-scm.com/)

---

### 2. Frontend Setup

```bash
# Install frontend dependencies
npm install

# Start Vite development server
npm run dev
```
> The frontend will be available at `http://localhost:8443` (or `http://localhost:5173`).

---

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.main:app --reload --port 8000
```
> Interactive Swagger API docs: `http://localhost:8000/docs`

---

## 🌐 Deployment Guide

### Deploying Frontend to Netlify

1. Push this repository to GitHub.
2. Log in to [Netlify](https://www.netlify.com/) and click **"Add new site"** -> **"Import an existing project"**.
3. Select your GitHub repository.
4. Set the build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Under **Environment variables**, set:
   - `VITE_TMDB_API_KEY`: `your_tmdb_api_key`
   - `VITE_API_URL`: `https://your-backend-api.onrender.com` (your deployed backend URL)
6. Click **"Deploy site"**.

### Deploying Backend to Render / Railway

1. Connect your repository to [Render](https://render.com/) or [Railway](https://railway.app/).
2. Create a new **Web Service**:
   - **Root Directory**: `backend` (or leave root and set start command)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `TMDB_API_KEY`: `your_tmdb_api_key`
   - `CORS_ORIGINS`: `https://your-app.netlify.app,http://localhost:5173`

---

## 📄 License

This project is licensed under the MIT License.
