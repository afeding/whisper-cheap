import { getDictionary, type Locale } from '@/dictionaries'
import type { Metadata } from 'next'
import {
  MicIcon,
  GlobeIcon,
  DownloadIcon,
  ArrowDownIcon,
  Monitor,
  CheckIcon,
} from 'lucide-react'

const GITHUB_OWNER = 'afeding'
const GITHUB_REPO = 'whisper-cheap'
const DOWNLOAD_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest/download/WhisperCheapSetup.exe`
const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`

interface PrivacyPageProps {
  params: { lang: Locale }
}

export async function generateMetadata({
  params,
}: PrivacyPageProps): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const privacy = dict.privacy

  return {
    title: privacy.meta.title,
    description: privacy.meta.description,
    keywords: privacy.meta.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/features/privacy`,
      languages: {
        en: '/en/features/privacy',
        es: '/es/features/privacy',
        'x-default': '/en/features/privacy',
      },
    },
    openGraph: {
      title: privacy.meta.title,
      description: privacy.meta.description,
      url: `${baseUrl}/${params.lang}/features/privacy`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Whisper Cheap - Private Speech-to-Text',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: privacy.meta.title,
      description: privacy.meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
    },
  }
}

export default async function PrivacyPage({
  params,
}: PrivacyPageProps) {
  const dict = await getDictionary(params.lang)
  const privacy = dict.privacy
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
              href={`/${otherLang}/features/privacy`}
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
              {privacy.hero.cta}
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
              <MicIcon className="w-3.5 h-3.5" />
              {privacy.hero.eyebrow}
            </span>

            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold leading-[0.95] tracking-tight mb-6">
              {privacy.hero.title}
            </h1>

            <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed mb-8">
              {privacy.hero.subtitle}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href={DOWNLOAD_URL}
                className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
              >
                <Monitor className="w-5 h-5" />
                {privacy.hero.cta}
                <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
              </a>
              <div className="text-text-dim text-sm">
                {params.lang === 'en' ? 'Free, forever. No catch.' : 'Gratis, para siempre. Sin trampa.'}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12">
            {privacy.problem.title}
          </h2>

          <div className="space-y-8">
            {[
              privacy.problem.reason1,
              privacy.problem.reason2,
              privacy.problem.reason3,
              privacy.problem.reason4,
            ].map((reason: any, i: number) => (
              <div key={i} className="flex gap-4">
                <div className="w-1 bg-accent rounded-full flex-shrink-0" />
                <p className="text-text-secondary leading-relaxed">{reason}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 p-6 sm:p-8 bg-bg-card rounded-2xl border border-accent/20">
            <p className="text-text-primary font-semibold">{privacy.problem.conclusion}</p>
          </div>
        </div>
      </section>

      {/* How Whisper Cheap Protects Privacy */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            {privacy.how_protects.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              privacy.how_protects.local,
              privacy.how_protects.no_account,
              privacy.how_protects.open_source,
            ].map((item: any, i: number) => (
              <div
                key={i}
                className="p-6 rounded-2xl bg-bg-secondary border border-border-default hover:border-accent/50 transition-all"
              >
                <h3 className="font-display font-semibold text-xl mb-3 text-accent">
                  {item.heading}
                </h3>
                <p className="text-text-secondary leading-relaxed">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-4">
            {privacy.use_cases.title}
          </h2>
          <p className="text-text-secondary text-lg text-center mb-16 max-w-2xl mx-auto">
            {privacy.use_cases.intro}
          </p>

          <div className="grid sm:grid-cols-2 gap-8">
            {privacy.use_cases.cases.map((useCase: any, i: number) => (
              <div key={i} className="p-6 rounded-xl bg-bg-card border border-border-default hover:border-accent/50 transition-all">
                <h3 className="font-display font-semibold text-lg mb-2 text-accent">
                  {useCase.title}
                </h3>
                <p className="text-text-secondary leading-relaxed">{useCase.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy Comparison Table */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center mb-16">
            {privacy.comparison.title}
          </h2>

          <div className="overflow-x-auto rounded-2xl border border-border-default">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-bg-secondary border-b border-border-default">
                  <th className="px-6 py-4 text-left font-semibold text-text-secondary">
                    {privacy.comparison.headers[0]}
                  </th>
                  <th className="px-6 py-4 text-left font-semibold text-accent">
                    {privacy.comparison.headers[1]}
                  </th>
                  <th className="px-6 py-4 text-left font-semibold text-text-secondary">
                    {privacy.comparison.headers[2]}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-default">
                {privacy.comparison.rows.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-bg-elevated/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-text-primary">
                      {row[0]}
                    </td>
                    <td className="px-6 py-4 text-accent font-medium">{row[1]}</td>
                    <td className="px-6 py-4 text-text-secondary">{row[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-2xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12 text-center">
            {privacy.faq.title}
          </h2>

          <div className="space-y-8">
            {privacy.faq.items.map((item: any, i: number) => (
              <div key={i} className="border-b border-border-default pb-8 last:border-0">
                <h3 className="font-display font-semibold text-lg mb-3 text-text-primary">
                  {item.q}
                </h3>
                <p className="text-text-secondary leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-6">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-bold mb-4">
            {privacy.cta.title}
          </h2>
          <p className="text-text-secondary text-lg mb-8">
            {privacy.cta.subtitle}
          </p>
          <a
            href={DOWNLOAD_URL}
            className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
          >
            <Monitor className="w-5 h-5" />
            {privacy.cta.button}
            <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-border-default">
        <div className="max-w-6xl mx-auto text-center text-text-dim text-sm">
          <p>Whisper Cheap - Free local speech-to-text for Windows</p>
          <div className="mt-4 flex items-center justify-center gap-6">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-text-secondary transition-colors"
            >
              GitHub
            </a>
            <a
              href={`/${otherLang}/features/privacy`}
              className="hover:text-text-secondary transition-colors"
            >
              {otherLang === 'en' ? 'English' : 'Español'}
            </a>
          </div>
        </div>
      </footer>

      {/* Schema Markup - Article */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: privacy.meta.title,
            description: privacy.meta.description,
            author: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
            },
            datePublished: '2025-01-03',
            dateModified: '2025-01-03',
            publisher: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
              logo: {
                '@type': 'ImageObject',
                url: 'https://whispercheap.com/icon.svg',
              },
            },
          }),
        }}
      />

      {/* Schema Markup - FAQ */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: privacy.faq.items.map((item: any) => ({
              '@type': 'Question',
              name: item.q,
              acceptedAnswer: {
                '@type': 'Answer',
                text: item.a,
              },
            })),
          }),
        }}
      />
    </div>
  )
}
