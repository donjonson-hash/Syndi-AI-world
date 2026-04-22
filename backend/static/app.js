const API_BASE = '';  // Используем относительные URL, т.к. статика на том же домене

// Состояние приложения
const state = {
  currentUser: null,
  testQuestions: [],
  currentQuestionIndex: 0,
  answers: [],
  matches: []
};

// DOM элементы
const steps = {
  profile: document.getElementById('step-profile'),
  test: document.getElementById('step-test'),
  matches: document.getElementById('step-matches')
};
const userStatus = document.getElementById('user-status');
const loader = document.getElementById('loader');

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  // Проверяем, есть ли сохранённый пользователь
  const savedUserId = localStorage.getItem('syndi_user_id');
  if (savedUserId) {
    loadUser(savedUserId);
  }
  setupEventListeners();
});

function setupEventListeners() {
  document.getElementById('profile-form').addEventListener('submit', handleProfileSubmit);
  
  // Обработчики для теста Big Five
  document.querySelectorAll('.likert button').forEach(btn => {
    btn.addEventListener('click', (e) => handleTestAnswer(e.target.value));
  });
  
  document.getElementById('skip-btn').addEventListener('click', () => handleMatchAction('skip'));
  document.getElementById('like-btn').addEventListener('click', () => handleMatchAction('like'));
  document.getElementById('refresh-matches').addEventListener('click', loadMatches);
}

// --- Работа с API ---
async function apiRequest(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) options.body = JSON.stringify(body);
  
  showLoader(true);
  try {
    const response = await fetch(API_BASE + endpoint, options);
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Ошибка запроса');
    }
    return await response.json();
  } finally {
    showLoader(false);
  }
}

function showLoader(show) {
  loader.classList.toggle('hidden', !show);
}

// --- Профиль ---
async function handleProfileSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const role = document.getElementById('role').value;
  const bio = document.getElementById('bio').value;
  
  // Создаём пользователя (эндпоинт зависит от реализации; предположим POST /users)
  try {
    const user = await apiRequest('/users', 'POST', {
      name, email, role, bio
    });
    state.currentUser = user;
    localStorage.setItem('syndi_user_id', user.id);
    userStatus.textContent = `${user.name} (${user.role})`;
    
    // Переходим к тесту
    await loadTest();
    showStep('test');
  } catch (error) {
    alert('Ошибка создания профиля: ' + error.message);
  }
}

async function loadUser(userId) {
  try {
    const user = await apiRequest(`/users/${userId}`);
    state.currentUser = user;
    userStatus.textContent = `${user.name} (${user.role})`;
    
    // Проверяем, пройден ли тест
    if (user.has_completed_test) {
      await loadMatches();
      showStep('matches');
    } else {
      await loadTest();
      showStep('test');
    }
  } catch (error) {
    localStorage.removeItem('syndi_user_id');
    showStep('profile');
  }
}

// --- Тест Big Five ---
async function loadTest() {
  try {
    const data = await apiRequest('/bigfive/questions');
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
  
  // Сброс выделения кнопок
  document.querySelectorAll('.likert button').forEach(btn => btn.classList.remove('selected'));
}

function handleTestAnswer(value) {
  const answerValue = parseInt(value);
  state.answers.push({
    question_id: state.testQuestions[state.currentQuestionIndex].id,
    value: answerValue
  });
  
  // Подсветка выбранной кнопки (опционально)
  document.querySelectorAll('.likert button').forEach(btn => {
    if (parseInt(btn.value) === answerValue) btn.classList.add('selected');
  });
  
  if (state.currentQuestionIndex < state.testQuestions.length - 1) {
    state.currentQuestionIndex++;
    renderQuestion();
  } else {
    submitTest();
  }
}

async function submitTest() {
  try {
    const result = await apiRequest('/bigfive/submit', 'POST', {
      user_id: state.currentUser.id,
      answers: state.answers
    });
    
    // Обновляем пользователя
    state.currentUser.has_completed_test = true;
    state.currentUser.big_five = result.profile;
    
    // Переходим к матчам
    await loadMatches();
    showStep('matches');
  } catch (error) {
    alert('Ошибка отправки теста: ' + error.message);
  }
}

// --- Матчи ---
async function loadMatches() {
  try {
    const data = await apiRequest(`/match/${state.currentUser.id}`);
    // API возвращает List[MatchCard] (массив напрямую), не {matches:[]}
    state.matches = Array.isArray(data) ? data : (data.matches || []);
    renderMatches();
  } catch (error) {
    alert('Ошибка загрузки матчей: ' + error.message);
  }
}

function renderMatches() {
  const container = document.getElementById('matches-container');
  if (!state.matches || state.matches.length === 0) {
    container.innerHTML = '<p>Пока нет подходящих кандидатов. Попробуй позже.</p>';
    return;
  }

  container.innerHTML = state.matches.map(match => {
    // Маппинг полей API ⇒ UI
    // API: candidate_id, total_score, why_there_is_a_chance, risks
    const candidateId  = match.candidate_id  || match.user_id || '?';
    const score        = match.total_score   ?? match.compatibility_score ?? 0;
    const why          = match.why_there_is_a_chance || match.why_text || '';
    const riskFlags    = match.risks         || match.risk_flags || [];
    const scoreDisplay = score <= 1 ? Math.round(score * 100) : Math.round(score);

    return `
    <div class="match-card" data-candidate-id="${candidateId}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <h3>Кандидат ${candidateId}</h3>
        <div class="match-score">${scoreDisplay}%</div>
      </div>
      ${why ? `<p style="margin:8px 0;color:#475569"><em>✨ ${why}</em></p>` : ''}
      ${riskFlags.length
        ? `<div class="risk-flags">⚠️ ${riskFlags.map(f => f.replace(/_/g,' ')).join(' · ')}</div>`
        : '<div style="color:#10b981;font-size:13px;margin-top:8px">✅ Нет риск-флагов</div>'}
    </div>`;
  }).join('');
}

function handleMatchAction(action) {
  // В MVP просто переходим к следующему кандидату или обновляем список
  // Можно добавить эндпоинт для фиксации решения (like/skip), но пока просто имитируем свайп
  if (state.matches.length > 0) {
    // Удаляем первый матч из локального списка (имитация)
    state.matches.shift();
    renderMatches();
  } else {
    loadMatches();
  }
}

// --- Навигация ---
function showStep(stepName) {
  Object.values(steps).forEach(el => el.classList.remove('active'));
  steps[stepName].classList.add('active');
}
