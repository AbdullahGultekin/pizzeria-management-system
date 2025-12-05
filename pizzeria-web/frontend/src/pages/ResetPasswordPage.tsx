import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import { customerAPI } from '../services/api'
import { brandColors } from '../theme/colors'
import { getErrorMessage } from '../utils/errorHandler'

const ResetPasswordPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [passwordErrors, setPasswordErrors] = useState<string[]>([])

  useEffect(() => {
    if (!token) {
      setError('Geen reset token gevonden in de link. Vraag een nieuwe reset link aan.')
    }
  }, [token])

  const validatePassword = (password: string): string[] => {
    const errors: string[] = []
    if (password.length < 8) {
      errors.push('Minimaal 8 tekens')
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Minimaal één hoofdletter')
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Minimaal één kleine letter')
    }
    if (!/\d/.test(password)) {
      errors.push('Minimaal één cijfer')
    }
    if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
      errors.push('Minimaal één speciaal teken (!@#$%^&*()_+-=[]{}|;:,.<>?)')
    }
    return errors
  }

  const handlePasswordChange = (value: string) => {
    setNewPassword(value)
    if (value) {
      const errors = validatePassword(value)
      setPasswordErrors(errors)
    } else {
      setPasswordErrors([])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!token) {
      setError('Geen reset token gevonden. Vraag een nieuwe reset link aan.')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Wachtwoorden komen niet overeen.')
      return
    }

    const errors = validatePassword(newPassword)
    if (errors.length > 0) {
      setError('Wachtwoord voldoet niet aan de vereisten.')
      return
    }

    setLoading(true)

    try {
      const result = await customerAPI.resetPassword(token, newPassword)
      setSuccess(true)
    } catch (err: any) {
      console.error('Reset password error:', err)
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
            onClick={() => navigate('/forgot-password')}
            sx={{
              mb: 2,
              color: brandColors.primary,
              textTransform: 'none',
            }}
          >
            Terug
          </Button>

          {success ? (
            <Box sx={{ textAlign: 'center' }}>
              <CheckCircleIcon sx={{ fontSize: 60, color: '#4caf50', mb: 2 }} />
              <Typography variant="h4" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
                Wachtwoord gereset!
              </Typography>
              <Alert severity="success" sx={{ mb: 3, borderRadius: '10px' }}>
                Je wachtwoord is succesvol gereset. Je kunt nu inloggen met je nieuwe wachtwoord.
              </Alert>
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
                Ga naar inloggen
              </Button>
            </Box>
          ) : (
            <>
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                {!token ? (
                  <ErrorIcon sx={{ fontSize: 60, color: '#f44336', mb: 2 }} />
                ) : (
                  <Typography variant="h4" sx={{ mb: 2, color: brandColors.primary, fontWeight: 700 }}>
                Nieuw wachtwoord instellen
              </Typography>
                )}
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
                  {error}
                </Alert>
              )}

              {!token ? (
                <Box sx={{ textAlign: 'center' }}>
                  <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
                    Geen reset token gevonden in de link. Vraag een nieuwe reset link aan.
                  </Alert>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/forgot-password')}
                    sx={{
                      bgcolor: brandColors.primary,
                      '&:hover': { bgcolor: brandColors.primaryDark },
                      textTransform: 'none',
                      fontWeight: 600,
                    }}
                  >
                    Nieuwe reset link aanvragen
                  </Button>
                </Box>
              ) : (
                <form onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    label="Nieuw wachtwoord"
                    type={showPassword ? 'text' : 'password'}
                    variant="outlined"
                    margin="normal"
                    value={newPassword}
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    required
                    autoFocus
                    error={passwordErrors.length > 0 && newPassword.length > 0}
                    helperText={
                      passwordErrors.length > 0 && newPassword.length > 0
                        ? passwordErrors[0]
                        : ''
                    }
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Bevestig wachtwoord"
                    type={showConfirmPassword ? 'text' : 'password'}
                    variant="outlined"
                    margin="normal"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    error={confirmPassword.length > 0 && newPassword !== confirmPassword}
                    helperText={
                      confirmPassword.length > 0 && newPassword !== confirmPassword
                        ? 'Wachtwoorden komen niet overeen'
                        : ''
                    }
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            edge="end"
                          >
                            {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ mb: 3 }}
                  />

                  {passwordErrors.length > 0 && newPassword.length > 0 && (
                    <Box sx={{ mb: 3, p: 2, bgcolor: '#fff3cd', borderRadius: '10px' }}>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                        Wachtwoord moet bevatten:
                      </Typography>
                      <Box component="ul" sx={{ m: 0, pl: 2 }}>
                        {passwordErrors.map((err, index) => (
                          <li key={index}>
                            <Typography
                              variant="body2"
                              sx={{ color: passwordErrors.length === 0 ? '#4caf50' : '#f44336' }}
                            >
                              {err}
                            </Typography>
                          </li>
                        ))}
                      </Box>
                    </Box>
                  )}

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading || passwordErrors.length > 0 || newPassword !== confirmPassword}
                    sx={{
                      bgcolor: brandColors.primary,
                      '&:hover': { bgcolor: brandColors.primaryDark },
                      '&:disabled': { bgcolor: '#ccc' },
                      textTransform: 'none',
                      fontWeight: 600,
                      py: 1.5,
                      mb: 2,
                    }}
                  >
                    {loading ? (
                      <>
                        <CircularProgress size={20} sx={{ mr: 1, color: 'white' }} />
                        Resetten...
                      </>
                    ) : (
                      'Wachtwoord resetten'
                    )}
                  </Button>
                </form>
              )}
            </>
          )}
        </Paper>
      </Container>
    </Box>
  )
}

export default ResetPasswordPage


