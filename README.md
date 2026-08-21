# 🎬 CineX — Machine Learning Movie Recommendation Platform

![CineX Banner](https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&h=400&fit=crop&auto=format)

> A modern, AI-powered movie discovery and recommendation platform featuring K-Nearest Neighbors (KNN) content-based filtering, rich TMDB metadata integration, TMDB-styled 16:9 trailer playback, interactive community reviews, and personalized watchlists.

---

## ✨ Features

- 🧠 **Machine Learning Recommendation Engine**: Uses Scikit-learn's `NearestNeighbors` (KNN cosine similarity) on vectorized movie genres, descriptions, directors, and cast.
- 🎬 **TMDB-Styled Trailer Player**: Centered 16:9 trailer modal with smooth backdrop, keyboard shortcuts (`Esc`), and browser history back button navigation.
- 🔍 **Real-Time Search & Discovery**: Fast search across movie titles, genres, actors, directors, and languages (Tamil, Telugu, Malayalam, Hindi, Kannada, English).
- 🏷️ **Watchlist & Favorites**: Client-side persistent watchlist and liked movie collections with zero intrusive alerts.
- ⭐ **Rating & Community Reviews**: Star rating system with full review CRUD support (add, edit, delete your own reviews).
- 📱 **Mobile Optimized UI**: Seamless bottom navigation bar and touch-friendly controls.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Bundler**: Vite
- **Styling**: Tailwind CSS + Custom Design System
- **Icons & Typography**: DM Serif Display, Outfit, JetBrains Mono

### Backend & Machine Learning
- **Framework**: FastAPI (Python 3.10+)
- **ML / Data**: Scikit-learn (`NearestNeighbors`, `CountVectorizer`), Pandas, NumPy
- **Metadata API**: The Movie Database (TMDB) API + YouTube Embed Integration

---

## 📁 Project Structure

```
cinex-movie-recommendation/
├── backend/                      # FastAPI & Machine Learning Backend
│   ├── data/                     # Cleaned movie metadata & features
│   ├── main.py                   # FastAPI REST endpoints
│   ├── recommender.py            # KNN recommendation algorithm
│   ├── tmdb.py                   # TMDB API client & enricher
│   ├── models.py                 # Pydantic schema models
│   └── requirements.txt          # Python dependencies
├── dataset/                      # Raw datasets & CSV data
│   └── master_movies.csv         # Master movie dataset
├── src/                          # React + TypeScript Frontend
│   ├── components/               # UI components
│   ├── services/                 # API client & services
│   ├── App.tsx                   # Main application root
│   ├── main.tsx                  # Vite entry point
│   └── index.css                 # Global design system & animations
├── index.html                    # HTML template
├── package.json                  # Node.js dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite configuration
└── README.md                     # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/) (v3.10 or higher)
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
python -m venv venv
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```
> The backend API will be available at `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`).

---

## 🔑 Environment Variables

Create a `.env` file in the root directory (refer to `.env.example`):

```env
VITE_TMDB_API_KEY=your_tmdb_api_key_here
```

---

## 👨‍💻 Author

**Lakshmadeepan**  
- [LinkedIn Profile](https://www.linkedin.com/in/lakshma-deepan-76bb2537a)  
- [GitHub Repository](https://github.com/Lakshmadeepan)

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
