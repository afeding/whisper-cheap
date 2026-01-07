import { getDictionary } from '@/dictionaries'

export async function GET() {
  const baseUrl = 'https://whispercheap.com'
  const dict = await getDictionary('en')

  const blogPosts = [
    {
      slug: 'voice-typing-tips',
      title:
        dict.blog?.voiceTypingTips?.meta?.title ||
        '15 Voice Typing Tips to 3x Your Productivity',
      description:
        dict.blog?.voiceTypingTips?.meta?.description ||
        'Master voice typing with these proven productivity tips.',
      date: '2025-01-03T00:00:00Z',
    },
    {
      slug: 'ai-dictation-guide',
      title:
        dict.blog?.aiDictationGuide?.meta?.title ||
        "How to Use AI Dictation: Complete Beginner's Guide (2025)",
      description:
        dict.blog?.aiDictationGuide?.meta?.description ||
        'Learn to use AI dictation effectively. Setup, tips, best practices, and common mistakes.',
      date: '2025-01-03T00:00:00Z',
    },
  ]

  const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Whisper Cheap Blog</title>
    <link>${baseUrl}/en</link>
    <description>AI dictation guides, productivity tips, and voice typing best practices</description>
    <language>en</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${baseUrl}/feed.xml" rel="self" type="application/rss+xml" />
    ${blogPosts
      .map(
        (post) => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${baseUrl}/en/blog/${post.slug}</link>
      <guid isPermaLink="true">${baseUrl}/en/blog/${post.slug}</guid>
      <description><![CDATA[${post.description}]]></description>
      <pubDate>${new Date(post.date).toUTCString()}</pubDate>
    </item>`
      )
      .join('')}
  </channel>
</rss>`

  return new Response(feed, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
