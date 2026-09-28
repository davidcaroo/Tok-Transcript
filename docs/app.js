/* ==========================================================================
   Tok-Transcript Landing Page Client-Side Logic & Interactivity
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // ------------------------------------------------------------------------
  // 1. Theme Management (Dark / Light Mode)
  // ------------------------------------------------------------------------
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const sunIcon = document.getElementById('sunIcon');
  const moonIcon = document.getElementById('moonIcon');
  const metaThemeColor = document.getElementById('meta-theme-color');

  const THEME_STORAGE_KEY = 'tok_transcript_theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);

    if (theme === 'light') {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
      if (metaThemeColor) metaThemeColor.setAttribute('content', '#f8fafc');
    } else {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
      if (metaThemeColor) metaThemeColor.setAttribute('content', '#080c14');
    }
  }

  // Detect initial theme preference
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    applyTheme('light');
  } else {
    applyTheme('dark');
  }

  // Theme toggle click handler
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }

  // ------------------------------------------------------------------------
  // 2. Interactive Mockup Tab Switcher
  // ------------------------------------------------------------------------
  const mockupTabs = document.querySelectorAll('.mockup-tab-btn');
  const mockupImage = document.getElementById('mainMockupImg');

  mockupTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      mockupTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      const targetImgSrc = tab.getAttribute('data-img');
      if (mockupImage && targetImgSrc) {
        mockupImage.style.opacity = '0.3';
        setTimeout(() => {
          mockupImage.src = targetImgSrc;
          mockupImage.style.opacity = '1';
        }, 150);
      }
    });
  });

  // ------------------------------------------------------------------------
  // 3. Interactive Transcription Simulator
  // ------------------------------------------------------------------------
  const simRunBtn = document.getElementById('simRunBtn');
  const simProgressContainer = document.getElementById('simProgressContainer');
  const simProgressBar = document.getElementById('simProgressBar');
  const simStatusText = document.getElementById('simStatusText');
  const simPercentText = document.getElementById('simPercentText');
  const simOutputBox = document.getElementById('simOutputBox');

  const simulatedTranscriptLines = [
    "[00:00.00 -> 00:03.20] ¡Hola a todos! Bienvenidos a este video donde les muestro",
    "[00:03.20 -> 00:06.85] cómo transcribir cualquier audio de TikTok a texto de manera 100% gratuita.",
    "[00:06.85 -> 00:10.50] Tok-Transcript corre localmente en tu ordenador gracias a Faster-Whisper,",
    "[00:10.50 -> 00:14.10] sin límites de tiempo y garantizando total privacidad de tus datos. 🚀"
  ];

  let isSimulating = false;

  if (simRunBtn) {
    simRunBtn.addEventListener('click', () => {
      if (isSimulating) return;
      isSimulating = true;

      simRunBtn.disabled = true;
      simProgressContainer.style.display = 'block';
      simProgressBar.style.width = '0%';
      simPercentText.textContent = '0%';
      simStatusText.textContent = 'Iniciando conexión con TikTok...';
      simOutputBox.innerHTML = '<span style="color: var(--brand-primary)">// Conectando con bypass curl_cffi...</span>\n';

      // Step 1: Downloading Audio (0% -> 35%)
      setTimeout(() => {
        simProgressBar.style.width = '35%';
        simPercentText.textContent = '35%';
        simStatusText.textContent = 'Extrayendo flujo de audio sin marcas de agua...';
        simOutputBox.innerHTML += '<span style="color: #10b981;">[OK]</span> Audio extraído: 1.8 MB (AAC 128kbps)\n';
      }, 600);

      // Step 2: FFmpeg conversion (35% -> 65%)
      setTimeout(() => {
        simProgressBar.style.width = '65%';
        simPercentText.textContent = '65%';
        simStatusText.textContent = 'Procesando formato con FFmpeg (16kHz Mono)...';
        simOutputBox.innerHTML += '<span style="color: #10b981;">[OK]</span> Muestreo acústico normalizado a 16000Hz\n';
      }, 1200);

      // Step 3: Whisper Inference (65% -> 90%)
      setTimeout(() => {
        simProgressBar.style.width = '90%';
        simPercentText.textContent = '90%';
        simStatusText.textContent = 'Ejecutando inferencia Faster-Whisper (INT8)...';
        simOutputBox.innerHTML += '<span style="color: var(--badge-text);">[IA]</span> Modelo Whisper cargado en memoria. Detectando segmentos...\n\n';
      }, 1800);

      // Step 4: Finished! (100%)
      setTimeout(() => {
        simProgressBar.style.width = '100%';
        simPercentText.textContent = '100%';
        simStatusText.textContent = '¡Transcripción completada con éxito en 2.3s!';
        
        simOutputBox.innerHTML += '<strong>--- RESULTADO DE LA TRANSCRIPCIÓN ---</strong>\n';
        simulatedTranscriptLines.forEach(line => {
          simOutputBox.innerHTML += line + '\n';
        });

        simRunBtn.disabled = false;
        simRunBtn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="1 4 1 10 7 10"></polyline><polyline points="23 20 23 14 17 14"></polyline><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path></svg>
          <span>Reiniciar Simulación</span>
        `;
        isSimulating = false;
      }, 2500);
    });
  }
});
