import type {
  QuoteMetricsDto,
  QuoteMetricsUi,
} from '../../domain/quote/metricsTypes';

/**
 * Map metrics from API DTO to UI types
 * Converts string decimals to numbers and snake_case to camelCase
 */
export function mapMetricsToUi(dto: QuoteMetricsDto): QuoteMetricsUi {
  return {
    totalQuotes: dto.total_quotes,
    estimatedRevenue: parseFloat(dto.estimated_revenue),
    acceptanceRate: dto.acceptance_rate,
    monthlyBreakdown: dto.monthly_breakdown.map((m) => ({
      month: new Date(m.month),
      quoteCount: m.quote_count,
      revenue: parseFloat(m.revenue),
    })),
  };
}
