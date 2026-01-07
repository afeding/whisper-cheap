import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://whispercheap.com'
  const lastModified = new Date()

  // Helper function to create bilingual route entries
  const createBilingualRoute = (path: string, priority: number = 0.8): MetadataRoute.Sitemap => {
    return [
      {
        url: `${baseUrl}/en${path}`,
        lastModified,
        changeFrequency: 'weekly' as const,
        priority,
        alternates: {
          languages: {
            en: `${baseUrl}/en${path}`,
            es: `${baseUrl}/es${path}`,
          },
        },
      },
      {
        url: `${baseUrl}/es${path}`,
        lastModified,
        changeFrequency: 'weekly' as const,
        priority,
        alternates: {
          languages: {
            en: `${baseUrl}/en${path}`,
            es: `${baseUrl}/es${path}`,
          },
        },
      },
    ]
  }

  return [
    // Landing pages (highest priority)
    ...createBilingualRoute('', 1.0),

    // Comparison pages (high priority - main traffic drivers)
    ...createBilingualRoute('/vs/wispr-flow', 0.9),
    ...createBilingualRoute('/vs/dragon', 0.9),

    // Use case pages (high priority - conversion focused)
    ...createBilingualRoute('/use-cases/writers', 0.8),
    ...createBilingualRoute('/use-cases/developers', 0.8),
    ...createBilingualRoute('/use-cases/lawyers', 0.8),
    ...createBilingualRoute('/use-cases/students', 0.8),

    // Feature pages (medium-high priority)
    ...createBilingualRoute('/features/offline', 0.7),
    ...createBilingualRoute('/features/privacy', 0.7),

    // Blog posts (medium priority - evergreen content)
    ...createBilingualRoute('/blog/ai-dictation-guide', 0.6),
    ...createBilingualRoute('/blog/voice-typing-tips', 0.6),
  ]
}
