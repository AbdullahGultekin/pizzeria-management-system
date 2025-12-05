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
import { useTranslations } from '../hooks/useTranslations'

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
  const { t, translateProduct } = useTranslations()
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
      setError(t.language === 'nl' ? 'Voer een bonnummer in' : t.language === 'fr' ? 'Entrez un numéro de commande' : 'Enter an order number')
      return
    }

    if (!trackPhone) {
      setError(t.language === 'nl' ? 'Telefoonnummer is verplicht om je bestelling te volgen' : t.language === 'fr' ? 'Le numéro de téléphone est requis pour suivre votre commande' : 'Phone number is required to track your order')
      return
    }

    setLoading(true)
    setError('')
    setOrder(null)

    try {
      const response = await orderAPI.trackOrder(trackBonnummer, trackPhone)
      setOrder(response)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || t.orderNotFound
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
            {t.trackYourOrder}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t.language === 'nl' ? 'Volg je bestelling met je bonnummer en telefoonnummer (verplicht voor beveiliging)' : t.language === 'fr' ? 'Suivez votre commande avec votre numéro de commande et votre numéro de téléphone (obligatoire pour la sécurité)' : 'Track your order with your order number and phone number (required for security)'}
          </Typography>
        </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Box component="form" onSubmit={(e) => { e.preventDefault(); handleTrack(); }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={`${t.orderNumber} *`}
                value={bonnummer}
                onChange={(e) => setBonnummer(e.target.value)}
                placeholder="Bijv. 20240001"
                required
                disabled={loading}
                helperText={t.helperTextOrderNumber}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={`${t.phone} *`}
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Bijv. +32477123456"
                required
                disabled={loading}
                helperText={t.helperTextPhoneRequired}
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
                {loading ? t.loading : t.track}
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
                  {t.orderNumber} #{order.bonnummer}
                </Typography>
                {order.klant_naam && (
                  <Typography variant="body2" color="text.secondary">
                    {t.orderPlacedBy} {order.klant_naam}
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
                {t.orderDate}
              </Typography>
              <Typography variant="body1" gutterBottom>
                {formatDate(order.datum)} om {formatTime(order.tijd)}
              </Typography>
            </Grid>
            {order.levertijd && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {t.deliveryTime}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {order.levertijd} {t.minutes}
                </Typography>
              </Grid>
            )}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {t.paymentMethod}
              </Typography>
              <Typography variant="body1" gutterBottom>
                {order.betaalmethode === 'bancontact' ? 'Bancontact' : 
                 order.betaalmethode === 'cash' ? (t.language === 'nl' ? 'Contant' : t.language === 'fr' ? 'Espèces' : 'Cash') : 
                 order.betaalmethode || t.paymentMethodNotSpecified}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                {t.total}
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
                  {t.comment}
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
              {t.items}
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
                    {item.aantal}x {translateProduct(item.product_naam)}
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
            {t.noAccountNeeded}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {t.haveAccount} <a href="/login" style={{ color: brandColors.primary }}>{t.login}</a> {t.logInToSee}
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

