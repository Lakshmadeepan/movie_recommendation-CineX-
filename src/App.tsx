import { useState, useRef, useEffect } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────
interface Movie {
  id: number;
  title: string;
  year: number;
  rating: number;
  language: string;
  genres: string[];
  runtime: string;
  overview: string;
  tagline: string;
  director: string;
  poster: string;
  backdrop: string;
  trailerId: string;
  cast: { name: string; role: string; photo: string }[];
  streaming: { name: string; logo: string; color: string }[];
}

// ─── Mock Data ────────────────────────────────────────────────────────────────
const MOVIES: Movie[] = [
  {
    id: 1,
    title: "Maari",
    year: 2015,
    rating: 6.0,
    language: "Tamil",
    genres: ["Action", "Comedy"],
    runtime: "2h 18m",
    overview: "A feared local rowdy, known for his dominance in the streets and pigeon racing, finds himself at odds with a newly appointed police officer. As tensions rise, hidden motives and betrayals unfold, shaking the balance of power in the neighborhood.",
    tagline: "The most wanted rowdy is back",
    director: "Balaji Mohan",
    poster: "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
    trailerId: "bk5lKWDVJAI",
    cast: [
      { name: "Dhanush", role: "Maari", photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format" },
      { name: "Kajal Aggarwal", role: "Sridevi", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
      { name: "Robo Shankar", role: "Kader", photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format" },
      { name: "Vijay Yesudas", role: "ACP", photo: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&auto=format" },
      { name: "Kalaiyarasan", role: "Sub-Inspector", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format" },
      { name: "M. S. Bhaskar", role: "Vetri", photo: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [
      { name: "Amazon Prime", logo: "▶", color: "#00A8E1" },
      { name: "Netflix", logo: "N", color: "#E50914" },
    ],
  },
  {
    id: 2,
    title: "Vikram",
    year: 2022,
    rating: 8.4,
    language: "Tamil",
    genres: ["Action", "Thriller"],
    runtime: "2h 55m",
    overview: "A special agent is tasked with finding the person responsible for a series of masked vigilante murders. The investigation uncovers a dark conspiracy involving a powerful drug cartel.",
    tagline: "One mission. One truth.",
    director: "Lokesh Kanagaraj",
    poster: "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format",
    trailerId: "OKBMCL-0BVU",
    cast: [
      { name: "Kamal Haasan", role: "Vikram", photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format" },
      { name: "Fahadh Faasil", role: "Amar", photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format" },
      { name: "Vijay Sethupathi", role: "Santhanam", photo: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&auto=format" },
      { name: "Suriya", role: "Rolex", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Disney+ Hotstar", logo: "✦", color: "#0A3CA8" }],
  },
  {
    id: 3,
    title: "KGF Chapter 2",
    year: 2022,
    rating: 8.2,
    language: "Kannada",
    genres: ["Action", "Drama"],
    runtime: "2h 48m",
    overview: "Rocky's bloodthirsty rage has caught the eye of Adheera, a fierce warrior from the Kolar Gold Fields' past. Meanwhile, the government wants him dead.",
    tagline: "The most powerful empire rises.",
    director: "Prashanth Neel",
    poster: "https://images.unsplash.com/photo-1611174777809-c8dcea724bb7?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
    trailerId: "xnvLkHMmIKo",
    cast: [
      { name: "Yash", role: "Rocky", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format" },
      { name: "Sanjay Dutt", role: "Adheera", photo: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=200&h=200&fit=crop&auto=format" },
      { name: "Raveena Tandon", role: "Ramika Sen", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Amazon Prime", logo: "▶", color: "#00A8E1" }],
  },
  {
    id: 4,
    title: "Pushpa: The Rise",
    year: 2021,
    rating: 7.6,
    language: "Telugu",
    genres: ["Action", "Drama", "Crime"],
    runtime: "2h 59m",
    overview: "Pushpa Raj, a truck driver, rises through the ranks of red sandalwood smuggling syndicate while being chased by a relentless cop.",
    tagline: "Thaggede Le.",
    director: "Sukumar",
    poster: "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1518929458119-e5bf444c30f4?w=1400&h=600&fit=crop&auto=format",
    trailerId: "Q1NKMPhP8PY",
    cast: [
      { name: "Allu Arjun", role: "Pushpa Raj", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format" },
      { name: "Rashmika Mandanna", role: "Srivalli", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
      { name: "Fahadh Faasil", role: "SP Bhanwar Singh", photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Amazon Prime", logo: "▶", color: "#00A8E1" }, { name: "Netflix", logo: "N", color: "#E50914" }],
  },
  {
    id: 5,
    title: "RRR",
    year: 2022,
    rating: 7.9,
    language: "Telugu",
    genres: ["Action", "Drama", "History"],
    runtime: "3h 7m",
    overview: "A fictional story about two legendary revolutionaries and their journey away from home before they started fighting for their country in the 1920s.",
    tagline: "Rise. Roar. Revolt.",
    director: "S. S. Rajamouli",
    poster: "https://images.unsplash.com/photo-1543622748-5ee7237e8565?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1518929458119-e5bf444c30f4?w=1400&h=600&fit=crop&auto=format",
    trailerId: "f_AczdmmkqA",
    cast: [
      { name: "N. T. Rama Rao Jr.", role: "Komaram Bheem", photo: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&auto=format" },
      { name: "Ram Charan", role: "A. Rama Raju", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format" },
      { name: "Alia Bhatt", role: "Sita", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Netflix", logo: "N", color: "#E50914" }],
  },
  {
    id: 6,
    title: "Master",
    year: 2021,
    rating: 7.8,
    language: "Tamil",
    genres: ["Action", "Thriller"],
    runtime: "2h 59m",
    overview: "An alcoholic professor is sent to a juvenile school where he must confront a dangerous gangster using the students as tools for his crimes.",
    tagline: "Thalapathy is here.",
    director: "Lokesh Kanagaraj",
    poster: "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
    trailerId: "Pc9S-yvB4uo",
    cast: [
      { name: "Vijay", role: "JD", photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format" },
      { name: "Vijay Sethupathi", role: "Bhavani", photo: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=200&h=200&fit=crop&auto=format" },
      { name: "Malavika Mohanan", role: "Charulatha", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Amazon Prime", logo: "▶", color: "#00A8E1" }],
  },
  {
    id: 7,
    title: "Bahubali: The Beginning",
    year: 2015,
    rating: 8.0,
    language: "Telugu",
    genres: ["Action", "Drama", "Fantasy"],
    runtime: "2h 39m",
    overview: "A young man raised by jungle tribes discovers his true royal heritage and fights to reclaim his kingdom from the cruel uncle who usurped the throne.",
    tagline: "The Beginning of an Epic.",
    director: "S. S. Rajamouli",
    poster: "https://images.unsplash.com/photo-1611174777809-c8dcea724bb7?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format",
    trailerId: "x2CzVNF2sTU",
    cast: [
      { name: "Prabhas", role: "Bahubali", photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format" },
      { name: "Rana Daggubati", role: "Bhallaladeva", photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format" },
      { name: "Anushka Shetty", role: "Devasena", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Netflix", logo: "N", color: "#E50914" }, { name: "Amazon Prime", logo: "▶", color: "#00A8E1" }],
  },
  {
    id: 8,
    title: "Kabali",
    year: 2016,
    rating: 5.9,
    language: "Tamil",
    genres: ["Action", "Drama"],
    runtime: "2h 35m",
    overview: "An aging gangster from Malaysia leads a civil rights movement for Tamil workers while searching for his missing wife and daughter.",
    tagline: "The Don is back.",
    director: "Pa. Ranjith",
    poster: "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400&h=600&fit=crop&auto=format",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
    trailerId: "YRqaAjyITQo",
    cast: [
      { name: "Rajinikanth", role: "Kabali", photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format" },
      { name: "Radhika Apte", role: "Yogi", photo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format" },
      { name: "Dhansika", role: "Kumari", photo: "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=200&h=200&fit=crop&auto=format" },
    ],
    streaming: [{ name: "Netflix", logo: "N", color: "#E50914" }],
  },
];

const GENRES = ["Action", "Comedy", "Thriller", "Romance", "Sci-Fi", "Drama", "Crime", "Fantasy", "History"];
const LANGUAGES = ["Tamil", "Telugu", "Malayalam", "Hindi", "Kannada", "English"];

// ─── Rating Circle ────────────────────────────────────────────────────────────
function RatingCircle({ rating, size = "md" }: { rating: number; size?: "sm" | "md" | "lg" }) {
  const pct = Math.round((rating / 10) * 100);
  const color = rating >= 7 ? "#22C55E" : rating >= 5 ? "#F59E0B" : "#EF4444";
  const dims = size === "lg" ? 72 : size === "md" ? 52 : 36;
  const stroke = size === "lg" ? 5 : 3.5;
  const r = (dims - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const fontSize = size === "lg" ? "text-base font-bold" : size === "md" ? "text-xs font-bold" : "text-[10px] font-bold";

  return (
    <div className="relative inline-flex items-center justify-center bg-[#0D1117] rounded-full" style={{ width: dims, height: dims }}>
      <svg width={dims} height={dims} className="absolute inset-0 -rotate-90">
        <circle cx={dims / 2} cy={dims / 2} r={r} fill="none" stroke="#2D2520" strokeWidth={stroke} />
        <circle cx={dims / 2} cy={dims / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round" />
      </svg>
      <span className={`${fontSize} text-white z-10`}>{pct}<span style={{ fontSize: "0.55em" }}>%</span></span>
    </div>
  );
}

// ─── Genre Badge ──────────────────────────────────────────────────────────────
function GenreBadge({ genre }: { genre: string }) {
  return (
    <span className="inline-block px-3 py-0.5 bg-stone-100 text-stone-600 text-xs font-medium rounded-full border border-stone-200">
      {genre}
    </span>
  );
}

// ─── Movie Card ───────────────────────────────────────────────────────────────
function MovieCard({ movie, onClick }: { movie: Movie; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="group relative flex-shrink-0 w-40 md:w-44 text-left rounded-xl overflow-hidden bg-white shadow-sm border border-stone-100 hover:shadow-lg hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-amber-400"
      style={{ transition: "transform 0.2s, box-shadow 0.2s" }}>
      <div className="relative overflow-hidden bg-stone-200" style={{ paddingBottom: "150%" }}>
        <img src={movie.poster} alt={movie.title}
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-105"
          style={{ transition: "transform 0.4s" }} />
        <div className="absolute top-2 left-2">
          <RatingCircle rating={movie.rating} size="sm" />
        </div>
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/70 to-transparent" />
      </div>
      <div className="p-2.5">
        <p className="text-xs font-semibold text-stone-800 line-clamp-1 leading-tight">{movie.title}</p>
        <p className="text-[11px] text-stone-400 mt-0.5">{movie.year} · {movie.language}</p>
      </div>
    </button>
  );
}

// ─── Movie Grid Card ──────────────────────────────────────────────────────────
function MovieGridCard({ movie, onClick }: { movie: Movie; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="group text-left rounded-xl overflow-hidden bg-white shadow-sm border border-stone-100 hover:shadow-lg hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-amber-400"
      style={{ transition: "transform 0.2s, box-shadow 0.2s" }}>
      <div className="relative overflow-hidden bg-stone-200" style={{ paddingBottom: "150%" }}>
        <img src={movie.poster} alt={movie.title}
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-105"
          style={{ transition: "transform 0.4s" }} />
        <div className="absolute top-2 left-2">
          <RatingCircle rating={movie.rating} size="sm" />
        </div>
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/70 to-transparent" />
      </div>
      <div className="p-3">
        <p className="text-sm font-semibold text-stone-800 line-clamp-1">{movie.title}</p>
        <p className="text-xs text-stone-400 mt-0.5">{movie.year}</p>
        <div className="flex flex-wrap gap-1 mt-1.5">
          {movie.genres.slice(0, 2).map(g => <GenreBadge key={g} genre={g} />)}
        </div>
        <p className="text-xs font-medium text-amber-600 mt-1.5">{movie.language}</p>
      </div>
    </button>
  );
}

// ─── Skeleton Loader ──────────────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="flex-shrink-0 w-40 md:w-44 rounded-xl overflow-hidden bg-white shadow-sm border border-stone-100 animate-pulse">
      <div className="bg-stone-200" style={{ paddingBottom: "150%" }} />
      <div className="p-2.5 space-y-1.5">
        <div className="h-3 bg-stone-200 rounded w-3/4" />
        <div className="h-2.5 bg-stone-100 rounded w-1/2" />
      </div>
    </div>
  );
}

// ─── Movie Carousel ───────────────────────────────────────────────────────────
function MovieCarousel({ title, movies, onSelect }: { title: string; movies: Movie[]; onSelect: (m: Movie) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const scroll = (dir: "l" | "r") => {
    if (ref.current) ref.current.scrollBy({ left: dir === "r" ? 320 : -320, behavior: "smooth" });
  };
  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-4 px-4 md:px-8">
        <h2 className="font-display text-2xl text-stone-800">{title}</h2>
        <div className="flex gap-2">
          <button onClick={() => scroll("l")} className="w-8 h-8 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 hover:text-stone-800">‹</button>
          <button onClick={() => scroll("r")} className="w-8 h-8 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 hover:text-stone-800">›</button>
        </div>
      </div>
      <div ref={ref} className="flex gap-4 overflow-x-auto scroll-hide snap-x px-4 md:px-8 pb-2">
        {movies.map(m => <MovieCard key={m.id} movie={m} onClick={() => onSelect(m)} />)}
      </div>
    </section>
  );
}

// ─── Navbar ───────────────────────────────────────────────────────────────────
function Navbar({ onHome, onSearch, searchQuery, setSearchQuery }: {
  onHome: () => void;
  onSearch: (q: string) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) onSearch(searchQuery.trim());
  };

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-stone-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center h-16 gap-6">
          {/* Logo */}
          <button onClick={onHome} className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center">
              <span className="text-amber-400 font-bold text-sm font-mono-data">CX</span>
            </div>
            <span className="font-display text-lg text-stone-800 hidden sm:block">CineX</span>
          </button>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6 flex-1">
            <button onClick={onHome} className="text-sm font-medium text-stone-600 hover:text-stone-900">Home</button>
            <button onClick={() => onSearch("")} className="text-sm font-medium text-stone-600 hover:text-stone-900">Movies</button>
            <div className="relative group">
              <button className="text-sm font-medium text-stone-600 hover:text-stone-900">Genres ▾</button>
              <div className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-lg border border-stone-100 p-3 grid grid-cols-2 gap-1 w-48 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto" style={{ transition: "opacity 0.15s" }}>
                {GENRES.map(g => <button key={g} onClick={() => onSearch(g)} className="text-xs text-stone-600 hover:text-amber-600 text-left px-2 py-1 rounded hover:bg-stone-50">{g}</button>)}
              </div>
            </div>
            <div className="relative group">
              <button className="text-sm font-medium text-stone-600 hover:text-stone-900">Language ▾</button>
              <div className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-lg border border-stone-100 p-3 flex flex-col gap-1 w-36 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto" style={{ transition: "opacity 0.15s" }}>
                {LANGUAGES.map(l => <button key={l} onClick={() => onSearch(l)} className="text-xs text-stone-600 hover:text-amber-600 text-left px-2 py-1 rounded hover:bg-stone-50">{l}</button>)}
              </div>
            </div>
          </div>

          {/* Search bar */}
          <form onSubmit={handleSearch} className={`${searchOpen ? "flex flex-1" : "hidden md:flex"} items-center relative`}>
            <input ref={inputRef} value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search movies, actors or genres..."
              className="w-full md:w-72 pl-9 pr-4 py-2 text-sm bg-stone-50 border border-stone-200 rounded-full focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent placeholder-stone-400" />
            <span className="absolute left-3 text-stone-400 text-sm">🔍</span>
            {searchQuery && (
              <button type="button" onClick={() => setSearchQuery("")} className="absolute right-3 text-stone-300 hover:text-stone-500 text-sm">✕</button>
            )}
          </form>

          {/* Mobile icons */}
          <div className="flex md:hidden items-center gap-2 ml-auto">
            <button onClick={() => { setSearchOpen(s => !s); setTimeout(() => inputRef.current?.focus(), 100); }} className="w-8 h-8 flex items-center justify-center text-stone-500">🔍</button>
            <button onClick={() => setMobileOpen(s => !s)} className="w-8 h-8 flex items-center justify-center text-stone-500">
              {mobileOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden py-3 border-t border-stone-100 flex flex-col gap-1">
            <button onClick={() => { onHome(); setMobileOpen(false); }} className="text-sm text-stone-600 hover:text-stone-900 text-left px-2 py-2">Home</button>
            <button onClick={() => { onSearch(""); setMobileOpen(false); }} className="text-sm text-stone-600 hover:text-stone-900 text-left px-2 py-2">Movies</button>
            {LANGUAGES.map(l => <button key={l} onClick={() => { onSearch(l); setMobileOpen(false); }} className="text-sm text-stone-500 hover:text-amber-600 text-left px-4 py-1.5">{l}</button>)}
          </div>
        )}
      </div>
    </nav>
  );
}

// ─── Trailer Modal ────────────────────────────────────────────────────────────
function TrailerModal({ trailerId, title, onClose }: { trailerId: string; title: string; onClose: () => void }) {
  useEffect(() => {
    const handle = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handle);
    document.body.style.overflow = "hidden";
    return () => { window.removeEventListener("keydown", handle); document.body.style.overflow = ""; };
  }, [onClose]);

  return (
    <div className="trailer-backdrop fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-black/85 backdrop-blur-sm"
      onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="trailer-modal relative w-full max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-stone-400 text-xs uppercase tracking-widest font-mono-data">Official Trailer</p>
            <h3 className="font-display text-white text-xl md:text-2xl">{title}</h3>
          </div>
          <button onClick={onClose}
            className="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white text-lg transition-colors">
            ✕
          </button>
        </div>

        {/* Video */}
        <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-black" style={{ paddingBottom: "56.25%" }}>
          <iframe
            src={`https://www.youtube.com/embed/${trailerId}?autoplay=1&rel=0&modestbranding=1`}
            title={`${title} Official Trailer`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
            allowFullScreen
            className="absolute inset-0 w-full h-full"
          />
        </div>

        {/* Footer hint */}
        <p className="text-center text-stone-500 text-xs mt-3">Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white font-mono-data text-[10px]">Esc</kbd> or click outside to close</p>
      </div>
    </div>
  );
}

// ─── Home Page ────────────────────────────────────────────────────────────────
function HomePage({ onSearch, onSelect }: { onSearch: (q: string) => void; onSelect: (m: Movie) => void }) {
  const [query, setQuery] = useState("");
  const heroMovies = MOVIES.slice(0, 3);
  const [heroIdx, setHeroIdx] = useState(0);
  const hero = heroMovies[heroIdx];

  useEffect(() => {
    const t = setInterval(() => setHeroIdx(i => (i + 1) % heroMovies.length), 6000);
    return () => clearInterval(t);
  }, []);

  const trending = MOVIES;
  const popular = [...MOVIES].sort((a, b) => b.rating - a.rating);
  const tamil = MOVIES.filter(m => m.language === "Tamil");

  return (
    <div>
      {/* Hero */}
      <div className="relative h-[65vh] min-h-[420px] overflow-hidden">
        <img key={hero.id} src={hero.backdrop} alt={hero.title}
          className="absolute inset-0 w-full h-full object-cover"
          style={{ transition: "opacity 0.8s" }} />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#FAF8F4] via-transparent to-transparent" />

        <div className="relative z-10 h-full flex flex-col justify-center px-6 md:px-16 max-w-4xl">
          <p className="text-amber-400 text-xs font-mono-data uppercase tracking-widest mb-3">Now Trending</p>
          <h1 className="font-display text-4xl md:text-6xl text-white leading-tight mb-2">{hero.title}</h1>
          <p className="text-stone-300 text-sm md:text-base max-w-md mb-6 line-clamp-2">{hero.overview}</p>

          {/* Search */}
          <form onSubmit={e => { e.preventDefault(); if (query.trim()) onSearch(query.trim()); }}
            className="flex items-center bg-white rounded-full shadow-xl overflow-hidden max-w-xl">
            <span className="pl-4 text-stone-400">🔍</span>
            <input value={query} onChange={e => setQuery(e.target.value)}
              placeholder="Search movies, actors or genres..."
              className="flex-1 px-3 py-3.5 text-sm text-stone-800 bg-transparent focus:outline-none placeholder-stone-400" />
            <button type="submit" className="m-1 bg-amber-500 hover:bg-amber-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold">
              Search
            </button>
          </form>

          {/* Hero indicators */}
          <div className="flex gap-2 mt-5">
            {heroMovies.map((_, i) => (
              <button key={i} onClick={() => setHeroIdx(i)}
                className={`h-1 rounded-full transition-all ${i === heroIdx ? "w-8 bg-amber-400" : "w-3 bg-white/40 hover:bg-white/60"}`} />
            ))}
          </div>
        </div>

        {/* View details btn */}
        <button onClick={() => onSelect(hero)}
          className="absolute bottom-8 right-6 md:right-16 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white px-4 py-2 rounded-full text-sm font-medium">
          View Details ›
        </button>
      </div>

      {/* Genre chips */}
      <div className="px-4 md:px-8 py-6 border-b border-stone-100">
        <div className="flex flex-wrap gap-2">
          {[...LANGUAGES, ...GENRES].map(chip => (
            <button key={chip} onClick={() => onSearch(chip)}
              className="px-4 py-1.5 rounded-full text-xs font-medium border border-stone-200 bg-white text-stone-600 hover:bg-stone-900 hover:text-white hover:border-stone-900"
              style={{ transition: "all 0.15s" }}>
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Carousels */}
      <div className="bg-[#FAF8F4]">
        <MovieCarousel title="Trending Now" movies={trending} onSelect={onSelect} />
        <div className="border-t border-stone-100" />
        <MovieCarousel title="Top Rated" movies={popular} onSelect={onSelect} />
        <div className="border-t border-stone-100" />
        <MovieCarousel title="Tamil Cinema" movies={tamil} onSelect={onSelect} />
      </div>
    </div>
  );
}

// ─── Search Results ───────────────────────────────────────────────────────────
function SearchResults({ query, onSelect, onBack }: { query: string; onSelect: (m: Movie) => void; onBack: () => void }) {
  const [localQuery, setLocalQuery] = useState(query);
  const [activeQuery, setActiveQuery] = useState(query);

  const results = activeQuery
    ? MOVIES.filter(m =>
      m.title.toLowerCase().includes(activeQuery.toLowerCase()) ||
      m.language.toLowerCase().includes(activeQuery.toLowerCase()) ||
      m.genres.some(g => g.toLowerCase().includes(activeQuery.toLowerCase())) ||
      m.director.toLowerCase().includes(activeQuery.toLowerCase()) ||
      m.cast.some(c => c.name.toLowerCase().includes(activeQuery.toLowerCase()))
    )
    : MOVIES;

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
      {/* Search header */}
      <div className="mb-6">
        <button onClick={onBack} className="text-stone-400 hover:text-stone-600 text-sm mb-3 flex items-center gap-1">
          ← Back to Home
        </button>
        <form onSubmit={e => { e.preventDefault(); setActiveQuery(localQuery); }}
          className="flex items-center bg-white border border-stone-200 rounded-full overflow-hidden shadow-sm max-w-xl">
          <span className="pl-4 text-stone-400">🔍</span>
          <input value={localQuery} onChange={e => setLocalQuery(e.target.value)}
            placeholder="Search movies, actors or genres..."
            className="flex-1 px-3 py-3 text-sm text-stone-800 bg-transparent focus:outline-none" />
          {localQuery && <button type="button" onClick={() => { setLocalQuery(""); setActiveQuery(""); }} className="pr-3 text-stone-300 hover:text-stone-500">✕</button>}
        </form>
        <p className="mt-3 text-sm text-stone-500">
          {activeQuery ? <>Showing <span className="font-semibold text-stone-700">{results.length}</span> results for "<span className="text-amber-600">{activeQuery}</span>"</> : `All movies (${results.length})`}
        </p>
      </div>

      {results.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🎬</div>
          <h3 className="font-display text-xl text-stone-600 mb-2">No movies found</h3>
          <p className="text-stone-400 text-sm">Try searching for a different title, genre, or language.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {results.map(m => <MovieGridCard key={m.id} movie={m} onClick={() => onSelect(m)} />)}
        </div>
      )}
    </div>
  );
}

// ─── Movie Details ─────────────────────────────────────────────────────────────
function MovieDetailsPage({ movie, onBack, onSelect }: { movie: Movie; onBack: () => void; onSelect: (m: Movie) => void }) {
  const [trailerOpen, setTrailerOpen] = useState(false);
  const [tab, setTab] = useState<"overview" | "cast" | "media">("overview");

  const recommended = MOVIES.filter(m =>
    m.id !== movie.id && (m.language === movie.language || m.genres.some(g => movie.genres.includes(g)))
  );
  const carouselRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen">
      {/* Hero backdrop */}
      <div className="relative" style={{ minHeight: 480 }}>
        <img src={movie.backdrop} alt={movie.title} className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/60 to-black/30" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#FAF8F4] via-transparent to-transparent" />

        {/* Back */}
        <button onClick={onBack} className="absolute top-5 left-4 md:left-8 z-10 bg-black/40 hover:bg-black/60 backdrop-blur-sm border border-white/20 text-white px-3 py-1.5 rounded-full text-sm flex items-center gap-1">
          ← Back
        </button>

        <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 pt-16 pb-10 flex flex-col md:flex-row gap-8 items-start">
          {/* Poster */}
          <div className="flex-shrink-0 mx-auto md:mx-0">
            <div className="w-48 md:w-56 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/10 bg-stone-200">
              <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover" style={{ aspectRatio: "2/3" }} />
            </div>
            {/* Streaming */}
            <div className="mt-3 space-y-2">
              {movie.streaming.map(s => (
                <div key={s.name} className="flex items-center gap-2 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2">
                  <span className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold text-white" style={{ background: s.color }}>{s.logo}</span>
                  <div>
                    <p className="text-[10px] text-stone-400 font-mono-data">STREAMING ON</p>
                    <p className="text-white text-xs font-semibold">{s.name}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-xs border border-stone-400 text-stone-300 px-2 py-0.5 rounded font-mono-data">U</span>
              <span className="text-stone-300 text-sm">{new Date(movie.year, 6, 17).toLocaleDateString("en-IN", { day: "2-digit", month: "2-digit", year: "numeric" })}</span>
              <span className="text-stone-500">·</span>
              {movie.genres.map(g => <span key={g} className="text-stone-300 text-sm">{g}</span>).reduce((a, b) => <>{a}<span className="text-stone-500">, </span>{b}</>)}
              <span className="text-stone-500">·</span>
              <span className="text-stone-300 text-sm">{movie.runtime}</span>
            </div>

            <h1 className="font-display text-4xl md:text-5xl text-white mb-1">{movie.title}</h1>
            {movie.tagline && <p className="text-stone-400 italic text-base mb-4">"{movie.tagline}"</p>}

            {/* Rating + actions */}
            <div className="flex flex-wrap items-center gap-4 mb-6">
              <div className="flex items-center gap-3">
                <RatingCircle rating={movie.rating} size="lg" />
                <div>
                  <p className="text-white font-semibold text-sm">User Score</p>
                  <p className="text-stone-400 text-xs font-mono-data">{Math.round(movie.rating * 10)}% liked</p>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setTrailerOpen(true)}
                  className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white px-5 py-2.5 rounded-full font-semibold text-sm shadow-lg hover:shadow-amber-500/30"
                  style={{ transition: "all 0.2s" }}>
                  <span className="text-base">▶</span> Play Trailer
                </button>
                <button className="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white px-4 py-2.5 rounded-full text-sm">
                  <span>♥</span> Favourite
                </button>
                <button className="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white px-4 py-2.5 rounded-full text-sm">
                  <span>🔖</span> Watchlist
                </button>
              </div>
            </div>

            {/* Overview on desktop */}
            <div className="hidden md:block">
              <p className="text-stone-300 text-sm md:text-base leading-relaxed max-w-2xl mb-4">{movie.overview}</p>
              <div className="flex items-center gap-3">
                <div>
                  <p className="text-white font-semibold text-sm">{movie.director}</p>
                  <p className="text-stone-400 text-xs">Director</p>
                </div>
                <div className="w-px h-8 bg-white/20" />
                <div>
                  <p className="text-white font-semibold text-sm">{movie.language}</p>
                  <p className="text-stone-400 text-xs">Language</p>
                </div>
                <div className="w-px h-8 bg-white/20" />
                <div>
                  <p className="text-white font-semibold text-sm">{movie.runtime}</p>
                  <p className="text-stone-400 text-xs">Runtime</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content tabs */}
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex gap-0 border-b border-stone-200 mb-6">
          {(["overview", "cast", "media"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-3 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${tab === t ? "border-amber-500 text-amber-600" : "border-transparent text-stone-500 hover:text-stone-800"}`}>
              {t === "cast" ? "Top Billed Cast" : t === "media" ? "Media & Trailer" : "Overview"}
            </button>
          ))}
        </div>

        {tab === "overview" && (
          <div className="grid md:grid-cols-3 gap-8 pb-8">
            <div className="md:col-span-2 space-y-6">
              <div>
                <h3 className="font-display text-xl text-stone-800 mb-2">Overview</h3>
                <p className="text-stone-600 leading-relaxed">{movie.overview}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Director", value: movie.director },
                  { label: "Language", value: movie.language },
                  { label: "Runtime", value: movie.runtime },
                  { label: "Release Year", value: String(movie.year) },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-stone-50 rounded-xl p-4">
                    <p className="text-xs text-stone-400 font-mono-data uppercase tracking-wide mb-1">{label}</p>
                    <p className="text-stone-800 font-medium text-sm">{value}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-xs text-stone-400 font-mono-data uppercase tracking-wide mb-2">Genres</p>
                <div className="flex flex-wrap gap-2">
                  {movie.genres.map(g => (
                    <span key={g} className="px-3 py-1 bg-stone-900 text-white text-xs font-medium rounded-full">{g}</span>
                  ))}
                </div>
              </div>
            </div>
            {/* Where to watch sidebar */}
            <div className="space-y-4">
              <div className="bg-stone-50 rounded-2xl p-5 border border-stone-100">
                <h4 className="font-semibold text-stone-800 mb-3 text-sm">Where to Watch</h4>
                <div className="space-y-2.5">
                  {movie.streaming.map(s => (
                    <div key={s.name} className="flex items-center gap-3 p-2.5 bg-white rounded-xl border border-stone-100 hover:border-stone-200 cursor-pointer" style={{ transition: "border-color 0.15s" }}>
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-white flex-shrink-0" style={{ background: s.color }}>{s.logo}</div>
                      <div>
                        <p className="text-xs font-semibold text-stone-800">{s.name}</p>
                        <p className="text-[10px] text-stone-400">Stream Now</p>
                      </div>
                      <span className="ml-auto text-stone-300 text-xs">›</span>
                    </div>
                  ))}
                </div>
              </div>
              <button onClick={() => setTrailerOpen(true)}
                className="w-full relative rounded-2xl overflow-hidden group cursor-pointer border-0 p-0">
                <img src={movie.backdrop} alt="Trailer thumbnail" className="w-full h-36 object-cover group-hover:scale-105" style={{ transition: "transform 0.3s" }} />
                <div className="absolute inset-0 bg-black/50 group-hover:bg-black/40 flex flex-col items-center justify-center gap-2" style={{ transition: "background 0.2s" }}>
                  <div className="w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center text-white text-xl shadow-lg group-hover:scale-110" style={{ transition: "transform 0.2s" }}>▶</div>
                  <span className="text-white text-xs font-semibold tracking-wide uppercase">Official Trailer</span>
                </div>
              </button>
            </div>
          </div>
        )}

        {tab === "cast" && (
          <div className="pb-8">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {movie.cast.map(c => (
                <div key={c.name} className="text-center group cursor-pointer">
                  <div className="relative w-full rounded-xl overflow-hidden bg-stone-200 shadow-sm group-hover:shadow-md mb-2" style={{ paddingBottom: "130%", transition: "box-shadow 0.2s" }}>
                    <img src={c.photo} alt={c.name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-105" style={{ transition: "transform 0.3s" }} />
                  </div>
                  <p className="text-sm font-semibold text-stone-800 line-clamp-1">{c.name}</p>
                  <p className="text-xs text-stone-400">{c.role}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === "media" && (
          <div className="pb-8 space-y-6">
            <div>
              <h3 className="font-display text-xl text-stone-800 mb-4">Official Trailer</h3>
              <button onClick={() => setTrailerOpen(true)}
                className="relative w-full max-w-2xl rounded-2xl overflow-hidden group cursor-pointer border-0 p-0 block">
                <img src={movie.backdrop} alt="Trailer" className="w-full object-cover h-64 group-hover:scale-102" style={{ transition: "transform 0.3s", aspectRatio: "16/9" }} />
                <div className="absolute inset-0 bg-black/50 group-hover:bg-black/40 flex flex-col items-center justify-center gap-3" style={{ transition: "background 0.2s" }}>
                  <div className="w-16 h-16 bg-amber-500 rounded-full flex items-center justify-center text-white text-2xl shadow-xl group-hover:scale-110" style={{ transition: "transform 0.2s" }}>▶</div>
                  <div className="text-center">
                    <p className="text-white font-bold text-lg uppercase tracking-wide">Official Trailer</p>
                    <p className="text-stone-300 text-sm">{movie.title} · {movie.year}</p>
                  </div>
                </div>
              </button>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-stone-500 uppercase tracking-widest font-mono-data mb-3">Backdrops</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[movie.backdrop, movie.poster, movie.backdrop].map((src, i) => (
                  <div key={i} className="rounded-xl overflow-hidden bg-stone-200 aspect-video">
                    <img src={src} alt={`Backdrop ${i + 1}`} className="w-full h-full object-cover hover:scale-105 cursor-pointer" style={{ transition: "transform 0.3s" }} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {recommended.length > 0 && (
        <div className="border-t border-stone-100 bg-[#FAF8F4]">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between px-4 md:px-8 pt-8 pb-4">
              <div>
                <h2 className="font-display text-2xl text-stone-800">Recommended For You</h2>
                <p className="text-stone-400 text-sm mt-0.5">Because you watched <span className="text-amber-600">{movie.title}</span></p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => carouselRef.current?.scrollBy({ left: -320, behavior: "smooth" })} className="w-8 h-8 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100">‹</button>
                <button onClick={() => carouselRef.current?.scrollBy({ left: 320, behavior: "smooth" })} className="w-8 h-8 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100">›</button>
              </div>
            </div>
            <div ref={carouselRef} className="flex gap-4 overflow-x-auto scroll-hide snap-x px-4 md:px-8 pb-8">
              {recommended.map(m => <MovieCard key={m.id} movie={m} onClick={() => onSelect(m)} />)}
            </div>
          </div>
        </div>
      )}

      {trailerOpen && <TrailerModal trailerId={movie.trailerId} title={movie.title} onClose={() => setTrailerOpen(false)} />}
    </div>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────
function Footer() {
  return (
    <footer className="bg-stone-900 text-stone-400 py-12 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 bg-amber-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs font-mono-data">CX</span>
              </div>
              <span className="font-display text-white text-base">CineX</span>
            </div>
            <p className="text-xs leading-relaxed text-stone-500">Your premium movie discovery platform. Find, explore, and enjoy cinema from around the world.</p>
          </div>
          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Navigate</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="#" className="hover:text-white transition-colors">Home</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Movies</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Genres</a></li>
              <li><a href="#" className="hover:text-white transition-colors">About</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Languages</h4>
            <ul className="space-y-2 text-xs">
              {LANGUAGES.map(l => <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>)}
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Connect</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="https://www.linkedin.com/in/lakshma-deepan-76bb2537a" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-2"><span className="w-4 h-4 bg-blue-600 rounded flex items-center justify-center text-[10px] font-bold text-white">in</span>LinkedIn</a></li>
              <li><a href="https://github.com/Lakshmadeepan" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-2"><span className="w-4 h-4 bg-stone-700 rounded flex items-center justify-center text-[10px] font-bold text-white">gh</span>GitHub</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-stone-800 pt-6 flex flex-col md:flex-row items-center justify-between gap-2">
          <p className="text-xs text-stone-500">© 2024 CineX. Built using TMDB API.</p>
          <p className="text-xs text-stone-500">Developed by <a href="https://www.linkedin.com/in/lakshma-deepan-76bb2537a" target="_blank" rel="noopener noreferrer" className="text-amber-400 font-medium hover:text-amber-300 transition-colors">Lakshmadeepan</a> · Data from TMDB</p>
        </div>
      </div>
    </footer>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
type Page = "home" | "search" | "details";

export default function App() {
  const [page, setPage] = useState<Page>("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setPage("search");
  };

  const handleSelect = (m: Movie) => {
    setSelectedMovie(m);
    setPage("details");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleHome = () => {
    setPage("home");
    setSearchQuery("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#FAF8F4] flex flex-col">
      <Navbar
        onHome={handleHome}
        onSearch={handleSearch}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      <main className="flex-1">
        {page === "home" && <HomePage onSearch={handleSearch} onSelect={handleSelect} />}
        {page === "search" && <SearchResults query={searchQuery} onSelect={handleSelect} onBack={handleHome} />}
        {page === "details" && selectedMovie && (
          <MovieDetailsPage movie={selectedMovie} onBack={() => setPage(searchQuery ? "search" : "home")} onSelect={handleSelect} />
        )}
      </main>

      <Footer />
    </div>
  );
}
