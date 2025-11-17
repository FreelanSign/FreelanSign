# Sidebar Responsive Fix - Context

**Last Updated: 2025-11-17**

## Problem Statement

Sidebar component overlaps page content on `QuoteCreatePage` when viewport width is between ~1024px and ~1512px.

## Key Files

### Primary Files (to modify)
1. **frontend/src/interface/pages/Quote/QuoteCreatePage.tsx**
   - Line 504-506: Main container, Sidebar, and Navbar render
   - Current: `<main className={container mx-auto p-6 grid gap-6 ${styles.page}}>`
   - Need to add: `${styles.withSidebar}` class

2. **frontend/src/interface/pages/Quote/quote-edit-create.module.css**
   - Contains page-specific styles
   - Need to add: Media query for sidebar margin compensation

### Reference Files (for understanding)
3. **frontend/src/interface/components/sidebar/Sidebar.tsx**
   - Sidebar component implementation
   - Line 64-112: Sidebar structure with fixed positioning

4. **frontend/src/interface/components/sidebar/sidebar.module.css**
   - Line 14-29: `.sidebar` with `position: fixed`, `width: 96px`
   - Line 120-124: Breakpoint at 1024px that hides sidebar

5. **frontend/src/interface/components/navbar/Navbar.tsx**
   - Also renders on the page (line 506 of QuoteCreatePage)
   - Handles own responsive layout

## Technical Details

### Sidebar Specifications
- **Width**: 96px
- **Position**: `fixed` (left: 0, top: 0)
- **Z-index**: 50
- **Breakpoint**: Hidden when viewport < 1024px
- **Background**: `var(--sidebar-bg)` (#f5f7fa)

### Current Layout Issue
```
Viewport < 1024px:     [=== Content (full width) ===]        ✅ Works
Viewport 1024-1512px:  [S][=== Content overlaps ===]         ❌ Bug
Viewport > 1512px:     [S]  [=== Content ===]                ✅ Works

S = Sidebar (96px)
```

### Proposed Fix
```css
@media (min-width: 1025px) {
  .withSidebar {
    margin-left: 96px;
    max-width: calc(100% - 96px);
  }
}
```

## Architecture Context

### Frontend Structure
```
frontend/src/interface/
├── pages/Quote/
│   ├── QuoteCreatePage.tsx         ← Main file to fix
│   └── quote-edit-create.module.css ← Add CSS here
├── components/
│   ├── sidebar/
│   │   ├── Sidebar.tsx             ← Reference only
│   │   └── sidebar.module.css      ← Reference only
│   └── navbar/
│       ├── Navbar.tsx              ← Coexists with Sidebar
│       └── Navbar.module.css
```

### Design System Variables (CSS Custom Properties)
From both CSS files:
```css
--brand: #2456c2
--success: #3ccf91
--accent: #ff8a3d
--dark: #0d0d0d
--paper: #f5f7fa
--sidebar-bg: #f5f7fa
--icon-bg: rgba(255, 255, 255, 0.92)
--icon-border: #3ccf91
--text: #222
```

## Key Decisions

### Decision 1: CSS Module Approach
- **Choice**: Add `.withSidebar` class to existing CSS module
- **Rationale**: Minimal change, scoped to affected page
- **Alternative**: Global layout wrapper (more complex, future enhancement)

### Decision 2: Breakpoint Selection
- **Choice**: Use `min-width: 1025px` (just above sidebar hide breakpoint)
- **Rationale**: Aligns with existing sidebar breakpoint at 1024px
- **Alternative**: Different breakpoint (would need design system alignment)

### Decision 3: Margin Strategy
- **Choice**: Left margin + max-width adjustment
- **Rationale**: Simple, predictable, doesn't break existing layout
- **Alternative**: Padding (would affect internal spacing), Flexbox wrapper (more complex)

## Dependencies

### Technical Stack
- React 18+ (TypeScript)
- React Router (for navigation)
- CSS Modules
- React Hook Form (used in QuoteCreatePage)

### Build Tools
- Vite (likely, based on frontend structure)
- TypeScript compiler
- CSS preprocessor (if any)

### Testing Requirements
- Browser DevTools for responsive testing
- No automated tests currently specified
- Manual QA across viewport ranges

## Related Components

### Pages that may need similar fix
Search for files importing `Sidebar`:
```bash
grep -r "import.*Sidebar" frontend/src/interface/pages/
```

### Common Layout Patterns
If multiple pages have this issue, consider:
1. Creating `<SidebarLayout>` wrapper component
2. Updating global CSS for `.container` class
3. Adding layout utility classes

## Edge Cases

1. **Very narrow content + sidebar**: Content < 600px usable width
   - Sidebar already hides at 1024px, so minimum is ~928px content

2. **Horizontal scroll**: Ensure fix doesn't introduce scroll
   - Use `max-width: calc(100% - 96px)` to prevent

3. **Z-index conflicts**: Navbar vs Sidebar stacking
   - Current: Sidebar z-index: 50
   - Check Navbar z-index if issues arise

4. **Print layout**: Sidebar should not appear in print
   - Check if print styles exist, may need `@media print`

## Browser Compatibility

Target browsers (assumed modern):
- Chrome/Edge (Chromium) latest
- Firefox latest
- Safari latest

CSS features used:
- CSS Custom Properties (widely supported)
- calc() (widely supported)
- Media queries (universal support)
- CSS Modules (build-time transform)

## Future Improvements

1. **Global layout system**: Extract to reusable component
2. **Sidebar collapse**: Add toggle for manual hide/show
3. **Responsive refinement**: Adjust breakpoints based on analytics
4. **Accessibility**: Ensure keyboard nav works with fixed sidebar
5. **Mobile drawer**: Consider drawer pattern for <1024px instead of hide

## Notes from Codebase

- Project uses **absolute imports**: `from apps.quote.domain import ...`
- **Clean Architecture**: Frontend follows domain/infrastructure/interface pattern
- **Conventional commits**: Required for changelog
- **Type safety**: Strict TypeScript (must type-check before commit)
