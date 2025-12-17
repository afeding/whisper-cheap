import { getDictionary, type Locale } from '@/dictionaries'
import { LandingPage } from '@/components/LandingPage'

export default async function Home({ params }: { params: { lang: Locale } }) {
  const dict = await getDictionary(params.lang)
  return <LandingPage dict={dict} lang={params.lang} />
}
