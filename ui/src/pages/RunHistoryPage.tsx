import React, { useEffect, useState } from 'react'
import {
  Check,
  Clock,
  Copy,
  Download,
  Eye,
  RotateCcw,
  X,
} from 'lucide-react'
import { api } from '../services/api'
import type { RunDetailResponse, RunSummary } from '../types'

export const RunHistoryPage: React.FC = () => {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [totalRuns, setTotalRuns] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRunDetail, setSelectedRunDetail] = useState<RunDetailResponse | null>(null)
  const [copiedRunId, setCopiedRunId] = useState<string | null>(null)
  const [copiedJson, setCopiedJson] = useState(false)

  const fetchRuns = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await api.getRuns(50, 0)
      setRuns(res.runs)
      setTotalRuns(res.total_runs)
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch evaluation run history.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRuns()
  }, [])

  const handleInspectRun = async (runId: string) => {
    try {
      const res = await api.getRunDetail(runId)
      setSelectedRunDetail(res)
    } catch (err: any) {
      alert(`Failed to load run details: ${err?.message || 'Unknown error'}`)
    }
  }

  const handleCopyId = (runId: string) => {
    navigator.clipboard.writeText(runId)
    setCopiedRunId(runId)
    setTimeout(() => setCopiedRunId(null), 2000)
  }

  const handleCopyReportJson = () => {
    if (!selectedRunDetail) return
    navigator.clipboard.writeText(JSON.stringify(selectedRunDetail.report, null, 2))
    setCopiedJson(true)
    setTimeout(() => setCopiedJson(false), 2000)
  }

  const handleDownloadReportJson = () => {
    if (!selectedRunDetail) return
    const blob = new Blob([JSON.stringify(selectedRunDetail.report, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rehearsal-run-${selectedRunDetail.run_id}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div style={{ padding: '3rem 0', textAlign: 'center' }}>
        <div className="spinner" style={{ width: 24, height: 24, margin: '0 auto 0.75rem' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading persisted evaluation history...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel" style={{ borderColor: 'var(--status-flawed-border)' }}>
        <h3 style={{ color: 'var(--status-flawed-text)', marginBottom: '0.25rem', fontSize: '0.92rem', fontWeight: 600 }}>Failed to Load Runs</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '0.85rem', fontSize: '0.8rem' }}>{error}</p>
        <button className="btn btn-secondary" onClick={fetchRuns}>
          <RotateCcw size={13} /> Retry
        </button>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* 1. Control Bar */}
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
              Evaluation Run History Archive
            </h2>
            <span className="badge badge-domain">{totalRuns} Runs Recorded</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.785rem' }}>
            Persistent SQLite audit trail in <code>rehearsal_history.sqlite3</code>
          </p>
        </div>

        <button className="btn btn-secondary" onClick={fetchRuns} style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}>
          <RotateCcw size={13} /> Refresh Log
        </button>
      </div>

      {/* 2. Compact Data Grid */}
      {runs.length === 0 ? (
        <div className="panel" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
          <Clock size={24} color="var(--text-dim)" style={{ margin: '0 auto 0.5rem' }} />
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>No Evaluation Runs Stored</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Execute an evaluation suite to benchmark tool accuracy and create verifiable audit records.
          </div>
        </div>
      ) : (
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 140 }}>Run Identifier</th>
                  <th style={{ width: 110 }}>Domain</th>
                  <th style={{ width: 80 }}>Cases</th>
                  <th style={{ width: 140 }}>Tool Accuracy</th>
                  <th style={{ width: 140 }}>Exact Arg Match</th>
                  <th style={{ width: 130 }}>Est. Speech</th>
                  <th style={{ width: 160 }}>Timestamp</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => {
                  const isCopied = copiedRunId === r.run_id
                  return (
                    <tr key={r.run_id}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <code style={{ fontSize: '0.785rem', color: '#fff', fontWeight: 600 }}>{r.run_id}</code>
                          <button
                            className="btn-icon"
                            style={{ padding: '2px 3px', border: 'none' }}
                            onClick={() => handleCopyId(r.run_id)}
                            title="Copy Run ID"
                          >
                            {isCopied ? <Check size={11} color="var(--status-corrected-text)" /> : <Copy size={11} />}
                          </button>
                        </div>
                      </td>

                      <td>
                        <span className="badge badge-domain">
                          {r.domain || 'All Domains'}
                        </span>
                      </td>

                      <td>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.785rem' }}>
                          {r.total_cases}
                        </span>
                      </td>

                      <td>
                        <span style={{ fontWeight: 600, color: 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                          {(r.tool_accuracy * 100).toFixed(0)}%
                        </span>
                      </td>

                      <td>
                        <span style={{ fontWeight: 600, color: '#38bdf8', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                          {(r.exact_match_rate * 100).toFixed(0)}%
                        </span>
                      </td>

                      <td>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.785rem', color: 'var(--text-secondary)' }}>
                          {r.average_duration_seconds.toFixed(1)}s
                        </span>
                      </td>

                      <td>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {new Date(r.created_at).toLocaleString()}
                        </span>
                      </td>

                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '2px 8px', fontSize: '0.72rem' }}
                          onClick={() => handleInspectRun(r.run_id)}
                        >
                          <Eye size={11} /> Inspect
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. Detailed Run Inspection Modal */}
      {selectedRunDetail && (
        <div className="modal-overlay" onClick={() => setSelectedRunDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                  Run Telemetry Inspector:
                </span>
                <code style={{ fontSize: '0.85rem', color: 'var(--accent-primary)' }}>
                  {selectedRunDetail.run_id}
                </code>
              </div>

              <button className="btn-icon" onClick={() => setSelectedRunDetail(null)}>
                <X size={15} />
              </button>
            </div>

            <div className="modal-body">
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                  gap: '0.65rem',
                  marginBottom: '1rem',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Domain</div>
                  <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.82rem' }}>{selectedRunDetail.domain || 'All Domains'}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Cases Tested</div>
                  <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.82rem' }}>{selectedRunDetail.summary.total_cases}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tool Accuracy</div>
                  <div style={{ fontWeight: 600, color: 'var(--status-corrected-text)', fontSize: '0.82rem' }}>
                    {(selectedRunDetail.summary.tool_accuracy * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Arg Match</div>
                  <div style={{ fontWeight: 600, color: '#38bdf8', fontSize: '0.82rem' }}>
                    {(selectedRunDetail.summary.exact_match_rate * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#fff' }}>Verifiable Report JSON</div>
                <div style={{ display: 'flex', gap: '0.35rem' }}>
                  <button className="btn btn-secondary" style={{ padding: '2px 6px', fontSize: '0.72rem' }} onClick={handleCopyReportJson}>
                    {copiedJson ? <Check size={11} color="var(--status-corrected-text)" /> : <Copy size={11} />}
                    <span>{copiedJson ? 'Copied' : 'Copy'}</span>
                  </button>
                  <button className="btn btn-secondary" style={{ padding: '2px 6px', fontSize: '0.72rem' }} onClick={handleDownloadReportJson}>
                    <Download size={11} /> Export JSON
                  </button>
                </div>
              </div>

              <pre className="code-block" style={{ maxHeight: 350 }}>
                {JSON.stringify(selectedRunDetail.report, null, 2)}
              </pre>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectedRunDetail(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
