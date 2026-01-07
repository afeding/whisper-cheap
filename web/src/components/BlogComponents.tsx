'use client'

import React from 'react'

/**
 * Reusable blog components for Whisper Cheap articles
 * Can be extracted to a separate package or component library
 */

interface TipCardProps {
  number: number
  title: string
  description: string
  proTipLabel: string
  example: string
}

export function TipCard({
  number,
  title,
  description,
  proTipLabel,
  example,
}: TipCardProps) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-blue-500/50 transition-colors">
      <div className="flex items-start gap-4 mb-3">
        <div className="bg-blue-500 text-white font-bold text-lg rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mt-0.5">
          {number}
        </div>
        <h3 className="text-2xl font-bold text-white leading-tight">
          {title}
        </h3>
      </div>

      <p className="text-slate-300 leading-relaxed mb-4 ml-12">
        {description}
      </p>

      <div className="bg-slate-700/50 border-l-4 border-blue-500 p-4 rounded-r ml-12">
        <p className="text-sm font-semibold text-blue-300 mb-2">
          {proTipLabel}
        </p>
        <p className="text-slate-300 text-sm">{example}</p>
      </div>
    </div>
  )
}

interface ChecklistProps {
  title: string
  items: string[]
}

export function InteractiveChecklist({ title, items }: ChecklistProps) {
  const [checkedItems, setCheckedItems] = React.useState<Set<number>>(
    new Set()
  )

  const toggleItem = (index: number) => {
    const newChecked = new Set(checkedItems)
    if (newChecked.has(index)) {
      newChecked.delete(index)
    } else {
      newChecked.add(index)
    }
    setCheckedItems(newChecked)
  }

  return (
    <section className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-lg p-8 my-14">
      <h2 className="text-2xl font-bold text-white mb-6">{title}</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {items.map((item, idx) => (
          <button
            key={idx}
            onClick={() => toggleItem(idx)}
            className="flex items-center gap-3 text-left hover:bg-blue-500/10 p-2 rounded transition-colors"
          >
            <input
              type="checkbox"
              checked={checkedItems.has(idx)}
              onChange={() => toggleItem(idx)}
              className="w-5 h-5 rounded border-slate-600 accent-blue-500 cursor-pointer"
              aria-label={item}
            />
            <span className="text-slate-300 group-hover:text-white transition-colors">
              {item}
            </span>
          </button>
        ))}
      </div>
    </section>
  )
}

interface FAQItem {
  q: string
  a: string
}

interface FAQProps {
  title: string
  items: FAQItem[]
}

export function FAQ({ title, items }: FAQProps) {
  return (
    <section className="mb-14">
      <h2 className="text-3xl font-bold mb-8 text-white">{title}</h2>
      <div className="space-y-4">
        {items.map((faq, idx) => (
          <details
            key={idx}
            className="group bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-blue-500/50 transition-colors"
          >
            <summary className="cursor-pointer flex items-center justify-between font-semibold text-white">
              <span>{faq.q}</span>
              <svg
                className="w-5 h-5 transition-transform group-open:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
              </svg>
            </summary>
            <p className="text-slate-300 mt-4">{faq.a}</p>
          </details>
        ))}
      </div>
    </section>
  )
}

interface CTAProps {
  title: string
  description: string
  buttonText: string
  buttonHref: string
}

export function CTASection({
  title,
  description,
  buttonText,
  buttonHref,
}: CTAProps) {
  return (
    <section className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-center">
      <h2 className="text-2xl font-bold text-white mb-3">{title}</h2>
      <p className="text-blue-100 mb-6">{description}</p>
      <a
        href={buttonHref}
        className="inline-block bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors"
      >
        {buttonText}
      </a>
    </section>
  )
}

interface BlogHeroProps {
  badge: string
  title: string
  subtitle: string
  readingTime: string
  date: string
}

export function BlogHero({
  badge,
  title,
  subtitle,
  readingTime,
  date,
}: BlogHeroProps) {
  return (
    <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-16 px-4 md:py-24">
      <div className="max-w-3xl mx-auto">
        <div className="inline-block bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm mb-4 border border-blue-500/30">
          {badge}
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
          {title}
        </h1>
        <p className="text-xl text-slate-300 mb-6">{subtitle}</p>
        <div className="flex flex-col sm:flex-row items-center gap-4 text-slate-400 text-sm">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.893 3.5a4.365 4.365 0 00-5.606 0l-.707.707.707-.707a4.365 4.365 0 000 6.172l.707.707-.707-.707a4.365 4.365 0 005.606 0l.707.707-.707-.707a4.365 4.365 0 000-6.172l-.707-.707.707.707zM12.6 9.55A3.365 3.365 0 008.05 5a3.365 3.365 0 104.55 4.55z" />
            </svg>
            {readingTime}
          </span>
          <span>•</span>
          <span>{date}</span>
        </div>
      </div>
    </section>
  )
}

interface CategorySectionProps {
  name: string
  description: string
  children: React.ReactNode
}

export function CategorySection({
  name,
  description,
  children,
}: CategorySectionProps) {
  return (
    <section className="mb-14">
      <h2 className="text-3xl font-bold mb-2 text-white">{name}</h2>
      <p className="text-slate-400 mb-8">{description}</p>
      <div className="space-y-8">{children}</div>
    </section>
  )
}

export function BlogIntro({ children }: { children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <div className="space-y-4 text-lg text-slate-300 leading-relaxed">
        {children}
      </div>
    </section>
  )
}

export function BlogFooter({
  backText,
  backHref,
}: {
  backText: string
  backHref: string
}) {
  return (
    <div className="mt-12 pt-8 border-t border-slate-700">
      <a
        href={backHref}
        className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2"
      >
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
            d="M15 19l-7-7 7-7"
          />
        </svg>
        {backText}
      </a>
    </div>
  )
}
