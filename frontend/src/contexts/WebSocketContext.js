import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useAuth } from "./AuthContext";
import { useSnackbar } from "notistack";

// Estados de conexión
const CONNECTION_STATUS = {
  CONNECTING: "connecting",
  CONNECTED: "connected",
  DISCONNECTED: "disconnected",
  ERROR: "error",
};

// Contexto
const WebSocketContext = createContext();

// Hook personalizado
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket debe ser usado dentro de WebSocketProvider");
  }
  return context;
};

// Provider
export const WebSocketProvider = ({ children }) => {
  const { user, token, isAuthenticated } = useAuth();
  const { enqueueSnackbar } = useSnackbar();

  const [connectionStatus, setConnectionStatus] = useState(
    CONNECTION_STATUS.DISCONNECTED
  );
  const [lastMessage, setLastMessage] = useState(null);
  const [messageHistory, setMessageHistory] = useState([]);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = 3000; // 3 segundos

  // URL del WebSocket
  const WS_BASE_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws";

  // Función para conectar WebSocket
  const connect = () => {
    if (!isAuthenticated || !token) {
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setConnectionStatus(CONNECTION_STATUS.CONNECTING);

      // Construir URL con token
      const wsUrl = `${WS_BASE_URL}?token=${token}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log("WebSocket conectado");
        setConnectionStatus(CONNECTION_STATUS.CONNECTED);
        reconnectAttemptsRef.current = 0;

        // Enviar mensaje de identificación
        sendMessage({
          type: "identify",
          data: {
            user_id: user?.id,
            timestamp: new Date().toISOString(),
          },
        });
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log("WebSocket mensaje recibido:", message);

          setLastMessage(message);
          setMessageHistory((prev) => [...prev.slice(-99), message]); // Mantener últimos 100 mensajes

          // Manejar diferentes tipos de mensajes
          handleMessage(message);
        } catch (error) {
          console.error("Error parseando mensaje WebSocket:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log("WebSocket desconectado:", event.code, event.reason);
        setConnectionStatus(CONNECTION_STATUS.DISCONNECTED);

        // Intentar reconectar si no fue un cierre intencional
        if (
          event.code !== 1000 &&
          isAuthenticated &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          scheduleReconnect();
        }
      };

      wsRef.current.onerror = (error) => {
        console.error("Error en WebSocket:", error);
        setConnectionStatus(CONNECTION_STATUS.ERROR);
      };
    } catch (error) {
      console.error("Error conectando WebSocket:", error);
      setConnectionStatus(CONNECTION_STATUS.ERROR);
    }
  };

  // Función para desconectar WebSocket
  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "Desconexión intencional");
      wsRef.current = null;
    }

    setConnectionStatus(CONNECTION_STATUS.DISCONNECTED);
  };

  // Función para programar reconexión
  const scheduleReconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    reconnectAttemptsRef.current += 1;
    const delay =
      reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1); // Backoff exponencial

    console.log(
      `Reintentando conexión WebSocket en ${delay}ms (intento ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
    );

    reconnectTimeoutRef.current = setTimeout(() => {
      if (isAuthenticated) {
        connect();
      }
    }, delay);
  };

  // Función para enviar mensajes
  const sendMessage = (message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        const messageString = JSON.stringify(message);
        wsRef.current.send(messageString);
        console.log("WebSocket mensaje enviado:", message);
        return true;
      } catch (error) {
        console.error("Error enviando mensaje WebSocket:", error);
        return false;
      }
    } else {
      console.warn("WebSocket no está conectado");
      return false;
    }
  };

  // Función para manejar mensajes recibidos
  const handleMessage = (message) => {
    switch (message.type) {
      case "notification":
        handleNotification(message.data);
        break;

      case "campaign_update":
        handleCampaignUpdate(message.data);
        break;

      case "message_status":
        handleMessageStatus(message.data);
        break;

      case "connector_status":
        handleConnectorStatus(message.data);
        break;

      case "system_alert":
        handleSystemAlert(message.data);
        break;

      case "user_activity":
        handleUserActivity(message.data);
        break;

      case "billing_update":
        handleBillingUpdate(message.data);
        break;

      default:
        console.log("Tipo de mensaje WebSocket no manejado:", message.type);
    }
  };

  // Manejadores específicos de mensajes
  const handleNotification = (data) => {
    const { title, message, type = "info", persistent = false } = data;

    enqueueSnackbar(message, {
      variant: type,
      persist: persistent,
      anchorOrigin: {
        vertical: "top",
        horizontal: "right",
      },
    });
  };

  const handleCampaignUpdate = (data) => {
    // Emitir evento personalizado para que los componentes puedan escuchar
    window.dispatchEvent(new CustomEvent("campaignUpdate", { detail: data }));
  };

  const handleMessageStatus = (data) => {
    window.dispatchEvent(new CustomEvent("messageStatus", { detail: data }));
  };

  const handleConnectorStatus = (data) => {
    window.dispatchEvent(new CustomEvent("connectorStatus", { detail: data }));

    // Mostrar notificación si hay cambio de estado crítico
    if (data.status === "disconnected" || data.status === "error") {
      enqueueSnackbar(`Conector ${data.name}: ${data.status}`, {
        variant: "warning",
        persist: true,
      });
    }
  };

  const handleSystemAlert = (data) => {
    const { level, message, title } = data;

    enqueueSnackbar(`${title}: ${message}`, {
      variant:
        level === "critical"
          ? "error"
          : level === "warning"
          ? "warning"
          : "info",
      persist: level === "critical",
    });
  };

  const handleUserActivity = (data) => {
    // Solo para administradores
    if (user?.role === "admin" || user?.role === "super_admin") {
      window.dispatchEvent(new CustomEvent("userActivity", { detail: data }));
    }
  };

  const handleBillingUpdate = (data) => {
    window.dispatchEvent(new CustomEvent("billingUpdate", { detail: data }));

    // Notificar si hay problemas de crédito
    if (data.type === "low_credits") {
      enqueueSnackbar("Créditos bajos: " + data.message, {
        variant: "warning",
        persist: true,
      });
    }
  };

  // Funciones de suscripción a eventos específicos
  const subscribeTo = (eventType, callback) => {
    sendMessage({
      type: "subscribe",
      data: {
        event_type: eventType,
        user_id: user?.id,
      },
    });

    // Agregar listener para eventos personalizados
    const eventName = eventType.replace("_", "");
    window.addEventListener(eventName, callback);

    // Retornar función de cleanup
    return () => {
      window.removeEventListener(eventName, callback);
      sendMessage({
        type: "unsubscribe",
        data: {
          event_type: eventType,
          user_id: user?.id,
        },
      });
    };
  };

  // Función para obtener estadísticas en tiempo real
  const requestStats = (statsType = "dashboard") => {
    sendMessage({
      type: "request_stats",
      data: {
        stats_type: statsType,
        user_id: user?.id,
      },
    });
  };

  // Función para enviar heartbeat
  const sendHeartbeat = () => {
    sendMessage({
      type: "heartbeat",
      data: {
        timestamp: new Date().toISOString(),
        user_id: user?.id,
      },
    });
  };

  // Efectos
  useEffect(() => {
    if (isAuthenticated && token) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, token]);

  // Heartbeat cada 30 segundos
  useEffect(() => {
    if (connectionStatus === CONNECTION_STATUS.CONNECTED) {
      const heartbeatInterval = setInterval(sendHeartbeat, 30000);
      return () => clearInterval(heartbeatInterval);
    }
  }, [connectionStatus]);

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  const value = {
    connectionStatus,
    lastMessage,
    messageHistory,
    sendMessage,
    subscribeTo,
    requestStats,
    connect,
    disconnect,
    isConnected: connectionStatus === CONNECTION_STATUS.CONNECTED,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketContext;
