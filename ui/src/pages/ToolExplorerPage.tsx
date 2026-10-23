import React, { useEffect, useState } from 'react'
import {
  Check,
  CheckCircle2,
  Code2,
  Copy,
  RotateCcw,
  Search,
  Table,
  XCircle,
} from 'lucide-react'
import { api } from '../services/api'
import type { MCPTool } from '../types'

export const ToolExplorerPage: React.FC = () => {
  const [tools, setTools] = useState<MCPTool[]>([])
  const [selectedToolName, setSelectedToolName] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters & State
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [groupFilter, setGroupFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [viewMode, setViewMode] = useState<'table' | 'json'>('table')
  const [isCopied, setIsCopied] = useState(false)

  const fetchTools = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await api.getTools()
      setTools(res.tools)
      if (res.tools.length > 0) {
        setSelectedToolName(res.tools[0].name)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch registered tools from backend.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTools()
  }, [])

  const filteredTools = tools.filter((tool) => {
    if (domainFilter !== 'all' && tool.domain !== domainFilter) return false
    if (groupFilter !== 'all' && tool.group !== groupFilter) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchName = tool.name.toLowerCase().includes(q)
      const matchDesc = tool.description.toLowerCase().includes(q)
      if (!matchName && !matchDesc) return false
    }
    return true
  })

  const selectedTool = tools.find((t) => t.name === selectedToolName) || filteredTools[0]

  const handleCopy = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setIsCopied(true)
    setTimeout(() => {
      setIsCopied(false)
    }, 2000)
  }

  if (isLoading) {
    return (
      <div style={{ padding: '3rem 0', textAlign: 'center' }}>
        <div className="spinner" style={{ width: 24, height: 24, margin: '0 auto 0.75rem' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading reference MCP tools...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel" style={{ borderColor: 'var(--status-flawed-border)' }}>
        <h3 style={{ color: 'var(--status-flawed-text)', marginBottom: '0.25rem', fontSize: '0.92rem', fontWeight: 600 }}>Failed to Load Tools</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '0.85rem', fontSize: '0.8rem' }}>{error}</p>
        <button className="btn btn-secondary" onClick={fetchTools}>
          <RotateCcw size={13} /> Retry
        </button>
      </div>
    )
  }

  // Schema analysis for selected tool
  const schema = selectedTool?.input_schema || {}
  const properties = schema.properties || {}
  const requiredProps: string[] = schema.required || []
  const propKeys = Object.keys(properties)
  const isFlawed = selectedTool?.group === 'flawed'
  const hasDefs = '$defs' in schema || 'definitions' in schema

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* Top Filter Bar */}
      <div
        className="panel"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          padding: '0.65rem 1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {/* Search Input */}
          <div style={{ position: 'relative', width: 200 }}>
            <Search size={13} style={{ position: 'absolute', left: 8, top: 8, color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.3rem 0.6rem 0.3rem 1.7rem',
                backgroundColor: 'var(--bg-surface-elevated)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-sm)',
                color: '#fff',
                fontSize: '0.785rem',
              }}
            />
          </div>

          {/* Group Filter */}
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
                backgroundColor: groupFilter === 'all' ? 'var(--accent-primary)' : 'transparent',
                color: groupFilter === 'all' ? '#fff' : 'var(--text-secondary)',
                fontWeight: groupFilter === 'all' ? 600 : 400,
              }}
              onClick={() => setGroupFilter('all')}
            >
              All (6)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: groupFilter === 'flawed' ? 'var(--status-flawed-bg)' : 'transparent',
                color: groupFilter === 'flawed' ? 'var(--status-flawed-text)' : 'var(--text-secondary)',
                fontWeight: groupFilter === 'flawed' ? 600 : 400,
              }}
              onClick={() => setGroupFilter('flawed')}
            >
              Flawed (3)
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: groupFilter === 'corrected' ? 'var(--status-corrected-bg)' : 'transparent',
                color: groupFilter === 'corrected' ? 'var(--status-corrected-text)' : 'var(--text-secondary)',
                fontWeight: groupFilter === 'corrected' ? 600 : 400,
              }}
              onClick={() => setGroupFilter('corrected')}
            >
              Voice-First (3)
            </button>
          </div>

          {/* Domain Filter */}
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
                backgroundColor: domainFilter === 'all' ? 'var(--accent-primary)' : 'transparent',
                color: domainFilter === 'all' ? '#fff' : 'var(--text-secondary)',
                fontWeight: domainFilter === 'all' ? 600 : 400,
              }}
              onClick={() => setDomainFilter('all')}
            >
              All
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: domainFilter === 'weather' ? 'var(--accent-primary)' : 'transparent',
                color: domainFilter === 'weather' ? '#fff' : 'var(--text-secondary)',
                fontWeight: domainFilter === 'weather' ? 600 : 400,
              }}
              onClick={() => setDomainFilter('weather')}
            >
              Weather
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: domainFilter === 'smart_home' ? 'var(--accent-primary)' : 'transparent',
                color: domainFilter === 'smart_home' ? '#fff' : 'var(--text-secondary)',
                fontWeight: domainFilter === 'smart_home' ? 600 : 400,
              }}
              onClick={() => setDomainFilter('smart_home')}
            >
              Smart Home
            </button>
            <button
              className="btn btn-ghost"
              style={{
                padding: '3px 8px',
                fontSize: '0.72rem',
                backgroundColor: domainFilter === 'travel' ? 'var(--accent-primary)' : 'transparent',
                color: domainFilter === 'travel' ? '#fff' : 'var(--text-secondary)',
                fontWeight: domainFilter === 'travel' ? 600 : 400,
              }}
              onClick={() => setDomainFilter('travel')}
            >
              Travel
            </button>
          </div>
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Showing <strong>{filteredTools.length}</strong> of {tools.length} registered tools
        </div>
      </div>

      {/* Workbench Master-Detail Split */}
      <div className="workbench-split">
        {/* Left Pane: Tool List */}
        <div className="workbench-pane-list">
          <div
            style={{
              padding: '0.6rem 0.85rem',
              borderBottom: '1px solid var(--border-subtle)',
              fontSize: '0.7rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--text-dim)',
              backgroundColor: 'var(--bg-surface-elevated)',
            }}
          >
            Registered MCP Tools
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            {filteredTools.map((tool) => {
              const isSelected = selectedTool?.name === tool.name
              const isFlawedTool = tool.group === 'flawed'

              return (
                <div
                  key={tool.name}
                  onClick={() => setSelectedToolName(tool.name)}
                  style={{
                    padding: '0.65rem 0.85rem',
                    borderBottom: '1px solid var(--border-subtle)',
                    backgroundColor: isSelected ? 'var(--bg-surface-elevated)' : 'transparent',
                    borderLeft: isSelected ? '3px solid var(--accent-primary)' : '3px solid transparent',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                      <span
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          backgroundColor: isFlawedTool ? 'var(--status-flawed-text)' : 'var(--status-corrected-text)',
                        }}
                      />
                      <code style={{ fontSize: '0.8rem', fontWeight: 600, color: isSelected ? '#fff' : 'var(--text-primary)' }}>
                        {tool.name}
                      </code>
                    </div>

                    <span className={`badge ${isFlawedTool ? 'badge-flawed' : 'badge-corrected'}`} style={{ fontSize: '0.65rem' }}>
                      {isFlawedTool ? 'Flawed' : 'Voice-First'}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    <span>Domain: {tool.domain}</span>
                    <span>{Object.keys(tool.input_schema?.properties || {}).length} params</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Pane: Tool Inspector */}
        <div className="workbench-pane-detail">
          {selectedTool ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <code style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
                      {selectedTool.name}
                    </code>
                    <span className="badge badge-domain">{selectedTool.domain}</span>
                    <span className={`badge ${isFlawed ? 'badge-flawed' : 'badge-corrected'}`}>
                      {isFlawed ? <XCircle size={11} /> : <CheckCircle2 size={11} />}
                      {isFlawed ? 'Anti-Pattern Architecture' : 'Voice-First Architecture'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {selectedTool.description}
                  </div>
                </div>

                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                  onClick={() => handleCopy(selectedTool.input_schema)}
                >
                  {isCopied ? <Check size={12} color="var(--status-corrected-text)" /> : <Copy size={12} />}
                  <span>{isCopied ? 'Copied' : 'Copy Schema'}</span>
                </button>
              </div>

              {/* Heuristic Ergonomics Strip */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '0.75rem',
                }}
              >
                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Nesting Depth
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: hasDefs || isFlawed ? 'var(--status-flawed-text)' : 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    {isFlawed ? 'Depth 3 ($defs nested)' : 'Depth 1 (Flat schema)'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {isFlawed ? 'Blocks voice entity mapping' : 'Direct acoustic slot extraction'}
                  </div>
                </div>

                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Required Arguments
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: requiredProps.length > 3 ? 'var(--status-warning-text)' : 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    {requiredProps.length} required / {propKeys.length} total
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {requiredProps.length > 3 ? 'Exceeds cognitive load' : 'Optimized for turn-taking'}
                  </div>
                </div>

                <div style={{ backgroundColor: 'var(--bg-surface-elevated)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    TTS Response Format
                  </div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: isFlawed ? 'var(--status-flawed-text)' : 'var(--status-corrected-text)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    {isFlawed ? 'Raw JSON / Markdown' : 'Conversational Speech'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {isFlawed ? 'Causes severe ear fatigue' : 'Succinct 1-2 sentence spoken summary'}
                  </div>
                </div>
              </div>

              {/* Schema Inspector Section */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>
                    Input Schema Specification
                  </div>

                  {/* Table vs JSON Toggle */}
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
                        padding: '2px 8px',
                        fontSize: '0.72rem',
                        backgroundColor: viewMode === 'table' ? 'var(--accent-primary)' : 'transparent',
                        color: viewMode === 'table' ? '#fff' : 'var(--text-secondary)',
                      }}
                      onClick={() => setViewMode('table')}
                    >
                      <Table size={12} /> Table View
                    </button>
                    <button
                      className="btn btn-ghost"
                      style={{
                        padding: '2px 8px',
                        fontSize: '0.72rem',
                        backgroundColor: viewMode === 'json' ? 'var(--accent-primary)' : 'transparent',
                        color: viewMode === 'json' ? '#fff' : 'var(--text-secondary)',
                      }}
                      onClick={() => setViewMode('json')}
                    >
                      <Code2 size={12} /> Raw JSON
                    </button>
                  </div>
                </div>

                {viewMode === 'table' ? (
                  <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Property</th>
                          <th>Type</th>
                          <th>Required</th>
                          <th>Description & Constraints</th>
                        </tr>
                      </thead>
                      <tbody>
                        {propKeys.length === 0 ? (
                          <tr>
                            <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                              No properties defined in schema.
                            </td>
                          </tr>
                        ) : (
                          propKeys.map((pk) => {
                            const prop = properties[pk] || {}
                            const isReq = requiredProps.includes(pk)
                            return (
                              <tr key={pk}>
                                <td>
                                  <code style={{ fontSize: '0.785rem', color: '#fff', fontWeight: 600 }}>{pk}</code>
                                </td>
                                <td>
                                  <span className="badge badge-domain" style={{ color: '#38bdf8' }}>
                                    {prop.type || (prop['$ref'] ? 'ref ($defs)' : 'object')}
                                  </span>
                                </td>
                                <td>
                                  <span
                                    className="badge"
                                    style={{
                                      backgroundColor: isReq ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                                      color: isReq ? 'var(--status-flawed-text)' : 'var(--text-muted)',
                                      border: isReq ? '1px solid var(--status-flawed-border)' : '1px solid var(--border-subtle)',
                                    }}
                                  >
                                    {isReq ? 'Required' : 'Optional'}
                                  </span>
                                </td>
                                <td>
                                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.76rem' }}>
                                    {prop.description || 'No description provided.'}
                                  </div>
                                  {prop.enum && (
                                    <div style={{ marginTop: '0.2rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                      Allowed: <code>{prop.enum.join(' | ')}</code>
                                    </div>
                                  )}
                                </td>
                              </tr>
                            )
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <pre className="code-block" style={{ maxHeight: 320 }}>
                    {JSON.stringify(selectedTool.input_schema, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              Select a tool from the left catalog to inspect.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
