import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  templates: [],
  currentTemplate: null,
  loading: false,
  error: null,
};

const templatesSlice = createSlice({
  name: 'templates',
  initialState,
  reducers: {
    setLoading: (state, action) => { state.loading = action.payload; },
    setTemplates: (state, action) => { state.templates = action.payload; state.loading = false; },
    addTemplate: (state, action) => { state.templates.unshift(action.payload); },
    updateTemplate: (state, action) => {
      const index = state.templates.findIndex(t => t.id === action.payload.id);
      if (index !== -1) state.templates[index] = { ...state.templates[index], ...action.payload };
    },
    deleteTemplate: (state, action) => { state.templates = state.templates.filter(t => t.id !== action.payload); },
    setCurrentTemplate: (state, action) => { state.currentTemplate = action.payload; },
    setError: (state, action) => { state.error = action.payload; state.loading = false; },
    clearError: (state) => { state.error = null; },
  },
});

export const { setLoading, setTemplates, addTemplate, updateTemplate, deleteTemplate, setCurrentTemplate, setError, clearError } = templatesSlice.actions;
export default templatesSlice.reducer;