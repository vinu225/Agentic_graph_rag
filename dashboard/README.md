# Agentic GraphRAG Technical Analytics Dashboard & Research Observatory

A high-quality, genuinely interactive ML research and benchmarking web application comparing **Plain RAG**, **Deterministic GraphRAG**, and **Autonomous Agentic GraphRAG** across 100 benchmark evaluation questions over the Olympic Games Knowledge Base.

---

## 🚀 Key Features

1. **Active Benchmark Selector**:
   - Seamlessly toggle between the **100-Question Public Benchmark (Final Optimized)** and the **15-Question Presentation Subset (Baseline)** without mixing datasets.
2. **Interactive Pareto Frontier**:
   - Scatter visualization plotting **Accuracy (%) vs. Average Tokens / Question** with live detail inspection (accuracy, latency, relative token economics).
3. **Query Type Matrix**:
   - Taxonomy breakdown across *Aggregation*, *Lookup*, *Multi-Hop*, *Superlative*, and *Temporal* questions with drill-down question drawers.
4. **Question Detail Modal & Trace Player**:
   - Deep inspection of every question, displaying the ground truth gold answer, 3-pipeline side-by-side responses, deterministic outcome explanation, and an interactive **Play Trace (▶)** player stepping through each autonomous reasoning turn with expandable raw JSON views.
5. **Diverging Agentic Advantage & Observed Winners**:
   - Visual delta highlighting where the autonomous agent adds breakthrough value (+95.2% on aggregation) vs. where lexical RAG was already sufficient.
6. **Frac@8 Retrieval Completeness Explorer**:
   - Visualizing how top-k text chunk retrieval suffers context truncation on high-cardinality counting questions.
7. **Failure Mode Post-Mortem**:
   - Dedicated failure categorization for each architecture with actual vs. expected answer comparisons.
8. **Export Tools**:
   - Instant browser-side export of filtered benchmarks as JSON or CSV.

---

## 🛠️ Technology Stack

- **Framework**: React 19 + TypeScript + Vite
- **Charting**: Recharts
- **Icons**: Lucide React
- **Design System**: Dark ML Research Theme (Slate / Cyan / Purple / Emerald)

---

## 💻 How to Run Locally

```bash
# 1. Navigate to the dashboard directory
cd dashboard

# 2. Install dependencies (if not already installed)
npm install

# 3. Start development server
npm run dev

# 4. Open in browser:
# http://localhost:5173/
```

To create a production bundle:
```bash
npm run build
npm run preview
```
