import { useMemo, useState } from 'react';
import { Navigation as NavigationIcon, MapPin, Fuel, Clock, Send } from 'lucide-react';
import { useShips, useWaypoints, useNavigateShip } from '../../hooks/useSpaceTraders';
import { calculateDistance, calculateFuelNeeded, calculateTravelTime, formatDuration } from '../../utils/helpers';
import LoadingState from '../common/LoadingState';

const Navigation = () => {
  const { data: ships, isLoading: shipsLoading } = useShips();
  const [selectedShip, setSelectedShip] = useState('');
  const [destinationWaypoint, setDestinationWaypoint] = useState('');
  const navigateShip = useNavigateShip();

  const ship = useMemo(() => ships?.find((s) => s.symbol === selectedShip), [ships, selectedShip]);
  const systemSymbol = ship?.nav.systemSymbol || '';

  const { data: waypointsData, isLoading: waypointsLoading } = useWaypoints(systemSymbol);

  const waypoints = useMemo(() => waypointsData?.data ?? [], [waypointsData]);

  if (shipsLoading) {
    return (
      <div className="p-6">
        <LoadingState label="Navigation" description="Fetching ship telemetry..." />
      </div>
    );
  }

  const handleNavigate = async () => {
    if (!selectedShip || !destinationWaypoint) return;

    try {
      await navigateShip.mutateAsync({
        shipSymbol: selectedShip,
        waypointSymbol: destinationWaypoint,
      });
      alert('Navigation started!');
      setDestinationWaypoint('');
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to navigate');
    }
  };

  const destination = useMemo(
    () => waypoints.find((w) => w.symbol === destinationWaypoint),
    [destinationWaypoint, waypoints]
  );
  const distance = ship && destination
    ? calculateDistance(
        ship.nav.route.origin.x,
        ship.nav.route.origin.y,
        destination.x,
        destination.y
      )
    : 0;

  const fuelNeeded = distance > 0 ? calculateFuelNeeded(distance, ship?.nav.flightMode) : 0;
  const travelTime = ship && distance > 0 ? calculateTravelTime(distance, ship.engine.speed, ship.nav.flightMode) : 0;
  const canNavigate = ship && ship.nav.status !== 'IN_TRANSIT' && destinationWaypoint && fuelNeeded <= ship.fuel.current;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Navigation</h1>
        <p className="text-gray-400">Plan and execute ship movements</p>
      </div>

      {/* Ship Selection */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Select Ship</h2>
        <select
          value={selectedShip}
          onChange={(e) => setSelectedShip(e.target.value)}
          className="input w-full"
        >
          <option value="">Choose a ship...</option>
          {ships
            ?.filter((s) => s.nav.status !== 'IN_TRANSIT')
            .map((ship) => (
              <option key={ship.symbol} value={ship.symbol}>
                {ship.registration.name} - {ship.nav.waypointSymbol}
              </option>
            ))}
        </select>
      </div>

      {/* Current Location */}
      {ship && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Current Location</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">System</p>
              <p className="text-white font-medium">{ship.nav.systemSymbol}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Waypoint</p>
              <p className="text-white font-medium">{ship.nav.waypointSymbol}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Status</p>
              <span
                className={`badge ${
                  ship.nav.status === 'DOCKED'
                    ? 'badge-success'
                    : ship.nav.status === 'IN_ORBIT'
                    ? 'badge-warning'
                    : 'badge-info'
                }`}
              >
                {ship.nav.status.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Destination Selection */}
      {ship && (shipsLoading || waypointsLoading) && (
        <div className="card">
          <LoadingState label="Destinations" description="Mapping system waypoints..." />
        </div>
      )}

      {ship && !waypointsLoading && waypoints.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Select Destination</h2>
          <select
            value={destinationWaypoint}
            onChange={(e) => setDestinationWaypoint(e.target.value)}
            className="input w-full"
          >
            <option value="">Choose a destination...</option>
            {waypoints
              .filter((w) => w.symbol !== ship.nav.waypointSymbol)
              .map((waypoint) => (
                <option key={waypoint.symbol} value={waypoint.symbol}>
                  {waypoint.symbol} - {waypoint.type.replace('_', ' ')}
                </option>
              ))}
          </select>
        </div>
      )}

      {ship && !waypointsLoading && waypoints.length === 0 && (
        <div className="card text-center py-12 text-gray-400">
          No alternative waypoints detected in this system.
        </div>
      )}

      {/* Route Information */}
      {ship && !waypointsLoading && destination && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Route Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-gray-800/50 rounded">
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <MapPin className="w-4 h-4" />
                <span className="text-sm">Distance</span>
              </div>
              <p className="text-xl font-semibold text-white">{Math.round(distance)}</p>
            </div>
            <div className="p-4 bg-gray-800/50 rounded">
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <Fuel className="w-4 h-4" />
                <span className="text-sm">Fuel Needed</span>
              </div>
              <p className="text-xl font-semibold text-white">
                {fuelNeeded} / {ship.fuel.current}
              </p>
            </div>
            <div className="p-4 bg-gray-800/50 rounded">
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Travel Time</span>
              </div>
              <p className="text-xl font-semibold text-white">{formatDuration(travelTime)}</p>
            </div>
            <div className="p-4 bg-gray-800/50 rounded">
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <NavigationIcon className="w-4 h-4" />
                <span className="text-sm">Flight Mode</span>
              </div>
              <p className="text-xl font-semibold text-white">{ship.nav.flightMode}</p>
            </div>
          </div>

          {fuelNeeded > ship.fuel.current && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded mb-4">
              <p className="text-red-400 text-sm">
                ⚠️ Insufficient fuel! You need {fuelNeeded} fuel but only have {ship.fuel.current}.
                Please refuel before navigating.
              </p>
            </div>
          )}

          <button
            onClick={handleNavigate}
            disabled={!canNavigate || navigateShip.isPending}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            {navigateShip.isPending ? 'Navigating...' : 'Start Navigation'}
          </button>
        </div>
      )}

      {!selectedShip && (
        <div className="card text-center py-12">
          <NavigationIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Select a ship to begin navigation</p>
        </div>
      )}
    </div>
  );
};

export default Navigation;
