import { configureStore } from "@reduxjs/toolkit";
import { combineReducers } from "@reduxjs/toolkit";

// Importar slices (reducers)
import authSlice from "./slices/authSlice";
import dashboardSlice from "./slices/dashboardSlice";
import campaignsSlice from "./slices/campaignsSlice";
import contactsSlice from "./slices/contactsSlice";
import messagesSlice from "./slices/messagesSlice";
import connectorsSlice from "./slices/connectorsSlice";
import templatesSlice from "./slices/templatesSlice";
import billingSlice from "./slices/billingSlice";
import settingsSlice from "./slices/settingsSlice";

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

// Configurar store
export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [],
        ignoredPaths: [],
      },
    }),
  devTools: process.env.NODE_ENV !== "production",
});

export default store;
