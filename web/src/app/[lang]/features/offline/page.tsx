import { getDictionary, type Locale } from '@/dictionaries'
import type { Metadata } from 'next'

const GITHUB_OWNER = 'afeding'
const GITHUB_REPO = 'whisper-cheap'
const DOWNLOAD_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest/download/WhisperCheapSetup.exe`
const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`

interface OfflinePageProps {
  params: { lang: Locale }
}

// Metadata generation for SEO
export async function generateMetadata({
  params,
}: OfflinePageProps): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const featuresOffline = (dict as any).features_offline

  return {
    title: featuresOffline.meta.title,
    description: featuresOffline.meta.description,
    keywords: featuresOffline.meta.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/features/offline`,
      languages: {
        en: '/en/features/offline',
        es: '/es/features/offline',
        'x-default': '/en/features/offline',
      },
    },
    openGraph: {
      title: featuresOffline.meta.title,
      description: featuresOffline.meta.description,
      url: `${baseUrl}/${params.lang}/features/offline`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Whisper Cheap - Offline AI Transcription',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: featuresOffline.meta.title,
      description: featuresOffline.meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
    },
  }
}

export default async function OfflinePage({
  params,
}: OfflinePageProps) {
  const dict = await getDictionary(params.lang)
  const featuresOffline = (dict as any).features_offline
  const otherLang = params.lang === 'en' ? 'es' : 'en'

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary bg-noise">
      {/* Gradient decoration */}
      <div className="fixed inset-0 bg-gradient-radial pointer-events-none" />

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href={`/${params.lang}`} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
              <MicIcon className="w-4 h-4 text-accent" />
            </div>
            <span className="font-display font-semibold text-lg tracking-tight">Whisper Cheap</span>
          </a>

          <div className="flex items-center gap-2">
            <a
              href={`/${otherLang}/features/offline`}
              className="p-2.5 rounded-lg text-text-dim hover:text-text-secondary hover:bg-bg-elevated transition-all flex items-center gap-1.5"
              aria-label={`Switch to ${otherLang === 'en' ? 'English' : 'Spanish'}`}
            >
              <GlobeIcon className="w-5 h-5" />
              <span className="text-xs font-medium uppercase">{otherLang}</span>
            </a>

            <a
              href={DOWNLOAD_URL}
              className="ml-2 btn-glow inline-flex items-center gap-2 bg-accent text-bg-primary font-semibold px-5 py-2.5 rounded-full hover:bg-accent-hover transition-all text-sm"
            >
              <DownloadIcon className="w-4 h-4" />
              {dict.nav.download}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-24 pb-12 px-6 overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="relative max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-flex items-center gap-2 text-accent text-sm font-medium px-4 py-1.5 rounded-full mb-6 bg-accent/10 badge-glow">
              <ShieldIcon className="w-3.5 h-3.5" />
              {featuresOffline.hero.badge}
            </span>

            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold leading-[0.95] tracking-tight mb-6">
              {featuresOffline.hero.title}
            </h1>

            <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed mb-8">
              {featuresOffline.hero.subtitle}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href={DOWNLOAD_URL}
                className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
              >
                <WindowsIcon className="w-5 h-5" />
                {featuresOffline.cta.button}
                <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
              </a>
              <div className="text-text-dim text-sm">
                {featuresOffline.hero.note}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Offline Matters */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16 text-center">
            {featuresOffline.why.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <LockIcon />,
                title: featuresOffline.why.privacy.title,
                desc: featuresOffline.why.privacy.desc,
              },
              {
                icon: <ServerIcon />,
                title: featuresOffline.why.reliability.title,
                desc: featuresOffline.why.reliability.desc,
              },
              {
                icon: <ZapIcon />,
                title: featuresOffline.why.speed.title,
                desc: featuresOffline.why.speed.desc,
              },
            ].map((item: any, i: number) => (
              <div
                key={i}
                className="p-8 rounded-2xl bg-bg-card border border-border-default hover:border-accent/30 transition-all group"
              >
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-6 group-hover:bg-accent/20 transition-colors">
                  <div className="w-6 h-6 text-accent">{item.icon}</div>
                </div>
                <h3 className="font-display font-semibold text-lg mb-3">{item.title}</h3>
                <p className="text-text-secondary leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-8 text-center">
            {featuresOffline.howWorks.title}
          </h2>
          <p className="text-text-secondary text-lg text-center mb-12">
            {featuresOffline.howWorks.subtitle}
          </p>

          <div className="space-y-6">
            {[
              {
                title: featuresOffline.howWorks.step1Title,
                desc: featuresOffline.howWorks.step1Desc,
              },
              {
                title: featuresOffline.howWorks.step2Title,
                desc: featuresOffline.howWorks.step2Desc,
              },
              {
                title: featuresOffline.howWorks.step3Title,
                desc: featuresOffline.howWorks.step3Desc,
              },
            ].map((step: any, i: number) => (
              <div key={i} className="flex gap-5 items-start p-6 rounded-xl bg-bg-card border border-border-default hover:border-accent/30 transition-colors">
                <div className="w-10 h-10 rounded-full bg-accent/10 text-accent font-display font-bold flex items-center justify-center flex-shrink-0">
                  {i + 1}
                </div>
                <div className="pt-1 flex-1">
                  <h3 className="font-display font-semibold text-lg mb-1">{step.title}</h3>
                  <p className="text-text-secondary">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 p-6 rounded-xl bg-accent/5 border border-accent/20">
            <p className="text-text-secondary text-sm leading-relaxed">
              <span className="font-semibold text-accent">Size:</span> {featuresOffline.howWorks.size}
            </p>
          </div>
        </div>
      </section>

      {/* Online vs Offline Comparison */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            {featuresOffline.comparison.title}
          </h2>

          <div className="overflow-x-auto rounded-2xl border border-border-default">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-bg-secondary border-b border-border-default">
                  {featuresOffline.comparison.headers.map((header: string, i: number) => (
                    <th
                      key={i}
                      className={`px-6 py-4 text-left font-semibold ${
                        i === 0
                          ? 'text-text-primary'
                          : i === 2
                            ? 'text-accent'
                            : 'text-text-secondary'
                      }`}
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border-default">
                {featuresOffline.comparison.rows.map((row: string[], i: number) => (
                  <tr key={i} className="hover:bg-bg-elevated/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-text-primary">{row[0]}</td>
                    <td className="px-6 py-4 text-text-secondary">{row[1]}</td>
                    <td
                      className={`px-6 py-4 ${
                        row[2].includes('✓') || row[2].includes('Always') || row[2].includes('Instant')
                          ? 'text-accent font-medium'
                          : 'text-text-secondary'
                      }`}
                    >
                      {row[2]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16 text-center">
            {featuresOffline.useCases.title}
          </h2>

          <div className="space-y-4">
            {featuresOffline.useCases.cases.map((useCase: string, i: number) => (
              <div key={i} className="flex gap-4 p-5 rounded-lg bg-bg-card border border-border-default hover:border-accent/30 transition-colors">
                <div className="w-6 h-6 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CheckIcon className="w-4 h-4 text-accent" />
                </div>
                <p className="text-text-secondary leading-relaxed">{useCase}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Details */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12 text-center">
            {featuresOffline.technical.title}
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: featuresOffline.technical.architecture.title,
                desc: featuresOffline.technical.architecture.desc,
              },
              {
                title: featuresOffline.technical.model.title,
                desc: featuresOffline.technical.model.desc,
              },
              {
                title: featuresOffline.technical.latency.title,
                desc: featuresOffline.technical.latency.desc,
              },
              {
                title: featuresOffline.technical.disk.title,
                desc: featuresOffline.technical.disk.desc,
              },
            ].map((item: any, i: number) => (
              <div key={i} className="p-6 rounded-xl bg-bg-card border border-border-default">
                <h3 className="font-display font-semibold text-lg mb-2 text-accent">
                  {item.title}
                </h3>
                <p className="text-text-secondary text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12 text-center">
            {featuresOffline.faq.title}
          </h2>

          <div className="space-y-8">
            {[
              { q: featuresOffline.faq.q1, a: featuresOffline.faq.a1 },
              { q: featuresOffline.faq.q2, a: featuresOffline.faq.a2 },
              { q: featuresOffline.faq.q3, a: featuresOffline.faq.a3 },
              { q: featuresOffline.faq.q4, a: featuresOffline.faq.a4 },
              { q: featuresOffline.faq.q5, a: featuresOffline.faq.a5 },
            ].map((item: any, i: number) => (
              <div key={i} className="border-b border-border-default pb-6 last:border-0">
                <h3 className="font-display font-semibold text-lg mb-2">{item.q}</h3>
                <p className="text-text-secondary leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-6 bg-bg-secondary">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-bold mb-6">
            {featuresOffline.cta.title}
          </h2>
          <p className="text-text-secondary text-lg mb-8">
            {featuresOffline.cta.subtitle}
          </p>
          <a
            href={DOWNLOAD_URL}
            className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
          >
            <WindowsIcon className="w-5 h-5" />
            {featuresOffline.cta.button}
            <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-border-default">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5 text-text-dim">
            <MicIcon className="w-4 h-4 text-accent" />
            <span className="text-sm">{dict.footer.tagline}</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a
              href={GITHUB_URL}
              className="text-text-dim hover:text-text-secondary transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {dict.footer.github}
            </a>
            <a
              href={`/${params.lang}`}
              className="text-text-dim hover:text-text-secondary transition-colors"
            >
              Home
            </a>
          </div>
        </div>
      </footer>

      {/* Schema.org structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: featuresOffline.meta.title,
            description: featuresOffline.meta.description,
            author: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
            },
            datePublished: '2025-01-03',
            dateModified: '2025-01-03',
          }),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: [
              {
                '@type': 'Question',
                name: featuresOffline.faq.q1,
                acceptedAnswer: { '@type': 'Answer', text: featuresOffline.faq.a1 },
              },
              {
                '@type': 'Question',
                name: featuresOffline.faq.q2,
                acceptedAnswer: { '@type': 'Answer', text: featuresOffline.faq.a2 },
              },
              {
                '@type': 'Question',
                name: featuresOffline.faq.q3,
                acceptedAnswer: { '@type': 'Answer', text: featuresOffline.faq.a3 },
              },
              {
                '@type': 'Question',
                name: featuresOffline.faq.q4,
                acceptedAnswer: { '@type': 'Answer', text: featuresOffline.faq.a4 },
              },
              {
                '@type': 'Question',
                name: featuresOffline.faq.q5,
                acceptedAnswer: { '@type': 'Answer', text: featuresOffline.faq.a5 },
              },
            ],
          }),
        }}
      />
    </div>
  )
}

// ICONS
function MicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
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

function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
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

function ArrowDownIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  )
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
    </svg>
  )
}

function LockIcon() {
  return (
    <svg fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 1L9 4H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-4l-3-3z" />
      <path d="M12 4c3.31 0 6 2.69 6 6v3h3c1.1 0 2 .9 2 2v8c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2v-8c0-1.1.9-2 2-2h3V8c0-3.31 2.69-6 6-6zm0 2c2.21 0 4 1.79 4 4v3H8V8c0-2.21 1.79-4 4-4z" />
    </svg>
  )
}

function ServerIcon() {
  return (
    <svg fill="currentColor" viewBox="0 0 24 24">
      <path d="M20 13H4c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h16c.55 0 1-.45 1-1v-6c0-.55-.45-1-1-1zM7 19c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM20 3H4c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h16c.55 0 1-.45 1-1V4c0-.55-.45-1-1-1zm-3 8h-2V5h2v6z" />
    </svg>
  )
}

function ZapIcon() {
  return (
    <svg fill="currentColor" viewBox="0 0 24 24">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
    </svg>
  )
}
