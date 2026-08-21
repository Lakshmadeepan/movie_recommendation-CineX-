import { type Movie, FALLBACK_MOVIES } from "./api";

/**
 * ══════════════════════════════════════════════════════════════════════════════
 * RECOMMENDATION ENGINE SERVICE (ISOLATED)
 * ══════════════════════════════════════════════════════════════════════════════
 * This module is temporarily using content-based heuristic matching.
 * It is isolated here so it can be swapped with the FastAPI KNN Recommender
 * API endpoint (`/api/movies/{id}/recommendations`) in the next phase.
 */

export async function getRecommendationsForMovie(targetMovie: Movie, limit = 6): Promise<Movie[]> {
  // Try local / mock similarity matching first
  const candidates = FALLBACK_MOVIES.filter((m) => m.id !== targetMovie.id);

  const scored = candidates.map((m) => {
    let score = 0;
    // Same language
    if (m.language.toLowerCase() === targetMovie.language.toLowerCase()) {
      score += 3;
    }
    // Shared genres
    const sharedGenres = m.genres.filter((g) =>
      targetMovie.genres.map((tg) => tg.toLowerCase()).includes(g.toLowerCase())
    );
    score += sharedGenres.length * 2;

    // Rating proximity
    score += (10 - Math.abs(m.rating - targetMovie.rating)) * 0.2;

    return { movie: m, score };
  });

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, limit).map((s) => s.movie);
}
