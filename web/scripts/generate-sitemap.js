const fs = require('fs');
const path = require('path');

const baseUrl = 'https://whispercheap.com';
const lastModified = new Date().toISOString();

const routes = [
  { path: '', priority: 1.0 },
  { path: '/vs/wispr-flow', priority: 0.9 },
  { path: '/vs/dragon', priority: 0.9 },
  { path: '/use-cases/writers', priority: 0.8 },
  { path: '/use-cases/developers', priority: 0.8 },
  { path: '/use-cases/lawyers', priority: 0.8 },
  { path: '/use-cases/students', priority: 0.8 },
  { path: '/features/offline', priority: 0.7 },
  { path: '/features/privacy', priority: 0.7 },
  { path: '/blog', priority: 0.7 },
  { path: '/blog/ai-dictation-guide', priority: 0.6 },
  { path: '/blog/voice-typing-tips', priority: 0.6 },
];

function generateUrlEntry(path, lang, priority) {
  const url = `${baseUrl}/${lang}${path}`;
  const enUrl = `${baseUrl}/en${path}`;
  const esUrl = `${baseUrl}/es${path}`;

  return `<url>
<loc>${url}</loc>
<xhtml:link rel="alternate" hreflang="en" href="${enUrl}" />
<xhtml:link rel="alternate" hreflang="es" href="${esUrl}" />
<xhtml:link rel="alternate" hreflang="x-default" href="${enUrl}" />
<lastmod>${lastModified}</lastmod>
<changefreq>weekly</changefreq>
<priority>${priority}</priority>
</url>`;
}

function generateSitemap() {
  console.log('🗺️  Generando sitemap.xml...\n');

  let urlEntries = [];

  routes.forEach(route => {
    urlEntries.push(generateUrlEntry(route.path, 'en', route.priority));
    urlEntries.push(generateUrlEntry(route.path, 'es', route.priority));
  });

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urlEntries.join('\n')}
</urlset>`;

  const outDir = path.join(__dirname, '../out');
  const publicDir = path.join(__dirname, '../public');

  // Escribir en out/ para el deployment actual
  fs.writeFileSync(path.join(outDir, 'sitemap.xml'), sitemap);
  console.log(`✅ sitemap.xml generado en /out (${urlEntries.length} URLs)`);

  // También escribir en public/ como backup
  fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemap);
  console.log(`✅ sitemap.xml copiado a /public (${urlEntries.length} URLs)`);

  console.log('\n📊 Resumen:');
  routes.forEach(route => {
    console.log(`   ${route.path || '/'} (EN/ES) - Prioridad: ${route.priority}`);
  });
  console.log(`\n✨ Total: ${urlEntries.length} URLs (${routes.length} rutas × 2 idiomas)`);
}

generateSitemap();
