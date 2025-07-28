import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from '@reduxjs/toolkit';

// Importar slices (reducers)
import authSlice from './slices/authSlice';
import dashboardSlice from './slices/dashboardSlice';
import campaignsSlice from './slices/campaignsSlice';
import contactsSlice from './slices/contactsSlice';
import messagesSlice from './slices/messagesSlice';
import connectorsSlice from './slices/connectorsSlice';
import templatesSlice from './slices/templatesSlice';
import billingSlice from './slices/billingSlice';
import settingsSlice from './slices/settingsSlice';

// Configuración de persistencia
const persistConfig = {
  key: 'jasmin-sms-dashboard',
  storage,
  whitelist: ['auth', 'settings'], // Solo persistir auth y settings
  blacklist: ['dashboard', 'campaigns', 'contacts', 'messages'], // No persistir datos temporales
};

// Combinar reducers
const rootReducer = combineReducers({
  auth: authSlice,
  dashboard: dashboardSlice,
  campaigns: campaignsSlice,
  contacts: contactsSlice,
  messages: messagesSlice,
  connectors: connectorsSlice,
  templates: templatesSlice,
  billing: billingSlice,
  settings: settingsSlice,
});

// Aplicar persistencia
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configurar store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        ignoredPaths: ['register'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Crear persistor
export const persistor = persistStore(store);

export default store;