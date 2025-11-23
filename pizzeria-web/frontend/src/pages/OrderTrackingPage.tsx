import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Grid,
} from '@mui/material'
import { Search, LocalShipping, CheckCircle, AccessTime, Restaurant } from '@mui/icons-material'
import { orderAPI } from '../services/api'
import { brandColors } from '../theme/colors'
import PublicHeader from '../components/PublicHeader'

interface OrderItem {
  id: number
  product_naam: string
  aantal: number
  prijs: number
}

interface Order {
  id: number
  bonnummer: string
  klant_naam?: string
  datum: string
  tijd: string
  totaal: number
  opmerking?: string
  levertijd?: string
  status: string
  betaalmethode?: string
  items: OrderItem[]
}

const statusColors: Record<string, { color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning', icon: any }> = {
  'Nieuw': { color: 'info', icon: AccessTime },
  'In de keuken': { color: 'warning', icon: Restaurant },
  'Onderweg': { color: 'primary', icon: LocalShipping },
  'Afgeleverd': { color: 'success', icon: CheckCircle },
}

export default function OrderTrackingPage() {
  const [searchParams] = useSearchParams()
  const [bonnummer, setBonnummer] = useState('')
  const [phone, setPhone] = useState('')
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTrack = async (bn?: string) => {
    const trackBonnummer = bn || bonnummer.trim()
    const trackPhone = phone.trim()
    
    if (!trackBonnummer) {
      setError('Voer een bonnummer in')
      return
    }

    if (!trackPhone) {
      setError('Telefoonnummer is verplicht om je bestelling te volgen')
      return
    }

    setLoading(true)
    setError('')
    setOrder(null)

    try {
      const response = await orderAPI.trackOrder(trackBonnummer, trackPhone)
      setOrder(response)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Bestelling niet gevonden. Controleer het bonnummer en telefoonnummer.'
      setError(errorMsg)
      setOrder(null)
    } finally {
      setLoading(false)
    }
  }

  // Load bonnummer from URL params if available
  // Note: We don't auto-track because phone number is required
  useEffect(() => {
    const bonnummerParam = searchParams.get('bonnummer')
    if (bonnummerParam) {
      setBonnummer(bonnummerParam)
      // Don't auto-track - user must enter phone number first for security
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  const formatDate = (date: string) => {
    try {
      const d = new Date(date)
      return d.toLocaleDateString('nl-NL', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    } catch {
      return date
    }
  }

  const formatTime = (time: string) => {
    return time.substring(0, 5) // HH:MM
  }

  const getStatusInfo = (status: string) => {
    return statusColors[status] || { color: 'default' as const, icon: AccessTime }
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f0', display: 'flex', flexDirection: 'column' }}>
      {/* Header - Shared Component */}
      <PublicHeader />

      <Container maxWidth="md" sx={{ py: 4, flex: 1 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ color: brandColors.primary, fontWeight: 'bold' }}>
            Bestelling Volgen
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Volg je bestelling met je bonnummer en telefoonnummer (verplicht voor beveiliging)
          </Typography>
        </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Box component="form" onSubmit={(e) => { e.preventDefault(); handleTrack(); }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Bonnummer *"
                value={bonnummer}
                onChange={(e) => setBonnummer(e.target.value)}
                placeholder="Bijv. 20240001"
                required
                disabled={loading}
                helperText="Het bonnummer dat je hebt ontvangen bij je bestelling"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Telefoonnummer *"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Bijv. +32477123456"
                required
                disabled={loading}
                helperText="Verplicht om je bestelling te volgen (beveiliging)"
                error={!phone.trim() && bonnummer.trim() !== ''}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading || !bonnummer.trim() || !phone.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <Search />}
                sx={{
                  bgcolor: brandColors.primary,
                  '&:hover': { bgcolor: brandColors.primaryDark },
                  py: 1.5,
                }}
              >
                {loading ? 'Zoeken...' : 'Bestelling Zoeken'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {order && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Typography variant="h5" component="h2" gutterBottom>
                  Bestelling #{order.bonnummer}
                </Typography>
                {order.klant_naam && (
                  <Typography variant="body2" color="text.secondary">
                    Besteld door: {order.klant_naam}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} sm={6} sx={{ textAlign: { xs: 'left', sm: 'right' } }}>
                {(() => {
                  const statusInfo = getStatusInfo(order.status)
                  const StatusIcon = statusInfo.icon
                  return (
                    <Chip
                      icon={<StatusIcon />}
                      label={order.status}
                      color={statusInfo.color}
                      sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
                    />
                  )
                })()}
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Besteldatum
              </Typography>
              <Typography variant="body1" gutterBottom>
                {formatDate(order.datum)} om {formatTime(order.tijd)}
              </Typography>
            </Grid>
            {order.levertijd && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Verwachte levertijd
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {order.levertijd} minuten
                </Typography>
              </Grid>
            )}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Betaalmethode
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.betaalmethode === 'bancontact' ? 'Bancontact' : 
                 order.betaalmethode === 'cash' ? 'Contant' : 
                 order.betaalmethode || 'Niet gespecificeerd'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Totaalbedrag
              </Typography>
              <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 'bold' }}>
                €{order.totaal.toFixed(2)}
              </Typography>
            </Grid>
          </Grid>

          {order.opmerking && (
            <>
              <Divider sx={{ my: 3 }} />
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Opmerking
                </Typography>
                <Typography variant="body1">
                  {order.opmerking}
                </Typography>
              </Box>
            </>
          )}

          <Divider sx={{ my: 3 }} />

          <Box>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Bestelde Items
            </Typography>
            {order.items.map((item, index) => (
              <Box
                key={item.id || index}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 1.5,
                  borderBottom: index < order.items.length - 1 ? '1px solid #e0e0e0' : 'none',
                }}
              >
                <Box>
                  <Typography variant="body1" fontWeight="medium">
                    {item.aantal}x {item.product_naam}
                  </Typography>
                </Box>
                <Typography variant="body1" fontWeight="medium">
                  €{(item.prijs * item.aantal).toFixed(2)}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Geen account nodig om je bestelling te volgen
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Heb je een account? <a href="/login" style={{ color: brandColors.primary }}>Log in</a> om al je bestellingen te zien
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

