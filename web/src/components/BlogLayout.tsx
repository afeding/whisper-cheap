'use client'

import { type ReactNode, useMemo, useEffect, useState } from 'react'
import type { Locale } from '@/dictionaries'

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

/**
 * BlogLayout - Reusable component for blog article pages
 *
 * Provides:
 * - Navigation bar (fixed)
 * - Breadcrumb navigation
 * - Article header with metadata
 * - Prose-optimized content area
 * - Optional sidebar with TOC (sticky on scroll)
 * - Related articles section
 * - Footer
 * - Full a11y + SEO semantics
 */
export function BlogLayout({
  title,
  date,
  readingTime,
  lang,
  children,
  breadcrumbs,
  author,
  relatedArticles,
  tableOfContents: providedToc,
}: BlogLayoutProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'
  const defaultBreadcrumbs = useMemo(
    () =>
      breadcrumbs || [
        { label: lang === 'en' ? 'Home' : 'Inicio', href: `/${lang}` },
        { label: lang === 'en' ? 'Blog' : 'Blog', href: `/${lang}/blog` },
      ],
    [lang, breadcrumbs]
  )

  // Auto-generate TOC from headings if not provided
  const [toc, setToc] = useState(providedToc || [])
  const [activeHeading, setActiveHeading] = useState<string | null>(null)

  useEffect(() => {
    if (providedToc) {
      setToc(providedToc)
      return
    }

    // Auto-generate TOC from h2/h3 headings
    const headings = Array.from(document.querySelectorAll('article h2, article h3')).map((el) => {
      const id = el.id || el.textContent?.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '') || ''
      if (!el.id) el.id = id
      const level = el.tagName === 'H2' ? 2 : 3
      return {
        id,
        label: el.textContent || '',
        level,
      }
    })
    setToc(headings)
  }, [providedToc])

  // Track active heading on scroll
  useEffect(() => {
    const handleScroll = () => {
      const headingElements = toc
        .map(({ id }) => ({ id, el: document.getElementById(id) }))
        .filter(({ el }) => el !== null)

      for (const { id, el } of headingElements) {
        const rect = el!.getBoundingClientRect()
        if (rect.top >= 0 && rect.top <= 150) {
          setActiveHeading(id)
          break
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [toc])

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary bg-noise">
      {/* Decorative gradient */}
      <div className="fixed inset-0 bg-gradient-radial pointer-events-none" />

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href={`/${lang}`} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
              <MicIcon className="w-4 h-4 text-accent" />
            </div>
            <span className="font-display font-semibold text-lg tracking-tight">Whisper Cheap</span>
          </a>

          <div className="flex items-center gap-2">
            <a
              href={`https://github.com/afeding/whisper-cheap`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2.5 rounded-lg text-text-dim hover:text-text-secondary hover:bg-bg-elevated transition-all"
              aria-label="GitHub"
            >
              <GitHubIcon className="w-5 h-5" />
            </a>

            <a
              href={`/${otherLang}`}
              className="p-2.5 rounded-lg text-text-dim hover:text-text-secondary hover:bg-bg-elevated transition-all flex items-center gap-1.5"
              aria-label={`Switch to ${otherLang === 'en' ? 'English' : 'Spanish'}`}
            >
              <GlobeIcon className="w-5 h-5" />
              <span className="text-xs font-medium uppercase">{otherLang}</span>
            </a>

            <a
              href={`https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe`}
              className="ml-2 btn-glow inline-flex items-center gap-2 bg-accent text-bg-primary font-semibold px-5 py-2.5 rounded-full hover:bg-accent-hover transition-all text-sm"
            >
              <DownloadIcon className="w-4 h-4" />
              {lang === 'en' ? 'Download' : 'Descargar'}
            </a>
          </div>
        </div>
      </nav>

      {/* Main content wrapper */}
      <main className="relative pt-24 pb-24 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Article header section */}
          <div className="max-w-3xl mb-16">
            {/* Breadcrumbs */}
            <nav
              className="flex items-center gap-2 text-sm mb-6 flex-wrap"
              aria-label="Breadcrumb"
            >
              {defaultBreadcrumbs.map((crumb, idx) => (
                <div key={crumb.href} className="flex items-center gap-2">
                  <a
                    href={crumb.href}
                    className="text-text-dim hover:text-accent transition-colors link-underline"
                  >
                    {crumb.label}
                  </a>
                  {idx < defaultBreadcrumbs.length - 1 && (
                    <span className="text-border-default">/</span>
                  )}
                </div>
              ))}
            </nav>

            {/* Article title */}
            <h1 className="font-display text-5xl sm:text-6xl font-bold leading-tight tracking-tight mb-6 text-text-primary">
              {title}
            </h1>

            {/* Meta information */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 mb-8">
              <div className="flex items-center gap-3">
                <time dateTime={date} className="text-text-secondary">
                  {formatDate(date, lang)}
                </time>
              </div>

              <div className="hidden sm:block w-px h-4 bg-border-default" />

              <div className="flex items-center gap-3">
                <ClockIcon className="w-4 h-4 text-accent" />
                <span className="text-text-secondary">{readingTime}</span>
              </div>

              {author && (
                <>
                  <div className="hidden sm:block w-px h-4 bg-border-default" />
                  <div className="flex items-center gap-2">
                    {author.image && (
                      <img
                        src={author.image}
                        alt={author.name}
                        className="w-6 h-6 rounded-full"
                      />
                    )}
                    <span className="text-text-secondary">{author.name}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Content grid: article + sidebar */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 lg:gap-16">
            {/* Article content */}
            <article className="lg:col-span-2 prose-article min-w-0">
              {children}
            </article>

            {/* Sidebar */}
            <aside className="lg:col-span-1">
              {/* Table of Contents */}
              {toc.length > 0 && (
                <div className="sticky top-24 mb-12 p-6 bg-bg-card rounded-2xl border border-border-default">
                  <h2 className="font-display font-semibold text-sm mb-4 text-text-primary uppercase tracking-wide">
                    {lang === 'en' ? 'On this page' : 'En esta página'}
                  </h2>
                  <nav className="space-y-2">
                    {toc.map(({ id, label, level }) => (
                      <a
                        key={id}
                        href={`#${id}`}
                        className={`block px-2 py-1 rounded text-sm transition-all duration-200 ${
                          activeHeading === id
                            ? 'text-accent font-semibold bg-accent/10'
                            : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated'
                        } ${level === 3 ? 'ml-2' : ''}`}
                      >
                        {label}
                      </a>
                    ))}
                  </nav>
                </div>
              )}

              {/* Related Articles */}
              {relatedArticles && relatedArticles.length > 0 && (
                <div className="p-6 bg-bg-card rounded-2xl border border-border-default">
                  <h2 className="font-display font-semibold text-sm mb-4 text-text-primary uppercase tracking-wide">
                    {lang === 'en' ? 'Related Articles' : 'Artículos Relacionados'}
                  </h2>
                  <div className="space-y-4">
                    {relatedArticles.map(({ title: articleTitle, slug, date: articleDate, readingTime: articleReadingTime }) => (
                      <a
                        key={slug}
                        href={`/${lang}/blog/${slug}`}
                        className="group block p-3 rounded-lg border border-border-default/50 hover:border-accent/50 hover:bg-bg-elevated transition-all duration-200"
                      >
                        <h3 className="text-sm font-semibold text-text-primary group-hover:text-accent transition-colors mb-2 line-clamp-2">
                          {articleTitle}
                        </h3>
                        <div className="text-xs text-text-dim flex gap-2">
                          <span>{formatDate(articleDate, lang)}</span>
                          <span className="text-border-default">•</span>
                          <span>{articleReadingTime}</span>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </aside>
          </div>

          {/* Call-to-action section */}
          <div className="mt-24 pt-12 border-t border-border-default max-w-3xl">
            <div className="text-center py-12">
              <h2 className="font-display text-3xl font-bold mb-4 text-text-primary">
                {lang === 'en'
                  ? 'Ready to type less?'
                  : 'Listo para escribir menos?'}
              </h2>
              <p className="text-text-secondary mb-8 max-w-lg mx-auto">
                {lang === 'en'
                  ? 'Download Whisper Cheap and start dictating. 100% free, forever.'
                  : 'Descarga Whisper Cheap y empieza a dictar. 100% gratis, siempre.'}
              </p>
              <a
                href={`https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe`}
                className="btn-glow inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all"
              >
                <WindowsIcon className="w-5 h-5" />
                {lang === 'en' ? 'Download' : 'Descargar'}
              </a>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-border-default">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5 text-text-dim">
            <MicIcon className="w-4 h-4 text-accent" />
            <span className="text-sm">
              {lang === 'en' ? 'For those who hate typing' : 'Para los que odian teclear'}
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a
              href={`https://github.com/afeding/whisper-cheap`}
              className="text-text-dim hover:text-text-secondary transition-colors link-underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              href={`https://github.com/afeding/whisper-cheap/releases`}
              className="text-text-dim hover:text-text-secondary transition-colors link-underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {lang === 'en' ? 'Releases' : 'Versiones'}
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}

/**
 * Format date to locale-specific string
 */
function formatDate(dateStr: string, locale: Locale): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString(locale === 'es' ? 'es-ES' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

// Icons
function MicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
    </svg>
  )
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
    </svg>
  )
}

function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 003 12c0-1.605.42-3.113 1.157-4.418" />
    </svg>
  )
}

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  )
}

function WindowsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" />
    </svg>
  )
}

function ClockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}
