/**
 * Example Blog Post Page
 *
 * This is a complete example showing how to use the BlogLayout component.
 * You can use this as a template for creating new blog posts.
 *
 * Location: src/app/[lang]/blog/example-getting-started/page.tsx
 * URL: /en/blog/example-getting-started or /es/blog/example-getting-started
 */

import { BlogLayout } from '@/components/BlogLayout'
import type { Metadata } from 'next'
import type { Locale } from '@/dictionaries'

export async function generateMetadata({
  params
}: {
  params: { lang: Locale }
}): Promise<Metadata> {
  const isEn = params.lang === 'en'

  return {
    title: isEn
      ? 'Getting Started with Whisper Cheap'
      : 'Empezando con Whisper Cheap',
    description: isEn
      ? 'Learn how to install and use Whisper Cheap for the first time. A complete guide for beginners.'
      : 'Aprende a instalar y usar Whisper Cheap por primera vez. Una guía completa para principiantes.',
    keywords: isEn
      ? ['whisper cheap', 'getting started', 'installation', 'dictation']
      : ['whisper cheap', 'empezando', 'instalación', 'dictado'],
    openGraph: {
      title: isEn ? 'Getting Started with Whisper Cheap' : 'Empezando con Whisper Cheap',
      description: isEn
        ? 'Learn how to install and use Whisper Cheap'
        : 'Aprende a instalar y usar Whisper Cheap',
      type: 'article',
      publishedTime: '2024-01-10T00:00:00Z',
      authors: ['Andrés Feding']
    },
    twitter: {
      card: 'summary_large_image'
    }
  }
}

export default function GettingStartedPage({ params }: { params: { lang: Locale } }) {
  const isEn = params.lang === 'en'

  const relatedArticles = [
    {
      title: isEn ? 'Privacy Guide' : 'Guía de Privacidad',
      slug: 'privacy-guide',
      date: '2024-01-15',
      readingTime: isEn ? '7 min read' : '7 min de lectura'
    },
    {
      title: isEn ? 'Advanced Tips for Developers' : 'Consejos Avanzados para Desarrolladores',
      slug: 'advanced-tips',
      date: '2024-01-20',
      readingTime: isEn ? '10 min read' : '10 min de lectura'
    }
  ]

  return (
    <BlogLayout
      title={isEn ? 'Getting Started with Whisper Cheap' : 'Empezando con Whisper Cheap'}
      date="2024-01-10"
      readingTime={isEn ? '5 min read' : '5 min de lectura'}
      lang={params.lang}
      author={{
        name: 'Andrés Feding',
        role: isEn ? 'Creator' : 'Creador'
      }}
      relatedArticles={relatedArticles}
    >
      {/* ========== INTRODUCTION ========== */}
      <h2 id="introduction">
        {isEn ? 'Introduction' : 'Introducción'}
      </h2>

      <p>
        {isEn
          ? 'Whisper Cheap is a free, local speech-to-text application for Windows. This guide will walk you through installation and your first dictation in just 5 minutes.'
          : 'Whisper Cheap es una aplicación gratuita de voz a texto local para Windows. Esta guía te mostrará cómo instalarla y hacer tu primer dictado en solo 5 minutos.'}
      </p>

      <p>
        {isEn
          ? "Whether you're a writer, developer, student, or professional, Whisper Cheap can help you type faster by simply speaking. Let's get started."
          : 'Ya seas escritor, desarrollador, estudiante o profesional, Whisper Cheap puede ayudarte a escribir más rápido simplemente hablando. Vamos a empezar.'}
      </p>

      {/* ========== WHAT YOU'LL NEED ========== */}
      <h2 id="requirements">
        {isEn ? 'What You\'ll Need' : 'Lo que Necesitarás'}
      </h2>

      <ul>
        <li>
          <strong>Windows 10 or later</strong>
          {isEn ? ' - Whisper Cheap is Windows-only for now.' : ' - Whisper Cheap es solo para Windows por ahora.'}
        </li>
        <li>
          <strong>A microphone</strong>
          {isEn ? ' - Built-in or external, doesn\'t matter.' : ' - Integrado o externo, no importa.'}
        </li>
        <li>
          <strong>200MB of free disk space</strong>
          {isEn ? ' - For the app and AI model.' : ' - Para la aplicación y el modelo de IA.'}
        </li>
        <li>
          <strong>No account required</strong>
          {isEn ? ' - Download and use immediately.' : ' - Descarga y usa inmediatamente.'}
        </li>
      </ul>

      {/* ========== INSTALLATION ========== */}
      <h2 id="installation">
        {isEn ? 'Installation' : 'Instalación'}
      </h2>

      <h3 id="step1-download">
        {isEn ? 'Step 1: Download' : 'Paso 1: Descargar'}
      </h3>

      <ol>
        <li>
          {isEn
            ? 'Go to GitHub: github.com/afeding/whisper-cheap'
            : 'Ve a GitHub: github.com/afeding/whisper-cheap'}
        </li>
        <li>
          {isEn
            ? 'Click "Releases" and download the latest WhisperCheapSetup.exe'
            : 'Haz clic en "Releases" y descarga el último WhisperCheapSetup.exe'}
        </li>
        <li>
          {isEn
            ? 'Wait for the download to complete.'
            : 'Espera a que se complete la descarga.'}
        </li>
      </ol>

      <h3 id="step2-install">
        {isEn ? 'Step 2: Install' : 'Paso 2: Instalar'}
      </h3>

      <ol>
        <li>
          {isEn
            ? 'Double-click WhisperCheapSetup.exe'
            : 'Haz doble clic en WhisperCheapSetup.exe'}
        </li>
        <li>
          {isEn
            ? 'Click "Install" and choose your installation folder'
            : 'Haz clic en "Instalar" y elige tu carpeta de instalación'}
        </li>
        <li>
          {isEn
            ? 'The installer will download the AI model (~150MB)'
            : 'El instalador descargará el modelo de IA (~150MB)'}
        </li>
        <li>
          {isEn
            ? 'Click "Finish" when done'
            : 'Haz clic en "Finalizar" cuando termine'}
        </li>
      </ol>

      <p>
        <strong>{isEn ? 'That\'s it!' : 'Eso es todo!'}</strong>
        {isEn
          ? ' Whisper Cheap will launch automatically. You should see the settings window and a system tray icon.'
          : ' Whisper Cheap se iniciará automáticamente. Deberías ver la ventana de configuración y un ícono en la bandeja del sistema.'}
      </p>

      {/* ========== FIRST DICTATION ========== */}
      <h2 id="first-dictation">
        {isEn ? 'Your First Dictation' : 'Tu Primer Dictado'}
      </h2>

      <p>
        {isEn
          ? 'Now let\'s record your first text. Follow these steps:'
          : 'Ahora vamos a grabar tu primer texto. Sigue estos pasos:'}
      </p>

      <ol>
        <li>
          {isEn ? 'Open any text editor (Word, Notepad, Google Docs, etc.)' : 'Abre cualquier editor de texto (Word, Notepad, Google Docs, etc.)'}
        </li>
        <li>
          {isEn ? 'Click in the text area where you want text to appear' : 'Haz clic en el área de texto donde quieras que aparezca el texto'}
        </li>
        <li>
          {isEn ? 'Press your hotkey: Ctrl + Space (default)' : 'Presiona tu tecla de acceso rápido: Ctrl + Espacio (predeterminado)'}
        </li>
        <li>
          {isEn ? 'Say something: "Hello, this is my first dictation"' : 'Di algo: "Hola, este es mi primer dictado"'}
        </li>
        <li>
          {isEn ? 'Release the hotkey' : 'Suelta la tecla de acceso rápido'}
        </li>
        <li>
          {isEn ? 'Watch the text appear in your editor' : 'Mira el texto aparecer en tu editor'}
        </li>
      </ol>

      <blockquote>
        {isEn
          ? '"Tip: Speak clearly and naturally. You don\'t need to change how you normally speak."'
          : '"Consejo: Habla claro y naturalmente. No necesitas cambiar cómo hablas normalmente."'}
      </blockquote>

      {/* ========== BASIC SETTINGS ========== */}
      <h2 id="settings">
        {isEn ? 'Basic Settings' : 'Configuración Básica'}
      </h2>

      <p>
        {isEn
          ? 'A settings window should have opened during installation. Here are the key options:'
          : 'Una ventana de configuración debería haberse abierto durante la instalación. Aquí están las opciones clave:'}
      </p>

      <h3 id="hotkey">
        {isEn ? 'Hotkey' : 'Tecla de Acceso Rápido'}
      </h3>

      <p>
        {isEn
          ? 'Default is Ctrl + Space. You can change this to any key combination you prefer. Suggestions:'
          : 'El predeterminado es Ctrl + Espacio. Puedes cambiar esto a cualquier combinación de teclas que prefieras. Sugerencias:'}
      </p>

      <ul>
        <li><code>Ctrl + Shift + V</code> {isEn ? '(voice)' : '(voz)'}</li>
        <li><code>Ctrl + Alt + D</code> {isEn ? '(dictate)' : '(dictar)'}</li>
        <li><code>F12</code> {isEn ? '(function key)' : '(tecla de función)'}</li>
      </ul>

      <h3 id="activation-mode">
        {isEn ? 'Activation Mode' : 'Modo de Activación'}
      </h3>

      <ul>
        <li>
          <strong>{isEn ? 'Push-to-Talk (PTT)' : 'Presionar para Hablar'}</strong>
          {isEn
            ? ': Hold down the hotkey while speaking. Release to stop.'
            : ': Mantén presionada la tecla de acceso rápido mientras hablas. Suelta para detener.'}
        </li>
        <li>
          <strong>{isEn ? 'Toggle' : 'Alternar'}</strong>
          {isEn
            ? ': Press once to start, press again to stop. Useful for hands-free recording.'
            : ': Presiona una vez para comenzar, presiona nuevamente para detener. Útil para grabación manos libres.'}
        </li>
      </ul>

      {/* ========== TIPS & TRICKS ========== */}
      <h2 id="tips">
        {isEn ? 'Tips & Tricks' : 'Consejos y Trucos'}
      </h2>

      <h3 id="punctuation">
        {isEn ? 'Handling Punctuation' : 'Manejo de Puntuación'}
      </h3>

      <p>
        {isEn
          ? 'Whisper Cheap will transcribe what you say, but it doesn\'t always add punctuation. You have two options:'
          : 'Whisper Cheap transcribirá lo que digas, pero no siempre añade puntuación. Tienes dos opciones:'}
      </p>

      <ol>
        <li>
          <strong>{isEn ? 'Say the punctuation:' : 'Di la puntuación:'}</strong>
          {isEn
            ? ' "This is great period. How are you question mark" → "This is great. How are you?"'
            : ' "Esto es genial punto. Cómo estás signo de pregunta" → "Esto es genial. Cómo estás?"'}
        </li>
        <li>
          <strong>{isEn ? 'Edit manually:' : 'Edita manualmente:'}</strong>
          {isEn
            ? ' Dictate without punctuation, then add it in the editing pass (usually faster).'
            : ' Dicta sin puntuación, luego agrégala en la pasada de edición (generalmente más rápido).'}
        </li>
      </ol>

      <h3 id="accuracy">
        {isEn ? 'Improving Accuracy' : 'Mejorando la Precisión'}
      </h3>

      <ul>
        <li>
          <strong>{isEn ? 'Use a good microphone:' : 'Usa un micrófono de buena calidad:'}</strong>
          {isEn
            ? ' Built-in mics work, but a headset is better.'
            : ' Los micrófonos integrados funcionan, pero un auricular es mejor.'}
        </li>
        <li>
          <strong>{isEn ? 'Minimize background noise:' : 'Minimiza el ruido de fondo:'}</strong>
          {isEn
            ? ' Find a quiet space for best results.'
            : ' Encuentra un lugar tranquilo para mejores resultados.'}
        </li>
        <li>
          <strong>{isEn ? 'Speak clearly:' : 'Habla claramente:'}</strong>
          {isEn
            ? ' Articulate, but don\'t over-enunciate.'
            : ' Articula, pero no sobre-enuncies.'}
        </li>
        <li>
          <strong>{isEn ? 'Use natural rhythm:' : 'Usa un ritmo natural:'}</strong>
          {isEn
            ? ' Don\'t rush or pause awkwardly.'
            : ' No apresures ni hagas pausas incómodas.'}
        </li>
      </ul>

      <h3 id="workflow">
        {isEn ? 'Suggested Workflow' : 'Flujo de Trabajo Sugerido'}
      </h3>

      <ol>
        <li>
          <strong>{isEn ? 'Dictate first:' : 'Dicta primero:'}</strong>
          {isEn
            ? ' Get your ideas into text quickly. Don\'t worry about perfection.'
            : ' Obtén tus ideas en texto rápidamente. No te preocupes por la perfección.'}
        </li>
        <li>
          <strong>{isEn ? 'Edit second:' : 'Edita segundo:'}</strong>
          {isEn
            ? ' Go back and fix any mistakes. Add punctuation and formatting.'
            : ' Vuelve atrás y corrige cualquier error. Añade puntuación y formato.'}
        </li>
        <li>
          <strong>{isEn ? 'Polish third:' : 'Pule en tercer lugar:'}</strong>
          {isEn
            ? ' Read through once more for clarity and flow.'
            : ' Lee una vez más para claridad y fluidez.'}
        </li>
      </ol>

      {/* ========== NEXT STEPS ========== */}
      <h2 id="next-steps">
        {isEn ? 'Next Steps' : 'Próximos Pasos'}
      </h2>

      <p>
        {isEn
          ? 'Now that you\'ve got the basics down, you can explore more advanced features:'
          : 'Ahora que tienes lo básico, puedes explorar funciones más avanzadas:'}
      </p>

      <ul>
        <li>
          {isEn
            ? 'Check out the Privacy Guide to learn how your data is protected'
            : 'Consulta la Guía de Privacidad para aprender cómo se protegen tus datos'}
        </li>
        <li>
          {isEn
            ? 'Read Advanced Tips for Developers for coding-specific workflows'
            : 'Lee Consejos Avanzados para Desarrolladores para flujos de trabajo específicos de codificación'}
        </li>
        <li>
          {isEn
            ? 'Customize your settings to match your workflow'
            : 'Personaliza tu configuración para que coincida con tu flujo de trabajo'}
        </li>
        <li>
          {isEn
            ? 'Join the community on GitHub and share your experience'
            : 'Únete a la comunidad en GitHub y comparte tu experiencia'}
        </li>
      </ul>

      {/* ========== TROUBLESHOOTING ========== */}
      <h2 id="troubleshooting">
        {isEn ? 'Troubleshooting' : 'Solución de Problemas'}
      </h2>

      <h3>{isEn ? 'Hotkey not working?' : 'Tecla de acceso rápido no funciona?'}</h3>
      <p>
        {isEn
          ? 'Some apps capture hotkeys. Try a different combination or use Toggle mode instead.'
          : 'Algunas aplicaciones capturan teclas de acceso rápido. Intenta una combinación diferente o usa el modo Alternar.'}
      </p>

      <h3>{isEn ? 'No text appearing?' : 'Sin texto que aparezca?'}</h3>
      <p>
        {isEn
          ? 'Make sure the text editor is in focus (click it first). Then press your hotkey and speak clearly.'
          : 'Asegúrate de que el editor de texto esté enfocado (haz clic primero). Luego presiona tu tecla de acceso rápido y habla claramente.'}
      </p>

      <h3>{isEn ? 'Accuracy is poor?' : 'Precisión es pobre?'}</h3>
      <p>
        {isEn
          ? 'Check your microphone, use a quieter space, and speak clearly. See the "Improving Accuracy" section above.'
          : 'Comprueba tu micrófono, usa un lugar más tranquilo y habla claramente. Consulta la sección "Mejorando la Precisión" arriba.'}
      </p>

      {/* ========== CONCLUSION ========== */}
      <h2 id="conclusion">
        {isEn ? 'Conclusion' : 'Conclusión'}
      </h2>

      <p>
        {isEn
          ? "Congratulations! You now know how to use Whisper Cheap for basic dictation. The best way to get better is to practice. Try dictating different types of content and see what works best for you."
          : 'Felicitaciones! Ahora sabes cómo usar Whisper Cheap para dictado básico. La mejor manera de mejorar es practicar. Intenta dictar diferentes tipos de contenido y ve qué funciona mejor para ti.'}
      </p>

      <p>
        {isEn
          ? 'Remember: Whisper Cheap is free forever, runs 100% locally on your computer, and gets better with practice. Enjoy faster writing!'
          : 'Recuerda: Whisper Cheap es gratis para siempre, funciona 100% localmente en tu computadora y mejora con la práctica. ¡Disfruta de escritura más rápida!'}
      </p>
    </BlogLayout>
  )
}
