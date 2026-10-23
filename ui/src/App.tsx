import React, { useEffect, useState } from 'react'
import {
  Activity,
  Boxes,
  Clock,
  Gauge,
  Menu,
  Play,
  Scale,
  Terminal,
  X,
} from 'lucide-react'
import { ComparePage } from './pages/ComparePage'
import { EvaluationRunnerPage } from './pages/EvaluationRunnerPage'
import { OverviewPage } from './pages/OverviewPage'
import { RunHistoryPage } from './pages/RunHistoryPage'
import { ToolExplorerPage } from './pages/ToolExplorerPage'
import { VoiceLinterPage } from './pages/VoiceLinterPage'
import { api } from './services/api'
import type { HealthResponse } from './types'

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const checkHealth = async () => {
    try {
      const data = await api.getHealth()
      setHealth(data)
      setIsBackendHealthy(data.status === 'healthy')
    } catch {
      setIsBackendHealthy(false)
      setHealth(null)
    }
  }

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleTabChange = (tab: string) => {
    setActiveTab(tab)
    setMobileMenuOpen(false)
  }

  const getBreadcrumbTitle = () => {
    switch (activeTab) {
      case 'overview':
        return 'Overview'
      case 'tools':
        return 'Tool Explorer'
      case 'linter':
        return 'Voice Linter'
      case 'compare':
        return 'Compare (Benchmark)'
      case 'runner':
        return 'Evaluation Runner'
      case 'history':
        return 'Run History'
      default:
        return 'Workbench'
    }
  }

  return (
    <div className="app-shell">
      {/* Sidebar Navigation */}
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="brand-header">
          <div className="brand-icon">
            <Terminal size={14} />
          </div>
          <div>
            <div className="brand-title">Rehearsal</div>
            <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              MCP Workbench
            </div>
          </div>
          <span className="brand-badge">v0.1.0</span>
        </div>

        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
          <div className="nav-section-title">Core Workspace</div>
          <ul className="nav-links">
            <li>
              <button
                className={`nav-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => handleTabChange('overview')}
              >
                <Gauge size={14} />
                Overview
              </button>
            </li>
            <li>
              <button
                className={`nav-button ${activeTab === 'tools' ? 'active' : ''}`}
                onClick={() => handleTabChange('tools')}
              >
                <Boxes size={14} />
                Tool Explorer
              </button>
            </li>
          </ul>

          <div className="nav-section-title">Diagnostics & Benchmarks</div>
          <ul className="nav-links">
            <li>
              <button
                className={`nav-button ${activeTab === 'linter' ? 'active' : ''}`}
                onClick={() => handleTabChange('linter')}
              >
                <Activity size={14} />
                Voice Linter
              </button>
            </li>
            <li>
              <button
                className={`nav-button ${activeTab === 'compare' ? 'active' : ''}`}
                onClick={() => handleTabChange('compare')}
              >
                <Scale size={14} />
                Compare
              </button>
            </li>
          </ul>

          <div className="nav-section-title">Execution & Telemetry</div>
          <ul className="nav-links">
            <li>
              <button
                className={`nav-button ${activeTab === 'runner' ? 'active' : ''}`}
                onClick={() => handleTabChange('runner')}
              >
                <Play size={14} />
                Evaluation Runner
              </button>
            </li>
            <li>
              <button
                className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
                onClick={() => handleTabChange('history')}
              >
                <Clock size={14} />
                Run History
              </button>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--accent-primary)' }} />
            <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Independent Studio</span>
          </div>
          <div>MCP voice-readiness evaluation testbed</div>
        </div>
      </aside>

      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-label="Close navigation overlay"
        />
      )}

      {/* Main Viewport */}
      <main className="main-viewport">
        {/* Top Header Bar */}
        <header className="top-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              className="btn-icon mobile-menu-toggle"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
            </button>

            <div className="top-bar-breadcrumb">
              <span className="crumb-root">rehearsal</span>
              <span className="crumb-divider">/</span>
              <span className="crumb-active">{getBreadcrumbTitle()}</span>
            </div>
          </div>

          <div className="top-bar-actions">
            {isBackendHealthy ? (
              <div className="health-pill" title="FastAPI backend connected at 127.0.0.1:8000">
                <span className="health-dot" />
                <span>127.0.0.1:8000 (mcp-sdk v{health?.mcp_sdk_version || '2.3.0'})</span>
              </div>
            ) : isBackendHealthy === false ? (
              <div className="health-pill offline" title="FastAPI backend offline">
                <span className="health-dot" />
                <span>Backend Offline</span>
              </div>
            ) : (
              <div className="health-pill">
                <span className="spinner" style={{ width: 8, height: 8 }} />
                <span>Connecting...</span>
              </div>
            )}
          </div>
        </header>

        {/* Tab Content */}
        <div className="content-container">
          {activeTab === 'overview' && <OverviewPage onNavigate={(tab) => handleTabChange(tab)} />}
          {activeTab === 'tools' && <ToolExplorerPage />}
          {activeTab === 'linter' && <VoiceLinterPage />}
          {activeTab === 'compare' && <ComparePage />}
          {activeTab === 'runner' && <EvaluationRunnerPage />}
          {activeTab === 'history' && <RunHistoryPage />}
        </div>
      </main>
    </div>
  )
}

export default App
