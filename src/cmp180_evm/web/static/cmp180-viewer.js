const root = document.getElementById('cmp180Viewer');
const stage = document.getElementById('cmp180ViewerStage');
const loadButton = document.getElementById('cmp180Load');
const controls = document.getElementById('cmp180Controls');
const status = document.getElementById('cmp180ViewerStatus');
const rotateButton = document.getElementById('cmp180Rotate');
const fullButton = document.getElementById('cmp180Fullscreen');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const DEFAULT_ORBIT = '35deg 70deg 90%';
const copy = {
  zh: {
    load: '啟用 360° 檢視', loading: '正在載入 3D…', retry: '重新載入 3D',
    idle: '按一下載入立體模型，拖曳查看各個角度。',
    ready: '拖曳旋轉 · 滾輪／雙指縮放 · 聚焦模型後可用方向鍵。手機上下滑動仍可捲頁。',
    error: '3D 載入失敗或瀏覽器未支援 WebGL。已保留靜態圖，可重試。',
    front: '正面', rear: '背面', side: '側面', reset: '重設視角', rotate: '自動旋轉',
    pause: '暫停旋轉', fullscreen: '全螢幕', exit: '離開全螢幕', static: '靜態圖',
    note: '外觀參考模型；接口細節依照片估算。',
    alt: 'R&S CMP180 可旋轉立體模型；方向鍵旋轉，Page Up／Page Down 縮放。',
    zoomIn: '放大', zoomOut: '縮小', fullscreenError: '瀏覽器無法開啟全螢幕，仍可在此拖曳與縮放。',
  },
  en: {
    load: 'Explore in 360°', loading: 'Loading 3D…', retry: 'Retry 3D',
    idle: 'Load the 3D model, then drag to explore every angle.',
    ready: 'Drag to orbit · Scroll / pinch to zoom · Arrow keys when focused. Vertical swipes still scroll the page.',
    error: '3D could not load or WebGL is unavailable. The still image is available; you can retry.',
    front: 'Front', rear: 'Rear', side: 'Side', reset: 'Reset view', rotate: 'Auto rotate',
    pause: 'Pause rotation', fullscreen: 'Fullscreen', exit: 'Exit fullscreen', static: 'Still image',
    note: 'Exterior reference model; connector details are estimated from photos.',
    alt: 'Rotatable R&S CMP180 model. Arrow keys orbit; Page Up / Page Down zoom.',
    zoomIn: 'Zoom in', zoomOut: 'Zoom out', fullscreenError: 'Fullscreen is unavailable. Drag and zoom are still available here.',
  },
};
const cameraAnnouncements = {
  zh: { left: '左側', right: '右側', front: '正面', back: '背面',
    'upper-left': '左上方', 'upper-right': '右上方', 'upper-front': '正面上方', 'upper-back': '背面上方',
    'lower-left': '左下方', 'lower-right': '右下方', 'lower-front': '正面下方', 'lower-back': '背面下方',
    'interaction-prompt': '' },
  en: { left: 'Left', right: 'Right', front: 'Front', back: 'Rear',
    'upper-left': 'Upper left', 'upper-right': 'Upper right', 'upper-front': 'Upper front', 'upper-back': 'Upper rear',
    'lower-left': 'Lower left', 'lower-right': 'Lower right', 'lower-front': 'Lower front', 'lower-back': 'Lower rear',
    'interaction-prompt': '' },
};
let viewer = null;
let generation = 0;
let timeout;
let rotating = false;
let visible = true;
let statusKey = 'idle';
let progress = 0;
const words = () => copy[document.documentElement.lang === 'en' ? 'en' : 'zh'];

function translate() {
  const text = words();
  root.querySelectorAll('[data-viewer-text]').forEach(element => { element.textContent = text[element.dataset.viewerText]; });
  loadButton.textContent = text[root.dataset.state === 'loading' ? 'loading' : root.dataset.state === 'error' ? 'retry' : 'load'];
  status.textContent = text[statusKey] + (statusKey === 'loading' && progress ? ` ${progress}%` : '');
  rotateButton.textContent = text[rotating ? 'pause' : 'rotate'];
  rotateButton.setAttribute('aria-pressed', String(rotating));
  fullButton.textContent = text[document.fullscreenElement === root ? 'exit' : 'fullscreen'];
  document.getElementById('cmp180ZoomIn').setAttribute('aria-label', text.zoomIn);
  document.getElementById('cmp180ZoomOut').setAttribute('aria-label', text.zoomOut);
  if (viewer) {
    viewer.alt = text.alt;
    viewer.a11y = cameraAnnouncements[document.documentElement.lang === 'en' ? 'en' : 'zh'];
  }
}

function syncRotation() {
  if (viewer) viewer.autoRotate = rotating && visible && !document.hidden;
  rotateButton.setAttribute('aria-pressed', String(rotating));
  rotateButton.textContent = words()[rotating ? 'pause' : 'rotate'];
}

function release(state = 'idle') {
  // 失敗、逾時或回到靜態圖時，使舊載入回呼失效，釋放模型並恢復可重試狀態。
  generation += 1;
  clearTimeout(timeout);
  if (viewer) { viewer.autoRotate = false; viewer.remove(); viewer = null; }
  if (document.fullscreenElement === root) document.exitFullscreen().catch(() => {});
  rotating = false;
  root.dataset.state = state;
  root.setAttribute('aria-busy', 'false');
  controls.hidden = true;
  loadButton.disabled = false;
  progress = 0;
  statusKey = state;
  translate();
}

async function load() {
  if (root.dataset.state === 'loading' || root.dataset.state === 'ready') return;
  const retry = root.dataset.state === 'error';
  const token = ++generation;
  root.dataset.state = 'loading';
  root.setAttribute('aria-busy', 'true');
  statusKey = 'loading';
  loadButton.disabled = true;
  translate();
  timeout = setTimeout(() => { if (token === generation) release('error'); }, 45000);
  try {
    // 自動載入本機固定版本；所有互動只改相機，不呼叫量測或儀器 API。
    if (!customElements.get('model-viewer')) await import(`./vendor/model-viewer/model-viewer.min.js?attempt=${token}`);
    if (token !== generation) return;
    viewer = document.createElement('model-viewer');
    const current = viewer;
    const attributes = {
      'camera-controls': '', 'disable-pan': '', 'disable-tap': '', 'touch-action': 'pan-y',
      'camera-orbit': DEFAULT_ORBIT, 'min-camera-orbit': 'auto 5deg 65%',
      'max-camera-orbit': 'auto 175deg 180%', 'field-of-view': '30deg',
      'min-field-of-view': '30deg', 'max-field-of-view': '30deg',
      'interaction-prompt': 'none', 'environment-image': 'neutral',
      'shadow-intensity': '0.3', 'shadow-softness': '1', exposure: '0.9', 'rotation-per-second': '18deg',
      'auto-rotate-delay': '0', loading: 'eager', reveal: 'auto',
      alt: words().alt, 'aria-describedby': 'cmp180ViewerStatus',
    };
    for (const [key, value] of Object.entries(attributes)) current.setAttribute(key, value);
    current.addEventListener('load', () => {
      if (token !== generation) return;
      clearTimeout(timeout);
      root.dataset.state = 'ready';
      root.setAttribute('aria-busy', 'false');
      statusKey = 'ready';
      controls.hidden = false;
      // 首次載入即自轉，但尊重減少動態偏好；自動載入不可搶走使用者焦點。
      rotating = !reducedMotion.matches;
      syncRotation();
      translate();
      if (document.activeElement === loadButton) root.querySelector('[data-viewer-orbit]').focus({ preventScroll: true });
    }, { once: true });
    current.addEventListener('error', () => { if (token === generation) release('error'); });
    current.addEventListener('progress', event => {
      if (token !== generation || root.dataset.state !== 'loading') return;
      const next = Math.floor(event.detail.totalProgress * 10) * 10;
      if (next !== progress) { progress = next; translate(); }
    });
    current.addEventListener('camera-change', event => {
      // 使用者拖曳後停止自轉，避免模型與手勢互相拉扯。
      if (event.detail.source === 'user-interaction' && rotating) { rotating = false; syncRotation(); }
    });
    stage.append(current);
    // 失敗資產可能仍在檢視器 Promise cache；重試換 URL，避免再次取得已拒絕的 Promise。
    current.src = '/assets/cmp180-web.glb' + (retry ? `?retry=${token}` : '');
  } catch { if (token === generation) release('error'); }
}

function setView(orbit) {
  if (!viewer) return;
  rotating = false;
  syncRotation();
  viewer.resetTurntableRotation();
  viewer.cameraOrbit = orbit;
  viewer.fieldOfView = '30deg';
  if (reducedMotion.matches) viewer.jumpCameraToGoal();
}

loadButton.addEventListener('click', load);
root.querySelectorAll('[data-viewer-orbit]').forEach(button => button.addEventListener('click', () => setView(button.dataset.viewerOrbit)));
document.getElementById('cmp180Reset').addEventListener('click', () => setView(DEFAULT_ORBIT));
document.getElementById('cmp180ZoomIn').addEventListener('click', () => { if (viewer) viewer.zoom(2); });
document.getElementById('cmp180ZoomOut').addEventListener('click', () => { if (viewer) viewer.zoom(-2); });
rotateButton.addEventListener('click', () => { rotating = !rotating; syncRotation(); });
document.getElementById('cmp180Static').addEventListener('click', () => { release(); loadButton.focus(); });
if (!root.requestFullscreen || !document.fullscreenEnabled) fullButton.hidden = true;
fullButton.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement === root) await document.exitFullscreen();
    else await root.requestFullscreen();
  } catch { statusKey = 'fullscreenError'; translate(); }
});
document.addEventListener('fullscreenchange', translate);
document.addEventListener('visibilitychange', syncRotation);
new IntersectionObserver(entries => { visible = entries[0].isIntersecting; syncRotation(); }).observe(root);
// 減少動態偏好切換時立即暫停，避免突然恢復動畫。
reducedMotion.addEventListener('change', () => { rotating = false; syncRotation(); });
window.addEventListener('cmp180-language-change', translate);
window.addEventListener('pagehide', () => release());
translate();
// 進入頁面即載入外觀模型；不涉及儀器連線或 RF 狀態。
load();
