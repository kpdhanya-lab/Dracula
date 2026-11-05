---
name: Luminous Hydro Glass
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3f4850'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#707881'
  outline-variant: '#bfc7d2'
  surface-tint: '#006398'
  primary: '#006194'
  on-primary: '#ffffff'
  primary-container: '#007bb9'
  on-primary-container: '#fdfcff'
  inverse-primary: '#93ccff'
  secondary: '#00687a'
  on-secondary: '#ffffff'
  secondary-container: '#57dffe'
  on-secondary-container: '#006172'
  tertiary: '#6b38d4'
  on-tertiary: '#ffffff'
  tertiary-container: '#8455ef'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 52px
    fontWeight: '800'
    lineHeight: 60px
    letterSpacing: -0.03em
  display-hero-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system translates critical, often anxiety-inducing hydrological data into an approachable, transparent, and vibrant civic tool. Designed for civic explorers, researchers, urban planners, and affected citizens, the visual identity replaces traditional dry disaster mapping with a luminous, energetic, and optimistic interface.

The design movement combines **Vibrant Glassmorphism** with **Playful Modern UI**. Surfaces behave like clear water caught in sunlight: translucent frosted layers, chromatic highlights, and fluid micro-interactions with gentle spring kinetics. Complex catchment systems and flood thresholds are communicated through high-clarity color codes, soft pill containers, and bright ambient luminescence rather than dense tables or harsh militaristic radar tones.

## Colors

The palette draws directly from water bodies, atmospheric light, and sunset horizons over floodplains. The default canvas is an ultra-clean, crystalline light mode that allows tinted glass elements to refract without visual muddiness.

- **Primary Canvas & Sky:** Deep Sky Blue (`#0284C7`) and Sky Tint (`#38BDF8`) guide the primary hierarchy, core actions, and current stream stages.
- **Aquatic Middleground:** Aqua (`#06B6D4`) and Turquoise (`#14B8A6`) indicate baseline hydrology, safe pool levels, and interactive filtration toggles.
- **Topographic Violet:** Purple/Violet (`#8B5CF6`) denotes elevated basins, multi-catchment aggregation, and analytical overlay states.
- **Warm Accents:** Coral (`#FB7185`), Sunset Orange (`#F97316`), and Sunshine Yellow (`#FBBF24`) represent rising water trends, warnings, and energetic callouts.
- **Background Ecosystem:** Surfaces transition across Canvas Mist (`#F8FAFC`) down into Luminous Aqua-Wash (`#F0F9FF`), anchored by Slate Neutral (`#64748B`) and Deep Obsidian (`#0F172A`) for high-legibility typography.
- **Hazard Status Matrix:** Clear semantic tokens ensure instant cognitive parsing:
  - Normal / Safe: Emerald Green (`#10B981`)
  - Watch / Minor: Amber Yellow (`#F59E0B`)
  - Warning / Significant: Coral Orange (`#F97316`)
  - Emergency / Extreme: Vivid Red (`#EF4444`)

## Typography

The typography uses **Plus Jakarta Sans** across all roles to achieve a warm, highly legible, and rounded geometric cadence. Its wide apertures, friendly counters, and confident terminals ensure technical hydrology readouts feel approachable rather than intimidating.

- Headings use tight negative letter-spacing and heavier weights (`700` and `800`) to create strong anchor points over translucent glass panels.
- Numerical measurements (e.g., flow rate `m³/s`, river crest feet) always employ tabular figures (`tnum`) with bold weights to avoid shifting layouts during live hydrologic updates.
- Micro-labels and warning badges use uppercased or prominent medium tracking (`+0.02em` to `+0.04em`) to maintain legibility against varied background map blurs.

## Layout & Spacing

The platform follows a responsive 12-column fluid grid system paired with layered, floating floating sheet navigation on top of an interactive canvas.

- **Desktop (1280px+):** 12 columns, 24px (`1.5rem`) gutters, 32px (`2rem`) margins. Side-docks, analytical drawers, and search controllers float as frosted modules with 24px safe gaps between the viewport boundary and the map canvas.
- **Tablet (768px - 1279px):** 8 columns, 20px gutters, 24px margins. Sliding glass trays stack from the bottom edge; map inspection panels span 4 to 8 columns.
- **Mobile (< 768px):** 4 columns, 16px (`1rem`) gutters, 16px margins. Primary navigation and flood timeline controls dock into an anchored glass bottom bar with safe area padding. Full-screen map controls collapse into floating pill clusters.

## Shapes

The shape system adopts a pill-shaped, hyper-rounded geometry (`roundedness: 3`) to evoke organic water drops and tactile buoyancy.

- **Primary actions, status chips, and toggles:** Use fully rounded capsules (`border-radius: 9999px` / `pill-full`).
- **Cards, alert sheets, and modal panels:** Use extra-large organic rounding (`border-radius: 2rem` or `rounded-2xl`).
- **Data inputs, sliders, and nested controls:** Use soft capsule containers (`border-radius: 1.25rem`).
- **Dividers & Indicators:** Edge tracks and slider handles feature circular and tubular pill profiles to maintain smooth, non-aggressive silhouettes.

## Components

### Buttons & Interactive Badges
- **Primary Pill:** Gradient-filled (`#0284C7` to `#06B6D4`), high-contrast white text, pill radius, paired with an inner top gloss line (`inset 0 1px 1px rgba(255, 255, 255, 0.4)`). Hover states trigger a bouncy scale up (`transform: scale(1.03)` with cubic-bezier spring `cubic-bezier(0.34, 1.56, 0.64, 1)`).
- **Secondary Glass Pill:** Frosted translucent background (`rgba(255, 255, 255, 0.8)`), border highlight (`rgba(56, 189, 248, 0.4)`), primary-colored text. Hover adds a warm sunshine or aqua glow.
- **Alert Badges:** Pill-shaped status caps with an animated pulsing orb indicator (e.g., Emerald Green glow for "Normal Pool Level", Coral/Red strobe for "Active Spillway Release").

### Cards & Flood Station Panels
- Structured with 2rem (`32px`) rounded corners and frosted backdrop blur.
- Header sections feature micro-tags indicating river catchment names along with real-time status pills.
- Gradient rim lighting adapts based on basin risk: cyan/sky for nominal stages, warming into violet/coral transitions as discharge rates increase.

### Inputs & Scrubbers
- **Hydro Search Input:** Rounded pill container with a prominent magnifying icon, translucent white background, and an active neon-aqua focus ring (`0 0 0 4px rgba(6, 182, 212, 0.25)`).
- **Flood Time-Scrubber:** A glass capsule slider that lets users drag between historical, real-time, and projected flood forecast models. The thumb handle is an elevated circular drop with an inner liquid tint, providing tactile haptic and visual bounce upon dragging.

### Checkboxes, Switches, & Radio Pills
- Toggle switches adopt plump capsule tracks (`48px x 28px`) with fluid sliding spheres that stretch slightly during movement (`jelly transition`).
- Multi-select basin filters exist as clickable frosted chips that turn into bright cyan or violet pills when active.

### Water Level Gauges & Visualization Cards
- Visual depth is represented via translucent liquid gauge tubes with subtle animated water surface waves.
- Critical threshold markers (Minor, Moderate, Major Flood) are styled as floating pill pins intersecting the water level column for immediate, cross-demographic comprehension.