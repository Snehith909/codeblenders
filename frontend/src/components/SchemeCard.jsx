import { useState } from 'react'
import StatusBadge from './StatusBadge.jsx'
import WhyList from './WhyList.jsx'

export default function SchemeCard({ result, name, benefit, onOpen }) {
  const [open, setOpen] = useState(false)
  const {
    scheme_id,
    status,
    matched_rules = [],
    failed_rules = [],
    unknown_rules = [],
  } = result
  const missing = unknown_rules.map((r) => r.reason).join(', ')

  return (
    <article className="card">
      <StatusBadge status={status} />
      <h3>{name}</h3>
      <p>
        <strong>What you get:</strong> {benefit}
      </p>
      {status === 'maybe' && <p className="muted">Missing: {missing}</p>}
      <button
        type="button"
        className="btn-secondary"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        Why?
      </button>
      {open && (
        <WhyList
          matched={matched_rules}
          failed={failed_rules}
          unknown={unknown_rules}
        />
      )}
      <button type="button" className="btn" onClick={() => onOpen(scheme_id)}>
        View details
      </button>
    </article>
  )
}


