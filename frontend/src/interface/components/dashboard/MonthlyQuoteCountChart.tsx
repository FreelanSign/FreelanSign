import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
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
    <Card className="shadow-none border border-border">
      <CardHeader>
        <CardTitle className="text-base font-semibold">
          Volume d'activité
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
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
              allowDecimals={false}
            />
            <Tooltip
              cursor={{ fill: 'hsl(166 100% 39% / 0.05)' }}
              contentStyle={{
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(value) => [value, 'Nombre de devis']}
            />
            <Bar
              dataKey="count"
              fill="hsl(166 100% 39%)"
              radius={[4, 4, 0, 0]}
              barSize={32}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
