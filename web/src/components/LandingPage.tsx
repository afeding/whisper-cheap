'use client'

import { useEffect, useState } from 'react'
import { type Locale } from '@/dictionaries'

interface LandingPageProps {
  dict: {
    meta: { title: string; description: string; keywords: string }
    nav: { features: string; download: string }
    hero: {
      tagline: string
      title1: string
      title2: string
      subtitle: string
      cta: string
      note: string
    }
    demo: {
      press: string
      recording: string
      output: string
    }
    problem: {
      title: string
      stat1: string
      stat1Label: string
      stat2: string
      stat2Label: string
      description: string
      solution: string
    }
    whyThis: {
      title: string
      reason1Title: string
      reason1Desc: string
      reason2Title: string
      reason2Desc: string
      reason3Title: string
      reason3Desc: string
      conclusion: string
    }
    features: {
      local: { title: string; desc: string }
      fast: { title: string; desc: string }
      simple: { title: string; desc: string }
    }
    howItWorks: {
      title: string
      step1: string
      step1Desc: string
      step2: string
      step2Desc: string
      step3: string
      step3Desc: string
    }
    founder: {
      quote: string
      name: string
      role: string
    }
    faq: {
      title: string
      q1: string; a1: string
      q2: string; a2: string
      q3: string; a3: string
      q4: string; a4: string
    }
    cta: { title: string; button: string }
    footer: { tagline: string; github: string; releases: string }
  }
  lang: Locale
}

export function LandingPage({ dict, lang }: LandingPageProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'
  const otherLangLabel = lang === 'en' ? 'ES' : 'EN'

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e5e5e5]">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MicIcon className="w-7 h-7 text-[#00ff88]" />
            <span className="font-semibold text-lg">Whisper Cheap</span>
          </div>
          <div className="flex items-center gap-5">
            <a
              href={`/${otherLang}`}
              className="text-base text-[#666] hover:text-[#999] transition-colors"
            >
              {otherLangLabel}
            </a>
            <a
              href="#download"
              className="text-base font-semibold bg-[#00ff88] text-black px-5 py-2.5 rounded-full hover:bg-[#00dd77] transition-colors"
            >
              {dict.nav.download}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero - Big Statement */}
      <section className="pt-36 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-[#00ff88] text-base font-mono mb-6 tracking-wide">
            {dict.hero.tagline}
          </p>
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[0.9] tracking-tight mb-8">
            <span className="text-[#e5e5e5]">{dict.hero.title1}</span>
            <br />
            <span className="text-[#00ff88]">{dict.hero.title2}</span>
          </h1>
          <p className="text-xl sm:text-2xl text-[#888] max-w-xl leading-relaxed mb-12">
            {dict.hero.subtitle}
          </p>
          <div className="flex flex-col sm:flex-row items-start gap-4">
            <a
              href="#download"
              className="inline-flex items-center gap-3 bg-[#00ff88] text-black font-semibold px-8 py-4 rounded-full hover:bg-[#00dd77] transition-all hover:scale-[1.02] text-lg"
            >
              <WindowsIcon className="w-5 h-5" />
              {dict.hero.cta}
            </a>
            <p className="text-sm text-[#555] pt-3">
              {dict.hero.note}
            </p>
          </div>
        </div>
      </section>

      {/* Product Demo - Animated Waveform */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <ProductDemo dict={dict} />
        </div>
      </section>

      {/* Problem - Speed Comparison */}
      <section className="py-24 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold mb-16 text-center">
            {dict.problem.title}
          </h2>

          <div className="flex justify-center items-end gap-8 sm:gap-16 mb-12">
            <div className="text-center">
              <div className="text-6xl sm:text-8xl font-bold text-[#444] mb-2">
                {dict.problem.stat1}
              </div>
              <div className="text-sm sm:text-base text-[#555] uppercase tracking-wider">
                {dict.problem.stat1Label}
              </div>
            </div>
            <div className="text-center">
              <div className="text-6xl sm:text-8xl font-bold text-[#00ff88] mb-2">
                {dict.problem.stat2}
              </div>
              <div className="text-sm sm:text-base text-[#555] uppercase tracking-wider">
                {dict.problem.stat2Label}
              </div>
            </div>
          </div>

          <p className="text-lg text-[#888] text-center max-w-xl mx-auto leading-relaxed mb-6">
            {dict.problem.description}
          </p>
          <p className="text-[#00ff88] text-center font-medium text-xl">
            {dict.problem.solution}
          </p>
        </div>
      </section>

      {/* Why This Exists */}
      <section className="py-24 px-6 bg-[#0d0d0d]">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold mb-16">
            {dict.whyThis.title}
          </h2>

          <div className="space-y-12">
            <div className="border-l-2 border-[#ff4444] pl-6">
              <h3 className="font-semibold text-lg mb-2">{dict.whyThis.reason1Title}</h3>
              <p className="text-[#888] text-base leading-relaxed">{dict.whyThis.reason1Desc}</p>
            </div>
            <div className="border-l-2 border-[#ff8844] pl-6">
              <h3 className="font-semibold text-lg mb-2">{dict.whyThis.reason2Title}</h3>
              <p className="text-[#888] text-base leading-relaxed">{dict.whyThis.reason2Desc}</p>
            </div>
            <div className="border-l-2 border-[#ffaa44] pl-6">
              <h3 className="font-semibold text-lg mb-2">{dict.whyThis.reason3Title}</h3>
              <p className="text-[#888] text-base leading-relaxed">{dict.whyThis.reason3Desc}</p>
            </div>
          </div>

          <div className="mt-16 p-8 bg-[#0a0a0a] rounded-2xl border border-[#1a1a1a]">
            <p className="text-[#e5e5e5] text-lg leading-relaxed">
              {dict.whyThis.conclusion}
            </p>
          </div>
        </div>
      </section>

      {/* Features - Minimal */}
      <section id="features" className="py-24 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-12">
            <div>
              <div className="w-12 h-12 rounded-full bg-[#00ff88]/10 flex items-center justify-center mb-5">
                <ShieldIcon className="w-6 h-6 text-[#00ff88]" />
              </div>
              <h3 className="font-semibold text-xl mb-3">{dict.features.local.title}</h3>
              <p className="text-base text-[#888] leading-relaxed">{dict.features.local.desc}</p>
            </div>
            <div>
              <div className="w-12 h-12 rounded-full bg-[#00ff88]/10 flex items-center justify-center mb-5">
                <BoltIcon className="w-6 h-6 text-[#00ff88]" />
              </div>
              <h3 className="font-semibold text-xl mb-3">{dict.features.fast.title}</h3>
              <p className="text-base text-[#888] leading-relaxed">{dict.features.fast.desc}</p>
            </div>
            <div>
              <div className="w-12 h-12 rounded-full bg-[#00ff88]/10 flex items-center justify-center mb-5">
                <KeyIcon className="w-6 h-6 text-[#00ff88]" />
              </div>
              <h3 className="font-semibold text-xl mb-3">{dict.features.simple.title}</h3>
              <p className="text-base text-[#888] leading-relaxed">{dict.features.simple.desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Visual Steps */}
      <section className="py-24 px-6 bg-[#0d0d0d]">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold mb-16 text-center">
            {dict.howItWorks.title}
          </h2>

          <div className="space-y-10">
            <div className="flex gap-6 items-start">
              <div className="w-10 h-10 rounded-full bg-[#00ff88] text-black font-bold text-base flex items-center justify-center flex-shrink-0">
                1
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">{dict.howItWorks.step1}</h3>
                <p className="text-base text-[#888]">{dict.howItWorks.step1Desc}</p>
              </div>
            </div>
            <div className="flex gap-6 items-start">
              <div className="w-10 h-10 rounded-full bg-[#00ff88] text-black font-bold text-base flex items-center justify-center flex-shrink-0">
                2
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">{dict.howItWorks.step2}</h3>
                <p className="text-base text-[#888]">{dict.howItWorks.step2Desc}</p>
              </div>
            </div>
            <div className="flex gap-6 items-start">
              <div className="w-10 h-10 rounded-full bg-[#00ff88] text-black font-bold text-base flex items-center justify-center flex-shrink-0">
                3
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">{dict.howItWorks.step3}</h3>
                <p className="text-base text-[#888]">{dict.howItWorks.step3Desc}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Founder Quote */}
      <section className="py-24 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-3xl mx-auto">
          <blockquote className="text-xl sm:text-2xl leading-relaxed text-[#ccc] mb-10">
            "{dict.founder.quote}"
          </blockquote>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#00ff88] to-[#00aa55] flex items-center justify-center text-black font-bold text-xl">
              A
            </div>
            <div>
              <div className="font-semibold text-lg">{dict.founder.name}</div>
              <div className="text-base text-[#888]">{dict.founder.role}</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ - Minimal */}
      <section className="py-24 px-6 bg-[#0d0d0d]">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold mb-12 text-center">
            {dict.faq.title}
          </h2>

          <div className="space-y-10">
            <div>
              <h3 className="font-semibold text-lg mb-2">{dict.faq.q1}</h3>
              <p className="text-base text-[#888]">{dict.faq.a1}</p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">{dict.faq.q2}</h3>
              <p className="text-base text-[#888]">{dict.faq.a2}</p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">{dict.faq.q3}</h3>
              <p className="text-base text-[#888]">{dict.faq.a3}</p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">{dict.faq.q4}</h3>
              <p className="text-base text-[#888]">{dict.faq.a4}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section id="download" className="py-32 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="text-4xl sm:text-5xl font-bold mb-8">
            {dict.cta.title}
          </h2>
          <a
            href="https://github.com/user/whisper-cheap/releases/latest"
            className="inline-flex items-center gap-3 bg-[#00ff88] text-black font-semibold px-8 py-4 rounded-full hover:bg-[#00dd77] transition-all hover:scale-[1.02] text-lg"
          >
            <WindowsIcon className="w-5 h-5" />
            {dict.cta.button}
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-[#1a1a1a]">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-base text-[#555]">
            <MicIcon className="w-5 h-5 text-[#00ff88]" />
            <span>{dict.footer.tagline}</span>
          </div>
          <div className="flex items-center gap-6 text-base">
            <a
              href="https://github.com/user/whisper-cheap"
              className="text-[#555] hover:text-[#888] transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {dict.footer.github}
            </a>
            <a
              href="https://github.com/user/whisper-cheap/releases"
              className="text-[#555] hover:text-[#888] transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {dict.footer.releases}
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Animated Product Demo Component
function ProductDemo({ dict }: { dict: LandingPageProps['dict'] }) {
  const [phase, setPhase] = useState<'idle' | 'recording' | 'done'>('idle')
  const [displayText, setDisplayText] = useState('')

  useEffect(() => {
    const sequence = async () => {
      // Idle
      setPhase('idle')
      setDisplayText('')
      await sleep(2000)

      // Recording
      setPhase('recording')
      await sleep(3000)

      // Done - typewriter effect
      setPhase('done')
      const text = dict.demo.output
      for (let i = 0; i <= text.length; i++) {
        setDisplayText(text.slice(0, i))
        await sleep(30)
      }
      await sleep(3000)
    }

    sequence()
    const interval = setInterval(sequence, 10000)
    return () => clearInterval(interval)
  }, [dict.demo.output])

  return (
    <div className="bg-[#111] rounded-2xl border border-[#222] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#222]">
        <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
        <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
        <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
      </div>

      {/* Content */}
      <div className="p-8 min-h-[220px] flex flex-col justify-center">
        {phase === 'idle' && (
          <div className="flex items-center gap-3 text-[#888]">
            <span className="text-base">{dict.demo.press}</span>
            <kbd className="px-3 py-1.5 bg-[#1a1a1a] rounded text-sm text-[#00ff88] border border-[#333]">
              Ctrl
            </kbd>
            <span className="text-sm">+</span>
            <kbd className="px-3 py-1.5 bg-[#1a1a1a] rounded text-sm text-[#00ff88] border border-[#333]">
              Space
            </kbd>
          </div>
        )}

        {phase === 'recording' && (
          <div className="flex flex-col gap-5">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
              <span className="text-base text-[#888]">{dict.demo.recording}</span>
            </div>
            <Waveform />
          </div>
        )}

        {phase === 'done' && (
          <div className="font-mono text-base">
            <span className="text-[#00ff88]">→ </span>
            <span className="text-[#e5e5e5]">{displayText}</span>
            <span className="animate-blink">|</span>
          </div>
        )}
      </div>
    </div>
  )
}

// Animated Waveform - matches the app's overlay
function Waveform() {
  const bars = 18

  return (
    <div className="flex items-center justify-center gap-[3px] h-8">
      {Array.from({ length: bars }).map((_, i) => {
        const center = (bars - 1) / 2
        const distance = Math.abs(i - center) / center
        const baseHeight = 1 - distance * 0.7

        return (
          <div
            key={i}
            className="w-[3px] rounded-full bg-[#00ff88]"
            style={{
              height: `${baseHeight * 100}%`,
              animation: `waveform 0.8s ease-in-out infinite`,
              animationDelay: `${i * 0.05}s`,
            }}
          />
        )
      })}
    </div>
  )
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Icons
function MicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
    </svg>
  )
}

function WindowsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" />
    </svg>
  )
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  )
}

function BoltIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  )
}

function KeyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
  )
}
