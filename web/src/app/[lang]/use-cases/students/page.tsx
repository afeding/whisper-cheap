import type { Metadata } from 'next'
import type { Locale } from '@/dictionaries'
import { getDictionary } from '@/dictionaries'
import StudentsPageClient from './client'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const studentDict = dict?.students
  const baseUrl = 'https://whispercheap.com'

  return {
    title: studentDict?.meta?.title || 'Voice Typing for Students',
    description: studentDict?.meta?.description,
    keywords: studentDict?.meta?.keywords,
    authors: [{ name: 'Whisper Cheap' }],
    creator: 'Whisper Cheap',
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: `/${params.lang}/use-cases/students`,
      languages: {
        en: '/en/use-cases/students',
        es: '/es/use-cases/students',
        'x-default': '/en/use-cases/students',
      },
    },
    openGraph: {
      title: studentDict?.meta?.title,
      description: studentDict?.meta?.description,
      url: `${baseUrl}/${params.lang}/use-cases/students`,
      siteName: 'Whisper Cheap',
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
      type: 'website',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: 'Whisper Cheap - Voice Typing for Students',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: studentDict?.meta?.title,
      description: studentDict?.meta?.description,
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

export default async function StudentsPage({
  params,
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)
  const studentDict = dict?.students
  const baseUrl = 'https://whispercheap.com'

  const schemaArticle = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: studentDict?.meta?.title,
    description: studentDict?.meta?.description,
    image: '/og-image.png',
    author: {
      '@type': 'Organization',
      name: 'Whisper Cheap',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Whisper Cheap',
      logo: {
        '@type': 'ImageObject',
        url: '/logo.png',
      },
    },
    datePublished: new Date().toISOString(),
    url: `${baseUrl}/${params.lang}/use-cases/students`,
  }

  const schemaFAQ = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: studentDict?.faq?.items?.map((item: any) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.a,
      },
    })) || [],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(schemaArticle),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(schemaFAQ),
        }}
      />
      <StudentsPageClient params={params} dict={dict} />
    </>
  )
}
