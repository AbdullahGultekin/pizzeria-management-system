import { useState } from 'react'
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
} from '@mui/material'
import { contactAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorHandler'
import {
  LocationOn as LocationIcon,
  Route as RouteIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
} from '@mui/icons-material'
import PublicHeader from '../components/PublicHeader'
import { brandColors } from '../theme/colors'

const ContactPage = () => {
  const [formData, setFormData] = useState({
    naam: '',
    email: '',
    telefoon: '',
    bericht: '',
  })
  const [errors, setErrors] = useState<Partial<typeof formData>>({})
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const openingstijden = [
    { dag: 'Maandag', tijd: 'Gesloten' },
    { dag: 'Dinsdag', tijd: '17:00 - 20:30' },
    { dag: 'Woensdag', tijd: '17:00 - 20:30' },
    { dag: 'Donderdag', tijd: '17:00 - 20:30' },
    { dag: 'Vrijdag', tijd: '17:00 - 20:30' },
    { dag: 'Zaterdag', tijd: '17:00 - 20:30' },
    { dag: 'Zondag', tijd: '17:00 - 20:30' },
  ]

  const validateForm = () => {
    const newErrors: Partial<typeof formData> = {}
    
    if (!formData.naam.trim()) {
      newErrors.naam = 'Naam is verplicht'
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'E-mail is verplicht'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Ongeldig e-mailadres'
    }
    
    if (!formData.bericht.trim()) {
      newErrors.bericht = 'Bericht is verplicht'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setSubmitting(true)
    setError('')

    try {
      await contactAPI.submit(formData)
      
      setSuccess(true)
      setFormData({
        naam: '',
        email: '',
        telefoon: '',
        bericht: '',
      })
      
      setTimeout(() => {
        setSuccess(false)
      }, 5000)
    } catch (err: any) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa', pb: 4 }}>
      {/* Header - Shared Component */}
      <PublicHeader />

      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Contact Info */}
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 4,
                borderRadius: '15px',
                boxShadow: '0 3px 15px rgba(0,0,0,0.1)',
                height: '100%',
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  color: brandColors.primary,
                  mb: 3,
                  pb: 2,
                  borderBottom: '2px solid brandColors.primary',
                }}
              >
                Contactgegevens
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <LocationIcon sx={{ color: brandColors.primary, mr: 1.5 }} />
                  <Typography>Brugstraat 12, 9120 Vrasene</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PhoneIcon sx={{ color: brandColors.primary, mr: 1.5 }} />
                  <Box
                    component="a"
                    href="tel:037757228"
                    sx={{ color: 'inherit', textDecoration: 'none' }}
                  >
                    03 775 72 28
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <EmailIcon sx={{ color: brandColors.primary, mr: 1.5 }} />
                  <Box
                    component="a"
                    href="mailto:info@pitapizzanapoli.be"
                    sx={{ color: 'inherit', textDecoration: 'none' }}
                  >
                    info@pitapizzanapoli.be
                  </Box>
                </Box>
              </Box>

              {/* Openingstijden */}
              <Box
                sx={{
                  bgcolor: '#fff8f8',
                  p: 2,
                  borderRadius: '10px',
                  mb: 3,
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ color: brandColors.primary, mb: 2 }}
                >
                  Openingstijden
                </Typography>
                <Box component="table" sx={{ width: '100%' }}>
                  <Box component="tbody">
                    {openingstijden.map((item) => (
                      <Box
                        component="tr"
                        key={item.dag}
                        sx={{
                          borderBottom: '1px solid #ffe5e5',
                          '&:last-child': { borderBottom: 'none' },
                        }}
                      >
                        <Box
                          component="td"
                          sx={{ py: 1, pr: 2 }}
                        >
                          {item.dag}
                        </Box>
                        <Box
                          component="td"
                          sx={{ py: 1, textAlign: 'right', fontWeight: 500 }}
                        >
                          {item.tijd}
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </Box>
              </Box>

              {/* Google Maps */}
              <Box
                sx={{
                  borderRadius: '10px',
                  overflow: 'hidden',
                  mb: 2,
                  height: '250px',
                }}
              >
                <iframe
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2503.379834829995!2d4.204675!3d51.197782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47c38c7f7c86be37%3A0x4b127b954b33741a!2sBrugstraat%2012%2C%209120%20Vrasene!5e0!3m2!1snl!2sbe!4v1744827225!5m2!1snl!2sbe"
                  width="100%"
                  height="250"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Locatie Pita Pizza Napoli"
                />
              </Box>

              <Box
                component="a"
                href="https://www.google.com/maps/dir//Brugstraat+12,+9120+Vrasene"
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  color: brandColors.primary,
                  textDecoration: 'none',
                  '&:hover': { textDecoration: 'underline' },
                }}
              >
                <RouteIcon sx={{ mr: 1 }} />
                Route plannen met Google Maps
              </Box>
            </Paper>
          </Grid>

          {/* Contact Form */}
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 4,
                borderRadius: '15px',
                boxShadow: '0 3px 15px rgba(0,0,0,0.1)',
                height: '100%',
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  color: brandColors.primary,
                  mb: 2,
                  pb: 2,
                  borderBottom: '2px solid brandColors.primary',
                }}
              >
                Stuur ons een bericht
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Heb je vragen, opmerkingen of wil je direct bestellen? Neem contact met ons op!
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Bedankt voor je bericht! We nemen zo spoedig mogelijk contact met je op.
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Naam"
                  value={formData.naam}
                  onChange={handleChange('naam')}
                  error={!!errors.naam}
                  helperText={errors.naam}
                  required
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  label="E-mail"
                  type="email"
                  value={formData.email}
                  onChange={handleChange('email')}
                  error={!!errors.email}
                  helperText={errors.email}
                  required
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  label="Telefoonnummer"
                  type="tel"
                  value={formData.telefoon}
                  onChange={handleChange('telefoon')}
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  label="Bericht"
                  multiline
                  rows={6}
                  value={formData.bericht}
                  onChange={handleChange('bericht')}
                  error={!!errors.bericht}
                  helperText={errors.bericht}
                  required
                  sx={{ mb: 3 }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={submitting}
                  sx={{
                    bgcolor: brandColors.primary,
                    py: 1.5,
                    fontSize: '1rem',
                    fontWeight: 600,
                    '&:hover': { bgcolor: brandColors.primaryDark },
                  }}
                >
                  {submitting ? 'Versturen...' : 'Versturen'}
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          bgcolor: '#333',
          color: 'white',
          textAlign: 'center',
          py: 3,
          mt: 6,
        }}
      >
        <Typography>
          &copy; 2025 Pita Pizza Napoli - Alle rechten voorbehouden
        </Typography>
      </Box>
    </Box>
  )
}

export default ContactPage

