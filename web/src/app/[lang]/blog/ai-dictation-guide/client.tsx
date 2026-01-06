'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Breadcrumbs } from '@/components/Breadcrumbs'

interface BlogDictionary {
  hero: {
    title: string
    subtitle: string
    date: string
    readingTime: string
    author: string
    authorRole: string
  }
  toc: {
    label: string
    items: Array<{
      id: string
      title: string
    }>
  }
  sections: {
    whatIs: {
      title: string
      subtitle: string
      content: string
      points: string[]
    }
    benefits: {
      title: string
      intro: string
      items: Array<{
        title: string
        description: string
        metric: string
      }>
    }
    gettingStarted: {
      title: string
      intro: string
      steps: Array<{
        num: string
        title: string
        description: string
        tips?: string[]
      }>
    }
    bestPractices: {
      title: string
      intro: string
      practices: Array<{
        title: string
        description: string
        icon: string
      }>
    }
    commonMistakes: {
      title: string
      intro: string
      mistakes: Array<{
        title: string
        description: string
        solution: string
      }>
    }
    advancedTips: {
      title: string
      intro: string
      tips: Array<{
        title: string
        description: string
      }>
    }
    faq: {
      title: string
      items: Array<{
        q: string
        a: string
      }>
    }
    cta: {
      title: string
      description: string
      buttonText: string
    }
  }
  relatedArticles: {
    label: string
    articles: Array<{
      title: string
      description: string
      url: string
    }>
  }
}

export function AIDictationGuideClient({
  lang,
  blogDict,
}: {
  lang: 'en' | 'es'
  blogDict: BlogDictionary | undefined
}) {
  const [tocOpen, setTocOpen] = useState(false)

  if (!blogDict) {
    return <div>Loading...</div>
  }

  if (!blogDict.sections || !blogDict.sections.whatIs) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary text-text-primary">
        <p>Content not available in this language yet.</p>
      </div>
    )
  }

  return (
    <article className="min-h-screen bg-gradient-to-b from-bg-primary to-bg-secondary">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border-default bg-bg-primary py-16 sm:py-24">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <Breadcrumbs lang={lang} items={[{ label: 'Blog', href: `/${lang}/blog` }, { label: blogDict.hero.title }]} />

          {/* Title and Meta */}
          <h1 className="mb-4 font-display text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            {blogDict.hero.title}
          </h1>
          <p className="mb-6 text-xl text-text-secondary sm:text-2xl">{blogDict.hero.subtitle}</p>

          {/* Author & Meta Info */}
          <div className="flex flex-wrap items-center gap-6 text-sm text-text-secondary">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent to-accent-hover" />
              <div>
                <div className="font-medium text-text-primary">{blogDict.hero.author}</div>
                <div className="text-xs">{blogDict.hero.authorRole}</div>
              </div>
            </div>
            <div className="hidden h-6 border-l border-border-default sm:block" />
            <time>{blogDict.hero.date}</time>
            <div className="hidden h-6 border-l border-border-default sm:block" />
            <span>{blogDict.hero.readingTime}</span>
          </div>
        </div>
      </section>

      {/* Table of Contents (Sticky) */}
      <TableOfContents
        items={blogDict.toc.items}
        lang={lang}
        label={blogDict.toc.label}
        isOpen={tocOpen}
        onToggle={setTocOpen}
      />


      {/* Main Content */}
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="prose prose-invert max-w-none space-y-16">
          {/* What is AI Dictation */}
          <section id="what-is-ai-dictation">
            <h2 className="mb-4 font-display text-3xl font-bold">{blogDict.sections.whatIs.title}</h2>
            <p className="mb-6 text-lg leading-relaxed text-text-secondary">
              {blogDict.sections.whatIs.subtitle}
            </p>
            <p className="mb-6 text-text-secondary">{blogDict.sections.whatIs.content}</p>
            <ul className="space-y-3 text-text-secondary">
              {blogDict.sections.whatIs.points.map((point, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="mt-1 inline-block h-2 w-2 rounded-full bg-accent flex-shrink-0" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Benefits */}
          <section id="benefits">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.benefits.title}</h2>
            <p className="mb-8 text-text-secondary">{blogDict.sections.benefits.intro}</p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {blogDict.sections.benefits.items.map((item, idx) => (
                <BenefitCard key={idx} item={item} />
              ))}
            </div>
          </section>

          {/* Getting Started */}
          <section id="getting-started">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.gettingStarted.title}</h2>
            <p className="mb-8 text-text-secondary">{blogDict.sections.gettingStarted.intro}</p>
            <div className="space-y-6">
              {blogDict.sections.gettingStarted.steps.map((step, idx) => (
                <StepCard key={idx} step={step} />
              ))}
            </div>
          </section>

          {/* Best Practices */}
          <section id="best-practices">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.bestPractices.title}</h2>
            <p className="mb-8 text-text-secondary">{blogDict.sections.bestPractices.intro}</p>
            <div className="grid gap-5 sm:grid-cols-2">
              {blogDict.sections.bestPractices.practices.map((practice, idx) => (
                <PracticeCard key={idx} practice={practice} />
              ))}
            </div>
          </section>

          {/* Common Mistakes */}
          <section id="common-mistakes">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.commonMistakes.title}</h2>
            <p className="mb-8 text-text-secondary">{blogDict.sections.commonMistakes.intro}</p>
            <div className="space-y-4">
              {blogDict.sections.commonMistakes.mistakes.map((mistake, idx) => (
                <MistakeCard key={idx} mistake={mistake} />
              ))}
            </div>
          </section>

          {/* Advanced Tips */}
          <section id="advanced-tips">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.advancedTips.title}</h2>
            <p className="mb-8 text-text-secondary">{blogDict.sections.advancedTips.intro}</p>
            <div className="space-y-4">
              {blogDict.sections.advancedTips.tips.map((tip, idx) => (
                <TipCard key={idx} tip={tip} />
              ))}
            </div>
          </section>

          {/* FAQ */}
          <section id="faq">
            <h2 className="mb-6 font-display text-3xl font-bold">{blogDict.sections.faq.title}</h2>
            <div className="space-y-4">
              {blogDict.sections.faq.items.map((item, idx) => (
                <FAQItem key={idx} item={item} />
              ))}
            </div>
          </section>

          {/* Related Articles */}
          <section className="border-t border-border-default pt-12">
            <h3 className="mb-6 font-display text-2xl font-bold">{blogDict.relatedArticles.label}</h3>
            <div className="grid gap-4 sm:grid-cols-2">
              {blogDict.relatedArticles.articles.map((article, idx) => (
                <div
                  key={idx}
                  className="rounded-lg border border-border-default bg-bg-secondary p-5 hover:border-accent transition-colors"
                >
                  <h4 className="mb-2 font-semibold text-text-primary">{article.title}</h4>
                  <p className="mb-3 text-sm text-text-secondary">{article.description}</p>
                  <Link href={article.url} className="text-sm text-accent hover:underline">
                    Read article →
                  </Link>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Final CTA */}
        <section className="mt-16 rounded-lg border border-accent bg-gradient-to-r from-accent/10 to-accent-hover/10 p-8 sm:p-12">
          <h2 className="mb-4 font-display text-2xl font-bold">{blogDict.sections.cta.title}</h2>
          <p className="mb-6 text-text-secondary">{blogDict.sections.cta.description}</p>
          <Link
            href={`/${lang}#download`}
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 font-semibold text-bg-primary hover:bg-accent-hover transition-colors"
          >
            {blogDict.sections.cta.buttonText}
            <span>→</span>
          </Link>
        </section>
      </div>
    </article>
  )
}

/* ============================================================================
   Components
   ============================================================================ */

function TableOfContents({
  items,
  lang,
  label,
  isOpen,
  onToggle,
}: {
  items: Array<{ id: string; title: string }>
  lang: string
  label: string
  isOpen: boolean
  onToggle: (val: boolean) => void
}) {
  return (
    <nav className="sticky top-0 z-40 border-b border-border-default bg-bg-primary/95 backdrop-blur-sm">
      <div className="mx-auto max-w-4xl px-4 py-4 sm:px-6 lg:px-8">
        <button
          onClick={() => onToggle(!isOpen)}
          className="mb-3 inline-flex w-full items-center justify-between rounded-lg border border-border-default bg-bg-secondary p-3 sm:hidden"
        >
          <span className="font-semibold">{label}</span>
          <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>▼</span>
        </button>

        <div className={`${isOpen ? 'block' : 'hidden'} sm:block`}>
          <div className="hidden text-sm sm:grid sm:auto-cols-fr sm:grid-flow-col sm:gap-1">
            {items.map((item: any) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className="rounded px-2 py-1 text-xs text-text-secondary hover:bg-bg-secondary hover:text-text-primary transition-colors"
              >
                {item.title}
              </a>
            ))}
          </div>
          <ul className="space-y-2 sm:hidden">
            {items.map((item: any) => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  className="block rounded px-3 py-2 text-sm text-text-secondary hover:bg-bg-secondary hover:text-text-primary transition-colors"
                  onClick={() => onToggle(false)}
                >
                  {item.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </nav>
  )
}

function BenefitCard({
  item,
}: {
  item: { title: string; description: string; metric: string }
}) {
  return (
    <div className="rounded-lg border border-border-default bg-bg-secondary p-6 hover:border-accent transition-colors">
      <div className="mb-3 text-3xl font-bold text-accent">{item.metric}</div>
      <h3 className="mb-2 font-semibold text-text-primary">{item.title}</h3>
      <p className="text-sm text-text-secondary">{item.description}</p>
    </div>
  )
}

function StepCard({
  step,
}: {
  step: { num: string; title: string; description: string; tips?: string[] }
}) {
  return (
    <div className="rounded-lg border border-border-default bg-bg-secondary p-6">
      <div className="mb-4 flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent font-bold text-bg-primary">
          {step.num}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-text-primary">{step.title}</h3>
          <p className="mt-2 text-text-secondary">{step.description}</p>
          {step.tips && (
            <ul className="mt-4 space-y-2">
              {step.tips.map((tip, idx) => (
                <li key={idx} className="flex gap-2 text-sm text-text-secondary">
                  <span className="shrink-0">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

function PracticeCard({
  practice,
}: {
  practice: { title: string; description: string; icon: string }
}) {
  return (
    <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
      <div className="mb-2 text-2xl">{practice.icon}</div>
      <h3 className="mb-2 font-semibold text-text-primary">{practice.title}</h3>
      <p className="text-sm text-text-secondary">{practice.description}</p>
    </div>
  )
}

function MistakeCard({
  mistake,
}: {
  mistake: { title: string; description: string; solution: string }
}) {
  return (
    <div className="rounded-lg border-l-4 border-l-accent/50 bg-accent-dim/10 p-4">
      <div className="font-semibold text-accent-dim">{mistake.title}</div>
      <p className="mt-1 text-sm text-text-secondary">{mistake.description}</p>
      <div className="mt-2 flex items-start gap-2 text-sm">
        <span className="shrink-0 font-semibold text-accent">Fix:</span>
        <span className="text-accent/80">{mistake.solution}</span>
      </div>
    </div>
  )
}

function TipCard({ tip }: { tip: { title: string; description: string } }) {
  return (
    <div className="rounded-lg border-l-4 border-l-accent bg-accent/10 p-4">
      <div className="font-semibold text-accent">{tip.title}</div>
      <p className="mt-1 text-sm text-text-secondary">{tip.description}</p>
    </div>
  )
}

function FAQItem({ item }: { item: { q: string; a: string } }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="rounded-lg border border-border-default overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-bg-secondary p-4 text-left font-semibold hover:bg-bg-secondary/80 transition-colors flex items-center justify-between"
      >
        <span>{item.q}</span>
        <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>▼</span>
      </button>
      {isOpen && (
        <div className="border-t border-border-default bg-bg-primary/50 p-4 text-text-secondary">
          {item.a}
        </div>
      )}
    </div>
  )
}
