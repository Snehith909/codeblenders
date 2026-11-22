import { useState } from 'react'
import { match } from '../api.js'

const ALL_QUESTIONS = [
  { key: 'age', label: 'Your age', type: 'number' },
  {
    key: 'occupation',
    label: 'Your work',
    type: 'select',
    options: ['', 'farmer', 'farm labourer', 'other'],
  },
  {
    key: 'land_acres',
    label: 'Land you own (acres)',
    type: 'number',
    step: 0.1,
    min: 0,
  },
  {
    key: 'is_income_tax_payer',
    label: 'Do you pay income tax?',
    type: 'select',
    options: ['', 'yes', 'no'],
  },
  { key: 'district', label: 'Your district', type: 'text' },
]

const PROFILE_KEYS = [
  'age',
  'gender',
  'occupation',
  'land_acres',
  'land_ownership',
  'annual_income',
  'category',
  'district',
  'has_bank_account',
  'is_income_tax_payer',
]

function toNullableString(value) {
  return typeof value === 'string' && value.trim() !== '' ? value : null
}

function prefill(base) {
  const out = {}
  if (base.age != null) out.age = String(base.age)
  if (base.occupation) out.occupation = base.occupation
  if (base.land_acres != null) out.land_acres = String(base.land_acres)
  if (base.is_income_tax_payer === true) out.is_income_tax_payer = 'yes'
  if (base.is_income_tax_payer === false) out.is_income_tax_payer = 'no'
  if (base.district) out.district = base.district
  return out
}

function buildProfile(base, answers) {
  const built = {}
  for (const key of PROFILE_KEYS) {
    built[key] = base[key] !== undefined ? base[key] : null
  }
  const ageNum = parseInt(answers.age, 10)
  built.age = Number.isNaN(ageNum) ? null : ageNum

  const acres = parseFloat(answers.land_acres)
  built.land_acres = Number.isNaN(acres) ? null : acres

  if (answers.is_income_tax_payer === 'yes') built.is_income_tax_payer = true
  else if (answers.is_income_tax_payer === 'no') built.is_income_tax_payer = false
  else built.is_income_tax_payer = null

  built.occupation = toNullableString(answers.occupation)
  built.district = toNullableString(answers.district)
  return built
}

export default function Questions({ go, profile, missing, onResults }) {
  const questions =
    !missing || missing.length === 0
      ? ALL_QUESTIONS
      : ALL_QUESTIONS.filter((q) => missing.includes(q.key))

  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState(() => prefill(profile || {}))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const total = questions.length
  const question = questions[index]

  function setAnswer(value) {
    setAnswers((prev) => ({ ...prev, [question.key]: value }))
  }

  async function handleNext() {
    if (index < total - 1) {
      setIndex(index + 1)
      return
    }
    setLoading(true)
    setError('')
    try {
      const built = buildProfile(profile || {}, answers)
      const data = await match({ profile: built })
      onResults((data && data.results) || [])
      go('results')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (total === 0) {
    return (
      <section>
        <p>No questions to ask.</p>
        <button
          type="button"
          className="btn"
          disabled={loading}
          onClick={handleNext}
        >
          See schemes
        </button>
      </section>
    )
  }

  const value = answers[question.key] ?? ''
  const inputId = `q-${question.key}`

  let input
  if (question.type === 'select') {
    input = (
      <select id={inputId} value={value} onChange={(e) => setAnswer(e.target.value)}>
        {question.options.map((opt) => (
          <option key={opt} value={opt}>
            {opt === '' ? 'Select' : opt}
          </option>
        ))}
      </select>
    )
  } else {
    input = (
      <input
        id={inputId}
        type={question.type}
        step={question.step}
        min={question.min}
        value={value}
        onChange={(e) => setAnswer(e.target.value)}
      />
    )
  }

  const isLast = index === total - 1

  return (
    <section>
      <p>
        Progress: question {index + 1} of {total}
      </p>
      <label htmlFor={inputId}>{question.label}</label>
      {input}
      {error && <p className="error">{error}</p>}
      <div>
        {index > 0 && (
          <button
            type="button"
            className="btn-secondary"
            disabled={loading}
            onClick={() => setIndex(index - 1)}
          >
            Back
          </button>
        )}
        <button
          type="button"
          className="btn"
          disabled={loading}
          onClick={handleNext}
        >
          {isLast ? 'See schemes' : 'Next'}
        </button>
      </div>
    </section>
  )
}
