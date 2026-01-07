# Code Snippets - Students Use Case Implementation

## File Locations

Absolute paths:
```
D:\1.SASS\whisper-cheap\web\src\app\[lang]\use-cases\students\page.tsx
D:\1.SASS\whisper-cheap\web\src\app\[lang]\use-cases\students\client.tsx
D:\1.SASS\whisper-cheap\web\src\dictionaries\en.json (students section)
D:\1.SASS\whisper-cheap\web\src\dictionaries\es.json (students section)
```

---

## 1. Server Component - page.tsx

Metadata generation and schema injection:

```typescript
export async function generateMetadata({
  params,
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const dict = await getDictionary(params.lang)
  const studentDict = dict?.students

  return {
    title: studentDict?.meta?.title,
    description: studentDict?.meta?.description,
    keywords: studentDict?.meta?.keywords,
    alternates: {
      canonical: `/${params.lang}/use-cases/students`,
      languages: {
        en: '/en/use-cases/students',
        es: '/es/use-cases/students',
        'x-default': '/en/use-cases/students',
      },
    },
    openGraph: {
      title: studentDict?.meta?.title,
      description: studentDict?.meta?.description,
      url: `${baseUrl}/${params.lang}/use-cases/students`,
      locale: params.lang === 'es' ? 'es_ES' : 'en_US',
    },
  }
}
```

JSON-LD Schema Generation:

```typescript
const schemaArticle = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: studentDict?.meta?.title,
  description: studentDict?.meta?.description,
  image: '/og-image.png',
  author: {
    '@type': 'Organization',
    name: 'Whisper Cheap',
  },
  datePublished: new Date().toISOString(),
}

const schemaFAQ = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: studentDict?.faq?.items?.map((item: any) => ({
    '@type': 'Question',
    name: item.q,
    acceptedAnswer: {
      '@type': 'Answer',
      text: item.a,
    },
  })) || [],
}
```

---

## 2. Client Component - client.tsx

Hero Section:

```typescript
<section className="pt-32 pb-20 px-6">
  <div className="max-w-4xl mx-auto text-center">
    <h1 className="text-5xl md:text-6xl font-display font-bold tracking-tight mb-6">
      {studentDict.hero?.title}
    </h1>
    <a href={downloadUrl} className="px-8 py-3 rounded-lg bg-accent text-bg-primary">
      {studentDict.hero?.cta}
    </a>
  </div>
</section>
```

Problem Section Grid:

```typescript
<div className="grid md:grid-cols-2 gap-6">
  {[
    { title: studentDict.problem?.pain1, desc: studentDict.problem?.pain1Desc },
    { title: studentDict.problem?.pain2, desc: studentDict.problem?.pain2Desc },
  ].map((item, i) => (
    <div key={i} className="p-6 rounded-lg border border-border-default/50">
      <h3 className="font-semibold mb-2">{item.title}</h3>
      <p className="text-sm text-text-secondary">{item.desc}</p>
    </div>
  ))}
</div>
```

FAQ Collapsible:

```typescript
<details className="group p-6 rounded-lg border border-border-default/50">
  <summary className="font-semibold flex items-center justify-between">
    {item.q}
    <span className="ml-4 group-open:rotate-180 transition-transform">▼</span>
  </summary>
  <p className="text-text-secondary text-sm mt-4">{item.a}</p>
</details>
```

Use Cases with Icons:

```typescript
const useCaseIcons: Record<string, React.ComponentType<any>> = {
  BookOpen,
  FileText,
  Lightbulb,
  Brain,
  Search,
}

{studentDict.useCases?.cases?.map((useCase: any, i: number) => {
  const IconComponent = useCaseIcons[useCase.icon] || BookOpen
  return (
    <div key={i} className="p-6 rounded-lg bg-bg-secondary/50">
      <IconComponent className="w-8 h-8 text-accent mb-4" />
      <h3 className="font-semibold mb-2">{useCase.title}</h3>
    </div>
  )
})}
```

Navigation with Language Switcher:

```typescript
<nav className="fixed top-0 left-0 right-0 z-50">
  <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
    <Link href={`/${params.lang}`}>
      <Volume2 className="w-4 h-4 text-accent" />
      Whisper Cheap
    </Link>
    <Link href={`/${otherLang}/use-cases/students`}>
      {params.lang === 'en' ? 'ES' : 'EN'}
    </Link>
  </div>
</nav>
```

---

## 3. Dictionary Structure Example

From en.json students section:

```json
{
  "students": {
    "meta": {
      "title": "Voice Typing for Students - Take Notes Faster | Whisper Cheap",
      "description": "Free voice typing for students...",
      "keywords": "voice typing for students, dictation for studying..."
    },
    "hero": {
      "tagline": "FOR STUDENTS",
      "title": "Study Smarter, Type Less",
      "subtitle": "Capture lecture notes in real-time...",
      "cta": "Download Free",
      "highlight": "100% free, no subscriptions, works offline"
    },
    "problem": {
      "title": "The Student's Challenge",
      "pain1": "Lecture notes can't keep pace",
      "pain1Desc": "By the time you finish typing one slide..."
    },
    "solution": {
      "benefit1": "Capture Complete Notes",
      "benefit1Desc": "Speak naturally and keep pace..."
    },
    "useCases": {
      "cases": [
        {
          "icon": "BookOpen",
          "title": "Lecture Notes",
          "desc": "Capture every slide in real-time..."
        }
      ]
    },
    "faq": {
      "items": [
        {
          "q": "Is it really free?",
          "a": "Yes. 100% free, no subscriptions..."
        }
      ]
    }
  }
}
```

---

## 4. Routes & URLs

Route structure:
```
/[lang]/use-cases/students/page.tsx
```

Generated URLs:
```
https://whispercheap.com/en/use-cases/students
https://whispercheap.com/es/use-cases/students
```

Language switcher:
```
EN → /en/use-cases/students
ES → /es/use-cases/students
```

---

## 5. Key Tailwind Classes

Spacing:
```
pt-32 pb-20 px-6
gap-6
p-6
```

Typography:
```
text-5xl md:text-6xl
font-display font-bold
text-text-secondary
text-sm
```

Colors:
```
bg-bg-primary, bg-bg-secondary/30
text-text-primary, text-text-secondary
border-border-default/50
bg-accent text-bg-primary
```

Layout:
```
max-w-4xl mx-auto
grid md:grid-cols-2
flex items-center justify-between
rounded-lg
```

---

## 6. Component Props

StudentsPageClientProps:

```typescript
interface StudentsPageClientProps {
  params: { lang: Locale }
  dict: {
    students: {
      meta: { title: string; description: string; keywords: string }
      hero: { tagline: string; title: string; subtitle: string; ... }
      problem: { title: string; pain1: string; pain1Desc: string; ... }
      solution: { title: string; benefit1: string; benefit1Desc: string; ... }
      whyWhisperCheap: { [key: string]: { title: string; desc: string } }
      useCases: { cases: Array<{ icon: string; title: string; desc: string }> }
      faq: { items: Array<{ q: string; a: string }> }
      testimonial: { quote: string; author: string }
      cta: { title: string; subtitle: string; button: string }
    }
  }
}
```

---

## 7. Icons Used

From lucide-react:

```typescript
import {
  BookOpen,      // Lecture Notes
  FileText,      // Essays
  Lightbulb,     // Study Notes
  Brain,         // Flashcards
  Search,        // Research
  CheckCircle2,  // UI
  ArrowRight,    // UI
  Volume2        // Logo icon
} from 'lucide-react'
```

---

## 8. SEO Configuration

Meta tags in page.tsx:

```typescript
{
  title: "Voice Typing for Students - Take Notes Faster",
  description: "Free voice typing for students. Take lecture notes...",
  keywords: "voice typing for students, dictation for studying...",
  canonical: "/en/use-cases/students",
  alternates: {
    languages: {
      en: "/en/use-cases/students",
      es: "/es/use-cases/students"
    }
  },
  openGraph: {
    title: "Voice Typing for Students...",
    description: "Free voice typing for students...",
    url: "https://whispercheap.com/en/use-cases/students",
    locale: "en_US"
  }
}
```

---

## 9. Sections Breakdown

1. **Hero** - Title, subtitle, CTA (pt-32 pb-20)
2. **Problem** - 4 pain points in 2x2 grid (py-20)
3. **Solution** - 3 benefits in 3-column grid (py-20)
4. **Why Whisper Cheap** - 4 cards in 2x2 grid (py-20)
5. **Use Cases** - 5 scenarios in 2-column grid (py-20)
6. **FAQ** - 8 collapsible items (py-20, max-w-3xl)
7. **Testimonial** - Quote section (py-20, centered)
8. **Final CTA** - Call to action (py-20, accent bg)
9. **Footer** - Links, tagline (py-12)

---

## 10. Testing Checklist

- [ ] Server component metadata generates
- [ ] Schema JSON-LD valid (use schema.org validator)
- [ ] Mobile responsive at 375px, 768px, 1024px
- [ ] FAQ opens/closes properly
- [ ] Language switcher navigates correctly
- [ ] Download button links to GitHub
- [ ] All dictionary keys are populated
- [ ] Icons render without errors
- [ ] No TypeScript errors
- [ ] SEO tags present in source

---

**Status: Production-ready code**
**Last Updated: 2026-01-03**
