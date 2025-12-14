// API DTOs (backend response format)

export type MonthlyMetricDto = {
  month: string; // ISO date "2025-01-01"
  quote_count: number;
  revenue: string; // decimal as string "3500.00"
};

export type QuoteMetricsDto = {
  total_quotes: number;
  estimated_revenue: string; // decimal as string
  acceptance_rate: number;
  monthly_breakdown: MonthlyMetricDto[];
};

// UI types (frontend usage)

export type MonthlyMetricUi = {
  month: Date;
  quoteCount: number;
  revenue: number;
};

export type QuoteMetricsUi = {
  totalQuotes: number;
  estimatedRevenue: number;
  acceptanceRate: number;
  monthlyBreakdown: MonthlyMetricUi[];
};
