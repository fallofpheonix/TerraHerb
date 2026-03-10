import React, { useState } from 'react';
import './App.css';
import { Upload, Leaf, Search, Info, ShieldCheck, AlertTriangle, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function App() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped && dropped.type.startsWith('image/')) {
            setFile(dropped);
            setPreview(URL.createObjectURL(dropped));
            setResult(null);
            setError(null);
        }
    };

    const handleDragOver = (e) => e.preventDefault();

    const handleIdentify = async () => {
        if (!file) return;
        setIsProcessing(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await fetch(`${API_BASE}/identify`, {
                method: 'POST',
                body: formData,
            });

            if (!resp.ok) {
                const errData = await resp.json().catch(() => ({}));
                throw new Error(errData.detail || `Server error: ${resp.status}`);
            }

            const data = await resp.json();
            setResult(data);
        } catch (err) {
            setError(err.message || 'Failed to connect to the Terraherb API. Is the backend running?');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
    };

    const confidencePct = result ? Math.round(result.confidence * 100) : 0;
    const topPredictions = result?.top_predictions || [];
    const knowledge = result?.knowledge || {};
    const treatment = knowledge.treatment || {};

    return (
        <div className="app-container">
            <header className="hero-section">
                <div className="hero-badge">🌿 AI-Powered</div>
                <h1 className="hero-title">Terraherb AI</h1>
                <p className="hero-subtitle">
                    Deep Learning Plant Identification &amp; Botanical Intelligence
                </p>
            </header>

            <main>
                {!result ? (
                    <div className="glass-card">
                        <div
                            className="upload-area"
                            onClick={() => document.getElementById('fileInput').click()}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        >
                            <input
                                type="file"
                                id="fileInput"
                                hidden
                                onChange={handleFileChange}
                                accept="image/*"
                            />
                            {preview ? (
                                <img src={preview} alt="Upload Preview" className="plant-image-preview" />
                            ) : (
                                <>
                                    <Upload size={48} color="var(--leaf-secondary)" style={{ marginBottom: '1rem' }} />
                                    <h3>Upload Plant Image</h3>
                                    <p style={{ color: 'var(--text-dim)' }}>Drag and drop or click to select a leaf or crop image</p>
                                    <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                        Supports: JPG, PNG, WebP • Max 10MB
                                    </p>
                                </>
                            )}
                        </div>

                        {error && (
                            <div className="error-banner">
                                <AlertTriangle size={16} style={{ marginRight: '0.5rem', flexShrink: 0 }} />
                                {error}
                            </div>
                        )}

                        {file && (
                            <div style={{ textAlign: 'center', marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                                <button
                                    className="button-secondary"
                                    onClick={handleReset}
                                >
                                    Clear
                                </button>
                                <button
                                    className="button-primary"
                                    onClick={handleIdentify}
                                    disabled={isProcessing}
                                    id="identifyBtn"
                                >
                                    {isProcessing ? (
                                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <RefreshCw size={16} className="spin" /> Analyzing…
                                        </span>
                                    ) : 'Identify Species'}
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="results-grid">
                        {/* Image + Confidence */}
                        <div className="glass-card" style={{ padding: '1rem' }}>
                            <img src={preview} alt="Identified Plant" className="plant-image-preview" />
                            <div className="confidence-bar-wrap">
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>Confidence</span>
                                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: result.low_confidence ? 'var(--warn-color)' : 'var(--leaf-secondary)' }}>
                                        {confidencePct}%
                                    </span>
                                </div>
                                <div className="confidence-bar">
                                    <div
                                        className="confidence-fill"
                                        style={{
                                            width: `${confidencePct}%`,
                                            background: result.low_confidence
                                                ? 'linear-gradient(90deg, #f59e0b, #ef4444)'
                                                : 'linear-gradient(90deg, var(--leaf-primary), var(--leaf-secondary))',
                                        }}
                                    />
                                </div>
                                {result.low_confidence && (
                                    <p style={{ color: 'var(--warn-color)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                        ⚠️ Low confidence — try a clearer image
                                    </p>
                                )}
                            </div>

                            {/* Top Predictions */}
                            <div style={{ marginTop: '1.5rem' }}>
                                <div className="metadata-label">Top Predictions</div>
                                {topPredictions.map((p, i) => (
                                    <div key={i} className="prediction-row">
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', flex: 1 }}>
                                            {p.label.replace(/___/g, ' › ').replace(/_/g, ' ')}
                                        </span>
                                        <span style={{ fontWeight: 700, color: 'var(--leaf-secondary)', fontSize: '0.85rem' }}>
                                            {Math.round(p.probability * 100)}%
                                        </span>
                                    </div>
                                ))}
                            </div>

                            <button
                                className="button-secondary"
                                style={{ width: '100%', marginTop: '1.5rem' }}
                                onClick={handleReset}
                            >
                                New Identification
                            </button>
                        </div>

                        {/* Main Result */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div className="glass-card">
                                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <Leaf color="var(--accent-gold)" style={{ marginRight: '0.75rem' }} />
                                    <h2 style={{ margin: 0 }}>Identification Result</h2>
                                    {result.is_healthy && (
                                        <span className="badge-healthy">✓ Healthy</span>
                                    )}
                                </div>

                                <div className="metadata-label">Crop</div>
                                <div className="metadata-value">{result.crop}</div>

                                <div className="metadata-label">Condition</div>
                                <div className="metadata-value" style={{ color: result.is_healthy ? 'var(--leaf-secondary)' : 'var(--warn-color)' }}>
                                    {result.condition}
                                </div>

                                {knowledge.taxonomy?.scientific_name && (
                                    <>
                                        <div className="metadata-label">Scientific Name</div>
                                        <div className="metadata-value" style={{ fontStyle: 'italic', color: 'var(--accent-gold)' }}>
                                            {knowledge.taxonomy.scientific_name}
                                        </div>
                                    </>
                                )}

                                {knowledge.description && (
                                    <>
                                        <div className="metadata-label">About</div>
                                        <div className="metadata-value" style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-dim)' }}>
                                            {knowledge.description}
                                        </div>
                                    </>
                                )}

                                {knowledge.distribution_states?.length > 0 && (
                                    <>
                                        <div className="metadata-label">Distribution</div>
                                        <div className="metadata-value" style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                                            Found in {knowledge.distribution_states.length} US states
                                        </div>
                                    </>
                                )}

                                <div className="metadata-label" style={{ marginTop: '1rem' }}>Knowledge Sources</div>
                                <div style={{ display: 'flex', alignItems: 'center', fontSize: '0.9rem', color: 'var(--text-dim)' }}>
                                    <ShieldCheck size={16} color="var(--leaf-secondary)" style={{ marginRight: '0.4rem' }} />
                                    {(knowledge.sources || []).join(' • ') || 'Built-in database'}
                                </div>
                            </div>

                            {/* Treatment Panel (only for diseased plants) */}
                            {!result.is_healthy && (Object.keys(treatment).length > 0) && (
                                <div className="glass-card">
                                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
                                        <Info color="var(--warn-color)" style={{ marginRight: '0.75rem' }} />
                                        <h3 style={{ margin: 0 }}>Treatment Guide</h3>
                                    </div>

                                    {treatment.organic?.length > 0 && (
                                        <>
                                            <div className="metadata-label">🌿 Organic Treatment</div>
                                            <ul className="treatment-list">
                                                {treatment.organic.map((t, i) => <li key={i}>{t}</li>)}
                                            </ul>
                                        </>
                                    )}

                                    {treatment.chemical?.length > 0 && (
                                        <>
                                            <div className="metadata-label">🧪 Chemical Treatment</div>
                                            <ul className="treatment-list">
                                                {treatment.chemical.map((t, i) => <li key={i}>{t}</li>)}
                                            </ul>
                                        </>
                                    )}

                                    {treatment.prevention?.length > 0 && (
                                        <>
                                            <div className="metadata-label">🛡️ Prevention</div>
                                            <ul className="treatment-list">
                                                {treatment.prevention.map((t, i) => <li key={i}>{t}</li>)}
                                            </ul>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>

            <footer style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
                <p>Terraherb AI Research Substrate • v0.2.0 • Powered by MobileNetV2 + GBIF + UCI Plants</p>
            </footer>
        </div>
    );
}

export default App;
