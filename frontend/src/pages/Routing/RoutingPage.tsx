import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Paper,
  Divider,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  DragIndicator as DragIcon,
  FilterList as FilterIcon,
  Route as RouteIcon,
  TestTube as TestIcon,
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// API services
import { routingApi, connectorsApi } from '../../services/api';

// Types
interface Route {
  id: string;
  order: number;
  type: 'default' | 'static_mt' | 'random_round_robin' | 'failover';
  connectorId: string;
  connectorLabel: string;
  rate: number;
  filters: string[];
  isActive: boolean;
  description?: string;
}

interface Filter {
  id: string;
  fid: string;
  type: 'destination' | 'source' | 'short_code' | 'content' | 'tag' | 'user';
  parameter: string;
  value: string;
  isRegex: boolean;
  isCaseSensitive: boolean;
  negate: boolean;
  isActive: boolean;
  description?: string;
}

interface Connector {
  id: string;
  cid: string;
  label: string;
  status: string;
  host: string;
  port: number;
}

interface RouteTestResult {
  matchedRoute?: Route;
  matchedFilters: Filter[];
  testMessage: any;
}

// Form schemas
const routeSchema = yup.object({
  type: yup.string().required('Route type is required'),
  connectorId: yup.string().required('Connector is required'),
  rate: yup.number().min(0, 'Rate must be positive').required('Rate is required'),
  filters: yup.array().of(yup.string()),
  description: yup.string(),
});

const filterSchema = yup.object({
  fid: yup.string().required('Filter ID is required'),
  type: yup.string().required('Filter type is required'),
  parameter: yup.string().required('Parameter is required'),
  value: yup.string().required('Value is required'),
  description: yup.string(),
});

const RoutingPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [routeDialogOpen, setRouteDialogOpen] = useState(false);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [editingRoute, setEditingRoute] = useState<Route | null>(null);
  const [editingFilter, setEditingFilter] = useState<Filter | null>(null);
  const [testResult, setTestResult] = useState<RouteTestResult | null>(null);

  // Fetch data
  const { data: routes = [], isLoading: routesLoading } = useQuery<Route[]>(
    'routes',
    routingApi.getRoutes
  );

  const { data: filters = [], isLoading: filtersLoading } = useQuery<Filter[]>(
    'filters',
    routingApi.getFilters
  );

  const { data: connectors = [] } = useQuery<Connector[]>(
    'connectors',
    connectorsApi.getConnectors
  );

  // Mutations
  const createRouteMutation = useMutation(routingApi.createRoute, {
    onSuccess: () => {
      queryClient.invalidateQueries('routes');
      setRouteDialogOpen(false);
      resetRouteForm();
    },
  });

  const updateRouteMutation = useMutation(routingApi.updateRoute, {
    onSuccess: () => {
      queryClient.invalidateQueries('routes');
      setRouteDialogOpen(false);
      setEditingRoute(null);
      resetRouteForm();
    },
  });

  const deleteRouteMutation = useMutation(routingApi.deleteRoute, {
    onSuccess: () => {
      queryClient.invalidateQueries('routes');
    },
  });

  const createFilterMutation = useMutation(routingApi.createFilter, {
    onSuccess: () => {
      queryClient.invalidateQueries('filters');
      setFilterDialogOpen(false);
      resetFilterForm();
    },
  });

  const updateFilterMutation = useMutation(routingApi.updateFilter, {
    onSuccess: () => {
      queryClient.invalidateQueries('filters');
      setFilterDialogOpen(false);
      setEditingFilter(null);
      resetFilterForm();
    },
  });

  const deleteFilterMutation = useMutation(routingApi.deleteFilter, {
    onSuccess: () => {
      queryClient.invalidateQueries('filters');
    },
  });

  const testRouteMutation = useMutation(routingApi.testRoute, {
    onSuccess: (result) => {
      setTestResult(result);
    },
  });

  // Forms
  const {
    control: routeControl,
    handleSubmit: handleRouteSubmit,
    reset: resetRouteForm,
    formState: { errors: routeErrors },
  } = useForm({
    resolver: yupResolver(routeSchema),
    defaultValues: {
      type: 'default',
      connectorId: '',
      rate: 0,
      filters: [],
      description: '',
    },
  });

  const {
    control: filterControl,
    handleSubmit: handleFilterSubmit,
    reset: resetFilterForm,
    formState: { errors: filterErrors },
  } = useForm({
    resolver: yupResolver(filterSchema),
    defaultValues: {
      fid: '',
      type: 'destination',
      parameter: '',
      value: '',
      isRegex: false,
      isCaseSensitive: true,
      negate: false,
      description: '',
    },
  });

  const {
    control: testControl,
    handleSubmit: handleTestSubmit,
    formState: { errors: testErrors },
  } = useForm({
    defaultValues: {
      from: '',
      to: '',
      content: '',
      userId: '',
    },
  });

  // Handle drag and drop for routes
  const handleRouteDragEnd = async (result: DropResult) => {
    if (!result.destination) return;

    const items = Array.from(routes);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update order in backend
    try {
      await routingApi.reorderRoutes(
        items.map((route, index) => ({
          id: route.id,
          order: index + 1,
        }))
      );
      queryClient.invalidateQueries('routes');
    } catch (error) {
      console.error('Failed to reorder routes:', error);
    }
  };

  // Form handlers
  const onRouteSubmit = (data: any) => {
    if (editingRoute) {
      updateRouteMutation.mutate({ id: editingRoute.id, ...data });
    } else {
      createRouteMutation.mutate(data);
    }
  };

  const onFilterSubmit = (data: any) => {
    if (editingFilter) {
      updateFilterMutation.mutate({ id: editingFilter.id, ...data });
    } else {
      createFilterMutation.mutate(data);
    }
  };

  const onTestSubmit = (data: any) => {
    testRouteMutation.mutate(data);
  };

  const handleEditRoute = (route: Route) => {
    setEditingRoute(route);
    resetRouteForm({
      type: route.type,
      connectorId: route.connectorId,
      rate: route.rate,
      filters: route.filters,
      description: route.description || '',
    });
    setRouteDialogOpen(true);
  };

  const handleEditFilter = (filter: Filter) => {
    setEditingFilter(filter);
    resetFilterForm({
      fid: filter.fid,
      type: filter.type,
      parameter: filter.parameter,
      value: filter.value,
      isRegex: filter.isRegex,
      isCaseSensitive: filter.isCaseSensitive,
      negate: filter.negate,
      description: filter.description || '',
    });
    setFilterDialogOpen(true);
  };

  const handleDeleteRoute = (routeId: string) => {
    if (window.confirm('Are you sure you want to delete this route?')) {
      deleteRouteMutation.mutate(routeId);
    }
  };

  const handleDeleteFilter = (filterId: string) => {
    if (window.confirm('Are you sure you want to delete this filter?')) {
      deleteFilterMutation.mutate(filterId);
    }
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Routing & Filtering
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<TestIcon />}
            onClick={() => setTestDialogOpen(true)}
          >
            Test Route
          </Button>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setFilterDialogOpen(true)}
          >
            Add Filter
          </Button>
          <Button
            variant="contained"
            startIcon={<RouteIcon />}
            onClick={() => setRouteDialogOpen(true)}
          >
            Add Route
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Routes Section */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Message Routes
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={2}>
                Drag and drop to reorder routes. Routes are processed in order from top to bottom.
              </Typography>

              {routesLoading ? (
                <Typography>Loading routes...</Typography>
              ) : routes.length === 0 ? (
                <Alert severity="info">
                  No routes configured. Create your first route to start routing messages.
                </Alert>
              ) : (
                <DragDropContext onDragEnd={handleRouteDragEnd}>
                  <Droppable droppableId="routes">
                    {(provided) => (
                      <div {...provided.droppableProps} ref={provided.innerRef}>
                        {routes.map((route, index) => (
                          <Draggable key={route.id} draggableId={route.id} index={index}>
                            {(provided, snapshot) => (
                              <Paper
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                sx={{
                                  p: 2,
                                  mb: 2,
                                  backgroundColor: snapshot.isDragging ? 'action.hover' : 'background.paper',
                                  border: route.isActive ? '2px solid' : '1px solid',
                                  borderColor: route.isActive ? 'success.main' : 'divider',
                                }}
                              >
                                <Box display="flex" alignItems="center" gap={2}>
                                  <div {...provided.dragHandleProps}>
                                    <DragIcon color="action" />
                                  </div>
                                  
                                  <Box flex={1}>
                                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                                      <Typography variant="subtitle1" fontWeight="bold">
                                        #{route.order} - {route.connectorLabel}
                                      </Typography>
                                      <Chip
                                        label={route.type.replace('_', ' ').toUpperCase()}
                                        size="small"
                                        color="primary"
                                      />
                                      <Chip
                                        label={route.isActive ? 'Active' : 'Inactive'}
                                        size="small"
                                        color={route.isActive ? 'success' : 'default'}
                                      />
                                    </Box>
                                    
                                    <Typography variant="body2" color="textSecondary">
                                      Rate: ${route.rate} per message
                                    </Typography>
                                    
                                    {route.filters.length > 0 && (
                                      <Box display="flex" gap={1} mt={1}>
                                        <Typography variant="caption">Filters:</Typography>
                                        {route.filters.map((filterId) => {
                                          const filter = filters.find(f => f.id === filterId);
                                          return filter ? (
                                            <Chip
                                              key={filterId}
                                              label={filter.fid}
                                              size="small"
                                              variant="outlined"
                                            />
                                          ) : null;
                                        })}
                                      </Box>
                                    )}
                                    
                                    {route.description && (
                                      <Typography variant="body2" color="textSecondary" mt={1}>
                                        {route.description}
                                      </Typography>
                                    )}
                                  </Box>
                                  
                                  <Box display="flex" gap={1}>
                                    <Tooltip title="Edit Route">
                                      <IconButton
                                        size="small"
                                        onClick={() => handleEditRoute(route)}
                                      >
                                        <EditIcon />
                                      </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete Route">
                                      <IconButton
                                        size="small"
                                        color="error"
                                        onClick={() => handleDeleteRoute(route.id)}
                                      >
                                        <DeleteIcon />
                                      </IconButton>
                                    </Tooltip>
                                  </Box>
                                </Box>
                              </Paper>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Filters Section */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Message Filters
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={2}>
                Create filters to control message routing based on various criteria.
              </Typography>

              {filtersLoading ? (
                <Typography>Loading filters...</Typography>
              ) : filters.length === 0 ? (
                <Alert severity="info">
                  No filters configured. Create filters to control message routing.
                </Alert>
              ) : (
                <Box>
                  {filters.map((filter) => (
                    <Paper key={filter.id} sx={{ p: 2, mb: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="start">
                        <Box flex={1}>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {filter.fid}
                            </Typography>
                            <Chip
                              label={filter.type}
                              size="small"
                              color="secondary"
                            />
                            <Chip
                              label={filter.isActive ? 'Active' : 'Inactive'}
                              size="small"
                              color={filter.isActive ? 'success' : 'default'}
                            />
                          </Box>
                          
                          <Typography variant="body2" color="textSecondary">
                            {filter.parameter}: {filter.value}
                          </Typography>
                          
                          <Box display="flex" gap={1} mt={1}>
                            {filter.isRegex && (
                              <Chip label="Regex" size="small" variant="outlined" />
                            )}
                            {!filter.isCaseSensitive && (
                              <Chip label="Case Insensitive" size="small" variant="outlined" />
                            )}
                            {filter.negate && (
                              <Chip label="Negated" size="small" variant="outlined" />
                            )}
                          </Box>
                          
                          {filter.description && (
                            <Typography variant="caption" color="textSecondary" mt={1}>
                              {filter.description}
                            </Typography>
                          )}
                        </Box>
                        
                        <Box display="flex" flexDirection="column" gap={1}>
                          <IconButton
                            size="small"
                            onClick={() => handleEditFilter(filter)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteFilter(filter.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Route Dialog */}
      <Dialog open={routeDialogOpen} onClose={() => setRouteDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRoute ? 'Edit Route' : 'Create New Route'}
        </DialogTitle>
        <form onSubmit={handleRouteSubmit(onRouteSubmit)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="type"
                  control={routeControl}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!routeErrors.type}>
                      <InputLabel>Route Type</InputLabel>
                      <Select {...field} label="Route Type">
                        <MenuItem value="default">Default</MenuItem>
                        <MenuItem value="static_mt">Static MT</MenuItem>
                        <MenuItem value="random_round_robin">Random Round Robin</MenuItem>
                        <MenuItem value="failover">Failover</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="connectorId"
                  control={routeControl}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!routeErrors.connectorId}>
                      <InputLabel>Connector</InputLabel>
                      <Select {...field} label="Connector">
                        {connectors.map((connector) => (
                          <MenuItem key={connector.id} value={connector.id}>
                            {connector.label} ({connector.cid})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="rate"
                  control={routeControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Rate per Message"
                      type="number"
                      inputProps={{ step: 0.001, min: 0 }}
                      error={!!routeErrors.rate}
                      helperText={routeErrors.rate?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="filters"
                  control={routeControl}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Filters</InputLabel>
                      <Select
                        {...field}
                        multiple
                        label="Filters"
                        renderValue={(selected) => (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {(selected as string[]).map((value) => {
                              const filter = filters.find(f => f.id === value);
                              return (
                                <Chip key={value} label={filter?.fid || value} size="small" />
                              );
                            })}
                          </Box>
                        )}
                      >
                        {filters.map((filter) => (
                          <MenuItem key={filter.id} value={filter.id}>
                            {filter.fid} ({filter.type})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={routeControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Description"
                      multiline
                      rows={2}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRouteDialogOpen(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createRouteMutation.isLoading || updateRouteMutation.isLoading}
            >
              {editingRoute ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Filter Dialog */}
      <Dialog open={filterDialogOpen} onClose={() => setFilterDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingFilter ? 'Edit Filter' : 'Create New Filter'}
        </DialogTitle>
        <form onSubmit={handleFilterSubmit(onFilterSubmit)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="fid"
                  control={filterControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Filter ID"
                      error={!!filterErrors.fid}
                      helperText={filterErrors.fid?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="type"
                  control={filterControl}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!filterErrors.type}>
                      <InputLabel>Filter Type</InputLabel>
                      <Select {...field} label="Filter Type">
                        <MenuItem value="destination">Destination</MenuItem>
                        <MenuItem value="source">Source</MenuItem>
                        <MenuItem value="short_code">Short Code</MenuItem>
                        <MenuItem value="content">Content</MenuItem>
                        <MenuItem value="tag">Tag</MenuItem>
                        <MenuItem value="user">User</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="parameter"
                  control={filterControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Parameter"
                      error={!!filterErrors.parameter}
                      helperText={filterErrors.parameter?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="value"
                  control={filterControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Value"
                      error={!!filterErrors.value}
                      helperText={filterErrors.value?.message}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={filterControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Description"
                      multiline
                      rows={2}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Box display="flex" gap={2}>
                  <Controller
                    name="isRegex"
                    control={filterControl}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Use Regular Expression"
                      />
                    )}
                  />
                  
                  <Controller
                    name="isCaseSensitive"
                    control={filterControl}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Case Sensitive"
                      />
                    )}
                  />
                  
                  <Controller
                    name="negate"
                    control={filterControl}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Negate (NOT condition)"
                      />
                    )}
                  />
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFilterDialogOpen(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createFilterMutation.isLoading || updateFilterMutation.isLoading}
            >
              {editingFilter ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Route Test Dialog */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Test Message Routing</DialogTitle>
        <form onSubmit={handleTestSubmit(onTestSubmit)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="from"
                  control={testControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="From Number"
                      placeholder="+1234567890"
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Controller
                  name="to"
                  control={testControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="To Number"
                      placeholder="+0987654321"
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="content"
                  control={testControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Message Content"
                      multiline
                      rows={3}
                      placeholder="Enter test message content..."
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Controller
                  name="userId"
                  control={testControl}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="User ID (optional)"
                      placeholder="test_user"
                    />
                  )}
                />
              </Grid>
            </Grid>
            
            {testResult && (
              <Box mt={3}>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Test Result
                </Typography>
                
                {testResult.matchedRoute ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Message would be routed to: <strong>{testResult.matchedRoute.connectorLabel}</strong>
                  </Alert>
                ) : (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    No matching route found. Message would be rejected.
                  </Alert>
                )}
                
                {testResult.matchedFilters.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Matched Filters:
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {testResult.matchedFilters.map((filter) => (
                        <Chip
                          key={filter.id}
                          label={`${filter.fid} (${filter.type})`}
                          size="small"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTestDialogOpen(false)}>Close</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={testRouteMutation.isLoading}
            >
              Test Route
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default RoutingPage;