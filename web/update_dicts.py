#!/usr/bin/env python3
import json

# Read and update EN dictionary
with open('src/dictionaries/en.json', 'r', encoding='utf-8') as f:
    en_dict = json.load(f)

en_dict['writers'] = {
    "meta": {
        "title": "AI Dictation for Writers - Write 3x Faster | Whisper Cheap",
        "description": "Free AI dictation software for writers. Write novels, articles, and scripts by voice. Capture ideas before they fade. 100% private, works offline."
    },
    "hero": {
        "hook": "Capture Every Idea at the Speed of Thought",
        "subtitle": "Stop losing sentences while your fingers catch up. Write your first draft in half the time. Dictation built for the creative process.",
        "cta": "Download Free"
    },
    "problem": {
        "title": "The Writer's Dilemma: Thinking vs Typing",
        "intro": "Your mind moves faster than your fingers ever could.",
        "painPoint1": "Typing can't keep up with your thoughts",
        "painPoint1Desc": "By the time you finish typing one sentence, you've forgotten the next three ideas.",
        "painPoint2": "Ideas fade while you hunt for keys",
        "painPoint2Desc": "Keyboard shortcuts, tab switching, reaching for the mouse—it all breaks your creative flow.",
        "painPoint3": "Writer's block and the inner critic",
        "painPoint3Desc": "Typing makes you edit as you write. Speaking helps you draft freely without judgment.",
        "painPoint4": "RSI and typing fatigue are real",
        "painPoint4Desc": "Wrist pain, shoulder tension, and repetitive strain don't go away. Voice offers relief."
    },
    "solution": {
        "title": "How Voice Dictation Changes Your Writing",
        "intro": "Professional writers have used dictation for decades. Now it's free, accurate, and works offline.",
        "benefit1Title": "First Drafts in Half the Time",
        "benefit1Desc": "Speak naturally and transcription keeps pace. Your first draft becomes real in one session instead of three.",
        "benefit2Title": "Capture Ideas Anywhere",
        "benefit2Desc": "Walking, thinking in bed, in a coffee shop. Your phone's microphone is always ready. Ideas don't fade anymore.",
        "benefit3Title": "Beat Writer's Block",
        "benefit3Desc": "Speaking bypasses the internal editor. You just talk—no second-guessing, no perfectionism slowing you down."
    },
    "whyWhisperCheap": {
        "title": "Why Writers Choose Whisper Cheap",
        "reason1Title": "Free Forever = No Paywall to Overcome",
        "reason1Desc": "No subscription. No word limits. No 'upgrade to unlock' nonsense. Download and start writing.",
        "reason2Title": "100% Offline = Write Anywhere, Anytime",
        "reason2Desc": "No WiFi needed. Airport, road trip, cabin—your AI model is on your computer. Works without internet.",
        "reason3Title": "Your Stories Stay Yours",
        "reason3Desc": "Your voice never leaves your computer. No cloud, no data collection, no AI companies training on your unpublished work."
    },
    "workflows": {
        "title": "Real Writing Workflows with Whisper Cheap",
        "intro": "Different writers use dictation differently. Here's how.",
        "workflow1Title": "Morning Pages & Journaling",
        "workflow1Desc": "Capture stream-of-consciousness thoughts first thing. No editing, just voice. 10-15 minutes becomes 2,000+ words.",
        "workflow2Title": "First Draft Power Sessions",
        "workflow2Desc": "Dictate 2,000-5,000 words in one sitting. Speaking maintains narrative momentum. Edit later.",
        "workflow3Title": "Dialogue Writing",
        "workflow3Desc": "Say your character's lines aloud. Hear how they sound. Natural speech becomes authentic dialogue.",
        "workflow4Title": "Outlining & Brainstorming",
        "workflow4Desc": "Talk through your plot. Capture ideas verbally. Organize later. Thinking happens faster than typing.",
        "workflow5Title": "Research Notes",
        "workflow5Desc": "Listen to a podcast, article, or video. Narrate key points into Whisper Cheap. Hands-free note-taking."
    },
    "tips": {
        "title": "Tips for Writers Using Voice Dictation",
        "intro": "A few practices make dictation even more powerful.",
        "tip1Title": "Speak Your Punctuation",
        "tip1Desc": "Say 'period', 'comma', 'question mark', 'exclamation point' when you need them. Or edit in a second pass.",
        "tip2Title": "Keep Sessions Short (15-20 min)",
        "tip2Desc": "Your voice gets tired. Dictate in focused bursts, then switch to editing or reading.",
        "tip3Title": "Edit in a Separate Pass",
        "tip3Desc": "First pass: dictate everything. Second pass: edit. Separating drafting from editing accelerates both.",
        "tip4Title": "Read Your Dialogue Aloud",
        "tip4Desc": "Before you dictate, read the character's line. Then speak it naturally into the mic.",
        "tip5Title": "Minimize Ambient Noise",
        "tip5Desc": "Quiet room = better accuracy. If you're noisy, Whisper Cheap has VAD (voice detection) to ignore background sound."
    },
    "faqWriters": {
        "title": "Questions Writers Ask",
        "q1": "Will it understand my accent?",
        "a1": "Whisper Cheap is trained on 99 languages and accents. It's very tolerant. Test with a short dictation to see how it performs with your voice.",
        "q2": "Can I dictate directly into Scrivener, Word, or Google Docs?",
        "a2": "Yes. Press your hotkey (Ctrl+Space), dictate, and release. The text pastes wherever your cursor is—Word, Scrivener, Google Docs, Notion, anywhere.",
        "q3": "How do I handle punctuation?",
        "a3": "Say the punctuation word ('period', 'comma', 'dash') or add it in your edit pass. Many writers skip it during dictation and clean up later.",
        "q4": "Do I need to edit everything?",
        "a4": "Accuracy is very high, but yes—expect a light edit pass. Whisper Cheap isn't perfect, but it's fast enough that total time is still much less than typing.",
        "q5": "Can I use it for different genres?",
        "a5": "Absolutely. Literary fiction, romance, sci-fi, nonfiction, screenplays—your voice works in all of them. Dialogue especially benefits from spoken delivery.",
        "q6": "What if there's too much background noise?",
        "a6": "Whisper Cheap includes voice detection (VAD). Turn it on to ignore silence and background noise. Works best in quiet environments."
    },
    "cta": {
        "title": "Stop Losing Ideas. Start Writing Faster.",
        "subtitle": "Your next draft is waiting. Download Whisper Cheap free.",
        "button": "Download Now"
    }
}

with open('src/dictionaries/en.json', 'w', encoding='utf-8') as f:
    json.dump(en_dict, f, ensure_ascii=False, indent=2)

print("Updated EN dictionary with writers section")

# Read and update ES dictionary
with open('src/dictionaries/es.json', 'r', encoding='utf-8') as f:
    es_dict = json.load(f)

es_dict['writers'] = {
    "meta": {
        "title": "Dictado IA para Escritores - Escribe 3x Mas Rapido | Whisper Cheap",
        "description": "Software de dictado IA gratuito para escritores. Escribe novelas, articulos y guiones por voz. Captura ideas antes de que se desvanezcan. 100% privado, funciona sin conexion."
    },
    "hero": {
        "hook": "Captura Cada Idea a la Velocidad del Pensamiento",
        "subtitle": "Deja de perder oraciones mientras tus dedos se ponen al dia. Escribe tu primer borrador en la mitad del tiempo. Dictado diseñado para el proceso creativo.",
        "cta": "Descargar Gratis"
    },
    "problem": {
        "title": "El Dilema del Escritor: Pensar vs Teclear",
        "intro": "Tu mente se mueve mas rapido de lo que tus dedos jamas podrian.",
        "painPoint1": "Teclear no puede mantenerse al ritmo de tus pensamientos",
        "painPoint1Desc": "Para cuando terminas de teclear una oracion, ya olvidaste las siguientes tres ideas.",
        "painPoint2": "Las ideas se desvanecen mientras buscas las teclas",
        "painPoint2Desc": "Atajos de teclado, cambio de pestañas, alcanzar el raton—todo rompe tu flujo creativo.",
        "painPoint3": "Bloqueo de escritor y el critico interno",
        "painPoint3Desc": "Teclear te hace editar mientras escribes. Hablar te ayuda a redactar libremente sin juzgarte.",
        "painPoint4": "El RSI y la fatiga por tipeo son reales",
        "painPoint4Desc": "Dolor de muñeca, tension de hombros y esfuerzo repetitivo no desaparecen. La voz ofrece alivio."
    },
    "solution": {
        "title": "Como el Dictado por Voz Cambia Tu Escritura",
        "intro": "Los escritores profesionales han usado dictado durante decadas. Ahora es gratis, preciso y funciona sin conexion.",
        "benefit1Title": "Primeros Borradores en la Mitad del Tiempo",
        "benefit1Desc": "Habla naturalmente y la transcripcion te sigue el ritmo. Tu primer borrador se hace real en una sesion en lugar de tres.",
        "benefit2Title": "Captura Ideas en Cualquier Lugar",
        "benefit2Desc": "Caminando, pensando en la cama, en una cafeteria. El microfono siempre esta listo. Las ideas ya no se desvanecen.",
        "benefit3Title": "Supera el Bloqueo de Escritor",
        "benefit3Desc": "Hablar evita el editor interno. Solo hablas—sin dudas, sin perfeccionismo ralentizandote."
    },
    "whyWhisperCheap": {
        "title": "Por Que los Escritores Eligen Whisper Cheap",
        "reason1Title": "Gratis Para Siempre = Sin Barrera para Intentar",
        "reason1Desc": "Sin suscripcion. Sin limites de palabras. Sin 'actualiza para desbloquear'. Descarga y empieza a escribir.",
        "reason2Title": "100% Offline = Escribe Donde Quieras, Cuando Quieras",
        "reason2Desc": "Sin WiFi necesario. Aeropuerto, viaje por carretera, cabaña—tu modelo IA esta en tu computadora. Funciona sin internet.",
        "reason3Title": "Tus Historias Te Pertenecen",
        "reason3Desc": "Tu voz nunca sale de tu computadora. Sin nube, sin recopilacion de datos, sin empresas de IA entrenando en tu trabajo no publicado."
    },
    "workflows": {
        "title": "Flujos de Trabajo Reales de Escritura con Whisper Cheap",
        "intro": "Diferentes escritores usan dictado de diferentes formas. Asi es como.",
        "workflow1Title": "Paginas Matutinas y Diarios",
        "workflow1Desc": "Captura pensamientos de flujo de conciencia primero. Sin editar, solo voz. 10-15 minutos se convierten en 2,000+ palabras.",
        "workflow2Title": "Sesiones de Poder de Primer Borrador",
        "workflow2Desc": "Dicta 2,000-5,000 palabras en una sesion. Hablar mantiene el impulso narrativo. Edita despues.",
        "workflow3Title": "Escritura de Dialogos",
        "workflow3Desc": "Pronuncia las lineas de tu personaje. Escucha como suenan. El habla natural se convierte en dialogos autenticos.",
        "workflow4Title": "Esquematizacion y Lluvia de Ideas",
        "workflow4Desc": "Habla tu trama. Captura ideas verbalmente. Organiza despues. Pensar es mas rapido que teclear.",
        "workflow5Title": "Notas de Investigacion",
        "workflow5Desc": "Escucha un podcast, articulo o video. Narra puntos clave en Whisper Cheap. Toma de notas sin manos."
    },
    "tips": {
        "title": "Consejos para Escritores que Usan Dictado por Voz",
        "intro": "Algunas practicas hacen el dictado aun mas poderoso.",
        "tip1Title": "Pronuncia Tu Puntuacion",
        "tip1Desc": "Di 'punto', 'coma', 'signo de pregunta', 'signo de exclamacion' cuando los necesites. O edita en una segunda pasada.",
        "tip2Title": "Mantén Sesiones Cortas (15-20 min)",
        "tip2Desc": "Tu voz se cansa. Dicta en rafagas enfocadas, luego cambia a editar o leer.",
        "tip3Title": "Edita en Una Pasada Separada",
        "tip3Desc": "Primera pasada: dicta todo. Segunda pasada: edita. Separar redaccion de edicion acelera ambas.",
        "tip4Title": "Lee Tu Dialogo en Voz Alta",
        "tip4Desc": "Antes de dictar, lee la linea del personaje. Luego pronunciala naturalmente al microfono.",
        "tip5Title": "Minimiza el Ruido Ambiental",
        "tip5Desc": "Habitacion silenciosa = mejor precision. Si hay ruido, Whisper Cheap tiene VAD (deteccion de voz) para ignorar sonido de fondo."
    },
    "faqWriters": {
        "title": "Preguntas que Hacen los Escritores",
        "q1": "Entendera mi acento?",
        "a1": "Whisper Cheap esta entrenado en 99 idiomas y acentos. Es muy tolerante. Prueba con un dictado corto para ver como funciona con tu voz.",
        "q2": "Puedo dictar directamente en Scrivener, Word o Google Docs?",
        "a2": "Si. Presiona tu atajo (Ctrl+Espacio), dicta y suelta. El texto se pega donde este tu cursor—Word, Scrivener, Google Docs, Notion, cualquier lugar.",
        "q3": "Como manejo la puntuacion?",
        "a3": "Di la palabra de puntuacion ('punto', 'coma', 'guion') o agregala en tu pasada de edicion. Muchos escritores la saltan durante el dictado y limpian despues.",
        "q4": "Necesito editar todo?",
        "a4": "La precision es muy alta, pero si—espera una pasada de edicion ligera. Whisper Cheap no es perfecto, pero es lo suficientemente rapido para que el tiempo total sea mucho menor que teclear.",
        "q5": "Puedo usarlo para diferentes generos?",
        "a5": "Absolutamente. Ficcion literaria, romance, ciencia ficcion, no ficcion, guiones—tu voz funciona en todos. El dialogo especialmente se beneficia de la entrega hablada.",
        "q6": "Que si hay demasiado ruido de fondo?",
        "a6": "Whisper Cheap incluye deteccion de voz (VAD). Activala para ignorar silencio y ruido de fondo. Funciona mejor en ambientes silenciosos."
    },
    "cta": {
        "title": "Deja de Perder Ideas. Empieza a Escribir Mas Rapido.",
        "subtitle": "Tu proximo borrador te esta esperando. Descarga Whisper Cheap gratis.",
        "button": "Descargar Ahora"
    }
}

with open('src/dictionaries/es.json', 'w', encoding='utf-8') as f:
    json.dump(es_dict, f, ensure_ascii=False, indent=2)

print("Updated ES dictionary with writers section")
