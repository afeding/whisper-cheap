import { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { DevelopersPage } from '@/components/DevelopersPage'

interface Props {
  params: { lang: Locale }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const meta = (dict as any).developers.meta
  const baseUrl = 'https://whispercheap.com'
  const canonicalUrl = `${baseUrl}/${params.lang}/use-cases/developers`

  return {
    title: meta.title,
    description: meta.description,
    keywords: meta.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: canonicalUrl,
      languages: {
        en: `${baseUrl}/en/use-cases/developers`,
        es: `${baseUrl}/es/use-cases/developers`,
        'x-default': `${baseUrl}/en/use-cases/developers`,
      },
    },
    openGraph: {
      title: meta.title,
      description: meta.description,
      url: canonicalUrl,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      authors: ['Whisper Cheap'],
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Voice Dictation for Developers - Whisper Cheap',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: meta.title,
      description: meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
  }
}

export default async function DevelopersUseCasePage({ params }: Props) {
  const dict = await getDictionary(params.lang)

  return (
    <>
      <DevelopersPage dict={(dict as any).developers} lang={params.lang} />

      {/* Schema.org Article + FAQPage */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: (dict as any).developers.meta.title,
            description: (dict as any).developers.meta.description,
            author: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
              url: 'https://whispercheap.com',
            },
            publisher: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
              logo: {
                '@type': 'ImageObject',
                url: 'https://whispercheap.com/logo.png',
              },
            },
            datePublished: '2025-01-03',
            dateModified: new Date().toISOString().split('T')[0],
            image: 'https://whispercheap.com/og-image.png',
            inLanguage: params.lang,
          }),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: (dict as any).developers.faq.items.map((item: any) => ({
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
    </>
  )
}
