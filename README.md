# SpaceTraders Control Center

A modern, feature-rich control panel for playing [SpaceTraders](https://spacetraders.io) - an API-based space trading game.

## 🚀 Features

### Core Functionality
- **Dashboard**: Real-time overview of your agent, fleet status, active contracts, and quick actions
- **Fleet Management**: Complete ship management with detailed views, cargo tracking, and fuel monitoring
- **Market System**: View marketplaces, trade goods, and find profitable trade routes
- **Contract Management**: Accept, track, and fulfill faction contracts
- **Systems Explorer**: Browse systems and discover waypoints
- **Navigation**: Plan routes, calculate fuel requirements, and navigate ships

### Advanced Features
- **Real-time Updates**: Auto-refreshing data every 5-30 seconds
- **Cooldown Tracking**: Visual cooldown timers for mining and other operations
- **Fuel Calculations**: Automatic fuel requirement calculations based on distance and flight mode
- **Cargo Management**: Track cargo capacity and manage inventory
- **Ship Controls**: Dock, orbit, refuel, mine, and trade - all from the UI
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Dark Theme**: Beautiful space-themed dark UI with custom styling

## 🛠️ Technology Stack

- **Frontend**: React 19 with TypeScript
- **Build Tool**: Vite for lightning-fast development
- **State Management**: Zustand with persistence
- **Data Fetching**: TanStack Query (React Query) for efficient API calls
- **Routing**: React Router v7
- **Styling**: TailwindCSS with custom space theme
- **Icons**: Lucide React
- **Charts**: Recharts for data visualization
- **API Client**: Axios for SpaceTraders API v2

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm

### Setup

1. **Clone/Download the project**
   ```bash
   cd spacetraders-controlcenter
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   Navigate to `http://localhost:3000`

## 🎮 Getting Started

### First Time Setup

1. **Register a New Agent**
   - Click "Register" on the login page
   - Choose an agent symbol (3-14 characters, uppercase, numbers, underscores, hyphens)
   - Select your starting faction
   - Save your API token securely!

2. **Or Login with Existing Token**
   - Click "Login" on the login page
   - Enter your SpaceTraders API token

### Basic Gameplay

1. **Dashboard**: View your agent stats and fleet overview
2. **Fleet**: Manage your ships, view details, and control operations
3. **Navigation**: Move ships between waypoints
4. **Mining**: Extract resources from asteroid fields
5. **Trading**: Buy low, sell high at different markets
6. **Contracts**: Accept and fulfill faction contracts for rewards

## 🎯 Key Features Explained

### Dashboard
- Real-time credits, fleet size, and contract tracking
- Quick access to all major features
- Fleet status overview showing docked, in-orbit, and in-transit ships
- Active contract progress tracking

### Fleet Management
- **Fleet View**: Grid of all ships with status, fuel, and cargo at a glance
- **Ship Detail**: Comprehensive ship information including:
  - Navigation controls (dock, orbit, navigate)
  - Resource management (fuel, cargo)
  - Mining operations
  - Ship specifications and condition
  - Crew information

### Navigation System
- Select ships and destinations
- Automatic distance calculation
- Fuel requirement estimation
- Travel time calculation based on ship speed and flight mode
- Visual feedback for insufficient fuel

### Market System
- Discover marketplaces in your current system
- View trade goods, prices, and supply levels
- Identify profitable trade opportunities

### Contract System
- View available, active, and completed contracts
- Track delivery progress
- Accept new contracts
- Fulfill completed contracts for rewards

## 🔧 Project Structure

```
spacetraders-controlcenter/
├── src/
│   ├── api/               # API client and endpoints
│   │   └── client.ts      # SpaceTraders API wrapper
│   ├── components/        # React components
│   │   ├── Dashboard/     # Dashboard view
│   │   ├── Fleet/         # Fleet management
│   │   ├── Markets/       # Market system
│   │   ├── Contracts/     # Contract management
│   │   ├── Systems/       # System explorer
│   │   ├── Navigation/    # Navigation interface
│   │   ├── Layout.tsx     # Main layout with sidebar
│   │   └── Login.tsx      # Authentication
│   ├── hooks/             # Custom React hooks
│   │   └── useSpaceTraders.ts
│   ├── store/             # Zustand state management
│   │   └── index.ts
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/             # Utility functions
│   │   └── helpers.ts
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
└── tailwind.config.js     # Tailwind config
```

## 🎨 Customization

### Theme Colors
Edit `tailwind.config.js` to customize the color scheme:
```js
colors: {
  'space-dark': '#0a0e1a',
  'space-blue': '#1a2332',
  'space-accent': '#3b82f6',
  'space-gold': '#fbbf24',
}
```

### API Refresh Intervals
Modify refresh rates in `src/hooks/useSpaceTraders.ts`:
- Agent data: 10 seconds
- Ships: 5 seconds
- Contracts: 30 seconds

## 📝 Development

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Type Checking
TypeScript is configured for strict mode. Run type checking with:
```bash
npx tsc --noEmit
```

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to authenticate"**
   - Check your API token is correct
   - Ensure you're using a valid SpaceTraders v2 token

2. **Ships not updating**
   - Check your internet connection
   - The app auto-refreshes every 5-30 seconds
   - Use the refresh button for immediate updates

3. **Can't navigate ship**
   - Ensure ship is not in transit
   - Check you have enough fuel
   - Ship must be in orbit to navigate

4. **Mining not working**
   - Ship must be in orbit at an asteroid field
   - Wait for cooldown to expire
   - Ensure cargo has space

## 🔗 Links

- [SpaceTraders Website](https://spacetraders.io)
- [SpaceTraders API Documentation](https://docs.spacetraders.io)
- [SpaceTraders Discord](https://discord.com/invite/jh6zurdWk5)
- [API GitHub](https://github.com/SpaceTradersAPI/api-docs)

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built for the [SpaceTraders](https://spacetraders.io) community
- Uses the SpaceTraders API v2
- Inspired by various community clients and tools

## 🚀 Future Enhancements

Potential features to add:
- Advanced route optimization
- Market price tracking and graphs
- Ship automation scripts
- Multi-agent management
- Faction diplomacy tracking
- System mapping visualization
- Trade route calculator
- Fleet automation
- Survey management
- Jump gate navigation
- Shipyard management
- Construction projects

---

**Happy Trading, Commander! 🚀**
