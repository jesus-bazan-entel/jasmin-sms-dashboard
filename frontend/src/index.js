import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Provider } from "react-redux";
import { SnackbarProvider } from "notistack";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { es } from "date-fns/locale";

import App from "./App";
import { store } from "./store/store";
import { AuthProvider } from "./contexts/AuthContext";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import LoadingSpinner from "./components/common/LoadingSpinner";
import ErrorBoundary from "./components/common/ErrorBoundary";

import "./index.css";

// Configuración del tema Material-UI
const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#667eea",
      light: "#9bb5ff",
      dark: "#3f51b5",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#764ba2",
      light: "#a478d4",
      dark: "#4a2c73",
      contrastText: "#ffffff",
    },
    background: {
      default: "#f5f5f5",
      paper: "#ffffff",
    },
    text: {
      primary: "#333333",
      secondary: "#666666",
    },
    success: {
      main: "#4caf50",
      light: "#81c784",
      dark: "#388e3c",
    },
    warning: {
      main: "#ff9800",
      light: "#ffb74d",
      dark: "#f57c00",
    },
    error: {
      main: "#f44336",
      light: "#e57373",
      dark: "#d32f2f",
    },
    info: {
      main: "#2196f3",
      light: "#64b5f6",
      dark: "#1976d2",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: "2rem",
      fontWeight: 500,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: "1.75rem",
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: "1.5rem",
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: "1.25rem",
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: "1rem",
      fontWeight: 500,
      lineHeight: 1.6,
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.5,
    },
    body2: {
      fontSize: "0.875rem",
      lineHeight: 1.43,
    },
    button: {
      textTransform: "none",
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "8px 16px",
          fontSize: "0.875rem",
          fontWeight: 500,
          textTransform: "none",
          boxShadow: "none",
          "&:hover": {
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          },
        },
        contained: {
          background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
          "&:hover": {
            background: "linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          "&:hover": {
            boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: "1px solid rgba(0,0,0,0.12)",
          background: "#fafafa",
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: "2px 8px",
          "&.Mui-selected": {
            background: "linear-gradient(45deg, #667eea 30%, #764ba2 90%)",
            color: "white",
            "&:hover": {
              background: "linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)",
            },
          },
        },
      },
    },
  },
});

// Configuración de Notistack
const notistackRef = React.createRef();
const onClickDismiss = (key) => () => {
  notistackRef.current.closeSnackbar(key);
};

// Componente principal
const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
            <SnackbarProvider
              ref={notistackRef}
              maxSnack={3}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              action={(key) => (
                <button
                  onClick={onClickDismiss(key)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "white",
                    cursor: "pointer",
                    fontSize: "16px",
                    padding: "4px",
                  }}
                >
                  ✕
                </button>
              )}
              dense
              preventDuplicate
            >
              <BrowserRouter>
                <AuthProvider>
                  <WebSocketProvider>
                    <App />
                  </WebSocketProvider>
                </AuthProvider>
              </BrowserRouter>
            </SnackbarProvider>
          </LocalizationProvider>
        </ThemeProvider>
      </Provider>
    </ErrorBoundary>
  </React.StrictMode>
);

// Registro del Service Worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registrado: ", registration);

        // Verificar actualizaciones cada 60 segundos
        setInterval(() => {
          registration.update();
        }, 60000);

        // Manejar actualizaciones del SW
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          newWorker.addEventListener("statechange", () => {
            if (
              newWorker.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              // Nueva versión disponible
              if (
                window.confirm("Nueva versión disponible. ¿Recargar la página?")
              ) {
                newWorker.postMessage({ type: "SKIP_WAITING" });
                window.location.reload();
              }
            }
          });
        });
      })
      .catch((registrationError) => {
        console.log("SW registration failed: ", registrationError);
      });
  });
}

// Manejar actualizaciones del SW
navigator.serviceWorker?.addEventListener("controllerchange", () => {
  window.location.reload();
});

// Configuración global de errores
window.addEventListener("error", (event) => {
  console.error("Error global:", event.error);
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("Promise rechazada:", event.reason);
});

console.log("Jasmin SMS Dashboard v2.0.0 - Frontend iniciado");
