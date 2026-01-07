import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import Link from 'next/link'
import { Breadcrumbs } from '@/components/Breadcrumbs'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const isSpanish = params.lang === 'es'

  const title = isSpanish
    ? 'Blog - Guías y Consejos de Dictado por IA | Whisper Cheap'
    : 'Blog - AI Dictation Guides & Tips | Whisper Cheap'
  const description = isSpanish
    ? 'Guías completas, consejos de productividad y mejores prácticas para dominar el dictado por IA. Aprende a escribir más rápido con voz.'
    : 'Complete guides, productivity tips, and best practices for mastering AI dictation. Learn to write faster with voice.'

  return {
    title,
    description,
    keywords: isSpanish
      ? 'blog dictado IA, guías voz a texto, consejos productividad, tutoriales dictado'
      : 'AI dictation blog, voice typing guides, productivity tips, dictation tutorials',
    alternates: {
      canonical: `/${params.lang}/blog`,
      languages: {
        en: '/en/blog',
        es: '/es/blog',
        'x-default': '/en/blog',
      },
    },
    openGraph: {
      title,
      description,
      url: `${baseUrl}/${params.lang}/blog`,
      siteName: 'Whisper Cheap',
      locale: isSpanish ? 'es_ES' : 'en_US',
      type: 'website',
    },
  }
}

export default async function BlogIndexPage({
  params,
}: {
  params: { lang: Locale }
}) {
  const dict = await getDictionary(params.lang)
  const isSpanish = params.lang === 'es'

  const blogPosts = [
    {
      slug: 'voice-typing-tips',
      title: dict.blog?.voiceTypingTips?.meta?.title || (isSpanish
        ? '15 Consejos de Escritura por Voz para Triplicar tu Productividad'
        : '15 Voice Typing Tips to 3x Your Productivity'),
      description: dict.blog?.voiceTypingTips?.meta?.description || (isSpanish
        ? 'Domina la escritura por voz con estos consejos de productividad comprobados. Escribe más rápido, reduce errores y maximiza la eficiencia con dictado por IA.'
        : 'Master voice typing with these proven productivity tips. Write faster, reduce errors, and maximize efficiency with AI dictation.'),
      date: isSpanish ? '3 de enero de 2025' : 'January 3, 2025',
      readingTime: isSpanish ? '18 min de lectura' : '18 min read',
      category: isSpanish ? 'Productividad' : 'Productivity',
      badge: isSpanish ? 'Guía Completa' : 'Complete Guide',
    },
    {
      slug: 'ai-dictation-guide',
      title: dict.blog?.aiDictationGuide?.meta?.title || (isSpanish
        ? 'Cómo Usar el Dictado por IA: Guía Completa para Principiantes (2025)'
        : 'How to Use AI Dictation: Complete Beginner\'s Guide (2025)'),
      description: dict.blog?.aiDictationGuide?.meta?.description || (isSpanish
        ? 'Aprende a usar el dictado por IA efectivamente. Configuración, consejos, mejores prácticas y errores comunes. Comienza a escribir por voz en 5 minutos.'
        : 'Learn to use AI dictation effectively. Setup, tips, best practices, and common mistakes. Start voice typing in 5 minutes.'),
      date: isSpanish ? '3 de enero de 2025' : 'January 3, 2025',
      readingTime: isSpanish ? '10 min de lectura' : '10 min read',
      category: isSpanish ? 'Tutorial' : 'Tutorial',
      badge: isSpanish ? 'Para Principiantes' : 'For Beginners',
    },
  ]

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Hero Section */}
      <section className="bg-bg-primary text-text-primary py-16 px-4 md:py-24">
        <div className="max-w-4xl mx-auto">
          <Breadcrumbs lang={params.lang} items={[{ label: isSpanish ? 'Blog' : 'Blog' }]} />
          <h1 className="text-4xl md:text-5xl font-bold font-display mb-6">
            {isSpanish ? 'Blog de Whisper Cheap' : 'Whisper Cheap Blog'}
          </h1>
          <p className="text-xl text-text-secondary mb-8">
            {isSpanish
              ? 'Guías completas, consejos de productividad y mejores prácticas para dominar el dictado por IA.'
              : 'Complete guides, productivity tips, and best practices for mastering AI dictation.'}
          </p>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <span className="text-sm text-text-secondary">
                {blogPosts.length} {isSpanish ? 'artículos' : 'articles'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <span className="text-sm text-text-secondary">
                {isSpanish ? 'Actualizado regularmente' : 'Updated regularly'}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Blog Posts Grid */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {blogPosts.map((post) => (
              <Link
                key={post.slug}
                href={`/${params.lang}/blog/${post.slug}`}
                className="group block bg-bg-card border border-border-default rounded-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:border-border-hover hover:bg-bg-elevated"
              >
                <div className="p-6">
                  {/* Badge */}
                  <div className="inline-block bg-accent/10 text-accent border border-accent/20 px-3 py-1 rounded-full text-sm font-medium mb-4">
                    {post.badge}
                  </div>

                  {/* Title */}
                  <h2 className="text-2xl font-bold font-display text-text-primary mb-3 group-hover:text-accent transition-colors">
                    {post.title}
                  </h2>

                  {/* Description */}
                  <p className="text-text-secondary mb-4 line-clamp-3">
                    {post.description}
                  </p>

                  {/* Meta */}
                  <div className="flex items-center gap-4 text-sm text-text-dim">
                    <span>{post.date}</span>
                    <span>•</span>
                    <span>{post.readingTime}</span>
                    <span>•</span>
                    <span className="text-accent font-medium">{post.category}</span>
                  </div>

                  {/* Read more arrow */}
                  <div className="mt-4 flex items-center gap-2 text-accent font-medium group-hover:gap-3 transition-all">
                    <span>{isSpanish ? 'Leer más' : 'Read more'}</span>
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-bg-secondary py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold font-display text-text-primary mb-4">
            {isSpanish ? '¿Listo para empezar?' : 'Ready to get started?'}
          </h2>
          <p className="text-xl text-text-secondary mb-8">
            {isSpanish
              ? 'Descarga Whisper Cheap y comienza a escribir por voz hoy mismo.'
              : 'Download Whisper Cheap and start voice typing today.'}
          </p>
          <Link
            href="https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe"
            className="inline-block bg-accent text-bg-primary px-8 py-3 rounded-lg font-medium hover:bg-accent-hover transition-colors"
          >
            {isSpanish ? 'Descargar' : 'Download'}
          </Link>
        </div>
      </section>
    </div>
  )
}
