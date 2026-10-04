import json
from pathlib import Path

WORKSPACE_ROOT = Path("c:/LATEST/RAG/Agentic_graph_rag")
json_path = WORKSPACE_ROOT / "comparison_15q.json"
html_path = WORKSPACE_ROOT / "metrics_dashboard.html"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

json_data_str = json.dumps(data, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>3-Pipeline Comparative Metrics Dashboard | Deliverable #5</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0a0e17;
      --bg-secondary: #111827;
      --bg-card: #162032;
      --bg-card-hover: #1e293b;
      --border-color: #273549;
      --border-subtle: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      
      --color-rag: #f59e0b;
      --color-rag-bg: rgba(245, 158, 11, 0.12);
      --color-rag-border: rgba(245, 158, 11, 0.35);

      --color-graphrag: #06b6d4;
      --color-graphrag-bg: rgba(6, 182, 212, 0.12);
      --color-graphrag-border: rgba(6, 182, 212, 0.35);

      --color-agent: #a855f7;
      --color-agent-bg: rgba(168, 85, 247, 0.12);
      --color-agent-border: rgba(168, 85, 247, 0.35);

      --color-success: #10b981;
      --color-danger: #ef4444;
      --color-info: #3b82f6;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      padding: 24px;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* Header */
    header {{
      background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(30, 41, 59, 0.75));
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(12px);
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 16px;
    }}

    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      background: rgba(99, 102, 241, 0.15);
      color: #818cf8;
      border: 1px solid rgba(99, 102, 241, 0.3);
    }}

    h1 {{
      font-size: 1.85rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      margin-top: 4px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 6px;
      max-width: 850px;
    }}

    .meta-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }}

    .meta-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      color: var(--text-muted);
      background: rgba(15, 23, 42, 0.7);
      padding: 5px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
    }}

    .meta-tag strong {{
      color: var(--text-main);
    }}

    /* Pipeline Legend Pills */
    .legend-group {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .legend-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
    }}
    .chip-rag {{
      background: var(--color-rag-bg);
      color: var(--color-rag);
      border: 1px solid var(--color-rag-border);
    }}
    .chip-graphrag {{
      background: var(--color-graphrag-bg);
      color: var(--color-graphrag);
      border: 1px solid var(--color-graphrag-border);
    }}
    .chip-agent {{
      background: var(--color-agent-bg);
      color: var(--color-agent);
      border: 1px solid var(--color-agent-border);
    }}

    /* Executive Summary Banner */
    .summary-card {{
      background: linear-gradient(135deg, rgba(16, 24, 40, 0.9), rgba(20, 30, 48, 0.8));
      border: 1px solid #334155;
      border-left: 5px solid var(--color-agent);
      border-radius: 14px;
      padding: 22px 28px;
      margin-bottom: 24px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }}

    .summary-card h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .findings-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }}

    .finding-item {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 14px 18px;
    }}

    .finding-title {{
      font-weight: 700;
      font-size: 0.88rem;
      color: #e2e8f0;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .finding-desc {{
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    /* KPI Stats Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: #475569;
    }}

    .kpi-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}

    .kpi-label {{
      font-size: 0.82rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }}

    .kpi-icon {{
      font-size: 1.1rem;
    }}

    .kpi-comparison {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .kpi-pipeline-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
    }}

    .kpi-pipeline-name {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-muted);
    }}

    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
    }}
    .dot-rag {{ background-color: var(--color-rag); }}
    .dot-graphrag {{ background-color: var(--color-graphrag); }}
    .dot-agent {{ background-color: var(--color-agent); }}

    .kpi-value {{
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      font-size: 1.05rem;
    }}

    .val-best {{
      color: var(--color-success);
    }}

    /* Charts Section */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(580px, 1fr));
      gap: 22px;
      margin-bottom: 24px;
    }}

    .chart-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 22px 24px;
      display: flex;
      flex-direction: column;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 18px;
    }}

    .chart-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #ffffff;
    }}

    .chart-desc {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    .chart-wrapper {{
      position: relative;
      flex: 1;
      min-height: 280px;
    }}

    /* Frac@8 Completeness Section (Prominent Highlight) */
    .completeness-section {{
      background: linear-gradient(180deg, #131d2e 0%, var(--bg-secondary) 100%);
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: 14px;
      padding: 26px;
      margin-bottom: 24px;
      box-shadow: 0 8px 30px rgba(6, 182, 212, 0.08);
    }}

    .completeness-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .completeness-header h3 {{
      font-size: 1.2rem;
      font-weight: 800;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .gap-badge {{
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.35);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .completeness-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }}

    .case-card {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 18px;
    }}

    .case-qid {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      color: #38bdf8;
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .case-question {{
      font-size: 0.85rem;
      font-weight: 600;
      color: #e2e8f0;
      margin-bottom: 12px;
      height: 38px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }}

    .case-metric-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.82rem;
    }}

    .case-metric-row:last-child {{
      border-bottom: none;
    }}

    .progress-bar-bg {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 3px;
      overflow: hidden;
      margin-top: 4px;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: 3px;
    }}

    /* Table Section */
    .table-section {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }}

    .table-controls {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 20px;
    }}

    .filter-buttons {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .btn-filter {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .btn-filter:hover {{
      background: #1e293b;
      color: var(--text-main);
    }}

    .btn-filter.active {{
      background: #3b82f6;
      border-color: #3b82f6;
      color: #ffffff;
    }}

    .search-box {{
      position: relative;
      min-width: 260px;
    }}

    .search-box input {{
      width: 100%;
      background: #0f172a;
      border: 1px solid var(--border-color);
      color: #ffffff;
      padding: 8px 14px 8px 34px;
      border-radius: 8px;
      font-size: 0.85rem;
      outline: none;
      transition: border-color 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: #3b82f6;
    }}

    .search-icon {{
      position: absolute;
      left: 11px;
      top: 9px;
      color: var(--text-dim);
      font-size: 0.85rem;
    }}

    .table-responsive {{
      overflow-x: auto;
      max-height: 720px;
      border: 1px solid var(--border-color);
      border-radius: 10px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
      text-align: left;
    }}

    th {{
      background: #0f172a;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 12px 14px;
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 2px solid var(--border-color);
      white-space: nowrap;
    }}

    td {{
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      vertical-align: top;
    }}

    tr:hover td {{
      background: rgba(30, 41, 59, 0.4);
    }}

    .qid-cell {{
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: #38bdf8;
      white-space: nowrap;
    }}

    .qtype-badge {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .type-aggregation {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
    .type-temporal {{ background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); }}
    .type-superlative {{ background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }}
    .type-multi_hop {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
    .type-lookup {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }}

    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
    }}
    .status-pass {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .status-fail {{
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}

    .answer-snippet {{
      font-size: 0.8rem;
      color: #cbd5e1;
      margin-top: 4px;
      max-width: 320px;
      word-break: break-word;
    }}

    .metric-sub {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      color: var(--text-dim);
      margin-top: 2px;
    }}

    /* Footer */
    footer {{
      text-align: center;
      padding: 20px;
      font-size: 0.82rem;
      color: var(--text-dim);
      border-top: 1px solid var(--border-subtle);
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="header-top">
        <div>
          <div class="badge-pill">TigerGraph Hackathon • Deliverable #5</div>
          <h1>🏆 3-Pipeline Comparative Metrics Dashboard</h1>
          <p class="subtitle">Empirical evaluation comparing <strong>Standalone RAG</strong>, <strong>Minimal GraphRAG</strong>, and <strong>Autonomous Agentic GraphRAG</strong> across Accuracy, Token Efficiency, Latency, and Retrieval Completeness.</p>
        </div>
        <div class="legend-group">
          <div class="legend-chip chip-rag">
            <span class="dot dot-rag"></span> Pipeline 1: Plain RAG
          </div>
          <div class="legend-chip chip-graphrag">
            <span class="dot dot-graphrag"></span> Pipeline 2: GraphRAG
          </div>
          <div class="legend-chip chip-agent">
            <span class="dot dot-agent"></span> Pipeline 3: Agentic GraphRAG
          </div>
        </div>
      </div>
      <div class="meta-bar">
        <div class="meta-tag">📊 Testset: <strong>15 Stratified Questions</strong> (eval_public.jsonl)</div>
        <div class="meta-tag">🧠 Model: <strong>Qwen 3:8B</strong> (Local Ollama)</div>
        <div class="meta-tag">🕸️ Graph DB: <strong>SQLite (36MB, 21k events, 12k athletes)</strong> + TigerGraph Schema</div>
        <div class="meta-tag">⚡ Vector Index: <strong>SQLite FTS5 BM25 (10,950 Chunks)</strong></div>
        <div class="meta-tag">⏱️ Timestamp: <strong>October 2026 Run</strong></div>
      </div>
    </header>

    <!-- Executive Summary Card (Headline Finding) -->
    <section class="summary-card">
      <h2>📌 Executive Summary & Headline Findings (Empirical Data)</h2>
      <div class="findings-grid">
        <div class="finding-item">
          <div class="finding-title">💥 The Frac@8 Under-Retrieval Gap</div>
          <div class="finding-desc">
            Plain RAG suffered <strong>0.0% accuracy on Aggregation</strong> questions (pub-001, pub-003, pub-010). Because BM25 top-k truncation caps context at 8 chunks, candidate documents were truncated, causing severe undercounting or honest refusals. <strong>Agentic GraphRAG scored 100.0%</strong> by querying structured graph tables directly.
          </div>
        </div>
        <div class="finding-item">
          <div class="finding-title">⏱️ Temporal Anchor Disambiguation</div>
          <div class="finding-desc">
            On relative temporal hops (<em>"immediately before 2016"</em> $\to$ 2012 Games), <strong>GraphRAG and Agentic both achieved 100.0% accuracy</strong> by walking the Olympic chronology relation. Plain RAG (66.7%) suffered lexical attraction to distractor year tokens (matching 2016 docs instead of 2012).
          </div>
        </div>
        <div class="finding-item">
          <div class="finding-title">⚖️ The Accuracy vs Token Trade-off</div>
          <div class="finding-desc">
            <strong>GraphRAG achieved the highest overall score (93.3%)</strong> at only <strong>2,172 tokens</strong> and <strong>15.3s</strong> latency — the optimal sweet spot for single-hop graph queries. <strong>Agentic GraphRAG scored 86.7%</strong> (100% on aggregation/temporal/multi-hop) with full autonomous planning, using <strong>6,389 tokens</strong> (~3x) and <strong>26.1s</strong>.
          </div>
        </div>
      </div>
    </section>

    <!-- KPI Metric Cards Grid -->
    <div class="kpi-grid">
      <!-- KPI 1: Overall Accuracy -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Overall Accuracy</span>
          <span class="kpi-icon">🎯</span>
        </div>
        <div class="kpi-comparison">
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-graphrag"></span> GraphRAG</span>
            <span class="kpi-value val-best">93.3% <span style="font-size: 0.72rem; color: #94a3b8;">(14/15)</span></span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-agent"></span> Agentic</span>
            <span class="kpi-value">86.7% <span style="font-size: 0.72rem; color: #94a3b8;">(13/15)</span></span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-rag"></span> Plain RAG</span>
            <span class="kpi-value" style="color: var(--color-danger);">66.7% <span style="font-size: 0.72rem; color: #94a3b8;">(10/15)</span></span>
          </div>
        </div>
      </div>

      <!-- KPI 2: Aggregation Accuracy (The Core Difference) -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Aggregation Accuracy</span>
          <span class="kpi-icon">∑</span>
        </div>
        <div class="kpi-comparison">
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-agent"></span> Agentic</span>
            <span class="kpi-value val-best">100.0% <span style="font-size: 0.72rem; color: #94a3b8;">(3/3)</span></span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-graphrag"></span> GraphRAG</span>
            <span class="kpi-value">66.7% <span style="font-size: 0.72rem; color: #94a3b8;">(2/3)</span></span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-rag"></span> Plain RAG</span>
            <span class="kpi-value" style="color: var(--color-danger);">0.0% <span style="font-size: 0.72rem; color: #94a3b8;">(0/3)</span></span>
          </div>
        </div>
      </div>

      <!-- KPI 3: Token Efficiency -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Avg Tokens / Question</span>
          <span class="kpi-icon">🪙</span>
        </div>
        <div class="kpi-comparison">
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-rag"></span> Plain RAG</span>
            <span class="kpi-value val-best">2,161</span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-graphrag"></span> GraphRAG</span>
            <span class="kpi-value">2,172</span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-agent"></span> Agentic</span>
            <span class="kpi-value" style="color: var(--color-agent);">6,389 <span style="font-size: 0.72rem; color: #94a3b8;">(2.95x)</span></span>
          </div>
        </div>
      </div>

      <!-- KPI 4: Latency -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Avg Latency (Seconds)</span>
          <span class="kpi-icon">⚡</span>
        </div>
        <div class="kpi-comparison">
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-rag"></span> Plain RAG</span>
            <span class="kpi-value val-best">10.97s</span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-graphrag"></span> GraphRAG</span>
            <span class="kpi-value">15.33s</span>
          </div>
          <div class="kpi-pipeline-row">
            <span class="kpi-pipeline-name"><span class="dot dot-agent"></span> Agentic</span>
            <span class="kpi-value" style="color: var(--color-agent);">26.06s <span style="font-size: 0.72rem; color: #94a3b8;">(2.38x)</span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Grid: Accuracy & Tokens -->
    <div class="charts-grid">
      <!-- Chart 1: Accuracy Breakdown by Query Type -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Accuracy Comparison by Query Type (%)</div>
            <div class="chart-desc">100% = all 3 questions in category answered correctly</div>
          </div>
        </div>
        <div class="chart-wrapper">
          <canvas id="accuracyChart"></canvas>
        </div>
      </div>

      <!-- Chart 2: Token Efficiency by Query Type -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Average Total Tokens per Question</div>
            <div class="chart-desc">Prompt context + generation tokens per question category</div>
          </div>
        </div>
        <div class="chart-wrapper">
          <canvas id="tokenChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Charts Grid 2: Overall Accuracy & Latency -->
    <div class="charts-grid">
      <!-- Chart 3: Overall Accuracy Comparison -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Overall Accuracy & Success Rate</div>
            <div class="chart-desc">Performance across all 15 stratified benchmark questions</div>
          </div>
        </div>
        <div class="chart-wrapper">
          <canvas id="overallAccuracyChart"></canvas>
        </div>
      </div>

      <!-- Chart 4: Latency Comparison -->
      <div class="chart-header-wrap chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Average Latency per Query Category (Seconds)</div>
            <div class="chart-desc">End-to-end response time including retrieval, tool loops & generation</div>
          </div>
        </div>
        <div class="chart-wrapper">
          <canvas id="latencyChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Prominent Spotlight: The Completeness Breakdown (Frac@8 Retrieval Gap) -->
    <section class="completeness-section">
      <div class="completeness-header">
        <div>
          <h3>🔍 Retrieval Completeness & The Frac@8 Retrieval Gap</h3>
          <p class="subtitle" style="font-size: 0.85rem; margin-top: 4px;">
            In high-cardinality aggregation and superlative queries, standard RAG top-k retrieval truncates candidates outside the top 8 chunks. 
            Structured graph querying completely bypasses this limitation.
          </p>
        </div>
        <span class="gap-badge">Core Architectural Vulnerability</span>
      </div>

      <div class="completeness-grid">
        <!-- Case 1: pub-001 -->
        <div class="case-card">
          <div class="case-qid">pub-001 • AGGREGATION</div>
          <div class="case-question">Biathlon events at 2018 Winter Olympics with &gt;73 competitors</div>
          <div class="case-metric-row">
            <span style="color: #94a3b8;">Gold Target:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #38bdf8;">5 events</span>
          </div>
          <div class="case-metric-row">
            <span><span class="dot dot-rag"></span> RAG Captured:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-danger);">0 / 5 (0%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 0%; background: var(--color-danger);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-graphrag"></span> GraphRAG:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">5 / 5 (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-success);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-agent"></span> Agentic:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">5 / 5 (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-agent);"></div></div>
        </div>

        <!-- Case 2: pub-003 -->
        <div class="case-card">
          <div class="case-qid">pub-003 • AGGREGATION</div>
          <div class="case-question">Shooting events at 2004 Summer Olympics with &gt;37 competitors</div>
          <div class="case-metric-row">
            <span style="color: #94a3b8;">Gold Target:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #38bdf8;">8 events</span>
          </div>
          <div class="case-metric-row">
            <span><span class="dot dot-rag"></span> RAG Captured:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-danger);">3 / 8 (37.5%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 37.5%; background: var(--color-danger);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-graphrag"></span> GraphRAG:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">8 / 8 (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-success);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-agent"></span> Agentic:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">8 / 8 (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-agent);"></div></div>
        </div>

        <!-- Case 3: pub-010 -->
        <div class="case-card">
          <div class="case-qid">pub-010 • AGGREGATION</div>
          <div class="case-question">Cycling events at 2000 Summer Olympics with &gt;30 competitors</div>
          <div class="case-metric-row">
            <span style="color: #94a3b8;">Gold Target:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #38bdf8;">4 events</span>
          </div>
          <div class="case-metric-row">
            <span><span class="dot dot-rag"></span> RAG Captured:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-danger);">2 / 4 (50%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 50%; background: var(--color-danger);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-graphrag"></span> GraphRAG:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #facc15;">3 / 4 (75%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 75%; background: #facc15;"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-agent"></span> Agentic:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">4 / 4 (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-agent);"></div></div>
        </div>

        <!-- Case 4: pub-004 -->
        <div class="case-card">
          <div class="case-qid">pub-004 • SUPERLATIVE</div>
          <div class="case-question">Athletics event at 2008 Summer Olympics with highest competitors</div>
          <div class="case-metric-row">
            <span style="color: #94a3b8;">Gold Target:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #38bdf8;">Men's marathon (95)</span>
          </div>
          <div class="case-metric-row">
            <span><span class="dot dot-rag"></span> RAG Captured:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-danger);">0 / 1 ("not found")</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 0%; background: var(--color-danger);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-graphrag"></span> GraphRAG:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">Marathon (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-success);"></div></div>
          <div class="case-metric-row" style="margin-top: 6px;">
            <span><span class="dot dot-agent"></span> Agentic:</span>
            <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: var(--color-success);">Marathon (100%)</span>
          </div>
          <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%; background: var(--color-agent);"></div></div>
        </div>
      </div>
    </section>

    <!-- Detailed Question-by-Question Results Table -->
    <section class="table-section">
      <div class="table-controls">
        <div class="filter-buttons">
          <button class="btn-filter active" onclick="filterTable('all')">All Questions (15)</button>
          <button class="btn-filter" onclick="filterTable('aggregation')">Aggregation (3)</button>
          <button class="btn-filter" onclick="filterTable('temporal')">Temporal (3)</button>
          <button class="btn-filter" onclick="filterTable('superlative')">Superlative (3)</button>
          <button class="btn-filter" onclick="filterTable('multi_hop')">Multi-Hop (3)</button>
          <button class="btn-filter" onclick="filterTable('lookup')">Lookup (3)</button>
          <button class="btn-filter" onclick="filterTable('disagreement')">⚠️ RAG Failures (5)</button>
        </div>
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" placeholder="Search questions, answers..." onkeyup="searchTable()">
        </div>
      </div>

      <div class="table-responsive">
        <table id="resultsTable">
          <thead>
            <tr>
              <th>QID & Type</th>
              <th>Question & Gold Answer</th>
              <th>Pipeline 1: RAG</th>
              <th>Pipeline 2: GraphRAG</th>
              <th>Pipeline 3: Agentic GraphRAG</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <!-- Dynamically populated from JS -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Footer -->
    <footer>
      Agentic GraphRAG Benchmark Dashboard • TigerGraph Olympic Dataset Evaluation • Deliverable #5 Complete
    </footer>
  </div>

  <script>
    // Embedded Benchmark Data
    const BENCHMARK_DATA = {json_data_str};

    // Color Constants
    const COLOR_RAG = '#f59e0b';
    const COLOR_GRAPHRAG = '#06b6d4';
    const COLOR_AGENT = '#a855f7';

    // Chart Options Helper
    function getBaseChartOptions() {{
      return {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            labels: {{
              color: '#cbd5e1',
              font: {{ family: 'Inter', size: 12 }}
            }}
          }},
          tooltip: {{
            backgroundColor: '#1e293b',
            titleColor: '#ffffff',
            bodyColor: '#cbd5e1',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 10,
            bodyFont: {{ family: 'Inter', size: 12 }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
            ticks: {{ color: '#94a3b8', font: {{ family: 'Inter', size: 11 }} }}
          }},
          y: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
            ticks: {{ color: '#94a3b8', font: {{ family: 'Inter', size: 11 }} }}
          }}
        }}
      }};
    }}

    // Render All Charts
    function renderCharts() {{
      const byType = BENCHMARK_DATA.summary.by_type;
      const categories = ['aggregation', 'temporal', 'superlative', 'multi_hop', 'lookup'];
      const catLabels = ['Aggregation', 'Temporal', 'Superlative', 'Multi-Hop', 'Lookup'];

      // 1. Accuracy by Type Grouped Chart
      const accCtx = document.getElementById('accuracyChart').getContext('2d');
      new Chart(accCtx, {{
        type: 'bar',
        data: {{
          labels: catLabels,
          datasets: [
            {{
              label: 'Plain RAG',
              data: categories.map(c => byType[c].accuracy.RAG),
              backgroundColor: 'rgba(245, 158, 11, 0.8)',
              borderColor: COLOR_RAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'GraphRAG',
              data: categories.map(c => byType[c].accuracy.GraphRAG),
              backgroundColor: 'rgba(6, 182, 212, 0.8)',
              borderColor: COLOR_GRAPHRAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'Agentic GraphRAG',
              data: categories.map(c => byType[c].accuracy.Agent),
              backgroundColor: 'rgba(168, 85, 247, 0.8)',
              borderColor: COLOR_AGENT,
              borderWidth: 1,
              borderRadius: 6
            }}
          ]
        }},
        options: {{
          ...getBaseChartOptions(),
          scales: {{
            ...getBaseChartOptions().scales,
            y: {{
              beginAtZero: true,
              max: 100,
              ticks: {{
                callback: function(val) {{ return val + '%'; }},
                color: '#94a3b8'
              }}
            }}
          }}
        }}
      }});

      // 2. Average Tokens by Type
      const tokenCtx = document.getElementById('tokenChart').getContext('2d');
      new Chart(tokenCtx, {{
        type: 'bar',
        data: {{
          labels: catLabels,
          datasets: [
            {{
              label: 'Plain RAG',
              data: categories.map(c => byType[c].tokens.RAG),
              backgroundColor: 'rgba(245, 158, 11, 0.8)',
              borderColor: COLOR_RAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'GraphRAG',
              data: categories.map(c => byType[c].tokens.GraphRAG),
              backgroundColor: 'rgba(6, 182, 212, 0.8)',
              borderColor: COLOR_GRAPHRAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'Agentic GraphRAG',
              data: categories.map(c => byType[c].tokens.Agent),
              backgroundColor: 'rgba(168, 85, 247, 0.8)',
              borderColor: COLOR_AGENT,
              borderWidth: 1,
              borderRadius: 6
            }}
          ]
        }},
        options: {{
          ...getBaseChartOptions(),
          scales: {{
            ...getBaseChartOptions().scales,
            y: {{
              beginAtZero: true,
              ticks: {{
                callback: function(val) {{ return val.toLocaleString() + ' tok'; }},
                color: '#94a3b8'
              }}
            }}
          }}
        }}
      }});

      // 3. Overall Accuracy Comparison
      const overallAccCtx = document.getElementById('overallAccuracyChart').getContext('2d');
      new Chart(overallAccCtx, {{
        type: 'bar',
        data: {{
          labels: ['Plain RAG', 'GraphRAG', 'Agentic GraphRAG'],
          datasets: [{{
            label: 'Overall Accuracy (%)',
            data: [
              BENCHMARK_DATA.summary.overall_accuracy.RAG,
              BENCHMARK_DATA.summary.overall_accuracy.GraphRAG,
              BENCHMARK_DATA.summary.overall_accuracy.Agent
            ],
            backgroundColor: [
              'rgba(245, 158, 11, 0.85)',
              'rgba(6, 182, 212, 0.85)',
              'rgba(168, 85, 247, 0.85)'
            ],
            borderColor: [COLOR_RAG, COLOR_GRAPHRAG, COLOR_AGENT],
            borderWidth: 1,
            borderRadius: 8
          }}]
        }},
        options: {{
          ...getBaseChartOptions(),
          plugins: {{
            legend: {{ display: false }}
          }},
          scales: {{
            ...getBaseChartOptions().scales,
            y: {{
              beginAtZero: true,
              max: 100,
              ticks: {{
                callback: function(val) {{ return val + '%'; }},
                color: '#94a3b8'
              }}
            }}
          }}
        }}
      }});

      // 4. Latency by Type
      const latCtx = document.getElementById('latencyChart').getContext('2d');
      new Chart(latCtx, {{
        type: 'bar',
        data: {{
          labels: catLabels,
          datasets: [
            {{
              label: 'Plain RAG',
              data: categories.map(c => byType[c].latency_s.RAG),
              backgroundColor: 'rgba(245, 158, 11, 0.8)',
              borderColor: COLOR_RAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'GraphRAG',
              data: categories.map(c => byType[c].latency_s.GraphRAG),
              backgroundColor: 'rgba(6, 182, 212, 0.8)',
              borderColor: COLOR_GRAPHRAG,
              borderWidth: 1,
              borderRadius: 6
            }},
            {{
              label: 'Agentic GraphRAG',
              data: categories.map(c => byType[c].latency_s.Agent),
              backgroundColor: 'rgba(168, 85, 247, 0.8)',
              borderColor: COLOR_AGENT,
              borderWidth: 1,
              borderRadius: 6
            }}
          ]
        }},
        options: {{
          ...getBaseChartOptions(),
          scales: {{
            ...getBaseChartOptions().scales,
            y: {{
              beginAtZero: true,
              ticks: {{
                callback: function(val) {{ return val + 's'; }},
                color: '#94a3b8'
              }}
            }}
          }}
        }}
      }});
    }}

    // Populate Detailed Question Table
    function populateTable() {{
      const tbody = document.getElementById('tableBody');
      tbody.innerHTML = '';

      BENCHMARK_DATA.questions.forEach(q => {{
        const tr = document.createElement('tr');
        tr.className = 'table-row';
        tr.dataset.qid = q.question_id;
        tr.dataset.qtype = q.query_type;
        tr.dataset.ragFail = !q.rag.correct;

        const goldText = Array.isArray(q.gold_answer) ? q.gold_answer.join(', ') : q.gold_answer;

        const ragPass = q.rag.correct;
        const grPass = q.graphrag.correct;
        const agPass = q.agent.correct;

        tr.innerHTML = `
          <td>
            <div class="qid-cell">${{q.question_id}}</div>
            <span class="qtype-badge type-${{q.query_type}}">${{q.query_type}}</span>
          </td>
          <td>
            <div style="font-weight: 500; color: #f1f5f9; margin-bottom: 6px;">${{q.question}}</div>
            <div style="font-size: 0.78rem; color: #38bdf8;"><strong>Gold:</strong> ${{goldText}}</div>
          </td>
          <td>
            <span class="status-badge ${{ragPass ? 'status-pass' : 'status-fail'}}">
              ${{ragPass ? '✅ PASS' : '❌ FAIL'}}
            </span>
            <div class="answer-snippet">${{q.rag.answer || 'N/A'}}</div>
            <div class="metric-sub">${{q.rag.tokens}} tokens • ${{q.rag.latency}}s</div>
          </td>
          <td>
            <span class="status-badge ${{grPass ? 'status-pass' : 'status-fail'}}">
              ${{grPass ? '✅ PASS' : '❌ FAIL'}}
            </span>
            <div class="answer-snippet">${{q.graphrag.answer || 'N/A'}}</div>
            <div class="metric-sub">${{q.graphrag.tokens}} tokens • ${{q.graphrag.latency}}s</div>
          </td>
          <td>
            <span class="status-badge ${{agPass ? 'status-pass' : 'status-fail'}}">
              ${{agPass ? '✅ PASS' : '❌ FAIL'}}
            </span>
            <div class="answer-snippet">${{q.agent.answer || 'N/A'}}</div>
            <div class="metric-sub">
              ${{q.agent.tokens}} tokens • ${{q.agent.latency}}s
              ${{q.agent.total_steps ? ' • ' + q.agent.total_steps + ' steps' : ''}}
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // Filter Table Function
    let currentFilter = 'all';
    function filterTable(type) {{
      currentFilter = type;
      document.querySelectorAll('.btn-filter').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');

      const rows = document.querySelectorAll('#tableBody tr');
      rows.forEach(row => {{
        const rowType = row.dataset.qtype;
        const isRagFail = row.dataset.ragFail === 'true';

        if (type === 'all') {{
          row.style.display = '';
        }} else if (type === 'disagreement') {{
          row.style.display = isRagFail ? '' : 'none';
        }} else {{
          row.style.display = (rowType === type) ? '' : 'none';
        }}
      }});
    }}

    // Search Table Function
    function searchTable() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const rows = document.querySelectorAll('#tableBody tr');

      rows.forEach(row => {{
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      }});
    }}

    // Initialize
    window.addEventListener('DOMContentLoaded', () => {{
      renderCharts();
      populateTable();
    }});
  </script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[Done] Generated metrics dashboard: {html_path}")
