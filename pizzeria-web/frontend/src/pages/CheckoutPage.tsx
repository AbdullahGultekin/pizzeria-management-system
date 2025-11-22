import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableFooter,
  Paper,
  Button,
  TextField,
  Grid,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  AppBar,
  Toolbar,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckIcon from '@mui/icons-material/Check'
import PhoneIcon from '@mui/icons-material/Phone'
import EmailIcon from '@mui/icons-material/Email'
import { orderAPI, customerAPI, addressAPI, settingsAPI } from '../services/api'
import { brandColors } from '../theme/colors'
import { getErrorMessage, formatValidationErrors } from '../utils/errorHandler'
import CustomerAuth from '../components/CustomerAuth'

interface CartItem {
  id: string
  product_id: number
  naam: string
  prijs: number
  aantal: number
  categorie: string
  extras?: any
}

interface CustomerData {
  naam: string
  telefoon: string
  email: string
  straat: string
  huisnummer: string
  postcode_gemeente: string  // Combined field: "9120 Vrasene"
  betaalmethode?: string
  opmerking?: string
}


const CheckoutPage = () => {
  const navigate = useNavigate()
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [customerData, setCustomerData] = useState<CustomerData>({
    naam: '',
    telefoon: '',
    email: '',
    straat: '',
    huisnummer: '',
    postcode_gemeente: '',
    betaalmethode: '',
    opmerking: '',
  })
  const [straatnamen, setStraatnamen] = useState<string[]>([])
  const [postcodes, setPostcodes] = useState<string[]>([])  // List of "9120 Vrasene" format
  const [deliveryZones, setDeliveryZones] = useState<Record<string, number>>({})  // Municipality -> min amount
  const [errors, setErrors] = useState<Partial<CustomerData>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [orderSuccess, setOrderSuccess] = useState(false)
  const [orderNumber, setOrderNumber] = useState('')
  const [minAmountWarning, setMinAmountWarning] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [authDialogOpen, setAuthDialogOpen] = useState(false)

  useEffect(() => {
    // Load cart from localStorage
    const savedCart = localStorage.getItem('cart')
    if (savedCart) {
      try {
        const items = JSON.parse(savedCart)
        setCartItems(items)
        if (items.length === 0) {
          navigate('/cart')
        }
      } catch (e) {
        console.error('Error loading cart:', e)
        navigate('/cart')
      }
    } else {
      navigate('/cart')
    }

    // Load street names
    const loadStreets = async () => {
      try {
        const streets = await addressAPI.getStreets()
        // Remove duplicates while preserving order
        const uniqueStreets = Array.from(new Set(streets as string[])) as string[]
        setStraatnamen(uniqueStreets)
      } catch (e) {
        console.error('Error loading streets:', e)
      }
    }
    
    // Load postcodes/gemeentes
    const loadPostcodes = async () => {
      try {
        const postcodesList = await addressAPI.getPostcodes()
        // Ensure it's always an array
        if (Array.isArray(postcodesList)) {
          setPostcodes(postcodesList)
        } else {
          console.warn('Postcodes response is not an array:', postcodesList)
          setPostcodes([])
        }
      } catch (e) {
        console.error('Error loading postcodes:', e)
        setPostcodes([]) // Set empty array on error
      }
    }
    
    // Load delivery zones with minimum amounts
    const loadDeliveryZones = async () => {
      try {
        const zones = await settingsAPI.getDeliveryZones()
        setDeliveryZones(zones)
      } catch (e) {
        console.error('Error loading delivery zones:', e)
        setDeliveryZones({}) // Set empty object on error
      }
    }
    
    // Load customer data if logged in
    const loadCustomerData = async () => {
      const token = localStorage.getItem('customer_token')
      const savedCustomerData = localStorage.getItem('customer_data')
      
      if (token && savedCustomerData) {
        try {
          // Verify token is still valid by fetching customer data
          const customer = await customerAPI.getMe()
          setIsLoggedIn(true)
          
          // Auto-fill form with customer data
          setCustomerData({
            naam: customer.naam || '',
            telefoon: customer.telefoon || '',
            email: customer.email || '',
            straat: customer.straat || '',
            huisnummer: customer.huisnummer || '',
            postcode_gemeente: customer.plaats || '',
            betaalmethode: '',
            opmerking: '',
          })
        } catch (e) {
          // Token invalid, clear it
          localStorage.removeItem('customer_token')
          localStorage.removeItem('customer_data')
          setIsLoggedIn(false)
        }
      } else {
        setIsLoggedIn(false)
      }
    }
    
    loadStreets()
    loadPostcodes()
    loadDeliveryZones()
    loadCustomerData()
  }, [navigate])

  const getTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0)
  }

  const formatCategory = (cat: string) => {
    return cat.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatExtras = (extras: any) => {
    if (!extras) return []
    const details: string[] = []
    
    if (extras.vlees) {
      details.push(`Vlees: ${extras.vlees}`)
    }
    if (extras.bijgerecht) {
      if (Array.isArray(extras.bijgerecht)) {
        details.push(`Bijgerecht: ${extras.bijgerecht.join(', ')}`)
      } else {
        details.push(`Bijgerecht: ${extras.bijgerecht}`)
      }
    }
    if (extras.sauzen) {
      if (Array.isArray(extras.sauzen)) {
        details.push(`Sauzen: ${extras.sauzen.join(', ')}`)
      } else {
        details.push(`Sauzen: ${extras.sauzen}`)
      }
    }
    if (extras.saus1) {
      details.push(`Saus 1: ${extras.saus1}`)
    }
    if (extras.saus2) {
      details.push(`Saus 2: ${extras.saus2}`)
    }
    if (extras.garnering && Array.isArray(extras.garnering) && extras.garnering.length > 0) {
      details.push(`Extra: ${extras.garnering.join(', ')}`)
    }
    if (extras.half_half && Array.isArray(extras.half_half) && extras.half_half.length === 2) {
      details.push(`Half-half: ${extras.half_half[0]} / ${extras.half_half[1]}`)
    }
    if (extras.opmerking) {
      details.push(`Opmerking: ${extras.opmerking}`)
    }
    
    return details
  }

  const validateForm = () => {
    const newErrors: Partial<CustomerData> = {}
    
    if (!customerData.naam.trim()) {
      newErrors.naam = 'Naam is verplicht'
    }
    
    if (!customerData.telefoon.trim()) {
      newErrors.telefoon = 'Telefoonnummer is verplicht'
    } else {
      const phoneRegex = /^[0-9+\s()-]{8,}$/
      if (!phoneRegex.test(customerData.telefoon.trim())) {
        newErrors.telefoon = 'Ongeldig telefoonnummer'
      }
    }
    
    if (!customerData.email.trim()) {
      newErrors.email = 'E-mail is verplicht'
    } else if (!/\S+@\S+\.\S+/.test(customerData.email.trim())) {
      newErrors.email = 'Ongeldig e-mailadres'
    }
    
    if (!customerData.straat.trim()) {
      newErrors.straat = 'Straat is verplicht'
    }
    
    if (!customerData.huisnummer.trim()) {
      newErrors.huisnummer = 'Huisnummer is verplicht'
    }
    
    if (!customerData.postcode_gemeente.trim()) {
      newErrors.postcode_gemeente = 'Postcode en gemeente zijn verplicht'
    } else {
      // Check minimum amount
      const parts = customerData.postcode_gemeente.trim().split(' ', 2)
      const gemeente = parts.length > 1 ? parts.slice(1).join(' ') : ''
      
      if (gemeente && deliveryZones && Object.keys(deliveryZones).length > 0) {
        const matchingGemeente = Object.keys(deliveryZones).find(
          zone => zone.toLowerCase() === gemeente.toLowerCase()
        )
        
        if (matchingGemeente) {
          const minAmount = deliveryZones[matchingGemeente]
          const total = getTotal()
          
          if (total < minAmount) {
            const difference = (minAmount - total).toFixed(2)
            newErrors.postcode_gemeente = `Minimum leveringsbedrag voor ${gemeente} is €${minAmount.toFixed(2)}. Uw bestelling is €${difference} te laag.`
          }
        }
      }
    }
    
    if (!customerData.betaalmethode) {
      newErrors.betaalmethode = 'Betaalmethode is verplicht'
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
      // Find or create customer
      let customer
      try {
        const existingCustomer = await customerAPI.getByPhone(customerData.telefoon)
        // Check if customer exists and has valid id
        if (existingCustomer && typeof existingCustomer === 'object' && 'id' in existingCustomer && existingCustomer.id) {
          // Split postcode_gemeente into postcode and plaats
          const { postcode, plaats } = splitPostcodeGemeente(customerData.postcode_gemeente)
          // Update customer if exists
          customer = await customerAPI.update(existingCustomer.id, {
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            postcode: postcode,
            plaats: plaats,
          })
        } else {
          // Customer doesn't exist or invalid response, create new one
          const { postcode, plaats } = splitPostcodeGemeente(customerData.postcode_gemeente)
          customer = await customerAPI.create({
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            postcode: postcode,
            plaats: plaats,
          })
        }
      } catch (err: any) {
        // If 404 or 400, customer doesn't exist - create new one
        if (err.response?.status === 404 || err.response?.status === 400) {
          const { postcode, plaats } = splitPostcodeGemeente(customerData.postcode_gemeente)
          customer = await customerAPI.create({
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            postcode: postcode,
            plaats: plaats,
          })
        } else {
          // Re-throw other errors
          throw err
        }
      }

      // Create order
      const orderItems = cartItems.map((item) => ({
        product_id: item.product_id,
        product_naam: item.naam,
        aantal: item.aantal,
        prijs: item.prijs,
        opmerking: item.extras?.opmerking || null,
        extras: item.extras || null,
      }))

      const totaal = getTotal()

      const order = await orderAPI.createPublic({
        klant_id: customer.id,
        items: orderItems,
        opmerking: customerData.opmerking || null,
        totaal: totaal,
        betaalmethode: customerData.betaalmethode || 'cash',
      })

      setOrderNumber(order.bonnummer || '')
      setOrderSuccess(true)
      
      // Clear cart
      localStorage.removeItem('cart')
      setCartItems([])

      // Redirect to status page after 3 seconds
      setTimeout(() => {
        navigate(`/status?bonnummer=${order.bonnummer}`)
      }, 3000)
    } catch (err: any) {
      console.error('Error placing order:', err)
      const errorMsg = getErrorMessage(err)
      const validationErrors = formatValidationErrors(err)
      setError(errorMsg)
      if (validationErrors) {
        setErrors(validationErrors as Partial<CustomerData>)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (field: keyof CustomerData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | { target: { value: string } }
  ) => {
    const value = e.target.value
    setCustomerData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
    
    // Check minimum amount when postcode_gemeente changes
    if (field === 'postcode_gemeente' && value) {
      checkMinimumAmount(value)
    }
  }
  
  const checkMinimumAmount = (postcodeGemeente: string) => {
    if (!postcodeGemeente || !deliveryZones || Object.keys(deliveryZones).length === 0) {
      setMinAmountWarning('')
      return
    }
    
    // Extract gemeente from "9120 Vrasene" format
    const parts = postcodeGemeente.trim().split(' ', 2)
    const gemeente = parts.length > 1 ? parts.slice(1).join(' ') : ''
    
    if (!gemeente) {
      setMinAmountWarning('')
      return
    }
    
    // Find matching municipality (case-insensitive)
    const matchingGemeente = Object.keys(deliveryZones).find(
      zone => zone.toLowerCase() === gemeente.toLowerCase()
    )
    
    if (matchingGemeente) {
      const minAmount = deliveryZones[matchingGemeente]
      const total = getTotal()
      
      if (total < minAmount) {
        const difference = (minAmount - total).toFixed(2)
        setMinAmountWarning(
          `Waarschuwing: Het minimum leveringsbedrag voor ${gemeente} is €${minAmount.toFixed(2)}. Uw bestelling is €${difference} te laag.`
        )
      } else {
        setMinAmountWarning('')
      }
    } else {
      setMinAmountWarning('')
    }
  }
  
  // Check minimum amount when cart changes or postcode is selected
  useEffect(() => {
    if (customerData.postcode_gemeente) {
      checkMinimumAmount(customerData.postcode_gemeente)
    }
  }, [cartItems, customerData.postcode_gemeente, deliveryZones])

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

  if (orderSuccess) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Container maxWidth="sm">
          <Paper sx={{ p: 4, textAlign: 'center', borderRadius: '17px' }}>
            <CheckIcon sx={{ fontSize: 60, color: '#4caf50', mb: 2 }} />
            <Typography variant="h4" sx={{ color: brandColors.primary, fontWeight: 700, mb: 2 }}>
              Bestelling geplaatst!
            </Typography>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Bonnummer: {orderNumber}
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              Uw bestelling is succesvol geplaatst. U wordt doorgestuurd naar de status pagina...
            </Typography>
          </Paper>
        </Container>
      </Box>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa' }}>
      {/* Header */}
      <AppBar position="sticky" className="navbar-light" sx={{ bgcolor: '#fff', color: '#333', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Toolbar className="navbar-container" sx={{ maxWidth: '1300px', margin: '0 auto', width: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            <Box
              component="a"
              href="/"
              onClick={(e) => {
                e.preventDefault()
                navigate('/')
              }}
              sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', textDecoration: 'none' }}
            >
              <Box
                component="img"
                src="/LOGO-MAGNEET.jpg"
                alt="Pita Pizza Napoli Logo"
                onError={(e) => {
                  const target = e.target as HTMLImageElement
                  target.style.display = 'none'
                }}
                sx={{
                  height: '70px',
                  width: '70px',
                  borderRadius: '50%',
                  objectFit: 'cover',
                  border: '3px solid brandColors.primary',
                  boxShadow: '0 2px 8px rgba(229, 37, 37, 0.2)',
                  mr: 2,
                }}
              />
              <Box>
                <Typography variant="h5" component="div" sx={{ color: brandColors.primary, fontWeight: 800, lineHeight: 1.2 }}>
                  Pita Pizza Napoli
                </Typography>
                <Typography variant="caption" sx={{ color: '#666', fontSize: '0.85rem' }}>
                  Brugstraat 12, 9120 Vrasene
                </Typography>
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: brandColors.primary, fontWeight: 500 }}>
              <PhoneIcon sx={{ fontSize: '1.1em' }} /> 03 775 72 28
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: brandColors.primary, fontWeight: 500 }}>
              <EmailIcon sx={{ fontSize: '1.1em' }} /> info@pitapizzanapoli.be
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, ml: 3 }}>
            <Button
              variant="text"
              onClick={() => navigate('/')}
              sx={{
                color: '#333',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': { bgcolor: '#fff5f5' },
              }}
            >
              Home
            </Button>
            <Button
              variant="text"
              onClick={() => navigate('/cart')}
              sx={{
                color: '#333',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': { bgcolor: '#fff5f5' },
              }}
            >
              Winkelwagen
            </Button>
            <Button
              variant="text"
              onClick={() => navigate('/contact')}
              sx={{
                color: '#333',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': { bgcolor: '#fff5f5' },
              }}
            >
              Contact
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper
          elevation={0}
          sx={{
            bgcolor: '#fff',
            padding: '24px 30px 35px 30px',
            borderRadius: '17px',
            maxWidth: '1000px',
            margin: '0 auto',
            boxShadow: '0 3px 20px -6px rgba(180, 68, 68, 0.3)',
          }}
        >
          <Typography
            variant="h4"
            sx={{
              color: brandColors.primary,
              marginTop: 0,
              fontSize: '2.1em',
              fontWeight: 700,
              mb: 3,
            }}
          >
            Afrekenen
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
              {error}
            </Alert>
          )}

          {minAmountWarning && (
            <Alert severity="warning" sx={{ mb: 3, borderRadius: '10px' }}>
              {minAmountWarning}
            </Alert>
          )}

          <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 600, mb: 2 }}>
            Bestellingsoverzicht
          </Typography>

          <TableContainer sx={{ mb: 4 }}>
            <Table sx={{ width: '100%', borderCollapse: 'collapse' }}>
              <TableHead>
                <TableRow sx={{ bgcolor: '#fff7f6' }}>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    Product
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    Details
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    Aantal
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    Prijs
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cartItems.map((item) => {
                  const extras = formatExtras(item.extras)
                  return (
                    <TableRow key={item.id}>
                      <TableCell sx={{ py: 2, verticalAlign: 'top' }}>
                        <Typography variant="body1" sx={{ fontWeight: 700, fontSize: { xs: '0.95rem', sm: '1.05rem' }, mb: 0.5, color: '#333' }}>
                          {item.naam || 'Onbekend product'}
                        </Typography>
                        <Typography variant="caption" sx={{ 
                          fontSize: { xs: '0.75rem', sm: '0.85rem' }, 
                          display: 'block', 
                          fontWeight: 600,
                          color: brandColors.primary,
                          mb: 0.5,
                        }}>
                          Categorie: {formatCategory(item.categorie)}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ py: 2, verticalAlign: 'top' }}>
                        {extras.length > 0 ? (
                          <Box component="ul" sx={{ 
                            listStyle: 'none', 
                            padding: 0, 
                            margin: 0, 
                            fontSize: '0.9em', 
                            color: '#555',
                            lineHeight: 1.6,
                          }}>
                            {extras.map((detail, idx) => (
                              <Box component="li" key={idx} sx={{ marginBottom: '4px' }}>
                                {detail}
                              </Box>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.9em', fontStyle: 'italic', color: '#999' }}>
                            Geen extra's
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell sx={{ py: 2 }}>{item.aantal}</TableCell>
                      <TableCell sx={{ py: 2, fontWeight: 600 }}>
                        €{(item.prijs * item.aantal).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
              <TableFooter>
                <TableRow>
                  <TableCell colSpan={3} align="right" sx={{ py: 2, fontWeight: 600 }}>
                    Totaal:
                  </TableCell>
                  <TableCell sx={{ py: 2, fontWeight: 700, color: brandColors.primary }}>
                    €{getTotal().toFixed(2)}
                  </TableCell>
                </TableRow>
              </TableFooter>
            </Table>
          </TableContainer>

          {/* Login/Register Section */}
          {!isLoggedIn && (
            <Box sx={{ mb: 3, p: 2, bgcolor: '#fff5f5', borderRadius: '10px', border: `1px solid ${brandColors.primary}`, mt: 4 }}>
              <Typography variant="body1" sx={{ mb: 2, color: '#666' }}>
                <strong>Tip:</strong> Log in of registreer je om je gegevens automatisch in te vullen bij volgende bestellingen.
              </Typography>
              <Button
                variant="contained"
                onClick={() => setAuthDialogOpen(true)}
                sx={{
                  bgcolor: brandColors.primary,
                  '&:hover': { bgcolor: brandColors.primaryDark },
                  textTransform: 'none',
                  fontWeight: 600,
                }}
              >
                Inloggen / Registreren
              </Button>
            </Box>
          )}

          {isLoggedIn && (
            <Box sx={{ mb: 3, p: 2, bgcolor: '#e8f5e9', borderRadius: '10px', border: '1px solid #4caf50', mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body1" sx={{ color: '#2e7d32', fontWeight: 500 }}>
                  ✓ Ingelogd als {customerData.naam || customerData.email}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    localStorage.removeItem('customer_token')
                    localStorage.removeItem('customer_data')
                    setIsLoggedIn(false)
                    setCustomerData({
                      naam: '',
                      telefoon: '',
                      email: '',
                      straat: '',
                      huisnummer: '',
                      postcode_gemeente: '',
                      betaalmethode: '',
                      opmerking: '',
                    })
                  }}
                  sx={{ textTransform: 'none' }}
                >
                  Uitloggen
                </Button>
              </Box>
            </Box>
          )}

          <form onSubmit={handleSubmit}>
            <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 600, mb: 2, mt: 4 }}>
              Bezorggegevens
            </Typography>

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Naam *"
                  value={customerData.naam}
                  onChange={handleChange('naam')}
                  error={!!errors.naam}
                  helperText={errors.naam}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Telefoonnummer *"
                  type="tel"
                  value={customerData.telefoon}
                  onChange={handleChange('telefoon')}
                  error={!!errors.telefoon}
                  helperText={errors.telefoon || "Alle EU landen: +32 123 45 67 89, +31 6 12345678, +49 30 12345678, etc. (ook vaste nummers)"}
                  required
                  placeholder="+32 123 45 67 89"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="E-mail *"
                  type="email"
                  value={customerData.email}
                  onChange={handleChange('email')}
                  error={!!errors.email}
                  helperText={errors.email}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={8}>
                <TextField
                  fullWidth
                  label="Bezorgadres *"
                  value={customerData.straat}
                  onChange={handleChange('straat')}
                  error={!!errors.straat}
                  helperText={errors.straat || 'Kies een straat uit de lijst en vul je huisnummer in'}
                  required
                  inputProps={{
                    list: 'straatnamen-list',
                  }}
                />
                       <datalist id="straatnamen-list">
                         {straatnamen.map((straat, index) => (
                           <option key={`${straat}-${index}`} value={straat} />
                         ))}
                       </datalist>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Huisnummer *"
                  value={customerData.huisnummer}
                  onChange={handleChange('huisnummer')}
                  error={!!errors.huisnummer}
                  helperText={errors.huisnummer}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth required error={!!errors.postcode_gemeente}>
                  <InputLabel>Postcode en Gemeente *</InputLabel>
                  <Select
                    value={customerData.postcode_gemeente}
                    onChange={(e) => handleChange('postcode_gemeente')({ target: { value: e.target.value } })}
                    label="Postcode en Gemeente *"
                  >
                    <MenuItem value="">Selecteer postcode en gemeente</MenuItem>
                    {Array.isArray(postcodes) && postcodes.map((pc) => (
                      <MenuItem key={pc} value={pc}>
                        {pc}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.postcode_gemeente && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.75 }}>
                      {errors.postcode_gemeente}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth required error={!!errors.betaalmethode}>
                  <InputLabel>Betaalmethode *</InputLabel>
                  <Select
                    value={customerData.betaalmethode}
                    onChange={(e) => handleChange('betaalmethode')({ target: { value: e.target.value } })}
                    label="Betaalmethode *"
                  >
                    <MenuItem value="">Selecteer een betaalmethode</MenuItem>
                    <MenuItem value="cash">💰 Contant bij bezorging</MenuItem>
                    <MenuItem value="bancontact">💳 Bancontact bij bezorging</MenuItem>
                  </Select>
                  {errors.betaalmethode && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.75 }}>
                      {errors.betaalmethode}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Opmerking (optioneel)"
                  multiline
                  rows={3}
                  value={customerData.opmerking}
                  onChange={handleChange('opmerking')}
                />
              </Grid>
            </Grid>

            <Box sx={{ display: 'flex', gap: 2, mt: 4, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/cart')}
                sx={{
                  borderColor: '#ffdbdb',
                  color: brandColors.primary,
                  fontWeight: 600,
                  padding: '10px 19px',
                  borderRadius: '19px',
                  fontSize: '1.06em',
                  '&:hover': {
                    borderColor: brandColors.primary,
                    bgcolor: '#fff5f5',
                  },
                }}
              >
                Terug naar winkelwagen
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<CheckIcon />}
                disabled={submitting}
                sx={{
                  bgcolor: brandColors.primary,
                  color: '#fff',
                  fontWeight: 600,
                  padding: '10px 19px',
                  borderRadius: '19px',
                  fontSize: '1.06em',
                  '&:hover': { bgcolor: '#a42323' },
                  '&:disabled': { bgcolor: '#ccc' },
                }}
              >
                {submitting ? 'Plaatsen...' : 'Bestelling plaatsen'}
              </Button>
            </Box>
          </form>
        </Paper>
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          textAlign: 'center',
          color: '#ad2929',
          padding: '17px 0',
          marginTop: '36px',
          fontSize: '0.96em',
        }}
      >
        &copy; 2025 Pita Pizza Napoli - Brugstraat 12, 9120 Vrasene
      </Box>

      {/* Customer Auth Dialog */}
      <CustomerAuth
        open={authDialogOpen}
        onClose={() => setAuthDialogOpen(false)}
        onSuccess={(customer, token) => {
          setIsLoggedIn(true)
          setCustomerData({
            naam: customer.naam || '',
            telefoon: customer.telefoon || '',
            email: customer.email || '',
            straat: customer.straat || '',
            huisnummer: customer.huisnummer || '',
            postcode_gemeente: customer.plaats || '',
            betaalmethode: '',
            opmerking: '',
          })
        }}
      />
    </Box>
  )
}

export default CheckoutPage

