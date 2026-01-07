import { getDictionary, type Locale } from '@/dictionaries'
import type { Metadata } from 'next'

const GITHUB_OWNER = 'afeding'
const GITHUB_REPO = 'whisper-cheap'
const DOWNLOAD_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest/download/WhisperCheapSetup.exe`
const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`

interface WisprFlowPageProps {
  params: { lang: Locale }
}

// Metadata generation for SEO
export async function generateMetadata({
  params,
}: WisprFlowPageProps): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const vsWispr = (dict as any).vs_wispr_flow

  return {
    title: vsWispr.meta.title,
    description: vsWispr.meta.description,
    keywords: vsWispr.meta.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/vs/wispr-flow`,
      languages: {
        en: '/en/vs/wispr-flow',
        es: '/es/vs/wispr-flow',
        'x-default': '/en/vs/wispr-flow',
      },
    },
    openGraph: {
      title: vsWispr.meta.title,
      description: vsWispr.meta.description,
      url: `${baseUrl}/${params.lang}/vs/wispr-flow`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Whisper Cheap - Wispr Flow Alternative',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: vsWispr.meta.title,
      description: vsWispr.meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
    },
  }
}

export default async function WisprFlowAlternativePage({
  params,
}: WisprFlowPageProps) {
  const dict = await getDictionary(params.lang)
  const vsWispr = (dict as any).vs_wispr_flow
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
              href={`/${otherLang}/vs/wispr-flow`}
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
              <SparklesIcon className="w-3.5 h-3.5" />
              {vsWispr.hero.badge}
            </span>

            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold leading-[0.95] tracking-tight mb-6">
              {vsWispr.hero.title}
            </h1>

            <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed mb-8">
              {vsWispr.hero.subtitle}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href={DOWNLOAD_URL}
                className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
              >
                <WindowsIcon className="w-5 h-5" />
                {vsWispr.cta.button}
                <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
              </a>
              <div className="text-text-dim text-sm">
                Free, forever. No catch.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12">
            {vsWispr.problem.title}
          </h2>

          <div className="space-y-8">
            {[
              { title: vsWispr.problem.issue1Title, desc: vsWispr.problem.issue1Desc },
              { title: vsWispr.problem.issue2Title, desc: vsWispr.problem.issue2Desc },
              { title: vsWispr.problem.issue3Title, desc: vsWispr.problem.issue3Desc },
            ].map((issue: any, i: number) => (
              <div key={i} className="flex gap-4">
                <div className="w-1 bg-accent rounded-full flex-shrink-0" />
                <div>
                  <h3 className="font-display font-semibold text-lg mb-2">{issue.title}</h3>
                  <p className="text-text-secondary leading-relaxed">{issue.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            {vsWispr.comparison.title}
          </h2>

          <div className="overflow-x-auto rounded-2xl border border-border-default">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-bg-secondary border-b border-border-default">
                  {vsWispr.comparison.headers.map((header: any, i: number) => (
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
                {vsWispr.comparison.rows.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-bg-elevated/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-text-primary">{row[0]}</td>
                    <td className="px-6 py-4 text-text-secondary">{row[1]}</td>
                    <td className={`px-6 py-4 ${row[0].includes('forever') || row[0].includes('Unlimited') || row[0].includes('100%') || row[0].includes('No') ? 'text-accent font-medium' : 'text-text-secondary'}`}>
                      {row[2]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Key Differences */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16">
            {vsWispr.differences.title}
          </h2>

          <div className="space-y-12">
            {[
              { title: vsWispr.differences.diff1Title, desc: vsWispr.differences.diff1Desc },
              { title: vsWispr.differences.diff2Title, desc: vsWispr.differences.diff2Desc },
              { title: vsWispr.differences.diff3Title, desc: vsWispr.differences.diff3Desc },
              { title: vsWispr.differences.diff4Title, desc: vsWispr.differences.diff4Desc },
            ].map((diff: any, i: number) => (
              <div key={i} className="p-6 rounded-xl bg-bg-card border-l-4 border-accent">
                <h3 className="font-display font-semibold text-lg mb-3">{diff.title}</h3>
                <p className="text-text-secondary leading-relaxed">{diff.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What Wispr Does Better (Honesty Section) */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-6">
            {vsWispr.wispr.title}
          </h2>
          <p className="text-text-secondary text-lg mb-12">
            {vsWispr.wispr.desc}
          </p>

          <ul className="space-y-4">
            {vsWispr.wispr.features.map((feature: any, i: number) => (
              <li key={i} className="flex items-start gap-4 p-4 rounded-lg bg-bg-card border border-border-default hover:border-border-hover transition-colors">
                <CheckIcon className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                <span className="text-text-secondary">{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Who Should Choose */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            {vsWispr.whoShouldChoose.title}
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            {vsWispr.whoShouldChoose.profiles.map((profile: any, i: number) => (
              <div
                key={i}
                className="p-6 rounded-2xl bg-bg-card border border-border-default hover:border-accent/50 transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                    <CheckIcon className="w-5 h-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-display font-semibold text-lg mb-2">
                      {profile.name}
                    </h3>
                    <p className="text-text-secondary leading-relaxed">{profile.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How to Switch */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16 text-center">
            {vsWispr.switch.title}
          </h2>

          <div className="space-y-8">
            {[
              { title: vsWispr.switch.step1Title, desc: vsWispr.switch.step1Desc },
              { title: vsWispr.switch.step2Title, desc: vsWispr.switch.step2Desc },
              { title: vsWispr.switch.step3Title, desc: vsWispr.switch.step3Desc },
              { title: vsWispr.switch.step4Title, desc: vsWispr.switch.step4Desc },
              { title: vsWispr.switch.step5Title, desc: vsWispr.switch.step5Desc },
            ].map((step: any, i: number) => (
              <div key={i} className="flex gap-5 items-start">
                <div className="w-10 h-10 rounded-full bg-accent text-bg-primary font-display font-bold flex items-center justify-center flex-shrink-0">
                  {i + 1}
                </div>
                <div className="pt-1 flex-1">
                  <h3 className="font-display font-semibold text-lg mb-1">{step.title}</h3>
                  <p className="text-text-secondary">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-2xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12 text-center">
            {vsWispr.faq.title}
          </h2>

          <div className="space-y-8">
            {[
              { q: vsWispr.faq.q1, a: vsWispr.faq.a1 },
              { q: vsWispr.faq.q2, a: vsWispr.faq.a2 },
              { q: vsWispr.faq.q3, a: vsWispr.faq.a3 },
              { q: vsWispr.faq.q4, a: vsWispr.faq.a4 },
              { q: vsWispr.faq.q5, a: vsWispr.faq.a5 },
              { q: vsWispr.faq.q6, a: vsWispr.faq.a6 },
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
      <section className="py-32 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-bold mb-6">
            {vsWispr.cta.title}
          </h2>
          <p className="text-text-secondary text-lg mb-8">
            {vsWispr.cta.subtitle}
          </p>
          <a
            href={DOWNLOAD_URL}
            className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
          >
            <WindowsIcon className="w-5 h-5" />
            {vsWispr.cta.button}
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
            headline: vsWispr.meta.title,
            description: vsWispr.meta.description,
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
                name: vsWispr.faq.q1,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a1 },
              },
              {
                '@type': 'Question',
                name: vsWispr.faq.q2,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a2 },
              },
              {
                '@type': 'Question',
                name: vsWispr.faq.q3,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a3 },
              },
              {
                '@type': 'Question',
                name: vsWispr.faq.q4,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a4 },
              },
              {
                '@type': 'Question',
                name: vsWispr.faq.q5,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a5 },
              },
              {
                '@type': 'Question',
                name: vsWispr.faq.q6,
                acceptedAnswer: { '@type': 'Answer', text: vsWispr.faq.a6 },
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

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 22.5l-.394-1.933a2.25 2.25 0 00-1.423-1.423L12.75 18.75l1.933-.394a2.25 2.25 0 001.423-1.423l.394-1.933.394 1.933a2.25 2.25 0 001.423 1.423l1.933.394-1.933.394a2.25 2.25 0 00-1.423 1.423z" />
    </svg>
  )
}
