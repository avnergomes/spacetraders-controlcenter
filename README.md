# SpaceTraders Control Center 🚀

A comprehensive Streamlit-based control center for managing your SpaceTraders fleet, contracts, trading, and exploration operations.

## Features

### 📊 Dashboard
- Real-time agent statistics and credits
- Fleet status overview (in transit, docked, orbiting)
- Contract status tracking
- Fleet composition analysis with charts
- Cargo utilization monitoring

### 🚢 Fleet Management
- Complete ship control interface
- Mission shortcuts for quick navigation (mining, delivery, warehouse)
- Advanced filtering by role and status
- Ship operations:
  - Orbit/Dock controls
  - Navigation with ETA tracking
  - Refueling
  - Resource extraction with survey support
  - Cargo management (buy/sell/jettison)
- Real-time cargo tracking and progress bars
- Route planner with logistics analysis
- Survey creation and management

### 📜 Contract Management
- View all contracts (active, pending, fulfilled)
- Accept contracts with one click
- Track delivery progress with visual indicators
- Quick delivery interface
- Payment and deadline tracking

### 🗺️ System Explorer
- Browse systems and waypoints
- Filter by traits (MARKETPLACE, SHIPYARD, etc.)
- Interactive system maps
- Waypoint type analysis
- Trait statistics
- Export waypoint data as JSON

### 💰 Market Analysis
- Real-time market data
- Price comparison charts
- Profit margin calculations
- Export/Import/Exchange categorization
- Transaction history
- Market data export

### 🏗️ Shipyard Browser
- Find shipyards in any system
- View available ships
- Purchase new ships
- Transaction history
- Ship specifications

### 🔧 Maintenance & Outfitting
- Ship repair interface
- Module and mount management
- Cargo transfer between ships
- Ship scrapping
- Detailed ship component information

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spacetraders-controlcenter.git
cd spacetraders-controlcenter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## Configuration

### Getting Your API Token

1. Visit [spacetraders.io](https://spacetraders.io)
2. Create a new agent or log in
3. Copy your bearer token
4. Paste it in the sidebar of the application

The token is stored only in your session and is never persisted to disk.

## Usage

### Quick Start

1. **Authentication**: Enter your SpaceTraders token in the sidebar
2. **Dashboard**: Overview of your fleet and operations
3. **Fleet**: Manage individual ships, set up navigation shortcuts
4. **Contracts**: Accept and track contract progress
5. **Explorer**: Navigate the universe and find waypoints
6. **Markets**: Analyze trading opportunities
7. **Shipyards**: Purchase new ships
8. **Maintenance**: Repair and upgrade your fleet

### Mission Shortcuts

Set up quick navigation targets in the Fleet tab:
- **Mining Waypoint**: Your primary mining location
- **Delivery Waypoint**: Main delivery/trading hub
- **Warehouse/Shipyard**: Maintenance and outfitting location

These shortcuts enable one-click navigation for all your ships.

### Best Practices

1. **Set Mission Shortcuts Early**: Configure your mining, delivery, and warehouse shortcuts for efficient fleet management
2. **Use Surveys**: Create surveys before mining for better yields
3. **Monitor Fuel**: Keep track of fuel levels to avoid being stranded
4. **Check Markets**: Compare prices before buying or selling
5. **Accept Contracts**: Complete contracts for reputation and credits
6. **Regular Maintenance**: Repair ships to maintain performance

## API Integration

This application integrates with the SpaceTraders API v2:
- Base URL: `https://api.spacetraders.io/v2`
- Authentication: Bearer token
- Rate limiting: Automatic retry with exponential backoff
- Caching: Smart caching for read operations

### Endpoints Used

- `/my/agent` - Agent information
- `/my/ships` - Fleet management
- `/my/contracts` - Contract operations
- `/systems` - System exploration
- `/systems/{system}/waypoints` - Waypoint data
- `/systems/{system}/waypoints/{waypoint}/market` - Market data
- `/systems/{system}/waypoints/{waypoint}/shipyard` - Shipyard data
- Various ship action endpoints (orbit, dock, navigate, extract, etc.)

## Technologies

- **Streamlit**: Web application framework
- **Requests**: HTTP client for API calls
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **Python 3.8+**: Core language

## Features in Detail

### Caching Strategy

The application uses Streamlit's caching to optimize performance:
- Agent data: 60s TTL
- Ship data: 30s TTL
- Contract data: 60s TTL
- System data: 300s TTL
- Market data: 120s TTL

### Error Handling

- Automatic retry with exponential backoff
- Rate limit detection and handling
- Cooldown period parsing from errors
- User-friendly error messages

### Real-time Updates

- Travel progress tracking with ETA
- Cargo utilization monitoring
- Contract delivery progress
- Fuel level tracking

## Development

### Project Structure

```
spacetraders-controlcenter/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding New Features

1. Add new functions in the appropriate section of `app.py`
2. Use caching for read operations
3. Clear cache after write operations
4. Follow the existing UI patterns with Streamlit components

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

**Token not working**
- Ensure you copied the complete token
- Check if your agent is still active
- Verify you're using the correct API endpoint

**Rate limiting**
- The app automatically handles rate limits
- Wait for the cooldown period if shown
- Reduce the frequency of manual refreshes

**Caching issues**
- Use the Refresh buttons to clear cache
- Restart the application if needed
- Check your internet connection

**Missing data**
- Some data requires ships at specific locations
- Markets require visiting with a ship
- Shipyards need proximity for full details

## Security

- Tokens are stored only in session state
- No data is persisted to disk
- All API calls use HTTPS
- No third-party analytics or tracking

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- SpaceTraders team for the amazing API game
- Streamlit for the excellent web framework
- The SpaceTraders community for feedback and ideas

## Links

- [SpaceTraders Website](https://spacetraders.io)
- [API Documentation](https://docs.spacetraders.io)
- [Discord Community](https://discord.gg/spacetraders)
- [GitHub Repository](https://github.com/yourusername/spacetraders-controlcenter)

## Changelog

### Version 2.0 (Current)
- Complete rewrite with improved architecture
- Added mission shortcuts for quick navigation
- Enhanced route planner with logistics analysis
- Improved market analysis with profit calculations
- Added cargo transfer between ships
- Better error handling and user feedback
- Interactive charts and visualizations
- Survey management system
- Real-time travel progress tracking

### Version 1.0
- Initial release
- Basic fleet management
- Contract tracking
- Market browsing

---

Built with ❤️ for the SpaceTraders community
