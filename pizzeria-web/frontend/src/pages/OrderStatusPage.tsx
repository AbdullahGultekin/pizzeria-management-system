import { useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Stepper,
  Step,
  StepLabel,
  Divider,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import { orderAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorHandler'
import { format, parseISO } from 'date-fns'

interface Order {
  id: number
  bonnummer: string
  totaal: number
  datum: string
  tijd: string
  status: string
  items: Array<{
    product_naam: string
    aantal: number
    prijs: number
  }>
}

const statusSteps = ['Nieuw', 'In behandeling', 'Klaar', 'Onderweg', 'Afgeleverd']
const statusColors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
  'Nieuw': 'info',
  'In behandeling': 'warning',
  'Klaar': 'primary',
  'Onderweg': 'secondary',
  'Afgeleverd': 'success',
  'Geannuleerd': 'error',
}

const OrderStatusPage = () => {
  const [bonnummer, setBonnummer] = useState('')
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isConnected, setIsConnected] = useState(false)

  // WebSocket for real-time status updates (optional)
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const baseUrl = API_BASE_URL.replace('/api/v1', '')
  const wsUrl = baseUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:') + '/ws'
  
  const { sendMessage, connect: wsConnect } = useWebSocket({
    url: wsUrl,
    autoConnect: false, // Don't auto-connect
    reconnectInterval: 10000, // Less aggressive reconnection
    onMessage: (message) => {
      if (message.type === 'order_status_changed' && message.data) {
        const updatedOrder = message.data
        if (order && updatedOrder.bonnummer === order.bonnummer) {
          // Update the order status in real-time
          setOrder({
            ...order,
            status: updatedOrder.status,
          })
        }
      }
    },
    onOpen: () => {
      setIsConnected(true)
      // Subscribe to order updates if we have an order
      if (order?.bonnummer) {
        sendMessage({ type: 'subscribe_order', order_id: order.id })
      }
    },
    onClose: () => {
      setIsConnected(false)
    },
  })

  const handleSearch = async () => {
    if (!bonnummer.trim()) {
      setError('Voer een bonnummer in')
      return
    }

    setLoading(true)
    setError('')
    setOrder(null)

    try {
      // Use public endpoint to get order by bonnummer
      const orderDetails = await orderAPI.getByBonnummerPublic(bonnummer.trim())
      setOrder(orderDetails)
      // Connect WebSocket and subscribe to updates for this order
      wsConnect()
      setTimeout(() => {
        sendMessage({ type: 'subscribe_order', order_id: orderDetails.id })
      }, 500)
    } catch (err: any) {
      console.error('Error searching order:', err)
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const getStatusIndex = (status: string): number => {
    const index = statusSteps.indexOf(status)
    return index >= 0 ? index : 0
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9', py: 4 }}>
      <Container maxWidth="md">
        <Paper sx={{ p: 4, borderRadius: '10px' }}>
          <Typography variant="h4" gutterBottom sx={{ color: '#e52525', fontWeight: 700, mb: 3 }}>
            Bestelling Status
          </Typography>

          <Box sx={{ mb: 4 }}>
            <TextField
              fullWidth
              label="Bonnummer"
              value={bonnummer}
              onChange={(e) => setBonnummer(e.target.value)}
              placeholder="Voer uw bonnummer in (bijv. 20240001)"
              InputProps={{
                endAdornment: (
                  <Button
                    variant="contained"
                    onClick={handleSearch}
                    disabled={loading}
                    sx={{
                      bgcolor: '#e52525',
                      '&:hover': { bgcolor: '#c41e1e' },
                      ml: 1,
                    }}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : <SearchIcon />}
                  </Button>
                ),
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearch()
                }
              }}
            />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {order && (
            <Box>
              <Card sx={{ mb: 3, borderRadius: '10px' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h5" sx={{ color: '#e52525', fontWeight: 700 }}>
                      Bonnummer: {order.bonnummer}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={order.status}
                        color={statusColors[order.status] || 'default'}
                        sx={{ fontWeight: 600 }}
                      />
                      {isConnected && (
                        <Chip
                          label="Live"
                          color="success"
                          size="small"
                          sx={{ fontWeight: 600 }}
                        />
                      )}
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Besteld op: {format(parseISO(order.datum), 'dd MMM yyyy')} om {order.tijd}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 2, color: '#e52525', fontWeight: 700 }}>
                    Totaal: €{order.totaal.toFixed(2)}
                  </Typography>
                </CardContent>
              </Card>

              <Stepper activeStep={getStatusIndex(order.status)} alternativeLabel sx={{ mb: 4 }}>
                {statusSteps.map((step) => (
                  <Step key={step}>
                    <StepLabel>{step}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Bestelde items:
              </Typography>
              {order.items.map((item, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    py: 1,
                    borderBottom: index < order.items.length - 1 ? '1px solid #eee' : 'none',
                  }}
                >
                  <Typography>
                    {item.aantal}x {item.product_naam}
                  </Typography>
                  <Typography sx={{ fontWeight: 600, color: '#e52525' }}>
                    €{(item.prijs * item.aantal).toFixed(2)}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}

          {!order && !loading && !error && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Voer uw bonnummer in om de status van uw bestelling te bekijken
              </Typography>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  )
}

export default OrderStatusPage

