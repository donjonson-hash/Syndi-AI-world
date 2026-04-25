const API_BASE = '';
const TOKEN_KEY = 'syndi_token';
const USER_KEY = 'syndi_user';

const state = {
  token: localStorage.getItem(TOKEN_KEY) || null,
  currentUser: null,            // {id, email, name, role?}
  authMode: 'login',            // 'login' | 'register'
  testQuestions: [],
  currentQuestionIndex: 0,
  answers: [],
  matches: [],                  // карточки для свайпа (Discover)
  currentTab: null,
  chatHistory: [],
};

const steps = {
  auth:      document.getElementById('step-auth'),
  profile:   document.getElementById('step-profile'),
  test:      document.getElementById('step-test'),
  matches:   document.getElementById('step-matches'),
  mymatches: document.getElementById('step-mymatches'),
  avatar:    document.getElementById('step-avatar'),
  chat:      document.getElementById('step-chat'),
};

const userStatus = document.getElementById('user-status');
const loader = document.getElementById('loader');
const tabBar = document.getElementById('tab-bar');

// ═══════════════════════════════════════════════════════════════════════════
// Init
// ═══════════════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  switchAuthMode('login');
  if (state.token) {
    bootstrapAuthenticated();
  } else {
    showStep('auth');
  }
});

function setupEventListeners() {
  // Auth tabs
  document.querySelectorAll('.auth-tab').forEach(btn => {
    btn.addEventListener('click', () => switchAuthMode(btn.dataset.mode));
  });
  document.getElementById('auth-form').addEventListener('submit', handleAuthSubmit);

  // Profile form
  document.getElementById('profile-form').addEventListener('submit', handleProfileSubmit);

  // Big Five test
  document.querySelectorAll('.likert button').forEach(btn => {
    btn.addEventListener('click', (e) => handleTestAnswer(e.target.value));
  });

  // Discover refresh
  document.getElementById('refresh-matches').addEventListener('click', loadMatches);

  // Tab bar
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Chat
  document.getElementById('chat-form').addEventListener('submit', handleChatSubmit);
}

// ═══════════════════════════════════════════════════════════════════════════
// API helper (with JWT)
// ═══════════════════════════════════════════════════════════════════════════
async function apiRequest(endpoint, method = 'GET', body = null, opts = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  if (!opts.silent) showLoader(true);
  try {
    const response = await fetch(API_BASE + endpoint, options);
    if (response.status === 401) {
      logout();
      throw new Error('Сессия истекла, войдите снова');
    }
    if (!response.ok) {
      let detail = 'Ошибка запроса';
      try {
        const err = await response.json();
        detail = err.detail || JSON.stringify(err);
      } catch (_) {}
      const e = new Error(detail);
      e.status = response.status;
      throw e;
    }
    if (response.status === 204) return null;
    return await response.json();
  } finally {
    if (!opts.silent) showLoader(false);
  }
}

function showLoader(show) {
  loader.classList.toggle('hidden', !show);
}

// ═══════════════════════════════════════════════════════════════════════════
// Auth
// ═══════════════════════════════════════════════════════════════════════════
function switchAuthMode(mode) {
  state.authMode = mode;
  document.querySelectorAll('.auth-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.mode === mode);
  });
  document.getElementById('auth-submit').textContent =
    mode === 'register' ? 'Зарегистрироваться' : 'Войти';
  document.getElementById('auth-name').style.display =
    mode === 'register' ? 'block' : 'none';
  hideAuthError();
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  hideAuthError();
  const email = document.getElementById('auth-email').value.trim();
  const password = document.getElementById('auth-password').value;
  const name = document.getElementById('auth-name').value.trim();

  try {
    let resp;
    if (state.authMode === 'register') {
      resp = await apiRequest('/api/v1/auth/register', 'POST', { email, password, name });
    } else {
      resp = await apiRequest('/api/v1/auth/login', 'POST', { email, password });
    }
    state.token = resp.token;
    localStorage.setItem(TOKEN_KEY, resp.token);
    await bootstrapAuthenticated();
  } catch (err) {
    showAuthError(err.message);
  }
}

function showAuthError(msg) {
  const el = document.getElementById('auth-error');
  el.textContent = msg;
  el.classList.remove('hidden');
}
function hideAuthError() {
  document.getElementById('auth-error').classList.add('hidden');
}

function logout() {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  tabBar.classList.add('hidden');
  userStatus.textContent = 'не авторизован';
  showStep('auth');
}

async function bootstrapAuthenticated() {
  try {
    const me = await apiRequest('/api/v1/auth/me');
    state.currentUser = me;
    localStorage.setItem(USER_KEY, JSON.stringify(me));
    userStatus.textContent = `${me.name || me.email}`;
    tabBar.classList.remove('hidden');

    // Решаем, куда вести: если профиль (founder_profile) есть → discover, иначе профиль → тест
    const hasProfile = await checkHasFounderProfile();
    if (hasProfile) {
      switchTab('matches');
    } else {
      tabBar.classList.add('hidden');
      showStep('profile');
    }
  } catch (err) {
    logout();
  }
}

async function checkHasFounderProfile() {
  try {
    const resp = await apiRequest('/api/v1/profile/me', 'GET', null, { silent: true });
    return !!(resp && resp.id);
  } catch (_) {
    return false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Profile + Big Five
// ═══════════════════════════════════════════════════════════════════════════
async function handleProfileSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const role = document.getElementById('role').value;
  const bio = document.getElementById('bio').value;

  try {
    // Обновляем профиль через PATCH
    await apiRequest('/api/v1/profile/me', 'PATCH', {
      name,
      bio,
      primary_role: role,
    });
    state.currentUser.name = name;
    userStatus.textContent = name;

    await loadTest();
    showStep('test');
  } catch (error) {
    alert('Ошибка сохранения профиля: ' + error.message);
  }
}

async function loadTest() {
  try {
    const data = await apiRequest('/api/v1/test/questions');
    state.testQuestions = data.questions;
    state.currentQuestionIndex = 0;
    state.answers = [];
    renderQuestion();
  } catch (error) {
    alert('Не удалось загрузить тест: ' + error.message);
  }
}

function renderQuestion() {
  const q = state.testQuestions[state.currentQuestionIndex];
  document.getElementById('question-text').textContent = q.text;
  document.getElementById('progress').textContent =
    `Вопрос ${state.currentQuestionIndex + 1} / ${state.testQuestions.length}`;
  document.querySelectorAll('.likert button').forEach(b => b.classList.remove('selected'));
}

function handleTestAnswer(value) {
  const v = parseInt(value);
  state.answers.push({
    question_id: state.testQuestions[state.currentQuestionIndex].id,
    value: v,
  });
  document.querySelectorAll('.likert button').forEach(btn => {
    if (parseInt(btn.value) === v) btn.classList.add('selected');
  });

  if (state.currentQuestionIndex < state.testQuestions.length - 1) {
    state.currentQuestionIndex++;
    setTimeout(renderQuestion, 200);
  } else {
    submitTest();
  }
}

async function submitTest() {
  try {
    await apiRequest('/api/v1/test/submit', 'POST', {
      user_id: String(state.currentUser.id),
      answers: state.answers,
    });
    tabBar.classList.remove('hidden');
    switchTab('matches');
  } catch (error) {
    alert('Ошибка отправки теста: ' + error.message);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Discover (swipe cards)
// ═══════════════════════════════════════════════════════════════════════════
async function loadMatches() {
  try {
    const data = await apiRequest(
      `/api/v1/discover?user_id=${state.currentUser.id}&limit=10`
    );
    state.matches = (data && data.cards) || [];
    renderMatches();
  } catch (error) {
    if (error.status === 404) {
      // нет founder_profile или нет кандидатов
      state.matches = [];
      renderMatches();
      return;
    }
    showEmptyState('Не удалось загрузить кандидатов: ' + error.message);
  }
}

function renderMatches() {
  const container = document.getElementById('matches-container');
  container.innerHTML = '';

  if (!state.matches.length) {
    showEmptyState('Пока нет подходящих кандидатов. Попробуй позже.');
    return;
  }

  // Рисуем стек: топ-3 карточки видимы (для эффекта стека)
  const visible = state.matches.slice(0, 3);
  visible.forEach((card, idx) => {
    const el = buildCardElement(card, idx);
    container.appendChild(el);
  });

  // Свайп-индикаторы (на топовой карточке)
  const top = container.lastElementChild;
  if (top) attachSwipe(top);
}

function buildCardElement(card, idx) {
  const el = document.createElement('div');
  el.className = 'match-card';
  el.dataset.candidateId = card.candidate_user_id;
  el.style.zIndex = String(100 - idx);
  el.style.transform = `translateY(${idx * 6}px) scale(${1 - idx * 0.04})`;
  el.style.opacity = String(1 - idx * 0.15);

  const score = Math.round(Number(card.total_score) || 0);
  const risks = (card.risk_flags || []).filter(Boolean);

  el.innerHTML = `
    <div class="swipe-indicator left">NOPE</div>
    <div class="swipe-indicator right">LIKE</div>
    <div class="card-header">
      <div>
        <h3>${escapeHtml(card.candidate_name || 'Без имени')}</h3>
        <span class="role-tag">${escapeHtml(card.primary_role || 'founder')}</span>
      </div>
      <div class="match-score">${score}%</div>
    </div>
    <p class="why">${escapeHtml(card.why || 'Базовая совместимость')}</p>
    ${card.intent_goal ? `<p class="why"><strong>Цель:</strong> ${escapeHtml(card.intent_goal)}</p>` : ''}
    ${risks.length ? `<div class="risk-flags">⚠️ ${risks.map(escapeHtml).join(', ')}</div>` : ''}
  `;
  return el;
}

function showEmptyState(msg) {
  const container = document.getElementById('matches-container');
  container.innerHTML = `<div class="empty-state">${escapeHtml(msg)}</div>`;
}

// ─── Swipe mechanics ────────────────────────────────────────────────────────
function attachSwipe(cardEl) {
  let startX = 0, startY = 0, currX = 0, currY = 0;
  let dragging = false;

  const indLeft = cardEl.querySelector('.swipe-indicator.left');
  const indRight = cardEl.querySelector('.swipe-indicator.right');

  function onStart(x, y) {
    dragging = true;
    startX = x; startY = y;
    cardEl.classList.add('dragging');
  }
  function onMove(x, y) {
    if (!dragging) return;
    currX = x - startX;
    currY = y - startY;
    const rotate = currX / 20;
    cardEl.style.transform = `translate(${currX}px, ${currY * 0.3}px) rotate(${rotate}deg)`;

    if (indLeft && indRight) {
      indRight.style.opacity = String(Math.max(0, Math.min(1, currX / 100)));
      indLeft.style.opacity = String(Math.max(0, Math.min(1, -currX / 100)));
    }
  }
  function onEnd() {
    if (!dragging) return;
    dragging = false;
    cardEl.classList.remove('dragging');
    const threshold = 80;
    if (currX > threshold) {
      finishSwipe('right');
    } else if (currX < -threshold) {
      finishSwipe('left');
    } else {
      cardEl.style.transform = '';
      if (indLeft) indLeft.style.opacity = 0;
      if (indRight) indRight.style.opacity = 0;
    }
  }
  function finishSwipe(dir) {
    cardEl.classList.add(dir === 'right' ? 'gone-right' : 'gone-left');
    const candidateId = parseInt(cardEl.dataset.candidateId, 10);
    sendLike(candidateId, dir === 'right');
    setTimeout(() => {
      cardEl.remove();
      state.matches.shift();
      renderMatches();
    }, 320);
  }

  // Touch
  cardEl.addEventListener('touchstart', (e) => {
    const t = e.touches[0]; onStart(t.clientX, t.clientY);
  }, { passive: true });
  cardEl.addEventListener('touchmove', (e) => {
    const t = e.touches[0]; onMove(t.clientX, t.clientY);
  }, { passive: true });
  cardEl.addEventListener('touchend', onEnd);
  cardEl.addEventListener('touchcancel', onEnd);

  // Mouse
  cardEl.addEventListener('mousedown', (e) => {
    e.preventDefault(); onStart(e.clientX, e.clientY);
    const onMM = (ev) => onMove(ev.clientX, ev.clientY);
    const onMU = () => {
      onEnd();
      window.removeEventListener('mousemove', onMM);
      window.removeEventListener('mouseup', onMU);
    };
    window.addEventListener('mousemove', onMM);
    window.addEventListener('mouseup', onMU);
  });
}

async function sendLike(toUserId, isLike) {
  if (!state.currentUser || !toUserId) return;
  try {
    const resp = await apiRequest(`/api/v1/like/${toUserId}`, 'POST', {
      from_user_id: state.currentUser.id,
      is_like: isLike,
    }, { silent: true });
    if (resp && resp.is_match) {
      // Лёгкая нотификация
      flashToast(`💚 Это матч! ${resp.match_score ? '(' + resp.match_score + '%)' : ''}`);
    }
  } catch (err) {
    console.warn('Like failed:', err.message);
  }
}

function flashToast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = `
    position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
    background: var(--accent-grad); color: white; padding: 12px 20px;
    border-radius: 999px; font-weight: 600; z-index: 200;
    box-shadow: 0 8px 24px rgba(108,99,255,0.4);
    animation: bubbleIn 0.25s ease;
  `;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2400);
}

// ═══════════════════════════════════════════════════════════════════════════
// My matches list
// ═══════════════════════════════════════════════════════════════════════════
async function loadMyMatches() {
  const container = document.getElementById('mymatches-list');
  container.innerHTML = '';
  try {
    const resp = await apiRequest('/api/v1/matches');
    const items = (resp && resp.matches) || [];
    if (!items.length) {
      container.innerHTML = `<div class="empty-state">Пока нет взаимных матчей. Свайпай вправо в Discover!</div>`;
      return;
    }
    container.innerHTML = items.map(m => `
      <div class="match-item">
        <div class="name">${escapeHtml(m.partner_name || 'User #' + m.partner_user_id)}</div>
        ${m.match_score != null ? `<div class="score">${Math.round(m.match_score)}%</div>` : ''}
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Ошибка загрузки: ${escapeHtml(err.message)}</div>`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Avatar
// ═══════════════════════════════════════════════════════════════════════════
async function loadAvatar() {
  const container = document.getElementById('avatar-container');
  container.innerHTML = '';
  try {
    const a = await apiRequest('/api/v1/avatar/me');
    container.innerHTML = renderAvatarCard(a);
    const chatBtn = container.querySelector('#avatar-chat-btn');
    if (chatBtn) chatBtn.addEventListener('click', () => switchTab('chat'));
  } catch (err) {
    if (err.status === 404) {
      container.innerHTML = `
        <div class="avatar-empty">
          <div style="font-size:48px; margin-bottom:12px;">🤖</div>
          <div>Аватар появится после первого матча.</div>
          <div style="margin-top:8px; font-size:13px;">Свайпай вправо в Discover, чтобы получить взаимный лайк.</div>
        </div>
      `;
    } else {
      container.innerHTML = `<div class="avatar-empty">Не удалось загрузить аватар: ${escapeHtml(err.message)}</div>`;
    }
  }
}

function renderAvatarCard(a) {
  const prof = a.profession || {};
  const emo = a.emotional_state || {};
  const skills = (prof.core_skills || []).slice(0, 6);
  const initial = (a.founder_name || '?').trim().charAt(0).toUpperCase();
  return `
    <div class="avatar-card">
      <div class="avatar-pulse">${escapeHtml(initial)}</div>
      <div class="avatar-name">${escapeHtml(a.founder_name || 'Аватар')}</div>
      <div class="avatar-role">${escapeHtml(a.role_id || '')}</div>
      ${prof.title ? `<div class="avatar-title">${escapeHtml(prof.title)}</div>` : ''}
      <div class="avatar-mood">
        <span class="label">Настроение</span>
        ${escapeHtml(emo.mood_description || '—')}
      </div>
      ${emo.dominant_emotion ? `
        <div class="avatar-mood">
          <span class="label">Доминирующая эмоция</span>
          ${escapeHtml(emo.dominant_emotion)}
        </div>` : ''}
      ${skills.length ? `
        <div class="skill-tags">
          ${skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}
        </div>` : ''}
      <button id="avatar-chat-btn" class="primary-btn" style="margin-top:12px;">💬 Чат с Kristina</button>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// Chat with Kristina
// ═══════════════════════════════════════════════════════════════════════════
async function loadChatHistory() {
  const list = document.getElementById('chat-history');
  list.innerHTML = '';
  state.chatHistory = [];

  try {
    const resp = await apiRequest('/api/v1/kristina/history');
    const msgs = (resp && resp.messages) || [];
    msgs.forEach(m => {
      const role = m.role === 'assistant' ? 'kristina' : 'user';
      appendChatBubble(role, m.content || '', { mood: m.mood, mode: m.agent_mode });
    });
    if (!msgs.length) {
      appendChatBubble('kristina',
        'Привет! Я Kristina — UX-дизайнер и твой AI-помощник. Расскажи о своём проекте, и я помогу с подбором сооснователя.'
      );
    }
  } catch (err) {
    appendChatBubble('error', 'Не удалось загрузить историю: ' + err.message);
  }
  scrollChatBottom();
}

async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  appendChatBubble('user', text);
  scrollChatBottom();

  try {
    const resp = await apiRequest('/api/v1/kristina/chat', 'POST', {
      message: text,
      session_id: String(state.currentUser.id),
    }, { silent: true });
    appendChatBubble('kristina', resp.response || '...', {
      mood: resp.mood,
      mode: resp.mode,
    });
  } catch (err) {
    appendChatBubble('error', 'Kristina недоступна: ' + err.message);
  }
  scrollChatBottom();
}

function appendChatBubble(role, text, meta = {}) {
  const list = document.getElementById('chat-history');
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  list.appendChild(bubble);

  const tags = [];
  if (meta.mood) tags.push(`mood: ${meta.mood}`);
  if (meta.mode) tags.push(`mode: ${meta.mode}`);
  if (tags.length && role !== 'error') {
    const m = document.createElement('div');
    m.className = `bubble-meta ${role === 'user' ? 'user' : ''}`;
    m.textContent = tags.join(' · ');
    list.appendChild(m);
  }
}

function scrollChatBottom() {
  const list = document.getElementById('chat-history');
  list.scrollTop = list.scrollHeight;
}

// ═══════════════════════════════════════════════════════════════════════════
// Navigation
// ═══════════════════════════════════════════════════════════════════════════
function showStep(stepName) {
  Object.values(steps).forEach(el => el && el.classList.remove('active'));
  if (steps[stepName]) steps[stepName].classList.add('active');
}

function switchTab(tab) {
  state.currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  showStep(tab);

  if (tab === 'matches')   loadMatches();
  if (tab === 'mymatches') loadMyMatches();
  if (tab === 'avatar')    loadAvatar();
  if (tab === 'chat')      loadChatHistory();
}

// ═══════════════════════════════════════════════════════════════════════════
// Utils
// ═══════════════════════════════════════════════════════════════════════════
function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
