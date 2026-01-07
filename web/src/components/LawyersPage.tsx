'use client'

import { Locale } from '@/dictionaries'
import Link from 'next/link'
import { ShieldCheckIcon, ChevronDownIcon, CheckIcon, MicIcon, ScaleIcon, LockIcon } from 'lucide-react'

const DOWNLOAD_URL = `https://github.com/afeding/whisper-cheap/releases/latest/download/WhisperCheapSetup.exe`

interface LawyersPageProps {
  dict: {
    meta: { title: string; description: string }
    hero: { eyebrow: string; title: string; subtitle: string; cta: string }
    privacy: {
      title: string
      intro: string
      point1Title: string
      point1Desc: string
      point2Title: string
      point2Desc: string
      point3Title: string
      point3Desc: string
      point4Title: string
      point4Desc: string
    }
    useCases: {
      title: string
      intro: string
      case1Title: string
      case1Desc: string
      case2Title: string
      case2Desc: string
      case3Title: string
      case3Desc: string
      case4Title: string
      case4Desc: string
      case5Title: string
      case5Desc: string
      case6Title: string
      case6Desc: string
    }
    whyLawyers: {
      title: string
      reason1Title: string
      reason1Desc: string
      reason2Title: string
      reason2Desc: string
      reason3Title: string
      reason3Desc: string
    }
    comparison: {
      title: string
      features: Array<{ label: string; dragon: string; whisper: string }>
    }
    dragonBetter: {
      title: string
      intro: string
      features: Array<{ heading: string; text: string }>
    }
    perfFor: {
      title: string
      profiles: string[]
    }
    tips: {
      title: string
      tips: string[]
    }
    faqLawyers: {
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
    complianceNote: {
      title: string
      text: string
    }
    cta: { title: string; subtitle: string; button: string }
  }
  lang: Locale
}

interface FAQItem {
  q: string
  a: string
}

export function LawyersPage({ dict, lang }: LawyersPageProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'

  const faqItems: FAQItem[] = [
    { q: dict.faqLawyers.q1, a: dict.faqLawyers.a1 },
    { q: dict.faqLawyers.q2, a: dict.faqLawyers.a2 },
    { q: dict.faqLawyers.q3, a: dict.faqLawyers.a3 },
    { q: dict.faqLawyers.q4, a: dict.faqLawyers.a4 },
    { q: dict.faqLawyers.q5, a: dict.faqLawyers.a5 },
    { q: dict.faqLawyers.q6, a: dict.faqLawyers.a6 },
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
            <a href={`/${otherLang}/use-cases/lawyers`} className="text-sm text-text-secondary hover:text-text-primary transition-colors">
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
            {dict.hero.eyebrow}
          </div>

          <h1 className="text-5xl md:text-6xl font-display font-bold tracking-tight">
            {dict.hero.title}
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

      {/* Privacy Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center">
            {dict.privacy.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.privacy.intro}</p>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Privacy Point 1 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <LockIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.privacy.point1Title}</h3>
              <p className="text-text-secondary">{dict.privacy.point1Desc}</p>
            </div>

            {/* Privacy Point 2 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <ShieldCheckIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.privacy.point2Title}</h3>
              <p className="text-text-secondary">{dict.privacy.point2Desc}</p>
            </div>

            {/* Privacy Point 3 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <ScaleIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.privacy.point3Title}</h3>
              <p className="text-text-secondary">{dict.privacy.point3Desc}</p>
            </div>

            {/* Privacy Point 4 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <CheckIcon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{dict.privacy.point4Title}</h3>
              <p className="text-text-secondary">{dict.privacy.point4Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center">
            {dict.useCases.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.useCases.intro}</p>

          <div className="grid md:grid-cols-2 gap-6">
            <UseCaseCard title={dict.useCases.case1Title} desc={dict.useCases.case1Desc} />
            <UseCaseCard title={dict.useCases.case2Title} desc={dict.useCases.case2Desc} />
            <UseCaseCard title={dict.useCases.case3Title} desc={dict.useCases.case3Desc} />
            <UseCaseCard title={dict.useCases.case4Title} desc={dict.useCases.case4Desc} />
            <UseCaseCard title={dict.useCases.case5Title} desc={dict.useCases.case5Desc} />
            <UseCaseCard title={dict.useCases.case6Title} desc={dict.useCases.case6Desc} />
          </div>
        </div>
      </section>

      {/* Why Lawyers Choose Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
            {dict.whyLawyers.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Reason 1 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">1</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyLawyers.reason1Title}</h3>
              <p className="text-text-secondary">{dict.whyLawyers.reason1Desc}</p>
            </div>

            {/* Reason 2 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">2</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyLawyers.reason2Title}</h3>
              <p className="text-text-secondary">{dict.whyLawyers.reason2Desc}</p>
            </div>

            {/* Reason 3 */}
            <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-accent font-bold">3</span>
              </div>
              <h3 className="font-semibold text-lg mb-3">{dict.whyLawyers.reason3Title}</h3>
              <p className="text-text-secondary">{dict.whyLawyers.reason3Desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
            {dict.comparison.title}
          </h2>

          <div className="overflow-x-auto rounded-xl border border-border-default/50">
            <table className="w-full">
              <thead>
                <tr className="bg-bg-secondary/50 border-b border-border-default/50">
                  <th className="px-6 py-4 text-left font-semibold">Feature</th>
                  <th className="px-6 py-4 text-left font-semibold text-red-400">Dragon Legal</th>
                  <th className="px-6 py-4 text-left font-semibold text-accent">Whisper Cheap</th>
                </tr>
              </thead>
              <tbody>
                {dict.comparison.features.map((feature, idx) => (
                  <tr key={idx} className="border-b border-border-default/30 hover:bg-bg-secondary/20">
                    <td className="px-6 py-4 font-medium">{feature.label}</td>
                    <td className="px-6 py-4 text-text-secondary">{feature.dragon}</td>
                    <td className="px-6 py-4 text-accent font-medium">{feature.whisper}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Where Dragon Wins Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center">
            {dict.dragonBetter.title}
          </h2>
          <p className="text-center text-text-secondary text-lg mb-16">{dict.dragonBetter.intro}</p>

          <div className="space-y-6">
            {dict.dragonBetter.features.map((feature, idx) => (
              <div key={idx} className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
                <h3 className="font-semibold text-lg mb-3">{feature.heading}</h3>
                <p className="text-text-secondary">{feature.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Perfect For Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
            {dict.perfFor.title}
          </h2>

          <div className="grid md:grid-cols-2 gap-4">
            {dict.perfFor.profiles.map((profile, idx) => (
              <div key={idx} className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary/50 border border-border-default/30">
                <CheckIcon className="w-5 h-5 text-accent flex-shrink-0 mt-1" />
                <p className="text-text-secondary">{profile}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tips Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
            {dict.tips.title}
          </h2>

          <div className="space-y-4">
            {dict.tips.tips.map((tip, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-bg-primary border border-border-default/30 flex gap-4">
                <span className="text-accent font-bold flex-shrink-0">{idx + 1}.</span>
                <p className="text-text-secondary">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Compliance Note */}
      <section className="relative py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="p-8 rounded-xl bg-accent/10 border border-accent/30">
            <h3 className="text-2xl font-display font-bold mb-4">{dict.complianceNote.title}</h3>
            <p className="text-text-secondary leading-relaxed">{dict.complianceNote.text}</p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-20 px-6 bg-bg-secondary/50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
            {dict.faqLawyers.title}
          </h2>

          <div className="space-y-3">
            {faqItems.map((item, idx) => (
              <FAQItem key={idx} question={item.q} answer={item.a} />
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-4xl md:text-5xl font-display font-bold tracking-tight">
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
 * Use case card component
 */
function UseCaseCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="p-6 rounded-xl bg-bg-card border border-border-default hover:border-accent/30 transition-all">
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-text-secondary">{desc}</p>
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
      className="group p-4 rounded-lg bg-bg-card border border-border-default hover:border-accent/30 transition-all cursor-pointer"
      open={isOpen}
      onToggle={() => setIsOpen(!isOpen)}
    >
      <summary className="flex items-center justify-between font-semibold select-none">
        <span>{question}</span>
        <ChevronDownIcon className="w-5 h-5 text-text-secondary group-open:rotate-180 transition-transform" />
      </summary>
      <div className="pt-4 text-text-secondary leading-relaxed">{answer}</div>
    </details>
  )
}

// Import React for useState
import * as React from 'react'
