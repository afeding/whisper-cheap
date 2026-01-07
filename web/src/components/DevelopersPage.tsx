'use client'

import { type Locale } from '@/dictionaries'
import Link from 'next/link'

interface DevelopersDictionary {
  meta: {
    title: string
    description: string
    keywords: string
  }
  hero: {
    tagline: string
    title: string
    subtitle: string
    highlight: string
  }
  pain: {
    title: string
    items: Array<{ title: string; desc: string }>
  }
  useCases: {
    title: string
    cases: Array<{ icon: string; title: string; desc: string }>
  }
  tools: {
    title: string
    description: string
    howItWorks: string
  }
  whyDevs: {
    title: string
    reasons: Array<{ title: string; desc: string }>
  }
  tips: {
    title: string
    tips: string[]
  }
  github: {
    title: string
    desc: string
    button: string
  }
  faq: {
    title: string
    items: Array<{ q: string; a: string }>
  }
  cta: {
    title: string
    subtitle: string
    note: string
  }
}

interface Props {
  dict: DevelopersDictionary
  lang: Locale
}

// Simple icon components (no external dependency)
const FileTextIcon = () => <span className="text-2xl">📄</span>
const GitBranchIcon = () => <span className="text-2xl">🌿</span>
const MessageSquareIcon = () => <span className="text-2xl">💬</span>
const BookOpenIcon = () => <span className="text-2xl">📖</span>
const LightbulbIcon = () => <span className="text-2xl">💡</span>
const GithubIcon = () => <span className="text-2xl">⚙️</span>
const CheckIcon = () => <span className="text-xl">✓</span>
const ArrowIcon = () => <span>→</span>

const iconMap: Record<string, () => JSX.Element> = {
  FileText: FileTextIcon,
  GitBranch: GitBranchIcon,
  MessageSquare: MessageSquareIcon,
  BookOpen: BookOpenIcon,
  Lightbulb: LightbulbIcon,
}

export function DevelopersPage({ dict, lang }: Props) {
  const downloadPath = lang === 'es' ? '/es#download' : '/en#download'

  return (
    <article className="min-h-screen bg-bg-primary text-text-primary">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="space-y-6">
            <div className="inline-block">
              <span className="text-sm font-semibold tracking-widest text-accent">
                {dict.hero.tagline}
              </span>
            </div>
            <h1 className="text-5xl font-display font-bold tracking-tight sm:text-6xl">
              {dict.hero.title}
            </h1>
            <p className="max-w-2xl text-xl text-text-secondary">
              {dict.hero.subtitle}
            </p>
            <p className="max-w-2xl text-lg font-semibold text-accent">
              {dict.hero.highlight}
            </p>
            <div>
              <Link
                href={downloadPath}
                className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 font-semibold text-bg-primary transition hover:bg-accent-hover"
              >
                {lang === 'es' ? 'Descargar' : 'Download'}
                <ArrowIcon />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Pain Points */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-3xl font-display font-bold">{dict.pain.title}</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            {dict.pain.items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-border-default bg-bg-card p-6">
                <h3 className="mb-2 font-semibold text-accent">{item.title}</h3>
                <p className="text-text-secondary">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-3xl font-display font-bold">{dict.useCases.title}</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {dict.useCases.cases.map((useCase, idx) => {
              const IconComponent = iconMap[useCase.icon as keyof typeof iconMap]
              return (
                <div key={idx} className="rounded-lg border border-border-default bg-bg-card p-6">
                  {IconComponent && (
                    <div className="mb-3">
                      <IconComponent />
                    </div>
                  )}
                  <h3 className="mb-2 font-semibold">{useCase.title}</h3>
                  <p className="text-sm text-text-secondary">{useCase.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Tools */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-6 text-3xl font-display font-bold">{dict.tools.title}</h2>
          <p className="mb-6 text-lg text-text-secondary">{dict.tools.description}</p>
          <div className="rounded-lg border border-accent/30 bg-accent/5 p-6">
            <code className="font-mono text-sm text-accent">{dict.tools.howItWorks}</code>
          </div>
        </div>
      </section>

      {/* Why Developers Choose Whisper Cheap */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-3xl font-display font-bold">{dict.whyDevs.title}</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            {dict.whyDevs.reasons.map((reason, idx) => (
              <div key={idx} className="rounded-lg border border-border-default bg-bg-card p-6">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-bg-primary">
                  <CheckIcon />
                </div>
                <h3 className="mb-2 font-semibold">{reason.title}</h3>
                <p className="text-sm text-text-secondary">{reason.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pro Tips */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-8 text-3xl font-display font-bold">{dict.tips.title}</h2>
          <div className="space-y-3">
            {dict.tips.tips.map((tip, idx) => (
              <div key={idx} className="flex gap-3 rounded-lg border border-border-default bg-bg-card p-4">
                <div className="flex-shrink-0 pt-1">
                  <span className="text-accent">
                    <CheckIcon />
                  </span>
                </div>
                <p className="text-text-secondary">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* GitHub CTA */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="rounded-lg border border-accent/30 bg-accent/5 p-8 text-center">
            <div className="mb-4 text-4xl">
              <GithubIcon />
            </div>
            <h2 className="mb-3 text-2xl font-display font-bold">{dict.github.title}</h2>
            <p className="mb-6 text-text-secondary">{dict.github.desc}</p>
            <a
              href="https://github.com/afeding/whisper-cheap"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-accent px-6 py-3 font-semibold text-accent transition hover:bg-accent/10"
            >
              <GithubIcon />
              {dict.github.button}
              <ArrowIcon />
            </a>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-3xl font-display font-bold">{dict.faq.title}</h2>
          <div className="space-y-6">
            {dict.faq.items.map((item, idx) => (
              <details
                key={idx}
                className="group rounded-lg border border-border-default bg-bg-card p-6 transition"
              >
                <summary className="flex cursor-pointer items-center justify-between font-semibold text-text-primary">
                  {item.q}
                  <span className="text-accent transition group-open:rotate-180">
                    ⌄
                  </span>
                </summary>
                <p className="mt-4 text-text-secondary">{item.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-b border-border-default">
        <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 lg:px-8 text-center">
          <h2 className="mb-4 text-4xl font-display font-bold">{dict.cta.title}</h2>
          <p className="mb-6 text-xl text-text-secondary">{dict.cta.subtitle}</p>
          <p className="mb-8 text-sm text-text-dim">{dict.cta.note}</p>
          <Link
            href={downloadPath}
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-8 py-4 text-lg font-semibold text-bg-primary transition hover:bg-accent-hover"
          >
            {lang === 'es' ? 'Descargar' : 'Download'}
            <ArrowIcon />
          </Link>
        </div>
      </section>
    </article>
  )
}
