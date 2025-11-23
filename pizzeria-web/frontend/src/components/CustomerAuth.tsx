import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Tab,
  Tabs,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import { customerAPI, addressAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorHandler'
import { brandColors } from '../theme/colors'

interface CustomerAuthProps {
  open: boolean
  onClose: () => void
  onSuccess: (customer: any, token: string) => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

const CustomerAuth = ({ open, onClose, onSuccess }: CustomerAuthProps) => {
  const [tab, setTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resendEmail, setResendEmail] = useState('')
  const [resendLoading, setResendLoading] = useState(false)
  const [emailAlreadyExists, setEmailAlreadyExists] = useState(false)

  // Login form
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  // Register form
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    telefoon: '',
    naam: '',
    straat: '',
    huisnummer: '',
    plaats: '',
  })
  
  // Address autocomplete data
  const [straatnamen, setStraatnamen] = useState<string[]>([])
  const [postcodes, setPostcodes] = useState<string[]>([])  // List of "9120 Vrasene" format

  // Load street names and postcodes on mount
  useEffect(() => {
    const loadAddressData = async () => {
      try {
        // Load street names
        const streetsResponse = await addressAPI.getStreets()
        const streets = Array.isArray(streetsResponse) ? streetsResponse : streetsResponse.streets || []
        // Remove duplicates while preserving order
        const uniqueStreets = Array.from(new Set(streets as string[])) as string[]
        setStraatnamen(uniqueStreets)
        
        // Load postcodes
        const postcodesResponse = await addressAPI.getPostcodes()
        const postcodesList = Array.isArray(postcodesResponse) ? postcodesResponse : postcodesResponse.postcodes || []
        setPostcodes(postcodesList)
      } catch (e) {
        console.error('Error loading address data:', e)
      }
    }
    
    loadAddressData()
  }, [])

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTab(newValue)
    setError('')
    setLoginEmail('')
    setLoginPassword('')
    setRegisterData({
      email: '',
      password: '',
      confirmPassword: '',
      telefoon: '',
      naam: '',
      straat: '',
      huisnummer: '',
      plaats: '',
    })
  }
  
  // Handle street name change - add to list if new
  const handleStraatChange = async (value: string) => {
    setRegisterData({ ...registerData, straat: value })
    
    // If street is not in the list and user has typed something, add it
    if (value.trim() && !straatnamen.some(s => s.toLowerCase() === value.trim().toLowerCase())) {
      try {
        await addressAPI.addStreet(value.trim())
        // Reload street names
        const streetsResponse = await addressAPI.getStreets()
        const streets = Array.isArray(streetsResponse) ? streetsResponse : streetsResponse.streets || []
        const uniqueStreets = Array.from(new Set(streets as string[])) as string[]
        setStraatnamen(uniqueStreets)
      } catch (e) {
        // Silently fail - street might already exist or there's a server error
        console.warn('Could not add street name:', e)
      }
    }
  }

  const handleLogin = async () => {
    setError('')
    setLoading(true)

    try {
      if (!loginEmail || !loginPassword) {
        setError('Vul alle velden in')
        setLoading(false)
        return
      }

      const response = await customerAPI.login(loginEmail, loginPassword)
      
      // Store token
      localStorage.setItem('customer_token', response.access_token)
      localStorage.setItem('customer_data', JSON.stringify(response.customer))

      onSuccess(response.customer, response.access_token)
      onClose()
    } catch (err: any) {
      // Log full error for debugging
      console.error('Login error:', err)
      console.error('Error response:', err.response?.data)
      
      const errorMsg = getErrorMessage(err)
      setError(errorMsg)
      
      // If email not verified, show resend option
      if (errorMsg.includes('niet geverifieerd') || errorMsg.includes('verificatie') || err.response?.status === 403) {
        setResendEmail(loginEmail)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleResendVerification = async () => {
    if (!resendEmail) return
    
    setResendLoading(true)
    try {
      await customerAPI.resendVerification(resendEmail)
      setError('')
      alert('Verificatielink is opnieuw verzonden naar je e-mailadres.')
      setResendEmail('')
    } catch (err: any) {
      setError(getErrorMessage(err))
    } finally {
      setResendLoading(false)
    }
  }

  const handleRegister = async () => {
    setError('')
    setEmailAlreadyExists(false)
    setLoading(true)

    try {
      // Validation
      if (!registerData.email || !registerData.password || !registerData.telefoon || !registerData.naam) {
        setError('Vul alle verplichte velden in')
        setLoading(false)
        return
      }

      if (registerData.password !== registerData.confirmPassword) {
        setError('Wachtwoorden komen niet overeen')
        setLoading(false)
        return
      }

      if (registerData.password.length < 6) {
        setError('Wachtwoord moet minimaal 6 tekens lang zijn')
        setLoading(false)
        return
      }

      try {
        // Helper function to split postcode_gemeente into postcode and plaats
        const splitPostcodeGemeente = (value: string): { postcode: string; plaats: string } => {
          const parts = value.trim().split(' ', 2)
          if (parts.length >= 2) {
            return {
              postcode: parts[0],
              plaats: parts.slice(1).join(' ')
            }
          }
          return { postcode: '', plaats: '' }
        }
        
        // Prepare registration data - split postcode_gemeente into postcode and plaats
        const registrationData: {
          email: string
          password: string
          telefoon: string
          naam: string
          straat?: string
          huisnummer?: string
          postcode?: string
          plaats?: string
        } = {
          email: registerData.email.trim(),
          password: registerData.password,
          telefoon: registerData.telefoon.trim(),
          naam: registerData.naam.trim(),
        }
        
        // Only add optional fields if they have values
        if (registerData.straat && registerData.straat.trim()) {
          registrationData.straat = registerData.straat.trim()
        }
        if (registerData.huisnummer && registerData.huisnummer.trim()) {
          registrationData.huisnummer = registerData.huisnummer.trim()
        }
        if (registerData.plaats && registerData.plaats.trim()) {
          // Split postcode_gemeente format "9120 Vrasene" into postcode and plaats
          const { postcode, plaats } = splitPostcodeGemeente(registerData.plaats)
          if (postcode) {
            registrationData.postcode = postcode
          }
          if (plaats) {
            registrationData.plaats = plaats
          }
        }
        
        await customerAPI.register(registrationData)
      } catch (err: any) {
        // Check if it's the verification message (201 status)
        if (err.response?.status === 201 || err.response?.data?.detail?.includes('verificatie')) {
          // Registration successful, but email verification required
          setError('')
          // Show success message
          alert('Registratie succesvol! Controleer je e-mail om je account te verifiëren. Je kunt pas inloggen na verificatie.')
          onClose()
          return
        }
        throw err
      }
    } catch (err: any) {
      // Log full error for debugging
      console.error('Registration error:', err)
      console.error('Error response:', err.response?.data)
      
      const errorMsg = getErrorMessage(err)
      const errorDetail = err.response?.data?.detail || ''
      
      // Check if email already exists
      if (errorDetail.includes('E-mailadres is al geregistreerd') || errorDetail.includes('al geregistreerd')) {
        setEmailAlreadyExists(true)
        setError('Dit e-mailadres is al geregistreerd. Log in met je bestaande account of gebruik een ander e-mailadres.')
      } else {
        setEmailAlreadyExists(false)
        setError(errorMsg)
      }
      
      // If it's a validation error, show more details
      if (err.response?.data?.errors && Array.isArray(err.response.data.errors)) {
        const validationErrors = err.response.data.errors
        if (validationErrors.length > 0) {
          const firstError = validationErrors[0]
          setError(firstError.message || errorMsg)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tab} onChange={handleTabChange} aria-label="auth tabs">
            <Tab label="Inloggen" />
            <Tab label="Registreren" />
          </Tabs>
        </Box>
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            action={
              emailAlreadyExists ? (
                <Button
                  color="inherit"
                  size="small"
                  onClick={() => {
                    setTab(0)
                    setError('')
                    setEmailAlreadyExists(false)
                    setLoginEmail(registerData.email)
                  }}
                >
                  Inloggen
                </Button>
              ) : null
            }
          >
            {error}
            {emailAlreadyExists && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Heb je al een account? Klik op "Inloggen" om in te loggen met dit e-mailadres.
              </Typography>
            )}
          </Alert>
        )}
        
        {/* Show resend verification option if email not verified */}
        {resendEmail && tab === 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Je e-mailadres is nog niet geverifieerd. Controleer je inbox en klik op de verificatielink.
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={handleResendVerification}
              disabled={resendLoading}
              sx={{ textTransform: 'none' }}
            >
              {resendLoading ? 'Verzenden...' : 'Verificatielink opnieuw verzenden'}
            </Button>
          </Alert>
        )}

        <TabPanel value={tab} index={0}>
          <Typography variant="h6" gutterBottom>
            Inloggen met je account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Log in om je gegevens automatisch in te vullen bij bestellen
          </Typography>
          <TextField
            fullWidth
            label="E-mailadres"
            type="email"
            value={loginEmail}
            onChange={(e) => setLoginEmail(e.target.value)}
            margin="normal"
            required
            autoComplete="email"
          />
          <TextField
            fullWidth
            label="Wachtwoord"
            type="password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            margin="normal"
            required
            autoComplete="current-password"
          />
          {resendEmail && (
            <Box sx={{ mt: 2, p: 2, bgcolor: '#fff3cd', borderRadius: '8px', border: '1px solid #ffc107' }}>
              <Typography variant="body2" sx={{ mb: 1, color: '#856404' }}>
                Je e-mailadres is nog niet geverifieerd. Klik op de link in je inbox of vraag een nieuwe link aan.
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleResendVerification}
                disabled={resendLoading}
                sx={{ textTransform: 'none' }}
              >
                {resendLoading ? 'Verzenden...' : 'Verificatielink opnieuw verzenden'}
              </Button>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={tab} index={1}>
          <Typography variant="h6" gutterBottom>
            Nieuw account aanmaken
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Registreer je om sneller te bestellen en je bestelgeschiedenis te bekijken
          </Typography>
          <TextField
            fullWidth
            label="E-mailadres *"
            type="email"
            value={registerData.email}
            onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
            margin="normal"
            required
            autoComplete="email"
          />
          <TextField
            fullWidth
            label="Wachtwoord *"
            type="password"
            value={registerData.password}
            onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
            margin="normal"
            required
            autoComplete="new-password"
            helperText="Minimaal 6 tekens"
          />
          <TextField
            fullWidth
            label="Wachtwoord bevestigen *"
            type="password"
            value={registerData.confirmPassword}
            onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
            margin="normal"
            required
            autoComplete="new-password"
          />
          <TextField
            fullWidth
            label="Naam *"
            value={registerData.naam}
            onChange={(e) => setRegisterData({ ...registerData, naam: e.target.value })}
            margin="normal"
            required
            autoComplete="name"
          />
          <TextField
            fullWidth
            label="Telefoonnummer *"
            type="tel"
            value={registerData.telefoon}
            onChange={(e) => setRegisterData({ ...registerData, telefoon: e.target.value })}
            margin="normal"
            required
            autoComplete="tel"
            helperText="Alle EU landen: +32 123 45 67 89, +31 6 12345678, +49 30 12345678, etc. (ook vaste nummers)"
            placeholder="+32 123 45 67 89"
          />
          <TextField
            fullWidth
            label="Straat"
            value={registerData.straat}
            onChange={(e) => handleStraatChange(e.target.value)}
            onBlur={(e) => {
              // When user leaves field, add street if it's new
              if (e.target.value.trim() && !straatnamen.some(s => s.toLowerCase() === e.target.value.trim().toLowerCase())) {
                handleStraatChange(e.target.value)
              }
            }}
            margin="normal"
            autoComplete="street-address"
            helperText="Kies een straat uit de lijst of typ een nieuwe straatnaam"
            inputProps={{
              list: 'straatnamen-list-register',
            }}
          />
          <datalist id="straatnamen-list-register">
            {straatnamen.map((straat, index) => (
              <option key={`${straat}-${index}`} value={straat} />
            ))}
          </datalist>
          <TextField
            fullWidth
            label="Huisnummer"
            value={registerData.huisnummer}
            onChange={(e) => setRegisterData({ ...registerData, huisnummer: e.target.value })}
            margin="normal"
            autoComplete="address-line2"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Postcode en Gemeente</InputLabel>
            <Select
              value={registerData.plaats}
              onChange={(e) => setRegisterData({ ...registerData, plaats: e.target.value })}
              label="Postcode en Gemeente"
            >
              <MenuItem value="">Selecteer postcode en gemeente</MenuItem>
              {Array.isArray(postcodes) && postcodes.map((pc) => (
                <MenuItem key={pc} value={pc}>
                  {pc}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Sluiten
        </Button>
        {tab === 0 ? (
          <Button
            onClick={handleLogin}
            variant="contained"
            disabled={loading}
            sx={{ bgcolor: brandColors.primary, '&:hover': { bgcolor: brandColors.primaryDark } }}
          >
            {loading ? 'Inloggen...' : 'Inloggen'}
          </Button>
        ) : (
          <Button
            onClick={handleRegister}
            variant="contained"
            disabled={loading}
            sx={{ bgcolor: brandColors.primary, '&:hover': { bgcolor: brandColors.primaryDark } }}
          >
            {loading ? 'Registreren...' : 'Registreren'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}

export default CustomerAuth

