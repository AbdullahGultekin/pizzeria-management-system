import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import EmailIcon from '@mui/icons-material/Email'
import { customerAPI } from '../services/api'
import { brandColors } from '../theme/colors'
import { getErrorMessage } from '../utils/errorHandler'

const ForgotPasswordPage = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await customerAPI.forgotPassword(email)
      setSuccess(true)
    } catch (err: any) {
      console.error('Forgot password error:', err)
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa', display: 'flex', alignItems: 'center', py: 4 }}>
      <Container maxWidth="sm">
        <Paper
          sx={{
            p: 4,
            borderRadius: '17px',
            boxShadow: '0 3px 20px -6px rgba(180, 68, 68, 0.3)',
          }}
        >
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(-1)}
            sx={{
              mb: 2,
              color: brandColors.primary,
              textTransform: 'none',
            }}
          >
            Terug
          </Button>

          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <EmailIcon sx={{ fontSize: 60, color: brandColors.primary, mb: 2 }} />
            <Typography variant="h4" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
              Wachtwoord vergeten?
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Geen probleem! Vul je e-mailadres in en we sturen je een link om je wachtwoord te resetten.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
              {error}
            </Alert>
          )}

          {success ? (
            <Box>
              <Alert severity="success" sx={{ mb: 3, borderRadius: '10px' }}>
                Als dit e-mailadres geregistreerd is, is er een wachtwoord reset link verzonden.
                Controleer je inbox (en spam folder) voor verdere instructies.
              </Alert>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                De reset link is 1 uur geldig.
              </Typography>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/checkout')}
                sx={{
                  bgcolor: brandColors.primary,
                  '&:hover': { bgcolor: brandColors.primaryDark },
                  textTransform: 'none',
                  fontWeight: 600,
                  py: 1.5,
                }}
              >
                Terug naar checkout
              </Button>
            </Box>
          ) : (
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="E-mailadres"
                type="email"
                variant="outlined"
                margin="normal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{
                  bgcolor: brandColors.primary,
                  '&:hover': { bgcolor: brandColors.primaryDark },
                  textTransform: 'none',
                  fontWeight: 600,
                  py: 1.5,
                  mb: 2,
                }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1, color: 'white' }} />
                    Verzenden...
                  </>
                ) : (
                  'Reset link verzenden'
                )}
              </Button>

              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Weet je je wachtwoord weer?{' '}
                  <Link
                    to="/checkout"
                    style={{
                      color: brandColors.primary,
                      textDecoration: 'none',
                      fontWeight: 600,
                    }}
                  >
                    Terug naar inloggen
                  </Link>
                </Typography>
              </Box>
            </form>
          )}

          <Box sx={{ mt: 4, p: 2, bgcolor: '#f5f5f5', borderRadius: '10px' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 600 }}>
              Wachtwoord vereisten:
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2 }}>
              <li>Minimaal 8 tekens</li>
              <li>Minimaal één hoofdletter</li>
              <li>Minimaal één kleine letter</li>
              <li>Minimaal één cijfer</li>
              <li>Minimaal één speciaal teken (!@#$%^&*()_+-=[]&#123;&#125;|;:,.&lt;&gt;?)</li>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}

export default ForgotPasswordPage

