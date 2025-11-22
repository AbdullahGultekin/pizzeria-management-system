import { useState } from 'react'
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
  Link,
} from '@mui/material'
import { customerAPI } from '../services/api'
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
  const navigate = useNavigate()
  const [tab, setTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resendEmail, setResendEmail] = useState('')
  const [resendLoading, setResendLoading] = useState(false)

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
      const errorMsg = getErrorMessage(err)
      setError(errorMsg)
      
      // If email not verified, show resend option
      if (errorMsg.includes('niet geverifieerd') || errorMsg.includes('verificatie')) {
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
        await customerAPI.register({
          email: registerData.email,
          password: registerData.password,
          telefoon: registerData.telefoon,
          naam: registerData.naam,
          straat: registerData.straat || undefined,
          huisnummer: registerData.huisnummer || undefined,
          plaats: registerData.plaats || undefined,
        })
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
      setError(getErrorMessage(err))
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
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
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
            onChange={(e) => setRegisterData({ ...registerData, straat: e.target.value })}
            margin="normal"
            autoComplete="street-address"
          />
          <TextField
            fullWidth
            label="Huisnummer"
            value={registerData.huisnummer}
            onChange={(e) => setRegisterData({ ...registerData, huisnummer: e.target.value })}
            margin="normal"
            autoComplete="address-line2"
          />
          <TextField
            fullWidth
            label="Plaats"
            value={registerData.plaats}
            onChange={(e) => setRegisterData({ ...registerData, plaats: e.target.value })}
            margin="normal"
            autoComplete="address-level2"
          />
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

