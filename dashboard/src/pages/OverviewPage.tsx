import React, { useState } from 'react';
import { 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  CartesianGrid
} from 'recharts';
import { 
  Award, 
  Zap, 
  Clock, 
  TrendingUp, 
  HelpCircle, 
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { BenchmarkDataset } from '../types/benchmark';

interface OverviewPageProps {
  dataset: BenchmarkDataset;
  onNavigateToExplorer: () => void;
  onNavigateToTraces: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  dataset,
  onNavigateToExplorer,
  onNavigateToTraces,
}) => {
  const { summary } = dataset;
  const [selectedFrontierPoint, setSelectedFrontierPoint] = useState<string>('agent');

  // Frontier scatter points
  const frontierData = [
    {
      id: 'rag',
      name: 'Plain RAG (BM25)',
      tokens: summary.tokens.rag_avg,
      accuracy: summary.accuracy.rag,
      latency: summary.latency.rag_avg_s,
      color: '#f59e0b',
      fill: 'rgba(245, 158, 11, 0.9)',
      size: 160,
    },
    {
      id: 'graphrag',
      name: 'Deterministic GraphRAG',
      tokens: summary.tokens.graphrag_avg,
      accuracy: summary.accuracy.graphrag,
      latency: summary.latency.graphrag_avg_s,
      color: '#06b6d4',
      fill: 'rgba(6, 182, 212, 0.9)',
      size: 160,
    },
    {
      id: 'agent',
      name: 'Autonomous Agentic GraphRAG',
      tokens: summary.tokens.agent_avg,
      accuracy: summary.accuracy.agent,
      latency: summary.latency.agent_avg_s,
      color: '#a855f7',
      fill: 'rgba(168, 85, 247, 0.9)',
      size: 220,
    },
  ];

  const activePoint = frontierData.find(p => p.id === selectedFrontierPoint) || frontierData[2];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Breadcrumb & Massive Headline from Reference Image */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div className="breadcrumb-banner">
          <span>HOME</span> &gt; <span>BENCHMARKS</span> &gt; <span style={{ color: '#e75a24' }}>AGENTIC GRAPHRAG OBSERVATORY</span>
        </div>
        <h1 className="hero-headline" style={{ fontSize: '2.5rem', margin: '4px 0 8px 0' }}>
          AGENTIC GRAPHRAG EVALUATION
        </h1>
        <p style={{ fontSize: '0.94rem', color: 'var(--text-secondary)', maxWidth: '850px', lineHeight: 1.6, fontFamily: 'Space Grotesk' }}>
          From single-turn lexical retrieval systems to autonomous multi-hop reasoning loops, we benchmark precision-engineered retrieval architectures that withstand the most demanding relational queries across Olympic history.
        </p>
      </div>

      {/* 3 Pillar Summary Cards with Reference Hexagon Bullets */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="hex-bullet" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase' }}>
              Plain RAG Architecture
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Single-shot BM25 full-text indexing over 20,100 corpus chunks. Fast ({summary.latency.rag_avg_s.toFixed(1)}s) and lightweight, but suffers severe context truncation on multi-document aggregation.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontFamily: 'Space Mono', fontSize: '0.74rem' }}>
            <span>ACCURACY:</span>
            <strong style={{ color: '#b45309' }}>{summary.accuracy.rag.toFixed(1)}%</strong>
          </div>
        </div>

        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="hex-bullet" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase' }}>
              Deterministic GraphRAG
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Single-turn heuristic filter extraction querying structured SQLite / TigerGraph Savanna. Achieves 100% accuracy on superlatives with the lowest token footprint.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontFamily: 'Space Mono', fontSize: '0.74rem' }}>
            <span>ACCURACY:</span>
            <strong style={{ color: '#0284c7' }}>{summary.accuracy.graphrag.toFixed(1)}%</strong>
          </div>
        </div>

        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '10px', borderColor: '#e75a24' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="hex-bullet" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase' }}>
              Autonomous Agentic Loop
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Multi-step ReAct orchestration with dynamic tool dispatch, entity linking, SQL aggregation, and chronology resolution. Solves complex multi-hop queries.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontFamily: 'Space Mono', fontSize: '0.74rem' }}>
            <span>ACCURACY:</span>
            <strong style={{ color: '#e75a24' }}>{summary.accuracy.agent.toFixed(1)}%</strong>
          </div>
        </div>
      </div>

      {/* Hero Comparison: Visual Accuracy Progression */}
      <div
        className="panel"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          alignItems: 'center',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="hex-bullet" style={{ width: '10px', height: '10px' }} />
            <span style={{ fontSize: '0.76rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', fontWeight: 700, fontFamily: 'Space Mono' }}>
              BENCHMARK ACCURACY SPECTRUM
            </span>
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', marginBottom: '16px' }}>
            Comparative Accuracy Hierarchy
          </h2>

          {/* Horizontal Progression Bars */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Plain RAG */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', marginBottom: '6px' }}>
                <span style={{ color: '#b45309', fontWeight: 700 }}>Plain RAG (BM25 Top-8)</span>
                <span style={{ fontWeight: 800, fontFamily: 'Space Mono', color: 'var(--text-primary)' }}>{summary.accuracy.rag.toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: '10px', background: '#dac7b2', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${summary.accuracy.rag}%`, height: '100%', background: '#b45309', borderRadius: '2px', transition: 'width 1s ease' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '3px', fontFamily: 'Space Mono' }}>
                Single-shot lexical retrieval over 20,100 chunks
              </div>
            </div>

            {/* GraphRAG */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', marginBottom: '6px' }}>
                <span style={{ color: '#0284c7', fontWeight: 700 }}>Deterministic GraphRAG</span>
                <span style={{ fontWeight: 800, fontFamily: 'Space Mono', color: 'var(--text-primary)' }}>{summary.accuracy.graphrag.toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: '10px', background: '#dac7b2', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${summary.accuracy.graphrag}%`, height: '100%', background: '#0284c7', borderRadius: '2px', transition: 'width 1s ease' }} />
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '3px', fontFamily: 'Space Mono' }}>
                Single-turn SQL knowledge graph query + chunk augmentation
              </div>
            </div>

            {/* Agentic GraphRAG */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', marginBottom: '6px' }}>
                <span style={{ color: '#e75a24', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="hex-bullet" style={{ width: '10px', height: '10px' }} />
                  Autonomous Agentic GraphRAG
                </span>
                <span style={{ fontWeight: 900, fontFamily: 'Space Mono', color: '#e75a24', fontSize: '1.15rem' }}>{summary.accuracy.agent.toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: '14px', background: '#dac7b2', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${summary.accuracy.agent}%`, height: '100%', background: '#e75a24', borderRadius: '2px', transition: 'width 1s ease' }} />
              </div>
              <div style={{ fontSize: '0.74rem', color: '#e75a24', marginTop: '3px', fontWeight: 700, fontFamily: 'Space Mono' }}>
                +{(summary.accuracy.agent - summary.accuracy.rag).toFixed(1)}% ABSOLUTE GAIN OVER PLAIN RAG
              </div>
            </div>
          </div>
        </div>

        {/* Narrative Card */}
        <div
          style={{
            background: '#ece0d1',
            border: '2px solid #dac7b2',
            borderRadius: '6px',
            padding: '24px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#e75a24', fontSize: '0.85rem', fontWeight: 800, fontFamily: 'Space Mono', textTransform: 'uppercase', marginBottom: '10px' }}>
            <span className="hex-bullet" style={{ width: '10px', height: '10px' }} />
            Core Architectural Finding
          </div>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontFamily: 'Space Grotesk' }}>
            Plain RAG collapses on multi-document aggregation (0.0% accuracy on high-cardinality queries) because the top-8 chunk window truncates the candidate evidence pool. 
            GraphRAG solves single-entity relations efficiently, but <strong>Agentic GraphRAG</strong> achieves <strong>{summary.accuracy.agent}% accuracy</strong> by autonomously chaining multi-turn investigations, verifying candidate counts, and recovering from zero-result queries.
          </p>
          <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
            <button
              onClick={onNavigateToExplorer}
              style={{
                background: '#e75a24',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                padding: '10px 18px',
                fontSize: '0.8rem',
                fontFamily: 'Space Mono',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                textTransform: 'uppercase',
              }}
            >
              Explore Questions <ArrowRight size={14} />
            </button>
            <button
              onClick={onNavigateToTraces}
              style={{
                background: 'transparent',
                color: '#141414',
                border: '1px solid #c4b09b',
                borderRadius: '4px',
                padding: '10px 18px',
                fontSize: '0.8rem',
                fontFamily: 'Space Mono',
                fontWeight: 700,
                cursor: 'pointer',
                textTransform: 'uppercase',
              }}
            >
              View Agent Traces
            </button>
          </div>
        </div>
      </div>

      {/* The Central Visual: Interactive Accuracy vs Cost Frontier Matching Reference Image */}
      <div className="panel" style={{ background: '#f5ebe1', border: '2px solid #dac7b2', borderRadius: '4px', padding: '28px' }}>
        
        {/* Section Top Header & 3 Right Stats Columns */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px', marginBottom: '24px' }}>
          <div>
            <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#e75a24', fontWeight: 700, fontFamily: 'Space Mono', marginBottom: '4px' }}>
              BENCHMARK ANALYSIS
            </div>
            <h2 className="hero-headline" style={{ fontSize: '2.4rem', margin: 0 }}>
              Accuracy vs. Compute Cost
            </h2>
            <div style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', fontFamily: 'Space Mono', marginTop: '4px' }}>
              Pareto frontier analysis of retrieval architectures on 100 Olympic Games questions.
            </div>
          </div>

          {/* 3 Right Stat Columns from Image */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
            <div style={{ textAlign: 'center', borderRight: '1px solid #dac7b2', paddingRight: '28px' }}>
              <div style={{ fontSize: '1.9rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1 }}>
                {summary.total_questions}
              </div>
              <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '4px' }}>
                QUESTIONS
              </div>
            </div>

            <div style={{ textAlign: 'center', borderRight: '1px solid #dac7b2', paddingRight: '28px' }}>
              <div style={{ fontSize: '1.9rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1 }}>
                5
              </div>
              <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '4px' }}>
                QUERY TYPES
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.9rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1 }}>
                3
              </div>
              <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '4px' }}>
                PIPELINES
              </div>
            </div>
          </div>
        </div>

        {/* Middle Section: Scatter Plot on Left + Selected Architecture Card on Right */}
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(380px, 1fr) 380px', gap: '24px', alignItems: 'stretch' }}>
          
          {/* Scatter Chart with Dotted Grid */}
          <div style={{ height: '360px', width: '100%', position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 60, bottom: 25, left: 15 }}>
                <CartesianGrid strokeDasharray="2 3" stroke="#dac7b2" vertical={true} horizontal={true} />
                <XAxis 
                  type="number" 
                  dataKey="tokens" 
                  name="Tokens" 
                  domain={[1500, 7500]}
                  ticks={[1500, 3000, 4500, 6000, 7500]}
                  stroke="#141414"
                  strokeWidth={2}
                  tick={{ fill: '#141414', fontSize: 11, fontFamily: 'Space Mono' }}
                  label={{ value: 'Average Tokens / Question', position: 'bottom', fill: '#141414', fontSize: 11, offset: 5, fontFamily: 'Space Mono' }}
                />
                <YAxis 
                  type="number" 
                  dataKey="accuracy" 
                  name="Accuracy" 
                  domain={[50, 100]}
                  ticks={[50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]}
                  stroke="#141414"
                  strokeWidth={2}
                  tickFormatter={(val) => `${val}%`}
                  tick={{ fill: '#141414', fontSize: 11, fontFamily: 'Space Mono' }}
                  label={{ value: 'Accuracy (%)', angle: -90, position: 'left', fill: '#141414', fontSize: 11, offset: 0, fontFamily: 'Space Mono' }}
                />
                <ZAxis type="number" dataKey="size" range={[200, 350]} />
                <Tooltip 
                  cursor={{ strokeDasharray: '2 2' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div style={{ background: '#0f1115', border: '1px solid #dac7b2', borderRadius: '4px', padding: '10px 14px' }}>
                          <div style={{ fontWeight: 800, color: data.color, fontSize: '0.85rem', fontFamily: 'Space Grotesk', textTransform: 'uppercase' }}>{data.name}</div>
                          <div style={{ fontSize: '0.78rem', color: '#f8fafc', marginTop: '4px', fontFamily: 'Space Mono' }}>
                            Accuracy: <strong>{data.accuracy}%</strong>
                          </div>
                          <div style={{ fontSize: '0.78rem', color: '#cbd5e1', fontFamily: 'Space Mono' }}>
                            Avg Tokens: <strong>{data.tokens.toLocaleString()}</strong>
                          </div>
                          <div style={{ fontSize: '0.78rem', color: '#cbd5e1', fontFamily: 'Space Mono' }}>
                            Avg Latency: <strong>{data.latency.toFixed(2)}s</strong>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter 
                  data={frontierData} 
                  onClick={(node: any) => setSelectedFrontierPoint(node.id)}
                  cursor="pointer"
                >
                  {frontierData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      stroke={entry.id === 'agent' ? 'rgba(231, 90, 36, 0.25)' : '#141414'}
                      strokeWidth={entry.id === 'agent' ? 12 : 2}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>

            {/* Labels beside points as in Reference Image */}
            <div style={{ position: 'absolute', top: '70px', right: '110px', pointerEvents: 'none' }}>
              <div style={{ fontSize: '0.76rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1.2 }}>
                Autonomous<br />Agentic GraphRAG
              </div>
            </div>
            <div style={{ position: 'absolute', bottom: '185px', left: '150px', pointerEvents: 'none' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1.2 }}>
                Deterministic<br />GraphRAG
              </div>
            </div>
            <div style={{ position: 'absolute', bottom: '128px', left: '150px', pointerEvents: 'none' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                Plain RAG
              </div>
            </div>
          </div>

          {/* Right Selected Architecture Detail Box (Exactly as in Reference) */}
          <div
            style={{
              background: '#f5ebe1',
              border: '2px solid #dac7b2',
              borderRadius: '4px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className="hex-bullet" style={{ width: '10px', height: '10px', backgroundColor: '#e75a24' }} />
                <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#e75a24', fontWeight: 800, fontFamily: 'Space Mono' }}>
                  SELECTED ARCHITECTURE
                </span>
              </div>
              <h3 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#141414', textTransform: 'uppercase', fontFamily: 'Space Grotesk', lineHeight: 1.1, marginBottom: '20px' }}>
                {activePoint.id === 'agent' ? 'AUTONOMOUS AGENTIC GRAPHRAG' : activePoint.id === 'graphrag' ? 'DETERMINISTIC GRAPHRAG' : 'PLAIN RAG'}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', borderTop: '2px solid #dac7b2', paddingTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.76rem', color: '#4a453e', fontFamily: 'Space Mono' }}>ACCURACY</span>
                  <span style={{ fontSize: '1.25rem', fontWeight: 900, color: '#141414', fontFamily: 'Space Grotesk' }}>
                    {activePoint.accuracy.toFixed(0)}%
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.76rem', color: '#4a453e', fontFamily: 'Space Mono' }}>AVG TOKENS / QUESTION</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 900, color: '#141414', fontFamily: 'Space Grotesk' }}>
                    {activePoint.tokens.toLocaleString()}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.76rem', color: '#4a453e', fontFamily: 'Space Mono' }}>AVG LATENCY</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 900, color: '#141414', fontFamily: 'Space Grotesk' }}>
                    {activePoint.latency.toFixed(2)}s
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.76rem', color: '#4a453e', fontFamily: 'Space Mono' }}>RELATIVE TOKEN COST</span>
                  <span style={{ fontSize: '1.05rem', fontWeight: 900, color: '#e75a24', fontFamily: 'Space Mono' }}>
                    {(activePoint.tokens / summary.tokens.rag_avg).toFixed(2)}x vs RAG
                  </span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #dac7b2', fontSize: '0.8rem', color: '#4a453e', lineHeight: 1.5, fontFamily: 'Space Mono' }}>
              {activePoint.id === 'agent' ? (
                <span>Agentic loop yields +18% accuracy over RAG, with dynamic multi-step reasoning and tool use at 2.28x the token cost.</span>
              ) : activePoint.id === 'graphrag' ? (
                <span>Single-pass GraphRAG offers high token efficiency with structured SQL queries, achieving 78% accuracy at 7.59s average latency.</span>
              ) : (
                <span>Plain RAG executes fast top-8 BM25 chunk retrieval at 2,291 tokens, but truncates multi-document evidence on complex relations.</span>
              )}
            </div>
          </div>

        </div>

        {/* Bottom 3 Comparison Cards (Exactly as in Reference Image) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '24px' }}>
          
          {/* Card 1: Plain RAG */}
          <div
            onClick={() => setSelectedFrontierPoint('rag')}
            style={{
              background: '#f5ebe1',
              border: selectedFrontierPoint === 'rag' ? '2px solid #e75a24' : '1px solid #dac7b2',
              borderRadius: '4px',
              padding: '16px 20px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className="hex-bullet" style={{ width: '8px', height: '8px', backgroundColor: '#e75a24' }} />
                <span style={{ fontSize: '0.72rem', fontWeight: 800, fontFamily: 'Space Mono', color: '#141414', textTransform: 'uppercase' }}>
                  PLAIN RAG
                </span>
              </div>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'baseline' }}>
                <div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.accuracy.rag.toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>ACCURACY</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.tokens.rag_avg.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>TOKENS / Q</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.latency.rag_avg_s.toFixed(2)}s
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>LATENCY</div>
                </div>
              </div>
            </div>

            {/* Orange Hatched Graphic Texture */}
            <div
              style={{
                width: '42px',
                height: '42px',
                backgroundImage: 'repeating-linear-gradient(45deg, #e75a24, #e75a24 2px, transparent 2px, transparent 6px)',
                opacity: 0.35,
              }}
            />
          </div>

          {/* Card 2: Deterministic GraphRAG */}
          <div
            onClick={() => setSelectedFrontierPoint('graphrag')}
            style={{
              background: '#f5ebe1',
              border: selectedFrontierPoint === 'graphrag' ? '2px solid #0284c7' : '1px solid #dac7b2',
              borderRadius: '4px',
              padding: '16px 20px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className="hex-bullet" style={{ width: '8px', height: '8px', backgroundColor: '#0284c7' }} />
                <span style={{ fontSize: '0.72rem', fontWeight: 800, fontFamily: 'Space Mono', color: '#141414', textTransform: 'uppercase' }}>
                  DETERMINISTIC GRAPHRAG
                </span>
              </div>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'baseline' }}>
                <div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.accuracy.graphrag.toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>ACCURACY</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.tokens.graphrag_avg.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>TOKENS / Q</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.latency.graphrag_avg_s.toFixed(2)}s
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>LATENCY</div>
                </div>
              </div>
            </div>

            {/* Cyan Hatched Graphic Texture */}
            <div
              style={{
                width: '42px',
                height: '42px',
                backgroundImage: 'repeating-linear-gradient(45deg, #0284c7, #0284c7 2px, transparent 2px, transparent 6px)',
                opacity: 0.35,
              }}
            />
          </div>

          {/* Card 3: Autonomous Agentic GraphRAG */}
          <div
            onClick={() => setSelectedFrontierPoint('agent')}
            style={{
              background: '#f5ebe1',
              border: selectedFrontierPoint === 'agent' ? '2px solid #e75a24' : '1px solid #dac7b2',
              borderRadius: '4px',
              padding: '16px 20px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span className="hex-bullet" style={{ width: '8px', height: '8px', backgroundColor: '#e75a24' }} />
                <span style={{ fontSize: '0.72rem', fontWeight: 800, fontFamily: 'Space Mono', color: '#141414', textTransform: 'uppercase' }}>
                  AUTONOMOUS AGENTIC GRAPHRAG
                </span>
              </div>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'baseline' }}>
                <div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.accuracy.agent.toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>ACCURACY</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.tokens.agent_avg.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>TOKENS / Q</div>
                </div>
                <div style={{ borderLeft: '1px solid #dac7b2', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {summary.latency.agent_avg_s.toFixed(2)}s
                  </div>
                  <div style={{ fontSize: '0.66rem', fontFamily: 'Space Mono', color: '#857c72' }}>LATENCY</div>
                </div>
              </div>
            </div>

            {/* Dotted Orange Pattern Texture */}
            <div
              style={{
                width: '42px',
                height: '42px',
                backgroundImage: 'radial-gradient(#e75a24 1.5px, transparent 1.5px)',
                backgroundSize: '6px 6px',
                opacity: 0.5,
              }}
            />
          </div>

        </div>

      </div>

    </div>
  );
};
