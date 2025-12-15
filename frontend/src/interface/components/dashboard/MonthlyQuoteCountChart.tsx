import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { MonthlyMetricUi } from '../../../domain/quote/metricsTypes';

type Props = { data: MonthlyMetricUi[] };

export function MonthlyQuoteCountChart({ data }: Props) {
  const chartData = data.map((d) => ({
    month: d.month.toLocaleDateString('fr-FR', {
      month: 'short',
      year: 'numeric',
    }),
    count: d.quoteCount,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nombre de devis mensuels</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis dataKey="month" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Bar dataKey="count" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
