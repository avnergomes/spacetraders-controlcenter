import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Rocket, Coins, FileText, TrendingUp, MapPin } from 'lucide-react';
import { useAgent, useShips, useContracts } from '../../hooks/useSpaceTraders';
import { formatCredits, formatNumber, getShipRoleColor, formatRelativeTime } from '../../utils/helpers';
import LoadingState from '../common/LoadingState';

const Dashboard = () => {
  const { data: agent, isLoading: agentLoading } = useAgent();
  const { data: ships, isLoading: shipsLoading } = useShips();
  const { data: contracts, isLoading: contractsLoading } = useContracts();

  if (agentLoading || shipsLoading || contractsLoading) {
    return (
      <div className="p-6">
        <LoadingState label="Command Center" description="Calibrating mission controls..." />
      </div>
    );
  }

  const stats = useMemo(
    () => [
      {
        label: 'Total Credits',
        value: agent ? formatCredits(agent.credits) : '-',
        icon: Coins,
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-500/10',
      },
      {
        label: 'Fleet Size',
        value: agent ? formatNumber(agent.shipCount) : '-',
        icon: Rocket,
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/10',
      },
      {
        label: 'Active Contracts',
        value: contracts ? contracts.filter(c => c.accepted && !c.fulfilled).length.toString() : '-',
        icon: FileText,
        color: 'text-green-400',
        bgColor: 'bg-green-500/10',
      },
      {
        label: 'Headquarters',
        value: agent?.headquarters?.split('-').slice(-1)[0] || '-',
        icon: MapPin,
        color: 'text-purple-400',
        bgColor: 'bg-purple-500/10',
      },
    ],
    [agent, contracts]
  );

  const activeShips = useMemo(
    () => ships?.filter(s => s.nav.status === 'IN_TRANSIT' || s.nav.status === 'IN_ORBIT') || [],
    [ships]
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Command Center</h1>
        <p className="text-gray-400">
          Welcome back, Agent {agent?.symbol}. Your headquarters: {agent?.headquarters}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Fleet Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Ships */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Fleet Status</h2>
            <Link to="/fleet" className="text-space-accent hover:underline text-sm">
              View All →
            </Link>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded">
              <span className="text-gray-400">In Transit</span>
              <span className="text-white font-semibold">
                {ships?.filter(s => s.nav.status === 'IN_TRANSIT').length || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded">
              <span className="text-gray-400">In Orbit</span>
              <span className="text-white font-semibold">
                {ships?.filter(s => s.nav.status === 'IN_ORBIT').length || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded">
              <span className="text-gray-400">Docked</span>
              <span className="text-white font-semibold">
                {ships?.filter(s => s.nav.status === 'DOCKED').length || 0}
              </span>
            </div>
          </div>

          {activeShips.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Ships in Transit</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {activeShips.slice(0, 5).map((ship) => (
                  <Link
                    key={ship.symbol}
                    to={`/fleet/${ship.symbol}`}
                    className="flex items-center justify-between p-2 hover:bg-gray-800/50 rounded transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Rocket className="w-4 h-4 text-blue-400" />
                      <span className="text-sm text-white">{ship.registration.name}</span>
                    </div>
                    {ship.nav.status === 'IN_TRANSIT' && ship.nav.route.arrival && (
                      <span className="text-xs text-gray-400">
                        ETA: {formatRelativeTime(ship.nav.route.arrival)}
                      </span>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Contracts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Active Contracts</h2>
            <Link to="/contracts" className="text-space-accent hover:underline text-sm">
              View All →
            </Link>
          </div>

          {contractsLoading ? (
            <div className="text-center text-gray-400 py-8">Loading contracts...</div>
          ) : contracts && contracts.length > 0 ? (
            <div className="space-y-3">
              {contracts
                .filter(c => c.accepted && !c.fulfilled)
                .slice(0, 3)
                .map((contract) => (
                  <div key={contract.id} className="p-3 bg-gray-800/50 rounded">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm font-medium text-white">{contract.type}</span>
                      <span className="badge badge-info text-xs">{contract.factionSymbol}</span>
                    </div>
                    {contract.terms.deliver.map((delivery, idx) => (
                      <div key={idx} className="text-xs text-gray-400 mt-1">
                        Deliver: {delivery.tradeSymbol} ({delivery.unitsFulfilled}/{delivery.unitsRequired})
                      </div>
                    ))}
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-700">
                      <span className="text-xs text-gray-400">
                        Deadline: {formatRelativeTime(contract.terms.deadline)}
                      </span>
                      <span className="text-xs text-green-400">
                        {formatCredits(contract.terms.payment.onFulfilled)}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-600 mx-auto mb-2" />
              <p className="text-gray-400 text-sm">No active contracts</p>
              <Link to="/contracts" className="text-space-accent hover:underline text-sm mt-2 inline-block">
                Find Contracts
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Fleet Distribution</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {ships && [...new Set(ships.map(s => s.registration.role))].map((role) => {
            const count = ships.filter(s => s.registration.role === role).length;
            return (
              <div key={role} className="p-3 bg-gray-800/50 rounded">
                <span className={`badge ${getShipRoleColor(role)} mb-2`}>
                  {role.replace('_', ' ')}
                </span>
                <p className="text-2xl font-bold text-white">{count}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Link
            to="/fleet"
            className="p-4 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded-lg transition-colors text-center"
          >
            <Rocket className="w-6 h-6 text-blue-400 mx-auto mb-2" />
            <span className="text-sm text-blue-400">Manage Fleet</span>
          </Link>
          <Link
            to="/markets"
            className="p-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/30 rounded-lg transition-colors text-center"
          >
            <TrendingUp className="w-6 h-6 text-green-400 mx-auto mb-2" />
            <span className="text-sm text-green-400">View Markets</span>
          </Link>
          <Link
            to="/contracts"
            className="p-4 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 rounded-lg transition-colors text-center"
          >
            <FileText className="w-6 h-6 text-purple-400 mx-auto mb-2" />
            <span className="text-sm text-purple-400">Contracts</span>
          </Link>
          <Link
            to="/navigation"
            className="p-4 bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/30 rounded-lg transition-colors text-center"
          >
            <MapPin className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
            <span className="text-sm text-yellow-400">Navigate</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
