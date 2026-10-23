export interface HealthResponse {
  status: string
  version: string
  service: string
  timestamp: string
  mcp_sdk_version: string
  disclaimer: string
}

export type ToolGroup = 'flawed' | 'corrected'
export type ToolDomain = 'weather' | 'smart_home' | 'travel'

export interface MCPTool {
  name: string
  description: string
  input_schema: Record<string, any>
  group: ToolGroup
  domain: ToolDomain
}

export interface ToolsListResponse {
  total_tools: number
  tools: MCPTool[]
}

export type SeverityLevel = 'error' | 'warning' | 'info'

export interface LinterFinding {
  rule_id: string
  severity: SeverityLevel
  tool_name: string
  title: string
  evidence: string
  voice_impact: string
  recommendation: string
  suggested_fix_example?: string | null
  is_heuristic: boolean
}

export interface LintResponse {
  target_group: string
  overall_score: number
  total_tools_analyzed: number
  error_count: number
  warning_count: number
  info_count: number
  tool_scores: Record<string, number>
  findings: LinterFinding[]
  findings_by_severity: Record<string, LinterFinding[]>
  rule_counts: Record<string, number>
  scoring_methodology: string
  disclaimer: string
}

export interface CaseEvaluationResult {
  case_id: string
  domain: string
  utterance: string
  expected_tool: string | null
  predicted_tool: string | null
  tool_match: boolean
  expected_arguments: Record<string, any>
  predicted_arguments: Record<string, any>
  exact_argument_match: boolean
  matched_slots: string[]
  missing_slots: string[]
  unexpected_slots: string[]
  is_abstention_correct: boolean
  tool_output?: string | null
  estimated_speech_duration_seconds?: number | null
  status: 'PASS' | 'FAIL'
}

export interface SlotMetrics {
  total_expected_slots: number
  total_predicted_slots: number
  true_positives: number
  precision: number
  recall: number
  f1_score: number
}

export interface DomainEvaluationResult {
  domain: string
  total_cases: number
  correct_tool_selections: number
  tool_selection_accuracy: number
  exact_argument_matches: number
  exact_argument_match_rate: number
}

export interface EvaluateResponse {
  run_id: string
  domain?: string | null
  total_cases: number
  correct_tool_selections: number
  tool_selection_accuracy: number
  exact_argument_matches: number
  exact_argument_match_rate: number
  slot_metrics: SlotMetrics
  missing_argument_count: number
  unexpected_argument_count: number
  total_abstentions: number
  correct_abstentions: number
  average_estimated_speech_duration_seconds: number
  per_domain_results: Record<string, DomainEvaluationResult>
  case_results: CaseEvaluationResult[]
}

export interface ToolComparisonItem {
  domain: string
  flawed_tool_name: string
  corrected_tool_name: string
  flawed_score: number
  corrected_score: number
  flawed_findings_count: number
  corrected_findings_count: number
  flawed_nesting_depth: number
  corrected_nesting_depth: number
  voice_differences: string[]
}

export interface CompareResponse {
  flawed_average_score: number
  corrected_average_score: number
  score_improvement: number
  comparisons: ToolComparisonItem[]
  disclaimer: string
}

export interface RunSummary {
  run_id: string
  created_at: string
  domain?: string | null
  total_cases: number
  tool_accuracy: number
  exact_match_rate: number
  f1_score: number
  average_duration_seconds: number
}

export interface RunListResponse {
  total_runs: number
  limit: number
  offset: number
  runs: RunSummary[]
}

export interface RunDetailResponse {
  run_id: string
  created_at: string
  domain?: string | null
  summary: {
    total_cases: number
    tool_accuracy: number
    exact_match_rate: number
    f1_score: number
    average_duration_seconds: number
  }
  report: EvaluateResponse
}
