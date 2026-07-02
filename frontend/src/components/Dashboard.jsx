import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

const COLORS = ["#10b981", "#34d399", "#059669", "#6ee7b7", "#047857", "#a7f3d0", "#065f46", "#d1fae5"]

function fmt(amount) {
    return `$${Number(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`
}

function Dashboard({ transactions, onReset }) {
    const total = transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0)
    const dates = transactions.map(t => new Date(t.date)).filter(d => !isNaN(d))
    const minDate = dates.length ? new Date(Math.min(...dates)) : null
    const maxDate = dates.length ? new Date(Math.max(...dates)) : null

    const categoryMap = {}
    transactions.forEach(t => {
        const cat = t.category || "Other"
        categoryMap[cat] = (categoryMap[cat] || 0) + Math.abs(t.amount)
    })
    const categoryData = Object.entries(categoryMap)
        .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(2)) }))
        .sort((a, b) => b.value - a.value)

    const categoryCounts = {}
    transactions.forEach(t => {
        const cat = t.category || "Other"
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1
    })

    const recurringMap = {}
    transactions.forEach(t => {
        const key = `${t.description}__${t.amount}`
        if (!recurringMap[key]) {
            recurringMap[key] = { description: t.description, amount: t.amount, count: 0, category: t.category }
        }
        recurringMap[key].count++
    })
    const recurring = Object.values(recurringMap)
        .filter(r => r.count >= 2)
        .sort((a, b) => b.amount - a.amount)

    const topCategory = categoryData[0]
    const topCategoryPct = topCategory ? Math.round((topCategory.value / total) * 100) : 0

    return (
        <div style={{ minHeight: "100vh", backgroundColor: "#0b1326", color: "#dbe2fd" }}>
            <header style={{
                position: "fixed", top: 0, width: "100%", zIndex: 50,
                backgroundColor: "rgba(11,19,38,0.9)", borderBottom: "1px solid rgba(255,255,255,0.1)",
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "12px 24px"
            }}>
                <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
                    <span style={{ fontSize: "20px", fontWeight: 700 }}>Spending Auditor</span>
                    <nav style={{ display: "flex", alignItems: "center", gap: "24px", fontSize: "14px" }}>
                        <span style={{ color: "#34d399", borderBottom: "2px solid #34d399", paddingBottom: "4px", fontWeight: 500 }}>Dashboard</span>
                        <span style={{ color: "#c3c5d9" }}>Settings</span>
                    </nav>
                </div>
                <button
                    onClick={onReset}
                    style={{
                        backgroundColor: "#10b981", color: "#064e3b", padding: "8px 20px",
                        borderRadius: "10px", fontWeight: 700, border: "none", cursor: "pointer", fontSize: "14px"
                    }}
                >
                    ← Upload New File
                </button>
            </header>

            <main style={{ paddingTop: "96px", paddingLeft: "24px", paddingRight: "24px", paddingBottom: "48px", maxWidth: "1280px", margin: "0 auto" }}>
                {/* Stat Cards */}
                <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "24px", marginBottom: "24px" }}>
                    <div style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px" }}>
                        <span style={{ color: "#c3c5d9", fontWeight: 500, fontSize: "14px" }}>Total Transactions</span>
                        <p style={{ fontSize: "36px", fontWeight: 800, color: "#34d399", marginTop: "8px" }}>{transactions.length}</p>
                    </div>
                    <div style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px" }}>
                        <span style={{ color: "#c3c5d9", fontWeight: 500, fontSize: "14px" }}>Total Spent</span>
                        <p style={{ fontSize: "36px", fontWeight: 800, color: "#34d399", marginTop: "8px" }}>{fmt(total)}</p>
                    </div>
                    <div style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px" }}>
                        <span style={{ color: "#c3c5d9", fontWeight: 500, fontSize: "14px" }}>Date Range</span>
                        <p style={{ fontSize: "24px", fontWeight: 700, color: "#34d399", marginTop: "12px" }}>
                            {minDate && maxDate
                                ? `${minDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })} – ${maxDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`
                                : "N/A"}
                        </p>
                    </div>
                </section>

                {/* Chart + Table */}
                <section style={{ display: "grid", gridTemplateColumns: "5fr 7fr", gap: "24px", marginBottom: "24px" }}>
                    <div style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px", display: "flex", flexDirection: "column" }}>
                        <h3 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "24px" }}>Spending by Category</h3>
                        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", flex: 1 }}>
                            <ResponsiveContainer width="100%" height={220}>
                                <PieChart>
                                    <Pie data={categoryData} cx="50%" cy="50%" innerRadius={65} outerRadius={95} paddingAngle={2} dataKey="value">
                                        {categoryData.map((_, i) => (
                                            <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(val) => fmt(val)} contentStyle={{ background: "#16203a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#dbe2fd" }} />
                                </PieChart>
                            </ResponsiveContainer>
                            {topCategory && (
                                <div style={{ position: "absolute", textAlign: "center", pointerEvents: "none" }}>
                                    <span style={{ display: "block", fontSize: "24px", fontWeight: 700 }}>{topCategoryPct}%</span>
                                    <span style={{ fontSize: "12px", color: "#c3c5d9" }}>{topCategory.name.split(" and ")[0]}</span>
                                </div>
                            )}
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginTop: "24px" }}>
                            {categoryData.slice(0, 6).map((cat, i) => (
                                <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                    <div style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: COLORS[i % COLORS.length] }} />
                                    <span style={{ fontSize: "12px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{cat.name.split(" and ")[0]}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px" }}>
                        <h3 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "24px" }}>Category Totals</h3>
                        <div style={{ overflowX: "auto" }}>
                            <table style={{ width: "100%", textAlign: "left", fontSize: "14px", borderCollapse: "collapse" }}>
                                <thead>
                                    <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", color: "#c3c5d9" }}>
                                        <th style={{ paddingBottom: "12px", fontWeight: 500 }}>Category</th>
                                        <th style={{ paddingBottom: "12px", fontWeight: 500 }}>Count</th>
                                        <th style={{ paddingBottom: "12px", fontWeight: 500 }}>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {categoryData.map((cat, i) => (
                                        <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                                            <td style={{ padding: "12px 0" }}>{cat.name}</td>
                                            <td style={{ padding: "12px 0", color: "#c3c5d9" }}>{categoryCounts[cat.name]}</td>
                                            <td style={{ padding: "12px 0", fontWeight: 600, color: "#34d399" }}>{fmt(cat.value)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>

                {/* Recurring Charges */}
                {recurring.length > 0 && (
                    <section style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px", marginBottom: "24px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "24px" }}>
                            <div style={{ width: "48px", height: "48px", borderRadius: "50%", backgroundColor: "rgba(249,115,22,0.2)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fb923c" }}>
                                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                                </svg>
                            </div>
                            <div>
                                <h3 style={{ fontSize: "18px", fontWeight: 600 }}>Recurring Charges</h3>
                                <p style={{ fontSize: "14px", color: "#c3c5d9" }}>
                                    {recurring.length} recurring charges totalling {fmt(recurring.reduce((s, r) => s + r.amount, 0))}
                                </p>
                            </div>
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
                            {recurring.map((r, i) => (
                                <div key={i} style={{ backgroundColor: "rgba(28,42,77,0.4)", padding: "16px", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.05)" }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                                        <span style={{ fontSize: "12px", fontFamily: "monospace", color: "#34d399" }}>{r.count}x CHARGED</span>
                                        <span style={{ fontSize: "14px", fontWeight: 600 }}>{fmt(r.amount)}</span>
                                    </div>
                                    <span style={{ display: "block", fontWeight: 700 }}>{r.description}</span>
                                    <span style={{ fontSize: "14px", color: "#c3c5d9" }}>{r.category}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* Transactions Table */}
                <section style={{ backgroundColor: "rgba(22,32,58,0.6)", border: "1px solid rgba(255,255,255,0.1)", padding: "24px", borderRadius: "16px" }}>
                    <h3 style={{ fontSize: "18px", fontWeight: 600, marginBottom: "24px" }}>All Transactions</h3>
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", textAlign: "left", fontSize: "14px", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ color: "#c3c5d9", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                                    <th style={{ padding: "12px 0", fontWeight: 500 }}>Date</th>
                                    <th style={{ padding: "12px 0", fontWeight: 500 }}>Description</th>
                                    <th style={{ padding: "12px 0", fontWeight: 500, textAlign: "right" }}>Amount</th>
                                    <th style={{ padding: "12px 0", fontWeight: 500, textAlign: "center" }}>Category</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map((t, i) => (
                                    <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                                        <td style={{ padding: "12px 0", fontFamily: "monospace", color: "#c3c5d9", fontSize: "12px" }}>
                                            {new Date(t.date).toLocaleDateString()}
                                        </td>
                                        <td style={{ padding: "12px 0", fontWeight: 500 }}>{t.description}</td>
                                        <td style={{ padding: "12px 0", textAlign: "right", fontWeight: 700 }}>{fmt(t.amount)}</td>
                                        <td style={{ padding: "12px 0", textAlign: "center" }}>
                                            <span style={{ padding: "4px 12px", backgroundColor: "rgba(16,185,129,0.1)", color: "#34d399", borderRadius: "9999px", fontSize: "12px" }}>
                                                {t.category}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>
        </div>
    )
}

export default Dashboard