import type {
  CompareResponse,
  EvaluateResponse,
  HealthResponse,
  LintResponse,
  RunDetailResponse,
  RunListResponse,
  ToolsListResponse,
} from '../types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...options.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })

    if (!response.ok) {
      let errorMsg = `Server error ${response.status}: ${response.statusText}`
      try {
        const errorData = await response.json()
        if (errorData?.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
        }
      } catch {
        // use fallback error message
      }
      throw new ApiError(errorMsg, response.status)
    }

    return await response.json()
  } catch (err) {
    if (err instanceof ApiError) {
      throw err
    }
    const message = err instanceof Error ? err.message : 'Unknown network failure'
    throw new ApiError(`Unable to connect to Rehearsal API at ${url}. Please ensure the backend is running. (${message})`, 0)
  }
}

export const api = {
  getHealth: (): Promise<HealthResponse> => request<HealthResponse>('/api/health'),

  getTools: (): Promise<ToolsListResponse> => request<ToolsListResponse>('/api/tools'),

  runLinter: (targetGroup: 'all' | 'flawed' | 'corrected' = 'all'): Promise<LintResponse> =>
    request<LintResponse>('/api/lint', {
      method: 'POST',
      body: JSON.stringify({ target_group: targetGroup }),
    }),

  runEvaluation: (domain?: string | null, liveExecution = true): Promise<EvaluateResponse> =>
    request<EvaluateResponse>('/api/evaluate', {
      method: 'POST',
      body: JSON.stringify({ domain: domain || null, live_execution: liveExecution }),
    }),

  getComparison: (): Promise<CompareResponse> =>
    request<CompareResponse>('/api/compare', {
      method: 'POST',
    }),

  getRuns: (limit = 20, offset = 0): Promise<RunListResponse> =>
    request<RunListResponse>(`/api/runs?limit=${limit}&offset=${offset}`),

  getRunDetail: (runId: string): Promise<RunDetailResponse> =>
    request<RunDetailResponse>(`/api/runs/${encodeURIComponent(runId)}`),
}
