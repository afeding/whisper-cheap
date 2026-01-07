import Link from 'next/link'
import type { Locale } from '@/dictionaries'

interface FooterProps {
  lang: Locale
}

export function Footer({ lang }: FooterProps) {
  const isSpanish = lang === 'es'
  const otherLang: Locale = lang === 'en' ? 'es' : 'en'

  const sections = {
    product: {
      title: isSpanish ? 'Producto' : 'Product',
      links: [
        { href: `/${lang}`, label: isSpanish ? 'Inicio' : 'Home' },
        { href: `/${lang}/features/offline`, label: isSpanish ? 'Offline' : 'Offline' },
        { href: `/${lang}/features/privacy`, label: isSpanish ? 'Privacidad' : 'Privacy' },
        {
          href: 'https://github.com/afeding/whisper-cheap/releases',
          label: isSpanish ? 'Descargar' : 'Download',
          external: true,
        },
      ],
    },
    useCases: {
      title: isSpanish ? 'Casos de Uso' : 'Use Cases',
      links: [
        { href: `/${lang}/use-cases/writers`, label: isSpanish ? 'Escritores' : 'Writers' },
        { href: `/${lang}/use-cases/developers`, label: isSpanish ? 'Desarrolladores' : 'Developers' },
        { href: `/${lang}/use-cases/lawyers`, label: isSpanish ? 'Abogados' : 'Lawyers' },
        { href: `/${lang}/use-cases/students`, label: isSpanish ? 'Estudiantes' : 'Students' },
      ],
    },
    comparisons: {
      title: isSpanish ? 'Comparaciones' : 'Comparisons',
      links: [
        { href: `/${lang}/vs/wispr-flow`, label: 'vs Wispr Flow' },
        { href: `/${lang}/vs/dragon`, label: 'vs Dragon' },
      ],
    },
    resources: {
      title: isSpanish ? 'Recursos' : 'Resources',
      links: [
        { href: `/${lang}/blog`, label: 'Blog' },
        {
          href: 'https://github.com/afeding/whisper-cheap',
          label: 'GitHub',
          external: true,
        },
        {
          href: 'https://github.com/afeding/whisper-cheap/issues',
          label: isSpanish ? 'Reportar Bug' : 'Report Bug',
          external: true,
        },
        {
          href: 'https://github.com/afeding/whisper-cheap/blob/master/README.md',
          label: isSpanish ? 'Documentación' : 'Documentation',
          external: true,
        },
      ],
    },
  }

  return (
    <footer className="bg-slate-900 text-white">
      {/* Organization Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'Whisper Cheap',
            url: 'https://whispercheap.com',
            logo: 'https://whispercheap.com/icon.svg',
            description: isSpanish
              ? 'Software gratuito de dictado por IA para Windows. Transcripción local de voz a texto 100% offline.'
              : 'Free AI dictation software for Windows. 100% offline local voice-to-text transcription.',
            sameAs: [
              'https://github.com/afeding/whisper-cheap',
            ],
            contactPoint: {
              '@type': 'ContactPoint',
              contactType: 'Customer Support',
              url: 'https://github.com/afeding/whisper-cheap/issues',
            },
          }),
        }}
      />

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          {Object.entries(sections).map(([key, section]) => (
            <div key={key}>
              <h3 className="font-semibold text-sm uppercase tracking-wider mb-4 text-slate-300">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.links.map((link: any) =>
                  link.external ? (
                    <li key={link.href}>
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-400 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </a>
                    </li>
                  ) : (
                    <li key={link.href}>
                      <Link
                        href={link.href}
                        className="text-slate-400 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </Link>
                    </li>
                  )
                )}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-slate-400 text-sm">
            © {new Date().getFullYear()} Whisper Cheap.{' '}
            {isSpanish ? 'Código abierto bajo licencia MIT' : 'Open source under MIT license'}.
          </div>

          <div className="flex items-center gap-6">
            {/* Language Switcher */}
            <Link
              href={`/${otherLang}`}
              className="text-slate-400 hover:text-white transition-colors text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                />
              </svg>
              {otherLang === 'en' ? 'English' : 'Español'}
            </Link>

            {/* Social Links */}
            <a
              href="https://github.com/afeding/whisper-cheap"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition-colors"
              aria-label="GitHub"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
