import { FALLBACK_MOVIES } from "./api";

// ─── Interfaces ──────────────────────────────────────────────────────────────
export interface CastMember {
  name: string;
  role: string;
  photo: string;
}

export interface StreamingPlatform {
  name: string;
  logo: string;
  color: string;
}

export interface Movie {
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
  cast: CastMember[];
  streaming: StreamingPlatform[];
}

// ─── TMDB Raw Interfaces ─────────────────────────────────────────────────────
interface TMDBMovieSummary {
  id: number;
  title?: string;
  name?: string;
  original_title?: string;
  original_language: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  release_date?: string;
  first_air_date?: string;
  vote_average: number;
  genre_ids?: number[];
  genres?: { id: number; name: string }[];
}

interface TMDBCredits {
  cast: {
    id: number;
    name: string;
    character: string;
    profile_path: string | null;
    order: number;
  }[];
  crew: {
    id: number;
    name: string;
    job: string;
    department: string;
  }[];
}

interface TMDBVideos {
  results: {
    id: string;
    key: string;
    name: string;
    site: string;
    type: string;
    official?: boolean;
  }[];
}

interface TMDBWatchProviders {
  results: {
    [countryCode: string]: {
      link?: string;
      flatrate?: { provider_id: number; provider_name: string; logo_path: string }[];
      rent?: { provider_id: number; provider_name: string; logo_path: string }[];
      buy?: { provider_id: number; provider_name: string; logo_path: string }[];
    };
  };
}

interface TMDBMovieDetails extends TMDBMovieSummary {
  runtime?: number;
  tagline?: string;
  credits?: TMDBCredits;
  videos?: TMDBVideos;
  "watch/providers"?: TMDBWatchProviders;
}

// ─── Constants & Mappings ────────────────────────────────────────────────────
const TMDB_BASE_URL = "https://api.themoviedb.org/3";
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p";

// Read API Key from Vite Environment
const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY || "f3b2275b26f4c53d086fb7614cbc2526";

const GENRE_MAP: Record<number, string> = {
  28: "Action",
  12: "Adventure",
  16: "Animation",
  35: "Comedy",
  80: "Crime",
  99: "Documentary",
  18: "Drama",
  10751: "Family",
  14: "Fantasy",
  36: "History",
  27: "Horror",
  10402: "Music",
  9648: "Mystery",
  10749: "Romance",
  878: "Sci-Fi",
  10770: "TV Movie",
  53: "Thriller",
  10752: "War",
  37: "Western",
};

const LANGUAGE_MAP: Record<string, string> = {
  ta: "Tamil",
  te: "Telugu",
  ml: "Malayalam",
  hi: "Hindi",
  kn: "Kannada",
  en: "English",
  ja: "Japanese",
  ko: "Korean",
  fr: "French",
  es: "Spanish",
  de: "German",
  zh: "Chinese",
};

// Fallback images
const DEFAULT_POSTER = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&h=600&fit=crop&auto=format";
const DEFAULT_BACKDROP = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format";
const DEFAULT_AVATAR = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format";

// ─── Helper Functions ────────────────────────────────────────────────────────
function formatRuntime(minutes?: number): string {
  if (!minutes || minutes <= 0) return "2h 15m";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m.toString().padStart(2, "0")}m`;
}

function getPosterUrl(path: string | null): string {
  return path ? `${TMDB_IMAGE_BASE}/w500${path}` : DEFAULT_POSTER;
}

function getBackdropUrl(path: string | null): string {
  return path ? `${TMDB_IMAGE_BASE}/w1280${path}` : DEFAULT_BACKDROP;
}

function getProfileUrl(path: string | null): string {
  return path ? `${TMDB_IMAGE_BASE}/w200${path}` : DEFAULT_AVATAR;
}

function getProviderLogoUrl(path: string | null): string {
  return path ? `${TMDB_IMAGE_BASE}/w92${path}` : "";
}

function mapLanguage(code: string): string {
  return LANGUAGE_MAP[code.toLowerCase()] || code.toUpperCase();
}

function mapGenres(genreIds?: number[], genresObj?: { id: number; name: string }[]): string[] {
  if (genresObj && genresObj.length > 0) {
    return genresObj.map((g) => g.name);
  }
  if (genreIds && genreIds.length > 0) {
    return genreIds.map((id) => GENRE_MAP[id] || "Drama").filter(Boolean);
  }
  return ["Action", "Drama"];
}

function extractTrailerId(videos?: TMDBVideos): string {
  if (!videos?.results || videos.results.length === 0) return "bk5lKWDVJAI"; // default trailer
  
  // Prefer official trailer on YouTube
  const officialTrailer = videos.results.find(
    (v) => v.site === "YouTube" && v.type === "Trailer" && v.official
  );
  if (officialTrailer) return officialTrailer.key;

  // Any YouTube trailer
  const trailer = videos.results.find((v) => v.site === "YouTube" && v.type === "Trailer");
  if (trailer) return trailer.key;

  // Any YouTube video (teaser, clip)
  const anyYoutube = videos.results.find((v) => v.site === "YouTube");
  return anyYoutube ? anyYoutube.key : "bk5lKWDVJAI";
}

function extractStreamingProviders(watchProviders?: TMDBWatchProviders): StreamingPlatform[] {
  const inProviders = watchProviders?.results?.IN;
  if (!inProviders) {
    return [
      { name: "Amazon Prime", logo: "▶", color: "#00A8E1" },
      { name: "Netflix", logo: "N", color: "#E50914" },
    ];
  }

  const list = inProviders.flatrate || inProviders.rent || inProviders.buy || [];
  if (list.length === 0) {
    return [{ name: "Theatrical Release", logo: "🎬", color: "#D97706" }];
  }

  return list.slice(0, 3).map((p) => ({
    name: p.provider_name,
    logo: p.logo_path ? getProviderLogoUrl(p.logo_path) : p.provider_name.charAt(0),
    color: "#1C1917",
  }));
}

function mapTMDBToMovie(item: TMDBMovieSummary, details?: Partial<TMDBMovieDetails>): Movie {
  const yearStr = item.release_date || item.first_air_date || "";
  const year = yearStr ? new Date(yearStr).getFullYear() : 2024;
  
  let director = "Unknown";
  let cast: CastMember[] = [];
  let trailerId = "bk5lKWDVJAI";
  let streaming: StreamingPlatform[] = [
    { name: "Amazon Prime", logo: "▶", color: "#00A8E1" },
    { name: "Netflix", logo: "N", color: "#E50914" },
  ];

  if (details?.credits) {
    const dir = details.credits.crew.find((c) => c.job === "Director");
    if (dir) director = dir.name;

    cast = details.credits.cast.slice(0, 6).map((c) => ({
      name: c.name,
      role: c.character || "Actor",
      photo: getProfileUrl(c.profile_path),
    }));
  }

  if (details?.videos) {
    trailerId = extractTrailerId(details.videos);
  }

  if (details?.["watch/providers"]) {
    streaming = extractStreamingProviders(details["watch/providers"]);
  }

  return {
    id: item.id,
    title: item.title || item.name || item.original_title || "Untitled",
    year: isNaN(year) ? 2024 : year,
    rating: Number((item.vote_average || 7.0).toFixed(1)),
    language: mapLanguage(item.original_language),
    genres: mapGenres(item.genre_ids, details?.genres || item.genres),
    runtime: formatRuntime(details?.runtime),
    overview: item.overview || "No overview available for this movie.",
    tagline: details?.tagline || "",
    director,
    poster: getPosterUrl(item.poster_path),
    backdrop: getBackdropUrl(item.backdrop_path || item.poster_path),
    trailerId,
    cast: cast.length > 0 ? cast : [
      { name: "Lead Actor", role: "Protagonist", photo: DEFAULT_AVATAR }
    ],
    streaming,
  };
}

// ─── Generic TMDB Fetcher ────────────────────────────────────────────────────
async function fetchFromTMDB<T>(endpoint: string, params: Record<string, string> = {}): Promise<T | null> {
  if (!TMDB_API_KEY) {
    return null;
  }

  try {
    const urlParams = new URLSearchParams({
      api_key: TMDB_API_KEY,
      language: "en-US",
      ...params,
    });

    const res = await fetch(`${TMDB_BASE_URL}${endpoint}?${urlParams.toString()}`);
    if (!res.ok) {
      console.warn(`[TMDB API Error] ${res.status}: ${res.statusText} on ${endpoint}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (error) {
    console.error(`[TMDB Network Error] on ${endpoint}:`, error);
    return null;
  }
}

// ─── Exported API Functions ───────────────────────────────────────────────────

/**
 * Fetch weekly trending movies from TMDB
 */
export async function getTrendingMovies(): Promise<Movie[]> {
  const data = await fetchFromTMDB<{ results: TMDBMovieSummary[] }>("/trending/movie/week");
  if (!data?.results || data.results.length === 0) {
    return FALLBACK_MOVIES.slice(0, 8);
  }
  return data.results.map((m) => mapTMDBToMovie(m));
}

/**
 * Fetch top rated movies from TMDB
 */
export async function getTopRatedMovies(): Promise<Movie[]> {
  const data = await fetchFromTMDB<{ results: TMDBMovieSummary[] }>("/movie/top_rated");
  if (!data?.results || data.results.length === 0) {
    return [...FALLBACK_MOVIES].sort((a, b) => b.rating - a.rating);
  }
  return data.results.map((m) => mapTMDBToMovie(m));
}

/**
 * Fetch Tamil movies using TMDB discover endpoint
 */
export async function getTamilMovies(): Promise<Movie[]> {
  const data = await fetchFromTMDB<{ results: TMDBMovieSummary[] }>("/discover/movie", {
    with_original_language: "ta",
    sort_by: "popularity.desc",
  });
  if (!data?.results || data.results.length === 0) {
    return FALLBACK_MOVIES.filter((m) => m.language === "Tamil");
  }
  return data.results.map((m) => mapTMDBToMovie(m));
}

/**
 * Search movies by text query from TMDB
 */
export async function searchMovies(query: string): Promise<Movie[]> {
  const q = query.trim();
  if (!q) {
    return getTrendingMovies();
  }

  // Check if searching for a language like "Tamil", "Telugu", etc.
  const lowerQ = q.toLowerCase();
  const matchedLangCode = Object.keys(LANGUAGE_MAP).find(
    (code) => LANGUAGE_MAP[code].toLowerCase() === lowerQ
  );

  if (matchedLangCode) {
    const data = await fetchFromTMDB<{ results: TMDBMovieSummary[] }>("/discover/movie", {
      with_original_language: matchedLangCode,
      sort_by: "popularity.desc",
    });
    if (data?.results && data.results.length > 0) {
      return data.results.map((m) => mapTMDBToMovie(m));
    }
  }

  const data = await fetchFromTMDB<{ results: TMDBMovieSummary[] }>("/search/movie", {
    query: q,
  });

  if (!data?.results || data.results.length === 0) {
    // Fallback to local filtering
    return FALLBACK_MOVIES.filter(
      (m) =>
        m.title.toLowerCase().includes(lowerQ) ||
        m.language.toLowerCase().includes(lowerQ) ||
        m.genres.some((g) => g.toLowerCase().includes(lowerQ)) ||
        m.director.toLowerCase().includes(lowerQ) ||
        m.cast.some((c) => c.name.toLowerCase().includes(lowerQ))
    );
  }

  return data.results.map((m) => mapTMDBToMovie(m));
}

/**
 * Fetch full movie details with credits, videos, and watch providers
 */
export async function getMovieDetails(id: number): Promise<Movie> {
  const data = await fetchFromTMDB<TMDBMovieDetails>(`/movie/${id}`, {
    append_to_response: "credits,videos,watch/providers",
  });

  if (!data) {
    const fallback = FALLBACK_MOVIES.find((m) => m.id === id);
    if (fallback) return fallback;
    return {
      id,
      title: "Movie Details",
      year: 2024,
      rating: 7.5,
      language: "Tamil",
      genres: ["Action", "Drama"],
      runtime: "2h 15m",
      overview: "Information could not be loaded from TMDB. Please check your API key.",
      tagline: "",
      director: "Unknown",
      poster: DEFAULT_POSTER,
      backdrop: DEFAULT_BACKDROP,
      trailerId: "bk5lKWDVJAI",
      cast: [],
      streaming: [],
    };
  }

  return mapTMDBToMovie(data, data);
}

/**
 * Fetch movie credits (cast and crew)
 */
export async function getMovieCredits(id: number): Promise<TMDBCredits | null> {
  return fetchFromTMDB<TMDBCredits>(`/movie/${id}/credits`);
}

/**
 * Fetch movie trailers and videos
 */
export async function getMovieVideos(id: number): Promise<TMDBVideos | null> {
  return fetchFromTMDB<TMDBVideos>(`/movie/${id}/videos`);
}

/**
 * Fetch movie watch providers (streaming platforms)
 */
export async function getWatchProviders(id: number): Promise<TMDBWatchProviders | null> {
  return fetchFromTMDB<TMDBWatchProviders>(`/movie/${id}/watch/providers`);
}
