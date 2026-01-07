const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, '../public');
const iconSvg = fs.readFileSync(path.join(publicDir, 'icon.svg'));

async function generateImages() {
  console.log('🎨 Generando imágenes para SEO...\n');

  // 1. Apple Touch Icon (180x180)
  console.log('📱 Generando apple-touch-icon.png (180×180)...');
  await sharp(iconSvg)
    .resize(180, 180)
    .png()
    .toFile(path.join(publicDir, 'apple-touch-icon.png'));
  console.log('✅ apple-touch-icon.png creado');

  // 2. Favicon (32x32 PNG, luego convertir a ICO)
  console.log('🌐 Generando favicon-32x32.png...');
  await sharp(iconSvg)
    .resize(32, 32)
    .png()
    .toFile(path.join(publicDir, 'favicon-32x32.png'));
  console.log('✅ favicon-32x32.png creado');

  // 3. Favicon 16x16
  console.log('🌐 Generando favicon-16x16.png...');
  await sharp(iconSvg)
    .resize(16, 16)
    .png()
    .toFile(path.join(publicDir, 'favicon-16x16.png'));
  console.log('✅ favicon-16x16.png creado');

  // 4. OG Image (1200x630) - Fondo con logo y texto
  console.log('🖼️  Generando og-image.png (1200×630)...');

  // Crear fondo degradado
  const ogBackground = Buffer.from(`
    <svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#0f172a;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#1e293b;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="1200" height="630" fill="url(#grad)"/>

      <!-- Logo centrado a la izquierda -->
      <g transform="translate(150, 215)">
        <rect width="200" height="200" rx="40" fill="#0a0a0a"/>
        <path d="M100 120c13.2 0 24-10.8 24-24V56c0-13.2-10.8-24-24-24s-24 10.8-24 24v40c0 13.2 10.8 24 24 24z" fill="#00ff88"/>
        <path d="M140 96c0 22-18 40-40 40s-40-18-40-40h-16c0 28.2 20.8 51.4 48 55.4V168h16v-16.6c27.2-4 48-27.2 48-55.4h-16z" fill="#00ff88"/>
      </g>

      <!-- Texto a la derecha -->
      <text x="420" y="260" font-family="Arial, sans-serif" font-size="72" font-weight="bold" fill="#ffffff">
        Whisper Cheap
      </text>
      <text x="420" y="330" font-family="Arial, sans-serif" font-size="40" fill="#00ff88">
        Free AI Voice Typing
      </text>
      <text x="420" y="390" font-family="Arial, sans-serif" font-size="32" fill="#94a3b8">
        100% Offline • Unlimited • Open Source
      </text>
    </svg>
  `);

  await sharp(ogBackground)
    .png()
    .toFile(path.join(publicDir, 'og-image.png'));
  console.log('✅ og-image.png creado');

  console.log('\n✨ Todas las imágenes generadas exitosamente!');
  console.log('\nArchivos creados en /public:');
  console.log('  - apple-touch-icon.png (180×180)');
  console.log('  - favicon-32x32.png (32×32)');
  console.log('  - favicon-16x16.png (16×16)');
  console.log('  - og-image.png (1200×630)');
  console.log('\nNota: Para favicon.ico, usa un convertidor online o favicon.io');
  console.log('      Sube favicon-32x32.png y favicon-16x16.png');
}

generateImages().catch(console.error);
