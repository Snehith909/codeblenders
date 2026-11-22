export default function WhyList({ matched = [], failed = [], unknown = [] }) {
  const sections = [
    { title: 'Matched', items: matched, icon: '✓' },
    { title: 'Not met', items: failed, icon: '✕' },
    { title: 'Missing information', items: unknown, icon: '?' },
  ]

  return (
    <div className="why">
      {sections
        .filter((s) => s.items.length > 0)
        .map((s) => (
          <section key={s.title}>
            <h3>{s.title}</h3>
            <ul>
              {s.items.map((item, i) => (
                <li key={`${item.id}-${i}`}>
                  <span aria-hidden="true">{s.icon} </span>
                  {item.reason}
                </li>
              ))}
            </ul>
          </section>
        ))}
    </div>
  )
}


