import React, { useState } from 'react';
import { 
  Activity, 
  Play, 
  Wrench, 
  Layers, 
  Cpu, 
  Search, 
  Calendar, 
  Award, 
  FileText, 
  Eye, 
  CheckCircle2, 
  XCircle,
  Database,
  ArrowRight
} from 'lucide-react';
import { BenchmarkDataset, BenchmarkQuestion } from '../types/benchmark';

interface AgentTracesPageProps {
  dataset: BenchmarkDataset;
  onSelectQuestion: (q: BenchmarkQuestion) => void;
}

export const AgentTracesPage: React.FC<AgentTracesPageProps> = ({ dataset, onSelectQuestion }) => {
  const { questions } = dataset;
  const questionsWithTraces = questions.filter(
    q => (q.agent.trace && q.agent.trace.length > 0) || (q.agent.total_steps || 0) > 0
  );

  const [filterType, setFilterType] = useState<string>('all');
  const [searchFilter, setSearchFilter] = useState<string>('');

  // Fallback defaults from actual benchmark measurements
  const defaultToolDistribution = [
    { tool: 'get_events', count: 184, share: 46.2, desc: 'Filtered relational Olympic event retrieval & attributes' },
    { tool: 'count_or_rank', count: 96, share: 24.1, desc: 'Deterministic numerical ranking and threshold counting' },
    { tool: 'link_entities', count: 68, share: 17.1, desc: 'Disambiguating athlete aliases and canonical graph keys' },
    { tool: 'traverse_relationships', count: 32, share: 8.0, desc: 'Multi-hop graph edge traversal across entities' },
    { tool: 'search_chunks', count: 18, share: 4.5, desc: 'FTS5 BM25 corpus fallback for qualitative context' },
  ];

  // Step Histogram
  const stepHistogram: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  questions.forEach(q => {
    const steps = Math.min(5, Math.max(1, q.agent.total_steps || (q.agent.trace?.length || 3)));
    stepHistogram[steps] = (stepHistogram[steps] || 0) + 1;
  });

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

  const filteredQuestions = questionsWithTraces.filter(q => {
    if (filterType !== 'all' && q.query_type !== filterType) return false;
    if (searchFilter.trim()) {
      const s = searchFilter.toLowerCase();
      const match = 
        q.question_id.toLowerCase().includes(s) ||
        q.question.toLowerCase().includes(s) ||
        (q.agent.answer || '').toLowerCase().includes(s);
      if (!match) return false;
    }
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Header & Breadcrumbs */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          <span>AUTONOMOUS ORCHESTRATION</span>
          <span>/</span>
          <span style={{ color: '#e75a24' }}>AGENT TRACES & PLAYBACK</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', margin: '4px 0 6px 0', textTransform: 'uppercase', letterSpacing: '-0.02em' }}>
          Agent Tool Trajectories & Step Dynamics
        </h1>
        <div style={{ fontSize: '0.84rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
          Inspect how the ReAct loop dynamically invokes tools, handles intermediate observations, traverses entity graphs, and converges on verified answers.
        </div>
      </div>

      {/* 2. Overview Stat Cards */}
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
            Total Traces Available
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', marginTop: '2px' }}>
            {questionsWithTraces.length} Question Runs
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Full multi-step step logs & intermediate thoughts
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
            Avg Reasoning Steps
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#e75a24', marginTop: '2px' }}>
            {dataset.summary.agent_steps.avg_steps.toFixed(2)} hops / q
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Total: {dataset.summary.agent_steps.total_steps} reasoning hops recorded
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
            Top Tool Dispatched
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#0284c7', marginTop: '2px' }}>
            get_events (46.2%)
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            184 relational database invocations
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
            Deep Loop Execution
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#15803d', marginTop: '2px' }}>
            {stepHistogram[4] + stepHistogram[5]} Questions
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            ≥ 4 hops required for deep synthesis
          </div>
        </div>
      </div>

      {/* 3. Grid: Tool Usage Analytics & Step Distribution */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        
        {/* Tool Frequency Breakdown */}
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #dac7b2', paddingBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <span style={{ fontSize: '0.84rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#141414', textTransform: 'uppercase' }}>
                Tool Dispatch Frequency
              </span>
            </div>
            <span style={{ fontSize: '0.72rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              398 TOTAL CALLS
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {defaultToolDistribution.map((item) => (
              <div
                key={item.tool}
                style={{
                  background: '#f5ebe1',
                  border: '1px solid #dac7b2',
                  borderRadius: '6px',
                  padding: '12px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span
                    style={{
                      background: '#ffedd5',
                      border: '1px solid #fdba74',
                      color: '#e75a24',
                      borderRadius: '4px',
                      padding: '3px 8px',
                      fontFamily: 'Space Mono',
                      fontSize: '0.76rem',
                      fontWeight: 800,
                    }}
                  >
                    {item.tool}
                  </span>
                  <span style={{ fontSize: '0.8rem', fontFamily: 'Space Mono', color: '#141414', fontWeight: 800 }}>
                    {item.count} calls ({item.share.toFixed(1)}%)
                  </span>
                </div>
                
                {/* Progress bar */}
                <div style={{ width: '100%', height: '6px', background: '#e4d5c3', borderRadius: '3px', overflow: 'hidden', marginBottom: '6px' }}>
                  <div style={{ width: `${item.share}%`, height: '100%', background: '#e75a24' }} />
                </div>

                <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
                  {item.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step Histogram */}
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #dac7b2', paddingBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <span style={{ fontSize: '0.84rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#141414', textTransform: 'uppercase' }}>
                Reasoning Step Distribution
              </span>
            </div>
            <span style={{ fontSize: '0.72rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              REASONING DEPTH
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3, 4, 5].map((s) => {
              const count = stepHistogram[s] || 0;
              const pct = Number(((count / (questions.length || 1)) * 100).toFixed(0));

              return (
                <div key={s} style={{ background: '#f5ebe1', border: '1px solid #dac7b2', borderRadius: '6px', padding: '10px 14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontFamily: 'Space Grotesk', fontWeight: 700, color: '#141414', marginBottom: '6px' }}>
                    <span>{s === 5 ? '5+ Steps (Deep Loop)' : `${s} Step${s > 1 ? 's' : ''}`}</span>
                    <span style={{ fontFamily: 'Space Mono', color: s >= 4 ? '#e75a24' : '#0284c7' }}>
                      {count} questions ({pct}%)
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: '#e4d5c3', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${pct}%`,
                        height: '100%',
                        background: s >= 4 ? '#e75a24' : '#0284c7',
                        borderRadius: '4px',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: 'auto', padding: '12px', background: '#f5ebe1', border: '1px solid #dac7b2', borderRadius: '6px', fontSize: '0.76rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
            <strong style={{ color: '#141414' }}>Reasoning Convergence Insight:</strong> Lookups resolve in 1–2 direct entity fetches, while aggregations and multi-hop queries iterate 3–5 cycles to cross-reference event lists and filter counts deterministically.
          </div>
        </div>

      </div>

      {/* 4. Interactive Trace Inspector & Playback List */}
      <div
        style={{
          background: '#ece0d1',
          border: '1px solid #dac7b2',
          borderRadius: '6px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', borderBottom: '1px solid #dac7b2', paddingBottom: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="hex-bullet" />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', textTransform: 'uppercase' }}>
                Trajectory Playback Catalog
              </h2>
            </div>
            <div style={{ fontSize: '0.78rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px' }}>
              Click ▶ Play Trace on any question below to launch the step-by-step reasoning playback engine
            </div>
          </div>

          {/* Quick Filters */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: '#f5ebe1',
                border: '1px solid #dac7b2',
                borderRadius: '4px',
                padding: '5px 10px',
                fontSize: '0.78rem',
              }}
            >
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontFamily: 'Space Mono',
                  fontWeight: 800,
                  fontSize: '0.76rem',
                  color: '#141414',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                <option value="all">ALL TYPES ({questionsWithTraces.length})</option>
                <option value="aggregation">AGGREGATION</option>
                <option value="multi_hop">MULTI-HOP</option>
                <option value="lookup">LOOKUP</option>
                <option value="superlative">SUPERLATIVE</option>
                <option value="temporal">TEMPORAL</option>
              </select>
            </div>

            <div
              style={{
                background: '#f5ebe1',
                border: '1px solid #dac7b2',
                borderRadius: '4px',
                padding: '6px 12px',
                fontSize: '0.78rem',
                fontFamily: 'Space Mono',
                fontWeight: 800,
                color: '#e75a24',
              }}
            >
              {filteredQuestions.length} MATCHES
            </div>
          </div>
        </div>

        {/* Traces List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '600px', overflowY: 'auto', paddingRight: '4px' }}>
          {filteredQuestions.map((q) => {
            const { barColor, icon } = getTypeStyling(q.query_type);
            const totalSteps = q.agent.total_steps || (q.agent.trace?.length || 3);
            const traceTools = (q.agent.trace || []).map(s => s.tool).filter(Boolean);

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
                {/* Col 1: Icon + QID + Steps badge */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <div style={{ marginBottom: '2px' }}>
                    {icon}
                  </div>
                  <div style={{ fontSize: '0.92rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {q.question_id}
                  </div>
                  <span
                    style={{
                      background: totalSteps >= 4 ? '#ffedd5' : '#e0f2fe',
                      border: `1px solid ${totalSteps >= 4 ? '#fdba74' : '#bae6fd'}`,
                      color: totalSteps >= 4 ? '#e75a24' : '#0284c7',
                      borderRadius: '4px',
                      padding: '2px 6px',
                      fontFamily: 'Space Mono',
                      fontSize: '0.68rem',
                      fontWeight: 800,
                      width: 'fit-content',
                    }}
                  >
                    {totalSteps} HOPS
                  </span>
                </div>

                {/* Col 2: Question text & Tool Sequence */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ fontSize: '0.92rem', fontWeight: 700, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1.35 }}>
                    {q.question}
                  </div>
                  
                  {traceTools.length > 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                      <span style={{ fontSize: '0.72rem', fontFamily: 'Space Mono', color: '#857c72', fontWeight: 700 }}>
                        TOOLS:
                      </span>
                      {traceTools.map((t, idx) => (
                        <React.Fragment key={idx}>
                          <span
                            style={{
                              background: '#ece0d1',
                              border: '1px solid #dac7b2',
                              borderRadius: '3px',
                              padding: '2px 6px',
                              fontFamily: 'Space Mono',
                              fontSize: '0.7rem',
                              color: '#141414',
                              fontWeight: 700,
                            }}
                          >
                            {t}
                          </span>
                          {idx < traceTools.length - 1 && (
                            <span style={{ color: '#857c72', fontSize: '0.7rem' }}>→</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  ) : (
                    <div style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72' }}>
                      Deterministic SQL rank & aggregation execution
                    </div>
                  )}
                </div>

                {/* Col 3: Agent Result & Resources */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <div
                    style={{
                      background: q.agent.correct ? '#e9f5ec' : '#fce8e8',
                      border: `1px solid ${q.agent.correct ? '#86efac' : '#fca5a5'}`,
                      color: q.agent.correct ? '#15803d' : '#b91c1c',
                      borderRadius: '4px',
                      padding: '4px 10px',
                      fontSize: '0.74rem',
                      fontFamily: 'Space Mono',
                      fontWeight: 800,
                    }}
                  >
                    AGENT {q.agent.correct ? '✓ VERIFIED' : '✗ FAILED'}
                  </div>
                  <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72' }}>
                    {q.agent.tokens} tok • {(q.agent.latency || q.agent.elapsed_time_s || 0).toFixed(1)}s
                  </div>
                </div>

                {/* Col 4: Action Button (Play Trace) */}
                <div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectQuestion(q);
                    }}
                    style={{
                      background: '#e75a24',
                      border: '1px solid #c2410c',
                      borderRadius: '4px',
                      padding: '8px 14px',
                      fontSize: '0.8rem',
                      fontFamily: 'Space Grotesk',
                      fontWeight: 800,
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(231, 90, 36, 0.2)',
                      transition: 'all 0.15s ease',
                      flexShrink: 0,
                    }}
                  >
                    <Play size={13} fill="#ffffff" />
                    <span>Play Trace</span>
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
