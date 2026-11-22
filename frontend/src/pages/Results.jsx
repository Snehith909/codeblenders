import { useEffect, useState } from 'react'
import { getSchemes } from '../api.js'
import SchemeCard from '../components/SchemeCard.jsx'

export default function Results({ go, results }) {
  const [map, setMap] = useState({})

  useEffect(() => {
    let cancelled = false
    getSchemes()
      .then((schemes) => {
        if (cancelled) return
        const byId = {}
        for (const s of schemes || []) byId[s.id] = s
        setMap(byId)
      })
      .catch(() => {
        // names fall back to scheme ids if the list cannot be loaded
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (!results || results.length === 0) {
    return (
      <section>
        <h1>No results yet</h1>
        <button type="button" className="btn" onClick={() => go('describe')}>
          Describe your situation
        </button>
      </section>
    )
  }

  return (
    <section>
      <h1>Schemes for you</h1>
      <p className="muted">
        These are likely eligible or maybe, based on what you told us. This is
        not a final decision.
      </p>
      {results.map((r) => (
        <SchemeCard
          key={r.scheme_id}
          result={r}
          name={map[r.scheme_id]?.name || r.scheme_id}
          benefit={map[r.scheme_id]?.benefit || ''}
          onOpen={(id) => go('scheme', { schemeId: id })}
        />
      ))}
    </section>
  )
}
