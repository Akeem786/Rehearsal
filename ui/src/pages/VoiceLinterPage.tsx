import React, { useEffect, useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Play,
} from 'lucide-react'
import { api } from '../services/api'
import type { LinterFinding, LintResponse } from '../types'

export const VoiceLinterPage: React.FC = () => {
  const [lintData, setLintData] = useState<LintResponse | null>(null)
  const [targetGroup, setTargetGroup] = useState<'all' | 'flawed' | 'corrected'>('all')
  const [severityFilter, setSeverityFilter] = useState<'all' | 'error' | 'warning'>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runLinter = async (group: 'all' | 'flawed' | 'corrected' = targetGroup) => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await api.runLinter(group)
      setLintData(res)
    } catch (err: any) {
      setError(err?.message || 'Failed to execute voice-readiness linter.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    runLinter('all')
  }, [])

  const handleGroupSelect = (group: 'all' | 'flawed' | 'corrected') => {
    setTargetGroup(group)
    runLinter(group)
  }

  const getScoreGrade = (score: number) => {
    if (score >= 95) return { grade: 'A+', color: 'var(--status-corrected-text)', label: 'Voice-Optimized' }
    if (score >= 85) return { grade: 'B', color: '#60a5fa', label: 'Voice-Friendly' }
    if (score >= 70) return { grade: 'C', color: 'var(--status-warning-text)', label: 'Moderate Friction' }
    return { grade: 'D', color: 'var(--status-flawed-text)', label: 'Severe Ear Fatigue' }
  }

  const filteredFindings = lintData?.findings.filter((f: LinterFinding) => {
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false
    return true
  }) || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* 1. Compact Control Bar & Score Strip */}
      <div
        className="panel"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          padding: '0.85rem 1.15rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.15rem' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', letterSpacing: '-0.02em' }}>
              Voice-Readiness Diagnostic Linter
            </h2>
            <span className="badge badge-domain">5 Heuristic Rules</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.785rem' }}>
            Analyzes tool definitions for schema depth, required argument overruns, and TTS hostility patterns.
          </p>
        </div>

        {/* Group Selector & Run Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          <div
            style={{
              display: 'inline-flex',
              backgroundColor: 'var(--bg-surface-elevated)',
              padding: '2px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: targetGroup === 'all' ? 'var(--accent-primary)' : 'transparent',
                color: targetGroup === 'all' ? '#fff' : 'var(--text-secondary)',
                fontWeight: targetGroup === 'all' ? 600 : 400,
              }}
              onClick={() => handleGroupSelect('all')}
            >
              All Tools (6)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: targetGroup === 'flawed' ? 'var(--status-flawed-bg)' : 'transparent',
                color: targetGroup === 'flawed' ? 'var(--status-flawed-text)' : 'var(--text-secondary)',
                fontWeight: targetGroup === 'flawed' ? 600 : 400,
              }}
              onClick={() => handleGroupSelect('flawed')}
            >
              Flawed Only (3)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: targetGroup === 'corrected' ? 'var(--status-corrected-bg)' : 'transparent',
                color: targetGroup === 'corrected' ? 'var(--status-corrected-text)' : 'var(--text-secondary)',
                fontWeight: targetGroup === 'corrected' ? 600 : 400,
              }}
              onClick={() => handleGroupSelect('corrected')}
            >
              Voice-First Only (3)
            </button>
          </div>

          <button
            className="btn btn-primary"
            disabled={isLoading}
            onClick={() => runLinter()}
          >
            {isLoading ? <span className="spinner" /> : <Play size={13} />}
            <span>{isLoading ? 'Scanning Schemas...' : 'Run Linter'}</span>
          </button>
        </div>
      </div>

      {/* 2. Compact Score & Severity Overview */}
      {lintData && (
        <div
          className="panel"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            padding: '0.75rem 1.15rem',
            backgroundColor: 'var(--bg-surface-elevated)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            {/* Overall Score */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div
                style={{
                  width: 38,
                  height: 38,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(255, 255, 255, 0.04)',
                  border: `1px solid ${getScoreGrade(lintData.overall_score).color}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  color: getScoreGrade(lintData.overall_score).color,
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {getScoreGrade(lintData.overall_score).grade}
              </div>

              <div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Aggregate Score
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.25rem' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: getScoreGrade(lintData.overall_score).color, fontFamily: 'var(--font-mono)' }}>
                    {lintData.overall_score}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 100</span>
                  <span style={{ fontSize: '0.72rem', color: getScoreGrade(lintData.overall_score).color, marginLeft: '0.35rem' }}>
                    ({getScoreGrade(lintData.overall_score).label})
                  </span>
                </div>
              </div>
            </div>

            {/* Severity Counters & Filter Chips */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <button
                className="btn btn-ghost"
                style={{
                  padding: '3px 8px',
                  fontSize: '0.75rem',
                  backgroundColor: severityFilter === 'all' ? 'var(--bg-surface-active)' : 'transparent',
                  color: severityFilter === 'all' ? '#fff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-subtle)',
                }}
                onClick={() => setSeverityFilter('all')}
              >
                All Findings ({lintData.findings.length})
              </button>

              <button
                className="btn btn-ghost"
                style={{
                  padding: '3px 8px',
                  fontSize: '0.75rem',
                  backgroundColor: severityFilter === 'error' ? 'var(--status-flawed-bg)' : 'transparent',
                  color: 'var(--status-flawed-text)',
                  border: '1px solid var(--status-flawed-border)',
                }}
                onClick={() => setSeverityFilter('error')}
              >
                <AlertCircle size={12} /> {lintData.error_count} Errors
              </button>

              <button
                className="btn btn-ghost"
                style={{
                  padding: '3px 8px',
                  fontSize: '0.75rem',
                  backgroundColor: severityFilter === 'warning' ? 'var(--status-warning-bg)' : 'transparent',
                  color: 'var(--status-warning-text)',
                  border: '1px solid var(--status-warning-border)',
                }}
                onClick={() => setSeverityFilter('warning')}
              >
                <AlertTriangle size={12} /> {lintData.warning_count} Warnings
              </button>
            </div>
          </div>

          <div style={{ fontSize: '0.73rem', color: 'var(--text-muted)' }}>
            <strong>{lintData.total_tools_analyzed}</strong> tools scanned • Deductions: -25/error, -10/warning
          </div>
        </div>
      )}

      {error && (
        <div className="panel" style={{ borderColor: 'var(--status-flawed-border)' }}>
          <div style={{ color: 'var(--status-flawed-text)', fontWeight: 600 }}>Linting Execution Failed</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.785rem', marginTop: '2px' }}>{error}</div>
        </div>
      )}

      {/* 3. Focused Diagnostics List (Workbench Table) */}
      <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '0.6rem 0.85rem', borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-surface-elevated)', fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Diagnostic Findings Console ({filteredFindings.length} Items)
        </div>

        {filteredFindings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <CheckCircle2 size={24} color="var(--status-corrected-text)" style={{ margin: '0 auto 0.5rem' }} />
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>No Active Lint Findings</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              All scanned tool schemas comply with selected voice-readiness heuristic rules.
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 90 }}>Severity</th>
                  <th style={{ width: 110 }}>Rule Code</th>
                  <th style={{ width: 220 }}>Target Tool</th>
                  <th>Diagnostic Issue & Remediation</th>
                </tr>
              </thead>
              <tbody>
                {filteredFindings.map((finding, idx) => {
                  const isError = finding.severity === 'error'
                  return (
                    <tr key={idx}>
                      <td>
                        <span className={`badge ${isError ? 'badge-flawed' : 'badge-warning'}`} style={{ fontSize: '0.65rem' }}>
                          {isError ? <AlertCircle size={10} /> : <AlertTriangle size={10} />}
                          {finding.severity.toUpperCase()}
                        </span>
                      </td>

                      <td>
                        <code style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
                          {finding.rule_id}
                        </code>
                      </td>

                      <td>
                        <code style={{ fontSize: '0.785rem', color: '#fff', fontWeight: 600 }}>
                          {finding.tool_name}
                        </code>
                      </td>

                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.785rem', marginBottom: '0.2rem' }}>
                          {finding.title}
                        </div>

                        {finding.evidence && (
                          <div style={{ marginBottom: '0.25rem' }}>
                            <code style={{ fontSize: '0.72rem', backgroundColor: 'var(--bg-code)', padding: '2px 6px', borderRadius: 'var(--radius-xs)', color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}>
                              Evidence: {finding.evidence}
                            </code>
                          </div>
                        )}

                        {finding.recommendation && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.73rem', color: 'var(--status-corrected-text)' }}>
                            <Lightbulb size={11} style={{ flexShrink: 0 }} />
                            <span>Remediation: {finding.recommendation}</span>
                          </div>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 4. Scanned Tools Compliance Checklist */}
      {lintData && lintData.tool_scores && Object.keys(lintData.tool_scores).length > 0 && (
        <div className="panel" style={{ padding: '0.85rem 1.15rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#fff', marginBottom: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Tool-Level Heuristic Scorecard
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.65rem' }}>
            {Object.entries(lintData.tool_scores).map(([name, score]) => {
              const grade = getScoreGrade(score)
              return (
                <div
                  key={name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.45rem 0.65rem',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <code style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>{name}</code>
                  <span style={{ fontSize: '0.785rem', fontWeight: 700, color: grade.color, fontFamily: 'var(--font-mono)' }}>
                    {score}/100
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
