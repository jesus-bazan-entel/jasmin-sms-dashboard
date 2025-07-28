import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  messages: [],
  currentMessage: null,
  loading: false,
  error: null,
  filters: { status: "all", search: "" },
  pagination: { page: 1, limit: 10, total: 0 },
};

const messagesSlice = createSlice({
  name: "messages",
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setMessages: (state, action) => {
      state.messages = action.payload;
      state.loading = false;
    },
    addMessage: (state, action) => {
      state.messages.unshift(action.payload);
    },
    updateMessage: (state, action) => {
      const index = state.messages.findIndex((m) => m.id === action.payload.id);
      if (index !== -1)
        state.messages[index] = { ...state.messages[index], ...action.payload };
    },
    setCurrentMessage: (state, action) => {
      state.currentMessage = action.payload;
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
  setMessages,
  addMessage,
  updateMessage,
  setCurrentMessage,
  setFilters,
  setPagination,
  setError,
  clearError,
} = messagesSlice.actions;
export default messagesSlice.reducer;
