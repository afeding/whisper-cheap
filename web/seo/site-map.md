# Site Architecture Map - Whisper Cheap

## Current Structure

```
/
├── /en (homepage EN)
│   └── [purpose: main landing, download CTA]
└── /es (homepage ES)
    └── [purpose: main landing ES, download CTA]
```

## Architecture Notes

Sitio single-page (landing page). No hay hub/spoke porque es una app simple con un solo objetivo: descargas.

### Current Pages
| Route | Purpose | Target Keyword |
|-------|---------|----------------|
| /en | Landing EN | speech to text windows free |
| /es | Landing ES | voz a texto windows gratis |

## SEO Elements Mapping

### Per-Page Optimization

| Element | /en | /es |
|---------|-----|-----|
| H1 | "Stop typing. Start talking." | "Deja de teclear. Empieza a hablar." |
| Title | Whisper Cheap - Free Local Speech-to-Text for Windows | Whisper Cheap - Dictado por Voz Gratuito y Local para Windows |
| Meta Desc | Type 10x faster by just talking... | Escribe 10 veces mas rapido hablando... |
| Schema | SoftwareApplication + FAQPage | SoftwareApplication + FAQPage |

## Internal Linking

Sitio single-page - no aplica linking interno tradicional.

### External Links
| From | To | Purpose |
|------|-----|---------|
| Landing | GitHub | Source code, trust signal |
| Landing | Releases | Downloads, changelogs |

## Canonical Strategy

- /en canonical → /en
- /es canonical → /es
- x-default → /en
- Hreflang bidireccional OK

## Future Expansion (Optional)

Si se quiere expandir SEO:
```
/
├── /en
├── /es
├── /blog/
│   ├── /blog/voice-typing-tips/
│   ├── /blog/speech-to-text-comparison/
│   └── ...
└── /changelog/
```

No recomendado a corto plazo - landing simple es mejor para conversion.
