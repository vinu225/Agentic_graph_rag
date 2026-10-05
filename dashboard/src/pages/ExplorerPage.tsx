import React, { useState } from 'react';
import { 
  Database,
  Search,
  ChevronDown,
  LayoutGrid,
  Zap,
  X,
  BarChart2,
  AlertTriangle,
  Menu,
  FileText,
  Calendar,
  Award,
  HelpCircle,
  Eye,
  ArrowRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { BenchmarkDataset, BenchmarkQuestion } from '../types/benchmark';
import { benchmarkKeys } from '../data/datasetManager';

interface ExplorerPageProps {
  dataset: BenchmarkDataset;
  activeDatasetId: string;
  onSelectDataset: (id: string) => void;
  selectedQueryType: string;
  onSelectQueryType: (type: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSelectQuestion: (q: BenchmarkQuestion) => void;
}

export const ExplorerPage: React.FC<ExplorerPageProps> = ({
  dataset,
  activeDatasetId,
  onSelectDataset,
  selectedQueryType,
  onSelectQueryType,
  searchQuery,
  onSearchChange,
  onSelectQuestion,
}) => {
  const [filterMode, setFilterMode] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('qid');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const { questions } = dataset;

  // Compute live filter counts
  const allCount = questions.length;
  const agentWinsCount = questions.filter(q => q.agent.correct && !q.rag.correct).length;
  const ragWinsCount = questions.filter(q => q.rag.correct && !q.agent.correct).length;
  const graphWinsCount = questions.filter(q => q.graphrag.correct && !q.rag.correct).length;
  const anyFailuresCount = questions.filter(q => !q.rag.correct || !q.graphrag.correct || !q.agent.correct).length;
  const deepStepsCount = questions.filter(q => (q.agent.total_steps || 0) >= 4 || (q.agent.trace && q.agent.trace.length >= 4)).length;

  // Filter questions
  const filteredQuestions = questions.filter((q) => {
    // Type Filter
    if (selectedQueryType !== 'all' && q.query_type !== selectedQueryType) {
      return false;
    }

    // Search Query Filter
    if (searchQuery.trim()) {
      const s = searchQuery.toLowerCase();
      const goldStr = Array.isArray(q.gold_answer) ? q.gold_answer.join(' ').toLowerCase() : String(q.gold_answer).toLowerCase();
      const matchesText = 
        q.question_id.toLowerCase().includes(s) ||
        q.question.toLowerCase().includes(s) ||
        goldStr.includes(s) ||
        (q.rag.answer || '').toLowerCase().includes(s) ||
        (q.agent.answer || '').toLowerCase().includes(s);
      if (!matchesText) return false;
    }

    // Quick Filter Mode
    if (filterMode === 'agent_wins') {
      return q.agent.correct && !q.rag.correct;
    }
    if (filterMode === 'rag_wins') {
      return q.rag.correct && !q.agent.correct;
    }
    if (filterMode === 'graph_wins') {
      return q.graphrag.correct && !q.rag.correct;
    }
    if (filterMode === 'only_failures') {
      return !q.rag.correct || !q.graphrag.correct || !q.agent.correct;
    }
    if (filterMode === 'deep_agent') {
      return (q.agent.total_steps || 0) >= 4 || (q.agent.trace && q.agent.trace.length >= 4);
    }

    return true;
  });

  // Sort questions
  const sortedQuestions = [...filteredQuestions].sort((a, b) => {
    let diff = 0;
    if (sortBy === 'qid') {
      diff = a.question_id.localeCompare(b.question_id, undefined, { numeric: true });
    } else if (sortBy === 'tokens') {
      diff = a.agent.tokens - b.agent.tokens;
    } else if (sortBy === 'latency') {
      diff = (a.agent.latency || a.agent.elapsed_time_s || 0) - (b.agent.latency || b.agent.elapsed_time_s || 0);
    } else if (sortBy === 'steps') {
      diff = (a.agent.total_steps || a.agent.trace?.length || 0) - (b.agent.total_steps || b.agent.trace?.length || 0);
    }
    return sortOrder === 'asc' ? diff : -diff;
  });

  // Helper for query type icon and theme bar
  const getTypeStyling = (type: string) => {
    switch (type.toLowerCase()) {
      case 'temporal':
        return {
          barColor: '#0d9488', // Teal
          icon: <Calendar size={18} style={{ color: '#0d9488' }} />,
        };
      case 'superlative':
        return {
          barColor: '#8b5cf6', // Violet
          icon: <Award size={18} style={{ color: '#8b5cf6' }} />,
        };
      case 'multi_hop':
        return {
          barColor: '#0284c7', // Blueprint Cyan
          icon: <FileText size={18} style={{ color: '#0284c7' }} />,
        };
      case 'aggregation':
      default:
        return {
          barColor: '#e75a24', // Industrial Orange
          icon: <FileText size={18} style={{ color: '#e75a24' }} />,
        };
    }
  };

  const queryTypes = ['all', 'aggregation', 'lookup', 'multi_hop', 'superlative', 'temporal'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* 1. Top Control Bar (Dataset Pill, Search Box, Query Type Dropdown) */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '12px',
          justifyContent: 'space-between',
        }}
      >
        {/* Left: Dataset Pill Selector */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: '#ece0d1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '6px 12px',
            gap: '8px',
          }}
        >
          <Database size={16} style={{ color: '#e75a24' }} />
          <span style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', fontWeight: 800, color: '#857c72', letterSpacing: '0.06em' }}>
            DATASET
          </span>
          <select
            value={activeDatasetId}
            onChange={(e) => onSelectDataset(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '0.84rem',
              fontWeight: 700,
              fontFamily: 'Space Grotesk',
              color: '#141414',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            {benchmarkKeys.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} ({item.count} Qs)
              </option>
            ))}
          </select>
        </div>

        {/* Center: Search Box */}
        <div
          style={{
            flex: 1,
            maxWidth: '520px',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Search size={16} style={{ position: 'absolute', left: '14px', color: '#857c72' }} />
          <input
            type="text"
            placeholder="Search QID, question text, athlete, event..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{
              width: '100%',
              background: '#f5ebe1',
              border: '1px solid #dac7b2',
              borderRadius: '6px',
              padding: '9px 12px 9px 38px',
              fontSize: '0.84rem',
              fontFamily: 'Space Grotesk',
              color: '#141414',
              outline: 'none',
            }}
          />
        </div>

        {/* Right: All Query Types Dropdown */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: '#f5ebe1',
            border: '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '7px 14px',
          }}
        >
          <select
            value={selectedQueryType}
            onChange={(e) => onSelectQueryType(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '0.8rem',
              fontFamily: 'Space Mono',
              fontWeight: 800,
              color: '#141414',
              textTransform: 'uppercase',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            {queryTypes.map((t) => (
              <option key={t} value={t}>
                {t === 'all' ? 'ALL QUERY TYPES' : t.replace('_', '-').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 2. Six Filter Metric Cards (Exactly as in Reference Image) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '12px',
        }}
      >
        {/* Card 1: All Questions */}
        <div
          onClick={() => setFilterMode('all')}
          style={{
            background: filterMode === 'all' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'all' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#e75a24' }}>
            <LayoutGrid size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              All Questions
            </div>
            <div style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              ({allCount})
            </div>
          </div>
        </div>

        {/* Card 2: Agentic Wins */}
        <div
          onClick={() => setFilterMode('agent_wins')}
          style={{
            background: filterMode === 'agent_wins' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'agent_wins' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#e75a24' }}>
            <Zap size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              Agentic Wins
            </div>
            <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              (Agent ✓, RAG ❌) ({agentWinsCount})
            </div>
          </div>
        </div>

        {/* Card 3: RAG Wins */}
        <div
          onClick={() => setFilterMode('rag_wins')}
          style={{
            background: filterMode === 'rag_wins' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'rag_wins' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#b91c1c' }}>
            <X size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              RAG Wins
            </div>
            <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              (RAG ✓, Agent ❌) ({ragWinsCount})
            </div>
          </div>
        </div>

        {/* Card 4: GraphRAG Wins */}
        <div
          onClick={() => setFilterMode('graph_wins')}
          style={{
            background: filterMode === 'graph_wins' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'graph_wins' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#0284c7' }}>
            <BarChart2 size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              GraphRAG Wins
            </div>
            <div style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              ({graphWinsCount})
            </div>
          </div>
        </div>

        {/* Card 5: Any Failures */}
        <div
          onClick={() => setFilterMode('only_failures')}
          style={{
            background: filterMode === 'only_failures' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'only_failures' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#e75a24' }}>
            <AlertTriangle size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              Any Failures
            </div>
            <div style={{ fontSize: '0.74rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              ({anyFailuresCount})
            </div>
          </div>
        </div>

        {/* Card 6: Deep Steps */}
        <div
          onClick={() => setFilterMode('deep_agent')}
          style={{
            background: filterMode === 'deep_agent' ? '#f0dfce' : '#f5ebe1',
            border: filterMode === 'deep_agent' ? '2px solid #e75a24' : '1px solid #dac7b2',
            borderRadius: '6px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ color: '#141414' }}>
            <Menu size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.84rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
              Deep Steps
            </div>
            <div style={{ fontSize: '0.7rem', fontFamily: 'Space Mono', color: '#857c72' }}>
              (≥4 hops) ({deepStepsCount})
            </div>
          </div>
        </div>
      </div>

      {/* 3. Subheader: Count and Sort Dropdowns */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '2px 4px',
        }}
      >
        <span style={{ fontSize: '0.86rem', fontFamily: 'Space Grotesk', color: '#141414' }}>
          Showing <strong>{sortedQuestions.length}</strong> questions
        </span>
        <ArrowUpDown size={15} style={{ color: '#857c72' }} />

        {/* Sort Dropdown */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: '#f5ebe1',
            border: '1px solid #dac7b2',
            borderRadius: '4px',
            padding: '5px 10px',
          }}
        >
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '0.78rem',
              fontFamily: 'Space Grotesk',
              fontWeight: 700,
              color: '#141414',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="qid">Sort by QID</option>
            <option value="tokens">Sort by Agent Tokens</option>
            <option value="latency">Sort by Agent Latency</option>
            <option value="steps">Sort by Agent Steps</option>
          </select>
        </div>

        {/* ASC / DESC Toggle Button */}
        <button
          onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}
          style={{
            background: '#f5ebe1',
            border: '1px solid #dac7b2',
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '0.78rem',
            fontFamily: 'Space Mono',
            fontWeight: 800,
            color: '#141414',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
          }}
        >
          {sortOrder === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
          <span>{sortOrder.toUpperCase()}</span>
        </button>
      </div>

      {/* 4. Question Cards List (Exactly Matching Reference Image) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {sortedQuestions.map((q) => {
          const goldText = Array.isArray(q.gold_answer) ? q.gold_answer.join(', ') : q.gold_answer;
          const { barColor, icon } = getTypeStyling(q.query_type);

          return (
            <div
              key={q.question_id}
              onClick={() => onSelectQuestion(q)}
              style={{
                background: '#f5ebe1',
                border: '1px solid #dac7b2',
                borderLeft: `5px solid ${barColor}`,
                borderRadius: '6px',
                padding: '16px 20px',
                display: 'grid',
                gridTemplateColumns: '130px 1fr auto auto',
                alignItems: 'center',
                gap: '24px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {/* Col 1: Icon + QID + Query Type */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <div style={{ marginBottom: '2px' }}>
                  {icon}
                </div>
                <div style={{ fontSize: '0.94rem', fontWeight: 800, fontFamily: 'Space Grotesk', color: '#141414' }}>
                  {q.question_id}
                </div>
                <div style={{ fontSize: '0.68rem', fontFamily: 'Space Mono', fontWeight: 700, color: '#857c72', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {q.query_type.replace('_', '-')}
                </div>
              </div>

              {/* Col 2: Question text & Gold Answer with Trophy */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ fontSize: '0.94rem', fontWeight: 700, fontFamily: 'Space Grotesk', color: '#141414', lineHeight: 1.35 }}>
                  {q.question}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.84rem', fontFamily: 'Space Grotesk' }}>
                  <span style={{ fontSize: '0.9rem' }}>🏆</span>
                  <span style={{ color: '#0284c7', fontWeight: 700 }}>
                    Gold: {goldText}
                  </span>
                </div>
              </div>

              {/* Col 3: Three Pipeline Status Badges (RAG, GRAPH, AGENT) */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {/* RAG Status */}
                <div
                  style={{
                    background: q.rag.correct ? '#e9f5ec' : '#fce8e8',
                    border: `1px solid ${q.rag.correct ? '#86efac' : '#fca5a5'}`,
                    color: q.rag.correct ? '#15803d' : '#b91c1c',
                    borderRadius: '4px',
                    padding: '6px 14px',
                    fontSize: '0.78rem',
                    fontFamily: 'Space Mono',
                    fontWeight: 800,
                    letterSpacing: '0.04em',
                  }}
                >
                  RAG {q.rag.correct ? '✓' : '✗'}
                </div>

                {/* GraphRAG Status */}
                <div
                  style={{
                    background: q.graphrag.correct ? '#e9f5ec' : '#fce8e8',
                    border: `1px solid ${q.graphrag.correct ? '#86efac' : '#fca5a5'}`,
                    color: q.graphrag.correct ? '#15803d' : '#b91c1c',
                    borderRadius: '4px',
                    padding: '6px 14px',
                    fontSize: '0.78rem',
                    fontFamily: 'Space Mono',
                    fontWeight: 800,
                    letterSpacing: '0.04em',
                  }}
                >
                  GRAPH {q.graphrag.correct ? '✓' : '✗'}
                </div>

                {/* Agentic Status */}
                <div
                  style={{
                    background: q.agent.correct ? '#ffedd5' : '#fce8e8',
                    border: `1px solid ${q.agent.correct ? '#fdba74' : '#fca5a5'}`,
                    color: q.agent.correct ? '#e75a24' : '#b91c1c',
                    borderRadius: '4px',
                    padding: '6px 14px',
                    fontSize: '0.78rem',
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
                    padding: '8px 16px',
                    fontSize: '0.8rem',
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
                  <Eye size={15} />
                  <span>Inspect</span>
                  <span>→</span>
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
