import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { WritersPage } from '@/components/WritersPage'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const writersData = (dict as any).writers as any

  return {
    title: writersData.meta.title,
    description: writersData.meta.description,
    keywords: 'AI dictation for writers, voice typing for writers, dictation software for authors, write by voice, free dictation software, voice to text for creative writing',
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/use-cases/writers`,
      languages: {
        en: '/en/use-cases/writers',
        es: '/es/use-cases/writers',
        'x-default': '/en/use-cases/writers',
      },
    },
    openGraph: {
      title: writersData.meta.title,
      description: writersData.meta.description,
      url: `${baseUrl}/${params.lang}/use-cases/writers`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'AI Dictation for Writers',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: writersData.meta.title,
      description: writersData.meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
    },
  }
}

export default async function WritersCaseStudyPage({
  params,
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)
  const writersData = (dict as any).writers as any

  return (
    <>
      <WritersPage dict={writersData} lang={params.lang} />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: writersData.meta.title,
            description: writersData.meta.description,
            author: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
            },
            datePublished: '2025-01-03',
            dateModified: '2025-01-03',
            image: '/og-image.png',
            url: `https://whispercheap.com/${params.lang}/use-cases/writers`,
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
                name: writersData.faqWriters.q1,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a1,
                },
              },
              {
                '@type': 'Question',
                name: writersData.faqWriters.q2,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a2,
                },
              },
              {
                '@type': 'Question',
                name: writersData.faqWriters.q3,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a3,
                },
              },
              {
                '@type': 'Question',
                name: writersData.faqWriters.q4,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a4,
                },
              },
              {
                '@type': 'Question',
                name: writersData.faqWriters.q5,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a5,
                },
              },
              {
                '@type': 'Question',
                name: writersData.faqWriters.q6,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: writersData.faqWriters.a6,
                },
              },
            ],
          }),
        }}
      />
    </>
  )
}
