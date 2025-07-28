import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  campaigns: [],
  currentCampaign: null,
  loading: false,
  error: null,
  filters: {
    status: 'all',
    search: '',
    dateRange: null,
  },
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
  },
};

const campaignsSlice = createSlice({
  name: 'campaigns',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setCampaigns: (state, action) => {
      state.campaigns = action.payload;
      state.loading = false;
    },
    addCampaign: (state, action) => {
      state.campaigns.unshift(action.payload);
    },
    updateCampaign: (state, action) => {
      const index = state.campaigns.findIndex(c => c.id === action.payload.id);
      if (index !== -1) {
        state.campaigns[index] = { ...state.campaigns[index], ...action.payload };
      }
    },
    deleteCampaign: (state, action) => {
      state.campaigns = state.campaigns.filter(c => c.id !== action.payload);
    },
    setCurrentCampaign: (state, action) => {
      state.currentCampaign = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
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
  setCampaigns,
  addCampaign,
  updateCampaign,
  deleteCampaign,
  setCurrentCampaign,
  setFilters,
  setPagination,
  setError,
  clearError,
} = campaignsSlice.actions;

export default campaignsSlice.reducer;