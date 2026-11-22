import { useEffect, useState } from "react";
import { getScheme, createApplication } from "../api.js";

export default function Scheme({ go, schemeId }) {
  const [scheme, setScheme] = useState(null);
  const [error, setError] = useState("");
  const [checked, setChecked] = useState({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;
    getScheme(schemeId)
      .then((s) => { if (active) setScheme(s); })
      .catch((e) => { if (active) setError(e.message || "Could not load scheme."); });
    return () => { active = false; };
  }, [schemeId]);

  async function save() {
    setSaving(true);
    setError("");
    try {
      await createApplication(scheme.id);
      setSaved(true);
    } catch (e) {
      setError(e.message || "Could not save application.");
    } finally {
      setSaving(false);
    }
  }

  if (!scheme) {
    return (
      <div>
        {error ? <p className="error">{error}</p> : <p>Loading scheme...</p>}
        <button className="btn" onClick={() => go("results")}>Back to results</button>
      </div>
    );
  }

  const documents = scheme.documents || [];
  const steps = scheme.apply_steps || [];

  return (
    <div>
      <h2>{scheme.name}</h2>
      <p className="muted">{scheme.level} · {scheme.state}</p>
      <p>{scheme.summary}</p>
      <p><strong>Benefit:</strong> {scheme.benefit}</p>

      {scheme.needs_verification && (
        <p className="error">Needs verification: check the official source before you apply.</p>
      )}

      <h3>Documents</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {documents.map((doc, i) => (
          <li key={i}>
            <label>
              <input
                type="checkbox"
                checked={!!checked[i]}
                onChange={(e) => setChecked({ ...checked, [i]: e.target.checked })}
              />{" "}
              {typeof doc === "string" ? doc : doc.name}
            </label>
          </li>
        ))}
      </ul>

      <h3>How to apply</h3>
      <ol>
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>

      <p>
        <a href={scheme.source_url} target="_blank" rel="noopener noreferrer">Official website</a>
      </p>
      <p className="muted">
        {scheme.last_verified ? `Last verified: ${scheme.last_verified}` : "Not yet verified"}
      </p>

      {error && <p className="error">{error}</p>}

      {saved ? (
        <p>Saved. You can track it under Tracker.</p>
      ) : (
        <button className="btn" onClick={save} disabled={saving}>
          {saving ? "Saving..." : "Save to my applications"}
        </button>
      )}

      <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
        {saved && <button className="btn" onClick={() => go("tracker")}>Go to Tracker</button>}
        <button className="btn" onClick={() => go("results")}>Back to results</button>
      </div>
    </div>
  );
}
