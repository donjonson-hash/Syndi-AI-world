import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Atom, Zap, Calendar, MessageSquare, Clock, AlertTriangle, Star } from 'lucide-react'

interface NumerologyResult {
  life_path_number: number
  expression_number: number
  quantum_randomness_score: number
  destiny_forecast: string
  element: string
  ruling_planet: string
}

interface OracleResult {
  answer: string
  probability: number
  quantum_basis: string
  esoteric_overlay: string
  recommended_action: string
}

export default function QuantumDestinyPage() {
  const [activeTab, setActiveTab] = useState<'numerology' | 'oracle' | 'timeline'>('numerology')
  const [birthDate, setBirthDate] = useState('')
  const [name, setName] = useState('')
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [numResult, setNumResult] = useState<NumerologyResult | null>(null)
  const [oracleResult, setOracleResult] = useState<OracleResult | null>(null)

  const handleNumerology = async () => {
    setLoading(true)
    // Mock API call — replace with real fetch to /api/v1/quantum/numerology
    setTimeout(() => {
      setNumResult({
        life_path_number: 7,
        expression_number: 3,
        quantum_randomness_score: 0.8472,
        destiny_forecast: "Анализ и духовность. Grover's algorithm: быстрый поход к истине. Квантовая случайность высока — Вселенная активно вмешивается.",
        element: "Water",
        ruling_planet: "Neptune",
      })
      setLoading(false)
    }, 1500)
  }

  const handleOracle = async () => {
    setLoading(true)
    setTimeout(() => {
      setOracleResult({
        answer: "Однозначно да. Высокая вероятность |1⟩. Вселенная на вашей стороне.",
        probability: 0.89,
        quantum_basis: "Y-basis",
        esoteric_overlay: "Юпитер экспансивен — удача на стороне масштабирования.",
        recommended_action: "Масштабируйте решение.",
      })
      setLoading(false)
    }, 2000)
  }

  const elementColors: Record<string, string> = {
    Fire: 'text-orange-400',
    Water: 'text-blue-400',
    Air: 'text-cyan-300',
    Earth: 'text-green-400',
  }

  return (
    <div className="min-h-[calc(100vh-64px)] bg-syndi-bg px-6 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-sm font-medium mb-4">
            <Atom className="w-4 h-4 animate-spin" />
            IONQ Quantum Powered
          </div>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-white mb-2">
            Quantum <span className="text-purple-400">Destiny Engine</span>
          </h1>
          <p className="text-syndi-text-secondary max-w-lg mx-auto">
            Квантовые вычисления + нумерология + астрология для предсказания судьбы вашей команды
          </p>
        </motion.div>

        {/* Tabs */}
        <div className="flex justify-center gap-2 mb-8">
          {[
            { id: 'numerology', label: 'Нумерология', icon: Star },
            { id: 'oracle', label: 'Квантовый Оракул', icon: Sparkles },
            { id: 'timeline', label: 'Таймлайн', icon: Clock },
          ].map((tab) => {
            const Icon = tab.icon
            const active = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                    : 'text-syndi-text-muted hover:text-syndi-text-primary border border-transparent'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Numerology Tab */}
        {activeTab === 'numerology' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="card-syndi max-w-lg mx-auto">
              <h3 className="font-display text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Star className="w-5 h-5 text-purple-400" />
                Квантовая нумерологическая карта
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-syndi-text-secondary mb-1 block">Дата рождения (ДД.ММ.ГГГГ)</label>
                  <input
                    type="text"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    placeholder="15.03.1995"
                    className="input-syndi w-full"
                  />
                </div>
                <div>
                  <label className="text-sm text-syndi-text-secondary mb-1 block">Имя</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Алексей"
                    className="input-syndi w-full"
                  />
                </div>
                <button
                  onClick={handleNumerology}
                  disabled={loading || !birthDate || !name}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-30"
                >
                  {loading ? <Atom className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                  {loading ? 'Квантовое вычисление...' : 'Рассчитать судьбу'}
                </button>
              </div>
            </div>

            {numResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-4"
              >
                <div className="card-syndi text-center">
                  <div className="text-5xl font-bold text-purple-400 mb-2">{numResult.life_path_number}</div>
                  <div className="text-sm text-syndi-text-secondary">Число жизненного пути</div>
                </div>
                <div className="card-syndi text-center">
                  <div className="text-5xl font-bold text-cyan-400 mb-2">{numResult.expression_number}</div>
                  <div className="text-sm text-syndi-text-secondary">Число экспрессии</div>
                </div>
                <div className="card-syndi text-center">
                  <div className={`text-3xl font-bold mb-2 ${elementColors[numResult.element] || 'text-white'}`}>
                    {numResult.element}
                  </div>
                  <div className="text-sm text-syndi-text-secondary">Стихия</div>
                </div>
                <div className="card-syndi text-center">
                  <div className="text-3xl font-bold text-yellow-400 mb-2">{numResult.ruling_planet}</div>
                  <div className="text-sm text-syndi-text-secondary">Управляющая планета</div>
                </div>
                <div className="card-syndi md:col-span-2">
                  <div className="flex items-center gap-2 mb-2">
                    <Atom className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-purple-400">Квантовая случайность: {numResult.quantum_randomness_score}</span>
                  </div>
                  <p className="text-syndi-text-secondary leading-relaxed">{numResult.destiny_forecast}</p>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Oracle Tab */}
        {activeTab === 'oracle' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="card-syndi max-w-lg mx-auto">
              <h3 className="font-display text-lg font-bold text-white mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                Задайте вопрос Вселенной
              </h3>
              <div className="space-y-4">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Стоит ли нам запускать продукт в следующем месяце? Будет ли наша команда успешной?"
                  className="input-syndi w-full h-24 resize-none"
                />
                <button
                  onClick={handleOracle}
                  disabled={loading || !question}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-30"
                >
                  {loading ? <Atom className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                  {loading ? 'Коллапс волновой функции...' : 'Спросить квантовый оракул'}
                </button>
              </div>
            </div>

            {oracleResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="card-syndi border-purple-500/30"
              >
                <div className="text-center mb-6">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs mb-4">
                    <Atom className="w-3 h-3" />
                    Базис: {oracleResult.quantum_basis} | Вероятность: {Math.round(oracleResult.probability * 100)}%
                  </div>
                  <p className="text-xl text-white font-medium leading-relaxed">{oracleResult.answer}</p>
                </div>
                <div className="space-y-3 border-t border-syndi-border pt-4">
                  <div className="flex items-start gap-3">
                    <Star className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <p className="text-syndi-text-secondary">{oracleResult.esoteric_overlay}</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <Zap className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <p className="text-cyan-400">{oracleResult.recommended_action}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="card-syndi">
              <h3 className="font-display text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-400" />
                Квантовый таймлайн проекта
              </h3>
              <div className="space-y-4">
                {[
                  { phase: 'Seed', months: '1-3', focus: 'Команда + Продукт', state: 'Суперпозиция', color: 'text-blue-400' },
                  { phase: 'Validation', months: '4-6', focus: 'PMF + Пользователи', state: 'Измерение', color: 'text-green-400' },
                  { phase: 'Growth', months: '7-12', focus: 'Масштабирование', state: 'Запутанность', color: 'text-purple-400' },
                  { phase: 'Series A', months: '12-18', focus: 'Финансирование', state: 'Телепортация', color: 'text-yellow-400' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-syndi-bg-elevated">
                    <div className="w-12 h-12 rounded-full bg-syndi-surface flex items-center justify-center text-lg font-bold text-white">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{item.phase}</span>
                        <span className="text-xs text-syndi-text-muted">{item.months} мес.</span>
                      </div>
                      <p className="text-sm text-syndi-text-secondary">{item.focus}</p>
                    </div>
                    <div className={`text-xs font-medium ${item.color} px-2 py-1 rounded bg-syndi-bg`}>
                      {item.state}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card-syndi">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  Критические периоды
                </h4>
                {[
                  { period: 'Меркурий ретроградный', dates: '07.01-28.01', risk: 'Коммуникации' },
                  { period: 'Сатурн ретроградный', dates: '17.06-11.11', risk: 'Структура' },
                ].map((c, i) => (
                  <div key={i} className="py-2 border-b border-syndi-border last:border-0">
                    <p className="text-sm text-white">{c.period}</p>
                    <p className="text-xs text-syndi-text-muted">{c.dates} — {c.risk}</p>
                  </div>
                ))}
              </div>
              <div className="card-syndi">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Star className="w-4 h-4 text-green-400" />
                  Благоприятные даты
                </h4>
                {['15.05.2026', '22.06.2026', '07.09.2026', '11.11.2026', '21.12.2026'].map((d, i) => (
                  <div key={i} className="py-2 border-b border-syndi-border last:border-0 flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-syndi-teal" />
                    <span className="text-sm text-syndi-text-secondary">{d}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
