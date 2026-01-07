'use client'

import { useEffect, useState, useRef } from 'react'
import { type Locale } from '@/dictionaries'
import Link from 'next/link'

// === CONSTANTES ===
const GITHUB_OWNER = 'afeding'
const GITHUB_REPO = 'whisper-cheap'
const DOWNLOAD_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest/download/WhisperCheapSetup.exe`
const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`
const RELEASES_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases`

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
      typing: string
      speaking: string
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
      q5: string; a5: string
      q6: string; a6: string
    }
    cta: { title: string; button: string }
    footer: { tagline: string; github: string; releases: string }
  }
  lang: Locale
}

export function LandingPage({ dict, lang }: LandingPageProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary bg-noise">
      {/* Gradiente superior decorativo */}
      <div className="fixed inset-0 bg-gradient-radial pointer-events-none" />

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href={`/${lang}`} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
              <MicIcon className="w-4 h-4 text-accent" />
            </div>
            <span className="font-display font-semibold text-lg tracking-tight">Whisper Cheap</span>
          </a>

          <div className="flex items-center gap-2">
            {/* GitHub link */}
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2.5 rounded-lg text-text-dim hover:text-text-secondary hover:bg-bg-elevated transition-all"
              aria-label="GitHub"
            >
              <GitHubIcon className="w-5 h-5" />
            </a>

            {/* Language switcher con icono */}
            <a
              href={`/${otherLang}`}
              className="p-2.5 rounded-lg text-text-dim hover:text-text-secondary hover:bg-bg-elevated transition-all flex items-center gap-1.5"
              aria-label={`Switch to ${otherLang === 'en' ? 'English' : 'Spanish'}`}
            >
              <GlobeIcon className="w-5 h-5" />
              <span className="text-xs font-medium uppercase">{otherLang}</span>
            </a>

            {/* Download CTA */}
            <a
              href={DOWNLOAD_URL}
              className="ml-2 btn-glow inline-flex items-center gap-2 bg-accent text-bg-primary font-semibold px-5 py-2.5 rounded-full hover:bg-accent-hover transition-all text-sm"
            >
              <DownloadIcon className="w-4 h-4" />
              {dict.nav.download}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero - 2 columnas en desktop */}
      <section className="relative pt-24 pb-12 px-6 overflow-hidden">
        {/* Grid pattern decorativo */}
        <div className="absolute inset-0 grid-pattern opacity-50" />

        <div className="relative max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Columna izquierda: Contenido */}
            <div>
              {/* Badge */}
              <div className="animate-fade-in-up">
                <span className="badge-glow inline-flex items-center gap-2 text-accent text-sm font-medium px-4 py-1.5 rounded-full mb-6">
                  <SparklesIcon className="w-3.5 h-3.5" />
                  {dict.hero.tagline}
                </span>
              </div>

              {/* Título principal */}
              <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold leading-[0.95] tracking-tight mb-6">
                <span className="block animate-fade-in-up animate-delay-100">{dict.hero.title1}</span>
                <span className="block text-accent animate-fade-in-up animate-delay-200">{dict.hero.title2}</span>
              </h1>

              {/* Subtítulo */}
              <p className="text-lg text-text-secondary max-w-xl leading-relaxed mb-8 animate-fade-in-up animate-delay-300">
                {dict.hero.subtitle}
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row items-start gap-4 animate-fade-in-up animate-delay-400">
                <a
                  href={DOWNLOAD_URL}
                  className="btn-glow group inline-flex items-center gap-2.5 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
                >
                  <WindowsIcon className="w-5 h-5" />
                  {dict.hero.cta}
                  <ArrowDownIcon className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" />
                </a>
                <div className="flex items-center gap-3 text-text-dim text-sm pt-3 sm:pt-4">
                  <CheckIcon className="w-4 h-4 text-accent" />
                  <span>{dict.hero.note}</span>
                </div>
              </div>
            </div>

            {/* Columna derecha: Demo */}
            <div className="animate-fade-in-up animate-delay-500">
              <ProductDemo dict={dict} />
            </div>
          </div>
        </div>
      </section>

      {/* Velocidad - Visual comparison */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-2xl sm:text-3xl font-bold mb-12 text-center">
            {dict.problem.title}
          </h2>

          <div className="space-y-6">
            {/* Typing bar */}
            <div className="flex items-center gap-4">
              <div className="w-24 text-right">
                <span className="text-text-dim text-sm">{dict.problem.typing}</span>
              </div>
              <div className="flex-1 h-12 bg-bg-card rounded-lg overflow-hidden relative">
                <div className="h-full bg-text-dim/30 rounded-lg" style={{ width: '27%' }} />
                <div className="absolute inset-y-0 left-0 flex items-center pl-4">
                  <KeyboardIcon className="w-5 h-5 text-text-dim mr-2" />
                  <span className="font-display font-bold text-text-dim">{dict.problem.stat1}</span>
                  <span className="text-text-dim/60 text-sm ml-1">{dict.problem.stat1Label}</span>
                </div>
              </div>
            </div>

            {/* Speaking bar */}
            <div className="flex items-center gap-4">
              <div className="w-24 text-right">
                <span className="text-accent text-sm font-medium">{dict.problem.speaking}</span>
              </div>
              <div className="flex-1 h-12 bg-bg-card rounded-lg overflow-hidden relative">
                <div className="h-full bg-accent/20 rounded-lg" style={{ width: '100%' }} />
                <div className="absolute inset-y-0 left-0 flex items-center pl-4">
                  <MicIcon className="w-5 h-5 text-accent mr-2" />
                  <span className="font-display font-bold text-accent">{dict.problem.stat2}</span>
                  <span className="text-accent/60 text-sm ml-1">{dict.problem.stat2Label}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Por qué existe */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16">
            {dict.whyThis.title}
          </h2>

          <div className="space-y-10">
            {[
              { title: dict.whyThis.reason1Title, desc: dict.whyThis.reason1Desc, color: 'bg-red-500' },
              { title: dict.whyThis.reason2Title, desc: dict.whyThis.reason2Desc, color: 'bg-orange-500' },
              { title: dict.whyThis.reason3Title, desc: dict.whyThis.reason3Desc, color: 'bg-yellow-500' },
            ].map((item, i) => (
              <div key={i} className="flex gap-4">
                <div className={`w-1 ${item.color} rounded-full flex-shrink-0`} />
                <div>
                  <h3 className="font-display font-semibold text-lg mb-2">{item.title}</h3>
                  <p className="text-text-secondary leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-14 p-6 sm:p-8 bg-bg-card rounded-2xl border border-border-default">
            <p className="text-text-primary leading-relaxed">
              {dict.whyThis.conclusion}
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: ShieldIcon, ...dict.features.local },
              { icon: BoltIcon, ...dict.features.fast },
              { icon: KeyIcon, ...dict.features.simple },
            ].map((feature, i) => (
              <div
                key={i}
                className="group p-6 rounded-2xl bg-bg-card border border-border-default hover:border-border-hover transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5 group-hover:bg-accent/15 transition-colors">
                  <feature.icon className="w-6 h-6 text-accent" />
                </div>
                <h3 className="font-display font-semibold text-xl mb-3">{feature.title}</h3>
                <p className="text-text-secondary leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-16 text-center">
            {dict.howItWorks.title}
          </h2>

          <div className="space-y-8">
            {[
              { num: '1', title: dict.howItWorks.step1, desc: dict.howItWorks.step1Desc },
              { num: '2', title: dict.howItWorks.step2, desc: dict.howItWorks.step2Desc },
              { num: '3', title: dict.howItWorks.step3, desc: dict.howItWorks.step3Desc },
            ].map((step, i) => (
              <div key={i} className="flex gap-5 items-start">
                <div className="w-10 h-10 rounded-full bg-accent text-bg-primary font-display font-bold flex items-center justify-center flex-shrink-0">
                  {step.num}
                </div>
                <div className="pt-1">
                  <h3 className="font-display font-semibold text-lg mb-1">{step.title}</h3>
                  <p className="text-text-secondary">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Founder Quote */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="relative">
            <QuoteIcon className="absolute -top-4 -left-2 w-12 h-12 text-accent/20" />
            <blockquote className="text-xl sm:text-2xl leading-relaxed text-text-primary mb-8 pl-6">
              {dict.founder.quote}
            </blockquote>
          </div>
          <div className="flex items-center gap-4 pl-6">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-accent to-accent-dim flex items-center justify-center text-bg-primary font-display font-bold text-lg">
              A
            </div>
            <div>
              <div className="font-display font-semibold">{dict.founder.name}</div>
              <div className="text-sm text-text-secondary">{dict.founder.role}</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-2xl mx-auto">
          <h2 className="font-display text-3xl sm:text-4xl font-bold mb-12 text-center">
            {dict.faq.title}
          </h2>

          <div className="space-y-8">
            {[
              { q: dict.faq.q1, a: dict.faq.a1 },
              { q: dict.faq.q2, a: dict.faq.a2 },
              { q: dict.faq.q3, a: dict.faq.a3 },
              { q: dict.faq.q4, a: dict.faq.a4 },
              { q: dict.faq.q5, a: dict.faq.a5 },
              { q: dict.faq.q6, a: dict.faq.a6 },
            ].map((item, i) => (
              <div key={i} className="border-b border-border-default pb-6 last:border-0">
                <h3 className="font-display font-semibold text-lg mb-2">{item.q}</h3>
                <p className="text-text-secondary leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Resources & Links Section */}
      <section className="py-24 px-6 bg-bg-secondary">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-text-primary mb-4">
              {lang === 'es' ? 'Más Recursos' : 'Learn More'}
            </h2>
            <p className="text-xl text-text-secondary">
              {lang === 'es'
                ? 'Guías, comparaciones y casos de uso para maximizar tu productividad'
                : 'Guides, comparisons, and use cases to maximize your productivity'}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Blog & Guides */}
            <div className="bg-bg-card p-6 rounded-lg border border-border-default hover:border-border-hover transition-all">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-display font-semibold text-text-primary mb-2">
                {lang === 'es' ? 'Guías y Tutoriales' : 'Guides & Tutorials'}
              </h3>
              <p className="text-text-secondary mb-4">
                {lang === 'es'
                  ? 'Aprende consejos y mejores prácticas para dictado por IA'
                  : 'Learn tips and best practices for AI dictation'}
              </p>
              <Link
                href={`/${lang}/blog`}
                className="text-accent font-medium hover:text-accent/80 inline-flex items-center gap-1"
              >
                {lang === 'es' ? 'Ver Blog' : 'View Blog'}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {/* Use Cases */}
            <div className="bg-bg-card p-6 rounded-lg border border-border-default hover:border-border-hover transition-all">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-display font-semibold text-text-primary mb-2">
                {lang === 'es' ? 'Casos de Uso' : 'Use Cases'}
              </h3>
              <p className="text-text-secondary mb-4">
                {lang === 'es'
                  ? 'Descubre cómo escritores, desarrolladores y abogados usan Whisper Cheap'
                  : 'See how writers, developers, and lawyers use Whisper Cheap'}
              </p>
              <div className="space-y-2">
                <Link href={`/${lang}/use-cases/writers`} className="block text-accent hover:text-accent/80">
                  {lang === 'es' ? '→ Para Escritores' : '→ For Writers'}
                </Link>
                <Link href={`/${lang}/use-cases/developers`} className="block text-accent hover:text-accent/80">
                  {lang === 'es' ? '→ Para Desarrolladores' : '→ For Developers'}
                </Link>
                <Link href={`/${lang}/use-cases/lawyers`} className="block text-accent hover:text-accent/80">
                  {lang === 'es' ? '→ Para Abogados' : '→ For Lawyers'}
                </Link>
              </div>
            </div>

            {/* Comparisons */}
            <div className="bg-bg-card p-6 rounded-lg border border-border-default hover:border-border-hover transition-all">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-display font-semibold text-text-primary mb-2">
                {lang === 'es' ? 'Comparaciones' : 'Comparisons'}
              </h3>
              <p className="text-text-secondary mb-4">
                {lang === 'es'
                  ? 'Compara Whisper Cheap con otras herramientas de dictado'
                  : 'Compare Whisper Cheap with other dictation tools'}
              </p>
              <div className="space-y-2">
                <Link href={`/${lang}/vs/wispr-flow`} className="block text-accent hover:text-accent/80">
                  {lang === 'es' ? '→ vs Wispr Flow' : '→ vs Wispr Flow'}
                </Link>
                <Link href={`/${lang}/vs/dragon`} className="block text-accent hover:text-accent/80">
                  {lang === 'es' ? '→ vs Dragon' : '→ vs Dragon'}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section id="download" className="py-32 px-6">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-bold mb-8">
            {dict.cta.title}
          </h2>
          <a
            href={DOWNLOAD_URL}
            className="btn-glow group inline-flex items-center gap-3 bg-accent text-bg-primary font-semibold px-8 py-4 rounded-full hover:bg-accent-hover transition-all text-lg"
          >
            <WindowsIcon className="w-5 h-5" />
            {dict.cta.button}
            <ArrowDownIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-border-default">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5 text-text-dim">
            <MicIcon className="w-4 h-4 text-accent" />
            <span className="text-sm">{dict.footer.tagline}</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a
              href={GITHUB_URL}
              className="text-text-dim hover:text-text-secondary transition-colors link-underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {dict.footer.github}
            </a>
            <a
              href={RELEASES_URL}
              className="text-text-dim hover:text-text-secondary transition-colors link-underline"
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

// === DEMO COMPONENT - Animación cinematográfica ===
function ProductDemo({ dict }: { dict: LandingPageProps['dict'] }) {
  const [phase, setPhase] = useState<'idle' | 'recording' | 'processing' | 'done'>('idle')
  const [displayText, setDisplayText] = useState('')
  const [audioLevel, setAudioLevel] = useState<number[]>(Array(30).fill(0.1))
  const animationRef = useRef<number>()

  useEffect(() => {
    const sequence = async () => {
      // Reset
      setPhase('idle')
      setDisplayText('')
      await sleep(1800)

      // Recording con audio reactivo
      setPhase('recording')

      // Simular niveles de audio cambiantes - más rápido y fluido
      let frame = 0
      const animateAudio = () => {
        const levels = Array(30).fill(0).map((_, i) => {
          const center = 15
          const dist = Math.abs(i - center) / center
          const base = 1 - dist * 0.5
          const noise = Math.sin(frame * 0.2 + i * 0.4) * 0.4 + Math.random() * 0.25
          return Math.max(0.15, Math.min(1, base * (0.4 + noise)))
        })
        setAudioLevel(levels)
        frame++
        animationRef.current = requestAnimationFrame(animateAudio)
      }
      animateAudio()

      await sleep(2500)
      cancelAnimationFrame(animationRef.current!)

      // Processing breve
      setPhase('processing')
      await sleep(400)

      // Typewriter INSTANTÁNEO - como IA generando texto
      setPhase('done')
      const text = dict.demo.output
      const lines = text.split('\n')

      // Mostrar línea por línea muy rápido
      for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
        const currentText = lines.slice(0, lineIdx + 1).join('\n')
        setDisplayText(currentText)
        // Pausa breve entre líneas para efecto de "generación"
        await sleep(lines[lineIdx] === '' ? 30 : 80)
      }

      await sleep(4000)
    }

    sequence()
    const interval = setInterval(sequence, 16000)
    return () => {
      clearInterval(interval)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [dict.demo.output])

  return (
    <div className="card-border-gradient overflow-hidden glow-accent">
      {/* Header estilo terminal */}
      <div className="flex items-center gap-2 px-5 py-3.5 bg-bg-elevated/50 border-b border-border-default">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
          <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
          <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
        </div>
        <div className="flex-1 text-center">
          <span className="text-xs text-text-dim font-mono">Whisper Cheap</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-8 sm:p-10 min-h-[200px] flex flex-col justify-center bg-bg-card">
        {phase === 'idle' && (
          <div className="flex items-center gap-3 text-text-secondary animate-fade-in-up">
            <span className="text-sm">{dict.demo.press}</span>
            <div className="flex items-center gap-1">
              <kbd className="px-2.5 py-1.5 bg-bg-elevated rounded-md text-xs font-mono text-accent border border-border-default">
                Ctrl
              </kbd>
              <span className="text-text-dim text-xs">+</span>
              <kbd className="px-2.5 py-1.5 bg-bg-elevated rounded-md text-xs font-mono text-accent border border-border-default">
                Space
              </kbd>
            </div>
          </div>
        )}

        {phase === 'recording' && (
          <div className="space-y-5 animate-fade-in-up">
            <div className="flex items-center gap-2.5">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse-soft" />
              <span className="text-sm text-text-secondary">{dict.demo.recording}</span>
            </div>
            <AudioWaveform levels={audioLevel} />
          </div>
        )}

        {phase === 'processing' && (
          <div className="flex items-center gap-3 animate-fade-in-up">
            <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-text-secondary">Processing...</span>
          </div>
        )}

        {phase === 'done' && (
          <div className="font-mono text-sm animate-fade-in-up whitespace-pre-wrap">
            <span className="text-accent">{">"}</span>
            <span className="text-text-primary ml-2">{displayText}</span>
            <span className="text-accent animate-blink">|</span>
          </div>
        )}
      </div>
    </div>
  )
}

// === AUDIO WAVEFORM - Más fluido y orgánico ===
function AudioWaveform({ levels }: { levels: number[] }) {
  return (
    <div className="flex items-center justify-center gap-[3px] h-12">
      {levels.map((level, i) => (
        <div
          key={i}
          className="w-[3px] rounded-full bg-accent transition-all duration-75"
          style={{
            height: `${level * 100}%`,
            opacity: 0.4 + level * 0.6,
          }}
        />
      ))}
    </div>
  )
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// === ICONS ===
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

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
    </svg>
  )
}

function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
    </svg>
  )
}

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  )
}

function ArrowDownIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  )
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  )
}

function BoltIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
  )
}

function KeyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z" />
    </svg>
  )
}

function QuoteIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
    </svg>
  )
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 22.5l-.394-1.933a2.25 2.25 0 00-1.423-1.423L12.75 18.75l1.933-.394a2.25 2.25 0 001.423-1.423l.394-1.933.394 1.933a2.25 2.25 0 001.423 1.423l1.933.394-1.933.394a2.25 2.25 0 00-1.423 1.423z" />
    </svg>
  )
}

function KeyboardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 3.75H6A2.25 2.25 0 003.75 6v1.5M16.5 3.75H18A2.25 2.25 0 0120.25 6v1.5m0 9V18A2.25 2.25 0 0118 20.25h-1.5m-9 0H6A2.25 2.25 0 013.75 18v-1.5M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}
