import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  AppBar,
  Toolbar,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import VisibilityIcon from '@mui/icons-material/Visibility'
import DeleteIcon from '@mui/icons-material/Delete'
import DateRangeIcon from '@mui/icons-material/DateRange'
import { useAuth } from '../contexts/AuthContext'
import { orderAPI } from '../services/api'
import { format, parseISO } from 'date-fns'

interface Order {
  id: number
  bonnummer: string
  klant_id: number | null
  klant_naam?: string
  totaal: number
  datum: string
  tijd?: string
  status: string
  opmerking: string | null
}

interface OrderItem {
  id: number
  product_naam: string
  aantal: number
  prijs: number
  opmerking: string | null
}

const HistoryPage = () => {
  const { user, logout } = useAuth()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [orderDetails, setOrderDetails] = useState<OrderItem[]>([])
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [stats, setStats] = useState({
    totalOrders: 0,
    totalRevenue: 0,
    averageOrder: 0,
  })

  useEffect(() => {
    loadOrders()
  }, [])

  useEffect(() => {
    calculateStats()
  }, [orders])

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

  const calculateStats = () => {
    const filtered = getFilteredOrders()
    const totalRevenue = filtered.reduce((sum, order) => sum + order.totaal, 0)
    const totalOrders = filtered.length
    setStats({
      totalOrders,
      totalRevenue,
      averageOrder: totalOrders > 0 ? totalRevenue / totalOrders : 0,
    })
  }

  const handleViewDetails = async (order: Order) => {
    setSelectedOrder(order)
    setDetailsDialogOpen(true)
    setDetailsLoading(true)

    try {
      const details = await orderAPI.getById(order.id)
      // The API returns an object with an 'items' array
      setOrderDetails(details.items || [])
      // Update selectedOrder with full details if needed
      if (details.klant_naam) {
        setSelectedOrder({ ...order, klant_naam: details.klant_naam })
      }
    } catch (err: any) {
      console.error('Error loading order details:', err)
      setError('Kon bestelling details niet laden')
    } finally {
      setDetailsLoading(false)
    }
  }

  const handleDelete = async (orderId: number) => {
    if (!window.confirm('Weet je zeker dat je deze bestelling wilt verwijderen?')) {
      return
    }

    try {
      await orderAPI.delete(orderId)
      await loadOrders()
    } catch (err: any) {
      console.error('Error deleting order:', err)
      setError(err.response?.data?.detail || 'Kon bestelling niet verwijderen')
    }
  }

  const getFilteredOrders = () => {
    return orders.filter((order) => {
      const searchLower = searchTerm.toLowerCase()
      const matchesSearch =
        order.bonnummer.toLowerCase().includes(searchLower) ||
        order.klant_naam?.toLowerCase().includes(searchLower) ||
        order.datum.toLowerCase().includes(searchLower)

      const matchesDate = !dateFilter || order.datum.startsWith(dateFilter)

      return matchesSearch && matchesDate
    })
  }

  const filteredOrders = getFilteredOrders()

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9' }}>
      <AppBar position="static" className="navbar-light">
        <Toolbar className="navbar-container">
          <Typography variant="h6" component="div" className="navbar-title" sx={{ flexGrow: 1 }}>
            Bestellingen Geschiedenis - {user?.username || 'Gebruiker'}
          </Typography>
          <Button color="inherit" onClick={logout} sx={{ color: '#333', fontWeight: 600 }}>
            Uitloggen
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" className="main-container" sx={{ mt: 3, mb: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Totaal Bestellingen
                </Typography>
                <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                  {stats.totalOrders}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Totale Omzet
                </Typography>
                <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                  €{stats.totalRevenue.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Gemiddelde Bestelling
                </Typography>
                <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                  €{stats.averageOrder.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3, borderRadius: '10px' }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
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
              <TextField
                fullWidth
                label="Filter op datum"
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                InputLabelProps={{ shrink: true }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <DateRangeIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => {
                  setSearchTerm('')
                  setDateFilter('')
                }}
                sx={{ borderColor: '#e52525', color: '#e52525' }}
              >
                Reset
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Orders Table */}
        <TableContainer component={Paper} sx={{ borderRadius: '10px' }}>
          <Table>
            <TableHead>
              <TableRow sx={{ background: '#fff5f5' }}>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Bonnummer</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Klant</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Datum & Tijd</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Totaal</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="center">Status</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Acties</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredOrders.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      {searchTerm || dateFilter ? 'Geen bestellingen gevonden' : 'Geen bestellingen'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredOrders.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell sx={{ fontWeight: 600 }}>{order.bonnummer}</TableCell>
                    <TableCell>{order.klant_naam || 'Geen klant'}</TableCell>
                    <TableCell>
                      {order.datum && format(parseISO(order.datum), 'dd MMM yyyy HH:mm')}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                      €{order.totaal.toFixed(2)}
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={order.status || 'Voltooid'}
                        color={order.status === 'Voltooid' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(order)}
                        sx={{ color: '#e52525' }}
                      >
                        <VisibilityIcon />
                      </IconButton>
                      {user?.role === 'admin' && (
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(order.id)}
                          sx={{ color: '#d32f2f' }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
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
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Klant: {selectedOrder?.klant_naam || 'Geen klant'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Datum: {selectedOrder?.datum && format(parseISO(selectedOrder.datum), 'dd MMM yyyy HH:mm')}
                </Typography>
                {selectedOrder?.opmerking && (
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Opmerking: {selectedOrder.opmerking}
                  </Typography>
                )}

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
                      {orderDetails.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>{item.product_naam}</TableCell>
                          <TableCell align="right">{item.aantal}</TableCell>
                          <TableCell align="right">€{item.prijs.toFixed(2)}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600 }}>
                            €{(item.prijs * item.aantal).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
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
      </Container>
    </Box>
  )
}

export default HistoryPage

