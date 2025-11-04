import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Rocket, 
  ShoppingCart, 
  FileText, 
  Map, 
  Navigation as NavigationIcon,
  Menu,
  LogOut,
  Coins
} from 'lucide-react';
import { useStore } from '../store';
import { useAgent } from '../hooks/useSpaceTraders';
import { api } from '../api/client';
import { formatCredits } from '../utils/helpers';

const Layout = () => {
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar, clearAuth } = useStore();
  const { data: agent } = useAgent();

  const handleLogout = () => {
    api.clearAuthToken();
    clearAuth();
    navigate('/login');
  };

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/fleet', icon: Rocket, label: 'Fleet' },
    { to: '/markets', icon: ShoppingCart, label: 'Markets' },
    { to: '/contracts', icon: FileText, label: 'Contracts' },
    { to: '/systems', icon: Map, label: 'Systems' },
    { to: '/navigation', icon: NavigationIcon, label: 'Navigation' },
  ];

  return (
    <div className="flex h-screen bg-space-dark">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-space-blue border-r border-gray-700 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-700">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-space-accent">SpaceTraders</h1>
          )}
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-700 rounded transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-space-accent text-white'
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Agent info */}
        {agent && (
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-space-accent rounded-full flex items-center justify-center">
                <span className="text-lg font-bold">
                  {agent.symbol.charAt(0)}
                </span>
              </div>
              {sidebarOpen && (
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold truncate">
                    {agent.symbol}
                  </div>
                  <div className="text-xs text-gray-400 flex items-center gap-1">
                    <Coins className="w-3 h-3" />
                    {formatCredits(agent.credits)}
                  </div>
                </div>
              )}
            </div>
            {sidebarOpen && (
              <button
                onClick={handleLogout}
                className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors text-sm"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            )}
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
