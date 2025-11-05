import { memo } from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  label?: string;
  description?: string;
}

const LoadingState = ({
  label = 'Loading',
  description = 'Fetching the latest telemetry...'
}: LoadingStateProps) => (
  <div className="flex flex-col items-center justify-center gap-2 py-12 text-center text-gray-400" role="status">
    <Loader2 className="h-6 w-6 animate-spin text-space-accent" />
    <div className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">{label}</div>
    <p className="text-xs text-gray-500">{description}</p>
  </div>
);

export default memo(LoadingState);
