# Code Snippets & Reference

Quick reference for key implementations in the Writers page.

## 1. Page Route (page.tsx)

### Basic Structure
```typescript
import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { WritersPage } from '@/components/WritersPage'

export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const baseUrl = 'https://whispercheap.com'
  const writersData = dict.writers as any

  return {
    title: writersData.meta.title,
    description: writersData.meta.description,
    keywords: '...',
    // ... full metadata
  }
}
```

### Schema Markup Embedding
```typescript
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: writersData.meta.title,
      description: writersData.meta.description,
      author: {
        '@type': 'Organization',
        name: 'Whisper Cheap',
      },
      datePublished: '2025-01-03',
      dateModified: '2025-01-03',
      image: '/og-image.png',
      url: `https://whispercheap.com/${params.lang}/use-cases/writers`,
    }),
  }}
/>
```

### FAQPage Schema
```typescript
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: dict.faqWriters.q1,
          acceptedAnswer: {
            '@type': 'Answer',
            text: dict.faqWriters.a1,
          },
        },
        // ... more questions
      ],
    }),
  }}
/>
```

## 2. Client Component Structure

### Component Signature
```typescript
interface WritersPageProps {
  dict: {
    meta: { title: string; description: string }
    hero: { hook: string; subtitle: string; cta: string }
    problem: {
      title: string
      intro: string
      painPoint1: string
      painPoint1Desc: string
      // ... 4 pain points total
    }
    solution: { /* ... */ }
    whyWhisperCheap: { /* ... */ }
    workflows: { /* ... */ }
    tips: { /* ... */ }
    faqWriters: {
      title: string
      q1: string; a1: string
      // ... 6 Q&A pairs
    }
    cta: { title: string; subtitle: string; button: string }
  }
  lang: Locale
}
```

### Hero Section Pattern
```typescript
<section className="relative pt-32 pb-16 px-6 md:pt-48 md:pb-24">
  <div className="max-w-3xl mx-auto text-center space-y-6">
    {/* Badge */}
    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-medium">
      <span className="w-2 h-2 rounded-full bg-accent" />
      {lang === 'en' ? 'For Writers' : 'Para Escritores'}
    </div>

    {/* H1 */}
    <h1 className="text-5xl md:text-6xl font-display font-bold tracking-tight">
      {dict.hero.hook}
    </h1>

    {/* Subtitle */}
    <p className="text-xl text-text-secondary leading-relaxed">
      {dict.hero.subtitle}
    </p>

    {/* CTA */}
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
```

### 4-Item Grid Pattern
```typescript
<section className="relative py-20 px-6 bg-bg-secondary/50">
  <div className="max-w-5xl mx-auto">
    <h2 className="text-4xl md:text-5xl font-display font-bold mb-4 text-center">
      {dict.problem.title}
    </h2>

    <div className="grid md:grid-cols-2 gap-6">
      {/* Item 1 */}
      <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50 hover:border-accent/30 transition-colors">
        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
          <PencilIcon className="w-5 h-5 text-accent" />
        </div>
        <h3 className="font-semibold text-lg mb-2">{dict.problem.painPoint1}</h3>
        <p className="text-text-secondary">{dict.problem.painPoint1Desc}</p>
      </div>

      {/* Items 2-4 follow same pattern */}
    </div>
  </div>
</section>
```

### 3-Column Benefit Section
```typescript
<section className="relative py-20 px-6">
  <div className="max-w-5xl mx-auto">
    <h2 className="text-4xl md:text-5xl font-display font-bold mb-16 text-center">
      {dict.solution.title}
    </h2>

    <div className="grid md:grid-cols-3 gap-8">
      <div className="space-y-4">
        <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
          <CheckIcon className="w-6 h-6 text-accent" />
        </div>
        <h3 className="font-semibold text-xl">{dict.solution.benefit1Title}</h3>
        <p className="text-text-secondary leading-relaxed">
          {dict.solution.benefit1Desc}
        </p>
      </div>

      {/* Benefit 2-3 follow same pattern */}
    </div>
  </div>
</section>
```

## 3. Sub-Components

### FAQ Item (Accordion)
```typescript
function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <details
      className="group p-4 rounded-lg border border-border-default/50 hover:border-accent/30 transition-all cursor-pointer"
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
```

### Workflow Item
```typescript
function WorkflowItem({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="p-6 rounded-xl bg-bg-secondary border border-border-default/50 hover:border-accent/30 transition-all">
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-text-secondary">{desc}</p>
    </div>
  )
}
```

### Tip Card
```typescript
function TipCard({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div className="p-6 rounded-xl bg-bg-primary border border-border-default/50">
      <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
        <span className="text-accent font-bold text-sm">{icon}</span>
      </div>
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-text-secondary text-sm leading-relaxed">{desc}</p>
    </div>
  )
}
```

## 4. Navigation Pattern

### Sticky Nav
```typescript
<nav className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/80 backdrop-blur-xl border-b border-border-default/50">
  <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
    {/* Logo */}
    <Link href={`/${lang}`} className="flex items-center gap-2.5 group">
      <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
        <MicIcon className="w-4 h-4 text-accent" />
      </div>
      <span className="font-display font-semibold text-lg tracking-tight">
        Whisper Cheap
      </span>
    </Link>

    {/* Right side */}
    <div className="flex items-center gap-6">
      <a href={DOWNLOAD_URL} className="px-4 py-2 rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors text-sm font-medium">
        {lang === 'en' ? 'Download' : 'Descargar'}
      </a>
      <a
        href={`/${otherLang}/use-cases/writers`}
        className="text-sm text-text-secondary hover:text-text-primary transition-colors"
      >
        {lang === 'en' ? 'ES' : 'EN'}
      </a>
    </div>
  </div>
</nav>
```

## 5. Responsive Grid Patterns

### 2-Column (Mobile → 2 cols on tablet)
```tsx
<div className="grid md:grid-cols-2 gap-6">
  {/* Items */}
</div>
```

### 3-Column (Mobile → 3 cols on desktop)
```tsx
<div className="grid md:grid-cols-3 gap-8">
  {/* Items */}
</div>
```

### 5-Item Grid (Mobile 1, Tablet 2, Desktop needs custom)
```tsx
<div className="space-y-4 md:grid md:grid-cols-2 gap-6">
  {/* Works for list of items */}
</div>
```

## 6. Dictionary Structure

### English (en.json)
```json
{
  "writers": {
    "meta": {
      "title": "AI Dictation for Writers - Write 3x Faster | Whisper Cheap",
      "description": "Free AI dictation software for writers..."
    },
    "hero": {
      "hook": "Capture Every Idea at the Speed of Thought",
      "subtitle": "Stop losing sentences...",
      "cta": "Download Free"
    },
    "problem": {
      "title": "The Writer's Dilemma: Thinking vs Typing",
      "intro": "Your mind moves faster...",
      "painPoint1": "Typing can't keep up with your thoughts",
      "painPoint1Desc": "By the time you finish typing...",
      "painPoint2": "Ideas fade while you hunt for keys",
      "painPoint2Desc": "Keyboard shortcuts...",
      "painPoint3": "Writer's block and the inner critic",
      "painPoint3Desc": "Typing makes you edit...",
      "painPoint4": "RSI and typing fatigue are real",
      "painPoint4Desc": "Wrist pain..."
    },
    "solution": {
      "title": "How Voice Dictation Changes Your Writing",
      "intro": "Professional writers...",
      "benefit1Title": "First Drafts in Half the Time",
      "benefit1Desc": "Speak naturally...",
      "benefit2Title": "Capture Ideas Anywhere",
      "benefit2Desc": "Walking...",
      "benefit3Title": "Beat Writer's Block",
      "benefit3Desc": "Speaking bypasses..."
    },
    "whyWhisperCheap": {
      "title": "Why Writers Choose Whisper Cheap",
      "reason1Title": "Free Forever = No Paywall to Overcome",
      "reason1Desc": "No subscription...",
      "reason2Title": "100% Offline = Write Anywhere, Anytime",
      "reason2Desc": "No WiFi needed...",
      "reason3Title": "Your Stories Stay Yours",
      "reason3Desc": "Your voice never leaves..."
    },
    "workflows": {
      "title": "Real Writing Workflows with Whisper Cheap",
      "intro": "Different writers use...",
      "workflow1Title": "Morning Pages & Journaling",
      "workflow1Desc": "Capture stream...",
      // ... workflow2-5
    },
    "tips": {
      "title": "Tips for Writers Using Voice Dictation",
      "intro": "A few practices...",
      "tip1Title": "Speak Your Punctuation",
      "tip1Desc": "Say 'period'...",
      // ... tip2-5
    },
    "faqWriters": {
      "title": "Questions Writers Ask",
      "q1": "Will it understand my accent?",
      "a1": "Whisper Cheap is trained on 99 languages...",
      "q2": "Can I dictate directly into Scrivener, Word, or Google Docs?",
      "a2": "Yes. Press your hotkey...",
      // ... q3-q6
    },
    "cta": {
      "title": "Stop Losing Ideas. Start Writing Faster.",
      "subtitle": "Your next draft is waiting...",
      "button": "Download Now"
    }
  }
}
```

## 7. Tailwind CSS Classes Used

### Layout
- `relative`, `fixed`, `absolute` - positioning
- `max-w-*` - width constraints (3xl, 5xl, 6xl)
- `mx-auto`, `px-6` - centering and padding
- `grid`, `md:grid-cols-2`, `md:grid-cols-3` - responsive grids
- `gap-6`, `gap-8`, `space-y-4` - spacing

### Typography
- `font-display`, `font-bold`, `font-semibold` - font families
- `text-5xl`, `text-4xl`, `text-lg`, `text-sm` - sizes
- `text-primary`, `text-secondary` - colors
- `tracking-tight` - letter spacing
- `leading-relaxed` - line height

### Colors
- `bg-primary`, `bg-secondary` - backgrounds
- `text-primary`, `text-secondary` - text
- `accent` - highlight color
- `/80`, `/90`, `/10` - opacity
- `border-default` - borders

### Effects
- `rounded-lg`, `rounded-xl` - border radius
- `hover:*` - hover states
- `transition-colors`, `transition-all` - animations
- `group-open:*` - state-based styling
- `backdrop-blur-xl` - blur effects

### Responsive
- `md:` - tablet breakpoint (768px)
- `lg:` - desktop breakpoint (1024px)

## 8. Import Statements

```typescript
// Page component
import type { Metadata } from 'next'
import { getDictionary, type Locale } from '@/dictionaries'
import { WritersPage } from '@/components/WritersPage'

// Client component
import { Locale } from '@/dictionaries'
import Link from 'next/link'
import { PencilIcon, BrainIcon, ChevronDownIcon, CheckIcon, MicIcon } from 'lucide-react'
import * as React from 'react'
```

## 9. Testing Queries

### Check TypeScript
```bash
npx tsc --noEmit src/app/[lang]/use-cases/writers/page.tsx
```

### Check Dictionary JSON
```bash
python3 -m json.tool src/dictionaries/en.json > /dev/null && echo "Valid JSON"
```

### Build
```bash
npm run build
```

### Dev Server
```bash
npm run dev
# Visit http://localhost:3000/en/use-cases/writers
```

## 10. Common Customizations

### Change Download URL
```typescript
const DOWNLOAD_URL = `https://your-domain.com/download`
```

### Change Color Scheme
Update `tailwind.config.ts`:
```typescript
colors: {
  accent: '#your-color',
  // ...
}
```

### Change Layout Widths
```typescript
<div className="max-w-7xl mx-auto"> {/* Wider */}
<div className="max-w-2xl mx-auto"> {/* Narrower */}
```

### Add New FAQ Item
Add to dictionary:
```json
"q7": "New question?",
"a7": "New answer.",
```

Then render:
```typescript
faqItems.push({ q: dict.faqWriters.q7, a: dict.faqWriters.a7 })
```

---

For full context, see `WRITERS_PAGE.md` and `IMPLEMENTATION_SUMMARY.md`
