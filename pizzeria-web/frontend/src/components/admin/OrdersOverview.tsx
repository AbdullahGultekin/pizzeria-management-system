import React, { useState, useEffect } from 'react'
import { useWebSocket } from '../../hooks/useWebSocket'
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import VisibilityIcon from '@mui/icons-material/Visibility'
import DeleteIcon from '@mui/icons-material/Delete'
import PrintIcon from '@mui/icons-material/Print'
import RefreshIcon from '@mui/icons-material/Refresh'
import NumbersIcon from '@mui/icons-material/Numbers'
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep'
import Checkbox from '@mui/material/Checkbox'
import { orderAPI, printerAPI } from '../../services/api'
import { format, parseISO } from 'date-fns'
import { nl } from 'date-fns/locale'

interface Order {
  id: number
  bonnummer: string
  klant_id: number | null
  klant_naam?: string
  totaal: number
  datum: string
  status: string
  opmerking: string | null
}

interface OrderItem {
  id: number
  product_naam: string
  aantal: number
  prijs: number
  opmerking: string | null
  extras?: any // Extras (vlees, bijgerecht, sauzen, garnering, etc.)
}

const OrdersOverview = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [orderDetails, setOrderDetails] = useState<OrderItem[]>([])
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [dateFilter, setDateFilter] = useState<string>('today')
  const [printingOrder, setPrintingOrder] = useState<number | null>(null)
  const [printError, setPrintError] = useState('')
  const [renumbering, setRenumbering] = useState(false)
  const [selectedOrderIds, setSelectedOrderIds] = useState<number[]>([])
  const [deleting, setDeleting] = useState(false)

  const statusOptions = ['Nieuw', 'In behandeling', 'Klaar', 'Onderweg', 'Afgeleverd', 'Geannuleerd']
  
  const statusColors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
    'Nieuw': 'info',
    'In behandeling': 'warning',
    'Klaar': 'primary',
    'Onderweg': 'secondary',
    'Afgeleverd': 'success',
    'Geannuleerd': 'error',
  }

  useEffect(() => {
    loadOrders()
  }, [])

  // WebSocket for real-time updates (optional - app works without it)
  // Only try to connect if backend is likely to support it
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const baseUrl = API_BASE_URL.replace('/api/v1', '')
  
  // Only try WebSocket if we have a valid base URL
  let wsUrl: string | undefined
  if (baseUrl && !baseUrl.includes('undefined')) {
    wsUrl = baseUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:') + '/ws'
  }
  
  const { isConnected } = useWebSocket({
    url: wsUrl, // Will be undefined if URL is invalid
    autoConnect: !!wsUrl, // Only auto-connect if we have a valid URL
    reconnectInterval: 30000, // Try every 30 seconds (much less aggressive)
    onMessage: (message) => {
      if (message.type === 'order_created' || message.type === 'order_updated') {
        // Reload orders when a new order is created or updated
        loadOrders()
      }
    },
    onOpen: () => {
      // Subscribe as admin
      setTimeout(() => {
        // Send subscribe message after connection is established
      }, 100)
    },
    onError: () => {
      // Silently handle - WebSocket is optional, polling will be used as fallback
    },
  })

  const loadOrders = async () => {
    try {
      setLoading(true)
      const data = await orderAPI.getAll()
      setOrders(data)
    } catch (err: any) {
      console.error('Error loading orders:', err)
      setError(err.response?.data?.detail || 'Kon bestellingen niet laden')
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = async (order: Order) => {
    setSelectedOrder(order)
    setDetailsDialogOpen(true)
    setDetailsLoading(true)

    try {
      const details = await orderAPI.getById(order.id)
      setOrderDetails(details.items || [])
    } catch (err: any) {
      console.error('Error loading order details:', err)
      setError('Kon bestelling details niet laden')
    } finally {
      setDetailsLoading(false)
    }
  }

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    setUpdatingStatus(orderId)
    try {
      await orderAPI.update(orderId, { status: newStatus })
      await loadOrders()
      // Update selected order if it's the one being updated
      if (selectedOrder && selectedOrder.id === orderId) {
        setSelectedOrder({ ...selectedOrder, status: newStatus })
      }
    } catch (err: any) {
      console.error('Error updating order status:', err)
      setError(err.response?.data?.detail || 'Kon status niet bijwerken')
    } finally {
      setUpdatingStatus(null)
    }
  }

  const handleDelete = async (orderId: number) => {
    if (!window.confirm('Weet je zeker dat je deze bestelling wilt verwijderen?')) {
      return
    }

    try {
      await orderAPI.delete(orderId)
      await loadOrders()
      setSelectedOrderIds([]) // Clear selection
    } catch (err: any) {
      console.error('Error deleting order:', err)
      setError(err.response?.data?.detail || 'Kon bestelling niet verwijderen')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedOrderIds.length === 0) {
      alert('Selecteer eerst bestellingen om te verwijderen')
      return
    }

    if (!window.confirm(
      `Weet je zeker dat je ${selectedOrderIds.length} bestelling(en) wilt verwijderen?\n\n` +
      'Deze actie kan niet ongedaan worden gemaakt.'
    )) {
      return
    }

    setDeleting(true)
    setError('')
    
    try {
      const result = await orderAPI.deleteMultiple(selectedOrderIds)
      alert(result.message || `${selectedOrderIds.length} bestelling(en) succesvol verwijderd`)
      setSelectedOrderIds([])
      await loadOrders()
    } catch (err: any) {
      console.error('Error deleting orders:', err)
      setError(err.response?.data?.detail || 'Kon bestellingen niet verwijderen')
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteAll = async () => {
    if (!window.confirm(
      'Weet u zeker dat u ALLE bestellingen permanent wilt verwijderen?\n\n' +
      'Dit kan niet ongedaan worden gemaakt.'
    )) {
      return
    }

    const confirmText = window.prompt(
      'Typ "VERWIJDER ALLES" om te bevestigen:'
    )

    if ((confirmText || '').trim().toUpperCase() !== 'VERWIJDER ALLES') {
      alert('Verwijderen geannuleerd')
      return
    }

    setDeleting(true)
    setError('')
    
    try {
      const result = await orderAPI.deleteMultiple() // No IDs = delete all
      alert(result.message || 'Alle bestellingen succesvol verwijderd')
      setSelectedOrderIds([])
      await loadOrders()
    } catch (err: any) {
      console.error('Error deleting all orders:', err)
      setError(err.response?.data?.detail || 'Kon alle bestellingen niet verwijderen')
    } finally {
      setDeleting(false)
    }
  }

  const handleToggleSelect = (orderId: number) => {
    setSelectedOrderIds(prev => {
      if (prev.includes(orderId)) {
        return prev.filter(id => id !== orderId)
      } else {
        return [...prev, orderId]
      }
    })
  }

  const handleSelectAll = () => {
    if (selectedOrderIds.length === filteredOrders.length) {
      setSelectedOrderIds([])
    } else {
      setSelectedOrderIds(filteredOrders.map(o => o.id))
    }
  }

  const handlePrintOrder = async (orderId: number) => {
    setPrintingOrder(orderId)
    setPrintError('')
    
    try {
      const result = await printerAPI.printOrder(orderId)
      console.log('Print job queued:', result)
      // Clear any previous errors
      setError('')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Kon bestelling niet printen'
      setPrintError(errorMsg)
      setError(errorMsg)
    } finally {
      setPrintingOrder(null)
    }
  }

  const handleRenumberReceipts = async () => {
    if (!window.confirm(
      'Weet u zeker dat u alle bonnen wilt hernummeren?\n\n' +
      'Dit zorgt ervoor dat alle bonnen opnieuw worden genummerd in volgorde van datum en tijd.\n' +
      'Deze actie kan niet ongedaan worden gemaakt.'
    )) {
      return
    }

    setRenumbering(true)
    setError('')
    
    try {
      const result = await orderAPI.renumberReceipts()
      alert(result.message || `Bonnen succesvol hernummerd! Aantal bijgewerkte bonnen: ${result.updated_count || 0}`)
      await loadOrders() // Reload orders to show new numbers
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Kon bonnen niet hernummeren'
      setError(errorMsg)
    } finally {
      setRenumbering(false)
    }
  }

  // Calculate statistics
  const stats = {
    total: orders.length,
    totalRevenue: orders.reduce((sum, o) => sum + o.totaal, 0),
    byStatus: statusOptions.reduce((acc, status) => {
      acc[status] = orders.filter(o => o.status === status).length
      return acc
    }, {} as Record<string, number>),
    today: orders.filter(o => {
      const orderDate = new Date(o.datum)
      const today = new Date()
      return orderDate.toDateString() === today.toDateString()
    }).length,
  }

  const filteredOrders = orders.filter((order) => {
    const searchLower = searchTerm.toLowerCase()
    const matchesSearch = (
      order.bonnummer.toLowerCase().includes(searchLower) ||
      order.klant_naam?.toLowerCase().includes(searchLower) ||
      order.datum.toLowerCase().includes(searchLower)
    )
    
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter
    
    const matchesDate = (() => {
      if (dateFilter === 'all') return true
      const orderDate = new Date(order.datum)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      switch (dateFilter) {
        case 'today':
          return orderDate.toDateString() === today.toDateString()
        case 'week':
          const weekAgo = new Date(today)
          weekAgo.setDate(weekAgo.getDate() - 7)
          return orderDate >= weekAgo
        case 'month':
          const monthAgo = new Date(today)
          monthAgo.setMonth(monthAgo.getMonth() - 1)
          return orderDate >= monthAgo
        default:
          return true
      }
    })()
    
    return matchesSearch && matchesStatus && matchesDate
  })

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        flexDirection={{ xs: 'column', sm: 'row' }}
        gap={2}
        sx={{ mb: 3 }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#d32f2f', 
              fontWeight: 600,
              fontSize: { xs: '1.25rem', sm: '1.5rem' },
            }}
          >
            Bestellingen Overzicht
          </Typography>
          <Chip
            label={isConnected ? 'Live' : 'Offline'}
            color={isConnected ? 'success' : 'default'}
            size="small"
            sx={{ fontWeight: 600 }}
          />
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', width: { xs: '100%', sm: 'auto' } }}>
          {selectedOrderIds.length > 0 && (
            <Button
              variant="contained"
              onClick={handleDeleteSelected}
              disabled={deleting}
              startIcon={deleting ? <CircularProgress size={16} /> : <DeleteSweepIcon />}
              sx={{ 
                background: '#d32f2f',
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                px: { xs: 1, sm: 2 },
              }}
              fullWidth={isMobile}
            >
              {deleting ? 'Verwijderen...' : `Verwijder ${selectedOrderIds.length}`}
            </Button>
          )}
          <Button
            variant="outlined"
            onClick={handleDeleteAll}
            disabled={deleting || orders.length === 0}
            startIcon={deleting ? <CircularProgress size={16} /> : <DeleteSweepIcon />}
            sx={{ 
              borderColor: '#8B0000', 
              color: '#8B0000',
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              px: { xs: 1, sm: 2 },
            }}
            fullWidth={isMobile}
          >
            {deleting ? 'Verwijderen...' : 'Verwijder Alles'}
          </Button>
          <Button
            variant="outlined"
            onClick={handleRenumberReceipts}
            disabled={renumbering}
            startIcon={renumbering ? <CircularProgress size={16} /> : <NumbersIcon />}
            sx={{ 
              borderColor: '#FFA500', 
              color: '#FFA500',
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              px: { xs: 1, sm: 2 },
            }}
            fullWidth={isMobile}
          >
            {renumbering ? 'Hernummeren...' : 'Hernummer'}
          </Button>
          <Button 
            variant="contained" 
            onClick={loadOrders} 
            sx={{ 
              background: '#e52525',
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              px: { xs: 1, sm: 2 },
            }}
            fullWidth={isMobile}
          >
            <RefreshIcon sx={{ mr: { xs: 0, sm: 1 } }} />
            <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>Vernieuwen</Box>
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {printError && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setPrintError('')}>
          Print fout: {printError}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e3f2fd' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Totaal Bestellingen
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2' }}>
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#f3e5f5' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Totaal Omzet
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#7b1fa2' }}>
                €{stats.totalRevenue.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Vandaag
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#e65100' }}>
                {stats.today}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Nieuw
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#2e7d32' }}>
                {stats.byStatus['Nieuw'] || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            placeholder="Zoek op bonnummer, klant of datum..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              label="Status Filter"
            >
              <MenuItem value="all">Alle Statussen</MenuItem>
              {statusOptions.map((status) => (
                <MenuItem key={status} value={status}>
                  {status}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Datum Filter</InputLabel>
            <Select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              label="Datum Filter"
            >
              <MenuItem value="all">Alle Datums</MenuItem>
              <MenuItem value="today">Vandaag</MenuItem>
              <MenuItem value="week">Laatste Week</MenuItem>
              <MenuItem value="month">Laatste Maand</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <TableContainer 
        component={Paper} 
        sx={{ 
          borderRadius: '10px',
          overflowX: 'auto',
          '& .MuiTable-root': {
            minWidth: 650,
          },
        }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ background: '#fff5f5' }}>
              <TableCell 
                padding="checkbox" 
                sx={{ 
                  fontWeight: 600, 
                  color: '#d32f2f',
                  display: { xs: 'none', sm: 'table-cell' },
                }}
              >
                <Checkbox
                  indeterminate={selectedOrderIds.length > 0 && selectedOrderIds.length < filteredOrders.length}
                  checked={filteredOrders.length > 0 && selectedOrderIds.length === filteredOrders.length}
                  onChange={handleSelectAll}
                  sx={{ color: '#d32f2f', '&.Mui-checked': { color: '#d32f2f' } }}
                />
              </TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Bonnummer</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f', display: { xs: 'none', md: 'table-cell' } }}>Klant</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f', display: { xs: 'none', lg: 'table-cell' } }}>Datum</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Totaal</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Acties</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredOrders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {searchTerm || statusFilter !== 'all' || dateFilter !== 'all' 
                      ? 'Geen bestellingen gevonden met deze filters' 
                      : 'Geen bestellingen'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredOrders.map((order) => (
                <TableRow 
                  key={order.id} 
                  hover
                  selected={selectedOrderIds.includes(order.id)}
                  sx={{
                    backgroundColor: selectedOrderIds.includes(order.id) ? '#fff3e0' : 'inherit',
                    '&:hover': {
                      cursor: 'pointer',
                      bgcolor: '#fff9f9',
                    },
                  }}
                  onClick={() => handleViewDetails(order)}
                >
                  <TableCell 
                    padding="checkbox"
                    onClick={(e) => e.stopPropagation()}
                    sx={{ display: { xs: 'none', sm: 'table-cell' } }}
                  >
                    <Checkbox
                      checked={selectedOrderIds.includes(order.id)}
                      onChange={() => handleToggleSelect(order.id)}
                      sx={{ color: '#d32f2f', '&.Mui-checked': { color: '#d32f2f' } }}
                    />
                  </TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {order.bonnummer}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: { xs: 'block', md: 'none' } }}>
                        {order.klant_naam || 'Geen klant'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: { xs: 'block', lg: 'none' } }}>
                        {order.datum && format(parseISO(order.datum), 'dd MMM HH:mm', { locale: nl })}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                    {order.klant_naam || 'Geen klant'}
                  </TableCell>
                  <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>
                    {order.datum && format(parseISO(order.datum), 'dd MMM yyyy HH:mm', { locale: nl })}
                  </TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#e52525' }}>
                    €{order.totaal.toFixed(2)}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    {updatingStatus === order.id ? (
                      <CircularProgress size={20} />
                    ) : (
                      <FormControl size="small" sx={{ minWidth: { xs: 100, sm: 150 } }}>
                        <Select
                          value={order.status || 'Nieuw'}
                          onChange={(e) => handleStatusChange(order.id, e.target.value)}
                          onClick={(e) => e.stopPropagation()}
                          sx={{
                            '& .MuiSelect-select': {
                              py: 0.5,
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            },
                          }}
                        >
                          {statusOptions.map((status) => (
                            <MenuItem key={status} value={status}>
                              {status}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Box sx={{ display: 'flex', gap: { xs: 0.5, sm: 1 }, flexWrap: 'nowrap' }}>
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(order)}
                        sx={{ color: '#1976d2' }}
                        title="Details bekijken"
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handlePrintOrder(order.id)}
                        disabled={printingOrder === order.id}
                        sx={{ color: '#e52525' }}
                        title="Print bon"
                      >
                        {printingOrder === order.id ? (
                          <CircularProgress size={16} />
                        ) : (
                          <PrintIcon fontSize="small" />
                        )}
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(order.id)}
                        sx={{ color: '#d32f2f' }}
                        title="Verwijderen"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Order Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>
          Bestelling Details - {selectedOrder?.bonnummer}
        </DialogTitle>
        <DialogContent>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Klant
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {selectedOrder?.klant_naam || 'Geen klant'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Datum & Tijd
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {selectedOrder?.datum && format(parseISO(selectedOrder.datum), 'dd MMM yyyy HH:mm', { locale: nl })}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedOrder?.status || 'Nieuw'}
                    color={statusColors[selectedOrder?.status || 'Nieuw'] || 'default'}
                    sx={{ mt: 0.5 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Totaal
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#e52525', mt: 0.5 }}>
                    €{selectedOrder?.totaal.toFixed(2)}
                  </Typography>
                </Grid>
                {selectedOrder?.opmerking && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Opmerking
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 0.5, fontStyle: 'italic' }}>
                      {selectedOrder.opmerking}
                    </Typography>
                  </Grid>
                )}
              </Grid>

              <TableContainer sx={{ mt: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Product</TableCell>
                      <TableCell sx={{ fontWeight: 600 }} align="right">Aantal</TableCell>
                      <TableCell sx={{ fontWeight: 600 }} align="right">Prijs</TableCell>
                      <TableCell sx={{ fontWeight: 600 }} align="right">Totaal</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {orderDetails.map((item) => {
                      const extras = item.extras || {}
                      return (
                        <React.Fragment key={item.id}>
                          <TableRow>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {item.product_naam}
                              </Typography>
                              {/* Display extras like on receipt */}
                              {extras.vlees && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Vlees: {extras.vlees}
                                </Typography>
                              )}
                              {extras.bijgerecht && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Bijgerecht: {Array.isArray(extras.bijgerecht) ? extras.bijgerecht.join(', ') : extras.bijgerecht}
                                </Typography>
                              )}
                              {extras.sauzen && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Sauzen: {Array.isArray(extras.sauzen) ? extras.sauzen.join(', ') : extras.sauzen}
                                </Typography>
                              )}
                              {extras.sauzen_toeslag && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Sauzen extra: €{parseFloat(extras.sauzen_toeslag).toFixed(2)}
                                </Typography>
                              )}
                              {extras.garnering && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Garnering: {Array.isArray(extras.garnering) ? extras.garnering.join(', ') : extras.garnering}
                                </Typography>
                              )}
                              {extras.half_half && Array.isArray(extras.half_half) && extras.half_half.length === 2 && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5 }}>
                                  Half-half: {extras.half_half[0]} / {extras.half_half[1]}
                                </Typography>
                              )}
                              {item.opmerking && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ ml: 2, mt: 0.5, fontStyle: 'italic' }}>
                                  Opmerking: {item.opmerking}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell align="right">{item.aantal}</TableCell>
                            <TableCell align="right">€{item.prijs.toFixed(2)}</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 600 }}>
                              €{(item.prijs * item.aantal).toFixed(2)}
                            </TableCell>
                          </TableRow>
                        </React.Fragment>
                      )
                    })}
                    <TableRow>
                      <TableCell colSpan={3} align="right" sx={{ fontWeight: 600 }}>
                        Totaal:
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700, color: '#e52525' }}>
                        €{selectedOrder?.totaal.toFixed(2)}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Sluiten</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default OrdersOverview

