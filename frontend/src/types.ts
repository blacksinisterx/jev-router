export interface TaskRequest {
  prompt: string;
  estimated_output_tokens?: number;
}

export interface ModelOption {
  id: string;
  name: string;
  tier: "fast" | "balanced" | "frontier";
  estimated_cost_usd: number;
  estimated_latency_ms: number;
}

export interface RoutingResult {
  selected_model: ModelOption;
  reason: string;
  latency_ms: number;
  provider: string;
  raw_answers: Record<string, unknown>;
  prompt: string;
  alternatives: ModelOption[];
}

export interface DemoTask {
  category: string;
  prompt: string;
}

export interface CatalogModel {
  id: string;
  name: string;
  tier: string;
  input_price_per_m: number;
  output_price_per_m: number;
  avg_latency_ms: number;
  max_complexity: number;
  supports_reasoning: boolean;
  good_for: string[];
}
