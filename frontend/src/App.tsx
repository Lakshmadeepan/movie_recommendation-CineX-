import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import {
  type Movie,
  FALLBACK_MOVIES,
  getTrendingMovies,
  getTopRatedMovies,
  getTamilMovies,
  getMovieById,
  getRecommendations,
  searchMovies,
} from "./services/api";

const GENRES = ["Action", "Comedy", "Thriller", "Romance", "Sci-Fi", "Drama", "Crime", "Fantasy", "History"];
const LANGUAGES = ["Tamil", "Telugu", "Malayalam", "Hindi", "Kannada", "English"];

const DEFAULT_POSTER = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&h=750&fit=crop&auto=format";

// ─── Interfaces ───────────────────────────────────────────────────────────────
export interface UserComment {
  id: string;
  movieId: number;
  author: string;
  text: string;
  rating?: number;
  createdAt: string;
  updatedAt?: string;
  isUserOwned: boolean;
}

// ─── Default Sample Comments for Popular Movies ──────────────────────────────
const SAMPLE_COMMUNITY_COMMENTS: Record<string, Omit<UserComment, "id" | "movieId" | "isUserOwned">[]> = {
  default: [
    {
      author: "Cinephile_99",
      text: "Outstanding cinematography and screenplay! Must watch on the big screen.",
      rating: 5,
      createdAt: "2 days ago",
    },
    {
      author: "Aravind K.",
      text: "Solid direction and gripping narrative throughout the second half.",
      rating: 4,
      createdAt: "1 week ago",
    }
  ]
};

// ─── Rating Circle ────────────────────────────────────────────────────────────
function RatingCircle({ rating, size = "md" }: { rating: number; size?: "sm" | "md" | "lg" }) {
  const safeRating = typeof rating === "number" && !isNaN(rating) && rating > 0 ? rating : 0;
  const pct = Math.round((safeRating / 10) * 100);
  const color = safeRating >= 7 ? "#22C55E" : safeRating >= 5 ? "#F59E0B" : safeRating > 0 ? "#EF4444" : "#57534E";
  const dims = size === "lg" ? 64 : size === "md" ? 46 : 34;
  const stroke = size === "lg" ? 4.5 : 3;
  const r = (dims - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const dash = safeRating > 0 ? (pct / 100) * circ : 0;
  const fontSize = size === "lg" ? "text-xs font-bold" : size === "md" ? "text-[10px] font-bold" : "text-[8px] font-bold";
  const displayText = safeRating > 0 ? safeRating.toFixed(1) : "—";

  return (
    <div className="relative inline-flex items-center justify-center bg-[#0D1117] rounded-full shadow-md flex-shrink-0" style={{ width: dims, height: dims }}>
      <svg width={dims} height={dims} className="absolute inset-0 -rotate-90">
        <circle cx={dims / 2} cy={dims / 2} r={r} fill="none" stroke="#2D2520" strokeWidth={stroke} />
        <circle cx={dims / 2} cy={dims / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round" />
      </svg>
      <span className={`${fontSize} text-white z-10 font-mono-data`}>{displayText}</span>
    </div>
  );
}

// ─── Genre Badge ──────────────────────────────────────────────────────────────
function GenreBadge({ genre }: { genre: string }) {
  return (
    <span className="inline-block px-2 py-0.5 bg-stone-100 text-stone-600 text-[10px] sm:text-[11px] font-medium rounded-full border border-stone-200">
      {genre}
    </span>
  );
}

// ─── Star Rating Component ────────────────────────────────────────────────────
function StarRating({
  rating,
  onRate,
  readOnly = false,
  size = "md",
}: {
  rating: number;
  onRate?: (r: number) => void;
  readOnly?: boolean;
  size?: "sm" | "md" | "lg";
}) {
  const [hoverRating, setHoverRating] = useState<number | null>(null);

  const starSizes = {
    sm: "text-sm",
    md: "text-xl sm:text-2xl",
    lg: "text-2xl sm:text-3xl",
  };

  const active = hoverRating !== null ? hoverRating : rating;

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const isFilled = star <= active;
        return (
          <button
            key={star}
            type="button"
            disabled={readOnly}
            onClick={() => onRate && onRate(star === rating ? 0 : star)}
            onMouseEnter={() => !readOnly && setHoverRating(star)}
            onMouseLeave={() => !readOnly && setHoverRating(null)}
            className={`${starSizes[size]} ${
              readOnly ? "cursor-default" : "cursor-pointer hover:scale-115 active:scale-95"
            } transition-transform p-0.5 focus:outline-none touch-manipulation`}
            title={readOnly ? `${rating}/5 stars` : `Rate ${star} star${star > 1 ? "s" : ""}`}
          >
            <span className={isFilled ? "text-amber-400 drop-shadow-sm" : "text-stone-300"}>
              ★
            </span>
          </button>
        );
      })}
    </div>
  );
}

// ─── Movie Card ───────────────────────────────────────────────────────────────
function MovieCard({
  movie,
  onClick,
  isFavorite,
  isWatchlist,
  onToggleFavorite,
  onToggleWatchlist,
  staggerIdx = 1,
}: {
  movie: Movie;
  onClick: () => void;
  isFavorite: boolean;
  isWatchlist: boolean;
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
  staggerIdx?: number;
}) {
  return (
    <div
      onClick={onClick}
      className={`group relative flex-shrink-0 w-32 sm:w-40 md:w-44 text-left rounded-xl overflow-hidden bg-white shadow-xs border border-stone-200/80 hover:shadow-lg hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer card-stagger-${Math.min(staggerIdx, 6)} active:scale-98`}
      style={{ transition: "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s" }}
    >
      <div className="relative overflow-hidden bg-stone-200" style={{ paddingBottom: "150%" }}>
        <img
          src={movie.poster || DEFAULT_POSTER}
          alt={movie.title}
          onError={(e) => {
            if (e.currentTarget.src !== DEFAULT_POSTER) {
              e.currentTarget.src = DEFAULT_POSTER;
            }
          }}
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-106"
          style={{ transition: "transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)" }}
        />
        <div className="absolute top-1.5 left-1.5 sm:top-2 sm:left-2">
          <RatingCircle rating={movie.rating} size="sm" />
        </div>

        {/* Action icons with touch-friendly hit areas */}
        <div className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 flex flex-col gap-1.5 z-10">
          <button
            onClick={(e) => onToggleFavorite(e, movie)}
            className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs backdrop-blur-md transition-all active:scale-80 shadow-md ${
              isFavorite ? "bg-red-500 text-white heart-pop" : "bg-black/60 text-white/80 hover:bg-black/85 hover:text-white"
            }`}
            title={isFavorite ? "Remove from Favorites" : "Add to Favorites"}
          >
            {isFavorite ? "♥" : "♡"}
          </button>
          <button
            onClick={(e) => onToggleWatchlist(e, movie)}
            className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs backdrop-blur-md transition-all active:scale-80 shadow-md ${
              isWatchlist ? "bg-amber-500 text-white bookmark-bounce" : "bg-black/60 text-white/80 hover:bg-black/85 hover:text-white"
            }`}
            title={isWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
          >
            {isWatchlist ? "🔖" : "🏷️"}
          </button>
        </div>

        <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-black/80 via-black/30 to-transparent pointer-events-none" />
      </div>
      <div className="p-2 sm:p-2.5">
        <p className="text-[11px] sm:text-xs font-bold text-stone-800 line-clamp-1 leading-tight">{movie.title}</p>
        <p className="text-[10px] sm:text-[11px] text-stone-400 mt-0.5">{movie.year ? movie.year : "Recent"} · {movie.language}</p>
      </div>
    </div>
  );
}

// ─── Movie Grid Card ──────────────────────────────────────────────────────────
function MovieGridCard({
  movie,
  onClick,
  isFavorite,
  isWatchlist,
  onToggleFavorite,
  onToggleWatchlist,
  staggerIdx = 1,
}: {
  movie: Movie;
  onClick: () => void;
  isFavorite: boolean;
  isWatchlist: boolean;
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
  staggerIdx?: number;
}) {
  return (
    <div
      onClick={onClick}
      className={`group relative text-left rounded-xl overflow-hidden bg-white shadow-xs border border-stone-200/80 hover:shadow-lg hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer card-stagger-${Math.min(staggerIdx, 6)} active:scale-98`}
      style={{ transition: "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s" }}
    >
      <div className="relative overflow-hidden bg-stone-200" style={{ paddingBottom: "150%" }}>
        <img
          src={movie.poster || DEFAULT_POSTER}
          alt={movie.title}
          onError={(e) => {
            if (e.currentTarget.src !== DEFAULT_POSTER) {
              e.currentTarget.src = DEFAULT_POSTER;
            }
          }}
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-106"
          style={{ transition: "transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)" }}
        />
        <div className="absolute top-1.5 left-1.5 sm:top-2 sm:left-2">
          <RatingCircle rating={movie.rating} size="sm" />
        </div>

        {/* Action icons */}
        <div className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 flex flex-col gap-1.5 z-10">
          <button
            onClick={(e) => onToggleFavorite(e, movie)}
            className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs backdrop-blur-md transition-all active:scale-80 shadow-md ${
              isFavorite ? "bg-red-500 text-white heart-pop" : "bg-black/60 text-white/80 hover:bg-black/85 hover:text-white"
            }`}
            title={isFavorite ? "Remove from Favorites" : "Add to Favorites"}
          >
            {isFavorite ? "♥" : "♡"}
          </button>
          <button
            onClick={(e) => onToggleWatchlist(e, movie)}
            className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs backdrop-blur-md transition-all active:scale-80 shadow-md ${
              isWatchlist ? "bg-amber-500 text-white bookmark-bounce" : "bg-black/60 text-white/80 hover:bg-black/85 hover:text-white"
            }`}
            title={isWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
          >
            {isWatchlist ? "🔖" : "🏷️"}
          </button>
        </div>

        <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-black/80 via-black/30 to-transparent pointer-events-none" />
      </div>
      <div className="p-2 sm:p-3">
        <p className="text-xs sm:text-sm font-bold text-stone-800 line-clamp-1">{movie.title}</p>
        <p className="text-[10px] sm:text-xs text-stone-400 mt-0.5">{movie.year ? movie.year : "Recent"}</p>
        <div className="flex flex-wrap gap-1 mt-1">
          {movie.genres?.slice(0, 2).map((g) => (
            <GenreBadge key={g} genre={g} />
          ))}
        </div>
        <p className="text-[11px] sm:text-xs font-semibold text-amber-600 mt-1">{movie.language}</p>
      </div>
    </div>
  );
}

// ─── Movie Carousel ───────────────────────────────────────────────────────────
function MovieCarousel({
  title,
  subtitle,
  movies,
  onSelect,
  favorites,
  watchlist,
  onToggleFavorite,
  onToggleWatchlist,
}: {
  title: string;
  subtitle?: string;
  movies: Movie[];
  onSelect: (m: Movie) => void;
  favorites: Movie[];
  watchlist: Movie[];
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const scroll = (dir: "l" | "r") => {
    if (ref.current) ref.current.scrollBy({ left: dir === "r" ? 300 : -300, behavior: "smooth" });
  };

  if (!movies || movies.length === 0) return null;

  return (
    <section className="py-5 sm:py-7">
      <div className="flex items-center justify-between mb-2.5 px-4 md:px-8">
        <div>
          <h2 className="font-display text-xl sm:text-2xl text-stone-800 tracking-tight">{title}</h2>
          {subtitle && <p className="text-[11px] sm:text-xs text-stone-400 mt-0.5">{subtitle}</p>}
        </div>
        <div className="hidden sm:flex gap-1.5">
          <button
            onClick={() => scroll("l")}
            className="w-7 h-7 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 hover:text-stone-800 cursor-pointer shadow-2xs"
          >
            ‹
          </button>
          <button
            onClick={() => scroll("r")}
            className="w-7 h-7 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 hover:text-stone-800 cursor-pointer shadow-2xs"
          >
            ›
          </button>
        </div>
      </div>
      <div ref={ref} className="flex gap-3 sm:gap-4 overflow-x-auto scroll-hide snap-x px-4 md:px-8 pb-2 pt-1">
        {movies.map((m, idx) => (
          <MovieCard
            key={m.id}
            movie={m}
            onClick={() => onSelect(m)}
            isFavorite={favorites.some((f) => f.id === m.id)}
            isWatchlist={watchlist.some((w) => w.id === m.id)}
            onToggleFavorite={onToggleFavorite}
            onToggleWatchlist={onToggleWatchlist}
            staggerIdx={(idx % 6) + 1}
          />
        ))}
      </div>
    </section>
  );
}

// ─── Top Navbar ───────────────────────────────────────────────────────────────
function Navbar({
  onHome,
  onSearch,
  onOpenWatchlist,
  onOpenFavorites,
  searchQuery,
  setSearchQuery,
  watchlistCount,
  favoritesCount,
  activeTab,
}: {
  onHome: () => void;
  onSearch: (q: string) => void;
  onOpenWatchlist: () => void;
  onOpenFavorites: () => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  watchlistCount: number;
  favoritesCount: number;
  activeTab: "home" | "movies" | "watchlist" | "favorites" | "details";
}) {
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
      setMobileSearchOpen(false);
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-stone-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16 gap-3 sm:gap-6">
          {/* Logo */}
          <button onClick={onHome} className="flex items-center gap-2 flex-shrink-0 cursor-pointer group">
            <div className="w-8 h-8 sm:w-9 sm:h-9 bg-stone-900 rounded-xl flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <span className="text-amber-400 font-bold text-xs sm:text-sm font-mono-data">CX</span>
            </div>
            <span className="font-display text-lg sm:text-xl text-stone-800 tracking-tight">CineX</span>
          </button>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-5 flex-1">
            <button
              onClick={onHome}
              className={`text-sm font-medium transition-colors cursor-pointer ${
                activeTab === "home" ? "text-amber-600 font-semibold" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onSearch("")}
              className={`text-sm font-medium transition-colors cursor-pointer ${
                activeTab === "movies" ? "text-amber-600 font-semibold" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Explore
            </button>
            <button
              onClick={onOpenWatchlist}
              className={`text-sm font-medium flex items-center gap-1.5 transition-colors cursor-pointer ${
                activeTab === "watchlist" ? "text-amber-600 font-semibold" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              <span>🔖 Watchlist</span>
              {watchlistCount > 0 && (
                <span className="px-1.5 py-0.2 bg-amber-100 text-amber-800 text-[10px] font-bold rounded-full">
                  {watchlistCount}
                </span>
              )}
            </button>
            <button
              onClick={onOpenFavorites}
              className={`text-sm font-medium flex items-center gap-1.5 transition-colors cursor-pointer ${
                activeTab === "favorites" ? "text-amber-600 font-semibold" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              <span>♥ Liked</span>
              {favoritesCount > 0 && (
                <span className="px-1.5 py-0.2 bg-red-100 text-red-700 text-[10px] font-bold rounded-full">
                  {favoritesCount}
                </span>
              )}
            </button>

            {/* Genres dropdown */}
            <div className="relative group">
              <button className="text-sm font-medium text-stone-600 hover:text-stone-900 cursor-pointer">
                Genres ▾
              </button>
              <div
                className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-xl border border-stone-100 p-3 grid grid-cols-2 gap-1 w-52 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity"
              >
                {GENRES.map((g) => (
                  <button
                    key={g}
                    onClick={() => onSearch(g)}
                    className="text-xs text-stone-600 hover:text-amber-600 text-left px-2 py-1.5 rounded hover:bg-stone-50 cursor-pointer"
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>

            {/* Languages dropdown */}
            <div className="relative group">
              <button className="text-sm font-medium text-stone-600 hover:text-stone-900 cursor-pointer">
                Language ▾
              </button>
              <div
                className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-xl border border-stone-100 p-3 flex flex-col gap-1 w-40 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity"
              >
                {LANGUAGES.map((l) => (
                  <button
                    key={l}
                    onClick={() => onSearch(l)}
                    className="text-xs text-stone-600 hover:text-amber-600 text-left px-2 py-1.5 rounded hover:bg-stone-50 cursor-pointer"
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Desktop search bar */}
          <form onSubmit={handleSearch} className="hidden md:flex items-center relative">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search movies, cast, genres..."
              className="w-64 lg:w-80 pl-9 pr-8 py-2 text-xs bg-stone-50 border border-stone-200 rounded-full focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent placeholder-stone-400 transition-all"
            />
            <span className="absolute left-3 text-stone-400 text-xs">🔍</span>
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-3 text-stone-300 hover:text-stone-500 text-xs cursor-pointer"
              >
                ✕
              </button>
            )}
          </form>

          {/* Mobile search toggle icon */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => {
                setMobileSearchOpen((s) => !s);
                setTimeout(() => inputRef.current?.focus(), 100);
              }}
              className="w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-stone-600 text-xs cursor-pointer active:scale-90"
              title="Search"
            >
              🔍
            </button>
          </div>
        </div>

        {/* Mobile search bar expandable */}
        {mobileSearchOpen && (
          <div className="md:hidden pb-3 pt-1 page-fade-in">
            <form onSubmit={handleSearch} className="flex items-center relative">
              <input
                ref={inputRef}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search movies, cast, genres..."
                className="w-full pl-9 pr-8 py-2 text-xs bg-stone-100 border border-stone-200 rounded-full focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
              <span className="absolute left-3 text-stone-400 text-xs">🔍</span>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 text-stone-400 text-xs cursor-pointer"
                >
                  ✕
                </button>
              )}
            </form>
          </div>
        )}
      </div>
    </nav>
  );
}

// ─── Mobile Bottom Navigation Bar (Optimized for phones) ──────────────────────
function MobileBottomNav({
  activeTab,
  onHome,
  onExplore,
  onWatchlist,
  onFavorites,
  watchlistCount,
  favoritesCount,
}: {
  activeTab: "home" | "movies" | "watchlist" | "favorites" | "details";
  onHome: () => void;
  onExplore: () => void;
  onWatchlist: () => void;
  onFavorites: () => void;
  watchlistCount: number;
  favoritesCount: number;
}) {
  return (
    <div className="md:hidden fixed bottom-0 inset-x-0 z-50 bg-white/96 backdrop-blur-lg border-t border-stone-200 py-1 px-2 flex items-center justify-around shadow-lg safe-area-pb">
      <button
        onClick={onHome}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all cursor-pointer ${
          activeTab === "home" ? "text-amber-600 font-bold scale-105" : "text-stone-500 hover:text-stone-800"
        }`}
      >
        <span className="text-base">🏠</span>
        <span className="text-[10px] mt-0.5">Home</span>
      </button>

      <button
        onClick={onExplore}
        className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all cursor-pointer ${
          activeTab === "movies" ? "text-amber-600 font-bold scale-105" : "text-stone-500 hover:text-stone-800"
        }`}
      >
        <span className="text-base">🔍</span>
        <span className="text-[10px] mt-0.5">Explore</span>
      </button>

      <button
        onClick={onWatchlist}
        className={`relative flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all cursor-pointer ${
          activeTab === "watchlist" ? "text-amber-600 font-bold scale-105" : "text-stone-500 hover:text-stone-800"
        }`}
      >
        <span className="text-base">🔖</span>
        <span className="text-[10px] mt-0.5">Watchlist</span>
        {watchlistCount > 0 && (
          <span className="absolute -top-0.5 right-2 px-1.5 py-0.2 bg-amber-500 text-stone-950 text-[9px] font-black rounded-full shadow-xs">
            {watchlistCount}
          </span>
        )}
      </button>

      <button
        onClick={onFavorites}
        className={`relative flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all cursor-pointer ${
          activeTab === "favorites" ? "text-amber-600 font-bold scale-105" : "text-stone-500 hover:text-stone-800"
        }`}
      >
        <span className="text-base">♥</span>
        <span className="text-[10px] mt-0.5">Liked</span>
        {favoritesCount > 0 && (
          <span className="absolute -top-0.5 right-2 px-1.5 py-0.2 bg-red-500 text-white text-[9px] font-black rounded-full shadow-xs">
            {favoritesCount}
          </span>
        )}
      </button>
    </div>
  );
}

// ─── Clean YouTube ID Extractor ─────────────────────────────────────────────
function extractYouTubeId(rawIdOrUrl?: string): string | null {
  if (!rawIdOrUrl || typeof rawIdOrUrl !== "string") return null;
  const trimmed = rawIdOrUrl.trim();
  if (
    !trimmed ||
    trimmed === "none" ||
    trimmed === "dQw4w9WgXcQ" ||
    trimmed === "null" ||
    trimmed === "undefined"
  ) {
    return null;
  }
  // Standard 11-char YouTube ID
  if (/^[a-zA-Z0-9_-]{11}$/.test(trimmed)) {
    return trimmed;
  }
  // URL matching (youtu.be, watch?v=, embed/, etc.)
  const match = trimmed.match(
    /(?:youtube(?:-nocookie)?\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  return match ? match[1] : null;
}

// ─── Trailer Modal (Target Reference Image 2 Style) ──────────────────────────
function TrailerModal({ movie, onClose }: { movie: Movie; onClose: () => void }) {
  useEffect(() => {
    // Push modal state to history so browser/mobile Back button closes the modal
    window.history.pushState({ modal: "trailer" }, "");

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    const handlePopState = () => {
      onClose();
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("popstate", handlePopState);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("popstate", handlePopState);
      document.body.style.overflow = originalOverflow;
    };
  }, [onClose]);

  const cleanTrailerId = extractYouTubeId(movie.trailerId);
  const ytSearchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(
    `${movie.title} ${movie.year || ""} official trailer`
  )}`;

  return createPortal(
    <div
      className="fixed inset-0 z-[99999] flex items-center justify-center p-3 sm:p-6 md:p-8 bg-black/80 backdrop-blur-xs"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="relative bg-black rounded-lg overflow-hidden shadow-2xl border border-stone-850 flex flex-col my-auto"
        style={{
          width: "min(85vw, 1100px)",
          maxHeight: "calc(100vh - 2.5rem)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Bar - Exactly Reference Image 2 */}
        <div className="flex items-center justify-between px-4 sm:px-5 h-11 sm:h-12 bg-black border-b border-stone-900 flex-shrink-0">
          <span className="text-white text-sm sm:text-base font-semibold tracking-tight">
            Play Trailer
          </span>
          <button
            onClick={onClose}
            className="text-stone-400 hover:text-white text-lg sm:text-xl transition-colors cursor-pointer w-7 h-7 flex items-center justify-center focus:outline-none"
            title="Close"
          >
            ✕
          </button>
        </div>

        {/* Video Area - 16:9 Aspect Ratio Frame */}
        <div className="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
          {cleanTrailerId ? (
            <iframe
              src={`https://www.youtube.com/embed/${cleanTrailerId}?autoplay=1&enablejsapi=1&rel=0&playsinline=1`}
              title={`${movie.title} Official Trailer`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen"
              allowFullScreen
              className="absolute inset-0 w-full h-full border-0"
              loading="eager"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-white p-6 text-center bg-black">
              <span className="text-4xl sm:text-5xl mb-2 sm:mb-3">🎬</span>
              <p className="text-base sm:text-xl font-bold font-display text-white mb-2">
                {movie.title} Official Trailer
              </p>
              <a
                href={ytSearchUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold text-xs sm:text-sm px-5 py-2.5 rounded-full shadow-lg transition-transform active:scale-95 cursor-pointer"
              >
                <span>▶</span> Watch on YouTube
              </a>
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

// ─── Comment Section Component ────────────────────────────────────────────────
function CommentSection({
  movieId,
  movieTitle,
  comments,
  onAddComment,
  onEditComment,
  onDeleteComment,
  userRating,
  onRate,
}: {
  movieId: number;
  movieTitle: string;
  comments: UserComment[];
  onAddComment: (text: string, rating: number, author: string) => void;
  onEditComment: (id: string, newText: string) => void;
  onDeleteComment: (id: string) => void;
  userRating: number;
  onRate: (r: number) => void;
}) {
  const [text, setText] = useState("");
  const [author, setAuthor] = useState(() => localStorage.getItem("cinex_user_name") || "Movie Lover");
  const [rating, setRating] = useState(userRating || 5);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [submittedStatus, setSubmittedStatus] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    localStorage.setItem("cinex_user_name", author);
    onAddComment(text.trim(), rating, author.trim() || "Movie Fan");
    setText("");
    setSubmittedStatus(true);
    setTimeout(() => setSubmittedStatus(false), 3000);
  };

  const startEdit = (c: UserComment) => {
    setEditingId(c.id);
    setEditText(c.text);
  };

  const saveEdit = (id: string) => {
    if (!editText.trim()) return;
    onEditComment(id, editText.trim());
    setEditingId(null);
  };

  return (
    <div className="space-y-5">
      {/* Rate & Review Card */}
      <div className="bg-white rounded-2xl p-4 sm:p-6 border border-stone-200 shadow-xs">
        <h3 className="font-display text-lg sm:text-xl text-stone-800 mb-0.5">Rate & Review "{movieTitle}"</h3>
        <p className="text-[11px] sm:text-xs text-stone-400 mb-3 sm:mb-4">Share your review with fellow movie fans</p>

        <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-stone-50 rounded-xl border border-stone-100">
            <div>
              <p className="text-xs font-semibold text-stone-700 mb-1">Your Star Rating</p>
              <StarRating
                rating={rating}
                onRate={(r) => {
                  setRating(r);
                  onRate(r);
                }}
                size="md"
              />
            </div>
            <div className="sm:max-w-xs">
              <label className="block text-[11px] font-semibold text-stone-700 mb-1">Your Name</label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="Enter your name"
                className="w-full text-xs px-3 py-2 bg-white border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
            </div>
          </div>

          <div>
            <textarea
              rows={3}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="What did you think of the story, acting, music, and climax?..."
              className="w-full text-xs sm:text-sm p-3 bg-stone-50 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 focus:bg-white resize-none"
            />
          </div>

          <div className="flex items-center justify-between">
            {submittedStatus ? (
              <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                ✓ Review posted successfully!
              </span>
            ) : <span />}
            <button
              type="submit"
              disabled={!text.trim()}
              className="bg-amber-500 hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs px-5 py-2 sm:px-6 sm:py-2.5 rounded-full shadow-md transition-transform active:scale-95 cursor-pointer"
            >
              Post Review
            </button>
          </div>
        </form>
      </div>

      {/* Comments List */}
      <div className="space-y-3">
        <h4 className="font-semibold text-stone-800 text-xs sm:text-sm">
          Community Comments & Reviews ({comments.length})
        </h4>

        {comments.length === 0 ? (
          <div className="text-center py-6 sm:py-8 bg-stone-50 rounded-2xl border border-stone-100">
            <span className="text-2xl sm:text-3xl mb-1 block">💬</span>
            <p className="text-xs sm:text-sm font-semibold text-stone-700">No reviews yet</p>
            <p className="text-[11px] text-stone-400 mt-0.5">Be the first to rate and review this title!</p>
          </div>
        ) : (
          comments.map((c) => (
            <div
              key={c.id}
              className={`p-3.5 sm:p-4 rounded-xl border transition-all ${
                c.isUserOwned
                  ? "bg-amber-50/40 border-amber-200/80 shadow-2xs"
                  : "bg-white border-stone-200 shadow-2xs"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-[10px] sm:text-xs font-bold ${
                      c.isUserOwned ? "bg-amber-500 text-white" : "bg-stone-200 text-stone-700"
                    }`}
                  >
                    {c.author.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-stone-800">{c.author}</span>
                      {c.isUserOwned && (
                        <span className="px-1.5 py-0.2 bg-amber-200 text-amber-900 text-[9px] font-semibold rounded">
                          You
                        </span>
                      )}
                    </div>
                    <p className="text-[9px] sm:text-[10px] text-stone-400">
                      {c.createdAt} {c.updatedAt && <span className="italic">(edited)</span>}
                    </p>
                  </div>
                </div>

                {c.rating && (
                  <div>
                    <StarRating rating={c.rating} readOnly size="sm" />
                  </div>
                )}
              </div>

              {editingId === c.id ? (
                <div className="mt-2 space-y-2">
                  <textarea
                    rows={2}
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    className="w-full text-xs p-2 bg-white border border-stone-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"
                  />
                  <div className="flex gap-2 justify-end">
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-2.5 py-1 text-[11px] text-stone-500 hover:text-stone-700 rounded cursor-pointer"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => saveEdit(c.id)}
                      className="px-3 py-1 text-[11px] bg-amber-500 text-white font-semibold rounded hover:bg-amber-600 cursor-pointer"
                    >
                      Save Changes
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-stone-700 leading-relaxed mt-1">{c.text}</p>
              )}

              {/* Edit/Delete only for user's own comments */}
              {c.isUserOwned && editingId !== c.id && (
                <div className="flex items-center gap-3 mt-2.5 pt-2 border-t border-amber-100/80 text-[10px] sm:text-[11px]">
                  <button
                    onClick={() => startEdit(c)}
                    className="text-stone-500 hover:text-stone-800 font-medium flex items-center gap-1 cursor-pointer"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => onDeleteComment(c.id)}
                    className="text-red-500 hover:text-red-700 font-medium flex items-center gap-1 cursor-pointer"
                  >
                    🗑️ Delete
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ─── Home Page ────────────────────────────────────────────────────────────────
function HomePage({
  onSearch,
  onSelect,
  favorites,
  watchlist,
  onToggleFavorite,
  onToggleWatchlist,
}: {
  onSearch: (q: string) => void;
  onSelect: (m: Movie) => void;
  favorites: Movie[];
  watchlist: Movie[];
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
}) {
  const [query, setQuery] = useState("");
  const [trending, setTrending] = useState<Movie[]>(FALLBACK_MOVIES.slice(0, 8));
  const [popular, setPopular] = useState<Movie[]>(FALLBACK_MOVIES);
  const [tamil, setTamil] = useState<Movie[]>(FALLBACK_MOVIES.filter((m) => m.language === "Tamil"));
  const [heroIdx, setHeroIdx] = useState(0);

  const heroMovies = trending.slice(0, 4);
  const hero = heroMovies[heroIdx] || FALLBACK_MOVIES[0];

  useEffect(() => {
    getTrendingMovies().then(setTrending);
    getTopRatedMovies().then(setPopular);
    getTamilMovies().then(setTamil);
  }, []);

  useEffect(() => {
    if (heroMovies.length <= 1) return;
    const t = setInterval(() => setHeroIdx((i) => (i + 1) % heroMovies.length), 6000);
    return () => clearInterval(t);
  }, [heroMovies.length]);

  return (
    <div className="page-fade-in">
      {/* Hero Header (Responsive for Mobile & Desktop) */}
      <div className="relative h-[55vh] sm:h-[65vh] min-h-[380px] sm:min-h-[440px] overflow-hidden bg-black">
        <img
          key={hero.id}
          src={hero.backdrop || DEFAULT_POSTER}
          alt={hero.title}
          className="absolute inset-0 w-full h-full object-cover opacity-80 page-fade-in"
          style={{ transition: "opacity 0.8s" }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/95 via-black/70 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#FAF8F4] via-transparent to-transparent" />

        <div className="relative z-10 h-full flex flex-col justify-center px-4 sm:px-8 md:px-16 max-w-4xl">
          <div className="flex items-center gap-2 mb-2 sm:mb-3">
            <span className="px-2.5 py-0.5 bg-amber-500 text-stone-950 font-bold text-[9px] sm:text-[10px] uppercase font-mono-data rounded-full">
              Trending Spotlight
            </span>
            <span className="text-stone-300 text-xs font-mono-data">{hero.language} · {hero.year}</span>
          </div>

          <h1 className="font-display text-2xl sm:text-4xl md:text-6xl text-white leading-tight mb-1.5 sm:mb-2 tracking-tight">
            {hero.title}
          </h1>
          <p className="text-stone-300 text-xs sm:text-sm md:text-base max-w-lg mb-4 sm:mb-6 line-clamp-2 leading-relaxed">
            {hero.overview}
          </p>

          {/* Hero Search */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (query.trim()) onSearch(query.trim());
            }}
            className="flex items-center bg-white/95 backdrop-blur-md rounded-full shadow-2xl overflow-hidden max-w-xl border border-white/20"
          >
            <span className="pl-3 sm:pl-4 text-stone-400 text-xs sm:text-sm">🔍</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search movies, Tamil blockbusters..."
              className="flex-1 px-2.5 sm:px-3 py-2.5 sm:py-3.5 text-xs sm:text-sm text-stone-800 bg-transparent focus:outline-none placeholder-stone-400"
            />
            <button
              type="submit"
              className="m-1 bg-amber-500 hover:bg-amber-600 text-white px-4 sm:px-6 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold cursor-pointer shadow-md transition-transform active:scale-95 flex-shrink-0"
            >
              Search
            </button>
          </form>

          {/* Hero indicators */}
          {heroMovies.length > 1 && (
            <div className="flex gap-1.5 sm:gap-2 mt-4 sm:mt-5 items-center">
              {heroMovies.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setHeroIdx(i)}
                  className={`h-1.5 rounded-full transition-all cursor-pointer ${
                    i === heroIdx ? "w-6 sm:w-8 bg-amber-400" : "w-2.5 sm:w-3 bg-white/40 hover:bg-white/60"
                  }`}
                />
              ))}
            </div>
          )}
        </div>

        {/* View details button */}
        <div className="absolute bottom-6 right-4 sm:bottom-8 sm:right-16 flex items-center gap-3 z-10">
          <button
            onClick={() => onSelect(hero)}
            className="bg-white/15 hover:bg-white/25 backdrop-blur-md border border-white/30 text-white px-3.5 py-1.5 sm:px-5 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold transition-all shadow-lg cursor-pointer active:scale-95"
          >
            Details ›
          </button>
        </div>
      </div>

      {/* Genre / Language quick chips */}
      <div className="px-4 md:px-8 py-3 sm:py-5 border-b border-stone-200 bg-white/60">
        <div className="max-w-7xl mx-auto flex items-center gap-2 overflow-x-auto scroll-hide pb-1">
          <span className="text-[10px] sm:text-xs font-semibold text-stone-400 uppercase font-mono-data mr-1 sm:mr-2 flex-shrink-0">
            Filters:
          </span>
          {[...LANGUAGES, ...GENRES].map((chip) => (
            <button
              key={chip}
              onClick={() => onSearch(chip)}
              className="px-3 py-1 sm:px-3.5 sm:py-1.5 rounded-full text-[11px] sm:text-xs font-medium border border-stone-200 bg-white text-stone-700 hover:bg-stone-900 hover:text-white hover:border-stone-900 transition-all flex-shrink-0 cursor-pointer shadow-2xs active:scale-95"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Watchlist & Favorites rows (automatically populated) */}
      {watchlist.length > 0 && (
        <div className="bg-amber-50/30 border-b border-amber-100/50">
          <div className="max-w-7xl mx-auto">
            <MovieCarousel
              title="🔖 Your Watchlist"
              subtitle={`You have saved ${watchlist.length} movie${watchlist.length > 1 ? "s" : ""}`}
              movies={watchlist}
              onSelect={onSelect}
              favorites={favorites}
              watchlist={watchlist}
              onToggleFavorite={onToggleFavorite}
              onToggleWatchlist={onToggleWatchlist}
            />
          </div>
        </div>
      )}

      {favorites.length > 0 && (
        <div className="bg-red-50/20 border-b border-red-100/40">
          <div className="max-w-7xl mx-auto">
            <MovieCarousel
              title="♥ Your Liked Movies"
              subtitle={`Your ${favorites.length} top favorite title${favorites.length > 1 ? "s" : ""}`}
              movies={favorites}
              onSelect={onSelect}
              favorites={favorites}
              watchlist={watchlist}
              onToggleFavorite={onToggleFavorite}
              onToggleWatchlist={onToggleWatchlist}
            />
          </div>
        </div>
      )}

      {/* Main Carousels */}
      <div className="max-w-7xl mx-auto">
        <MovieCarousel
          title="🔥 Trending Now"
          subtitle="Top streamed movies this week"
          movies={trending}
          onSelect={onSelect}
          favorites={favorites}
          watchlist={watchlist}
          onToggleFavorite={onToggleFavorite}
          onToggleWatchlist={onToggleWatchlist}
        />
        <div className="border-t border-stone-100 mx-4 md:mx-8" />
        <MovieCarousel
          title="⭐ Top Rated Cinema"
          subtitle="Critically acclaimed movies with highest scores"
          movies={popular}
          onSelect={onSelect}
          favorites={favorites}
          watchlist={watchlist}
          onToggleFavorite={onToggleFavorite}
          onToggleWatchlist={onToggleWatchlist}
        />
        <div className="border-t border-stone-100 mx-4 md:mx-8" />
        <MovieCarousel
          title="🎭 Tamil & South Cinema"
          subtitle="Kollywood blockbusters, thrillers & dramas"
          movies={tamil}
          onSelect={onSelect}
          favorites={favorites}
          watchlist={watchlist}
          onToggleFavorite={onToggleFavorite}
          onToggleWatchlist={onToggleWatchlist}
        />
      </div>
    </div>
  );
}

// ─── Search / Explore View ────────────────────────────────────────────────────
function SearchResults({
  query,
  onSelect,
  onBack,
  favorites,
  watchlist,
  onToggleFavorite,
  onToggleWatchlist,
}: {
  query: string;
  onSelect: (m: Movie) => void;
  onBack: () => void;
  favorites: Movie[];
  watchlist: Movie[];
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
}) {
  const [localQuery, setLocalQuery] = useState(query);
  const [activeQuery, setActiveQuery] = useState(query);
  const [results, setResults] = useState<Movie[]>(FALLBACK_MOVIES);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLocalQuery(query);
    setActiveQuery(query);
  }, [query]);

  useEffect(() => {
    setLoading(true);
    searchMovies(activeQuery)
      .then(setResults)
      .finally(() => setLoading(false));
  }, [activeQuery]);

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-5 sm:py-8 page-slide-up">
      {/* Header */}
      <div className="mb-5 sm:mb-6">
        <button
          onClick={onBack}
          className="text-stone-500 hover:text-stone-800 text-xs sm:text-sm mb-2.5 sm:mb-3 flex items-center gap-1 cursor-pointer font-medium"
        >
          ← Back to Home
        </button>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setActiveQuery(localQuery);
          }}
          className="flex items-center bg-white border border-stone-200 rounded-full overflow-hidden shadow-xs max-w-xl"
        >
          <span className="pl-3.5 text-stone-400 text-xs sm:text-sm">🔍</span>
          <input
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            placeholder="Search movies, actors or genres..."
            className="flex-1 px-2.5 sm:px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-stone-800 bg-transparent focus:outline-none"
          />
          {localQuery && (
            <button
              type="button"
              onClick={() => {
                setLocalQuery("");
                setActiveQuery("");
              }}
              className="pr-3 text-stone-300 hover:text-stone-500 text-xs cursor-pointer"
            >
              ✕
            </button>
          )}
        </form>
        <p className="mt-2.5 text-xs sm:text-sm text-stone-500">
          {activeQuery ? (
            <>
              Showing <span className="font-semibold text-stone-800">{results.length}</span> results for "
              <span className="text-amber-600 font-semibold">{activeQuery}</span>"
            </>
          ) : (
            `All movies in database (${results.length})`
          )}
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={i}
              className="flex-shrink-0 rounded-xl overflow-hidden bg-white shadow-xs border border-stone-100"
            >
              <div className="shimmer" style={{ paddingBottom: "150%" }} />
              <div className="p-2.5 space-y-1.5">
                <div className="h-3 bg-stone-200 rounded w-3/4" />
                <div className="h-2 bg-stone-100 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : results.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-3xl border border-stone-100 p-6 max-w-lg mx-auto">
          <div className="text-4xl mb-3">🎬</div>
          <h3 className="font-display text-xl sm:text-2xl text-stone-700 mb-1.5">No movies found</h3>
          <p className="text-stone-400 text-xs sm:text-sm mb-4">Try searching for a different title, actor, or genre.</p>
          <button
            onClick={() => {
              setLocalQuery("");
              setActiveQuery("");
            }}
            className="bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs px-5 py-2.5 rounded-full cursor-pointer shadow-sm active:scale-95"
          >
            Show All Movies
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {results.map((m, idx) => (
            <MovieGridCard
              key={m.id}
              movie={m}
              onClick={() => onSelect(m)}
              isFavorite={favorites.some((f) => f.id === m.id)}
              isWatchlist={watchlist.some((w) => w.id === m.id)}
              onToggleFavorite={onToggleFavorite}
              onToggleWatchlist={onToggleWatchlist}
              staggerIdx={(idx % 6) + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Dedicated Collection View (Watchlist / Favorites) ────────────────────────
function CollectionPage({
  title,
  subtitle,
  icon,
  movies,
  onSelect,
  onBack,
  favorites,
  watchlist,
  onToggleFavorite,
  onToggleWatchlist,
  emptyText,
}: {
  title: string;
  subtitle: string;
  icon: string;
  movies: Movie[];
  onSelect: (m: Movie) => void;
  onBack: () => void;
  favorites: Movie[];
  watchlist: Movie[];
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
  emptyText: string;
}) {
  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-5 sm:py-8 page-slide-up">
      <div className="mb-6 sm:mb-8">
        <button
          onClick={onBack}
          className="text-stone-500 hover:text-stone-800 text-xs sm:text-sm mb-2.5 sm:mb-3 flex items-center gap-1 cursor-pointer font-medium"
        >
          ← Back to Home
        </button>
        <div className="flex items-center gap-2.5 sm:gap-3">
          <span className="text-2xl sm:text-3xl">{icon}</span>
          <div>
            <h1 className="font-display text-2xl sm:text-4xl text-stone-800">{title}</h1>
            <p className="text-stone-400 text-xs sm:text-sm mt-0.5">
              {movies.length > 0 ? `${movies.length} movie${movies.length > 1 ? "s" : ""} saved` : subtitle}
            </p>
          </div>
        </div>
      </div>

      {movies.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-3xl border border-stone-200 p-6 max-w-lg mx-auto shadow-2xs">
          <span className="text-4xl sm:text-5xl mb-3 block">{icon}</span>
          <h3 className="font-display text-xl sm:text-2xl text-stone-800 mb-1.5">Nothing here yet</h3>
          <p className="text-stone-400 text-xs sm:text-sm mb-5 leading-relaxed">{emptyText}</p>
          <button
            onClick={onBack}
            className="bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs px-6 py-2.5 sm:py-3 rounded-full cursor-pointer shadow-md active:scale-95"
          >
            Explore & Add Movies
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {movies.map((m, idx) => (
            <MovieGridCard
              key={m.id}
              movie={m}
              onClick={() => onSelect(m)}
              isFavorite={favorites.some((f) => f.id === m.id)}
              isWatchlist={watchlist.some((w) => w.id === m.id)}
              onToggleFavorite={onToggleFavorite}
              onToggleWatchlist={onToggleWatchlist}
              staggerIdx={(idx % 6) + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Movie Details Page ───────────────────────────────────────────────────────
function MovieDetailsPage({
  movie,
  onBack,
  onSelect,
  isFavorite,
  isWatchlist,
  onToggleFavorite,
  onToggleWatchlist,
  userRating,
  onRate,
  comments,
  onAddComment,
  onEditComment,
  onDeleteComment,
  favorites,
  watchlist,
}: {
  movie: Movie;
  onBack: () => void;
  onSelect: (m: Movie) => void;
  isFavorite: boolean;
  isWatchlist: boolean;
  onToggleFavorite: (e: React.MouseEvent, m: Movie) => void;
  onToggleWatchlist: (e: React.MouseEvent, m: Movie) => void;
  userRating: number;
  onRate: (r: number) => void;
  comments: UserComment[];
  onAddComment: (text: string, rating: number, author: string) => void;
  onEditComment: (id: string, newText: string) => void;
  onDeleteComment: (id: string) => void;
  favorites: Movie[];
  watchlist: Movie[];
}) {
  const [fullMovie, setFullMovie] = useState<Movie>(movie);
  const [trailerOpen, setTrailerOpen] = useState(false);
  const [tab, setTab] = useState<"overview" | "reviews" | "cast" | "media">("overview");
  const [recommended, setRecommended] = useState<Movie[]>([]);
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setFullMovie(movie);
    getMovieById(movie.id).then((details) => {
      if (details) setFullMovie(details);
    });
    getRecommendations(movie.id, 10).then(setRecommended);
  }, [movie.id]);

  return (
    <div className="min-h-screen page-slide-up pb-12">
      {/* Hero Backdrop */}
      <div className="relative bg-black min-h-[420px] sm:min-h-[500px]">
        <img
          src={fullMovie.backdrop || fullMovie.poster || DEFAULT_POSTER}
          alt={fullMovie.title}
          className="absolute inset-0 w-full h-full object-cover opacity-70 page-fade-in"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/95 via-black/80 to-black/40" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#FAF8F4] via-transparent to-transparent" />

        {/* Back Button */}
        <button
          onClick={onBack}
          className="absolute top-4 left-4 sm:top-5 sm:left-8 z-20 bg-black/60 hover:bg-black/85 backdrop-blur-md border border-white/20 text-white px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1 cursor-pointer shadow-lg active:scale-95"
        >
          ← Back
        </button>

        <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 pt-14 sm:pt-16 pb-8 sm:pb-12 flex flex-col md:flex-row gap-6 sm:gap-8 items-start">
          {/* Movie Poster */}
          <div className="flex-shrink-0 mx-auto md:mx-0">
            <div className="w-40 sm:w-52 md:w-60 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/15 bg-stone-900 group relative">
              <img
                src={fullMovie.poster || DEFAULT_POSTER}
                alt={fullMovie.title}
                onError={(e) => {
                  if (e.currentTarget.src !== DEFAULT_POSTER) e.currentTarget.src = DEFAULT_POSTER;
                }}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                style={{ aspectRatio: "2/3" }}
              />
              <button
                onClick={() => setTrailerOpen(true)}
                className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer"
              >
                <div className="w-12 h-12 sm:w-14 sm:h-14 bg-amber-500 rounded-full flex items-center justify-center text-white text-lg sm:text-xl shadow-xl">
                  ▶
                </div>
              </button>
            </div>

            {/* Streaming providers */}
            <div className="mt-3 space-y-1.5 w-40 sm:w-52 md:w-60">
              {fullMovie.streaming && fullMovie.streaming.length > 0 ? (
                fullMovie.streaming.map((s) => (
                  <div
                    key={s.name}
                    className="flex items-center gap-2 bg-black/60 backdrop-blur-md rounded-xl px-2.5 py-1.5 border border-white/10"
                  >
                    {s.logo?.startsWith("http") ? (
                      <img src={s.logo} alt={s.name} className="w-5 h-5 rounded object-contain" />
                    ) : (
                      <span
                        className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold text-white"
                        style={{ background: s.color || "#00A8E1" }}
                      >
                        {s.logo || "▶"}
                      </span>
                    )}
                    <div>
                      <p className="text-[8px] text-stone-400 font-mono-data tracking-wider">AVAILABLE ON</p>
                      <p className="text-white text-[11px] font-semibold">{s.name}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-black/50 backdrop-blur-md rounded-xl px-2.5 py-1.5 text-stone-400 text-[10px] text-center border border-white/10">
                  Streaming details updating
                </div>
              )}
            </div>
          </div>

          {/* Info Column */}
          <div className="flex-1 min-w-0 w-full">
            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5">
              <span className="text-[10px] sm:text-xs border border-stone-400/60 text-stone-300 px-2 py-0.2 rounded font-mono-data">
                {fullMovie.language?.toUpperCase() || "TAMIL"}
              </span>
              <span className="text-stone-300 text-xs sm:text-sm">{fullMovie.year ? String(fullMovie.year) : "Recent"}</span>
              <span className="text-stone-500">·</span>
              {fullMovie.genres
                ?.map((g) => (
                  <span key={g} className="text-stone-300 text-xs sm:text-sm">
                    {g}
                  </span>
                ))
                .reduce((a, b) => (
                  <>
                    {a}
                    <span className="text-stone-500">, </span>
                    {b}
                  </>
                ))}
              <span className="text-stone-500">·</span>
              <span className="text-stone-300 text-xs sm:text-sm">{fullMovie.runtime}</span>
            </div>

            <h1 className="font-display text-2xl sm:text-4xl md:text-5xl text-white mb-1.5 leading-tight">
              {fullMovie.title}
            </h1>
            {fullMovie.tagline && (
              <p className="text-stone-400 italic text-xs sm:text-base mb-3 sm:mb-4 font-serif">"{fullMovie.tagline}"</p>
            )}

            {/* Score & Action Row */}
            <div className="flex flex-wrap items-center gap-3 sm:gap-5 mb-4 sm:mb-6">
              <div className="flex items-center gap-2.5">
                <RatingCircle rating={fullMovie.rating} size="lg" />
                <div>
                  <p className="text-white font-semibold text-xs sm:text-sm">
                    {fullMovie.rating_source === "IMDb" ? "IMDb Rating" : "TMDB Rating"}
                  </p>
                  <p className="text-amber-400 text-xs sm:text-sm font-bold font-mono-data flex items-center gap-1">
                    <span>★</span>
                    <span>{fullMovie.rating && fullMovie.rating > 0 ? `${fullMovie.rating.toFixed(1)} / 10` : "Not Rated"}</span>
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2 items-center">
                <button
                  onClick={() => setTrailerOpen(true)}
                  className="flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 sm:px-5 sm:py-2.5 rounded-full font-semibold text-xs sm:text-sm shadow-xl transition-transform active:scale-95 cursor-pointer"
                >
                  <span className="text-sm">▶</span> Play Trailer
                </button>

                <button
                  onClick={(e) => onToggleFavorite(e, fullMovie)}
                  className={`flex items-center gap-1.5 px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold transition-all cursor-pointer active:scale-95 ${
                    isFavorite
                      ? "bg-red-500 text-white shadow-md heart-pop"
                      : "bg-white/15 hover:bg-white/25 backdrop-blur-md border border-white/20 text-white"
                  }`}
                >
                  <span>{isFavorite ? "♥" : "♡"}</span> {isFavorite ? "Liked" : "Like"}
                </button>

                <button
                  onClick={(e) => onToggleWatchlist(e, fullMovie)}
                  className={`flex items-center gap-1.5 px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold transition-all cursor-pointer active:scale-95 ${
                    isWatchlist
                      ? "bg-amber-500 text-white shadow-md bookmark-bounce"
                      : "bg-white/15 hover:bg-white/25 backdrop-blur-md border border-white/20 text-white"
                  }`}
                >
                  <span>{isWatchlist ? "🔖" : "🏷️"}</span> {isWatchlist ? "Saved" : "Watchlist"}
                </button>
              </div>
            </div>

            {/* Interactive User Rating Badge */}
            <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-2xl p-3 sm:p-4 max-w-lg mb-4 sm:mb-6 flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-[10px] sm:text-xs font-semibold text-amber-400 uppercase font-mono-data tracking-wider">
                  Your Rating
                </p>
                <p className="text-white text-xs mt-0.5">
                  {userRating > 0 ? `You rated: ${userRating}/5 stars` : "Tap a star to rate"}
                </p>
              </div>
              <StarRating rating={userRating} onRate={onRate} size="md" />
            </div>

            {/* Desktop Overview snippet */}
            <div className="hidden md:block">
              <p className="text-stone-300 text-sm leading-relaxed max-w-2xl mb-3">
                {fullMovie.overview}
              </p>
              <div className="flex items-center gap-4 text-xs">
                <div>
                  <p className="text-white font-semibold text-sm">{fullMovie.director}</p>
                  <p className="text-stone-400">Director</p>
                </div>
                <div className="w-px h-8 bg-white/20" />
                <div>
                  <p className="text-white font-semibold text-sm">{fullMovie.language}</p>
                  <p className="text-stone-400">Language</p>
                </div>
                <div className="w-px h-8 bg-white/20" />
                <div>
                  <p className="text-white font-semibold text-sm">{fullMovie.runtime}</p>
                  <p className="text-stone-400">Runtime</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 mt-2 sm:mt-0">
        <div className="flex gap-2 border-b border-stone-200 mb-5 overflow-x-auto scroll-hide">
          {(["overview", "reviews", "cast", "media"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 sm:px-5 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold capitalize transition-all border-b-2 -mb-px cursor-pointer flex-shrink-0 flex items-center gap-1.5 ${
                tab === t
                  ? "border-amber-500 text-amber-600 font-bold"
                  : "border-transparent text-stone-500 hover:text-stone-800"
              }`}
            >
              {t === "overview" && "Overview"}
              {t === "reviews" && (
                <>
                  <span>Reviews</span>
                  <span className="px-1.5 py-0.2 bg-amber-100 text-amber-800 text-[9px] sm:text-[10px] font-bold rounded-full">
                    {comments.length}
                  </span>
                </>
              )}
              {t === "cast" && "Cast"}
              {t === "media" && "Trailers & Media"}
            </button>
          ))}
        </div>

        {/* Tab 1: Overview */}
        {tab === "overview" && (
          <div className="grid md:grid-cols-3 gap-6 sm:gap-8 pb-6 page-fade-in">
            <div className="md:col-span-2 space-y-4 sm:space-y-6">
              <div>
                <h3 className="font-display text-xl sm:text-2xl text-stone-800 mb-1.5">Synopsis</h3>
                <p className="text-xs sm:text-sm text-stone-600 leading-relaxed">{fullMovie.overview}</p>
              </div>
              <div className="grid grid-cols-2 gap-3 sm:gap-4">
                {[
                  { label: "Director", value: fullMovie.director },
                  { label: "Language", value: fullMovie.language },
                  { label: "Runtime", value: fullMovie.runtime },
                  { label: "Release Year", value: String(fullMovie.year || "N/A") },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-stone-50 rounded-xl p-3 sm:p-4 border border-stone-100">
                    <p className="text-[10px] sm:text-xs text-stone-400 font-mono-data uppercase tracking-wide mb-0.5">
                      {label}
                    </p>
                    <p className="text-stone-800 font-semibold text-xs sm:text-sm">{value}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-[10px] sm:text-xs text-stone-400 font-mono-data uppercase tracking-wide mb-1.5">
                  Genres
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {fullMovie.genres?.map((g) => (
                    <span
                      key={g}
                      className="px-3 py-1 bg-stone-900 text-white text-xs font-semibold rounded-full"
                    >
                      {g}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              <button
                onClick={() => setTrailerOpen(true)}
                className="w-full relative rounded-2xl overflow-hidden group cursor-pointer border border-stone-200 shadow-sm block p-0 text-left"
              >
                <img
                  src={fullMovie.backdrop || fullMovie.poster || DEFAULT_POSTER}
                  alt="Trailer thumbnail"
                  className="w-full h-32 sm:h-36 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-black/50 group-hover:bg-black/40 flex flex-col items-center justify-center gap-1.5 transition-colors">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-amber-500 rounded-full flex items-center justify-center text-white text-base sm:text-xl shadow-lg group-hover:scale-110 transition-transform">
                    ▶
                  </div>
                  <span className="text-white text-xs font-semibold tracking-wide uppercase">
                    Watch Official Trailer
                  </span>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Tab 2: Reviews & Comments */}
        {tab === "reviews" && (
          <div className="max-w-4xl pb-6 page-fade-in">
            <CommentSection
              movieId={fullMovie.id}
              movieTitle={fullMovie.title}
              comments={comments}
              onAddComment={onAddComment}
              onEditComment={onEditComment}
              onDeleteComment={onDeleteComment}
              userRating={userRating}
              onRate={onRate}
            />
          </div>
        )}

        {/* Tab 3: Cast */}
        {tab === "cast" && (
          <div className="pb-6 page-fade-in">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
              {fullMovie.cast?.map((c) => (
                <div key={c.name} className="text-center group">
                  <div
                    className="relative w-full rounded-2xl overflow-hidden bg-stone-200 shadow-2xs group-hover:shadow-md mb-1.5"
                    style={{ paddingBottom: "130%" }}
                  >
                    <img
                      src={c.photo}
                      alt={c.name}
                      loading="lazy"
                      className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <p className="text-xs sm:text-sm font-semibold text-stone-800 line-clamp-1">{c.name}</p>
                  <p className="text-[10px] sm:text-xs text-stone-400">{c.role}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Media */}
        {tab === "media" && (
          <div className="pb-6 space-y-4 sm:space-y-6 page-fade-in">
            <div>
              <h3 className="font-display text-lg sm:text-xl text-stone-800 mb-2.5">Official Video Trailer</h3>
              <button
                onClick={() => setTrailerOpen(true)}
                className="relative w-full max-w-2xl rounded-2xl overflow-hidden group cursor-pointer border border-stone-200 p-0 block shadow-md"
              >
                <img
                  src={fullMovie.backdrop || fullMovie.poster || DEFAULT_POSTER}
                  alt="Trailer"
                  className="w-full object-cover h-48 sm:h-72 group-hover:scale-103 transition-transform duration-300"
                  style={{ aspectRatio: "16/9" }}
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-amber-500 rounded-full flex items-center justify-center text-white text-xl sm:text-2xl shadow-xl group-hover:scale-110 transition-transform">
                    ▶
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* KNN Recommendations Carousel */}
      {recommended.length > 0 && (
        <div className="border-t border-stone-200 bg-[#FAF8F4]">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between px-4 md:px-8 pt-6 pb-2.5">
              <div>
                <h2 className="font-display text-lg sm:text-2xl text-stone-800">Recommended For You</h2>
                <p className="text-stone-400 text-[11px] sm:text-xs mt-0.5">
                  AI match for fans of <span className="text-amber-600 font-semibold">{fullMovie.title}</span>
                </p>
              </div>
              <div className="hidden sm:flex gap-1.5">
                <button
                  onClick={() => carouselRef.current?.scrollBy({ left: -300, behavior: "smooth" })}
                  className="w-7 h-7 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 cursor-pointer"
                >
                  ‹
                </button>
                <button
                  onClick={() => carouselRef.current?.scrollBy({ left: 300, behavior: "smooth" })}
                  className="w-7 h-7 rounded-full border border-stone-200 flex items-center justify-center text-stone-500 hover:bg-stone-100 cursor-pointer"
                >
                  ›
                </button>
              </div>
            </div>
            <div ref={carouselRef} className="flex gap-3 sm:gap-4 overflow-x-auto scroll-hide snap-x px-4 md:px-8 pb-6">
              {recommended.map((m, idx) => (
                <MovieCard
                  key={m.id}
                  movie={m}
                  onClick={() => onSelect(m)}
                  isFavorite={favorites.some((f) => f.id === m.id)}
                  isWatchlist={watchlist.some((w) => w.id === m.id)}
                  onToggleFavorite={onToggleFavorite}
                  onToggleWatchlist={onToggleWatchlist}
                  staggerIdx={(idx % 6) + 1}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {trailerOpen && <TrailerModal movie={fullMovie} onClose={() => setTrailerOpen(false)} />}
    </div>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────
function Footer({ onSelectGenre }: { onSelectGenre: (g: string) => void }) {
  return (
    <footer className="bg-stone-900 text-stone-400 py-8 sm:py-12 px-4 md:px-8 mt-auto border-t border-stone-800 pb-20 md:pb-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div className="w-6 h-6 sm:w-7 sm:h-7 bg-amber-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-[10px] sm:text-xs font-mono-data">CX</span>
              </div>
              <span className="font-display text-white text-base sm:text-lg tracking-tight">CineX</span>
            </div>
            <p className="text-[11px] sm:text-xs leading-relaxed text-stone-400">
              Machine Learning powered movie discovery platform with intelligent KNN recommendations and rich metadata.
            </p>
          </div>
          <div>
            <h4 className="text-white font-semibold text-[11px] sm:text-xs uppercase tracking-wider font-mono-data mb-2.5">
              Genres
            </h4>
            <ul className="space-y-1 text-[11px] sm:text-xs">
              {GENRES.slice(0, 5).map((g) => (
                <li key={g}>
                  <button
                    onClick={() => onSelectGenre(g)}
                    className="hover:text-amber-400 transition-colors cursor-pointer text-left"
                  >
                    {g}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold text-[11px] sm:text-xs uppercase tracking-wider font-mono-data mb-2.5">
              Languages
            </h4>
            <ul className="space-y-1 text-[11px] sm:text-xs">
              {LANGUAGES.map((l) => (
                <li key={l}>
                  <button
                    onClick={() => onSelectGenre(l)}
                    className="hover:text-amber-400 transition-colors cursor-pointer text-left"
                  >
                    {l}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold text-[11px] sm:text-xs uppercase tracking-wider font-mono-data mb-2.5">
              Connect
            </h4>
            <ul className="space-y-1.5 text-[11px] sm:text-xs">
              <li>
                <a
                  href="https://www.linkedin.com/in/lakshma-deepan-76bb2537a"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors flex items-center gap-1.5"
                >
                  <span className="w-4 h-4 bg-blue-600 rounded flex items-center justify-center text-[9px] font-bold text-white">
                    in
                  </span>
                  LinkedIn Profile
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/Lakshmadeepan"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors flex items-center gap-1.5"
                >
                  <span className="w-4 h-4 bg-stone-700 rounded flex items-center justify-center text-[9px] font-bold text-white">
                    gh
                  </span>
                  GitHub Repository
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-stone-800 pt-5 flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <p className="text-[10px] sm:text-xs text-stone-500">© 2026 CineX · Machine Learning Movie Discovery</p>
          <p className="text-[10px] sm:text-xs text-stone-500">
            Engineered by{" "}
            <a
              href="https://www.linkedin.com/in/lakshma-deepan-76bb2537a"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-400 font-medium hover:text-amber-300 transition-colors"
            >
              Lakshmadeepan
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}

// ─── Main App Root ────────────────────────────────────────────────────────────
type Page = "home" | "search" | "details" | "watchlist" | "favorites";

export default function App() {
  const [page, setPage] = useState<Page>("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  // Persistent Watchlist & Favorites
  const [watchlist, setWatchlist] = useState<Movie[]>(() => {
    try {
      const saved = localStorage.getItem("cinex_watchlist_v2");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [favorites, setFavorites] = useState<Movie[]>(() => {
    try {
      const saved = localStorage.getItem("cinex_favorites_v2");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Persistent Ratings: { [movieId]: rating }
  const [ratings, setRatings] = useState<Record<number, number>>(() => {
    try {
      const saved = localStorage.getItem("cinex_user_ratings_v2");
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Persistent Comments: { [movieId]: UserComment[] }
  const [commentsMap, setCommentsMap] = useState<Record<number, UserComment[]>>(() => {
    try {
      const saved = localStorage.getItem("cinex_comments_v2");
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Sync to LocalStorage
  useEffect(() => {
    localStorage.setItem("cinex_watchlist_v2", JSON.stringify(watchlist));
  }, [watchlist]);

  useEffect(() => {
    localStorage.setItem("cinex_favorites_v2", JSON.stringify(favorites));
  }, [favorites]);

  useEffect(() => {
    localStorage.setItem("cinex_user_ratings_v2", JSON.stringify(ratings));
  }, [ratings]);

  useEffect(() => {
    localStorage.setItem("cinex_comments_v2", JSON.stringify(commentsMap));
  }, [commentsMap]);

  // Actions without intrusive popups
  const handleToggleWatchlist = (e: React.MouseEvent, m: Movie) => {
    e.stopPropagation();
    setWatchlist((prev) => {
      const exists = prev.some((item) => item.id === m.id);
      if (exists) {
        return prev.filter((item) => item.id !== m.id);
      } else {
        return [m, ...prev];
      }
    });
  };

  const handleToggleFavorite = (e: React.MouseEvent, m: Movie) => {
    e.stopPropagation();
    setFavorites((prev) => {
      const exists = prev.some((item) => item.id === m.id);
      if (exists) {
        return prev.filter((item) => item.id !== m.id);
      } else {
        return [m, ...prev];
      }
    });
  };

  const handleRate = (movieId: number, r: number) => {
    setRatings((prev) => {
      const updated = { ...prev, [movieId]: r };
      if (r === 0) {
        delete updated[movieId];
      }
      return updated;
    });
  };

  const handleAddComment = (movieId: number, text: string, r: number, author: string) => {
    const newComment: UserComment = {
      id: "c_" + Date.now() + "_" + Math.random().toString(36).substring(2, 5),
      movieId,
      author,
      text,
      rating: r || undefined,
      createdAt: "Just now",
      isUserOwned: true,
    };
    setCommentsMap((prev) => {
      const list = prev[movieId] || [];
      return { ...prev, [movieId]: [newComment, ...list] };
    });
  };

  const handleEditComment = (movieId: number, id: string, newText: string) => {
    setCommentsMap((prev) => {
      const list = prev[movieId] || [];
      const updated = list.map((c) =>
        c.id === id ? { ...c, text: newText, updatedAt: "Just now" } : c
      );
      return { ...prev, [movieId]: updated };
    });
  };

  const handleDeleteComment = (movieId: number, id: string) => {
    setCommentsMap((prev) => {
      const list = prev[movieId] || [];
      return { ...prev, [movieId]: list.filter((c) => c.id !== id) };
    });
  };

  // Movie comments combining sample + user comments
  const getMovieComments = (movieId: number): UserComment[] => {
    const userComments = commentsMap[movieId] || [];
    const defaults = (SAMPLE_COMMUNITY_COMMENTS[String(movieId)] || SAMPLE_COMMUNITY_COMMENTS["default"]).map(
      (dc, i) => ({
        ...dc,
        id: `sample_${movieId}_${i}`,
        movieId,
        isUserOwned: false,
      })
    );
    return [...userComments, ...defaults];
  };

  // Set up browser history navigation so pressing Back returns to previous page without exiting
  useEffect(() => {
    if (!window.history.state || !window.history.state.page) {
      window.history.replaceState({ page: "home" }, "");
    }

    const handlePopState = (e: PopStateEvent) => {
      const state = e.state;
      if (state && state.page) {
        setPage(state.page);
        if (state.movie) {
          setSelectedMovie(state.movie);
        }
        if (state.query !== undefined) {
          setSearchQuery(state.query);
        }
      } else {
        setPage("home");
        setSelectedMovie(null);
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Navigation handlers with History push
  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setPage("search");
    window.history.pushState({ page: "search", query: q }, "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSelect = (m: Movie) => {
    setSelectedMovie(m);
    setPage("details");
    window.history.pushState({ page: "details", movie: m, query: searchQuery }, "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleHome = () => {
    setPage("home");
    setSearchQuery("");
    window.history.pushState({ page: "home" }, "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleOpenWatchlist = () => {
    setPage("watchlist");
    window.history.pushState({ page: "watchlist" }, "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleOpenFavorites = () => {
    setPage("favorites");
    window.history.pushState({ page: "favorites" }, "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBack = () => {
    if (window.history.state && window.history.length > 1) {
      window.history.back();
    } else {
      handleHome();
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF8F4] flex flex-col selection:bg-amber-400 selection:text-stone-900">
      <Navbar
        onHome={handleHome}
        onSearch={handleSearch}
        onOpenWatchlist={handleOpenWatchlist}
        onOpenFavorites={handleOpenFavorites}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        watchlistCount={watchlist.length}
        favoritesCount={favorites.length}
        activeTab={
          page === "home"
            ? "home"
            : page === "search"
            ? "movies"
            : page === "watchlist"
            ? "watchlist"
            : page === "favorites"
            ? "favorites"
            : "details"
        }
      />

      <main className="flex-1">
        {page === "home" && (
          <HomePage
            onSearch={handleSearch}
            onSelect={handleSelect}
            favorites={favorites}
            watchlist={watchlist}
            onToggleFavorite={handleToggleFavorite}
            onToggleWatchlist={handleToggleWatchlist}
          />
        )}

        {page === "search" && (
          <SearchResults
            query={searchQuery}
            onSelect={handleSelect}
            onBack={handleBack}
            favorites={favorites}
            watchlist={watchlist}
            onToggleFavorite={handleToggleFavorite}
            onToggleWatchlist={handleToggleWatchlist}
          />
        )}

        {page === "watchlist" && (
          <CollectionPage
            title="My Watchlist"
            subtitle="Movies you want to watch later"
            icon="🔖"
            movies={watchlist}
            onSelect={handleSelect}
            onBack={handleBack}
            favorites={favorites}
            watchlist={watchlist}
            onToggleFavorite={handleToggleFavorite}
            onToggleWatchlist={handleToggleWatchlist}
            emptyText="You haven't added any movies to your watchlist yet. Tap the bookmark icon on any movie to save it here!"
          />
        )}

        {page === "favorites" && (
          <CollectionPage
            title="My Liked Movies"
            subtitle="Your favorite movies and personal recommendations"
            icon="♥"
            movies={favorites}
            onSelect={handleSelect}
            onBack={handleBack}
            favorites={favorites}
            watchlist={watchlist}
            onToggleFavorite={handleToggleFavorite}
            onToggleWatchlist={handleToggleWatchlist}
            emptyText="You haven't liked any movies yet. Tap the heart icon on any movie card to add it to your favorites!"
          />
        )}

        {page === "details" && selectedMovie && (
          <MovieDetailsPage
            movie={selectedMovie}
            onBack={handleBack}
            onSelect={handleSelect}
            isFavorite={favorites.some((f) => f.id === selectedMovie.id)}
            isWatchlist={watchlist.some((w) => w.id === selectedMovie.id)}
            onToggleFavorite={handleToggleFavorite}
            onToggleWatchlist={handleToggleWatchlist}
            userRating={ratings[selectedMovie.id] || 0}
            onRate={(r) => handleRate(selectedMovie.id, r)}
            comments={getMovieComments(selectedMovie.id)}
            onAddComment={(text, r, author) => handleAddComment(selectedMovie.id, text, r, author)}
            onEditComment={(id, newText) => handleEditComment(selectedMovie.id, id, newText)}
            onDeleteComment={(id) => handleDeleteComment(selectedMovie.id, id)}
            favorites={favorites}
            watchlist={watchlist}
          />
        )}
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <MobileBottomNav
        activeTab={
          page === "home"
            ? "home"
            : page === "search"
            ? "movies"
            : page === "watchlist"
            ? "watchlist"
            : page === "favorites"
            ? "favorites"
            : "details"
        }
        onHome={handleHome}
        onExplore={() => handleSearch("")}
        onWatchlist={handleOpenWatchlist}
        onFavorites={handleOpenFavorites}
        watchlistCount={watchlist.length}
        favoritesCount={favorites.length}
      />

      <Footer onSelectGenre={handleSearch} />
    </div>
  );
}
