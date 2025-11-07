# SpaceTraders Control Center Enhanced 🚀

A comprehensive, modern control center for the SpaceTraders API game. Manage your fleet, automate trading routes, explore the universe, and maximize your profits with an intuitive web interface.

## 🌟 Features

### Core Features
- **🚢 Fleet Management**: Real-time monitoring and control of all your ships
- **📊 Market Analytics**: Advanced market analysis with price history and predictions
- **🗺️ Interactive Map**: Visual navigation system with route planning
- **📜 Contract Management**: Track and optimize contract fulfillment
- **💰 Trading Automation**: Automated trading routes with profit optimization
- **⛏️ Mining Operations**: Automated asteroid mining with resource tracking
- **🛡️ Ship Upgrades**: Manage ship modules and upgrades
- **📈 Performance Dashboard**: Real-time metrics and profit tracking
- **🏛️ Faction Relations**: Monitor and manage faction reputation
- **🔔 Alert System**: Notifications for important events and opportunities

### Advanced Features
- **AI-Powered Trading**: Machine learning algorithms for optimal trade routes
- **Fleet Coordination**: Multi-ship mission planning and execution
- **Market Predictions**: Price forecasting based on historical data
- **Resource Management**: Inventory optimization across your fleet
- **Mission Planner**: Automated mission execution with priority queuing
- **Data Export**: Export game data for external analysis
- **Dark Mode**: Full dark theme support for late-night trading
- **Mobile Responsive**: Full functionality on mobile devices

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- A SpaceTraders API token (get one at [spacetraders.io](https://spacetraders.io))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/avnergomes/spacetraders-controlcenter-enhanced.git
cd spacetraders-controlcenter-enhanced
```

2. Install dependencies:
```bash
npm run install:all
```

3. Configure your API token:
```bash
# Create .env file in the server directory
cd server
cp .env.example .env
# Edit .env and add your SpaceTraders API token
```

4. Start the application:
```bash
npm run dev
```

5. Open your browser and navigate to `http://localhost:3000`

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **React 18** with TypeScript for type safety
- **Redux Toolkit** for state management
- **Material-UI** for modern UI components
- **Recharts** for data visualization
- **Socket.io** for real-time updates
- **React Query** for efficient data fetching

### Backend (Node.js + Express)
- **Express.js** server with TypeScript
- **Socket.io** for WebSocket connections
- **Redis** for caching and session management
- **PostgreSQL** for data persistence
- **Bull** for job queuing
- **Winston** for logging

## 📱 Screenshots

### Dashboard
The main dashboard provides an overview of your fleet, current balance, active contracts, and real-time market opportunities.

### Fleet Management
Detailed view of each ship with cargo, fuel status, navigation controls, and quick actions.

### Market Analysis
Advanced charts showing price trends, trade opportunities, and profit calculations.

### Navigation Map
Interactive galaxy map with route planning, waypoint information, and travel time estimates.

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the server directory:

```env
# SpaceTraders API
SPACETRADERS_TOKEN=your_api_token_here
SPACETRADERS_API_URL=https://api.spacetraders.io/v2

# Server Configuration
PORT=5000
NODE_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/spacetraders

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here

# Features
ENABLE_AUTO_TRADING=true
ENABLE_AUTO_MINING=true
ENABLE_NOTIFICATIONS=true
```

## 🔧 API Integration

The application integrates with all SpaceTraders API endpoints:

- **Agent**: Registration and agent info
- **Contracts**: List, accept, and fulfill contracts
- **Factions**: View faction information
- **Fleet**: Ship management and navigation
- **Systems**: Explore systems and waypoints
- **Markets**: Trade goods and view prices

## 📊 Trading Strategies

The control center includes several automated trading strategies:

1. **Arbitrage Trading**: Find price differences between markets
2. **Supply Chain**: Optimize multi-hop trade routes
3. **Contract Focus**: Prioritize contract fulfillment
4. **Market Maker**: Buy low, sell high based on historical data
5. **Resource Hoarding**: Stockpile valuable resources

## 🚀 Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### Manual Deployment

1. Build the frontend:
```bash
cd client
npm run build
```

2. Start the production server:
```bash
NODE_ENV=production npm start
```

### Deployment Options
- **Heroku**: One-click deployment with Heroku button
- **Vercel**: Frontend deployment with serverless functions
- **DigitalOcean**: App Platform deployment
- **AWS**: EC2 or ECS deployment

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a pull request

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Trading Strategies](docs/TRADING_STRATEGIES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🐛 Known Issues

- Rate limiting may affect real-time updates during heavy trading
- Large fleets (50+ ships) may experience performance issues
- Some market data may be delayed by up to 60 seconds

## 🔮 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced AI trading algorithms
- [ ] Multi-account support
- [ ] Plugin system for custom strategies
- [ ] Voice commands integration
- [ ] VR interface for ship navigation
- [ ] Blockchain integration for asset trading
- [ ] Community marketplace for strategies

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- SpaceTraders API team for creating this amazing game
- All contributors and beta testers
- The SpaceTraders community for feedback and suggestions

## 💬 Support

- Discord: [SpaceTraders Discord](https://discord.gg/spacetraders)
- GitHub Issues: [Report bugs](https://github.com/avnergomes/spacetraders-controlcenter-enhanced/issues)
- Email: support@spacetraders-cc.com

---

Built with ❤️ by the SpaceTraders community
