import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
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
    <Card className="shadow-none border border-border">
      <CardHeader>
        <CardTitle className="text-base font-semibold">
          Évolution du CA
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 10, left: 10, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              className="stroke-muted"
            />
            <XAxis
              dataKey="month"
              className="text-[10px] text-muted-foreground"
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              className="text-[10px] text-muted-foreground"
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => `${value}€`}
            />
            <Tooltip
              contentStyle={{
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(value) => [`${value} €`, "Chiffre d'affaires"]}
            />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="hsl(166 100% 39%)"
              strokeWidth={3}
              dot={{
                fill: 'hsl(166 100% 39%)',
                strokeWidth: 2,
                r: 4,
                stroke: '#fff',
              }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
