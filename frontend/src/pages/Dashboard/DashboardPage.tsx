import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  IconButton,
  Chip,
  LinearProgress,
  Alert,
  Skeleton,
} from "@mui/material";
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Message as MessageIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Router as RouterIcon,
  Speed as SpeedIcon,
} from "@mui/icons-material";
import { Line, Doughnut, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from "chart.js";
import { useQuery } from "react-query";
import { format, subHours, subDays } from "date-fns";

// Context hooks
import { useWebSocket } from "../../contexts/WebSocketContext";
import { useAuth } from "../../contexts/AuthContext";

// API services
import { dashboardApi } from "../../services/api";

// Types
interface DashboardMetrics {
  totalMessages: number;
  messagesDelivered: number;
  messagesFailed: number;
  messagesPending: number;
  deliveryRate: number;
  activeConnectors: number;
  totalConnectors: number;
  activeCampaigns: number;
  totalContacts: number;
  creditBalance: number;
  monthlySpent: number;
  throughput: number;
}

interface ConnectorStatus {
  id: string;
  cid: string;
  label: string;
  status: "started" | "stopped" | "bound" | "error";
  messagesSent: number;
  messagesReceived: number;
  lastActivity?: string;
}

interface RealtimeMetrics {
  timestamp: string;
  messagesSent: number;
  messagesDelivered: number;
  messagesFailed: number;
  throughput: number;
  connectorStatus: Record<string, ConnectorStatus>;
}

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { socket, isConnected } = useWebSocket();
  const [realtimeMetrics, setRealtimeMetrics] =
    useState<RealtimeMetrics | null>(null);
  const [hourlyData, setHourlyData] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch dashboard data
  const {
    data: dashboardData,
    isLoading,
    error,
    refetch,
  } = useQuery<DashboardMetrics>("dashboard-metrics", dashboardApi.getMetrics, {
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: connectorsData, isLoading: connectorsLoading } = useQuery<
    ConnectorStatus[]
  >("connectors-status", dashboardApi.getConnectorsStatus, {
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // WebSocket real-time updates
  useEffect(() => {
    if (!socket || !isConnected) return;

    // Subscribe to real-time channels
    socket.emit("subscribe", {
      type: "subscribe",
      channels: ["metrics", "connectors", "campaigns", "alerts"],
    });

    // Handle metrics updates
    socket.on("metrics_update", (data: RealtimeMetrics) => {
      setRealtimeMetrics(data);

      // Update hourly data for charts
      setHourlyData((prev) => {
        const newData = [
          ...prev,
          {
            time: format(new Date(data.timestamp), "HH:mm"),
            sent: data.messagesSent,
            delivered: data.messagesDelivered,
            failed: data.messagesFailed,
            throughput: data.throughput,
          },
        ];

        // Keep only last 24 hours
        return newData.slice(-24);
      });
    });

    // Handle connector updates
    socket.on("connector_update", (data: any) => {
      // Update connector status in real-time
      console.log("Connector update:", data);
    });

    // Handle alerts
    socket.on("alert", (data: any) => {
      // Handle system alerts
      console.log("System alert:", data);
    });

    return () => {
      socket.off("metrics_update");
      socket.off("connector_update");
      socket.off("alert");
    };
  }, [socket, isConnected]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  // Chart configurations
  const messagesTrendData = {
    labels: hourlyData.map((d) => d.time),
    datasets: [
      {
        label: "Messages Sent",
        data: hourlyData.map((d) => d.sent),
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        tension: 0.1,
      },
      {
        label: "Messages Delivered",
        data: hourlyData.map((d) => d.delivered),
        borderColor: "rgb(54, 162, 235)",
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        tension: 0.1,
      },
      {
        label: "Messages Failed",
        data: hourlyData.map((d) => d.failed),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        tension: 0.1,
      },
    ],
  };

  const deliveryStatusData = {
    labels: ["Delivered", "Failed", "Pending"],
    datasets: [
      {
        data: [
          dashboardData?.messagesDelivered || 0,
          dashboardData?.messagesFailed || 0,
          dashboardData?.messagesPending || 0,
        ],
        backgroundColor: [
          "rgba(75, 192, 192, 0.8)",
          "rgba(255, 99, 132, 0.8)",
          "rgba(255, 206, 86, 0.8)",
        ],
        borderColor: [
          "rgba(75, 192, 192, 1)",
          "rgba(255, 99, 132, 1)",
          "rgba(255, 206, 86, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  const throughputData = {
    labels: hourlyData.map((d) => d.time),
    datasets: [
      {
        label: "Messages/Minute",
        data: hourlyData.map((d) => d.throughput),
        backgroundColor: "rgba(153, 102, 255, 0.8)",
        borderColor: "rgba(153, 102, 255, 1)",
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load dashboard data. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Header */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            icon={isConnected ? <CheckCircleIcon /> : <ErrorIcon />}
            label={isConnected ? "Connected" : "Disconnected"}
            color={isConnected ? "success" : "error"}
            size="small"
          />
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        {/* Total Messages */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Total Messages
                  </Typography>
                  {isLoading ? (
                    <Skeleton width={80} height={32} />
                  ) : (
                    <Typography variant="h5" component="div">
                      {dashboardData?.totalMessages?.toLocaleString() || 0}
                    </Typography>
                  )}
                </Box>
                <MessageIcon color="primary" fontSize="large" />
              </Box>
              {realtimeMetrics && (
                <Box display="flex" alignItems="center" mt={1}>
                  <TrendingUpIcon fontSize="small" color="success" />
                  <Typography variant="body2" color="success.main" ml={0.5}>
                    +{realtimeMetrics.messagesSent} today
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Delivery Rate */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Delivery Rate
                  </Typography>
                  {isLoading ? (
                    <Skeleton width={80} height={32} />
                  ) : (
                    <Typography variant="h5" component="div">
                      {dashboardData?.deliveryRate?.toFixed(1) || 0}%
                    </Typography>
                  )}
                </Box>
                <CheckCircleIcon color="success" fontSize="large" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={dashboardData?.deliveryRate || 0}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Active Connectors */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Active Connectors
                  </Typography>
                  {isLoading ? (
                    <Skeleton width={80} height={32} />
                  ) : (
                    <Typography variant="h5" component="div">
                      {dashboardData?.activeConnectors || 0} /{" "}
                      {dashboardData?.totalConnectors || 0}
                    </Typography>
                  )}
                </Box>
                <RouterIcon color="info" fontSize="large" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={
                  dashboardData?.totalConnectors
                    ? (dashboardData.activeConnectors /
                        dashboardData.totalConnectors) *
                      100
                    : 0
                }
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Throughput */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Throughput
                  </Typography>
                  {isLoading ? (
                    <Skeleton width={80} height={32} />
                  ) : (
                    <Typography variant="h5" component="div">
                      {realtimeMetrics?.throughput ||
                        dashboardData?.throughput ||
                        0}
                    </Typography>
                  )}
                  <Typography variant="body2" color="textSecondary">
                    msg/min
                  </Typography>
                </Box>
                <SpeedIcon color="warning" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={3}>
        {/* Messages Trend */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Messages Trend (Last 24 Hours)
              </Typography>
              {hourlyData.length > 0 ? (
                <Line data={messagesTrendData} options={chartOptions} />
              ) : (
                <Box
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                  height={300}
                >
                  <Typography color="textSecondary">
                    No data available. Messages will appear here in real-time.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Delivery Status */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Delivery Status
              </Typography>
              {dashboardData ? (
                <Doughnut data={deliveryStatusData} />
              ) : (
                <Skeleton variant="circular" width={200} height={200} />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Throughput Chart */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Throughput Analysis
              </Typography>
              {hourlyData.length > 0 ? (
                <Bar data={throughputData} options={chartOptions} />
              ) : (
                <Box
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                  height={300}
                >
                  <Typography color="textSecondary">
                    Throughput data will appear here in real-time.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Connectors Status */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SMPP Connectors Status
              </Typography>
              {connectorsLoading ? (
                <Box>
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} height={60} sx={{ mb: 1 }} />
                  ))}
                </Box>
              ) : connectorsData && connectorsData.length > 0 ? (
                <Grid container spacing={2}>
                  {connectorsData.map((connector) => (
                    <Grid item xs={12} sm={6} md={4} key={connector.id}>
                      <Paper sx={{ p: 2 }}>
                        <Box
                          display="flex"
                          justifyContent="space-between"
                          alignItems="center"
                        >
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {connector.label}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {connector.cid}
                            </Typography>
                          </Box>
                          <Chip
                            label={connector.status}
                            color={
                              connector.status === "bound" ||
                              connector.status === "started"
                                ? "success"
                                : connector.status === "error"
                                ? "error"
                                : "default"
                            }
                            size="small"
                          />
                        </Box>
                        <Box
                          display="flex"
                          justifyContent="space-between"
                          mt={1}
                        >
                          <Typography variant="body2">
                            Sent: {connector.messagesSent}
                          </Typography>
                          <Typography variant="body2">
                            Received: {connector.messagesReceived}
                          </Typography>
                        </Box>
                        {connector.lastActivity && (
                          <Typography variant="caption" color="textSecondary">
                            Last activity:{" "}
                            {format(
                              new Date(connector.lastActivity),
                              "HH:mm:ss"
                            )}
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography color="textSecondary">
                  No connectors configured. Add your first SMPP connector to get
                  started.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
