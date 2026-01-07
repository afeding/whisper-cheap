'use client'

import { Locale } from '@/dictionaries'
import Link from 'next/link'
import { PencilIcon, BrainIcon, ChevronDownIcon, CheckIcon, MicIcon } from 'lucide-react'

const DOWNLOAD_URL = `https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe`

interface WritersPageProps {
  dict: {
    meta: { title: string; description: string }
    hero: { hook: string; subtitle: string; cta: string }
    problem: {
      title: string
      intro: string
      painPoint1: string
      painPoint1Desc: string
      painPoint2: string
      painPoint2Desc: string
      painPoint3: string
      painPoint3Desc: string
      painPoint4: string
      painPoint4Desc: string
    }
    solution: {
      title: string
      intro: string
      benefit1Title: string
      benefit1Desc: string
      benefit2Title: string
      benefit2Desc: string
      benefit3Title: string
      benefit3Desc: string
    }
    whyWhisperCheap: {
      title: string
      reason1Title: string
      reason1Desc: string
      reason2Title: string
      reason2Desc: string
      reason3Title: string
      reason3Desc: string
    }
    workflows: {
      title: string
      intro: string
      workflow1Title: string
      workflow1Desc: string
      workflow2Title: string
      workflow2Desc: string
      workflow3Title: string
      workflow3Desc: string
      workflow4Title: string
      workflow4Desc: string
      workflow5Title: string
      workflow5Desc: string
    }
    tips: {
      title: string
      intro: string
      tip1Title: string
      tip1Desc: string
      tip2Title: string
      tip2Desc: string
      tip3Title: string
      tip3Desc: string
      tip4Title: string
      tip4Desc: string
      tip5Title: string
      tip5Desc: string
    }
    faqWriters: {
      title: string
      q1: string
      a1: string
      q2: string
      a2: string
      q3: string
      a3: string
      q4: string
      a4: string
      q5: string
      a5: string
      q6: string
      a6: string
    }
    cta: { title: string; subtitle: string; button: string }
  }
  lang: Locale
}

interface FAQItem {
  q: string
  a: string
}

export function WritersPage({ dict, lang }: WritersPageProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'

  const faqItems: FAQItem[] = [
    { q: dict.faqWriters.q1, a: dict.faqWriters.a1 },
    { q: dict.faqWriters.q2, a: dict.faqWriters.a2 },
    { q: dict.faqWriters.q3, a: dict.faqWriters.a3 },
    { q: dict.faqWriters.q4, a: dict.faqWriters.a4 },
    { q: dict.faqWriters.q5, a: dict.faqWriters.a5 },
    { q: dict.faqWriters.q6, a: dict.faqWriters.a6 },
  ]

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary bg-noise">
      {/* Fixed gradient background */}
      <div className="fixed inset-0 bg-gradient-radial pointer-events-none" />

      {/* Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href={`/${lang}`} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
              <MicIcon className="w-4 h-4 text-accent" />
            </div>
            <span className="font-display font-semibold text-lg tracking-tight">Whisper Cheap</span>
          </Link>

          <div className="flex items-center gap-6">
            <a
              href={DOWNLOAD_URL}
              className="px-4 py-2 rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors text-sm font-medium"
            >
              {lang === 'en' ? 'Download' : 'Descargar'}
            </a>
            <a href={`/${otherLang}/use-cases/writers`} className="text-sm text-text-secondary hover:text-text-primary transition-colors">
              {lang === 'en' ? 'ES' : 'EN'}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-16 px-6 md:pt-48 md:pb-24">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-accent" />
            {lang === 'en' ? 'For Writers' : 'Para Escritores'}
          </div>

          <h1 className="text-5xl md:text-6xl font-display font-bold tracking-tight">
            {dict.hero.hook}
          </h1>

          <p className="text-xl text-text-secondary leading-relaxed">
            {dict.hero.subtitle}
          </p>

          <div className="pt-4">
            <a
              href={DOWNLOAD_URL}
              className="inline-block px-8 py-4 rounded-lg bg-accent text-bg-primary font-semibold hover:bg-accent/90 transition-colors"
            >
              {dict.hero.cta}
            </a>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center text-text-primary">
            {dict.problem.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.problem.intro}</p>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Pain Point 1 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <PencilIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.problem.painPoint1}</h3>
              <p className="text-text-secondary">{dict.problem.painPoint1Desc}</p>
            </div>

            {/* Pain Point 2 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <BrainIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.problem.painPoint2}</h3>
              <p className="text-text-secondary">{dict.problem.painPoint2Desc}</p>
            </div>

            {/* Pain Point 3 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <MicIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.problem.painPoint3}</h3>
              <p className="text-text-secondary">{dict.problem.painPoint3Desc}</p>
            </div>

            {/* Pain Point 4 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <ChevronDownIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.problem.painPoint4}</h3>
              <p className="text-text-secondary">{dict.problem.painPoint4Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center text-text-primary">
            {dict.solution.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.solution.intro}</p>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Benefit 1 */}
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <CheckIcon className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-xl">{dict.solution.benefit1Title}</h3>
              <p className="text-text-secondary leading-relaxed">{dict.solution.benefit1Desc}</p>
            </div>

            {/* Benefit 2 */}
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <CheckIcon className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-xl">{dict.solution.benefit2Title}</h3>
              <p className="text-text-secondary leading-relaxed">{dict.solution.benefit2Desc}</p>
            </div>

            {/* Benefit 3 */}
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <CheckIcon className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-xl">{dict.solution.benefit3Title}</h3>
              <p className="text-text-secondary leading-relaxed">{dict.solution.benefit3Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Whisper Cheap Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center text-text-primary">
            {dict.whyWhisperCheap.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Reason 1 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">1</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyWhisperCheap.reason1Title}</h3>
              <p className="text-text-secondary">{dict.whyWhisperCheap.reason1Desc}</p>
            </div>

            {/* Reason 2 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">2</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyWhisperCheap.reason2Title}</h3>
              <p className="text-text-secondary">{dict.whyWhisperCheap.reason2Desc}</p>
            </div>

            {/* Reason 3 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">3</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyWhisperCheap.reason3Title}</h3>
              <p className="text-text-secondary">{dict.whyWhisperCheap.reason3Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Real Workflows Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center text-text-primary">
            {dict.workflows.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.workflows.intro}</p>

          <div className="space-y-4">
            <WorkflowItem title={dict.workflows.workflow1Title} desc={dict.workflows.workflow1Desc} />
            <WorkflowItem title={dict.workflows.workflow2Title} desc={dict.workflows.workflow2Desc} />
            <WorkflowItem title={dict.workflows.workflow3Title} desc={dict.workflows.workflow3Desc} />
            <WorkflowItem title={dict.workflows.workflow4Title} desc={dict.workflows.workflow4Desc} />
            <WorkflowItem title={dict.workflows.workflow5Title} desc={dict.workflows.workflow5Desc} />
          </div>
        </div>
      </section>

      {/* Tips Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center text-text-primary">
            {dict.tips.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.tips.intro}</p>

          <div className="grid md:grid-cols-2 gap-6">
            <TipCard title={dict.tips.tip1Title} desc={dict.tips.tip1Desc} icon="1" />
            <TipCard title={dict.tips.tip2Title} desc={dict.tips.tip2Desc} icon="2" />
            <TipCard title={dict.tips.tip3Title} desc={dict.tips.tip3Desc} icon="3" />
            <TipCard title={dict.tips.tip4Title} desc={dict.tips.tip4Desc} icon="4" />
            <TipCard title={dict.tips.tip5Title} desc={dict.tips.tip5Desc} icon="5" />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center text-text-primary">
            {dict.faqWriters.title}
          </h2>

          <div className="space-y-3">
            {faqItems.map((item, idx) => (
              <FAQItem key={idx} question={item.q} answer={item.a} />
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-4xl md:text-5xl font-display font-bold tracking-tight text-text-primary">
            {dict.cta.title}
          </h2>
          <p className="text-xl text-text-secondary">{dict.cta.subtitle}</p>
          <a
            href={DOWNLOAD_URL}
            className="inline-block px-8 py-4 rounded-lg bg-accent text-bg-primary font-semibold hover:bg-accent/90 transition-colors"
          >
            {dict.cta.button}
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-border-default/50 py-12 px-6">
        <div className="max-w-6xl mx-auto text-center text-text-secondary text-sm">
          <p>Whisper Cheap. For those who hate typing.</p>
        </div>
      </footer>
    </div>
  )
}

/**
 * Workflow item component
 */
function WorkflowItem({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="p-6 rounded-xl bg-bg-card border border-border-default/50 hover:border-accent/30 transition-all">
      <h3 className="font-semibold text-lg mb-2 text-text-primary">{title}</h3>
      <p className="text-text-secondary">{desc}</p>
    </div>
  )
}

/**
 * Tip card component
 */
function TipCard({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div className="p-6 rounded-xl bg-bg-card border border-border-default/50 hover:border-border-hover transition-colors">
      <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
        <span className="text-accent font-bold text-sm">{icon}</span>
      </div>
      <h3 className="font-semibold text-lg mb-2 text-text-primary">{title}</h3>
      <p className="text-text-secondary text-sm leading-relaxed">{desc}</p>
    </div>
  )
}

/**
 * FAQ item component (accordion)
 */
function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <details
      className="group p-4 rounded-lg bg-bg-card border border-border-default/50 hover:border-border-hover transition-all cursor-pointer"
      open={isOpen}
      onToggle={() => setIsOpen(!isOpen)}
    >
      <summary className="flex items-center justify-between font-semibold select-none text-text-primary">
        <span>{question}</span>
        <ChevronDownIcon className="w-5 h-5 text-text-secondary group-open:rotate-180 transition-transform" />
      </summary>
      <div className="pt-4 text-text-secondary leading-relaxed">{answer}</div>
    </details>
  )
}

// Import React for useState
import * as React from 'react'
