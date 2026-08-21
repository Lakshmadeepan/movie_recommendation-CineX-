Design a modern, premium, interactive **Movie Recommendation System** website that will be directly implemented using **React.js + Vite + Tailwind CSS** with a **FastAPI backend**.

The website does NOT require login or signup.

## Design Theme

Use a **creamy white / warm off-white** as the primary background instead of pure white.

Overall style:

* Premium
* Minimal
* Cinematic
* Modern
* Attractive
* Clean
* Highly responsive
* Smooth interactive feel
* Desktop-first but fully responsive for tablet and mobile

Use dark text with subtle accent colors that complement the creamy-white background.

Avoid an overly colorful design. Keep the interface elegant and professional.

## Main Navigation

Create a clean top navigation bar containing:

* Movie recommendation system logo/name
* Home
* Movies
* Genres
* Search
* Optional language filter

Keep the navigation simple and responsive.

## Home Page

Create an attractive hero section.

Include:

* Large cinematic movie background/image area
* Main heading such as:
  "Discover Your Next Favorite Movie"
* Short supporting text
* Large movie search bar
* Search icon
* Search placeholder:
  "Search movies, actors or genres..."

The search bar must be visually prominent.

Below the hero section create:

### Trending Movies

Horizontal movie-card carousel.

Each card should contain:

* Movie poster
* Movie title
* Release year
* Rating
* Hover interaction

### Popular Movies

Another horizontal movie section.

### Tamil Movies

A dedicated section for Tamil movies.

### Popular Languages / Genres

Create attractive filter chips or cards for:

* Tamil
* Telugu
* Malayalam
* Hindi
* Kannada
* English
* Action
* Comedy
* Thriller
* Romance
* Sci-Fi
* Drama

## Search Results Page

When the user searches for a movie, show a clean search-results layout.

Include:

* Search input at the top
* Search query
* Number of results
* Movie cards in a responsive grid

Each movie card should contain:

* Poster
* Movie title
* Release year
* Rating
* Language
* Genre

Cards should have smooth hover animations.

## Movie Details Page

Create a premium movie-details layout.

Include:

* Large movie backdrop
* Movie poster
* Movie title
* Tagline / one-line description
* Rating
* Release date
* Runtime
* Language
* Genres
* Overview
* Director
* Cast
* Crew
* Trailer button
* Watch / Streaming availability section

Create a dedicated section:

### Where to Watch

Provide a clean area for streaming platforms.

IMPORTANT:
Leave clearly structured UI space for dynamically loaded API data.

Do NOT hardcode movie data.

Create placeholders/components for:

* Poster URL
* Backdrop URL
* Rating
* Release date
* Overview
* Cast
* Crew
* Streaming platforms
* Trailer URL

These sections should be easy to connect to the TMDB API later.

## Recommendation Section

Below the movie details, create:

### Recommended For You

Subtitle:
"Because you watched [Movie Name]"

Display 5–10 recommended movie cards.

The recommendation cards should be designed so they can receive dynamic results from the KNN recommendation API.

Each card:

* Poster
* Title
* Rating
* Release year
* Language

Add smooth horizontal scrolling/carousel behavior.

When a user clicks a recommended movie, open its movie-details page.

## Interactive Behaviour

Design UI states for:

* Search
* Loading
* Movie results
* Empty search results
* API loading skeleton
* API error
* Movie details loading
* Recommendation loading
* No recommendations available

Use skeleton loaders rather than blank spaces.

Add:

* Hover animations
* Card scale effects
* Smooth transitions
* Button hover states
* Search focus states
* Carousel interactions
* Smooth page transitions

## API Integration-Friendly Design

The UI will later connect to:

* TMDB API for movie information
* FastAPI backend
* KNN recommendation model

Therefore, structure the UI into reusable components.

Create separate reusable components for:

* Navbar
* SearchBar
* MovieCard
* MovieGrid
* MovieCarousel
* MovieDetails
* CastCard
* CrewSection
* Rating
* GenreBadge
* LanguageFilter
* StreamingPlatform
* RecommendationSection
* LoadingSkeleton
* Footer

Keep API-dependent content inside clearly separated components so React developers can easily replace placeholder data with API responses.

Do not create unnecessary database/login UI.

## Responsive Design

Create responsive layouts for:

* Desktop
* Tablet
* Mobile

On mobile:

* Convert navigation into a compact menu
* Make search bar full width
* Convert movie grids into 2-column or 1-column layouts where appropriate
* Make horizontal movie carousels touch-friendly
* Stack movie details vertically
* Keep buttons easily tappable

## Footer

Create a professional footer.

Include:

"Developed by Lakshmadeepan"

Add a LinkedIn icon and LinkedIn profile link placeholder.

Also include:

* About
* Contact
* GitHub placeholder
* LinkedIn
* Copyright

Use placeholders for social links so they can be replaced during React development.

## Developer-Friendly Structure

Design the entire UI as reusable React components.

Use consistent:

* Spacing
* Typography
* Border radius
* Buttons
* Cards
* Shadows
* Responsive breakpoints

Keep the design realistic to implement using:

React.js
Vite
Tailwind CSS
Framer Motion

Do not design components that require unnecessary complex custom graphics.

The final Figma design should look like a **real production movie discovery platform**, not a basic college project.

Use realistic placeholder movie posters and content only for visual design. During development, all movie information will be dynamically loaded through APIs.

Create a complete clickable prototype showing:

Home → Search → Search Results → Movie Details → Recommended Movie → Movie Details

Make the prototype visually polished, interactive, responsive, and implementation-friendly.
