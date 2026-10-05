import React from 'react';
import { 
  Database, 
  AlertTriangle, 
  Layers, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  FileText, 
  Award,
  ArrowRight,
  TrendingDown,
  TrendingUp,
  Cpu
} from 'lucide-react';
import { BenchmarkDataset, BenchmarkQuestion } from '../types/benchmark';

interface RetrievalPageProps {
  dataset: BenchmarkDataset;
  onSelectQuestion: (q: BenchmarkQuestion) => void;
}

export const RetrievalPage: React.FC<RetrievalPageProps> = ({ dataset, onSelectQuestion }) => {
  // Candidate truncation questions (Aggregation queries)
  const aggregationQuestions = dataset.questions.filter(q => q.query_type === 'aggregation');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Header & Breadcrumbs */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          <span>INFORMATION RETRIEVAL THEORY</span>
          <span>/</span>
          <span style={{ color: '#e75a24' }}>FRAC@8 RETRIEVAL GAP</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', margin: '4px 0 6px 0', textTransform: 'uppercase', letterSpacing: '-0.02em' }}>
          The Frac@8 Retrieval Completeness Gap
        </h1>
        <div style={{ fontSize: '0.84rem', fontFamily: 'Space Grotesk', color: '#665d53' }}>
          Why Top-K unstructured chunk retrieval fundamentally breaks on high-cardinality multi-document counting questions, and how deterministic graph execution solves it.
        </div>
      </div>

      {/* 2. Key Theoretical Metrics Cards */}
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
            Impacted Query Scope
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', marginTop: '2px' }}>
            {aggregationQuestions.length} Questions
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            High-cardinality multi-event filtering & counting
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
            Plain RAG Baseline
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#b91c1c', marginTop: '2px' }}>
            0.0% Accuracy
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            0 out of {aggregationQuestions.length} correct due to chunk truncation
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
            GraphRAG Baseline
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#d97706', marginTop: '2px' }}>
            9.5% Accuracy
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Partial graph expansion still drops boundary events
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
            Agentic GraphRAG
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#e75a24', marginTop: '2px' }}>
            95.2% Accuracy
          </div>
          <div style={{ fontSize: '0.74rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '4px' }}>
            Deterministic SQL threshold counting eliminates hallucinations
          </div>
        </div>
      </div>

      {/* 3. Conceptual Illustration Panel */}
      <div
        style={{
          background: '#ece0d1',
          border: '1px solid #dac7b2',
          borderRadius: '6px',
          padding: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '24px',
        }}
      >
        {/* Left Column: Theory & Mathematics */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
            <span className="hex-bullet" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 900, fontFamily: 'Space Grotesk', color: '#141414', textTransform: 'uppercase' }}>
              The Top-K Context Window Truncation Problem
            </h2>
          </div>

          <p style={{ fontSize: '0.86rem', fontFamily: 'Space Grotesk', color: '#332d27', lineHeight: 1.6, marginBottom: '12px' }}>
            Consider a typical aggregation benchmark question: <br />
            <strong style={{ color: '#141414', background: '#f5ebe1', padding: '2px 6px', borderRadius: '4px', border: '1px solid #dac7b2' }}>
              "How many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"
            </strong>
          </p>

          <p style={{ fontSize: '0.84rem', fontFamily: 'Space Grotesk', color: '#524940', lineHeight: 1.6, marginBottom: '14px' }}>
            To answer this accurately, all <strong>11 biathlon events</strong> must be retrieved and checked against the threshold ($n &gt; 73$). Standard vector RAG retrieves at most <strong>k=8 chunks</strong>. Even with perfect BM25 or embedding cosine similarity, each chunk only spans 1–2 events.
          </p>

          <div
            style={{
              background: '#f5ebe1',
              border: '1px solid #dac7b2',
              borderRadius: '6px',
              padding: '12px 16px',
              fontFamily: 'Space Mono',
              fontSize: '0.76rem',
              color: '#141414',
              lineHeight: 1.5,
            }}
          >
            <div style={{ fontWeight: 800, color: '#e75a24', marginBottom: '4px' }}>
              FORMAL RETRIEVAL COMPLETENESS METRIC:
            </div>
            Frac@8 = |E_retrieved ∩ E_target| / |E_target| = 4 / 11 = <strong>36.4%</strong>
            <div style={{ color: '#b91c1c', marginTop: '4px' }}>
              → Unseen candidate events cannot be counted by the generator, guaranteeing failure.
            </div>
          </div>
        </div>

        {/* Right Column: Visual Evidence Capture Bars */}
        <div
          style={{
            background: '#f5ebe1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '18px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #dac7b2', paddingBottom: '10px' }}>
            <span style={{ fontSize: '0.84rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#141414' }}>
              EVIDENCE CAPTURE FRACTION (Frac@8)
            </span>
            <span style={{ fontSize: '0.72rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              CASE STUDY: BIATHLON 2018
            </span>
          </div>

          {/* Bar 1: Ground Truth */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontFamily: 'Space Grotesk', fontWeight: 700, marginBottom: '6px' }}>
              <span style={{ color: '#15803d' }}>Ground Truth Evidence Pool (11 Events)</span>
              <span style={{ fontFamily: 'Space Mono', color: '#15803d' }}>100% (11/11)</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: '#e4d5c3', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '100%', height: '100%', background: '#15803d' }} />
            </div>
            <div style={{ fontSize: '0.72rem', fontFamily: 'Space Grotesk', color: '#15803d', marginTop: '3px' }}>
              Complete dataset records present in relational schema
            </div>
          </div>

          {/* Bar 2: Plain RAG */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontFamily: 'Space Grotesk', fontWeight: 700, marginBottom: '6px' }}>
              <span style={{ color: '#b91c1c' }}>Plain RAG Top-8 Chunks Captured</span>
              <span style={{ fontFamily: 'Space Mono', color: '#b91c1c' }}>36.4% (4/11)</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: '#e4d5c3', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '36.4%', height: '100%', background: '#b91c1c' }} />
            </div>
            <div style={{ fontSize: '0.72rem', fontFamily: 'Space Grotesk', color: '#b91c1c', marginTop: '3px' }}>
              Result: Context overflow & counting hallucination (0.0% accuracy)
            </div>
          </div>

          {/* Bar 3: Agentic Graph */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontFamily: 'Space Grotesk', fontWeight: 700, marginBottom: '6px' }}>
              <span style={{ color: '#e75a24' }}>Agentic Graph Search Captured</span>
              <span style={{ fontFamily: 'Space Mono', color: '#e75a24' }}>100% (11/11)</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: '#e4d5c3', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '100%', height: '100%', background: '#e75a24' }} />
            </div>
            <div style={{ fontSize: '0.72rem', fontFamily: 'Space Grotesk', color: '#c2410c', marginTop: '3px' }}>
              Result: SQL threshold filter counts all records deterministically (95.2% accuracy)
            </div>
          </div>

        </div>
      </div>

      {/* 4. Case Study List of Affected Benchmark Questions */}
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
                Benchmark Questions Exhibiting the Retrieval Gap
              </h2>
            </div>
            <div style={{ fontSize: '0.78rem', fontFamily: 'Space Grotesk', color: '#665d53', marginTop: '2px' }}>
              Real questions from the benchmark where Top-K chunk truncation completely blinds baseline RAG while Agentic execution succeeds
            </div>
          </div>

          <span
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
            {aggregationQuestions.length} CASE STUDIES
          </span>
        </div>

        {/* Questions List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '550px', overflowY: 'auto', paddingRight: '4px' }}>
          {aggregationQuestions.map((q) => {
            const goldText = Array.isArray(q.gold_answer) ? q.gold_answer.join(', ') : String(q.gold_answer);

            return (
              <div
                key={q.question_id}
                onClick={() => onSelectQuestion(q)}
                style={{
                  background: '#f5ebe1',
                  border: '1px solid #dac7b2',
                  borderLeft: '5px solid #e75a24',
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
                {/* Col 1: QID & Query Type */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  <div style={{ fontSize: '0.92rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                    {q.question_id}
                  </div>
                  <div style={{ fontSize: '0.68rem', fontFamily: 'Space Mono', fontWeight: 700, color: '#e75a24', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    AGGREGATION
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

                {/* Col 3: Two Badges highlighting the Frac@8 Gap */}
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
                    }}
                  >
                    RAG {q.rag.correct ? '✓' : '✗ (Truncated)'}
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
                    }}
                  >
                    AGENT {q.agent.correct ? '✓ (Captured All)' : '✗'}
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

    </div>
  );
};
