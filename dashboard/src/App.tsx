import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { QuestionDetailModal } from './components/QuestionDetailModal';
import { OverviewPage } from './pages/OverviewPage';
import { ExplorerPage } from './pages/ExplorerPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { QueryTypePage } from './pages/QueryTypePage';
import { AgentTracesPage } from './pages/AgentTracesPage';
import { RetrievalPage } from './pages/RetrievalPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { benchmarkDatasets } from './data/datasetManager';
import { BenchmarkQuestion, ViewTab } from './types/benchmark';

export default function App() {
  const [currentTab, setCurrentTab] = useState<ViewTab>('overview');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [activeDatasetId, setActiveDatasetId] = useState<string>('100_final');
  const [selectedQueryType, setSelectedQueryType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeQuestion, setActiveQuestion] = useState<BenchmarkQuestion | null>(null);

  const activeDataset = benchmarkDatasets[activeDatasetId] || benchmarkDatasets['100_final'];

  // Export JSON handler
  const handleExportJson = () => {
    const jsonStr = JSON.stringify(activeDataset, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentic_graphrag_benchmark_${activeDatasetId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export CSV handler
  const handleExportCsv = () => {
    const headers = ['QID', 'Type', 'Question', 'Gold Answer', 'RAG Status', 'GraphRAG Status', 'Agent Status', 'Agent Tokens', 'Agent Latency (s)', 'Agent Steps'];
    const rows = activeDataset.questions.map(q => [
      q.question_id,
      q.query_type,
      `"${q.question.replace(/"/g, '""')}"`,
      `"${(Array.isArray(q.gold_answer) ? q.gold_answer.join(', ') : q.gold_answer).replace(/"/g, '""')}"`,
      q.rag.correct ? 'PASS' : 'FAIL',
      q.graphrag.correct ? 'PASS' : 'FAIL',
      q.agent.correct ? 'PASS' : 'FAIL',
      q.agent.tokens,
      q.agent.latency || q.agent.elapsed_time_s || '',
      q.agent.total_steps || (q.agent.trace?.length || 1),
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentic_graphrag_benchmark_${activeDatasetId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-main)' }}>
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Header */}
        <Header
          activeDatasetId={activeDatasetId}
          onSelectDataset={setActiveDatasetId}
          selectedQueryType={selectedQueryType}
          onSelectQueryType={setSelectedQueryType}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onExportJson={handleExportJson}
          onExportCsv={handleExportCsv}
        />

        {/* View Pages */}
        <main style={{ padding: '24px', maxWidth: '1440px', width: '100%', margin: '0 auto', flex: 1 }}>
          {currentTab === 'overview' && (
            <OverviewPage
              dataset={activeDataset}
              onNavigateToExplorer={() => setCurrentTab('explorer')}
              onNavigateToTraces={() => setCurrentTab('agent_traces')}
            />
          )}

          {currentTab === 'explorer' && (
            <ExplorerPage
              dataset={activeDataset}
              activeDatasetId={activeDatasetId}
              onSelectDataset={setActiveDatasetId}
              selectedQueryType={selectedQueryType}
              onSelectQueryType={setSelectedQueryType}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSelectQuestion={setActiveQuestion}
            />
          )}

          {currentTab === 'comparison' && (
            <ComparisonPage dataset={activeDataset} />
          )}

          {currentTab === 'query_types' && (
            <QueryTypePage
              dataset={activeDataset}
              onSelectQuestion={setActiveQuestion}
            />
          )}

          {currentTab === 'agent_traces' && (
            <AgentTracesPage
              dataset={activeDataset}
              onSelectQuestion={setActiveQuestion}
            />
          )}

          {currentTab === 'retrieval' && (
            <RetrievalPage
              dataset={activeDataset}
              onSelectQuestion={setActiveQuestion}
            />
          )}

          {currentTab === 'methodology' && (
            <MethodologyPage />
          )}
        </main>
      </div>

      {/* Modal Inspector with Play Trace */}
      <QuestionDetailModal
        question={activeQuestion}
        onClose={() => setActiveQuestion(null)}
      />
    </div>
  );
};
