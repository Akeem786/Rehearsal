import React, { useEffect, useState } from 'react'
import {
  Activity,
  ArrowRight,
  Check,
  Clock,
  Compass,
  Copy,
  Gauge,
  HelpCircle,
  Home,
  Play,
  RotateCcw,
  ShieldAlert,
  Terminal,
  Volume2,
} from 'lucide-react'
import { api } from '../services/api'
import type { CompareResponse, RunSummary, ToolComparisonItem, ToolsListResponse } from '../types'

interface OverviewPageProps {
  onNavigate: (tab: string) => void
}

interface DomainConfig {
  title: string
  focusTag: string
  icon: React.ReactNode
  flawedDisplay: string
  flawedTag: string
  correctedDisplay: string
  correctedTag: string
}

const DOMAIN_CONFIGS: Record<string, DomainConfig> = {
  weather: {
    title: 'Weather Services',
    focusTag: 'Schema Flattening & Payload Reduction',
    icon: <Gauge size={14} color="var(--accent-primary)" />,
    flawedDisplay: 'fetch_meteorological_telemetry',
    flawedTag: 'Depth 3 ($defs)',
    correctedDisplay: 'get_weather_summary',
    correctedTag: 'Flat String (Depth 1)',
  },
  smart_home: {
    title: 'Smart Home IoT',
    focusTag: 'Intent & Entity Resolution',
    icon: <Home size={14} color="var(--status-corrected-text)" />,
    flawedDisplay: 'execute_home_iot_command',
    flawedTag: 'Hex GUID Register (0x4A9F)',
    correctedDisplay: 'control_home_device',
    correctedTag: 'Natural Room Target',
  },
  travel: {
    title: 'Flight & Travel Booking',
    focusTag: 'Ear-Fatigue Mitigation',
    icon: <Compass size={14} color="#38bdf8" />,
    flawedDisplay: 'query_itinerary_matrix',
    flawedTag: 'IATA Codes & 200w GDS Matrix',
    correctedDisplay: 'find_flight_summary',
    correctedTag: '2 Spoken Choices + CTA',
  },
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  const [toolsData, setToolsData] = useState<ToolsListResponse | null>(null)
  const [compareData, setCompareData] = useState<CompareResponse | null>(null)
  const [recentRuns, setRecentRuns] = useState<RunSummary[]>([])
  const [selectedDomain, setSelectedDomain] = useState<string>('weather')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [, t, c, r] = await Promise.all([
        api.getHealth(),
        api.getTools(),
        api.getComparison(),
        api.getRuns(5, 0),
      ])
      setToolsData(t)
      setCompareData(c)
      setRecentRuns(r.runs)
      if (c && c.comparisons.length > 0 && !selectedDomain) {
        setSelectedDomain(c.comparisons[0].domain)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to connect to Rehearsal backend.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleCopyRunId = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    navigator.clipboard.writeText(id)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  if (isLoading) {
    return (
      <div style={{ padding: '3.5rem 0', textAlign: 'center' }}>
        <div className="spinner" style={{ width: 22, height: 22, margin: '0 auto 0.75rem' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
          Initializing MCP Testing Workbench...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel" style={{ borderColor: 'var(--status-flawed-border)', padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
          <ShieldAlert size={20} color="var(--status-flawed-text)" style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ color: 'var(--status-flawed-text)', fontWeight: 600, fontSize: '0.9rem' }}>
              Workbench Connection Offline
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', margin: '0.35rem 0 0.85rem' }}>
              {error}
            </div>
            <button className="btn btn-secondary" onClick={fetchData} style={{ fontSize: '0.785rem' }}>
              <RotateCcw size={13} /> Retry Connection
            </button>
          </div>
        </div>
      </div>
    )
  }

  const flawedScore = Math.round(compareData?.flawed_average_score ?? 60)
  const correctedScore = Math.round(compareData?.corrected_average_score ?? 100)
  const scoreImprovement = Math.round(compareData?.score_improvement ?? (correctedScore - flawedScore))

  const activeComparisonItem =
    compareData?.comparisons.find((c) => c.domain === selectedDomain) ||
    compareData?.comparisons[0]

  const activeCfg = activeComparisonItem
    ? DOMAIN_CONFIGS[activeComparisonItem.domain] || {
        title: activeComparisonItem.domain.replace('_', ' ').toUpperCase(),
        focusTag: 'Acoustic Ergonomics',
        icon: <Volume2 size={14} />,
        flawedDisplay: activeComparisonItem.flawed_tool_name,
        flawedTag: 'Anti-Pattern',
        correctedDisplay: activeComparisonItem.corrected_tool_name,
        correctedTag: 'Voice-First',
      }
    : null

  const activeDelta = activeComparisonItem
    ? activeComparisonItem.corrected_score - activeComparisonItem.flawed_score
    : 0

  return (
    <div className="overview-workspace">
      {/* 1. Compact Workspace Header */}
      <div className="workspace-header">
        <div className="workspace-header-main">
          <h1 className="workspace-title">MCP Voice Testing Workbench</h1>
          <p className="workspace-subtitle">
            Diagnostic environment for evaluating Model Context Protocol tool schemas against acoustic ergonomics heuristics and natural spoken turn-taking.
          </p>
        </div>

        <div className="workspace-header-actions">
          {/* Live Benchmark Summary Pill */}
          <div className="workspace-benchmark-pill" title="Actual scores from /api/compare endpoint">
            <span className="tag">Benchmark</span>
            <span className="flawed">{flawedScore}</span>
            <span className="arrow">➔</span>
            <span className="corrected">{correctedScore}</span>
            <span className="lift">+{scoreImprovement} pts</span>
          </div>

          <button className="btn btn-primary" onClick={() => onNavigate('runner')}>
            <Play size={13} /> Run Evaluation
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('linter')}>
            <Activity size={13} /> Open Linter
          </button>
        </div>
      </div>

      {/* 2. Benchmark Workspace: Balanced Responsive Comparison Grid with Interactive Selection */}
      <div className="benchmark-console">
        <div className="benchmark-console-header">
          <div className="benchmark-console-title">
            <Terminal size={14} color="var(--accent-primary)" />
            <span>Acoustic Usability Benchmark</span>
          </div>
          <div className="benchmark-console-meta">
            Interactive benchmark grid • Select a domain to inspect telemetry & schema specifications
          </div>
        </div>

        {/* 3-Column Responsive Grid */}
        <div className="domain-workbench-grid">
          {compareData?.comparisons.map((item: ToolComparisonItem) => {
            const isSelected = (selectedDomain || 'weather') === item.domain
            const delta = item.corrected_score - item.flawed_score
            const cfg = DOMAIN_CONFIGS[item.domain] || {
              title: item.domain.replace('_', ' ').toUpperCase(),
              focusTag: 'Acoustic Ergonomics',
              icon: <Volume2 size={14} />,
              flawedDisplay: item.flawed_tool_name,
              flawedTag: 'Anti-Pattern',
              correctedDisplay: item.corrected_tool_name,
              correctedTag: 'Voice-First',
            }

            return (
              <div
                key={item.domain}
                className={`domain-module-card ${isSelected ? 'selected' : ''}`}
                onClick={() => setSelectedDomain(item.domain)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    setSelectedDomain(item.domain)
                  }
                }}
                title={`Click to inspect ${cfg.title} architecture`}
              >
                {/* Header: Domain Title & Focus Tag */}
                <div className="domain-card-header">
                  <div className="domain-card-title">
                    {cfg.icon}
                    <span className="domain-card-name">{cfg.title}</span>
                  </div>
                  {isSelected ? (
                    <span className="domain-active-tag">INSPECTING</span>
                  ) : (
                    <span className="domain-select-tag">SELECT</span>
                  )}
                </div>

                <div className="domain-card-focus">{cfg.focusTag}</div>

                {/* Staggered 2-Row Tool Pair (Not crowded into 1 line) */}
                <div className="domain-card-tool-pair">
                  <div className="card-tool-row flawed">
                    <div className="card-tool-label">
                      <span className="role-tag flawed">Flawed</span>
                      <code
                        className="card-tool-name"
                        title={`Full Identifier: ${item.flawed_tool_name}\nDepth: ${item.flawed_nesting_depth}`}
                      >
                        {cfg.flawedDisplay}
                      </code>
                    </div>
                    <span className="card-tool-metric flawed" title={`Flawed Baseline: ${item.flawed_score}/100`}>
                      {item.flawed_score}
                    </span>
                  </div>

                  <div className="card-tool-row corrected">
                    <div className="card-tool-label">
                      <span className="role-tag corrected">Voice-First</span>
                      <code
                        className="card-tool-name"
                        title={`Full Identifier: ${item.corrected_tool_name}\nDepth: ${item.corrected_nesting_depth}`}
                      >
                        {cfg.correctedDisplay}
                      </code>
                    </div>
                    <span className="card-tool-metric corrected" title={`Voice-First Ceiling: ${item.corrected_score}/100`}>
                      {item.corrected_score}
                    </span>
                  </div>
                </div>

                {/* Segmented 0-100 Score Scale: Neutral Baseline + Vibrant Lift */}
                <div className="segmented-score-scale">
                  <div className="score-scale-metrics">
                    <div className="metric-col">
                      <span className="metric-label">Baseline</span>
                      <span className="metric-val flawed">{item.flawed_score}</span>
                    </div>
                    <div className="metric-col lift">
                      <span className="metric-label">Ergonomic Lift</span>
                      <span className="metric-val lift">+{delta} pts</span>
                    </div>
                    <div className="metric-col">
                      <span className="metric-label">Optimized</span>
                      <span className="metric-val corrected">{item.corrected_score}</span>
                    </div>
                  </div>

                  <div
                    className="score-scale-track"
                    role="progressbar"
                    aria-valuenow={item.corrected_score}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${cfg.title} score scale: baseline ${item.flawed_score}, lift +${delta} points to ${item.corrected_score}`}
                  >
                    {/* Neutral/restrained baseline segment up to flawed_score */}
                    <div
                      className="score-scale-segment baseline"
                      style={{ width: `${item.flawed_score}%` }}
                      title={`Baseline Score: ${item.flawed_score}/100`}
                    />
                    {/* Distinct ergonomic lift segment from flawed_score to corrected_score */}
                    <div
                      className="score-scale-segment lift"
                      style={{ left: `${item.flawed_score}%`, width: `${delta}%` }}
                      title={`Ergonomic Improvement Lift: +${delta} points`}
                    />
                    {/* Baseline score marker pin */}
                    <div
                      className="score-scale-marker"
                      style={{ left: `${item.flawed_score}%` }}
                      title={`Baseline Marker: ${item.flawed_score}`}
                    />
                  </div>

                  {/* Accessible textual caption */}
                  <div className="score-scale-caption">
                    Baseline: {item.flawed_score}/100 • Lift: +{delta} pts • Optimized: {item.corrected_score}/100
                  </div>
                </div>

                {/* Compact Architectural Note */}
                <div className="domain-card-summary">
                  {item.voice_differences && item.voice_differences.length > 0
                    ? item.voice_differences[0]
                    : 'Flat conversational schema replaces multi-parameter friction.'}
                </div>
              </div>
            )
          })}
        </div>

        {/* Selected Domain Detail Inspector Pane (Clean Interactive Detail) */}
        {activeComparisonItem && activeCfg && (
          <div className="domain-inspector-pane">
            <div className="domain-inspector-header">
              <div className="inspector-header-info">
                <span className="inspector-kicker">Active Inspector Telemetry</span>
                <div className="inspector-title">
                  {activeCfg.icon}
                  <span>{activeCfg.title}</span>
                  <span className="badge badge-domain">+{activeDelta} pts lift</span>
                </div>
              </div>

              <div className="inspector-actions">
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  onClick={() => onNavigate('compare')}
                >
                  Compare Deep-Dive <ArrowRight size={11} />
                </button>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  onClick={() => onNavigate('tools')}
                >
                  View Schemas <ArrowRight size={11} />
                </button>
              </div>
            </div>

            <div className="domain-inspector-body">
              {/* Left Column: Full Identifiers & Depths */}
              <div className="inspector-col">
                <div className="inspector-col-title">Full Tool Identifiers & Depths</div>

                <div className="inspector-id-card flawed">
                  <div className="id-card-top">
                    <span className="role-tag flawed">Flawed Baseline</span>
                    <span className="depth-badge">Depth {activeComparisonItem.flawed_nesting_depth}</span>
                  </div>
                  <code className="full-id-code" title={activeComparisonItem.flawed_tool_name}>
                    {activeComparisonItem.flawed_tool_name}
                  </code>
                  <div className="id-card-notes">
                    {activeComparisonItem.flawed_findings_count} heuristic lint deductions • {activeCfg.flawedTag}
                  </div>
                </div>

                <div className="inspector-id-card corrected">
                  <div className="id-card-top">
                    <span className="role-tag corrected">Voice-Optimized</span>
                    <span className="depth-badge">Depth {activeComparisonItem.corrected_nesting_depth} (Flat)</span>
                  </div>
                  <code className="full-id-code" title={activeComparisonItem.corrected_tool_name}>
                    {activeComparisonItem.corrected_tool_name}
                  </code>
                  <div className="id-card-notes">
                    0 heuristic lint deductions • {activeCfg.correctedTag}
                  </div>
                </div>
              </div>

              {/* Right Column: Architectural Transformations */}
              <div className="inspector-col">
                <div className="inspector-col-title">Architectural Transformations</div>
                <ul className="inspector-diff-list">
                  {activeComparisonItem.voice_differences && activeComparisonItem.voice_differences.length > 0 ? (
                    activeComparisonItem.voice_differences.map((diff, i) => (
                      <li key={i} className="inspector-diff-item">
                        <span className="diff-bullet" />
                        <span>{diff}</span>
                      </li>
                    ))
                  ) : (
                    <li className="inspector-diff-item">
                      <span className="diff-bullet" />
                      <span>Flat conversational schema replaces multi-parameter friction.</span>
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Compact Heuristic Standards & Rules Strip */}
        <div className="standards-strip">
          <div className="standards-strip-rules">
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Heuristic Evaluation Rules:</span>
            <span className="badge badge-domain">RULE-001 Depth ≤ 1</span>
            <span className="badge badge-domain">RULE-002 Required Args ≤ 3</span>
            <span className="badge badge-domain">RULE-003 Spoken TTS Conciseness</span>
          </div>

          <button className="standards-strip-link" onClick={() => onNavigate('linter')}>
            Inspect Complete Rules in Voice Linter <ArrowRight size={11} />
          </button>
        </div>
      </div>

      {/* 3. Supporting Workspace Dock (Secondary Visual Weight, High Technical Density) */}
      <div className="supporting-dock">
        {/* Left Pane: Reference Tool Suite */}
        <div className="dock-pane">
          <div className="dock-pane-header">
            <div>
              <h3 className="dock-pane-title">Reference Tool Suite</h3>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>6 tools registered on stdio transport</div>
            </div>
            <button className="btn btn-ghost" style={{ fontSize: '0.72rem', padding: '2px 6px' }} onClick={() => onNavigate('tools')}>
              Explore Catalog <ArrowRight size={11} />
            </button>
          </div>

          <div className="dock-pane-body">
            {toolsData?.tools.map((t) => {
              const isFlawed = t.group === 'flawed'
              const paramCount = Object.keys(t.input_schema?.properties || {}).length
              return (
                <div
                  key={t.name}
                  onClick={() => onNavigate('tools')}
                  className="dock-row-item"
                  title={`Inspect schema for ${t.name} in Tool Explorer`}
                >
                  <div className="dock-row-main">
                    <span
                      className="status-dot"
                      style={{ backgroundColor: isFlawed ? 'var(--status-flawed-text)' : 'var(--status-corrected-text)' }}
                    />
                    <code className="dock-row-code" title={t.name}>
                      {t.name}
                    </code>
                  </div>

                  <div className="dock-row-meta">
                    <span className="badge badge-domain">{t.domain}</span>
                    <span className={`badge ${isFlawed ? 'badge-flawed' : 'badge-corrected'}`}>
                      {isFlawed ? 'Flawed' : 'Voice-First'}
                    </span>
                    <span className="dock-stat-pill">
                      {paramCount} {paramCount === 1 ? 'arg' : 'args'}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Pane: Recent Evaluation Telemetry */}
        <div className="dock-pane">
          <div className="dock-pane-header">
            <div>
              <h3 className="dock-pane-title">Recent Evaluation Telemetry</h3>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Persisted in SQLite database</div>
            </div>
            <button className="btn btn-ghost" style={{ fontSize: '0.72rem', padding: '2px 6px' }} onClick={() => onNavigate('history')}>
              View Archive <ArrowRight size={11} />
            </button>
          </div>

          <div className="dock-pane-body">
            {recentRuns.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
                <Clock size={18} color="var(--text-dim)" style={{ margin: '0 auto 0.35rem' }} />
                <div style={{ fontSize: '0.785rem', fontWeight: 600, color: 'var(--text-secondary)' }}>No Evaluation Runs Logged</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: '0.2rem auto 0.5rem' }}>
                  Execute a test suite to verify tool accuracy and speech duration.
                </div>
                <button className="btn btn-primary" style={{ fontSize: '0.72rem', padding: '2px 8px' }} onClick={() => onNavigate('runner')}>
                  <Play size={10} /> Run Evaluation
                </button>
              </div>
            ) : (
              recentRuns.slice(0, 5).map((r) => {
                const isCopied = copiedId === r.run_id
                return (
                  <div
                    key={r.run_id}
                    onClick={() => onNavigate('history')}
                    className="dock-row-item"
                    title={`Inspect telemetry report for ${r.run_id} in Run History`}
                  >
                    <div className="dock-row-main">
                      <code className="dock-row-code" title={r.run_id}>
                        {r.run_id}
                      </code>
                      <button
                        className="btn-icon"
                        style={{ padding: '1px 3px', border: 'none' }}
                        onClick={(e) => handleCopyRunId(r.run_id, e)}
                        title="Copy Run ID"
                      >
                        {isCopied ? <Check size={10} color="var(--status-corrected-text)" /> : <Copy size={10} />}
                      </button>
                    </div>

                    <div className="dock-row-meta">
                      <span className="badge badge-domain">{r.domain || 'All Domains'}</span>
                      <span className="badge badge-corrected">
                        {(r.tool_accuracy * 100).toFixed(0)}% Match
                      </span>
                      <span className="dock-stat-pill">
                        {r.average_duration_seconds.toFixed(1)}s
                      </span>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>

      {/* 4. Independent Transparency Disclaimer */}
      <div className="disclaimer-strip">
        <HelpCircle size={13} color="var(--accent-primary)" style={{ flexShrink: 0 }} />
        <span>
          Independent open-source developer tool. Not affiliated with or endorsed by Amazon Alexa or Alexa+. Scores evaluate heuristic acoustic ergonomics across 18 deterministic utterance fixtures.
        </span>
      </div>
    </div>
  )
}
