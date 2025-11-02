import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const ScrapingDashboard = () => {
  // State management
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [sessionRunning, setSessionRunning] = useState(false);

  // Fetch status every 10 seconds
  useEffect(() => {
    fetchStatus();
    fetchStats();
    
    const interval = setInterval(() => {
      fetchStatus();
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  // API calls
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/scraping/status`);
      const data = await response.json();
      setStatus(data);
      setSessionRunning(data.system_status.session_active);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching status:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/scraping/stats?days=7`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Control actions
  const startManualSession = async () => {
    try {
      setSessionRunning(true);
      const response = await fetch(`${API_URL}/api/scraping/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          grants_limit: 20,
          test_mode: false
        })
      });
      const data = await response.json();
      alert(data.message);
      fetchStatus();
    } catch (error) {
      console.error('Error starting session:', error);
      setSessionRunning(false);
    }
  };

  const stopSession = async () => {
    try {
      const response = await fetch(`${API_URL}/api/scraping/session/stop`, {
        method: 'POST'
      });
      const data = await response.json();
      alert(data.message);
      setSessionRunning(false);
      fetchStatus();
    } catch (error) {
      console.error('Error stopping session:', error);
    }
  };

  const controlScheduler = async (action) => {
    try {
      const response = await fetch(`${API_URL}/api/scraping/scheduler/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const data = await response.json();
      alert(data.message);
      fetchStatus();
    } catch (error) {
      console.error('Error controlling scheduler:', error);
    }
  };

  const removeDuplicates = async () => {
    if (!window.confirm('Remove all duplicate grants from the database?')) return;
    
    try {
      const response = await fetch(`${API_URL}/api/scraping/grants/duplicates`, {
        method: 'DELETE'
      });
      const data = await response.json();
      alert(`Removed ${data.removed_count} duplicate grants`);
      fetchStatus();
    } catch (error) {
      console.error('Error removing duplicates:', error);
    }
  };

  // UI Components
  const StatusCard = ({ title, value, color }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-sm text-gray-600 mb-2">{title}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );

  const ProgressBar = ({ current, target, label }) => {
    const percentage = Math.min((current / target) * 100, 100);
    return (
      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <span className="text-sm text-gray-600">{label}</span>
          <span className="text-sm text-gray-600">{current} / {target}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Grant Scraping Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor and control your grant collection system
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 border-b">
        {['overview', 'control', 'statistics'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 capitalize ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && status && (
        <div>
          {/* Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatusCard
              title="Total Grants"
              value={status.progress.total_grants.toLocaleString()}
              color="text-blue-600"
            />
            <StatusCard
              title="Today's Grants"
              value={status.progress.grants_today}
              color="text-green-600"
            />
            <StatusCard
              title="Sessions Today"
              value={status.progress.sessions_today}
              color="text-purple-600"
            />
            <StatusCard
              title="Success Rate"
              value={`${status.progress.success_rate.toFixed(0)}%`}
              color="text-emerald-600"
            />
          </div>

          {/* Progress Bars */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">Collection Progress</h3>
            <ProgressBar
              current={status.progress.total_grants}
              target={2000}
              label="Target: 2,000 Grants"
            />
            <ProgressBar
              current={status.progress.total_grants}
              target={5000}
              label="Target: 5,000 Grants"
            />
            <div className="mt-4 text-sm text-gray-600">
              <p>Estimated days to 2,000: {status.progress.estimated_days_to_2000}</p>
              <p>Estimated days to 5,000: {status.progress.estimated_days_to_5000}</p>
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Sessions</h3>
            <div className="space-y-2">
              {status.recent_sessions.map((session, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div className="flex items-center">
                    <span className={`h-3 w-3 rounded-full mr-3 ${
                      session.status === 'completed' ? 'bg-green-500' :
                      session.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}></span>
                    <div>
                      <p className="text-sm font-medium">
                        Session {session.session_id}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(session.start_time).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm font-medium">
                    {session.grants_scraped} grants
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Control Tab */}
      {activeTab === 'control' && (
        <div className="space-y-6">
          {/* Manual Control */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Manual Control</h3>
            <div className="flex space-x-4">
              <button
                onClick={startManualSession}
                disabled={sessionRunning}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                Start Session
              </button>
              <button
                onClick={stopSession}
                disabled={!sessionRunning}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
              >
                Stop Session
              </button>
              <button
                onClick={() => fetchStatus()}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Refresh Status
              </button>
            </div>
            {sessionRunning && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800 flex items-center">
                  Session is currently running...
                </p>
              </div>
            )}
          </div>

          {/* Automatic Scheduler */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Automatic Scheduler</h3>
            <div className="flex space-x-4">
              <button
                onClick={() => controlScheduler('start')}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Start Scheduler
              </button>
              <button
                onClick={() => controlScheduler('pause')}
                className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
              >
                Pause
              </button>
              <button
                onClick={() => controlScheduler('stop')}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Stop
              </button>
            </div>
            <p className="mt-4 text-sm text-gray-600">
              Scheduler Status: {status?.system_status.scheduler_running ? 
                <span className="text-green-600 font-medium">Running</span> : 
                <span className="text-gray-600 font-medium">Stopped</span>
              }
            </p>
          </div>

          {/* Database Maintenance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Database Maintenance</h3>
            <button
              onClick={removeDuplicates}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              Remove Duplicate Grants
            </button>
          </div>
        </div>
      )}

      {/* Statistics Tab */}
      {activeTab === 'statistics' && stats && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Daily Collection (Last 7 Days)</h3>
            <div className="space-y-2">
              {stats.grants_by_day.map((day, idx) => (
                <div key={idx} className="flex items-center">
                  <span className="text-sm text-gray-600 w-32">{day.date}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div 
                      className="bg-blue-500 h-4 rounded-full"
                      style={{ width: `${(day.grants / 100) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium ml-4">{day.grants}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Session Analytics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold">{stats.session_analytics.total_sessions}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Successful</p>
                <p className="text-2xl font-bold text-green-600">{stats.session_analytics.successful}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-red-600">{stats.session_analytics.failed}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Grants/Session</p>
                <p className="text-2xl font-bold">{stats.session_analytics.avg_grants_per_session.toFixed(1)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScrapingDashboard;
