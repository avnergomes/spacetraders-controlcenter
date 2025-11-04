import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Agent, Ship, Contract } from '../types';

interface AppState {
  // Auth
  isAuthenticated: boolean;
  token: string | null;
  
  // Agent data
  agent: Agent | null;
  
  // Fleet data
  ships: Ship[];
  selectedShip: Ship | null;
  
  // Contracts
  contracts: Contract[];
  
  // UI state
  sidebarOpen: boolean;
  
  // Actions
  setAuth: (token: string, agent: Agent) => void;
  clearAuth: () => void;
  setAgent: (agent: Agent) => void;
  setShips: (ships: Ship[]) => void;
  setSelectedShip: (ship: Ship | null) => void;
  updateShip: (shipSymbol: string, updates: Partial<Ship>) => void;
  setContracts: (contracts: Contract[]) => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      isAuthenticated: false,
      token: null,
      agent: null,
      ships: [],
      selectedShip: null,
      contracts: [],
      sidebarOpen: true,
      
      // Actions
      setAuth: (token, agent) => {
        set({
          isAuthenticated: true,
          token,
          agent,
        });
      },
      
      clearAuth: () => {
        set({
          isAuthenticated: false,
          token: null,
          agent: null,
          ships: [],
          selectedShip: null,
          contracts: [],
        });
      },
      
      setAgent: (agent) => {
        set({ agent });
      },
      
      setShips: (ships) => {
        set({ ships });
      },
      
      setSelectedShip: (ship) => {
        set({ selectedShip: ship });
      },
      
      updateShip: (shipSymbol, updates) => {
        const ships = get().ships;
        const updatedShips = ships.map((ship) =>
          ship.symbol === shipSymbol ? { ...ship, ...updates } : ship
        );
        set({ ships: updatedShips });
        
        // Update selected ship if it's the one being updated
        const selectedShip = get().selectedShip;
        if (selectedShip && selectedShip.symbol === shipSymbol) {
          set({ selectedShip: { ...selectedShip, ...updates } });
        }
      },
      
      setContracts: (contracts) => {
        set({ contracts });
      },
      
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },
    }),
    {
      name: 'spacetraders-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);
