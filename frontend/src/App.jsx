import { useState } from 'react'
import Describe from './pages/Describe.jsx'
import Questions from './pages/Questions.jsx'
import Results from './pages/Results.jsx'
import Scheme from './pages/Scheme.jsx'
import Tracker from './pages/Tracker.jsx'

const NAV = [
  { name: 'describe', label: 'Describe' },
  { name: 'results', label: 'Results' },
  { name: 'tracker', label: 'Tracker' },
]

function App() {
  const [screen, setScreen] = useState({ name: 'describe' })
  const [lastResults, setLastResults] = useState([])
  const [hint, setHint] = useState('')

  const go = (name, data = {}) => {
    setHint('')
    setScreen({ name, ...data })
  }

  const openResults = () => {
    go('results')
    if (lastResults.length === 0) setHint('Describe your situation first')
  }

  const renderScreen = () => {
    switch (screen.name) {
      case 'questions':
        return (
          <Questions
            go={go}
            profile={screen.profile}
            missing={screen.missing}
            onResults={setLastResults}
          />
        )
      case 'results':
        return <Results go={go} results={lastResults} />
      case 'scheme':
        return <Scheme go={go} schemeId={screen.schemeId} />
      case 'tracker':
        return <Tracker go={go} />
      default:
        return <Describe go={go} />
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Claim What's Yours</h1>
        <nav className="nav" aria-label="Main">
          {NAV.map((item) => (
            <button
              key={item.name}
              type="button"
              className={screen.name === item.name ? 'nav-btn active' : 'nav-btn'}
              aria-current={screen.name === item.name ? 'page' : undefined}
              onClick={item.name === 'results' ? openResults : () => go(item.name)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>
      {hint && <p className="muted" role="status">{hint}</p>}
      <main>{renderScreen()}</main>
    </div>
  )
}

export default App

