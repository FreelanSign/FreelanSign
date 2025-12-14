import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { MonthlyMetricUi } from '../../../domain/quote/metricsTypes';

type Props = { data: MonthlyMetricUi[] };

export function MonthlyRevenueChart({ data }: Props) {
  const chartData = data.map((d) => ({
    month: d.month.toLocaleDateString('fr-FR', {
      month: 'short',
      year: 'numeric',
    }),
    revenue: d.revenue,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>CA mensuel</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis dataKey="month" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip formatter={(value) => `${value} €`} />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#6366f1"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
