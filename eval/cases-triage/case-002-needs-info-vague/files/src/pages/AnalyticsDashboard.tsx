import React, { useEffect, useState } from 'react';
import { fetchAnalyticsData } from '../api/analytics';

export function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsData()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="analytics-dashboard">
      <h1>Analytics</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
