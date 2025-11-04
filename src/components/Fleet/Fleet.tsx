import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Rocket, Fuel, Package, MapPin, Clock, Search } from 'lucide-react';
import { useShips } from '../../hooks/useSpaceTraders';
import { getShipRoleColor, formatRelativeTime, calculatePercentage } from '../../utils/helpers';
import type { Ship } from '../../types';

const Fleet = () => {
  const { data: ships, isLoading } = useShips();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredShips = ships?.filter((ship) => {
    const matchesSearch =
      ship.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ship.registration.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || ship.registration.role === roleFilter;
    const matchesStatus = statusFilter === 'ALL' || ship.nav.status === statusFilter;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const roles = ships ? [...new Set(ships.map((s) => s.registration.role))] : [];

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="text-gray-400">Loading fleet...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Fleet Management</h1>
          <p className="text-gray-400">Total Ships: {ships?.length || 0}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name or symbol..."
                className="input w-full pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Role</label>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="input w-full"
            >
              <option value="ALL">All Roles</option>
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input w-full"
            >
              <option value="ALL">All Statuses</option>
              <option value="DOCKED">Docked</option>
              <option value="IN_ORBIT">In Orbit</option>
              <option value="IN_TRANSIT">In Transit</option>
            </select>
          </div>
        </div>
      </div>

      {/* Ships Grid */}
      {filteredShips && filteredShips.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredShips.map((ship) => (
            <ShipCard key={ship.symbol} ship={ship} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <Rocket className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No ships found matching your filters</p>
        </div>
      )}
    </div>
  );
};

const ShipCard = ({ ship }: { ship: Ship }) => {
  const fuelPercentage = calculatePercentage(ship.fuel.current, ship.fuel.capacity);
  const cargoPercentage = calculatePercentage(ship.cargo.units, ship.cargo.capacity);

  const statusColors = {
    DOCKED: 'badge-success',
    IN_ORBIT: 'badge-warning',
    IN_TRANSIT: 'badge-info',
  };

  return (
    <Link
      to={`/fleet/${ship.symbol}`}
      className="card hover:border-space-accent transition-all duration-200 block"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">{ship.registration.name}</h3>
          <p className="text-sm text-gray-400">{ship.symbol}</p>
        </div>
        <Rocket className="w-8 h-8 text-space-accent" />
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className={`badge ${getShipRoleColor(ship.registration.role)}`}>
          {ship.registration.role.replace('_', ' ')}
        </span>
        <span className={`badge ${statusColors[ship.nav.status]}`}>
          {ship.nav.status.replace('_', ' ')}
        </span>
      </div>

      {/* Location */}
      <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
        <MapPin className="w-4 h-4" />
        <span>{ship.nav.waypointSymbol}</span>
      </div>

      {/* Transit Info */}
      {ship.nav.status === 'IN_TRANSIT' && ship.nav.route.arrival && (
        <div className="flex items-center gap-2 text-sm text-blue-400 mb-4 p-2 bg-blue-500/10 rounded">
          <Clock className="w-4 h-4" />
          <span>Arrives in {formatRelativeTime(ship.nav.route.arrival)}</span>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        {/* Fuel */}
        <div>
          <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
            <Fuel className="w-3 h-3" />
            <span>Fuel</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                fuelPercentage > 50 ? 'bg-green-500' : fuelPercentage > 25 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${fuelPercentage}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {ship.fuel.current} / {ship.fuel.capacity}
          </p>
        </div>

        {/* Cargo */}
        <div>
          <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
            <Package className="w-3 h-3" />
            <span>Cargo</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                cargoPercentage < 80 ? 'bg-blue-500' : cargoPercentage < 100 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${cargoPercentage}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {ship.cargo.units} / {ship.cargo.capacity}
          </p>
        </div>
      </div>
    </Link>
  );
};

export default Fleet;
