import { useState } from 'react'
import { extract } from '../api.js'

const EXAMPLES = [
  'I am a farmer in Mandya with 2 acres, age 35',
  'I am a farm labourer, age 28, no land',
]

export default function Describe({ go }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleContinue() {
    setLoading(true)
    setError('')
    try {
      const response = await extract(text)
      if (response && response.profile) {
        go('questions', {
          profile: response.profile,
          missing: response.missing_fields || [],
        })
      } else {
        go('questions', { profile: {}, missing: [] })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h1>Tell us about yourself</h1>
      <label htmlFor="situation">
        Describe your situation in your own words
      </label>
      <textarea
        id="situation"
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div>
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            className="chip"
            onClick={() => setText(example)}
          >
            {example}
          </button>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      <button
        type="button"
        className="btn"
        disabled={loading}
        onClick={handleContinue}
      >
        Continue
      </button>
      <button
        type="button"
        className="btn-secondary"
        onClick={() => go('questions', { profile: {}, missing: [] })}
      >
        Skip and fill the form
      </button>
    </section>
  )
}
