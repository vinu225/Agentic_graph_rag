import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';
import { BenchmarkDataset } from '../types/benchmark';
import { GitCompare, Award, Zap, Clock, ShieldCheck, ChevronRight } from 'lucide-react';

interface ComparisonPageProps {
  dataset: BenchmarkDataset;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({ dataset }) => {
  const [activeMetric, setActiveMetric] = useState<'accuracy' | 'tokens' | 'latency'>('accuracy');
  const [pipelineFocus, setPipelineFocus] = useState<'all' | 'rag' | 'graphrag' | 'agent'>('all');

  const { type_breakdown } = dataset;
  const categories = Object.keys(type_breakdown);

  // Prepare chart data based on active metric
  const chartData = categories.map((cat) => {
    const stats = type_breakdown[cat];
    return {
      category: cat.replace('_', '-').toUpperCase(),
      RAG: activeMetric === 'accuracy' 
        ? stats.accuracy.rag 
        : activeMetric === 'tokens' 
        ? stats.tokens_avg.rag 
        : stats.latency_avg_s.rag,
      GraphRAG: activeMetric === 'accuracy' 
        ? stats.accuracy.graphrag 
        : activeMetric === 'tokens' 
        ? stats.tokens_avg.graphrag 
        : stats.latency_avg_s.graphrag,
      Agentic: activeMetric === 'accuracy' 
        ? stats.accuracy.agent 
        : activeMetric === 'tokens' 
        ? stats.tokens_avg.agent 
        : stats.latency_avg_s.agent,
      steps: stats.agent_avg_steps,
    };
  });

  // Diverging Advantage Chart Data: Agentic Accuracy - RAG Accuracy
  const advantageData = categories.map((cat) => {
    const stats = type_breakdown[cat];
    const diff = stats.accuracy.agent - stats.accuracy.rag;
    return {
      category: cat.replace('_', '-').toUpperCase(),
      diff: Number(diff.toFixed(1)),
      color: diff >= 0 ? '#15803d' : '#b91c1c',
    };
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Header & Breadcrumbs */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          <span>COMPARATIVE ANALYSIS</span>
          <span>/</span>
          <span style={{ color: '#e75a24' }}>PIPELINE COMPARISON</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', margin: '4px 0 6px 0', textTransform: 'uppercase', letterSpacing: '-0.02em' }}>
          Pipeline Performance Dimensions
        </h1>
        <div style={{ fontSize: '0.84rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
          Head-to-head empirical trade-offs across Plain RAG, Deterministic GraphRAG, and Autonomous Agentic GraphRAG.
        </div>
      </div>

      {/* 2. Top Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '14px 18px',
          }}
        >
          <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Accuracy Champion
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#e75a24', marginTop: '2px' }}>
            Agentic ({dataset.summary.accuracy.agent.toFixed(1)}%)
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            +{(dataset.summary.accuracy.agent - dataset.summary.accuracy.rag).toFixed(1)}% absolute gain over Plain RAG
          </div>
        </div>

        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '14px 18px',
          }}
        >
          <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Compute Cost Winner
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#d97706', marginTop: '2px' }}>
            Plain RAG ({Math.round(dataset.summary.tokens.rag_avg).toLocaleString()} tok)
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            1.54x lower token consumption vs agentic loops
          </div>
        </div>

        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '14px 18px',
          }}
        >
          <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Latency Profile
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#0284c7', marginTop: '2px' }}>
            {dataset.summary.latency.rag_avg_s.toFixed(1)}s vs {dataset.summary.latency.agent_avg_s.toFixed(1)}s
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            RAG is 2.5x faster; Agent spends time in multi-hop loops
          </div>
        </div>

        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '14px 18px',
          }}
        >
          <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Deterministic Coverage
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#15803d', marginTop: '2px' }}>
            100% Reliability
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Zero hallucination on temporal & superlative relations
          </div>
        </div>
      </div>

      {/* 3. Metric Switcher Toolbar & Main Interactive Comparison Chart */}
      <div
        style={{
          background: '#ece0d1',
          border: '1px solid #dac7b2',
          borderRadius: '6px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '18px',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '14px',
            borderBottom: '1px solid #dac7b2',
            paddingBottom: '14px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', textTransform: 'uppercase' }}>
                Cross-Pipeline Dimension Explorer
              </h2>
            </div>
            <div style={{ fontSize: '0.78rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px' }}>
              Compare accuracy, token consumption, and latency across all five query taxonomy categories
            </div>
          </div>

          {/* Metric Selector Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
            {[
              { id: 'accuracy', label: 'ACCURACY (%)' },
              { id: 'tokens', label: 'AVERAGE TOKENS' },
              { id: 'latency', label: 'LATENCY (s)' },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => setActiveMetric(m.id as any)}
                style={{
                  background: activeMetric === m.id ? '#e75a24' : '#f5ebe1',
                  color: activeMetric === m.id ? '#ffffff' : '#141414',
                  border: activeMetric === m.id ? '1px solid #c2410c' : '1px solid #dac7b2',
                  borderRadius: '4px',
                  padding: '6px 14px',
                  fontSize: '0.74rem',
                  fontFamily: 'Space Mono',
                  fontWeight: 800,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Bar Chart */}
        <div style={{ height: '380px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dac7b2" vertical={false} />
              <XAxis 
                dataKey="category" 
                stroke="#141414" 
                tick={{ fill: '#141414', fontSize: 11, fontFamily: 'Space Mono', fontWeight: 700 }} 
              />
              <YAxis 
                stroke="#141414" 
                tick={{ fill: '#665d53', fontSize: 11, fontFamily: 'Space Mono' }}
                unit={activeMetric === 'accuracy' ? '%' : activeMetric === 'latency' ? 's' : ''} 
              />
              <Tooltip 
                contentStyle={{ 
                  background: '#f5ebe1', 
                  border: '1px solid #141414', 
                  borderRadius: '6px',
                  fontFamily: 'Space Grotesk',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
                }}
                labelStyle={{ color: '#141414', fontWeight: 800, fontFamily: 'Space Mono' }}
              />
              <Legend 
                wrapperStyle={{ 
                  fontSize: '0.8rem', 
                  fontFamily: 'Space Grotesk', 
                  fontWeight: 700, 
                  paddingTop: '14px' 
                }} 
              />
              
              <Bar dataKey="RAG" name="Plain RAG (BM25)" fill="#d97706" radius={[3, 3, 0, 0]} />
              <Bar dataKey="GraphRAG" name="Deterministic GraphRAG" fill="#0284c7" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Agentic" name="Autonomous Agentic GraphRAG" fill="#e75a24" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Two Column Analysis: Agentic Advantage vs Observed Routing Winners */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        
        {/* Diverging Bar Chart: Agentic Advantage */}
        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ borderBottom: '1px solid #dac7b2', paddingBottom: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <h2 style={{ fontSize: '1.05rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', textTransform: 'uppercase' }}>
                Agentic Accuracy Advantage (Δ vs RAG)
              </h2>
            </div>
            <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px' }}>
              Taxonomies where autonomous tool calling drives breakthrough value
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {advantageData.map((d) => (
              <div
                key={d.category}
                style={{
                  background: '#f5ebe1',
                  border: '1px solid #dac7b2',
                  borderRadius: '6px',
                  padding: '10px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontFamily: 'Space Grotesk', fontWeight: 700, marginBottom: '6px' }}>
                  <span style={{ color: '#141414' }}>{d.category}</span>
                  <span style={{ fontFamily: 'Space Mono', fontWeight: 800, color: d.diff >= 0 ? '#15803d' : '#b91c1c' }}>
                    {d.diff > 0 ? `+${d.diff}%` : `${d.diff}%`}
                  </span>
                </div>
                <div style={{ width: '100%', height: '8px', background: '#e4d5c3', borderRadius: '4px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${Math.min(100, Math.abs(d.diff))}%`, 
                      height: '100%', 
                      background: d.diff >= 0 ? '#15803d' : '#b91c1c', 
                      borderRadius: '4px' 
                    }} 
                  />
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 'auto', padding: '12px', background: '#f5ebe1', border: '1px solid #dac7b2', borderRadius: '6px', fontSize: '0.76rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
            <strong style={{ color: '#141414' }}>Key Takeaway:</strong> The agentic loop generates massive +95.2% lift on Aggregation and +20% on Temporal/Superlative queries, but incurs slight overhead on unstructured Multi-Hop where Wikipedia prose was already adequate.
          </div>
        </div>

        {/* Observed Benchmark Winner Matrix */}
        <div
          style={{
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ borderBottom: '1px solid #dac7b2', paddingBottom: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <h2 style={{ fontSize: '1.05rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', textTransform: 'uppercase' }}>
                Empirical Routing Blueprint
              </h2>
            </div>
            <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px' }}>
              Optimal production architecture to route incoming query taxonomies
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { type: 'AGGREGATION', winner: 'Agentic GraphRAG', stat: '95.2% accuracy', badgeColor: '#e75a24', badgeBg: '#ffedd5', border: '#fdba74', reason: 'Solves top-k evidence truncation via deterministic SQL count & threshold execution.' },
              { type: 'TEMPORAL', winner: 'GraphRAG / Agentic', stat: '100.0% accuracy', badgeColor: '#0284c7', badgeBg: '#e0f2fe', border: '#bae6fd', reason: 'ChronologyResolver maps relative editions without calendar math hallucination.' },
              { type: 'SUPERLATIVE', winner: 'GraphRAG / Agentic', stat: '100.0% accuracy', badgeColor: '#0284c7', badgeBg: '#e0f2fe', border: '#bae6fd', reason: 'Zero hallucination on max/min attribute rankings and tie-breakers.' },
              { type: 'LOOKUP', winner: 'Plain RAG (BM25)', stat: '100.0% accuracy', badgeColor: '#b45309', badgeBg: '#fef3c7', border: '#fde68a', reason: 'Fastest (5.97s) and cheapest (2,158 tokens) for single atomic factoid retrieval.' },
              { type: 'MULTI-HOP', winner: 'Plain RAG (BM25)', stat: '92.9% accuracy', badgeColor: '#b45309', badgeBg: '#fef3c7', border: '#fde68a', reason: 'Wikipedia prose matched informal venue aliases unrepresented in graph schema.' },
            ].map((item) => (
              <div 
                key={item.type}
                style={{
                  background: '#f5ebe1',
                  border: '1px solid #dac7b2',
                  borderRadius: '6px',
                  padding: '12px 14px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {item.type}
                  </div>
                  <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px', lineHeight: 1.35 }}>
                    {item.reason}
                  </div>
                </div>

                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <span
                    style={{
                      background: item.badgeBg,
                      border: `1px solid ${item.border}`,
                      color: item.badgeColor,
                      borderRadius: '4px',
                      padding: '4px 10px',
                      fontSize: '0.74rem',
                      fontFamily: 'Space Mono',
                      fontWeight: 800,
                      display: 'inline-block',
                    }}
                  >
                    {item.winner}
                  </span>
                  <div style={{ fontSize: '0.72rem', fontFamily: 'Space Mono', color: '#15803d', marginTop: '3px', fontWeight: 800 }}>
                    {item.stat}
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>

      </div>

    </div>
  );
};
