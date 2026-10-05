import React from 'react';
import { Database, Download, Filter, Search } from 'lucide-react';
import { benchmarkKeys } from '../data/datasetManager';

interface HeaderProps {
  activeDatasetId: string;
  onSelectDataset: (id: string) => void;
  selectedQueryType: string;
  onSelectQueryType: (type: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onExportJson: () => void;
  onExportCsv: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeDatasetId,
  onSelectDataset,
  selectedQueryType,
  onSelectQueryType,
  searchQuery,
  onSearchChange,
  onExportJson,
  onExportCsv,
}) => {
  const queryTypes = ['all', 'aggregation', 'lookup', 'multi_hop', 'superlative', 'temporal'];

  return (
    <header
      style={{
        backgroundColor: '#ebdccb',
        borderBottom: '2px solid #dac7b2',
        padding: '12px 28px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      {/* Left: Benchmark Dataset Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span className="hex-bullet" style={{ width: '10px', height: '10px' }} />
        <span style={{ fontFamily: 'Space Mono', fontWeight: 700, fontSize: '0.74rem', color: '#141414', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          DATASET:
        </span>
        <select
          value={activeDatasetId}
          onChange={(e) => onSelectDataset(e.target.value)}
          style={{
            background: '#f5ebe1',
            color: '#141414',
            border: '1px solid #c4b09b',
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '0.8rem',
            fontFamily: 'Space Grotesk',
            fontWeight: 600,
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

      {/* Middle: Universal Search and Type Filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: '1', maxWidth: '600px' }}>
        {/* Search */}
        <div
          style={{
            position: 'relative',
            flex: 1,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Search size={14} style={{ position: 'absolute', left: '10px', color: '#857c72' }} />
          <input
            type="text"
            placeholder="Search QID, question, answer, athlete, city, year..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{
              width: '100%',
              background: '#f5ebe1',
              border: '1px solid #c4b09b',
              borderRadius: '4px',
              padding: '6px 10px 6px 32px',
              fontSize: '0.8rem',
              fontFamily: 'Space Grotesk',
              color: '#141414',
              outline: 'none',
            }}
          />
        </div>

        {/* Global Query Type Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <select
            value={selectedQueryType}
            onChange={(e) => onSelectQueryType(e.target.value)}
            style={{
              background: '#f5ebe1',
              color: '#141414',
              border: '1px solid #c4b09b',
              borderRadius: '4px',
              padding: '6px 10px',
              fontSize: '0.78rem',
              fontFamily: 'Space Mono',
              fontWeight: 700,
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

      {/* Right: Export Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          onClick={onExportJson}
          title="Export current filtered data as JSON"
          style={{
            background: '#f5ebe1',
            color: '#141414',
            border: '1px solid #c4b09b',
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '0.74rem',
            fontFamily: 'Space Mono',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
          }}
        >
          <Download size={13} style={{ color: '#e75a24' }} />
          <span>JSON</span>
        </button>
        <button
          onClick={onExportCsv}
          title="Export benchmark questions to CSV"
          style={{
            background: '#141414',
            color: '#f5ebe1',
            border: 'none',
            borderRadius: '4px',
            padding: '6px 14px',
            fontSize: '0.74rem',
            fontFamily: 'Space Mono',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
          }}
        >
          <Download size={13} style={{ color: '#e75a24' }} />
          <span>CSV</span>
        </button>
      </div>
    </header>
  );
};
