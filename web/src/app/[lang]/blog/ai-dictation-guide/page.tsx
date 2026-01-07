import type { Metadata } from 'next'
import Link from 'next/link'
import { Breadcrumbs } from '@/components/Breadcrumbs'
import { getDictionary } from '@/dictionaries'
import { AIDictationGuideClient } from './client'

export async function generateMetadata({
  params,
}: {
  params: { lang: 'en' | 'es' }
}): Promise<Metadata> {
  const dict = (await getDictionary(params.lang)) as any
  const blogDict = (dict as any).blog?.aiDictationGuide

  return {
    title: blogDict?.meta?.title || 'How to Use AI Dictation: Complete Beginner\'s Guide',
    description:
      blogDict?.meta?.description ||
      'Learn to use AI dictation effectively. Setup, tips, best practices, and common mistakes. Start voice typing in 5 minutes.',
    keywords:
      blogDict?.meta?.keywords ||
      'how to use AI dictation, AI dictation tutorial, voice typing guide, speech to text tips',
    metadataBase: new URL('https://whispercheap.com'),
    alternates: {
      canonical: `https://whispercheap.com/${params.lang}/blog/ai-dictation-guide`,
    },
    openGraph: {
      title: blogDict?.meta?.title,
      description: blogDict?.meta?.description,
      url: `https://whispercheap.com/${params.lang}/blog/ai-dictation-guide`,
      type: 'article',
      publishedTime: new Date('2025-01-03').toISOString(),
      authors: ['Whisper Cheap Team'],
      images: [
        {
          url: '/og-blog-dictation.png',
          width: 1200,
          height: 630,
          alt: 'AI Dictation Guide',
        },
      ],
    },
  }
}

export default async function AIDictationGuidePage({
  params,
}: {
  params: { lang: 'en' | 'es' }
}) {
  const dict = (await getDictionary(params.lang)) as any
  const blogDict = (dict as any).blog?.aiDictationGuide

  return (
    <>
      <AIDictationGuideClient lang={params.lang} blogDict={blogDict} />
      {/* Article Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: blogDict?.hero?.title,
            description: blogDict?.hero?.subtitle,
            image: '/og-blog-dictation.png',
            datePublished: new Date('2025-01-03').toISOString(),
            dateModified: new Date('2025-01-03').toISOString(),
            author: {
              '@type': 'Organization',
              name: blogDict?.hero?.author,
            },
            publisher: {
              '@type': 'Organization',
              name: 'Whisper Cheap',
              logo: {
                '@type': 'ImageObject',
                url: '/logo.png',
              },
            },
          }),
        }}
      />

      {/* HowTo Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            name: blogDict?.sections?.gettingStarted?.title,
            step: (blogDict?.sections?.gettingStarted?.steps || []).map(
              (step: any, idx: number) => ({
                '@type': 'HowToStep',
                position: idx + 1,
                name: step.title,
                text: step.description,
              })
            ),
          }),
        }}
      />
    </>
  )
}
