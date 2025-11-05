import { useEffect, useMemo, useState } from 'react';
import { ShoppingCart } from 'lucide-react';
import { useShips, useWaypoints } from '../../hooks/useSpaceTraders';
import LoadingState from '../common/LoadingState';

const Markets = () => {
  const { data: ships, isLoading: shipsLoading } = useShips();
  const [selectedSystem, setSelectedSystem] = useState('');

  useEffect(() => {
    if (ships && ships.length > 0 && !selectedSystem) {
      const systemSymbol = ships[0].nav.systemSymbol;
      setSelectedSystem(systemSymbol);
    }
  }, [ships, selectedSystem]);

  const { data: waypointsData, isLoading: waypointsLoading } = useWaypoints(selectedSystem, 'MARKETPLACE');

  const markets = useMemo(() => waypointsData?.data ?? [], [waypointsData]);

  if (shipsLoading) {
    return (
      <div className="p-6">
        <LoadingState label="Markets" description="Locating your fleet to determine nearby exchanges..." />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Markets</h1>
        <p className="text-gray-400">View market data and find profitable trade routes</p>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Market Overview</h2>
        {waypointsLoading ? (
          <LoadingState label="Marketplaces" description="Scanning systems for trade hubs..." />
        ) : markets.length > 0 ? (
          <div className="space-y-4">
            <p className="text-gray-400">
              Found {markets.length} markets in {selectedSystem}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {markets.map((waypoint) => (
                <div key={waypoint.symbol} className="p-4 bg-gray-800/50 rounded-lg">
                  <h3 className="font-medium text-white mb-2">{waypoint.symbol}</h3>
                  <p className="text-sm text-gray-400 mb-2">{waypoint.type}</p>
                  <div className="flex items-center gap-2">
                    <ShoppingCart className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400">Marketplace Available</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            <p>No markets found in the current system</p>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Trade Opportunities</h2>
        <p className="text-gray-400 text-sm">
          Navigate to markets with your ships to view detailed trade goods and prices.
          Look for export goods with high supply to buy low, and import goods with high demand to sell high.
        </p>
      </div>
    </div>
  );
};

export default Markets;
