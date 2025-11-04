import React, { useState } from 'react';
import { MapPin, Search } from 'lucide-react';
import { useShips, useWaypoints } from '../../hooks/useSpaceTraders';
import { getWaypointTypeIcon } from '../../utils/helpers';

const Systems = () => {
  const { data: ships } = useShips();
  const [selectedSystem, setSelectedSystem] = useState('');

  React.useEffect(() => {
    if (ships && ships.length > 0 && !selectedSystem) {
      const systemSymbol = ships[0].nav.systemSymbol;
      setSelectedSystem(systemSymbol);
    }
  }, [ships, selectedSystem]);

  const { data: waypointsData, isLoading } = useWaypoints(selectedSystem);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Systems Explorer</h1>
        <p className="text-gray-400">Explore systems and discover waypoints</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm text-gray-400 mb-2">Current System</label>
            <div className="flex items-center gap-2 text-lg font-semibold text-white">
              <MapPin className="w-5 h-5 text-space-accent" />
              {selectedSystem || 'Loading...'}
            </div>
          </div>
        </div>

        {isLoading && (
          <div className="text-center py-12 text-gray-400">Loading waypoints...</div>
        )}

        {waypointsData && waypointsData.data.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              Waypoints ({waypointsData.data.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {waypointsData.data.map((waypoint) => (
                <div key={waypoint.symbol} className="p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getWaypointTypeIcon(waypoint.type)}</span>
                      <div>
                        <h4 className="font-medium text-white">{waypoint.symbol}</h4>
                        <p className="text-xs text-gray-400">{waypoint.type.replace('_', ' ')}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 mb-2">
                    Coordinates: ({waypoint.x}, {waypoint.y})
                  </div>

                  {waypoint.traits.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {waypoint.traits.slice(0, 3).map((trait, idx) => (
                        <span
                          key={idx}
                          className="badge badge-info text-xs"
                        >
                          {trait.symbol}
                        </span>
                      ))}
                      {waypoint.traits.length > 3 && (
                        <span className="text-xs text-gray-400">
                          +{waypoint.traits.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">System Information</h2>
        <p className="text-gray-400 text-sm">
          Waypoints are locations within a system where ships can dock, trade, mine, or refuel.
          Each waypoint has unique traits that determine what activities are available there.
        </p>
      </div>
    </div>
  );
};

export default Systems;
