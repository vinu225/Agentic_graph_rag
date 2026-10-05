import React from 'react';
import { 
  BarChart2, 
  Search, 
  GitCompare, 
  Layers, 
  Activity, 
  Database, 
  AlertTriangle, 
  BookOpen, 
  ChevronLeft, 
  ChevronRight,
  Cpu
} from 'lucide-react';
import { ViewTab } from '../types/benchmark';

interface SidebarProps {
  currentTab: ViewTab;
  onSelectTab: (tab: ViewTab) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
}) => {
  const navItems: { id: ViewTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <BarChart2 size={18} /> },
    { id: 'explorer', label: 'Benchmark Explorer', icon: <Search size={18} /> },
    { id: 'comparison', label: 'Pipeline Comparison', icon: <GitCompare size={18} /> },
    { id: 'query_types', label: 'Query Type Matrix', icon: <Layers size={18} /> },
    { id: 'agent_traces', label: 'Agent Traces & Playback', icon: <Activity size={18} /> },
    { id: 'retrieval', label: 'Retrieval Completeness', icon: <Database size={18} /> },
    { id: 'methodology', label: 'Methodology & Arch', icon: <BookOpen size={18} /> },
  ];

  return (
    <aside
      style={{
        width: isCollapsed ? '64px' : '260px',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        flexShrink: 0,
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: isCollapsed ? '16px 8px' : '22px 20px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
        }}
      >
        {!isCollapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              className="hex-bullet"
              style={{ width: '22px', height: '22px' }}
            />
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.94rem', color: '#f8fafc', letterSpacing: '-0.01em', textTransform: 'uppercase' }}>
                Agentic GraphRAG
              </div>
              <div style={{ fontSize: '0.68rem', fontFamily: 'Space Mono', color: '#e75a24', letterSpacing: '0.08em' }}>
                OBSERVATORY // TG-2026
              </div>
            </div>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '14px 10px', flex: 1, overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                title={isCollapsed ? item.label : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: isCollapsed ? '10px 0' : '10px 14px',
                  justifyContent: isCollapsed ? 'center' : 'flex-start',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: isActive ? '#1c212c' : 'transparent',
                  color: isActive ? '#f8fafc' : '#94a3b8',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.82rem',
                  fontFamily: 'Space Grotesk',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                  borderLeft: isActive && !isCollapsed ? '3px solid #e75a24' : '3px solid transparent',
                }}
              >
                <span style={{ color: isActive ? '#e75a24' : 'inherit', display: 'flex' }}>
                  {item.icon}
                </span>
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer Info */}
      {!isCollapsed && (
        <div
          style={{
            padding: '16px 20px',
            borderTop: '1px solid var(--border-subtle)',
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            lineHeight: 1.4,
          }}
        >
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
            TigerGraph Evaluation
          </div>
          <div>Olympic Games Knowledge Base</div>
          <div>Model: Qwen3:8B (Local Ollama)</div>
        </div>
      )}
    </aside>
  );
};
