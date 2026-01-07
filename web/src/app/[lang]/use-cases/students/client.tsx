'use client'

import type { Locale } from '@/dictionaries'
import { BookOpen, FileText, Lightbulb, Brain, Search, CheckCircle2, ArrowRight, Volume2 } from 'lucide-react'
import Link from 'next/link'

interface StudentsPageClientProps {
  params: { lang: Locale }
  dict: any
}

export default function StudentsPageClient({ params, dict }: StudentsPageClientProps) {
  const studentDict = dict?.students || {}
  const downloadUrl = 'https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe'
  const otherLang = params.lang === 'en' ? 'es' : 'en'

  const useCaseIcons: Record<string, React.ComponentType<any>> = {
    BookOpen,
    FileText,
    Lightbulb,
    Brain,
    Search,
  }

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary bg-noise">
      {/* Fixed background gradient */}
      <div className="fixed inset-0 bg-gradient-radial pointer-events-none" />

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href={`/${params.lang}`} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
              <Volume2 className="w-4 h-4 text-accent" />
            </div>
            <span className="font-display font-semibold text-lg tracking-tight">Whisper Cheap</span>
          </Link>
          <div className="flex items-center gap-4">
            <a
              href={downloadUrl}
              className="px-4 py-2 rounded-lg bg-accent text-bg-primary font-medium hover:opacity-90 transition-opacity"
            >
              {studentDict.hero?.cta || 'Download'}
            </a>
            <Link
              href={`/${otherLang}/use-cases/students`}
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              {params.lang === 'en' ? 'ES' : 'EN'}
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative">
        {/* Hero Section */}
        <section className="pt-32 pb-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 mb-6">
              <span className="text-sm font-medium text-accent">{studentDict.hero?.tagline}</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-display font-bold tracking-tight mb-6">
              {studentDict.hero?.title}
            </h1>
            <p className="text-xl text-text-secondary mb-8">
              {studentDict.hero?.subtitle}
            </p>
            <div className="inline-flex items-center gap-3 text-sm text-text-secondary bg-bg-secondary/50 px-4 py-2 rounded-lg border border-border-default/50 mb-8">
              <CheckCircle2 className="w-4 h-4 text-accent" />
              {studentDict.hero?.highlight}
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href={downloadUrl}
                className="px-8 py-3 rounded-lg bg-accent text-bg-primary font-semibold hover:opacity-90 transition-opacity inline-flex items-center gap-2 justify-center"
              >
                {studentDict.hero?.cta} <ArrowRight className="w-4 h-4" />
              </a>
              <a
                href="#faq"
                className="px-8 py-3 rounded-lg border border-border-default bg-bg-secondary/50 hover:bg-bg-secondary transition-colors inline-flex items-center gap-2 justify-center"
              >
                {params.lang === 'en' ? 'Learn More' : 'Saber Más'}
              </a>
            </div>
          </div>
        </section>

        {/* Problem Section */}
        <section className="py-20 px-6 bg-bg-secondary/30 border-y border-border-default/30">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-4 text-center">
              {studentDict.problem?.title}
            </h2>
            <p className="text-text-secondary text-center mb-12">
              {studentDict.problem?.intro}
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { title: studentDict.problem?.pain1, desc: studentDict.problem?.pain1Desc },
                { title: studentDict.problem?.pain2, desc: studentDict.problem?.pain2Desc },
                { title: studentDict.problem?.pain3, desc: studentDict.problem?.pain3Desc },
                { title: studentDict.problem?.pain4, desc: studentDict.problem?.pain4Desc },
              ].map((item: any, i: number) => (
                <div key={i} className="p-6 rounded-lg border border-border-default/50 bg-bg-primary">
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-text-secondary">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Solution Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-4 text-center">
              {studentDict.solution?.title}
            </h2>
            <p className="text-text-secondary text-center mb-12">
              {studentDict.solution?.intro}
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: studentDict.solution?.benefit1,
                  desc: studentDict.solution?.benefit1Desc,
                },
                {
                  title: studentDict.solution?.benefit2,
                  desc: studentDict.solution?.benefit2Desc,
                },
                {
                  title: studentDict.solution?.benefit3,
                  desc: studentDict.solution?.benefit3Desc,
                },
              ].map((item: any, i: number) => (
                <div key={i} className="p-6 rounded-lg bg-bg-secondary/50 border border-border-default/50 text-center">
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-text-secondary">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Why Whisper Cheap */}
        <section className="py-20 px-6 bg-bg-secondary/30 border-y border-border-default/30">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-12 text-center">
              {studentDict.whyWhisperCheap?.title}
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                {
                  title: studentDict.whyWhisperCheap?.free?.title,
                  desc: studentDict.whyWhisperCheap?.free?.desc,
                },
                {
                  title: studentDict.whyWhisperCheap?.offline?.title,
                  desc: studentDict.whyWhisperCheap?.offline?.desc,
                },
                {
                  title: studentDict.whyWhisperCheap?.private?.title,
                  desc: studentDict.whyWhisperCheap?.private?.desc,
                },
                {
                  title: studentDict.whyWhisperCheap?.easy?.title,
                  desc: studentDict.whyWhisperCheap?.easy?.desc,
                },
              ].map((item: any, i: number) => (
                <div key={i} className="p-6 rounded-lg border border-accent/20 bg-accent/5">
                  <h3 className="font-semibold mb-2 text-accent">{item.title}</h3>
                  <p className="text-sm text-text-secondary">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-12 text-center">
              {studentDict.useCases?.title}
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {studentDict.useCases?.cases?.map((useCase: any, i: number) => {
                const IconComponent = useCaseIcons[useCase.icon] || BookOpen
                return (
                  <div key={i} className="p-6 rounded-lg bg-bg-secondary/50 border border-border-default/50 hover:border-accent/50 transition-colors">
                    <IconComponent className="w-8 h-8 text-accent mb-4" />
                    <h3 className="font-semibold mb-2">{useCase.title}</h3>
                    <p className="text-sm text-text-secondary">{useCase.desc}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-20 px-6 bg-bg-secondary/30 border-y border-border-default/30">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-12 text-center">
              {studentDict.faq?.title}
            </h2>
            <div className="space-y-4">
              {studentDict.faq?.items?.map((item: any, i: number) => (
                <details
                  key={i}
                  className="group p-6 rounded-lg bg-bg-primary border border-border-default/50 hover:border-border-default transition-colors cursor-pointer"
                >
                  <summary className="font-semibold flex items-center justify-between">
                    {item.q}
                    <span className="ml-4 group-open:rotate-180 transition-transform">▼</span>
                  </summary>
                  <p className="text-text-secondary text-sm mt-4">{item.a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonial */}
        {studentDict.testimonial && (
          <section className="py-20 px-6">
            <div className="max-w-2xl mx-auto text-center">
              <p className="text-2xl font-semibold mb-6 italic">
                "{studentDict.testimonial.quote}"
              </p>
              <p className="text-text-secondary">— {studentDict.testimonial.author}</p>
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="py-20 px-6 bg-accent/5 border-y border-accent/20">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-display font-bold mb-4">
              {studentDict.cta?.title}
            </h2>
            <p className="text-text-secondary mb-8">
              {studentDict.cta?.subtitle}
            </p>
            <a
              href={downloadUrl}
              className="px-8 py-3 rounded-lg bg-accent text-bg-primary font-semibold hover:opacity-90 transition-opacity inline-flex items-center gap-2"
            >
              {studentDict.cta?.button} <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border-default/50 bg-bg-secondary/30 py-12 px-6">
        <div className="max-w-6xl mx-auto text-center text-text-secondary text-sm">
          <p>
            {params.lang === 'en'
              ? 'Built with care for students who think faster than they type.'
              : 'Hecho con cuidado para estudiantes que piensan más rápido de lo que escriben.'}
          </p>
          <div className="mt-6 flex items-center justify-center gap-6">
            <a href="https://github.com/afeding/whisper-cheap" className="hover:text-accent transition-colors">
              GitHub
            </a>
            <a href="https://github.com/afeding/whisper-cheap/releases" className="hover:text-accent transition-colors">
              {params.lang === 'en' ? 'Releases' : 'Versiones'}
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
