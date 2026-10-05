import React, { useState } from 'react';
import { 
  Layers, 
  ArrowRight, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  Calendar, 
  Award, 
  FileText, 
  HelpCircle,
  Database,
  Compass,
  Cpu
} from 'lucide-react';
import { BenchmarkDataset, BenchmarkQuestion } from '../types/benchmark';

interface QueryTypePageProps {
  dataset: BenchmarkDataset;
  onSelectQuestion: (q: BenchmarkQuestion) => void;
}

export const QueryTypePage: React.FC<QueryTypePageProps> = ({ dataset, onSelectQuestion }) => {
  const [selectedType, setSelectedType] = useState<string>('aggregation');
  const { type_breakdown, questions } = dataset;
  const categories = Object.keys(type_breakdown);

  const currentStats = type_breakdown[selectedType];
  const typeQuestions = questions.filter(q => q.query_type === selectedType);

  const getTypeStyling = (type: string) => {
    switch (type.toLowerCase()) {
      case 'temporal':
        return {
          barColor: '#0d9488',
          icon: <Calendar size={18} style={{ color: '#0d9488' }} />,
        };
      case 'superlative':
        return {
          barColor: '#8b5cf6',
          icon: <Award size={18} style={{ color: '#8b5cf6' }} />,
        };
      case 'multi_hop':
        return {
          barColor: '#0284c7',
          icon: <FileText size={18} style={{ color: '#0284c7' }} />,
        };
      case 'aggregation':
      default:
        return {
          barColor: '#e75a24',
          icon: <FileText size={18} style={{ color: '#e75a24' }} />,
        };
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Header & Breadcrumbs */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          <span>BENCHMARK ANALYSIS</span>
          <span>/</span>
          <span style={{ color: '#e75a24' }}>QUERY TYPE MATRIX</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', margin: '4px 0 6px 0', textTransform: 'uppercase', letterSpacing: '-0.02em' }}>
          Performance by Question Taxonomy
        </h1>
        <div style={{ fontSize: '0.84rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
          Explore performance breakdowns across multi-hop, aggregation, superlative, and temporal queries. Select any category row to inspect individual questions and pipeline accuracy gaps.
        </div>
      </div>

      {/* 2. Quick Highlight Stat Cards */}
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
            Taxonomies Analyzed
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', marginTop: '2px' }}>
            {categories.length} Categories
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Multi-hop, Aggregation, Superlative, Temporal & Lookup
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
            Hardest Query Taxonomy
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#b91c1c', marginTop: '2px' }}>
            Aggregation (0.0% RAG)
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Top-K context truncation causes complete baseline failure
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
            Largest Agentic Lead
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#e75a24', marginTop: '2px' }}>
            +95.2% Δ (vs RAG)
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Achieved via deterministic SQL threshold execution
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
            Selected Taxonomy
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#0284c7', marginTop: '2px', textTransform: 'uppercase' }}>
            {selectedType.replace('_', '-')}
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            {typeQuestions.length} Questions loaded in drilldown drawer
          </div>
        </div>
      </div>

      {/* 3. Interactive Matrix Table */}
      <div
        style={{
          background: '#ece0d1',
          border: '1px solid #dac7b2',
          borderRadius: '6px',
          overflow: 'hidden',
        }}
      >
        <div style={{ padding: '14px 18px', borderBottom: '1px solid #dac7b2', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="hex-bullet" />
            <span style={{ fontSize: '0.84rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#141414', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Taxonomy Comparison Matrix
            </span>
          </div>
          <span style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72' }}>
            CLICK ANY ROW TO DRILL DOWN
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#e4d5c3', borderBottom: '2px solid #dac7b2' }}>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#141414', letterSpacing: '0.05em' }}>QUERY TYPE</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#141414', letterSpacing: '0.05em' }}>COUNT</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#d97706', letterSpacing: '0.05em' }}>PLAIN RAG</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#0284c7', letterSpacing: '0.05em' }}>GRAPHRAG</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#e75a24', letterSpacing: '0.05em' }}>AGENTIC GRAPHRAG</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#141414', letterSpacing: '0.05em' }}>AVG STEPS</th>
                <th style={{ padding: '12px 18px', fontFamily: 'Space Mono', fontSize: '0.74rem', fontWeight: 800, color: '#141414', letterSpacing: '0.05em', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => {
                const stats = type_breakdown[cat];
                const isSelected = selectedType === cat;

                return (
                  <tr
                    key={cat}
                    onClick={() => setSelectedType(cat)}
                    style={{
                      borderBottom: '1px solid #dac7b2',
                      background: isSelected ? '#f5ebe1' : '#ece0d1',
                      borderLeft: isSelected ? '4px solid #e75a24' : '4px solid transparent',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <td style={{ padding: '14px 18px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: isSelected ? '#e75a24' : '#857c72',
                          }}
                        />
                        <span style={{ fontFamily: 'Space Grotesk', fontWeight: 800, fontSize: '0.9rem', color: '#141414' }}>
                          {cat.replace('_', '-').toUpperCase()}
                        </span>
                      </div>
                    </td>

                    <td style={{ padding: '14px 18px', fontFamily: 'Space Mono', fontSize: '0.84rem', color: '#665d53', fontWeight: 700 }}>
                      {stats.total} Qs
                    </td>

                    <td style={{ padding: '14px 18px' }}>
                      <span
                        style={{
                          background: stats.accuracy.rag === 0 ? '#fce8e8' : '#fef3c7',
                          border: `1px solid ${stats.accuracy.rag === 0 ? '#fca5a5' : '#fde68a'}`,
                          color: stats.accuracy.rag === 0 ? '#b91c1c' : '#b45309',
                          borderRadius: '4px',
                          padding: '3px 8px',
                          fontFamily: 'Space Mono',
                          fontSize: '0.78rem',
                          fontWeight: 800,
                        }}
                      >
                        {stats.accuracy.rag.toFixed(1)}%
                      </span>
                    </td>

                    <td style={{ padding: '14px 18px' }}>
                      <span
                        style={{
                          background: '#e0f2fe',
                          border: '1px solid #bae6fd',
                          color: '#0284c7',
                          borderRadius: '4px',
                          padding: '3px 8px',
                          fontFamily: 'Space Mono',
                          fontSize: '0.78rem',
                          fontWeight: 800,
                        }}
                      >
                        {stats.accuracy.graphrag.toFixed(1)}%
                      </span>
                    </td>

                    <td style={{ padding: '14px 18px' }}>
                      <span
                        style={{
                          background: '#ffedd5',
                          border: '1px solid #fdba74',
                          color: '#e75a24',
                          borderRadius: '4px',
                          padding: '3px 8px',
                          fontFamily: 'Space Mono',
                          fontSize: '0.86rem',
                          fontWeight: 900,
                        }}
                      >
                        {stats.accuracy.agent.toFixed(1)}%
                      </span>
                    </td>

                    <td style={{ padding: '14px 18px', fontFamily: 'Space Mono', fontSize: '0.82rem', color: '#141414', fontWeight: 700 }}>
                      {stats.agent_avg_steps.toFixed(2)} hops
                    </td>

                    <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                      <button
                        style={{
                          background: isSelected ? '#e75a24' : '#f5ebe1',
                          color: isSelected ? '#ffffff' : '#141414',
                          border: isSelected ? '1px solid #e75a24' : '1px solid #141414',
                          borderRadius: '4px',
                          padding: '5px 12px',
                          fontSize: '0.76rem',
                          fontFamily: 'Space Grotesk',
                          fontWeight: 800,
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        {isSelected ? 'Viewing' : 'Inspect'}
                        <span>→</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Selected Type Drilldown Drawer / Panel */}
      {currentStats && (
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
          {/* Header Row of Drawer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', borderBottom: '1px solid #dac7b2', paddingBottom: '14px' }}>
            <div>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: '#e75a24', fontWeight: 800, fontFamily: 'Space Mono' }}>
                Taxonomy Investigation
              </div>
              <h2 style={{ fontSize: '1.3rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', marginTop: '2px', textTransform: 'uppercase' }}>
                {selectedType.replace('_', '-')} Questions ({typeQuestions.length})
              </h2>
            </div>

            {/* Token & Latency Resource Badges */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <div
                style={{
                  background: '#fef3c7',
                  border: '1px solid #fde68a',
                  color: '#b45309',
                  borderRadius: '4px',
                  padding: '5px 12px',
                  fontSize: '0.74rem',
                  fontFamily: 'Space Mono',
                  fontWeight: 800,
                }}
              >
                RAG: {currentStats.tokens_avg.rag} tok • {currentStats.latency_avg_s.rag.toFixed(1)}s
              </div>
              <div
                style={{
                  background: '#e0f2fe',
                  border: '1px solid #bae6fd',
                  color: '#0284c7',
                  borderRadius: '4px',
                  padding: '5px 12px',
                  fontSize: '0.74rem',
                  fontFamily: 'Space Mono',
                  fontWeight: 800,
                }}
              >
                GRAPH: {currentStats.tokens_avg.graphrag} tok • {currentStats.latency_avg_s.graphrag.toFixed(1)}s
              </div>
              <div
                style={{
                  background: '#ffedd5',
                  border: '1px solid #fdba74',
                  color: '#e75a24',
                  borderRadius: '4px',
                  padding: '5px 12px',
                  fontSize: '0.74rem',
                  fontFamily: 'Space Mono',
                  fontWeight: 800,
                }}
              >
                AGENT: {currentStats.tokens_avg.agent} tok • {currentStats.latency_avg_s.agent.toFixed(1)}s
              </div>
            </div>
          </div>

          {/* Question List Using Explorer Card Format */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '550px', overflowY: 'auto', paddingRight: '4px' }}>
            {typeQuestions.map((q) => {
              const { barColor, icon } = getTypeStyling(q.query_type);
              const goldText = Array.isArray(q.gold_answer) ? q.gold_answer.join(', ') : String(q.gold_answer);

              return (
                <div
                  key={q.question_id}
                  onClick={() => onSelectQuestion(q)}
                  style={{
                    background: '#f5ebe1',
                    border: '1px solid #dac7b2',
                    borderLeft: `5px solid ${barColor}`,
                    borderRadius: '6px',
                    padding: '14px 18px',
                    display: 'grid',
                    gridTemplateColumns: '120px 1fr auto auto',
                    alignItems: 'center',
                    gap: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {/* Col 1: Icon + QID + Query Type */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    <div style={{ marginBottom: '2px' }}>
                      {icon}
                    </div>
                    <div style={{ fontSize: '0.92rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                      {q.question_id}
                    </div>
                    <div style={{ fontSize: '0.68rem', fontFamily: 'Space Mono', fontWeight: 700, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      {q.query_type.replace('_', '-')}
                    </div>
                  </div>

                  {/* Col 2: Question text & Gold Answer with Trophy */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ fontSize: '0.92rem', fontWeight: 700, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1.35 }}>
                      {q.question}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', fontFamily: 'Space Grotesk' }}>
                      <span style={{ fontSize: '0.9rem' }}>🏆</span>
                      <span style={{ color: '#0284c7', fontWeight: 700 }}>
                        Gold: {goldText}
                      </span>
                    </div>
                  </div>

                  {/* Col 3: Three Pipeline Status Badges (RAG, GRAPH, AGENT) */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div
                      style={{
                        background: q.rag.correct ? '#e9f5ec' : '#fce8e8',
                        border: `1px solid ${q.rag.correct ? '#86efac' : '#fca5a5'}`,
                        color: q.rag.correct ? '#15803d' : '#b91c1c',
                        borderRadius: '4px',
                        padding: '5px 10px',
                        fontSize: '0.74rem',
                        fontFamily: 'Space Mono',
                        fontWeight: 800,
                        letterSpacing: '0.04em',
                      }}
                    >
                      RAG {q.rag.correct ? '✓' : '✗'}
                    </div>

                    <div
                      style={{
                        background: q.graphrag.correct ? '#e9f5ec' : '#fce8e8',
                        border: `1px solid ${q.graphrag.correct ? '#86efac' : '#fca5a5'}`,
                        color: q.graphrag.correct ? '#15803d' : '#b91c1c',
                        borderRadius: '4px',
                        padding: '5px 10px',
                        fontSize: '0.74rem',
                        fontFamily: 'Space Mono',
                        fontWeight: 800,
                        letterSpacing: '0.04em',
                      }}
                    >
                      GRAPH {q.graphrag.correct ? '✓' : '✗'}
                    </div>

                    <div
                      style={{
                        background: q.agent.correct ? '#ffedd5' : '#fce8e8',
                        border: `1px solid ${q.agent.correct ? '#fdba74' : '#fca5a5'}`,
                        color: q.agent.correct ? '#e75a24' : '#b91c1c',
                        borderRadius: '4px',
                        padding: '5px 10px',
                        fontSize: '0.74rem',
                        fontFamily: 'Space Mono',
                        fontWeight: 800,
                        letterSpacing: '0.04em',
                      }}
                    >
                      AGENT {q.agent.correct ? '✓' : '✗'}
                    </div>
                  </div>

                  {/* Col 4: Inspect Button */}
                  <div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectQuestion(q);
                      }}
                      style={{
                        background: '#f5ebe1',
                        border: '1px solid #141414',
                        borderRadius: '4px',
                        padding: '6px 14px',
                        fontSize: '0.78rem',
                        fontFamily: 'Space Grotesk',
                        fontWeight: 800,
                        color: '#141414',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <Eye size={14} />
                      <span>Inspect</span>
                      <span>→</span>
                    </button>
                  </div>

                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};
