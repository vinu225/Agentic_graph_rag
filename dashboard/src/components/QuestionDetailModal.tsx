import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Zap, 
  Layers, 
  Info,
  Maximize2
} from 'lucide-react';
import { BenchmarkQuestion, TraceStep } from '../types/benchmark';
import { explainOutcome } from '../utils/explainer';

interface QuestionDetailModalProps {
  question: BenchmarkQuestion | null;
  onClose: () => void;
}

export const QuestionDetailModal: React.FC<QuestionDetailModalProps> = ({
  question,
  onClose,
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0);
  const [expandedJsonStep, setExpandedJsonStep] = useState<number | null>(null);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1500); // ms per step

  const trace: TraceStep[] = question?.agent?.trace || [];
  const goldText = question
    ? (Array.isArray(question.gold_answer) ? question.gold_answer.join(', ') : question.gold_answer)
    : '';

  // Handle Trace Playback
  React.useEffect(() => {
    let timer: any;
    if (isPlaying && trace.length > 0) {
      timer = setTimeout(() => {
        if (activeStepIndex < trace.length - 1) {
          setActiveStepIndex(prev => prev + 1);
        } else {
          setIsPlaying(false);
        }
      }, playbackSpeed);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, activeStepIndex, trace.length, playbackSpeed]);

  const restartPlayback = () => {
    setActiveStepIndex(0);
    setIsPlaying(true);
  };

  if (!question) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 17, 21, 0.75)',
        backdropFilter: 'blur(4px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
      onClick={onClose}
    >
      <div
        className="panel animate-fade-in"
        style={{
          width: '100%',
          maxWidth: '1080px',
          maxHeight: '92vh',
          overflowY: 'auto',
          backgroundColor: '#f5ebe1',
          borderColor: '#dac7b2',
          borderWidth: '2px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
          padding: '30px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #dac7b2', paddingBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge badge-rag" style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
                {question.question_id}
              </span>
              <span className="badge" style={{ background: '#ece0d1', color: '#141414', border: '1px solid #c4b09b' }}>
                {question.query_type.toUpperCase()}
              </span>
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.3, textTransform: 'uppercase' }}>
              {question.question}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '1.4rem',
              cursor: 'pointer',
              padding: '4px 8px',
            }}
          >
            ✕
          </button>
        </div>

        {/* Ground Truth Banner */}
        <div
          style={{
            background: '#e9f5ec',
            border: '2px solid #15803d',
            borderRadius: '4px',
            padding: '12px 18px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <span className="hex-bullet" style={{ backgroundColor: '#15803d' }} />
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#15803d', fontWeight: 800, fontFamily: 'Space Mono' }}>
              GROUND TRUTH (GOLD ANSWER)
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#141414', marginTop: '2px', fontFamily: 'Space Grotesk' }}>
              {goldText}
            </div>
          </div>
        </div>

        {/* 3 Pipeline Output Comparison */}
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', fontFamily: 'Space Mono', marginBottom: '12px' }}>
            Pipeline Side-by-Side Verification
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
            
            {/* Plain RAG */}
            <div
              style={{
                background: '#ece0d1',
                border: `2px solid ${question.rag.correct ? '#15803d' : '#b91c1c'}`,
                borderRadius: '6px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span className="badge badge-rag">Plain RAG (BM25)</span>
                  <span className={`badge ${question.rag.correct ? 'badge-success' : 'badge-danger'}`}>
                    {question.rag.correct ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-primary)', lineHeight: 1.5, margin: '10px 0', minHeight: '60px', fontFamily: 'Space Grotesk' }}>
                  {question.rag.answer || 'No response generated.'}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '14px', fontSize: '0.74rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px', fontFamily: 'Space Mono' }}>
                <span>TOKENS: {question.rag.tokens.toLocaleString()}</span>
                <span>LATENCY: {question.rag.latency || question.rag.elapsed_time_s?.toFixed(2)}s</span>
              </div>
            </div>

            {/* GraphRAG */}
            <div
              style={{
                background: '#ece0d1',
                border: `2px solid ${question.graphrag.correct ? '#15803d' : '#b91c1c'}`,
                borderRadius: '6px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span className="badge badge-graphrag">Single-Pass GraphRAG</span>
                  <span className={`badge ${question.graphrag.correct ? 'badge-success' : 'badge-danger'}`}>
                    {question.graphrag.correct ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-primary)', lineHeight: 1.5, margin: '10px 0', minHeight: '60px', fontFamily: 'Space Grotesk' }}>
                  {question.graphrag.answer || 'No response generated.'}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '14px', fontSize: '0.74rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px', fontFamily: 'Space Mono' }}>
                <span>TOKENS: {question.graphrag.tokens.toLocaleString()}</span>
                <span>LATENCY: {question.graphrag.latency || question.graphrag.elapsed_time_s?.toFixed(2)}s</span>
              </div>
            </div>

            {/* Agentic GraphRAG */}
            <div
              style={{
                background: '#ece0d1',
                border: `2px solid ${question.agent.correct ? '#e75a24' : '#b91c1c'}`,
                borderRadius: '6px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span className="badge badge-agent">Agentic GraphRAG (ReAct)</span>
                  <span className={`badge ${question.agent.correct ? 'badge-success' : 'badge-danger'}`}>
                    {question.agent.correct ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-primary)', lineHeight: 1.5, margin: '10px 0', minHeight: '60px', fontFamily: 'Space Grotesk' }}>
                  {question.agent.answer || 'No response generated.'}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '12px', fontSize: '0.74rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px', fontFamily: 'Space Mono' }}>
                <span>TOKENS: {question.agent.tokens.toLocaleString()}</span>
                <span>LATENCY: {question.agent.latency || question.agent.elapsed_time_s?.toFixed(2)}s</span>
                <span style={{ color: '#e75a24', fontWeight: 700 }}>STEPS: {question.agent.total_steps || trace.length}</span>
              </div>
            </div>

          </div>
        </div>

        {/* Why Did This Answer Win / Fail Explanation */}
        <div
          style={{
            background: '#ece0d1',
            border: '2px solid #dac7b2',
            borderRadius: '6px',
            padding: '16px 20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#e75a24', fontSize: '0.8rem', fontWeight: 800, fontFamily: 'Space Mono', textTransform: 'uppercase', marginBottom: '6px' }}>
            <span className="hex-bullet" style={{ width: '8px', height: '8px' }} />
            DETERMINISTIC OUTCOME ANALYSIS
          </div>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontFamily: 'Space Grotesk' }}>
            {explainOutcome(question)}
          </p>
        </div>

        {/* Agentic Trajectory & Interactive Playback */}
        {trace.length > 0 && (
          <div
            style={{
              border: '2px solid #dac7b2',
              borderRadius: '6px',
              padding: '22px',
              background: '#ece0d1',
            }}
          >
            {/* Playback Controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="hex-bullet" />
                  <span>AUTONOMOUS TOOL TRAJECTORY</span>
                  <span className="badge badge-agent">{trace.length} STEPS RECORDED</span>
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'Space Mono', marginTop: '2px' }}>
                  Step-by-step reasoning hops, tool selection, argument dictionary, and latency profile
                </div>
              </div>

              {/* Player Button Toolbar */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    backgroundColor: isPlaying ? '#b91c1c' : '#e75a24',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '8px 16px',
                    fontSize: '0.8rem',
                    fontFamily: 'Space Mono',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    cursor: 'pointer',
                  }}
                >
                  {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                  <span>{isPlaying ? 'PAUSE' : 'PLAY TRACE'}</span>
                </button>

                <button
                  onClick={restartPlayback}
                  title="Restart playback"
                  style={{
                    background: '#f5ebe1',
                    border: '1px solid #c4b09b',
                    color: 'var(--text-primary)',
                    borderRadius: '4px',
                    padding: '8px 10px',
                    cursor: 'pointer',
                  }}
                >
                  <RotateCcw size={14} />
                </button>

                <button
                  disabled={activeStepIndex === 0}
                  onClick={() => setActiveStepIndex(p => Math.max(0, p - 1))}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-secondary)',
                    borderRadius: '6px',
                    padding: '6px 10px',
                    cursor: activeStepIndex === 0 ? 'not-allowed' : 'pointer',
                    opacity: activeStepIndex === 0 ? 0.4 : 1,
                  }}
                >
                  <ChevronLeft size={14} />
                </button>

                <span style={{ fontSize: '0.78rem', color: '#94a3b8', padding: '0 4px' }}>
                  {activeStepIndex + 1} / {trace.length}
                </span>

                <button
                  disabled={activeStepIndex === trace.length - 1}
                  onClick={() => setActiveStepIndex(p => Math.min(trace.length - 1, p + 1))}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-secondary)',
                    borderRadius: '6px',
                    padding: '6px 10px',
                    cursor: activeStepIndex === trace.length - 1 ? 'not-allowed' : 'pointer',
                    opacity: activeStepIndex === trace.length - 1 ? 0.4 : 1,
                  }}
                >
                  <ChevronRight size={14} />
                </button>

                <select
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                  style={{
                    background: 'var(--bg-card)',
                    color: '#94a3b8',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    padding: '5px 8px',
                    fontSize: '0.74rem',
                    outline: 'none',
                  }}
                >
                  <option value={2500}>0.5x Speed</option>
                  <option value={1500}>1.0x Speed</option>
                  <option value={800}>2.0x Speed</option>
                </select>
              </div>
            </div>

            {/* Stepper Timeline */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {trace.map((step, idx) => {
                const isCurrent = activeStepIndex === idx;
                const isPast = activeStepIndex > idx;
                const isJsonExpanded = expandedJsonStep === idx;

                return (
                  <div
                    key={idx}
                    onClick={() => setActiveStepIndex(idx)}
                    style={{
                      border: `2px solid ${isCurrent ? '#e75a24' : isPast ? '#15803d' : '#dac7b2'}`,
                      backgroundColor: isCurrent ? '#f5ebe1' : '#f0e5d8',
                      borderRadius: '4px',
                      padding: '14px 18px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span
                          style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '4px',
                            background: isCurrent ? '#e75a24' : isPast ? '#15803d' : '#857c72',
                            color: '#fff',
                            fontSize: '0.75rem',
                            fontFamily: 'Space Mono',
                            fontWeight: 700,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          {idx + 1}
                        </span>
                        <span style={{ fontWeight: 800, fontSize: '0.9rem', color: 'var(--text-primary)', fontFamily: 'Space Grotesk' }}>
                          TOOL: <code style={{ color: '#e75a24', background: '#f5ebe1', padding: '2px 6px', borderRadius: '3px' }}>{step.tool}</code>
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '14px', fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'Space Mono' }}>
                        <span>⚡ {step.tokens.toLocaleString()} tok</span>
                        <span>⏱️ {step.duration_s?.toFixed(2)}s</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedJsonStep(isJsonExpanded ? null : idx);
                          }}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#e75a24',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontFamily: 'Space Mono',
                            fontWeight: 700,
                          }}
                        >
                          <Maximize2 size={12} />
                          {isJsonExpanded ? 'HIDE JSON' : 'INSPECT JSON'}
                        </button>
                      </div>
                    </div>

                    {/* Step Arguments preview */}
                    <div style={{ marginTop: '8px', fontSize: '0.78rem', color: 'var(--text-secondary)', fontFamily: 'Space Mono' }}>
                      <strong>ARGS:</strong>{' '}
                      <span style={{ color: '#141414' }}>
                        {JSON.stringify(step.args)}
                      </span>
                    </div>

                    {/* Expanded Raw JSON View */}
                    {isJsonExpanded && (
                      <pre
                        className="font-mono"
                        style={{
                          marginTop: '12px',
                          background: '#090d16',
                          padding: '12px',
                          borderRadius: '6px',
                          fontSize: '0.72rem',
                          color: '#34d399',
                          overflowX: 'auto',
                          border: '1px solid #1e293b',
                        }}
                      >
                        {JSON.stringify(step, null, 2)}
                      </pre>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
