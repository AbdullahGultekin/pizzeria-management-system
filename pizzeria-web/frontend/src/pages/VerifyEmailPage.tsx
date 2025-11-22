import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import { customerAPI } from '../services/api'
import { brandColors } from '../theme/colors'

const VerifyEmailPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Geen verificatietoken gevonden in de link.')
      return
    }

    const verifyEmail = async () => {
      try {
        const result = await customerAPI.verifyEmail(token)
        setStatus('success')
        setMessage(result.message || 'E-mailadres succesvol geverifieerd!')
        setEmail(result.email || '')
      } catch (error: any) {
        setStatus('error')
        setMessage(
          error.response?.data?.detail ||
          error.message ||
          'Verificatie mislukt. De link is mogelijk verlopen of ongeldig.'
        )
      }
    }

    verifyEmail()
  }, [token])

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa', display: 'flex', alignItems: 'center', py: 4 }}>
      <Container maxWidth="sm">
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            borderRadius: '17px',
            boxShadow: '0 3px 20px -6px rgba(180, 68, 68, 0.3)',
          }}
        >
          {status === 'loading' && (
            <>
              <CircularProgress sx={{ mb: 3, color: brandColors.primary }} />
              <Typography variant="h5" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
                E-mailadres verifiëren...
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Even geduld, we verifiëren je e-mailadres.
              </Typography>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircleIcon sx={{ fontSize: 60, color: '#4caf50', mb: 2 }} />
              <Typography variant="h5" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
                E-mailadres geverifieerd!
              </Typography>
              <Alert severity="success" sx={{ mb: 3, borderRadius: '10px' }}>
                {message}
              </Alert>
              {email && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Geverifieerd: {email}
                </Typography>
              )}
              <Button
                variant="contained"
                onClick={() => navigate('/checkout')}
                sx={{
                  bgcolor: brandColors.primary,
                  '&:hover': { bgcolor: brandColors.primaryDark },
                  textTransform: 'none',
                  fontWeight: 600,
                  px: 4,
                  py: 1.5,
                }}
              >
                Ga naar inloggen
              </Button>
            </>
          )}

          {status === 'error' && (
            <>
              <ErrorIcon sx={{ fontSize: 60, color: '#f44336', mb: 2 }} />
              <Typography variant="h5" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
                Verificatie mislukt
              </Typography>
              <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
                {message}
              </Alert>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/checkout')}
                  sx={{
                    borderColor: brandColors.primary,
                    color: brandColors.primary,
                    textTransform: 'none',
                    fontWeight: 600,
                  }}
                >
                  Terug naar checkout
                </Button>
                <Button
                  variant="contained"
                  onClick={() => navigate('/')}
                  sx={{
                    bgcolor: brandColors.primary,
                    '&:hover': { bgcolor: brandColors.primaryDark },
                    textTransform: 'none',
                    fontWeight: 600,
                  }}
                >
                  Naar home
                </Button>
              </Box>
            </>
          )}
        </Paper>
      </Container>
    </Box>
  )
}

export default VerifyEmailPage

