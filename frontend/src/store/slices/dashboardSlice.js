import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  stats: {
    totalMessages: 0,
    sentMessages: 0,
    failedMessages: 0,
    pendingMessages: 0,
    totalCampaigns: 0,
    activeCampaigns: 0,
    totalContacts: 0,
    totalCredits: 0,
  },
  recentActivity: [],
  systemHealth: {
    status: "unknown",
    connectors: [],
    lastUpdate: null,
  },
  loading: false,
  error: null,
};

const dashboardSlice = createSlice({
  name: "dashboard",
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setStats: (state, action) => {
      state.stats = { ...state.stats, ...action.payload };
    },
    setRecentActivity: (state, action) => {
      state.recentActivity = action.payload;
    },
    addActivity: (state, action) => {
      state.recentActivity.unshift(action.payload);
      if (state.recentActivity.length > 50) {
        state.recentActivity = state.recentActivity.slice(0, 50);
      }
    },
    setSystemHealth: (state, action) => {
      state.systemHealth = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setStats,
  setRecentActivity,
  addActivity,
  setSystemHealth,
  setError,
  clearError,
} = dashboardSlice.actions;

export default dashboardSlice.reducer;
