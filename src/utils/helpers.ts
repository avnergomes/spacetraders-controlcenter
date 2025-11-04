// Format numbers with thousands separators
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

// Format credits with currency symbol
export const formatCredits = (credits: number): string => {
  return `₡${formatNumber(credits)}`;
};

// Calculate distance between two waypoints
export const calculateDistance = (
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number => {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
};

// Calculate fuel needed for travel
export const calculateFuelNeeded = (
  distance: number,
  flightMode: 'DRIFT' | 'STEALTH' | 'CRUISE' | 'BURN' = 'CRUISE'
): number => {
  const baseFuel = Math.ceil(distance);
  switch (flightMode) {
    case 'DRIFT':
      return 0;
    case 'STEALTH':
      return Math.ceil(baseFuel * 0.3);
    case 'CRUISE':
      return baseFuel;
    case 'BURN':
      return baseFuel * 2;
    default:
      return baseFuel;
  }
};

// Calculate travel time based on distance and flight mode
export const calculateTravelTime = (
  distance: number,
  speed: number,
  flightMode: 'DRIFT' | 'STEALTH' | 'CRUISE' | 'BURN' = 'CRUISE'
): number => {
  let multiplier = 1;
  switch (flightMode) {
    case 'DRIFT':
      multiplier = 2.5;
      break;
    case 'STEALTH':
      multiplier = 1.5;
      break;
    case 'CRUISE':
      multiplier = 1;
      break;
    case 'BURN':
      multiplier = 0.5;
      break;
  }
  
  const baseTime = Math.max(1, Math.round((distance / speed) * 15));
  return Math.round(baseTime * multiplier);
};

// Format duration in seconds to human readable format
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

// Format ISO date to relative time
export const formatRelativeTime = (isoDate: string): string => {
  const date = new Date(isoDate);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  
  if (diffSecs < 0) {
    return 'Past';
  }
  
  return formatDuration(diffSecs);
};

// Calculate percentage
export const calculatePercentage = (current: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((current / total) * 100);
};

// Get color based on percentage
export const getPercentageColor = (percentage: number): string => {
  if (percentage >= 75) return 'text-green-400';
  if (percentage >= 50) return 'text-yellow-400';
  if (percentage >= 25) return 'text-orange-400';
  return 'text-red-400';
};

// Get ship role color
export const getShipRoleColor = (role: string): string => {
  const colors: Record<string, string> = {
    COMMAND: 'badge-info',
    EXPLORER: 'badge-success',
    HAULER: 'badge-warning',
    INTERCEPTOR: 'badge-danger',
    EXCAVATOR: 'badge-info',
    TRANSPORT: 'badge-warning',
    REPAIR: 'badge-success',
    SURVEYOR: 'badge-info',
    REFINERY: 'badge-warning',
    PATROL: 'badge-danger',
    SATELLITE: 'badge-info',
  };
  return colors[role] || 'badge-info';
};

// Get waypoint type icon
export const getWaypointTypeIcon = (type: string): string => {
  const icons: Record<string, string> = {
    PLANET: '🌍',
    GAS_GIANT: '🪐',
    MOON: '🌙',
    ORBITAL_STATION: '🛰️',
    JUMP_GATE: '🌀',
    ASTEROID_FIELD: '🪨',
    ASTEROID: '☄️',
    ENGINEERED_ASTEROID: '⚙️',
    ASTEROID_BASE: '🏭',
    NEBULA: '🌌',
    DEBRIS_FIELD: '💥',
    GRAVITY_WELL: '⚫',
    FUEL_STATION: '⛽',
  };
  return icons[type] || '📍';
};

// Check if cooldown is active
export const isCooldownActive = (expiration?: string): boolean => {
  if (!expiration) return false;
  return new Date(expiration).getTime() > Date.now();
};

// Get remaining cooldown time in seconds
export const getRemainingCooldown = (expiration?: string): number => {
  if (!expiration) return 0;
  const remaining = Math.max(0, Math.floor((new Date(expiration).getTime() - Date.now()) / 1000));
  return remaining;
};

// Calculate profit margin
export const calculateProfitMargin = (buyPrice: number, sellPrice: number): number => {
  if (buyPrice === 0) return 0;
  return Math.round(((sellPrice - buyPrice) / buyPrice) * 100);
};

// Find best trade route (simplified version)
export const findBestTrades = (markets: any[], cargoCapacity: number) => {
  const trades: any[] = [];
  
  markets.forEach((market) => {
    if (market.tradeGoods) {
      market.tradeGoods.forEach((good: any) => {
        if (good.type === 'EXPORT' && good.supply !== 'SCARCE') {
          trades.push({
            symbol: good.symbol,
            market: market.symbol,
            buyPrice: good.purchasePrice,
            sellPrice: good.sellPrice,
            margin: calculateProfitMargin(good.purchasePrice, good.sellPrice),
            supply: good.supply,
          });
        }
      });
    }
  });
  
  return trades.sort((a, b) => b.margin - a.margin).slice(0, 10);
};
