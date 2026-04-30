---
name: Precision Translation Interface
colors:
  surface: '#fbf8fa'
  surface-dim: '#dcd9db'
  surface-bright: '#fbf8fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f4'
  surface-container: '#f0edef'
  surface-container-high: '#eae7e9'
  surface-container-highest: '#e4e2e3'
  on-surface: '#1b1b1d'
  on-surface-variant: '#45474c'
  inverse-surface: '#303032'
  inverse-on-surface: '#f3f0f2'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545f73'
  primary: '#091426'
  on-primary: '#ffffff'
  primary-container: '#1e293b'
  on-primary-container: '#8590a6'
  inverse-primary: '#bcc7de'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#1e1200'
  on-tertiary: '#ffffff'
  tertiary-container: '#35260c'
  on-tertiary-container: '#a38c6a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e3fb'
  primary-fixed-dim: '#bcc7de'
  on-primary-fixed: '#111c2d'
  on-primary-fixed-variant: '#3c475a'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#fadfb8'
  tertiary-fixed-dim: '#ddc39d'
  on-tertiary-fixed: '#271902'
  on-tertiary-fixed-variant: '#564427'
  background: '#fbf8fa'
  on-background: '#1b1b1d'
  surface-variant: '#e4e2e3'
typography:
  display:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  heading:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  code:
    fontFamily: monospace
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  pane-padding: 12px
  gutter: 1px
  toolbar-height: 40px
  sidebar-width: 260px
---

## Brand & Style
The design system is engineered for high-performance translation environments where cognitive load must be minimized and data density maximized. It adopts a **Corporate/Modern** style infused with **Functional Minimalism**, prioritizing utility over ornamentation. The brand personality is scholarly, disciplined, and rigorous—echoing the precision required in professional linguistic conversion.

This design system avoids visual distractions to allow the user to focus on complex syntactic structures and terminology management. Every UI decision is driven by the need for clarity in high-density information environments, ensuring that the interface feels like a professional-grade instrument rather than a consumer application.

## Colors
The palette is built upon a foundation of **Porcelain and Off-white surfaces** to provide a clean, paper-like backdrop for translation tasks. **Slate and Graphite** serve as the primary anchors for text and structural elements, providing high contrast without the harshness of pure black.

Semantic colors are used sparingly but decisively:
- **Blue** identifies the current focus and primary actions.
- **Green** indicates verified segments or successful machine translation matches.
- **Amber** flags candidate translations or segments requiring review.
- **Red** denotes rejected strings or syntax errors.
- **Violet** highlights grammar insights and machine learning suggestions.

Contrast ratios are strictly maintained to ensure readability across long working sessions.

## Typography
The design system utilizes **Inter** for its exceptional legibility in high-density interfaces and its robust support for the varied diacritics of Vietnamese and the complex strokes of Chinese characters.

The type hierarchy is compact. Large display sizes are avoided in favor of subtle weight increases and letter-spacing adjustments. To accommodate the "data-rich" requirement, the system relies heavily on 13px and 14px sizes for primary work areas. Monospaced fallbacks are utilized for technical strings or tags to ensure character alignment in translation segments.

## Layout & Spacing
The layout follows an **IDE-inspired fluid grid** that maximizes screen real estate. The workspace is divided into functional zones:
- **Fixed Toolbars:** Top-aligned for global actions, using a strict 40px height.
- **Split-Panes:** The central work area uses adjustable vertical and horizontal splits to balance source text, target text, and translation memory.
- **Sidebars:** Collapsible utility panels for glossary, history, and project files.

A 4px spacing rhythm is applied globally. Containers use internal padding of 12px to maintain a compact feel while preventing content from touching borders. Borders are the primary method of separation, reducing the need for excessive negative space.

## Elevation & Depth
In this design system, hierarchy is communicated through **Tonal Layers and Bold Borders** rather than shadows.
- **Surface Level 0 (Porcelain):** The background of the entire workstation.
- **Surface Level 1 (White):** Primary content areas, such as the active translation cell.
- **Structural Dividers:** 1px Slate (#CBD5E1) borders define all panel boundaries.

Shadows are restricted to transient elements like dropdown menus or tooltips, using a very tight, neutral blur (4px blur, 10% opacity) to signify that they sit above the workspace. No glassmorphism or blur effects are permitted, ensuring maximum rendering performance for large documents.

## Shapes
The shape language is conservative and precise. A standard **6px border radius** is applied to buttons, input fields, and cards to soften the interface slightly without losing its serious, professional character.

Badges and status indicators use a smaller 4px radius or remain rectangular to maintain the high-density aesthetic. Large rounded corners are avoided as they waste valuable screen real estate in a tiled panel layout.

## Components
### Buttons & Controls
Buttons are low-profile, using the Slate primary color for outlines or solid fills. Segmented controls are preferred over tabs for pane-level navigation to save vertical space.

### Data Grids & Tables
The core of the system is the high-density table. Row heights are locked at 32px for metadata and expand dynamically for translation text. Hover states on rows use a subtle Porcelain tint (#F1F5F9) to aid eye-tracking across wide screens.

### Badges & Status
Compact, rectangular badges with 11px uppercase text identify "MT" (Machine Translation), "TM" (Translation Memory), or "Verified." They use a light background tint of their respective semantic color with a high-contrast text label.

### Translation Cells
Active translation cells are highlighted with a 2px Blue left-border and a white background to distinguish them from the read-only source text.

### Toolbars
Toolbars use 16px iconography with 1px stroke weights. Icons must be utilitarian and lack decorative fills.
