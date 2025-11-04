import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { useStore } from '../store';

// Agent hooks
export const useAgent = () => {
  const setAgent = useStore((state) => state.setAgent);
  
  return useQuery({
    queryKey: ['agent'],
    queryFn: async () => {
      const agent = await api.getMyAgent();
      setAgent(agent);
      return agent;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  });
};

// Fleet hooks
export const useShips = () => {
  const setShips = useStore((state) => state.setShips);
  
  return useQuery({
    queryKey: ['ships'],
    queryFn: async () => {
      const ships = await api.getMyShips();
      setShips(ships);
      return ships;
    },
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

export const useShip = (shipSymbol: string) => {
  return useQuery({
    queryKey: ['ship', shipSymbol],
    queryFn: () => api.getShip(shipSymbol),
    enabled: !!shipSymbol,
  });
};

// Navigation mutations
export const useNavigateShip = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ shipSymbol, waypointSymbol }: { shipSymbol: string; waypointSymbol: string }) =>
      api.navigateShip(shipSymbol, waypointSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

export const useDockShip = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (shipSymbol: string) => api.dockShip(shipSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
    },
  });
};

export const useOrbitShip = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (shipSymbol: string) => api.orbitShip(shipSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
    },
  });
};

// Mining mutations
export const useExtractResources = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (shipSymbol: string) => api.extractResources(shipSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

export const useCreateSurvey = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (shipSymbol: string) => api.createSurvey(shipSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
    },
  });
};

// Trading mutations
export const useSellCargo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ shipSymbol, symbol, units }: { shipSymbol: string; symbol: string; units: number }) =>
      api.sellCargo(shipSymbol, symbol, units),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

export const usePurchaseCargo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ shipSymbol, symbol, units }: { shipSymbol: string; symbol: string; units: number }) =>
      api.purchaseCargo(shipSymbol, symbol, units),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

export const useRefuelShip = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (shipSymbol: string) => api.refuelShip(shipSymbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ships'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

// Contract hooks
export const useContracts = () => {
  const setContracts = useStore((state) => state.setContracts);
  
  return useQuery({
    queryKey: ['contracts'],
    queryFn: async () => {
      const contracts = await api.getContracts();
      setContracts(contracts);
      return contracts;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export const useAcceptContract = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (contractId: string) => api.acceptContract(contractId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

export const useDeliverContract = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({
      contractId,
      shipSymbol,
      tradeSymbol,
      units,
    }: {
      contractId: string;
      shipSymbol: string;
      tradeSymbol: string;
      units: number;
    }) => api.deliverContract(contractId, shipSymbol, tradeSymbol, units),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      queryClient.invalidateQueries({ queryKey: ['ships'] });
    },
  });
};

export const useFulfillContract = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (contractId: string) => api.fulfillContract(contractId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      queryClient.invalidateQueries({ queryKey: ['agent'] });
    },
  });
};

// Systems and waypoints
export const useWaypoints = (systemSymbol: string, traits?: string) => {
  return useQuery({
    queryKey: ['waypoints', systemSymbol, traits],
    queryFn: () => api.getWaypoints(systemSymbol, 1, 50, traits),
    enabled: !!systemSymbol,
  });
};

export const useMarket = (systemSymbol: string, waypointSymbol: string) => {
  return useQuery({
    queryKey: ['market', systemSymbol, waypointSymbol],
    queryFn: () => api.getMarket(systemSymbol, waypointSymbol),
    enabled: !!systemSymbol && !!waypointSymbol,
    retry: false, // Don't retry if waypoint doesn't have a market
  });
};

export const useShipyard = (systemSymbol: string, waypointSymbol: string) => {
  return useQuery({
    queryKey: ['shipyard', systemSymbol, waypointSymbol],
    queryFn: () => api.getShipyard(systemSymbol, waypointSymbol),
    enabled: !!systemSymbol && !!waypointSymbol,
    retry: false,
  });
};
