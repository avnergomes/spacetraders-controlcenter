import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Navigation,
  Package,
  Fuel,
  Pickaxe,
  ShoppingCart,
  Anchor,
  Orbit,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import {
  useShip,
  useDockShip,
  useOrbitShip,
  useExtractResources,
  useRefuelShip,
  useSellCargo,
  useNavigateShip,
} from '../../hooks/useSpaceTraders';
import {
  formatNumber,
  formatRelativeTime,
  calculatePercentage,
  getShipRoleColor,
  isCooldownActive,
  getRemainingCooldown,
} from '../../utils/helpers';

const ShipDetail = () => {
  const { shipSymbol } = useParams<{ shipSymbol: string }>();
  const navigate = useNavigate();
  const { data: ship, isLoading, refetch } = useShip(shipSymbol!);
  const dockShip = useDockShip();
  const orbitShip = useOrbitShip();
  const extractResources = useExtractResources();
  const refuelShip = useRefuelShip();
  const [activeTab, setActiveTab] = useState<'overview' | 'cargo' | 'actions'>('overview');
  const [cooldownTimer, setCooldownTimer] = useState<number>(0);

  React.useEffect(() => {
    if (ship && ship.cooldown && isCooldownActive(ship.cooldown.expiration)) {
      const interval = setInterval(() => {
        const remaining = getRemainingCooldown(ship.cooldown.expiration);
        setCooldownTimer(remaining);
        if (remaining === 0) {
          refetch();
        }
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [ship, refetch]);

  if (isLoading || !ship) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-gray-400">Loading ship details...</div>
      </div>
    );
  }

  const handleDock = async () => {
    try {
      await dockShip.mutateAsync(ship.symbol);
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to dock ship');
    }
  };

  const handleOrbit = async () => {
    try {
      await orbitShip.mutateAsync(ship.symbol);
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to orbit ship');
    }
  };

  const handleExtract = async () => {
    try {
      await extractResources.mutateAsync(ship.symbol);
      alert('Resources extracted successfully!');
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to extract resources');
    }
  };

  const handleRefuel = async () => {
    try {
      await refuelShip.mutateAsync(ship.symbol);
      alert('Ship refueled successfully!');
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to refuel ship');
    }
  };

  const fuelPercentage = calculatePercentage(ship.fuel.current, ship.fuel.capacity);
  const cargoPercentage = calculatePercentage(ship.cargo.units, ship.cargo.capacity);
  const isOnCooldown = cooldownTimer > 0;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'cargo', label: 'Cargo' },
    { id: 'actions', label: 'Actions' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/fleet')}
          className="p-2 hover:bg-gray-700 rounded transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-white mb-2">{ship.registration.name}</h1>
          <p className="text-gray-400">{ship.symbol}</p>
        </div>
        <button
          onClick={() => refetch()}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Status */}
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Status</span>
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
          <p className="text-sm text-gray-300">
            {ship.nav.waypointSymbol}
          </p>
          {ship.nav.status === 'IN_TRANSIT' && ship.nav.route.arrival && (
            <p className="text-xs text-blue-400 mt-2">
              Arrives in {formatRelativeTime(ship.nav.route.arrival)}
            </p>
          )}
        </div>

        {/* Role */}
        <div className="card">
          <span className="text-sm text-gray-400 mb-2 block">Role</span>
          <span className={`badge ${getShipRoleColor(ship.registration.role)}`}>
            {ship.registration.role.replace('_', ' ')}
          </span>
        </div>

        {/* Flight Mode */}
        <div className="card">
          <span className="text-sm text-gray-400 mb-2 block">Flight Mode</span>
          <span className="badge badge-info">
            {ship.nav.flightMode}
          </span>
        </div>
      </div>

      {/* Cooldown Alert */}
      {isOnCooldown && (
        <div className="card bg-yellow-500/10 border-yellow-500/30">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            <div className="flex-1">
              <p className="text-yellow-400 font-semibold">Ship on Cooldown</p>
              <p className="text-sm text-gray-300">
                {Math.floor(cooldownTimer / 60)}m {cooldownTimer % 60}s remaining
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {ship.nav.status !== 'DOCKED' && (
            <button
              onClick={handleDock}
              disabled={dockShip.isPending || ship.nav.status === 'IN_TRANSIT'}
              className="btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Anchor className="w-4 h-4" />
              Dock
            </button>
          )}
          {ship.nav.status === 'DOCKED' && (
            <button
              onClick={handleOrbit}
              disabled={orbitShip.isPending}
              className="btn-secondary flex items-center justify-center gap-2"
            >
              <Orbit className="w-4 h-4" />
              Orbit
            </button>
          )}
          <button
            onClick={handleRefuel}
            disabled={refuelShip.isPending || ship.nav.status !== 'DOCKED' || fuelPercentage === 100}
            className="btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Fuel className="w-4 h-4" />
            Refuel
          </button>
          <button
            onClick={handleExtract}
            disabled={
              extractResources.isPending ||
              ship.nav.status !== 'IN_ORBIT' ||
              isOnCooldown ||
              ship.cargo.units >= ship.cargo.capacity
            }
            className="btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Pickaxe className="w-4 h-4" />
            Extract
          </button>
          <button
            onClick={() => navigate('/navigation')}
            disabled={ship.nav.status === 'IN_TRANSIT'}
            className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Navigation className="w-4 h-4" />
            Navigate
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-space-accent border-b-2 border-space-accent'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab ship={ship} />}
        {activeTab === 'cargo' && <CargoTab ship={ship} />}
        {activeTab === 'actions' && <ActionsTab ship={ship} />}
      </div>
    </div>
  );
};

const OverviewTab = ({ ship }: { ship: any }) => {
  const fuelPercentage = calculatePercentage(ship.fuel.current, ship.fuel.capacity);
  const cargoPercentage = calculatePercentage(ship.cargo.units, ship.cargo.capacity);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Resources */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Resources</h3>
        <div className="space-y-4">
          {/* Fuel */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-gray-300">
                <Fuel className="w-4 h-4" />
                <span className="text-sm">Fuel</span>
              </div>
              <span className="text-sm text-gray-400">
                {ship.fuel.current} / {ship.fuel.capacity}
              </span>
            </div>
            <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  fuelPercentage > 50 ? 'bg-green-500' : fuelPercentage > 25 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${fuelPercentage}%` }}
              />
            </div>
          </div>

          {/* Cargo */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-gray-300">
                <Package className="w-4 h-4" />
                <span className="text-sm">Cargo</span>
              </div>
              <span className="text-sm text-gray-400">
                {ship.cargo.units} / {ship.cargo.capacity}
              </span>
            </div>
            <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  cargoPercentage < 80 ? 'bg-blue-500' : cargoPercentage < 100 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${cargoPercentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Ship Info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Ship Information</h3>
        <div className="space-y-3">
          <InfoRow label="Frame" value={ship.frame.name} />
          <InfoRow label="Reactor" value={ship.reactor.name} />
          <InfoRow label="Engine" value={ship.engine.name} />
          <InfoRow label="Speed" value={ship.engine.speed.toString()} />
          <InfoRow label="Modules" value={ship.modules.length.toString()} />
          <InfoRow label="Mounts" value={ship.mounts.length.toString()} />
        </div>
      </div>

      {/* Crew */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Crew</h3>
        <div className="space-y-3">
          <InfoRow label="Current" value={`${ship.crew.current} / ${ship.crew.capacity}`} />
          <InfoRow label="Required" value={ship.crew.required.toString()} />
          <InfoRow label="Morale" value={`${ship.crew.morale}%`} />
          <InfoRow label="Rotation" value={ship.crew.rotation} />
        </div>
      </div>

      {/* Condition */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Condition</h3>
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-400">Frame Integrity</span>
              <span className="text-sm text-gray-300">{ship.frame.integrity}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  ship.frame.integrity > 75 ? 'bg-green-500' : ship.frame.integrity > 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${ship.frame.integrity}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-400">Engine Condition</span>
              <span className="text-sm text-gray-300">{ship.engine.condition}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  ship.engine.condition > 75 ? 'bg-green-500' : ship.engine.condition > 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${ship.engine.condition}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CargoTab = ({ ship }: { ship: any }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Cargo Hold</h3>
      {ship.cargo.inventory.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ship.cargo.inventory.map((item: any, index: number) => (
            <div key={index} className="p-4 bg-gray-800/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{item.name}</span>
                <span className="badge badge-info">{item.units}</span>
              </div>
              <p className="text-xs text-gray-400">{item.symbol}</p>
              <p className="text-xs text-gray-400 mt-2">{item.description}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Package className="w-12 h-12 text-gray-600 mx-auto mb-2" />
          <p className="text-gray-400">Cargo hold is empty</p>
        </div>
      )}
    </div>
  );
};

const ActionsTab = ({ ship }: { ship: any }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Available Actions</h3>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-medium text-white mb-2">Mining Operations</h4>
          <p className="text-sm text-gray-400 mb-3">
            Extract resources from asteroid fields. Requires ship to be in orbit.
          </p>
          <div className="text-xs text-gray-500">
            Cooldown: Varies by operation • Cargo space required
          </div>
        </div>
        
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-medium text-white mb-2">Trading</h4>
          <p className="text-sm text-gray-400 mb-3">
            Buy and sell goods at markets. Ship must be docked at a waypoint with a marketplace.
          </p>
          <div className="text-xs text-gray-500">
            Available when docked at market waypoints
          </div>
        </div>

        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="font-medium text-white mb-2">Navigation</h4>
          <p className="text-sm text-gray-400 mb-3">
            Travel to different waypoints in the system or jump to other systems.
          </p>
          <div className="text-xs text-gray-500">
            Fuel consumption varies by distance and flight mode
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-center justify-between">
    <span className="text-sm text-gray-400">{label}</span>
    <span className="text-sm text-gray-200">{value}</span>
  </div>
);

export default ShipDetail;
