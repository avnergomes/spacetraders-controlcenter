import React from 'react';
import { FileText, Clock, CheckCircle, TrendingUp, Package } from 'lucide-react';
import { useContracts, useAcceptContract, useFulfillContract } from '../../hooks/useSpaceTraders';
import { formatCredits, formatRelativeTime } from '../../utils/helpers';
import type { Contract } from '../../types';

const Contracts = () => {
  const { data: contracts, isLoading } = useContracts();
  const acceptContract = useAcceptContract();
  const fulfillContract = useFulfillContract();

  const handleAccept = async (contractId: string) => {
    try {
      await acceptContract.mutateAsync(contractId);
      alert('Contract accepted!');
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to accept contract');
    }
  };

  const handleFulfill = async (contractId: string) => {
    try {
      await fulfillContract.mutateAsync(contractId);
      alert('Contract fulfilled!');
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to fulfill contract');
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-gray-400">Loading contracts...</div>
      </div>
    );
  }

  const activeContracts = contracts?.filter(c => c.accepted && !c.fulfilled) || [];
  const availableContracts = contracts?.filter(c => !c.accepted) || [];
  const completedContracts = contracts?.filter(c => c.fulfilled) || [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Contracts</h1>
        <p className="text-gray-400">Manage your faction contracts and deliveries</p>
      </div>

      {/* Active Contracts */}
      {activeContracts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Active Contracts</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {activeContracts.map((contract) => (
              <ContractCard
                key={contract.id}
                contract={contract}
                onFulfill={handleFulfill}
                status="active"
              />
            ))}
          </div>
        </div>
      )}

      {/* Available Contracts */}
      {availableContracts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Available Contracts</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {availableContracts.map((contract) => (
              <ContractCard
                key={contract.id}
                contract={contract}
                onAccept={handleAccept}
                status="available"
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Contracts */}
      {completedContracts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Completed Contracts</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {completedContracts.map((contract) => (
              <ContractCard key={contract.id} contract={contract} status="completed" />
            ))}
          </div>
        </div>
      )}

      {contracts && contracts.length === 0 && (
        <div className="card text-center py-12">
          <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No contracts available</p>
        </div>
      )}
    </div>
  );
};

interface ContractCardProps {
  contract: Contract;
  onAccept?: (contractId: string) => void;
  onFulfill?: (contractId: string) => void;
  status: 'available' | 'active' | 'completed';
}

const ContractCard = ({ contract, onAccept, onFulfill, status }: ContractCardProps) => {
  const isComplete = contract.terms.deliver.every(
    (d) => d.unitsFulfilled >= d.unitsRequired
  );

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">{contract.type}</h3>
          <p className="text-sm text-gray-400">{contract.factionSymbol}</p>
        </div>
        {status === 'available' && (
          <span className="badge badge-info">Available</span>
        )}
        {status === 'active' && (
          <span className="badge badge-warning">In Progress</span>
        )}
        {status === 'completed' && (
          <span className="badge badge-success">Completed</span>
        )}
      </div>

      {/* Deliveries */}
      <div className="space-y-3 mb-4">
        {contract.terms.deliver.map((delivery, idx) => (
          <div key={idx} className="p-3 bg-gray-800/50 rounded">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <Package className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-white">
                  {delivery.tradeSymbol}
                </span>
              </div>
              <span className="text-xs text-gray-400">
                {delivery.unitsFulfilled} / {delivery.unitsRequired}
              </span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all"
                style={{
                  width: `${(delivery.unitsFulfilled / delivery.unitsRequired) * 100}%`,
                }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Deliver to: {delivery.destinationSymbol}
            </p>
          </div>
        ))}
      </div>

      {/* Payment */}
      <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-gray-800/30 rounded">
        <div>
          <p className="text-xs text-gray-400 mb-1">On Accepted</p>
          <p className="text-sm font-semibold text-green-400">
            {formatCredits(contract.terms.payment.onAccepted)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 mb-1">On Fulfilled</p>
          <p className="text-sm font-semibold text-green-400">
            {formatCredits(contract.terms.payment.onFulfilled)}
          </p>
        </div>
      </div>

      {/* Deadline */}
      <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
        <Clock className="w-4 h-4" />
        <span>
          {status === 'available'
            ? `Accept by: ${formatRelativeTime(contract.deadlineToAccept)}`
            : `Complete by: ${formatRelativeTime(contract.terms.deadline)}`}
        </span>
      </div>

      {/* Actions */}
      {status === 'available' && onAccept && (
        <button
          onClick={() => onAccept(contract.id)}
          className="btn-primary w-full"
        >
          Accept Contract
        </button>
      )}
      {status === 'active' && onFulfill && isComplete && (
        <button
          onClick={() => onFulfill(contract.id)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <CheckCircle className="w-4 h-4" />
          Fulfill Contract
        </button>
      )}
    </div>
  );
};

export default Contracts;
