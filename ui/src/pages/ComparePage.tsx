import React, { useEffect, useState } from 'react'
import {
  ArrowRight,
  CheckCircle2,
  HelpCircle,
  RotateCcw,
  TrendingUp,
  XCircle,
} from 'lucide-react'
import { api } from '../services/api'
import type { CompareResponse } from '../types'

export const ComparePage: React.FC = () => {
  const [data, setData] = useState<CompareResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchComparison = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await api.getComparison()
      setData(res)
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch comparison scorecard.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchComparison()
  }, [])

  if (isLoading) {
    return (
      <div style={{ padding: '3rem 0', textAlign: 'center' }}>
        <div className="spinner" style={{ width: 24, height: 24, margin: '0 auto 0.75rem' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Computing comparative voice-readiness scorecard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel" style={{ borderColor: 'var(--status-flawed-border)' }}>
        <h3 style={{ color: 'var(--status-flawed-text)', marginBottom: '0.25rem', fontSize: '0.92rem', fontWeight: 600 }}>Comparison Failed</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '0.85rem', fontSize: '0.8rem' }}>{error}</p>
        <button className="btn btn-secondary" onClick={fetchComparison}>
          <RotateCcw size={13} /> Retry
        </button>
      </div>
    )
  }

  if (!data) return null

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* 1. Header & Aggregate Delta Strip (Centerpiece) */}
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
              Anti-Pattern vs. Voice-Optimized Benchmark
            </h2>
            <span className="badge badge-domain">3 Paired Domains Tested</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.785rem' }}>
            Measures the ergonomic gain when transforming visual chatbot tools into voice-first MCP specifications.
          </p>
        </div>

        {/* Aggregate Delta Counter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', backgroundColor: 'var(--bg-surface-elevated)', padding: '0.45rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
          <div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Flawed Baseline</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--status-flawed-text)', fontFamily: 'var(--font-mono)' }}>
              {data.flawed_average_score}/100
            </div>
          </div>

          <div style={{ color: 'var(--text-muted)' }}>
            <ArrowRight size={16} />
          </div>

          <div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Corrected Voice-First</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)' }}>
              {data.corrected_average_score}/100
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-subtle)', paddingLeft: '0.85rem' }}>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Net Improvement</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
              +{data.score_improvement} pts
            </div>
          </div>
        </div>
      </div>

      {/* 2. Visual Progress Lift Bar */}
      <div className="panel" style={{ padding: '0.85rem 1.15rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span>Overall Voice Ergonomics Score Lift</span>
          <span>Flawed: {data.flawed_average_score}% ➔ Corrected: {data.corrected_average_score}% (+{data.score_improvement} pts)</span>
        </div>
        <div className="score-scale-track" style={{ height: 10 }}>
          <div
            className="score-scale-segment baseline"
            style={{ width: `${data.flawed_average_score}%` }}
            title={`Flawed baseline average: ${data.flawed_average_score}/100`}
          />
          <div
            className="score-scale-segment lift"
            style={{
              left: `${data.flawed_average_score}%`,
              width: `${data.score_improvement}%`,
            }}
            title={`Ergonomic score lift: +${data.score_improvement} points`}
          />
          <div
            className="score-scale-marker"
            style={{ left: `${data.flawed_average_score}%` }}
            title={`Baseline marker: ${data.flawed_average_score}`}
          />
        </div>
      </div>

      {/* 3. Paired Domain Technical Scorecards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {data.comparisons.map((item, idx) => {
          const delta = item.corrected_score - item.flawed_score
          return (
            <div key={idx} className="panel" style={{ padding: '1rem 1.15rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.65rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                    {item.domain.replace('_', ' ').toUpperCase()} Domain
                  </span>
                  <span className="badge badge-domain">{item.flawed_tool_name} vs {item.corrected_tool_name}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--status-corrected-text)', fontWeight: 600, fontSize: '0.785rem', fontFamily: 'var(--font-mono)' }}>
                  <TrendingUp size={13} /> +{delta} pts gain
                </div>
              </div>

              {/* Side-by-side Columns */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem', marginBottom: '0.85rem' }}>
                {/* Flawed Column */}
                <div style={{ backgroundColor: 'rgba(244, 63, 94, 0.03)', border: '1px solid var(--status-flawed-border)', borderRadius: 'var(--radius-sm)', padding: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <XCircle size={14} color="var(--status-flawed-text)" />
                      <code style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--status-flawed-text)' }}>
                        {item.flawed_tool_name}
                      </code>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-flawed-text)', fontFamily: 'var(--font-mono)' }}>
                      {item.flawed_score}/100
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '0.45rem', marginBottom: '0.65rem', flexWrap: 'wrap' }}>
                    <span className="badge badge-flawed">Nesting Depth: {item.flawed_nesting_depth} ($defs)</span>
                    <span className="badge badge-flawed">{item.flawed_findings_count} Lint Deductions</span>
                  </div>
                </div>

                {/* Corrected Column */}
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.03)', border: '1px solid var(--status-corrected-border)', borderRadius: 'var(--radius-sm)', padding: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <CheckCircle2 size={14} color="var(--status-corrected-text)" />
                      <code style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--status-corrected-text)' }}>
                        {item.corrected_tool_name}
                      </code>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)' }}>
                      {item.corrected_score}/100
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '0.45rem', marginBottom: '0.65rem', flexWrap: 'wrap' }}>
                    <span className="badge badge-corrected">Nesting Depth: {item.corrected_nesting_depth} (Flat)</span>
                    <span className="badge badge-corrected">{item.corrected_findings_count} Lint Deductions</span>
                  </div>
                </div>
              </div>

              {/* Voice Differences List */}
              {item.voice_differences && item.voice_differences.length > 0 && (
                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.6rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.35rem' }}>
                    Architectural Transformations
                  </div>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    {item.voice_differences.map((diff, dIdx) => (
                      <li key={dIdx} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ width: 4, height: 4, borderRadius: '50%', backgroundColor: 'var(--accent-primary)', flexShrink: 0 }} />
                        <span>{diff}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* 4. Disclaimers */}
      <div className="disclaimer-strip">
        <HelpCircle size={14} color="var(--accent-primary)" style={{ flexShrink: 0 }} />
        <span>
          <strong>Benchmark Methodology:</strong> Heuristic scoring evaluates input schema depth, required parameter count, and TTS output safety. Scores are calculated deterministically across reference implementations.
        </span>
      </div>
    </div>
  )
}
