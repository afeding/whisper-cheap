import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { LawyersPage } from '@/components/LawyersPage'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const lawyersData = (dict as any).lawyers as any

  return {
    title: lawyersData.meta.title,
    description: lawyersData.meta.description,
    keywords: lawyersData.meta.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/use-cases/lawyers`,
      languages: {
        en: '/en/use-cases/lawyers',
        es: '/es/use-cases/lawyers',
        'x-default': '/en/use-cases/lawyers',
      },
    },
    openGraph: {
      title: lawyersData.meta.title,
      description: lawyersData.meta.description,
      url: `${baseUrl}/${params.lang}/use-cases/lawyers`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'article',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Free Legal Dictation Software for Lawyers',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: lawyersData.meta.title,
      description: lawyersData.meta.description,
      images: ['/og-image.png'],
    },
    robots: {
      index: true,
      follow: true,
    },
  }
}

export default async function LawyersCaseStudyPage({
  params,
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)
  const lawyersData = (dict as any).lawyers as any

  return (
    <>
      <LawyersPage dict={lawyersData} lang={params.lang} />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: lawyersData.meta.title,
            description: lawyersData.meta.description,
            author: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
            },
            datePublished: '2025-01-03',
            dateModified: '2025-01-03',
            image: '/og-image.png',
            url: `https://whispercheap.com/${params.lang}/use-cases/lawyers`,
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
                name: lawyersData.faqLawyers.q1,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a1,
                },
              },
              {
                '@type': 'Question',
                name: lawyersData.faqLawyers.q2,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a2,
                },
              },
              {
                '@type': 'Question',
                name: lawyersData.faqLawyers.q3,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a3,
                },
              },
              {
                '@type': 'Question',
                name: lawyersData.faqLawyers.q4,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a4,
                },
              },
              {
                '@type': 'Question',
                name: lawyersData.faqLawyers.q5,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a5,
                },
              },
              {
                '@type': 'Question',
                name: lawyersData.faqLawyers.q6,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: lawyersData.faqLawyers.a6,
                },
              },
            ],
          }),
        }}
      />
    </>
  )
}
