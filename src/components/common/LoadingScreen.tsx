import { memo } from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingScreenProps {
  /** Message shown beneath the spinner */
  message?: string;
  /** When true, stretches to fill available vertical space */
  fullScreen?: boolean;
}

const LoadingScreen = ({ message = 'Loading...', fullScreen = false }: LoadingScreenProps) => {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-4 text-gray-300 ${
        fullScreen ? 'min-h-screen' : 'py-16'
      }`}
      role="status"
      aria-live="polite"
    >
      <Loader2 className="h-10 w-10 animate-spin text-space-accent" />
      <p className="text-sm uppercase tracking-[0.2em] text-gray-400">{message}</p>
    </div>
  );
};

export default memo(LoadingScreen);
