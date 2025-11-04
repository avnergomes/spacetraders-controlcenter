// Core API Types based on SpaceTraders API v2

export interface Agent {
  accountId: string;
  symbol: string;
  headquarters: string;
  credits: number;
  startingFaction: string;
  shipCount: number;
}

export interface Ship {
  symbol: string;
  registration: {
    name: string;
    factionSymbol: string;
    role: ShipRole;
  };
  nav: ShipNav;
  crew: ShipCrew;
  frame: ShipFrame;
  reactor: ShipReactor;
  engine: ShipEngine;
  cooldown: Cooldown;
  modules: ShipModule[];
  mounts: ShipMount[];
  cargo: ShipCargo;
  fuel: ShipFuel;
}

export type ShipRole = 'COMMAND' | 'EXPLORER' | 'HAULER' | 'INTERCEPTOR' | 'EXCAVATOR' | 'TRANSPORT' | 'REPAIR' | 'SURVEYOR' | 'REFINERY' | 'PATROL' | 'SATELLITE';

export interface ShipNav {
  systemSymbol: string;
  waypointSymbol: string;
  route: ShipNavRoute;
  status: 'IN_TRANSIT' | 'IN_ORBIT' | 'DOCKED';
  flightMode: 'DRIFT' | 'STEALTH' | 'CRUISE' | 'BURN';
}

export interface ShipNavRoute {
  destination: Waypoint;
  origin: Waypoint;
  departureTime: string;
  arrival: string;
}

export interface ShipCrew {
  current: number;
  required: number;
  capacity: number;
  rotation: 'STRICT' | 'RELAXED';
  morale: number;
  wages: number;
}

export interface ShipFrame {
  symbol: string;
  name: string;
  description: string;
  condition: number;
  integrity: number;
  moduleSlots: number;
  mountingPoints: number;
  fuelCapacity: number;
  requirements: ShipRequirements;
}

export interface ShipReactor {
  symbol: string;
  name: string;
  description: string;
  condition: number;
  integrity: number;
  powerOutput: number;
  requirements: ShipRequirements;
}

export interface ShipEngine {
  symbol: string;
  name: string;
  description: string;
  condition: number;
  integrity: number;
  speed: number;
  requirements: ShipRequirements;
}

export interface ShipModule {
  symbol: string;
  name: string;
  description: string;
  capacity?: number;
  range?: number;
  requirements: ShipRequirements;
}

export interface ShipMount {
  symbol: string;
  name: string;
  description: string;
  strength?: number;
  deposits?: string[];
  requirements: ShipRequirements;
}

export interface ShipRequirements {
  power?: number;
  crew?: number;
  slots?: number;
}

export interface ShipCargo {
  capacity: number;
  units: number;
  inventory: CargoItem[];
}

export interface CargoItem {
  symbol: string;
  name: string;
  description: string;
  units: number;
}

export interface ShipFuel {
  current: number;
  capacity: number;
  consumed?: {
    amount: number;
    timestamp: string;
  };
}

export interface Cooldown {
  shipSymbol: string;
  totalSeconds: number;
  remainingSeconds: number;
  expiration?: string;
}

export interface Contract {
  id: string;
  factionSymbol: string;
  type: 'PROCUREMENT' | 'TRANSPORT' | 'SHUTTLE';
  terms: ContractTerms;
  accepted: boolean;
  fulfilled: boolean;
  expiration: string;
  deadlineToAccept: string;
}

export interface ContractTerms {
  deadline: string;
  payment: ContractPayment;
  deliver: ContractDeliverGood[];
}

export interface ContractPayment {
  onAccepted: number;
  onFulfilled: number;
}

export interface ContractDeliverGood {
  tradeSymbol: string;
  destinationSymbol: string;
  unitsRequired: number;
  unitsFulfilled: number;
}

export interface Waypoint {
  symbol: string;
  type: WaypointType;
  systemSymbol: string;
  x: number;
  y: number;
  orbitals: WaypointOrbital[];
  orbits?: string;
  faction?: WaypointFaction;
  traits: WaypointTrait[];
  modifiers?: WaypointModifier[];
  chart?: Chart;
  isUnderConstruction: boolean;
}

export type WaypointType = 
  | 'PLANET' 
  | 'GAS_GIANT' 
  | 'MOON' 
  | 'ORBITAL_STATION' 
  | 'JUMP_GATE' 
  | 'ASTEROID_FIELD' 
  | 'ASTEROID' 
  | 'ENGINEERED_ASTEROID' 
  | 'ASTEROID_BASE' 
  | 'NEBULA' 
  | 'DEBRIS_FIELD' 
  | 'GRAVITY_WELL' 
  | 'ARTIFICIAL_GRAVITY_WELL' 
  | 'FUEL_STATION';

export interface WaypointOrbital {
  symbol: string;
}

export interface WaypointFaction {
  symbol: string;
}

export interface WaypointTrait {
  symbol: string;
  name: string;
  description: string;
}

export interface WaypointModifier {
  symbol: string;
  name: string;
  description: string;
}

export interface Chart {
  waypointSymbol?: string;
  submittedBy?: string;
  submittedOn?: string;
}

export interface System {
  symbol: string;
  sectorSymbol: string;
  type: string;
  x: number;
  y: number;
  waypoints: Waypoint[];
  factions: Faction[];
}

export interface Faction {
  symbol: string;
  name: string;
  description: string;
  headquarters: string;
  traits: FactionTrait[];
  isRecruiting: boolean;
}

export interface FactionTrait {
  symbol: string;
  name: string;
  description: string;
}

export interface Market {
  symbol: string;
  exports: TradeGood[];
  imports: TradeGood[];
  exchange: TradeGood[];
  transactions?: MarketTransaction[];
  tradeGoods?: MarketTradeGood[];
}

export interface TradeGood {
  symbol: string;
  name: string;
  description: string;
}

export interface MarketTradeGood {
  symbol: string;
  type: 'EXPORT' | 'IMPORT' | 'EXCHANGE';
  tradeVolume: number;
  supply: 'SCARCE' | 'LIMITED' | 'MODERATE' | 'HIGH' | 'ABUNDANT';
  activity?: 'WEAK' | 'GROWING' | 'STRONG' | 'RESTRICTED';
  purchasePrice: number;
  sellPrice: number;
}

export interface MarketTransaction {
  waypointSymbol: string;
  shipSymbol: string;
  tradeSymbol: string;
  type: 'PURCHASE' | 'SELL';
  units: number;
  pricePerUnit: number;
  totalPrice: number;
  timestamp: string;
}

export interface Survey {
  signature: string;
  symbol: string;
  deposits: SurveyDeposit[];
  expiration: string;
  size: 'SMALL' | 'MODERATE' | 'LARGE';
}

export interface SurveyDeposit {
  symbol: string;
}

export interface Extraction {
  shipSymbol: string;
  yield: ExtractionYield;
}

export interface ExtractionYield {
  symbol: string;
  units: number;
}

export interface ApiResponse<T> {
  data: T;
  meta?: {
    total: number;
    page: number;
    limit: number;
  };
}
