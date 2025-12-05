import { useState, useEffect } from 'react'
import { Box, Container, Typography, Button, Chip, Menu, MenuItem, IconButton } from '@mui/material'
import { useNavigate, useLocation } from 'react-router-dom'
import RestaurantIcon from '@mui/icons-material/Restaurant'
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart'
import ContactMailIcon from '@mui/icons-material/ContactMail'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import PersonIcon from '@mui/icons-material/Person'
import LoginIcon from '@mui/icons-material/Login'
import LanguageIcon from '@mui/icons-material/Language'
import LogoutIcon from '@mui/icons-material/Logout'
import { brandColors } from '../theme/colors'
import { useLanguage } from '../contexts/LanguageContext'
import CustomerAuth from './CustomerAuth'
import { Language } from '../i18n/translations'

const PublicHeader = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { language, setLanguage, t } = useLanguage()
  const [authDialogOpen, setAuthDialogOpen] = useState(false)
  const [languageMenuAnchor, setLanguageMenuAnchor] = useState<null | HTMLElement>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [customerName, setCustomerName] = useState('')

  // Check if customer is logged in
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('customer_token')
      const customerData = localStorage.getItem('customer_data')
      if (token && customerData) {
        try {
          const customer = JSON.parse(customerData)
          setIsLoggedIn(true)
          setCustomerName(customer.naam || customer.email || '')
        } catch (e) {
          setIsLoggedIn(false)
          setCustomerName('')
        }
      } else {
        setIsLoggedIn(false)
        setCustomerName('')
      }
    }
    checkAuth()
    // Check periodically
    const interval = setInterval(checkAuth, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('customer_token')
    localStorage.removeItem('customer_data')
    setIsLoggedIn(false)
    setCustomerName('')
    navigate('/')
  }

  // Opening hours logic
  const getOpeningHours = () => {
    const now = new Date()
    const day = now.getDay() // 0 = Sunday, 1 = Monday, etc.
    const hour = now.getHours()
    const minute = now.getMinutes()
    const currentTime = hour * 60 + minute

    // Opening hours: Tuesday-Sunday 17:00-20:30 (Monday closed)
    const openingTime = 17 * 60 // 17:00
    const closingTime = 20 * 60 + 30 // 20:30

    if (day === 1) { // Monday
      return { isOpen: false, status: t.closed, message: language === 'nl' ? 'Vandaag gesloten' : language === 'fr' ? 'Fermé aujourd\'hui' : 'Closed today' }
    }

    if (currentTime >= openingTime && currentTime <= closingTime) {
      return { 
        isOpen: true, 
        status: t.open, 
        message: language === 'nl' ? 'Open tot 20:30' : language === 'fr' ? 'Ouvert jusqu\'à 20:30' : 'Open until 20:30'
      }
    } else if (currentTime < openingTime) {
      return { 
        isOpen: false, 
        status: t.closed, 
        message: language === 'nl' ? 'Opent om 17:00' : language === 'fr' ? 'Ouvre à 17:00' : 'Opens at 17:00'
      }
    } else {
      return { 
        isOpen: false, 
        status: t.closed, 
        message: language === 'nl' ? 'Vandaag gesloten' : language === 'fr' ? 'Fermé aujourd\'hui' : 'Closed today'
      }
    }
  }

  const openingStatus = getOpeningHours()

  const openingstijden: { [key: number]: string } = {
    0: '17:00 - 20:30',
    1: t.closed,
    2: '17:00 - 20:30',
    3: '17:00 - 20:30',
    4: '17:00 - 20:30',
    5: '17:00 - 20:30',
    6: '17:00 - 20:30',
  }

  const getTodayHours = () => {
    const today = new Date().getDay()
    return openingstijden[today] || t.closed
  }

  const getTomorrowHours = () => {
    const tomorrow = (new Date().getDay() + 1) % 7
    return openingstijden[tomorrow] || t.closed
  }

  return (
    <>
      {/* Header - Modern Style */}
      <Box sx={{ 
        bgcolor: '#fff', 
        borderBottom: `2px solid ${brandColors.primary}`,
        boxShadow: `0 2px 10px ${brandColors.primary}20`,
        position: 'sticky',
        top: 0,
        zIndex: 1000,
      }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', alignItems: 'center', py: 2.5, gap: 3, flexWrap: { xs: 'wrap', md: 'nowrap' } }}>
            {/* Logo */}
            <Box
              component="img"
              src="/LOGO-MAGNEET.jpg"
              alt="Pita Pizza Napoli Logo"
              onError={(e) => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
              }}
              onClick={() => navigate('/')}
              sx={{
                height: { xs: '70px', sm: '90px' },
                width: { xs: '70px', sm: '90px' },
                borderRadius: '50%',
                objectFit: 'cover',
                border: `4px solid ${brandColors.primary}`,
                boxShadow: `0 4px 15px ${brandColors.primary}50`,
                flexShrink: 0,
                transition: 'transform 0.3s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'scale(1.05)',
                },
              }}
            />
            
            {/* Restaurant Info */}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography 
                variant="h4" 
                component="h1" 
                sx={{ 
                  color: brandColors.primary, 
                  fontWeight: 800, 
                  fontSize: { xs: '1.5rem', sm: '1.8rem', md: '2rem' },
                  mb: 0.5,
                  letterSpacing: '-0.5px',
                  textShadow: '0 2px 4px rgba(229, 37, 37, 0.1)',
                }}
              >
                Pita Pizza Napoli
              </Typography>
              <Typography variant="body2" sx={{ color: '#666', fontSize: { xs: '0.85rem', sm: '0.95rem' }, fontWeight: 500, mb: 1 }}>
                Brugstraat 12, 9120 Vrasene
              </Typography>
              {/* Opening Status */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={openingStatus.isOpen ? <CheckCircleIcon /> : <CancelIcon />}
                  label={openingStatus.status}
                  sx={{
                    bgcolor: openingStatus.isOpen ? '#4caf50' : '#f44336',
                    color: '#fff',
                    fontWeight: 700,
                    fontSize: '0.75rem',
                    height: '24px',
                  }}
                />
                <Typography variant="caption" sx={{ color: '#666', fontSize: '0.8rem', fontWeight: 500 }}>
                  {openingStatus.message}
                </Typography>
              </Box>
            </Box>

            {/* Opening Hours & Actions */}
            <Box sx={{ display: { xs: 'none', lg: 'flex' }, flexDirection: 'column', alignItems: 'flex-end', gap: 2, flexShrink: 0 }}>
              {/* Opening Hours */}
              <Box sx={{ textAlign: 'right' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5, justifyContent: 'flex-end' }}>
                  <AccessTimeIcon sx={{ color: brandColors.primary, fontSize: '1rem' }} />
                  <Typography variant="body2" sx={{ fontWeight: 700, color: brandColors.primary, fontSize: '0.95rem' }}>
                    {t.openingHours}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: '#666', fontSize: '0.9rem', fontWeight: 500, mb: 0.25 }}>
                  {t.today}: {getTodayHours()}
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', fontSize: '0.9rem', fontWeight: 500 }}>
                  {t.tomorrow}: {getTomorrowHours()}
                </Typography>
              </Box>
              
              {/* Language & Auth Buttons */}
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                {/* Language Selector */}
                <IconButton
                  onClick={(e) => setLanguageMenuAnchor(e.currentTarget)}
                  sx={{
                    color: brandColors.primary,
                    border: `1px solid ${brandColors.primary}`,
                    '&:hover': { bgcolor: `${brandColors.primary}10` },
                  }}
                  size="small"
                  title={t.language}
                >
                  <LanguageIcon />
                </IconButton>
                <Menu
                  anchorEl={languageMenuAnchor}
                  open={Boolean(languageMenuAnchor)}
                  onClose={() => setLanguageMenuAnchor(null)}
                >
                  <MenuItem
                    selected={language === 'nl'}
                    onClick={() => {
                      setLanguage('nl')
                      setLanguageMenuAnchor(null)
                    }}
                  >
                    {t.dutch}
                  </MenuItem>
                  <MenuItem
                    selected={language === 'fr'}
                    onClick={() => {
                      setLanguage('fr')
                      setLanguageMenuAnchor(null)
                    }}
                  >
                    {t.french}
                  </MenuItem>
                  <MenuItem
                    selected={language === 'en'}
                    onClick={() => {
                      setLanguage('en')
                      setLanguageMenuAnchor(null)
                    }}
                  >
                    {t.english}
                  </MenuItem>
                </Menu>
                
                {/* Login/Register or Account */}
                {isLoggedIn ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Button
                      startIcon={<PersonIcon />}
                      onClick={() => navigate('/checkout')}
                      sx={{
                        textTransform: 'none',
                        color: brandColors.primary,
                        borderColor: brandColors.primary,
                        '&:hover': { bgcolor: `${brandColors.primary}10` },
                      }}
                      variant="outlined"
                      size="small"
                    >
                      {customerName || t.myAccount}
                    </Button>
                    <IconButton
                      onClick={handleLogout}
                      sx={{
                        color: brandColors.primary,
                        '&:hover': { bgcolor: `${brandColors.primary}10` },
                      }}
                      size="small"
                      title={t.logout}
                    >
                      <LogoutIcon />
                    </IconButton>
                  </Box>
                ) : (
                  <Button
                    startIcon={<LoginIcon />}
                    onClick={() => setAuthDialogOpen(true)}
                    sx={{
                      textTransform: 'none',
                      bgcolor: brandColors.primary,
                      color: '#fff',
                      '&:hover': { bgcolor: brandColors.primaryDark },
                    }}
                    variant="contained"
                    size="small"
                  >
                    {t.login}
                  </Button>
                )}
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Navigation Menu */}
      <Box sx={{ 
        bgcolor: '#f8f8f8', 
        borderBottom: '1px solid #e0e0e0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', gap: 0, alignItems: 'center' }}>
            <Button
              startIcon={<RestaurantIcon />}
              onClick={() => navigate('/')}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                color: location.pathname === '/' || location.pathname === '/menu' ? brandColors.primary : '#666',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                borderBottom: location.pathname === '/' || location.pathname === '/menu' ? `3px solid ${brandColors.primary}` : '3px solid transparent',
                '&:hover': {
                  bgcolor: '#fff5f5',
                  color: brandColors.primary,
                },
                transition: 'all 0.2s ease',
              }}
            >
              {t.menu}
            </Button>
            <Button
              startIcon={<ShoppingCartIcon />}
              onClick={() => navigate('/cart')}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                color: location.pathname === '/cart' ? brandColors.primary : '#666',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                borderBottom: location.pathname === '/cart' ? `3px solid ${brandColors.primary}` : '3px solid transparent',
                '&:hover': {
                  bgcolor: '#fff5f5',
                  color: brandColors.primary,
                },
                transition: 'all 0.2s ease',
              }}
            >
              {t.cart}
            </Button>
            <Button
              startIcon={<LocalShippingIcon />}
              onClick={() => navigate('/track')}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                color: location.pathname === '/track' ? brandColors.primary : '#666',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                borderBottom: location.pathname === '/track' ? `3px solid ${brandColors.primary}` : '3px solid transparent',
                '&:hover': {
                  bgcolor: '#fff5f5',
                  color: brandColors.primary,
                },
                transition: 'all 0.2s ease',
              }}
            >
              {t.trackOrder}
            </Button>
            <Button
              startIcon={<ContactMailIcon />}
              onClick={() => navigate('/contact')}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                color: location.pathname === '/contact' ? brandColors.primary : '#666',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                borderBottom: location.pathname === '/contact' ? `3px solid ${brandColors.primary}` : '3px solid transparent',
                '&:hover': {
                  bgcolor: '#fff5f5',
                  color: brandColors.primary,
                },
                transition: 'all 0.2s ease',
              }}
            >
              {t.contact}
            </Button>
            
            {/* Mobile Login Button */}
            <Box sx={{ display: { xs: 'flex', lg: 'none' }, ml: 'auto', gap: 1 }}>
              <IconButton
                onClick={(e) => setLanguageMenuAnchor(e.currentTarget)}
                sx={{ color: brandColors.primary }}
                size="small"
              >
                <LanguageIcon />
              </IconButton>
              {isLoggedIn ? (
                <Button
                  startIcon={<PersonIcon />}
                  onClick={() => navigate('/checkout')}
                  sx={{
                    textTransform: 'none',
                    color: brandColors.primary,
                    fontSize: '0.9rem',
                  }}
                  size="small"
                >
                  {customerName || t.myAccount}
                </Button>
              ) : (
                <Button
                  startIcon={<LoginIcon />}
                  onClick={() => setAuthDialogOpen(true)}
                  sx={{
                    textTransform: 'none',
                    color: brandColors.primary,
                    fontSize: '0.9rem',
                  }}
                  size="small"
                >
                  {t.login}
                </Button>
              )}
            </Box>
          </Box>
        </Container>
      </Box>
      
      {/* Customer Auth Dialog */}
      <CustomerAuth
        open={authDialogOpen}
        onClose={() => setAuthDialogOpen(false)}
        onSuccess={(customer, token) => {
          setIsLoggedIn(true)
          setCustomerName(customer.naam || customer.email || '')
          setAuthDialogOpen(false)
        }}
      />
    </>
  )
}

export default PublicHeader

