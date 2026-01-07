import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { Breadcrumbs } from '@/components/Breadcrumbs'
import Link from 'next/link'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const isSpanish = params.lang === 'es'

  return {
    title: dict.blog?.voiceTypingTips?.meta?.title,
    description: dict.blog?.voiceTypingTips?.meta?.description,
    keywords: dict.blog?.voiceTypingTips?.meta?.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/blog/voice-typing-tips`,
      languages: {
        en: '/en/blog/voice-typing-tips',
        es: '/es/blog/voice-typing-tips',
        'x-default': '/en/blog/voice-typing-tips',
      },
    },
    openGraph: {
      title: dict.blog?.voiceTypingTips?.meta?.title,
      description: dict.blog?.voiceTypingTips?.meta?.description,
      url: `${baseUrl}/${params.lang}/blog/voice-typing-tips`,
      siteName: 'Whisper Cheap',
      locale: isSpanish ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: dict.blog?.voiceTypingTips?.meta?.title || 'Voice Typing Tips',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: dict.blog?.voiceTypingTips?.meta?.title,
      description: dict.blog?.voiceTypingTips?.meta?.description,
      images: ['/og-image.png'],
    },
  }
}

export default async function VoiceTypingTipsPage({
  params,
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)
  const content = dict.blog?.voiceTypingTips

  if (!content) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Content not available</p>
      </div>
    )
  }

  const isSpanish = params.lang === 'es'

  // Estimated reading time: ~15-18 minutes
  const readingTime = isSpanish ? '18 min de lectura' : '18 min read'

  // Schema.org Article + HowTo
  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: content.hero.title,
    description: content.meta.description,
    image: '/og-image.png',
    datePublished: '2025-01-03',
    author: {
      '@type': 'Organization',
      name: 'Whisper Cheap',
    },
  }

  const howToSchema = {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: content.hero.title,
    description: content.meta.description,
    image: '/og-image.png',
    step: ((content as any).tips || [])
      .slice(0, 5)
      .map((tip: any, idx: number) => ({
        '@type': 'HowToStep',
        position: idx + 1,
        name: tip.title,
        text: tip.description,
      })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(howToSchema) }}
      />

      {/* Hero */}
      <section className="bg-bg-primary text-text-primary py-16 px-4 md:py-24">
        <div className="max-w-3xl mx-auto">
          <Breadcrumbs lang={params.lang} items={[{ label: 'Blog', href: `/${params.lang}/blog` }, { label: content.hero.title }]} />
          <div className="inline-block bg-accent/10 text-accent px-3 py-1 rounded-full text-sm mb-4 border border-accent/20">
            {content.hero.badge}
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
            {content.hero.title}
          </h1>
          <p className="text-xl text-text-secondary mb-6">
            {content.hero.subtitle}
          </p>
          <div className="flex flex-col sm:flex-row items-center gap-4 text-text-secondary text-sm">
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.893 3.5a4.365 4.365 0 00-5.606 0l-.707.707.707-.707a4.365 4.365 0 000 6.172l.707.707-.707-.707a4.365 4.365 0 005.606 0l.707.707-.707-.707a4.365 4.365 0 000-6.172l-.707-.707.707.707zM12.6 9.55A3.365 3.365 0 008.05 5a3.365 3.365 0 104.55 4.55z" />
              </svg>
              {readingTime}
            </span>
            <span>•</span>
            <span>{content.hero.date}</span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-12">
        {/* Intro */}
        <section className="mb-12">
          <p className="text-lg text-text-secondary leading-relaxed mb-4">
            {content.intro.p1}
          </p>
          <p className="text-lg text-text-secondary leading-relaxed">
            {content.intro.p2}
          </p>
        </section>

        {/* Tips by Category */}
        {content.categories.map((category: any, categoryIdx: number) => (
          <section key={categoryIdx} className="mb-14">
            <h2 className="text-3xl font-bold mb-2 text-text-primary">
              {category.name}
            </h2>
            <p className="text-text-secondary mb-8">{category.description}</p>

            <div className="space-y-8">
              {category.tips.map((tip: any, tipIdx: number) => (
                <div
                  key={tipIdx}
                  className="bg-bg-card border border-border-default rounded-lg p-6 hover:border-border-hover transition-colors"
                >
                  {/* Tip Number & Title */}
                  <div className="flex items-start gap-4 mb-3">
                    <div className="bg-accent text-bg-primary font-bold text-lg rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-0.5">
                      {tip.number}
                    </div>
                    <h3 className="text-2xl font-bold text-text-primary leading-tight">
                      {tip.title}
                    </h3>
                  </div>

                  {/* Description */}
                  <p className="text-text-secondary leading-relaxed mb-4 ml-12">
                    {tip.description}
                  </p>

                  {/* Example/Pro Tip */}
                  <div className="bg-bg-secondary border-l-4 border-accent p-4 rounded-r ml-12">
                    <p className="text-sm font-semibold text-accent mb-2">
                      {(content as any)?.labels?.proTip || 'Pro Tip'}
                    </p>
                    <p className="text-text-secondary text-sm">
                      {tip.example}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}

        {/* Summary Checklist */}
        <section className="bg-bg-card border border-border-default rounded-lg p-8 my-14">
          <h2 className="text-2xl font-bold text-text-primary mb-6">
            {(content as any)?.checklist?.title || 'Quick Checklist'}
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {((content as any)?.checklist?.items || []).map((item: any, idx: number) => (
              <label
                key={idx}
                className="flex items-center gap-3 cursor-pointer group"
              >
                <input
                  type="checkbox"
                  className="w-5 h-5 rounded border-border-default accent-accent cursor-pointer"
                  defaultChecked={false}
                />
                <span className="text-text-secondary group-hover:text-text-primary transition-colors">
                  {item}
                </span>
              </label>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-14">
          <h2 className="text-3xl font-bold mb-8 text-text-primary">
            {(content as any)?.faq?.title || 'Frequently Asked Questions'}
          </h2>
          <div className="space-y-4">
            {((content as any)?.faq?.items || []).map((faq: any, idx: number) => (
              <details
                key={idx}
                className="group bg-bg-card border border-border-default rounded-lg p-4 hover:border-border-hover transition-colors"
              >
                <summary className="cursor-pointer flex items-center justify-between font-semibold text-text-primary">
                  <span>{faq.q}</span>
                  <svg
                    className="w-5 h-5 transition-transform group-open:rotate-180"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </summary>
                <p className="text-text-secondary mt-4">{faq.a}</p>
              </details>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="bg-accent/10 border border-accent/20 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-text-primary mb-3">
            {(content as any)?.cta?.title || 'Start Dictating Today'}
          </h2>
          <p className="text-text-secondary mb-6">
            {(content as any)?.cta?.description || 'Download Whisper Cheap and experience the future of voice typing.'}
          </p>
          <Link
            href={`/${params.lang}`}
            className="inline-block bg-accent text-bg-primary font-semibold px-8 py-3 rounded-lg hover:bg-accent/90 transition-colors"
          >
            {(content as any)?.cta?.button || 'Download'}
          </Link>
        </section>

        {/* Back to Blog Link */}
        <div className="mt-12 pt-8 border-t border-border-default">
          <Link
            href={`/${params.lang}`}
            className="text-accent hover:text-accent/80 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            {(content as any)?.labels?.backHome || 'Back to Home'}
          </Link>
        </div>
      </main>
    </>
  )
}
