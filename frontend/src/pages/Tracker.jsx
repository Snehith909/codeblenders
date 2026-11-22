import { useEffect, useState } from "react";
import { listApplications, getSchemes, getReminders, updateApplication } from "../api.js";

const STATUSES = ["not_started", "documents_ready", "applied", "under_review", "approved", "rejected"];

export default function Tracker({ go }) {
  const [apps, setApps] = useState([]);
  const [schemes, setSchemes] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([listApplications(), getSchemes(), getReminders()])
      .then(([a, s, r]) => {
        if (!active) return;
        setApps(a || []);
        setSchemes(s || []);
        setReminders(r || []);
      })
      .catch((e) => { if (active) setError(e.message || "Could not load applications."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function schemeName(id) {
    const s = schemes.find((x) => x.id === id);
    return s ? s.name : id;
  }

  async function change(app, body) {
    setError("");
    try {
      const updated = await updateApplication(app.id, body);
      setApps((list) =>
        list.map((x) => (x.id === app.id ? { ...x, ...(updated || body) } : x))
      );
    } catch (e) {
      setError(e.message || "Could not update application.");
    }
  }

  return (
    <div>
      <h2>My applications</h2>
      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && apps.length === 0 && (
        <div>
          <p>No applications yet. Open a scheme and save it.</p>
          <button className="btn" onClick={() => go("results")}>Go to results</button>
        </div>
      )}

      {apps.map((app) => (
        <div key={app.id} className="card">
          <h3>{schemeName(app.scheme_id)}</h3>
          <label>
            Status{" "}
            <select value={app.status} onChange={(e) => change(app, { status: e.target.value })}>
              {STATUSES.map((st) => (
                <option key={st} value={st}>{st.replace(/_/g, " ")}</option>
              ))}
            </select>
          </label>
          {app.next_action && <p className="muted">{app.next_action}</p>}
          <label>
            Reminder date{" "}
            <input
              type="date"
              value={app.reminder_date || ""}
              onChange={(e) => change(app, { reminder_date: e.target.value })}
            />
          </label>
        </div>
      ))}

      <h3>Reminders</h3>
      {reminders.length === 0 ? (
        <p>No reminders yet.</p>
      ) : (
        <ul>
          {reminders.map((r, i) => (
            <li key={r.id ?? i}>
              {r.message} <span className="muted">{r.date}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
