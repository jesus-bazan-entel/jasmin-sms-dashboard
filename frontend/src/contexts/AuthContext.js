import React, { createContext, useContext, useReducer, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSnackbar } from "notistack";

// Estado inicial
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

// Tipos de acciones
const AUTH_ACTIONS = {
  LOGIN_START: "LOGIN_START",
  LOGIN_SUCCESS: "LOGIN_SUCCESS",
  LOGIN_FAILURE: "LOGIN_FAILURE",
  LOGOUT: "LOGOUT",
  REGISTER_START: "REGISTER_START",
  REGISTER_SUCCESS: "REGISTER_SUCCESS",
  REGISTER_FAILURE: "REGISTER_FAILURE",
  UPDATE_USER: "UPDATE_USER",
  CLEAR_ERROR: "CLEAR_ERROR",
  SET_LOADING: "SET_LOADING",
};

// Credenciales de demostración
const DEMO_USERS = {
  'admin@jasmin.com': {
    id: 1,
    email: 'admin@jasmin.com',
    username: 'admin',
    full_name: 'Administrador del Sistema',
    role: 'super_admin',
    password: 'admin123',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  },
  'manager@jasmin.com': {
    id: 2,
    email: 'manager@jasmin.com',
    username: 'manager',
    full_name: 'Manager de Operaciones',
    role: 'manager',
    password: 'manager123',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  },
  'operator@jasmin.com': {
    id: 3,
    email: 'operator@jasmin.com',
    username: 'operator',
    full_name: 'Operador SMS',
    role: 'operator',
    password: 'operator123',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  },
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        loading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };

    default:
      return state;
  }
};

// Contexto
const AuthContext = createContext();

// Hook personalizado
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe ser usado dentro de AuthProvider");
  }
  return context;
};

// Provider
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();

  // API Base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

  // Función para verificar si el backend está disponible
  const isBackendAvailable = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        timeout: 3000, // 3 segundos timeout
      });
      return response.ok;
    } catch (error) {
      console.log('Backend no disponible, usando modo demo');
      return false;
    }
  };

  // Función para hacer peticiones HTTP
  const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    // Agregar token si está disponible
    if (state.token) {
      config.headers.Authorization = `Bearer ${state.token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Error en la petición");
      }

      return data;
    } catch (error) {
      console.error("API Request Error:", error);
      throw error;
    }
  };

  // Función de login con modo demo
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      // Verificar si el backend está disponible
      const backendAvailable = await isBackendAvailable();

      if (backendAvailable) {
        // Modo backend real
        const formData = new FormData();
        formData.append("username", credentials.email);
        formData.append("password", credentials.password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Error al iniciar sesión");
        }

        // Guardar token en localStorage
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: data.user,
            token: data.access_token,
          },
        });

        enqueueSnackbar("Sesión iniciada correctamente", { variant: "success" });
        navigate("/dashboard");

        return data;
      } else {
        // Modo demo/offline
        const demoUser = DEMO_USERS[credentials.email];
        
        if (!demoUser) {
          throw new Error("Usuario no encontrado. Use las credenciales de demostración.");
        }

        if (demoUser.password !== credentials.password) {
          throw new Error("Contraseña incorrecta");
        }

        // Crear token demo
        const demoToken = `demo_token_${Date.now()}_${demoUser.id}`;
        const userWithoutPassword = { ...demoUser };
        delete userWithoutPassword.password;

        // Guardar en localStorage
        localStorage.setItem("token", demoToken);
        localStorage.setItem("user", JSON.stringify(userWithoutPassword));
        localStorage.setItem("demo_mode", "true");

        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: userWithoutPassword,
            token: demoToken,
          },
        });

        enqueueSnackbar(`Bienvenido ${demoUser.full_name} (Modo Demo)`, { 
          variant: "success",
          autoHideDuration: 4000,
        });
        
        navigate("/dashboard");

        return { user: userWithoutPassword, access_token: demoToken };
      }
    } catch (error) {
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: error.message,
      });
      enqueueSnackbar(error.message, { variant: "error" });
      throw error;
    }
  };

  // Función de registro
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });

    try {
      const backendAvailable = await isBackendAvailable();

      if (backendAvailable) {
        const data = await apiRequest("/auth/register", {
          method: "POST",
          body: JSON.stringify(userData),
        });

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        dispatch({
          type: AUTH_ACTIONS.REGISTER_SUCCESS,
          payload: {
            user: data.user,
            token: data.access_token,
          },
        });

        enqueueSnackbar("Cuenta creada correctamente", { variant: "success" });
        navigate("/dashboard");

        return data;
      } else {
        throw new Error("Registro no disponible en modo demo. Use las credenciales existentes.");
      }
    } catch (error) {
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: error.message,
      });
      enqueueSnackbar(error.message, { variant: "error" });
      throw error;
    }
  };

  // Función de logout
  const logout = async () => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";
      
      if (!isDemoMode && state.token) {
        // Intentar hacer logout en el servidor solo si no es modo demo
        await apiRequest("/auth/logout", {
          method: "POST",
        });
      }
    } catch (error) {
      console.error("Error al hacer logout en el servidor:", error);
    } finally {
      // Limpiar localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("demo_mode");

      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      enqueueSnackbar("Sesión cerrada", { variant: "info" });
      navigate("/login");
    }
  };

  // Función para actualizar perfil
  const updateProfile = async (profileData) => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (isDemoMode) {
        // Modo demo: actualizar localmente
        const updatedUser = { ...state.user, ...profileData };
        localStorage.setItem("user", JSON.stringify(updatedUser));

        dispatch({
          type: AUTH_ACTIONS.UPDATE_USER,
          payload: profileData,
        });

        enqueueSnackbar("Perfil actualizado (Modo Demo)", { variant: "success" });
        return updatedUser;
      } else {
        // Modo backend real
        const data = await apiRequest("/auth/profile", {
          method: "PUT",
          body: JSON.stringify(profileData),
        });

        dispatch({
          type: AUTH_ACTIONS.UPDATE_USER,
          payload: data,
        });

        localStorage.setItem("user", JSON.stringify(data));
        enqueueSnackbar("Perfil actualizado correctamente", { variant: "success" });
        return data;
      }
    } catch (error) {
      enqueueSnackbar(error.message, { variant: "error" });
      throw error;
    }
  };

  // Función para cambiar contraseña
  const changePassword = async (passwordData) => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (isDemoMode) {
        enqueueSnackbar("Cambio de contraseña no disponible en modo demo", { 
          variant: "warning" 
        });
        return;
      }

      await apiRequest("/auth/change-password", {
        method: "POST",
        body: JSON.stringify(passwordData),
      });

      enqueueSnackbar("Contraseña cambiada correctamente", { variant: "success" });
    } catch (error) {
      enqueueSnackbar(error.message, { variant: "error" });
      throw error;
    }
  };

  // Función para recuperar contraseña
  const forgotPassword = async (email) => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (isDemoMode) {
        enqueueSnackbar("Recuperación de contraseña no disponible en modo demo", { 
          variant: "warning" 
        });
        return;
      }

      await apiRequest("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      enqueueSnackbar("Instrucciones enviadas a tu email", { variant: "success" });
    } catch (error) {
      enqueueSnackbar(error.message, { variant: "error" });
      throw error;
    }
  };

  // Función para verificar token
  const verifyToken = async (token) => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (isDemoMode) {
        // En modo demo, verificar que el token tenga el formato correcto
        return token && token.startsWith("demo_token_");
      }

      const response = await fetch(`${API_BASE_URL}/auth/verify-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Token inválido");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error verificando token:", error);
      return null;
    }
  };

  // Función para refrescar token
  const refreshToken = async () => {
    try {
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (isDemoMode) {
        // En modo demo, generar nuevo token
        const newToken = `demo_token_${Date.now()}_${state.user?.id}`;
        localStorage.setItem("token", newToken);

        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: state.user,
            token: newToken,
          },
        });

        return newToken;
      }

      const data = await apiRequest("/auth/refresh", {
        method: "POST",
      });

      localStorage.setItem("token", data.access_token);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user: state.user,
          token: data.access_token,
        },
      });

      return data.access_token;
    } catch (error) {
      console.error("Error refrescando token:", error);
      logout();
      return null;
    }
  };

  // Limpiar error
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Verificar autenticación al cargar
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      const userData = localStorage.getItem("user");
      const isDemoMode = localStorage.getItem("demo_mode") === "true";

      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          
          if (isDemoMode) {
            // Modo demo: verificar token demo
            if (token.startsWith("demo_token_")) {
              dispatch({
                type: AUTH_ACTIONS.LOGIN_SUCCESS,
                payload: {
                  user,
                  token,
                },
              });
            } else {
              localStorage.removeItem("token");
              localStorage.removeItem("user");
              localStorage.removeItem("demo_mode");
              dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
            }
          } else {
            // Modo backend: verificar con servidor
            const isValid = await verifyToken(token);

            if (isValid) {
              dispatch({
                type: AUTH_ACTIONS.LOGIN_SUCCESS,
                payload: {
                  user,
                  token,
                },
              });
            } else {
              localStorage.removeItem("token");
              localStorage.removeItem("user");
              dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
            }
          }
        } catch (error) {
          console.error("Error inicializando auth:", error);
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          localStorage.removeItem("demo_mode");
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } else {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    initAuth();
  }, []);

  // Configurar interceptor para refrescar token automáticamente
  useEffect(() => {
    if (state.token) {
      const interval = setInterval(() => {
        refreshToken();
      }, 15 * 60 * 1000); // Refrescar cada 15 minutos

      return () => clearInterval(interval);
    }
  }, [state.token]);

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    forgotPassword,
    refreshToken,
    clearError,
    apiRequest,
    isDemoMode: localStorage.getItem("demo_mode") === "true",
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
