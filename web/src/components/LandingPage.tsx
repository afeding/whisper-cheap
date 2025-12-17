'use client'

import { type Locale } from '@/dictionaries'

interface LandingPageProps {
  dict: {
    meta: { title: string; description: string; keywords: string }
    nav: { features: string; howItWorks: string; download: string }
    hero: {
      badge: string
      title: string
      titleHighlight: string
      subtitle: string
      cta: string
      ctaSecondary: string
      free: string
    }
    features: {
      title: string
      subtitle: string
      local: { title: string; description: string }
      fast: { title: string; description: string }
      free: { title: string; description: string }
      hotkey: { title: string; description: string }
      vad: { title: string; description: string }
      llm: { title: string; description: string }
    }
    howItWorks: {
      title: string
      subtitle: string
      step1: { number: string; title: string; description: string }
      step2: { number: string; title: string; description: string }
      step3: { number: string; title: string; description: string }
    }
    useCases: { title: string; items: string[] }
    cta: { title: string; subtitle: string; button: string; note: string }
    footer: { madeWith: string; by: string; github: string; releases: string }
  }
  lang: Locale
}

export function LandingPage({ dict, lang }: LandingPageProps) {
  const otherLang = lang === 'en' ? 'es' : 'en'
  const otherLangLabel = lang === 'en' ? 'ES' : 'EN'

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-md border-b border-border-default">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MicIcon className="w-7 h-7 text-accent" />
            <span className="font-semibold text-text-primary">Whisper Cheap</span>
          </div>
          <div className="flex items-center gap-8">
            <a href="#features" className="text-sm text-text-secondary hover:text-text-primary transition-colors animated-underline">
              {dict.nav.features}
            </a>
            <a href="#how-it-works" className="text-sm text-text-secondary hover:text-text-primary transition-colors animated-underline">
              {dict.nav.howItWorks}
            </a>
            <a
              href={`/${otherLang}`}
              className="text-sm text-text-dim hover:text-text-secondary transition-colors px-2 py-1 rounded border border-border-default hover:border-border-hover"
            >
              {otherLangLabel}
            </a>
            <a
              href="#download"
              className="text-sm font-semibold bg-accent text-black px-4 py-2 rounded-lg hover:bg-accent-hover transition-colors"
            >
              {dict.nav.download}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="animate-fade-in">
            <span className="inline-flex items-center gap-2 text-xs font-medium text-accent bg-accent/10 px-3 py-1.5 rounded-full border border-accent/20 mb-8">
              <span className="w-2 h-2 bg-accent rounded-full animate-pulse-accent" />
              {dict.hero.badge}
            </span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-text-primary mb-6 animate-fade-in-delay-1">
            {dict.hero.title}
            <br />
            <span className="text-accent">{dict.hero.titleHighlight}</span>
          </h1>

          <p className="text-xl text-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-delay-2">
            {dict.hero.subtitle}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-delay-3">
            <a
              href="#download"
              className="flex items-center gap-3 bg-accent text-black font-semibold px-8 py-4 rounded-xl hover:bg-accent-hover transition-all glow-accent hover:glow-accent-strong"
            >
              <WindowsIcon className="w-5 h-5" />
              {dict.hero.cta}
            </a>
            <a
              href="#how-it-works"
              className="flex items-center gap-2 text-text-secondary hover:text-text-primary px-6 py-4 rounded-xl border border-border-default hover:border-border-hover transition-all"
            >
              <PlayIcon className="w-5 h-5" />
              {dict.hero.ctaSecondary}
            </a>
          </div>

          <p className="text-sm text-text-dim mt-6 animate-fade-in-delay-3">
            {dict.hero.free}
          </p>
        </div>
      </section>

      {/* Demo Visual */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-bg-card rounded-2xl border border-border-default p-8 glow-accent">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <div className="font-mono text-sm">
              <div className="flex items-center gap-3 text-text-dim mb-4">
                <span className="text-accent">$</span>
                <span className="text-text-secondary">Press</span>
                <span className="bg-bg-input px-2 py-1 rounded text-accent border border-border-default">Ctrl</span>
                <span className="text-text-secondary">+</span>
                <span className="bg-bg-input px-2 py-1 rounded text-accent border border-border-default">Space</span>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-text-secondary">Recording...</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-accent">→</span>
                <span className="text-text-primary">
                  {lang === 'es'
                    ? '"Escribe el correo a Juan diciéndole que la reunión es mañana a las 10."'
                    : '"Write an email to John telling him the meeting is tomorrow at 10."'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-4">
              {dict.features.title}
            </h2>
            <p className="text-text-secondary text-lg">{dict.features.subtitle}</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<ShieldIcon className="w-6 h-6" />}
              title={dict.features.local.title}
              description={dict.features.local.description}
            />
            <FeatureCard
              icon={<BoltIcon className="w-6 h-6" />}
              title={dict.features.fast.title}
              description={dict.features.fast.description}
            />
            <FeatureCard
              icon={<GiftIcon className="w-6 h-6" />}
              title={dict.features.free.title}
              description={dict.features.free.description}
            />
            <FeatureCard
              icon={<KeyboardIcon className="w-6 h-6" />}
              title={dict.features.hotkey.title}
              description={dict.features.hotkey.description}
            />
            <FeatureCard
              icon={<WaveIcon className="w-6 h-6" />}
              title={dict.features.vad.title}
              description={dict.features.vad.description}
            />
            <FeatureCard
              icon={<SparklesIcon className="w-6 h-6" />}
              title={dict.features.llm.title}
              description={dict.features.llm.description}
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-6 bg-bg-secondary">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-4">
              {dict.howItWorks.title}
            </h2>
            <p className="text-text-secondary text-lg">{dict.howItWorks.subtitle}</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              number={dict.howItWorks.step1.number}
              title={dict.howItWorks.step1.title}
              description={dict.howItWorks.step1.description}
            />
            <StepCard
              number={dict.howItWorks.step2.number}
              title={dict.howItWorks.step2.title}
              description={dict.howItWorks.step2.description}
            />
            <StepCard
              number={dict.howItWorks.step3.number}
              title={dict.howItWorks.step3.title}
              description={dict.howItWorks.step3.description}
            />
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-12 text-center">
            {dict.useCases.title}
          </h2>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
            {dict.useCases.items.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-3 bg-bg-card rounded-xl border border-border-default p-4 card-hover"
              >
                <CheckIcon className="w-5 h-5 text-accent flex-shrink-0" />
                <span className="text-text-primary text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="download" className="py-20 px-6 bg-bg-secondary">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-4">
            {dict.cta.title}
          </h2>
          <p className="text-text-secondary text-lg mb-10">{dict.cta.subtitle}</p>

          <a
            href="https://github.com/user/whisper-cheap/releases/latest"
            className="inline-flex items-center gap-3 bg-accent text-black font-semibold px-10 py-5 rounded-xl hover:bg-accent-hover transition-all text-lg glow-accent hover:glow-accent-strong"
          >
            <WindowsIcon className="w-6 h-6" />
            {dict.cta.button}
          </a>

          <p className="text-sm text-text-dim mt-6">{dict.cta.note}</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-border-default">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <MicIcon className="w-5 h-5 text-accent" />
            <span className="text-text-secondary text-sm">
              {dict.footer.madeWith} <span className="text-accent">♥</span> {dict.footer.by}
            </span>
          </div>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/user/whisper-cheap"
              className="text-text-secondary hover:text-text-primary text-sm transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {dict.footer.github}
            </a>
            <a
              href="https://github.com/user/whisper-cheap/releases"
              className="text-text-secondary hover:text-text-primary text-sm transition-colors"
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

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-bg-card rounded-xl border border-border-default p-6 card-hover">
      <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center text-accent mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-secondary text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function StepCard({
  number,
  title,
  description,
}: {
  number: string
  title: string
  description: string
}) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-full bg-accent text-black font-bold text-2xl flex items-center justify-center mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-secondary text-sm">{description}</p>
    </div>
  )
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

function PlayIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
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

function GiftIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
    </svg>
  )
}

function KeyboardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  )
}

function WaveIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
    </svg>
  )
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  )
}
