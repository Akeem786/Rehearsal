import React, { useState } from 'react'
import {
  CheckCircle2,
  HelpCircle,
  Play,
  Volume2,
  VolumeX,
  XCircle,
} from 'lucide-react'
import { api } from '../services/api'
import type { CaseEvaluationResult, EvaluateResponse } from '../types'

export const EvaluationRunnerPage: React.FC = () => {
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [liveExecution, setLiveExecution] = useState(true)
  const [executedWithLive, setExecutedWithLive] = useState<boolean | null>(null)
  const [result, setResult] = useState<EvaluateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeSpeechText, setActiveSpeechText] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<'all' | 'pass' | 'fail'>('all')

  const handleRunEvaluation = async () => {
    setIsLoading(true)
    setError(null)
    const runWasLive = liveExecution
    try {
      const domParam = selectedDomain === 'all' ? null : selectedDomain
      const res = await api.runEvaluation(domParam, runWasLive)
      setResult(res)
      setExecutedWithLive(runWasLive)
    } catch (err: any) {
      setError(err?.message || 'Failed to execute evaluation suite.')
      setResult(null)
      setExecutedWithLive(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSpeak = (text: string) => {
    if (!('speechSynthesis' in window)) {
      alert('Web Speech API is not supported in this browser.')
      return
    }

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel()
      if (activeSpeechText === text) {
        setActiveSpeechText(null)
        return
      }
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.0
    utterance.onend = () => setActiveSpeechText(null)
    utterance.onerror = () => setActiveSpeechText(null)

    setActiveSpeechText(text)
    window.speechSynthesis.speak(utterance)
  }

  const filteredCases: CaseEvaluationResult[] = result?.case_results.filter((c: CaseEvaluationResult) => {
    if (statusFilter === 'pass' && !c.tool_match) return false
    if (statusFilter === 'fail' && c.tool_match) return false
    return true
  }) || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* 1. Top Workbench Controls */}
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
              Voice Utterance Evaluation Runner
            </h2>
            <span className="badge badge-domain">18 Deterministic Fixtures</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.785rem' }}>
            Tests tool mapping, slot extraction from casual speech, and estimates spoken ear fatigue.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          {/* Live Execution Toggle */}
          <label
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              fontSize: '0.785rem',
              color: 'var(--text-secondary)',
              backgroundColor: 'var(--bg-surface-elevated)',
              padding: '0.35rem 0.65rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              cursor: 'pointer',
            }}
          >
            <input
              type="checkbox"
              checked={liveExecution}
              onChange={(e) => setLiveExecution(e.target.checked)}
              style={{ accentColor: 'var(--accent-primary)', cursor: 'pointer' }}
            />
            <span>Live MCP Execution</span>
          </label>

          {/* Domain Selector */}
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
                backgroundColor: selectedDomain === 'all' ? 'var(--accent-primary)' : 'transparent',
                color: selectedDomain === 'all' ? '#fff' : 'var(--text-secondary)',
                fontWeight: selectedDomain === 'all' ? 600 : 400,
              }}
              onClick={() => setSelectedDomain('all')}
            >
              All (18)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: selectedDomain === 'weather' ? 'var(--accent-primary)' : 'transparent',
                color: selectedDomain === 'weather' ? '#fff' : 'var(--text-secondary)',
                fontWeight: selectedDomain === 'weather' ? 600 : 400,
              }}
              onClick={() => setSelectedDomain('weather')}
            >
              Weather (6)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: selectedDomain === 'smart_home' ? 'var(--accent-primary)' : 'transparent',
                color: selectedDomain === 'smart_home' ? '#fff' : 'var(--text-secondary)',
                fontWeight: selectedDomain === 'smart_home' ? 600 : 400,
              }}
              onClick={() => setSelectedDomain('smart_home')}
            >
              Smart Home (6)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: selectedDomain === 'travel' ? 'var(--accent-primary)' : 'transparent',
                color: selectedDomain === 'travel' ? '#fff' : 'var(--text-secondary)',
                fontWeight: selectedDomain === 'travel' ? 600 : 400,
              }}
              onClick={() => setSelectedDomain('travel')}
            >
              Travel (6)
            </button>
          </div>

          <button
            className="btn btn-primary"
            disabled={isLoading}
            onClick={handleRunEvaluation}
          >
            {isLoading ? <span className="spinner" /> : <Play size={13} />}
            <span>{isLoading ? 'Executing Test Suite...' : 'Run Test Suite'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="panel" style={{ borderColor: 'var(--status-flawed-border)' }}>
          <div style={{ color: 'var(--status-flawed-text)', fontWeight: 600, fontSize: '0.85rem' }}>Execution Failed</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.785rem', marginTop: '2px' }}>{error}</div>
        </div>
      )}

      {/* 2. Results Summary Strip (Appears when executed) */}
      {result && (
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.75rem', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Tool Match Accuracy
              </div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)' }}>
                {(result.tool_selection_accuracy * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {result.correct_tool_selections} of {result.total_cases} matches
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Exact Argument Match
              </div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)' }}>
                {(result.exact_argument_match_rate * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {result.exact_argument_matches} of {result.total_cases} cases
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Slot Extraction F1
              </div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#818cf8', fontFamily: 'var(--font-mono)' }}>
                {result.slot_metrics.f1_score.toFixed(3)}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                Prec: {result.slot_metrics.precision.toFixed(2)} | Rec: {result.slot_metrics.recall.toFixed(2)}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Est. Speech Duration
              </div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                {result.average_estimated_speech_duration_seconds.toFixed(1)}s
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                ~{Math.round(result.average_estimated_speech_duration_seconds * 2.5)} words spoken
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <span className="badge badge-domain">Run: {result.run_id}</span>
            {executedWithLive !== null && (
              <span className={`badge ${executedWithLive ? 'badge-corrected' : 'badge-domain'}`}>
                {executedWithLive ? 'Live MCP Connected' : 'Simulated Matcher'}
              </span>
            )}
          </div>
        </div>
      )}

      {/* 3. Per-Case Test Results Table */}
      <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '0.6rem 0.85rem', borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-surface-elevated)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Utterance Test Case Results ({result ? `${filteredCases.length} of ${result.total_cases} Cases` : '18 Fixtures Ready'})
          </div>

          {result && (
            <div style={{ display: 'flex', gap: '0.35rem' }}>
              <button
                className="btn btn-ghost"
                style={{ padding: '2px 6px', fontSize: '0.7rem', backgroundColor: statusFilter === 'all' ? 'var(--bg-surface-active)' : 'transparent' }}
                onClick={() => setStatusFilter('all')}
              >
                All ({result.total_cases})
              </button>
              <button
                className="btn btn-ghost"
                style={{ padding: '2px 6px', fontSize: '0.7rem', backgroundColor: statusFilter === 'pass' ? 'var(--status-corrected-bg)' : 'transparent', color: 'var(--status-corrected-text)' }}
                onClick={() => setStatusFilter('pass')}
              >
                Passed ({result.correct_tool_selections})
              </button>
            </div>
          )}
        </div>

        {!result ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <Play size={24} color="var(--text-dim)" style={{ margin: '0 auto 0.5rem' }} />
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>Evaluation Suite Ready</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px', maxWidth: 400, margin: '2px auto 0' }}>
              Click "Run Test Suite" to evaluate natural spoken utterances against reference MCP tools.
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 80 }}>Result</th>
                  <th style={{ width: 280 }}>Spoken Utterance</th>
                  <th style={{ width: 220 }}>Mapped MCP Tool</th>
                  <th>Extracted Slots & Live Response</th>
                  <th style={{ width: 110, textAlign: 'right' }}>Audio TTS</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.map((c) => {
                  const isSpeaking = activeSpeechText === c.tool_output
                  return (
                    <tr key={c.case_id}>
                      <td>
                        <span className={`badge ${c.tool_match ? 'badge-corrected' : 'badge-flawed'}`}>
                          {c.tool_match ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
                          {c.tool_match ? 'PASS' : 'FAIL'}
                        </span>
                      </td>

                      <td>
                        <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.785rem' }}>
                          "{c.utterance}"
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          Case ID: <code>{c.case_id}</code> • Domain: {c.domain}
                        </div>
                      </td>

                      <td>
                        <code style={{ fontSize: '0.785rem', color: c.tool_match ? 'var(--status-corrected-text)' : 'var(--status-flawed-text)', fontWeight: 600 }}>
                          {c.predicted_tool || '(Abstained)'}
                        </code>
                        {!c.tool_match && (
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                            Expected: <code>{c.expected_tool || '(None)'}</code>
                          </div>
                        )}
                      </td>

                      <td>
                        {/* Slots */}
                        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
                          {c.matched_slots.map((s) => (
                            <span key={s} className="badge badge-corrected" style={{ fontSize: '0.65rem' }}>
                              {s}
                            </span>
                          ))}
                          {c.missing_slots.map((s) => (
                            <span key={s} className="badge badge-flawed" style={{ fontSize: '0.65rem' }}>
                              missing: {s}
                            </span>
                          ))}
                          {c.matched_slots.length === 0 && c.missing_slots.length === 0 && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>No slots required</span>
                          )}
                        </div>

                        {/* Live output preview */}
                        {c.tool_output && (
                          <div style={{ fontSize: '0.73rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', backgroundColor: 'var(--bg-code)', padding: '2px 6px', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)', maxWidth: 450, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {c.tool_output}
                          </div>
                        )}
                      </td>

                      <td style={{ textAlign: 'right' }}>
                        {c.tool_output ? (
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '2px 6px', fontSize: '0.72rem' }}
                            onClick={() => handleSpeak(c.tool_output!)}
                            title="Test text-to-speech rendering in browser"
                          >
                            {isSpeaking ? (
                              <>
                                <div className="speech-pulse">
                                  <span />
                                  <span />
                                  <span />
                                  <span />
                                </div>
                                <VolumeX size={11} color="var(--status-flawed-text)" />
                              </>
                            ) : (
                              <>
                                <Volume2 size={11} color="var(--accent-cyan)" />
                                <span>Listen</span>
                              </>
                            )}
                          </button>
                        ) : (
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>—</span>
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

      {/* 4. Fixture Disclaimer */}
      <div className="disclaimer-strip">
        <HelpCircle size={14} color="var(--accent-primary)" style={{ flexShrink: 0 }} />
        <span>
          <strong>Deterministic Ground Truth:</strong> 18 natural utterance fixtures benchmark intent matching and slot extraction without non-deterministic LLM variance. Speech duration is calculated at 150 WPM conversational speed.
        </span>
      </div>
    </div>
  )
}
