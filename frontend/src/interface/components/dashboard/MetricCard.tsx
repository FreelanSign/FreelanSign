import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  className,
}: MetricCardProps) {
  return (
    <Card
      className={cn(
        'shadow-none border border-border overflow-hidden',
        className,
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            {title}
          </p>
          {icon && (
            <div className="p-2 rounded-lg bg-brand/10 text-brand">{icon}</div>
          )}
        </div>
        <div className="space-y-1">
          <div className="text-3xl font-bold tracking-tight text-brand">
            {value}
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground font-medium">
              {subtitle}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
