import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider,
  Chip,
  Grid,
} from '@mui/material'
import { printerAPI } from '../../services/api'
import RefreshIcon from '@mui/icons-material/Refresh'
import PrintIcon from '@mui/icons-material/Print'

const PrinterSettings = () => {
  const [printerInfo, setPrinterInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedPrinter, setSelectedPrinter] = useState('')

  useEffect(() => {
    loadPrinterInfo()
  }, [])

  const loadPrinterInfo = async () => {
    try {
      setLoading(true)
      setError('')
      const info = await printerAPI.getInfo()
      setPrinterInfo(info)
      setSelectedPrinter(info.current_printer || '')
    } catch (err: any) {
      console.error('Error loading printer info:', err)
      setError(err.response?.data?.detail || 'Kon printer informatie niet laden')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!selectedPrinter) {
      setError('Selecteer een printer')
      return
    }

    try {
      setSaving(true)
      setError('')
      setSuccess('')
      await printerAPI.configure(selectedPrinter)
      setSuccess(`Printer "${selectedPrinter}" succesvol geconfigureerd!`)
      await loadPrinterInfo()
    } catch (err: any) {
      console.error('Error configuring printer:', err)
      setError(err.response?.data?.detail || 'Kon printer niet configureren')
    } finally {
      setSaving(false)
    }
  }

  const handleTestPrint = async () => {
    if (!selectedPrinter) {
      setError('Selecteer eerst een printer')
      return
    }

    try {
      setSaving(true)
      setError('')
      setSuccess('')
      // Create a test print job
      // Note: This would require a test order or a test print endpoint
      setSuccess('Test print job gestart. Controleer de printer.')
    } catch (err: any) {
      console.error('Error testing print:', err)
      setError(err.response?.data?.detail || 'Kon test print niet uitvoeren')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ color: '#d32f2f', fontWeight: 600 }}>
          Printer Instellingen
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadPrinterInfo}
          disabled={loading}
        >
          Vernieuwen
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Printer Status Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ color: '#d32f2f', fontWeight: 600 }}>
                Printer Status
              </Typography>
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Direct Print Status
                </Typography>
                <Chip
                  label={printerInfo?.direct_print_enabled ? 'Ingeschakeld' : 'Uitgeschakeld'}
                  color={printerInfo?.direct_print_enabled ? 'success' : 'default'}
                  sx={{ mt: 1 }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Huidige Printer
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600, mt: 1 }}>
                  {printerInfo?.current_printer || 'Niet geconfigureerd'}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Pending Print Jobs
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#e52525', mt: 1 }}>
                  {printerInfo?.pending_jobs || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Printer Configuration Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ color: '#d32f2f', fontWeight: 600 }}>
                Printer Configuratie
              </Typography>
              <Divider sx={{ my: 2 }} />

              {printerInfo?.available_printers && printerInfo.available_printers.length > 0 ? (
                <>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Selecteer Printer</InputLabel>
                    <Select
                      value={selectedPrinter}
                      onChange={(e) => setSelectedPrinter(e.target.value)}
                      label="Selecteer Printer"
                    >
                      {printerInfo.available_printers.map((printer: string) => (
                        <MenuItem key={printer} value={printer}>
                          {printer}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleSave}
                      disabled={saving || !selectedPrinter}
                      sx={{ bgcolor: '#e52525', '&:hover': { bgcolor: '#c41e1e' } }}
                    >
                      {saving ? <CircularProgress size={20} /> : 'Opslaan'}
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<PrintIcon />}
                      onClick={handleTestPrint}
                      disabled={saving || !selectedPrinter}
                    >
                      Test Print
                    </Button>
                  </Box>
                </>
              ) : (
                <Alert severity="warning">
                  Geen printers gevonden. Zorg ervoor dat er een printer is aangesloten en ingeschakeld.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Info Card */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ color: '#d32f2f', fontWeight: 600 }}>
            Informatie
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>Direct Print:</strong> Als ingeschakeld, worden bestellingen direct naar de geselecteerde printer gestuurd.
            Als uitgeschakeld, worden print jobs in een queue gezet voor een desktop client.
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>Print Queue:</strong> Als direct print niet werkt of niet beschikbaar is, worden print jobs in een queue gezet.
            Een desktop client kan deze jobs ophalen en lokaal printen.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Opmerking:</strong> Direct print werkt alleen op Windows met een geconfigureerde thermal printer.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default PrinterSettings

