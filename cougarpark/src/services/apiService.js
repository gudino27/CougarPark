const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ec2-44-243-206-53.us-west-2.compute.amazonaws.com';

export const apiService = {
  async getZones() {
    const response = await fetch(`${API_BASE_URL}/api/zones/list`);
    if (!response.ok) throw new Error('Failed to fetch zones');
    return response.json();
  },

  async getZoneInfo(zoneName) {
    const response = await fetch(`${API_BASE_URL}/api/zones/${encodeURIComponent(zoneName)}/info`);
    if (!response.ok) throw new Error('Failed to fetch zone info');
    return response.json();
  },

  async predictOccupancy(zone, datetime) {
    const response = await fetch(`${API_BASE_URL}/api/occupancy/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zone, datetime })
    });
    if (!response.ok) throw new Error('Failed to predict occupancy');
    return response.json();
  },

  async predictEnforcementRisk(zone, datetime) {
    const response = await fetch(`${API_BASE_URL}/api/enforcement/risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zone, datetime })
    });
    if (!response.ok) throw new Error('Failed to predict enforcement risk');
    return response.json();
  },

  async getRecommendation(zone, datetime) {
    const response = await fetch(`${API_BASE_URL}/api/parking/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zone, datetime })
    });
    if (!response.ok) throw new Error('Failed to get recommendation');
    return response.json();
  },

  async submitFeedback(feedbackData) {
    const response = await fetch(`${API_BASE_URL}/api/feedback/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedbackData)
    });
    if (!response.ok) throw new Error('Failed to submit feedback');
    return response.json();
  },

  async getFeedbackStats() {
    const response = await fetch(`${API_BASE_URL}/api/feedback/stats`);
    if (!response.ok) throw new Error('Failed to fetch feedback stats');
    return response.json();
  },

  async getModelsInfo() {
    const response = await fetch(`${API_BASE_URL}/api/models/info`);
    if (!response.ok) throw new Error('Failed to fetch models info');
    return response.json();
  }
};
