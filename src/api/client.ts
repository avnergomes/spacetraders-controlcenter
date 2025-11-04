import axios, { AxiosInstance } from 'axios';
import type {
  Agent,
  Ship,
  Contract,
  Waypoint,
  System,
  Market,
  Faction,
  ApiResponse,
  Survey,
  Extraction,
} from '../types';

const BASE_URL = 'https://api.spacetraders.io/v2';

class SpaceTradersAPI {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('spacetraders_token');
      if (this.token) {
        this.setAuthToken(this.token);
      }
    }
  }

  setAuthToken(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('spacetraders_token', token);
    }
  }

  clearAuthToken() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
    if (typeof window !== 'undefined') {
      localStorage.removeItem('spacetraders_token');
    }
  }

  // Agent endpoints
  async registerAgent(symbol: string, faction: string) {
    const response = await this.client.post<ApiResponse<{
      agent: Agent;
      contract: Contract;
      faction: Faction;
      ship: Ship;
      token: string;
    }>>('/register', {
      symbol,
      faction,
    });
    this.setAuthToken(response.data.data.token);
    return response.data.data;
  }

  async getMyAgent(): Promise<Agent> {
    const response = await this.client.get<ApiResponse<Agent>>('/my/agent');
    return response.data.data;
  }

  // Fleet endpoints
  async getMyShips(): Promise<Ship[]> {
    const response = await this.client.get<ApiResponse<Ship[]>>('/my/ships');
    return response.data.data;
  }

  async getShip(shipSymbol: string): Promise<Ship> {
    const response = await this.client.get<ApiResponse<Ship>>(`/my/ships/${shipSymbol}`);
    return response.data.data;
  }

  async purchaseShip(shipType: string, waypointSymbol: string): Promise<{ agent: Agent; ship: Ship; transaction: any }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; ship: Ship; transaction: any }>>('/my/ships', {
      shipType,
      waypointSymbol,
    });
    return response.data.data;
  }

  // Navigation endpoints
  async orbitShip(shipSymbol: string): Promise<ShipNav> {
    const response = await this.client.post<ApiResponse<{ nav: any }>>(`/my/ships/${shipSymbol}/orbit`);
    return response.data.data.nav;
  }

  async dockShip(shipSymbol: string): Promise<any> {
    const response = await this.client.post<ApiResponse<{ nav: any }>>(`/my/ships/${shipSymbol}/dock`);
    return response.data.data.nav;
  }

  async navigateShip(shipSymbol: string, waypointSymbol: string): Promise<{ fuel: any; nav: any }> {
    const response = await this.client.post<ApiResponse<{ fuel: any; nav: any }>>(`/my/ships/${shipSymbol}/navigate`, {
      waypointSymbol,
    });
    return response.data.data;
  }

  async setFlightMode(shipSymbol: string, flightMode: 'DRIFT' | 'STEALTH' | 'CRUISE' | 'BURN'): Promise<any> {
    const response = await this.client.patch<ApiResponse<{ nav: any }>>(`/my/ships/${shipSymbol}/nav`, {
      flightMode,
    });
    return response.data.data;
  }

  async warpShip(shipSymbol: string, waypointSymbol: string): Promise<{ fuel: any; nav: any }> {
    const response = await this.client.post<ApiResponse<{ fuel: any; nav: any }>>(`/my/ships/${shipSymbol}/warp`, {
      waypointSymbol,
    });
    return response.data.data;
  }

  async jumpShip(shipSymbol: string, waypointSymbol: string): Promise<{ cooldown: any; nav: any; transaction: any }> {
    const response = await this.client.post<ApiResponse<{ cooldown: any; nav: any; transaction: any }>>(`/my/ships/${shipSymbol}/jump`, {
      waypointSymbol,
    });
    return response.data.data;
  }

  // Mining & Extraction
  async extractResources(shipSymbol: string, survey?: Survey): Promise<{ cooldown: any; extraction: Extraction; cargo: any }> {
    const response = await this.client.post<ApiResponse<{ cooldown: any; extraction: Extraction; cargo: any }>>(
      `/my/ships/${shipSymbol}/extract`,
      survey ? { survey } : {}
    );
    return response.data.data;
  }

  async createSurvey(shipSymbol: string): Promise<{ cooldown: any; surveys: Survey[] }> {
    const response = await this.client.post<ApiResponse<{ cooldown: any; surveys: Survey[] }>>(`/my/ships/${shipSymbol}/survey`);
    return response.data.data;
  }

  async siphonResources(shipSymbol: string): Promise<{ cooldown: any; siphon: any; cargo: any }> {
    const response = await this.client.post<ApiResponse<{ cooldown: any; siphon: any; cargo: any }>>(`/my/ships/${shipSymbol}/siphon`);
    return response.data.data;
  }

  // Cargo & Trading
  async sellCargo(shipSymbol: string, symbol: string, units: number): Promise<{ agent: Agent; cargo: any; transaction: any }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; cargo: any; transaction: any }>>(`/my/ships/${shipSymbol}/sell`, {
      symbol,
      units,
    });
    return response.data.data;
  }

  async purchaseCargo(shipSymbol: string, symbol: string, units: number): Promise<{ agent: Agent; cargo: any; transaction: any }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; cargo: any; transaction: any }>>(`/my/ships/${shipSymbol}/purchase`, {
      symbol,
      units,
    });
    return response.data.data;
  }

  async transferCargo(shipSymbol: string, tradeSymbol: string, units: number, destinationShipSymbol: string): Promise<{ cargo: any }> {
    const response = await this.client.post<ApiResponse<{ cargo: any }>>(`/my/ships/${shipSymbol}/transfer`, {
      tradeSymbol,
      units,
      shipSymbol: destinationShipSymbol,
    });
    return response.data.data;
  }

  async jettisonCargo(shipSymbol: string, symbol: string, units: number): Promise<{ cargo: any }> {
    const response = await this.client.post<ApiResponse<{ cargo: any }>>(`/my/ships/${shipSymbol}/jettison`, {
      symbol,
      units,
    });
    return response.data.data;
  }

  // Refueling
  async refuelShip(shipSymbol: string, units?: number, fromCargo?: boolean): Promise<{ agent: Agent; fuel: any; transaction: any }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; fuel: any; transaction: any }>>(`/my/ships/${shipSymbol}/refuel`, {
      units,
      fromCargo,
    });
    return response.data.data;
  }

  // Contract endpoints
  async getContracts(): Promise<Contract[]> {
    const response = await this.client.get<ApiResponse<Contract[]>>('/my/contracts');
    return response.data.data;
  }

  async getContract(contractId: string): Promise<Contract> {
    const response = await this.client.get<ApiResponse<Contract>>(`/my/contracts/${contractId}`);
    return response.data.data;
  }

  async acceptContract(contractId: string): Promise<{ agent: Agent; contract: Contract }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; contract: Contract }>>(`/my/contracts/${contractId}/accept`);
    return response.data.data;
  }

  async deliverContract(contractId: string, shipSymbol: string, tradeSymbol: string, units: number): Promise<{ contract: Contract; cargo: any }> {
    const response = await this.client.post<ApiResponse<{ contract: Contract; cargo: any }>>(`/my/contracts/${contractId}/deliver`, {
      shipSymbol,
      tradeSymbol,
      units,
    });
    return response.data.data;
  }

  async fulfillContract(contractId: string): Promise<{ agent: Agent; contract: Contract }> {
    const response = await this.client.post<ApiResponse<{ agent: Agent; contract: Contract }>>(`/my/contracts/${contractId}/fulfill`);
    return response.data.data;
  }

  // Systems endpoints
  async getSystems(page = 1, limit = 20): Promise<{ data: System[]; meta: any }> {
    const response = await this.client.get<ApiResponse<System[]>>('/systems', {
      params: { page, limit },
    });
    return { data: response.data.data, meta: response.data.meta };
  }

  async getSystem(systemSymbol: string): Promise<System> {
    const response = await this.client.get<ApiResponse<System>>(`/systems/${systemSymbol}`);
    return response.data.data;
  }

  async getWaypoints(systemSymbol: string, page = 1, limit = 20, traits?: string): Promise<{ data: Waypoint[]; meta: any }> {
    const response = await this.client.get<ApiResponse<Waypoint[]>>(`/systems/${systemSymbol}/waypoints`, {
      params: { page, limit, traits },
    });
    return { data: response.data.data, meta: response.data.meta };
  }

  async getWaypoint(systemSymbol: string, waypointSymbol: string): Promise<Waypoint> {
    const response = await this.client.get<ApiResponse<Waypoint>>(`/systems/${systemSymbol}/waypoints/${waypointSymbol}`);
    return response.data.data;
  }

  async getMarket(systemSymbol: string, waypointSymbol: string): Promise<Market> {
    const response = await this.client.get<ApiResponse<Market>>(`/systems/${systemSymbol}/waypoints/${waypointSymbol}/market`);
    return response.data.data;
  }

  async getShipyard(systemSymbol: string, waypointSymbol: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/systems/${systemSymbol}/waypoints/${waypointSymbol}/shipyard`);
    return response.data.data;
  }

  async getJumpGate(systemSymbol: string, waypointSymbol: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/systems/${systemSymbol}/waypoints/${waypointSymbol}/jump-gate`);
    return response.data.data;
  }

  // Factions
  async getFactions(page = 1, limit = 20): Promise<{ data: Faction[]; meta: any }> {
    const response = await this.client.get<ApiResponse<Faction[]>>('/factions', {
      params: { page, limit },
    });
    return { data: response.data.data, meta: response.data.meta };
  }

  async getFaction(factionSymbol: string): Promise<Faction> {
    const response = await this.client.get<ApiResponse<Faction>>(`/factions/${factionSymbol}`);
    return response.data.data;
  }

  // Status
  async getStatus(): Promise<any> {
    const response = await this.client.get('/');
    return response.data;
  }
}

export const api = new SpaceTradersAPI();
export default api;
