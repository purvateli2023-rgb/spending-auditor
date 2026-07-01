import { useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

function Upload({ onSuccess }) {
    const [dragging, setDragging] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [fileType, setFileType] = useState("csv")
    const [fileName, setFileName] = useState(null)

    const handleFile = async (file) => {
        if (!file) return
        setLoading(true)
        setError(null)
        setFileName(file.name)

        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await axios.post(`${API}/upload/${fileType}`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            })
            if (res.data.error) {
                setError(res.data.error)
                setLoading(false)
            } else {
                onSuccess(res.data)
            }
        } catch (err) {
            setError("Something went wrong. Make sure the backend is running.")
            setLoading(false)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragging(false)
        handleFile(e.dataTransfer.files[0])
    }

    return (
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "#0b1326", color: "#dbe2fd" }}>
            <header style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "0 24px", width: "100%", height: "64px", backgroundColor: "#0b1326",
                borderBottom: "1px solid rgba(255,255,255,0.1)", position: "fixed", top: 0, zIndex: 50
            }}>
                <span style={{ fontSize: "24px", fontWeight: 700, color: "#34d399" }}>Spending Auditor</span>
                <nav style={{ display: "flex", alignItems: "center", gap: "32px", fontSize: "14px" }}>
                    <span style={{ color: "#c3c5d9" }}>Dashboard</span>
                    <span style={{ color: "#34d399", fontWeight: 600 }}>Upload</span>
                    <span style={{ color: "#c3c5d9" }}>Settings</span>
                </nav>
            </header>

            <main style={{
                flexGrow: 1, paddingTop: "120px", paddingBottom: "96px", paddingLeft: "24px", paddingRight: "24px",
                maxWidth: "1280px", margin: "0 auto", width: "100%",
                display: "flex", flexDirection: "column", alignItems: "center"
            }}>
                <div style={{ textAlign: "center", marginBottom: "40px" }}>
                    <h1 style={{ fontSize: "48px", fontWeight: 800, color: "#dbe2fd", marginBottom: "12px", letterSpacing: "-0.02em" }}>
                        Upload Your Statements
                    </h1>
                    <p style={{ fontSize: "18px", color: "#c3c5d9", maxWidth: "600px", margin: "0 auto" }}>
                        Securely process your financial data with AI-driven auditing. Supports bank
                        statements, receipts, and CSV exports.
                    </p>
                </div>

                <div style={{
                    display: "inline-flex", padding: "4px", backgroundColor: "#16203a",
                    borderRadius: "12px", border: "1px solid rgba(255,255,255,0.1)", marginBottom: "40px"
                }}>
                    {["csv", "pdf", "image"].map((type) => (
                        <button
                            key={type}
                            onClick={() => setFileType(type)}
                            style={{
                                padding: "8px 32px",
                                borderRadius: "10px",
                                fontWeight: 500,
                                border: "none",
                                cursor: "pointer",
                                fontSize: "14px",
                                marginRight: type !== "image" ? "8px" : "0",
                                transition: "all 0.2s",
                                backgroundColor: fileType === type ? "#10b981" : "transparent",
                                color: fileType === type ? "#064e3b" : "#c3c5d9",
                            }}
                        >
                            {type.toUpperCase()}
                        </button>
                    ))}
                </div>

                <div
                    onClick={() => document.getElementById("fileInput").click()}
                    onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={handleDrop}
                    style={{
                        width: "100%", maxWidth: "900px", height: "384px",
                        borderRadius: "16px", border: `2px dashed ${dragging ? "#34d399" : "rgba(16,185,129,0.5)"}`,
                        cursor: "pointer", display: "flex", flexDirection: "column",
                        alignItems: "center", justifyContent: "center",
                        backgroundColor: dragging ? "#16203a" : "#131b2e",
                        transition: "all 0.2s"
                    }}
                >
                    {loading ? (
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>
                            <div style={{
                                width: "48px", height: "48px", border: "4px solid rgba(255,255,255,0.1)",
                                borderTopColor: "#34d399", borderRadius: "50%", animation: "spin 0.8s linear infinite"
                            }} />
                            <p style={{ fontSize: "18px", fontWeight: 600 }}>Processing {fileName}...</p>
                            <p style={{ color: "#c3c5d9", fontSize: "14px" }}>Running AI integrity checks</p>
                        </div>
                    ) : (
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                            <div style={{
                                width: "80px", height: "80px", borderRadius: "50%",
                                backgroundColor: "rgba(16,185,129,0.1)", display: "flex",
                                alignItems: "center", justifyContent: "center", marginBottom: "24px"
                            }}>
                                <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="#34d399" strokeWidth={1.5}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                </svg>
                            </div>
                            <h3 style={{ fontSize: "20px", fontWeight: 600, marginBottom: "8px" }}>drag and drop your file here</h3>
                            <p style={{ color: "#c3c5d9", marginBottom: "24px" }}>or click to browse from your computer</p>
                            <div style={{ display: "flex", gap: "12px" }}>
                                <span style={{ fontSize: "12px", fontFamily: "monospace", backgroundColor: "#1c2a4d", padding: "4px 12px", borderRadius: "6px", color: "#c3c5d9" }}>
                                    {fileType === "csv" ? ".CSV ONLY" : fileType === "pdf" ? ".PDF ONLY" : ".PNG / .JPG"}
                                </span>
                                <span style={{ fontSize: "12px", fontFamily: "monospace", backgroundColor: "#1c2a4d", padding: "4px 12px", borderRadius: "6px", color: "#c3c5d9" }}>
                                    MAX 50MB
                                </span>
                            </div>
                        </div>
                    )}
                    <input
                        id="fileInput"
                        type="file"
                        style={{ display: "none" }}
                        accept={fileType === "csv" ? ".csv" : fileType === "pdf" ? ".pdf" : ".png,.jpg,.jpeg"}
                        onChange={(e) => handleFile(e.target.files[0])}
                    />
                </div>

                {error && (
                    <div style={{
                        marginTop: "24px", padding: "12px 20px", backgroundColor: "rgba(127,29,29,0.4)",
                        border: "1px solid rgba(239,68,68,0.4)", borderRadius: "10px", color: "#fca5a5",
                        fontSize: "14px", maxWidth: "900px", width: "100%", textAlign: "center"
                    }}>
                        {error}
                    </div>
                )}

                <div style={{
                    display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px",
                    marginTop: "40px", width: "100%", maxWidth: "900px"
                }}>
                    <div style={{
                        backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)",
                        padding: "24px", borderRadius: "16px", display: "flex", alignItems: "flex-start", gap: "16px"
                    }}>
                        <div style={{ padding: "8px", backgroundColor: "rgba(16,185,129,0.2)", borderRadius: "10px" }}>
                            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#34d399" strokeWidth={1.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                            </svg>
                        </div>
                        <div>
                            <h4 style={{ fontWeight: 700, marginBottom: "4px" }}>Fast Processing</h4>
                            <p style={{ fontSize: "14px", color: "#c3c5d9", lineHeight: 1.6 }}>
                                Our parsing engine reads your file and extracts every transaction in seconds.
                            </p>
                        </div>
                    </div>
                    <div style={{
                        backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)",
                        padding: "24px", borderRadius: "16px", display: "flex", alignItems: "flex-start", gap: "16px"
                    }}>
                        <div style={{ padding: "8px", backgroundColor: "rgba(16,185,129,0.2)", borderRadius: "10px" }}>
                            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#34d399" strokeWidth={1.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                            </svg>
                        </div>
                        <div>
                            <h4 style={{ fontWeight: 700, marginBottom: "4px" }}>Smart Categorization</h4>
                            <p style={{ fontSize: "14px", color: "#c3c5d9", lineHeight: 1.6 }}>
                                Transactions are automatically sorted into categories like groceries, dining, and subscriptions.
                            </p>
                        </div>
                    </div>
                </div>
            </main>

            <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    )
}

export default Upload