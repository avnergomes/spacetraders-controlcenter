import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Rocket, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { useStore } from '../store';

const Login = () => {
  const navigate = useNavigate();
  const setAuth = useStore((state) => state.setAuth);
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [token, setToken] = useState('');
  const [agentSymbol, setAgentSymbol] = useState('');
  const [faction, setFaction] = useState('COSMIC');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const factions = [
    { value: 'COSMIC', label: 'Cosmic Engineers', description: 'Masters of advanced technology' },
    { value: 'VOID', label: 'Voidfarers', description: 'Explorers of the unknown' },
    { value: 'GALACTIC', label: 'Galactic Alliance', description: 'United for peace and prosperity' },
    { value: 'QUANTUM', label: 'Quantum Federation', description: 'Pioneers of quantum mechanics' },
    { value: 'DOMINION', label: 'Star Dominion', description: 'Military powerhouse' },
    { value: 'ASTRO', label: 'Astro-Salvage Alliance', description: 'Salvagers and recyclers' },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      api.setAuthToken(token);
      const agent = await api.getMyAgent();
      setAuth(token, agent);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to authenticate. Please check your token.');
      api.clearAuthToken();
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await api.registerAgent(agentSymbol, faction);
      setAuth(data.token, data.agent);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to register. Please try a different agent symbol.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-space-dark via-space-blue to-space-dark p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-space-accent rounded-full flex items-center justify-center">
              <Rocket className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-white mb-2">SpaceTraders</h2>
          <p className="text-gray-400">Control Center</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 p-1 bg-gray-800 rounded-lg">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2 px-4 rounded-md transition-colors ${
              mode === 'login'
                ? 'bg-space-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 py-2 px-4 rounded-md transition-colors ${
              mode === 'register'
                ? 'bg-space-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {/* Forms */}
        <div className="card">
          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Authentication Token
                </label>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="input w-full"
                  placeholder="Enter your SpaceTraders token"
                  required
                />
                <p className="mt-2 text-xs text-gray-400">
                  Enter your existing SpaceTraders API token to access your account.
                </p>
              </div>

              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !token}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Authenticating...' : 'Login'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Agent Symbol
                </label>
                <input
                  type="text"
                  value={agentSymbol}
                  onChange={(e) => setAgentSymbol(e.target.value.toUpperCase())}
                  className="input w-full"
                  placeholder="AGENT_NAME"
                  pattern="[A-Z0-9_-]{3,14}"
                  required
                />
                <p className="mt-2 text-xs text-gray-400">
                  3-14 characters, uppercase letters, numbers, underscores, and hyphens only.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Starting Faction
                </label>
                <select
                  value={faction}
                  onChange={(e) => setFaction(e.target.value)}
                  className="input w-full"
                  required
                >
                  {factions.map((f) => (
                    <option key={f.value} value={f.value}>
                      {f.label} - {f.description}
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !agentSymbol}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Agent...' : 'Register New Agent'}
              </button>

              <p className="text-xs text-gray-400 text-center">
                Registration will create a new agent and provide you with an API token. Save this token securely!
              </p>
            </form>
          )}
        </div>

        {/* Info */}
        <div className="text-center text-sm text-gray-400">
          <p>
            SpaceTraders is an open-universe game played through an API.
            <br />
            Visit{' '}
            <a
              href="https://spacetraders.io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-space-accent hover:underline"
            >
              spacetraders.io
            </a>{' '}
            to learn more.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
