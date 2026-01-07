# BlogLayout Component - Usage Guide

## Overview

`BlogLayout` is a reusable component for blog article pages in the Whisper Cheap website. It provides a complete, production-ready article template with:

- Responsive layout (mobile, tablet, desktop)
- Navigation bar with language switching
- Breadcrumb navigation
- Article header with metadata (date, reading time, author)
- Table of Contents (auto-generated from headings or provided)
- Sticky sidebar with active heading tracking
- Related articles section
- Call-to-action footer
- Full accessibility (a11y) and SEO semantics
- Prose-optimized typography for readability

## Component Location

```
src/components/BlogLayout.tsx
```

## Props

```typescript
interface BlogLayoutProps {
  /**
   * Article title (h1)
   */
  title: string

  /**
   * Publication date (ISO 8601 or readable format)
   */
  date: string

  /**
   * Estimated reading time (e.g., "5 min read")
   */
  readingTime: string

  /**
   * Current language
   */
  lang: Locale

  /**
   * Article content (markdown or JSX)
   */
  children: ReactNode

  /**
   * Optional breadcrumb navigation items
   * @default [{ label: 'Home', href: `/${lang}` }, { label: 'Blog', href: `/${lang}/blog` }]
   */
  breadcrumbs?: Array<{ label: string; href: string }>

  /**
   * Optional author information
   */
  author?: {
    name: string
    role?: string
    image?: string
  }

  /**
   * Optional related articles to show in sidebar
   */
  relatedArticles?: Array<{
    title: string
    slug: string
    date: string
    readingTime: string
  }>

  /**
   * Optional table of contents extracted from headings
   * If not provided, will be auto-generated from h2/h3 elements
   */
  tableOfContents?: Array<{
    id: string
    label: string
    level: number
  }>
}
```

## Basic Usage

### Simple Article (minimal props)

```tsx
import { BlogLayout } from '@/components/BlogLayout'

export default function BlogPost({ params }: { params: { lang: Locale } }) {
  return (
    <BlogLayout
      title="How to Use Whisper Cheap for Documentation"
      date="2024-01-15"
      readingTime="8 min read"
      lang={params.lang}
    >
      <h2>Introduction</h2>
      <p>Your article content goes here...</p>

      <h2>Section 1</h2>
      <p>More content...</p>

      <h3>Subsection</h3>
      <p>Details...</p>
    </BlogLayout>
  )
}
```

### Full Example (all props)

```tsx
import { BlogLayout } from '@/components/BlogLayout'
import { getDictionary, type Locale } from '@/dictionaries'

export default async function BlogPost({
  params
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)

  const relatedArticles = [
    {
      title: "Getting Started with Voice Dictation",
      slug: "getting-started",
      date: "2024-01-10",
      readingTime: "5 min read"
    },
    {
      title: "Privacy and Security Best Practices",
      slug: "privacy-guide",
      date: "2024-01-12",
      readingTime: "7 min read"
    }
  ]

  return (
    <BlogLayout
      title="Advanced Tips for Developers"
      date="2024-01-15"
      readingTime="12 min read"
      lang={params.lang}
      author={{
        name: "Andrés Feding",
        role: "Creator",
        image: "/authors/andres.jpg"
      }}
      relatedArticles={relatedArticles}
      tableOfContents={[
        { id: "intro", label: "Introduction", level: 2 },
        { id: "setup", label: "Setup", level: 2 },
        { id: "config", label: "Configuration", level: 3 },
        { id: "tips", label: "Pro Tips", level: 2 }
      ]}
      breadcrumbs={[
        { label: params.lang === 'en' ? 'Home' : 'Inicio', href: `/${params.lang}` },
        { label: 'Blog', href: `/${params.lang}/blog` },
        { label: 'Developers', href: `/${params.lang}/blog/developers` }
      ]}
    >
      <h2 id="intro">Introduction</h2>
      <p>Content here...</p>

      <h2 id="setup">Setup</h2>
      <p>Setup content...</p>

      <h3 id="config">Configuration</h3>
      <p>Config details...</p>

      <h2 id="tips">Pro Tips</h2>
      <p>Tips content...</p>
    </BlogLayout>
  )
}
```

## File Structure Example

Create blog posts in this structure:

```
src/app/[lang]/blog/
├── page.tsx                          # Blog index/listing
├── [slug]/
│   ├── page.tsx                      # Individual blog post
│   ├── (examples)
│   │   ├── getting-started/page.tsx
│   │   ├── privacy-guide/page.tsx
│   │   └── advanced-tips/page.tsx
```

## Creating a Blog Post

### Step 1: Create the page file

```tsx
// src/app/[lang]/blog/getting-started/page.tsx
'use client'

import { BlogLayout } from '@/components/BlogLayout'
import type { Locale } from '@/dictionaries'

export default function GettingStartedPage({ params }: { params: { lang: Locale } }) {
  return (
    <BlogLayout
      title={params.lang === 'en' ? 'Getting Started with Whisper Cheap' : 'Empezando con Whisper Cheap'}
      date="2024-01-10"
      readingTime={params.lang === 'en' ? "5 min read" : "5 min de lectura"}
      lang={params.lang}
    >
      <h2>Why Voice Dictation?</h2>
      <p>Speaking is faster than typing. Much faster.</p>

      <h2>Installation</h2>
      <ol>
        <li>Download from GitHub</li>
        <li>Run the installer</li>
        <li>Press Ctrl+Space to start</li>
      </ol>

      <h2>Your First Dictation</h2>
      <p>Open any text editor and press your hotkey...</p>
    </BlogLayout>
  )
}
```

### Step 2: Add metadata (optional but recommended)

```tsx
import type { Metadata } from 'next'

export async function generateMetadata({
  params
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  return {
    title: params.lang === 'en'
      ? 'Getting Started with Whisper Cheap'
      : 'Empezando con Whisper Cheap',
    description: params.lang === 'en'
      ? 'Learn how to install and use Whisper Cheap for the first time.'
      : 'Aprende a instalar y usar Whisper Cheap por primera vez.',
    openGraph: {
      title: 'Getting Started',
      description: 'Quick start guide for Whisper Cheap',
      type: 'article',
      publishedTime: '2024-01-10T00:00:00Z'
    }
  }
}
```

## Styling & Customization

### Prose Styling Classes

The component uses the `.prose-article` class for content styling. All standard HTML elements are automatically styled:

- **Headings**: h2, h3, h4 - Sora font family, auto scroll-margin-top
- **Links**: Green accent color with underline
- **Code**: Inline `code` and `<pre>` blocks with syntax highlighting
- **Blockquotes**: Accent-colored left border with subtle background
- **Lists**: Proper indentation and spacing
- **Tables**: Clean styling with hover effects
- **Images**: Responsive with border radius

### Customizing Prose Colors

Edit the color values in `src/app/globals.css` under the `/* === PROSE STYLING FOR BLOG ARTICLES === */` section:

```css
.prose-article a {
  color: #00ff88;  /* Link color */
  border-bottom: 1px solid rgba(0, 255, 136, 0.3);
}
```

### Adding Custom Elements to Articles

The prose container supports all standard HTML elements. Add custom styles in `globals.css`:

```css
/* Custom styling for article blockquotes */
.prose-article .custom-callout {
  background: rgba(0, 255, 136, 0.08);
  border-left: 4px solid #00ff88;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  margin: 1.5rem 0;
}
```

## Features

### Auto-Generated Table of Contents

If you don't provide `tableOfContents` prop, the component will automatically extract headings from the article:

```tsx
<BlogLayout
  title="Article"
  date="2024-01-15"
  readingTime="5 min"
  lang="en"
>
  {/* These headings are automatically added to TOC */}
  <h2 id="section-1">Section 1</h2>
  <h3 id="subsection">Subsection</h3>
  <h2 id="section-2">Section 2</h2>
</BlogLayout>
```

**Note:** IDs are auto-generated from text content if not provided. Best practice: manually set IDs for consistency.

### Sticky TOC with Active Heading Tracking

The sidebar TOC:
- Sticks to viewport on scroll
- Highlights the current section being read
- Smooth scroll to section on click
- Responsive: hidden on mobile, visible on lg+ screens

### Related Articles Sidebar

Show related content to encourage exploration:

```tsx
relatedArticles={[
  {
    title: "Related Article 1",
    slug: "article-1",
    date: "2024-01-12",
    readingTime: "4 min read"
  }
]}
```

### Author Information

Display author info in article header:

```tsx
author={{
  name: "Andrés Feding",
  role: "Creator",
  image: "/authors/andres.jpg"  // Optional
}}
```

## Accessibility Features

The component includes:

- Semantic HTML (`<article>`, `<nav>`, `<aside>`, `<time>`)
- Proper heading hierarchy (h1 > h2/h3)
- ARIA labels on buttons and navigation
- Focus-visible outlines (green accent)
- Keyboard navigation (Tab, Enter, Space)
- Color contrast compliance (WCAG AA+)
- Scroll-margin-top on headings for fixed nav
- Screen reader friendly breadcrumbs

## SEO Best Practices

1. **Use semantic HTML**: Headings, lists, tables are properly structured
2. **Include metadata**: Use Next.js `generateMetadata` for each post
3. **Internal linking**: Link to related articles and other pages
4. **Images**: Use proper alt text
5. **Structured data**: The component uses `<time datetime>` for dates
6. **Breadcrumbs**: Helps search engines understand site structure

Example metadata:

```tsx
export const metadata: Metadata = {
  title: 'Blog Post Title',
  description: 'Brief description for search results',
  keywords: ['keyword1', 'keyword2'],
  openGraph: {
    title: 'Blog Post Title',
    description: 'Description',
    type: 'article',
    publishedTime: '2024-01-15',
    authors: ['Author Name']
  },
  twitter: {
    card: 'summary_large_image'
  }
}
```

## Responsive Design

The layout is fully responsive:

- **Mobile** (< 768px): Single column, TOC hidden, larger touch targets
- **Tablet** (768px - 1024px): TOC slides in sidebar
- **Desktop** (> 1024px): 3-column grid (article + 2 sidebars)

## Performance

The component uses:

- `useMemo` for breadcrumb calculations
- `useEffect` with cleanup for scroll listeners
- Lazy rendering of optional sections (TOC, related articles)
- Memoized date formatting
- No unnecessary re-renders

## Date Formatting

Dates are automatically formatted to locale-specific format:

```
English (en): January 15, 2024
Spanish (es): 15 de enero de 2024
```

Pass ISO 8601 format (`YYYY-MM-DD`) or any valid date string. The component handles both.

## Language Support

The component is fully bilingual (English/Spanish):

- Automatically uses `lang` prop to determine locale
- All labels are translated (Home, Blog, etc.)
- Date formatting respects locale
- Breadcrumbs use translated labels by default

## Example: Complete Blog Post

```tsx
// src/app/[lang]/blog/privacy-guide/page.tsx
import { BlogLayout } from '@/components/BlogLayout'
import type { Metadata } from 'next'
import type { Locale } from '@/dictionaries'

export async function generateMetadata({
  params
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  return {
    title: params.lang === 'en' ? 'Privacy Guide' : 'Guía de Privacidad',
    description: params.lang === 'en'
      ? 'How Whisper Cheap protects your privacy'
      : 'Cómo Whisper Cheap protege tu privacidad'
  }
}

export default function PrivacyGuide({ params }: { params: { lang: Locale } }) {
  const isEn = params.lang === 'en'

  return (
    <BlogLayout
      title={isEn ? 'Privacy Guide' : 'Guía de Privacidad'}
      date="2024-01-15"
      readingTime={isEn ? "7 min read" : "7 min de lectura"}
      lang={params.lang}
      author={{
        name: "Andrés Feding",
        role: isEn ? "Creator" : "Creador"
      }}
      relatedArticles={[
        {
          title: isEn ? "Getting Started" : "Empezando",
          slug: "getting-started",
          date: "2024-01-10",
          readingTime: isEn ? "5 min read" : "5 min de lectura"
        }
      ]}
    >
      <h2>{isEn ? "Your Privacy Matters" : "Tu Privacidad Importa"}</h2>
      <p>Content...</p>

      <h2>{isEn ? "How We Protect It" : "Cómo La Protegemos"}</h2>
      <p>Content...</p>

      <h3>{isEn ? "100% Local Processing" : "Procesamiento 100% Local"}</h3>
      <p>Content...</p>

      <h2>{isEn ? "What This Means" : "Qué Significa Esto"}</h2>
      <p>Conclusion...</p>
    </BlogLayout>
  )
}
```

## Troubleshooting

### Headings not appearing in TOC

- Ensure headings are h2 or h3 elements
- Add `id` attributes for better control
- Wrap content in the `children` prop

### TOC not sticking on mobile

- The sticky behavior is disabled on mobile by design
- Use `lg:` Tailwind breakpoint if you want to adjust

### Author image not showing

- Check the image path is correct and accessible
- Use public assets from `/public` directory
- Consider WebP format for better performance

### Date formatting issues

- Pass ISO 8601 format: `YYYY-MM-DD`
- Or any valid JavaScript Date string
- Component handles parsing automatically

## Best Practices

1. **Use semantic headings**: h2 for main sections, h3 for subsections
2. **Add IDs to headings**: Makes TOC more reliable
3. **Keep articles focused**: Long articles are harder to read
4. **Use lists**: Better for scannability
5. **Include code examples**: Helps developers
6. **Optimize images**: Compress before upload
7. **Link internally**: Cross-link related content
8. **Proofread**: Use spell-checker before publishing

## Files Modified

- `src/components/BlogLayout.tsx` - Main component
- `src/app/globals.css` - Prose styling added

## Integration

The component is production-ready and can be used immediately:

```bash
# No additional dependencies needed
# Component uses only React built-ins and Tailwind
```

All styling is self-contained in globals.css with the `.prose-article` class.
