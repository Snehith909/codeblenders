const LABELS = {
  likely_eligible: { text: 'Likely eligible', cls: 'badge-green', icon: '✓' },
  maybe: { text: 'Maybe', cls: 'badge-amber', icon: '?' },
  not_eligible: { text: 'Not eligible', cls: 'badge-grey', icon: '✕' },
}

export default function StatusBadge({ status }) {
  const info = LABELS[status] || LABELS.not_eligible
  return (
    <span className={`badge ${info.cls}`}>
      <span aria-hidden="true">{info.icon} </span>
      {info.text}
    </span>
  )
}

