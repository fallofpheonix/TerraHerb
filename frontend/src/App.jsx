import React, { useState } from 'react';
import './App.css';
import { Upload, Leaf, Search, Info, ShieldCheck } from 'lucide-react';

function App() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
        }
    };

    const handleIdentify = async () => {
        if (!file) return;
        setIsProcessing(true);

        // Simulating API call for now
        setTimeout(() => {
            setResult({
                species: "Ocimum tenuiflorum",
                commonName: "Holy Basil (Tulsi)",
                family: "Lamiaceae",
                confidence: 0.98,
                uses: ["Medicinal", "Adaptogenic", "Culinary"],
                habitat: "Tropical regions of Southeast Asia",
                status: "Localized via UCI Knowledge Base"
            });
            setIsProcessing(false);
        }, 2000);
    };

    return (
        <div className="app-container">
            <header className="hero-section">
                <h1 className="hero-title">Terraherb AI</h1>
                <p style={{ color: 'var(--text-dim)', fontSize: '1.2rem' }}>
                    Deep Learning Plant Identification & Botanical Intelligence
                </p>
            </header>

            <main>
                {!result ? (
                    <div className="glass-card">
                        <div
                            className="upload-area"
                            onClick={() => document.getElementById('fileInput').click()}
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
                                </>
                            )}
                        </div>

                        {file && (
                            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                                <button
                                    className="button-primary"
                                    onClick={handleIdentify}
                                    disabled={isProcessing}
                                >
                                    {isProcessing ? 'Analyzing Core Model...' : 'Identify Species'}
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="results-grid">
                        <div className="glass-card" style={{ padding: '1rem' }}>
                            <img src={preview} alt="Identified Plant" className="plant-image-preview" />
                        </div>

                        <div className="glass-card">
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem' }}>
                                <Leaf color="var(--accent-gold)" style={{ marginRight: '0.75rem' }} />
                                <h2 style={{ margin: 0 }}>Identification Result</h2>
                            </div>

                            <div className="metadata-label">Scientific Name</div>
                            <div className="metadata-value" style={{ fontStyle: 'italic', color: 'var(--accent-gold)' }}>
                                {result.species}
                            </div>

                            <div className="metadata-label">Common Name</div>
                            <div className="metadata-value">{result.commonName}</div>

                            <div className="metadata-label">Botanical Family</div>
                            <div className="metadata-value">{result.family}</div>

                            <div className="metadata-label">Primary Uses</div>
                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                                {result.uses.map(use => (
                                    <span key={use} style={{
                                        background: 'var(--leaf-primary)',
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '20px',
                                        fontSize: '0.8rem'
                                    }}>
                                        {use}
                                    </span>
                                ))}
                            </div>

                            <div className="metadata-label">Knowledge Source</div>
                            <div className="metadata-value" style={{ display: 'flex', alignItems: 'center', fontSize: '0.9rem' }}>
                                <ShieldCheck size={16} color="var(--leaf-secondary)" style={{ marginRight: '0.4rem' }} />
                                Verified via GBIF & UCI Data
                            </div>

                            <button
                                className="button-primary"
                                style={{ width: '100%', marginTop: '1rem' }}
                                onClick={() => setResult(null)}
                            >
                                New Identification
                            </button>
                        </div>
                    </div>
                )}
            </main>

            <footer style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
                <p>Terraherb AI Research Substrate • Prototype v0.2.0 • CV-Ready Edition</p>
            </footer>
        </div>
    );
}

export default App;
