const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, '../public');

async function generateFavicon() {
  console.log('🌐 Generando favicon.ico...');

  const pngToIco = (await import('png-to-ico')).default;

  const pngFiles = [
    path.join(publicDir, 'favicon-16x16.png'),
    path.join(publicDir, 'favicon-32x32.png')
  ];

  const ico = await pngToIco(pngFiles);
  fs.writeFileSync(path.join(publicDir, 'favicon.ico'), ico);

  console.log('✅ favicon.ico creado (multi-size: 16×16 + 32×32)');
}

generateFavicon().catch(console.error);
