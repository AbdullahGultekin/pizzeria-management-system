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
import { orderAPI, customerAPI, addressAPI, settingsAPI, paymentsAPI } from '../services/api'
import { brandColors } from '../theme/colors'
import { getErrorMessage, formatValidationErrors } from '../utils/errorHandler'
import CustomerAuth from '../components/CustomerAuth'
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { useTranslations } from '../hooks/useTranslations'

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
  const { t, translateProduct, translateCategory } = useTranslations()
  const stripe = useStripe()
  const elements = useElements()
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
  const [minAmountWarning, setMinAmountWarning] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [authDialogOpen, setAuthDialogOpen] = useState(false)
  const [paymentError, setPaymentError] = useState<string | null>(null)
  const [paymentProcessing, setPaymentProcessing] = useState(false)
  const [hasAutofillData, setHasAutofillData] = useState(false)

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
      const savedToken = localStorage.getItem('customer_token')
      const savedCustomerData = localStorage.getItem('customer_data')
      
      if (savedToken && savedCustomerData) {
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
        
        // Load saved autofill data for non-logged-in users
        try {
          const savedAutofill = localStorage.getItem('checkout_autofill')
          if (savedAutofill) {
            const autofillData = JSON.parse(savedAutofill)
            setHasAutofillData(true)
            setCustomerData(prev => ({
              ...prev,
              naam: autofillData.naam || prev.naam,
              telefoon: autofillData.telefoon || prev.telefoon,
              email: autofillData.email || prev.email,
              straat: autofillData.straat || prev.straat,
              huisnummer: autofillData.huisnummer || prev.huisnummer,
              postcode_gemeente: autofillData.postcode_gemeente || prev.postcode_gemeente,
            }))
          } else {
            setHasAutofillData(false)
          }
        } catch (e) {
          console.error('Error loading autofill data:', e)
          // Clear invalid data
          localStorage.removeItem('checkout_autofill')
          setHasAutofillData(false)
        }
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
    const translated = translateCategory(cat)
    return translated.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatExtras = (extras: any) => {
    if (!extras) return []
    const details: string[] = []
    
    if (extras.vlees) {
      details.push(`${t.meat}: ${extras.vlees}`)
    }
    if (extras.bijgerecht) {
      if (Array.isArray(extras.bijgerecht)) {
        details.push(`${t.sideDish}: ${extras.bijgerecht.join(', ')}`)
      } else {
        details.push(`${t.sideDish}: ${extras.bijgerecht}`)
      }
    }
    if (extras.sauzen) {
      if (Array.isArray(extras.sauzen)) {
        details.push(`${t.sauces}: ${extras.sauzen.join(', ')}`)
      } else {
        details.push(`${t.sauces}: ${extras.sauzen}`)
      }
    }
    if (extras.saus1) {
      details.push(`${t.sauce1}: ${extras.saus1}`)
    }
    if (extras.saus2) {
      details.push(`${t.sauce2}: ${extras.saus2}`)
    }
    if (extras.garnering && Array.isArray(extras.garnering) && extras.garnering.length > 0) {
      details.push(`${t.extra}: ${extras.garnering.join(', ')}`)
    }
    if (extras.half_half && Array.isArray(extras.half_half) && extras.half_half.length === 2) {
      details.push(`${t.halfHalf}: ${extras.half_half[0]} / ${extras.half_half[1]}`)
    }
    if (extras.opmerking) {
      details.push(`${t.remark}: ${extras.opmerking}`)
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
    setPaymentError(null)

    try {
      // Find or create customer
      let customer
      try {
        const existingCustomer = await customerAPI.getByPhone(customerData.telefoon)
        // Check if customer exists and has valid id
        if (existingCustomer && typeof existingCustomer === 'object' && 'id' in existingCustomer && existingCustomer.id) {
          // Update customer if exists - plaats contains "postcode gemeente" (e.g., "9120 Vrasene")
          customer = await customerAPI.update(existingCustomer.id, {
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            email: customerData.email, // FIX: Include email address
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            plaats: customerData.postcode_gemeente, // plaats contains "postcode gemeente"
          })
        } else {
          // Customer doesn't exist or invalid response, create new one
          // plaats contains "postcode gemeente" (e.g., "9120 Vrasene")
          customer = await customerAPI.create({
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            email: customerData.email, // FIX: Include email address
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            plaats: customerData.postcode_gemeente, // plaats contains "postcode gemeente"
          })
        }
      } catch (err: any) {
        // If 404 or 400, customer doesn't exist - create new one
        if (err.response?.status === 404 || err.response?.status === 400) {
          // Customer doesn't exist - create new one
          // plaats contains "postcode gemeente" (e.g., "9120 Vrasene")
          customer = await customerAPI.create({
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            email: customerData.email, // FIX: Include email address
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            plaats: customerData.postcode_gemeente, // plaats contains "postcode gemeente"
          })
        } else {
          // Re-throw other errors
          throw err
        }
      }

      // Create order
      // Validate and filter cart items
      if (!cartItems || cartItems.length === 0) {
        throw new Error('Geen items in winkelwagen. Voeg eerst items toe aan je winkelwagen.')
      }
      
      // Log cart items for debugging
      console.log('Cart items before creating order:', cartItems)
      console.log('Cart items count:', cartItems.length)
      
      // Filter out invalid items (items without required fields)
      const validCartItems = cartItems.filter(item => {
        const isValid = item && 
                       item.naam && 
                       item.prijs && 
                       item.prijs > 0 && 
                       item.aantal && 
                       item.aantal > 0 &&
                       item.product_id
        if (!isValid) {
          console.warn('Invalid cart item filtered out:', item)
        }
        return isValid
      })
      
      if (validCartItems.length === 0) {
        throw new Error('Geen geldige items in winkelwagen. Voeg eerst items toe aan je winkelwagen.')
      }
      
      if (validCartItems.length !== cartItems.length) {
        console.warn(`Filtered out ${cartItems.length - validCartItems.length} invalid items from cart`)
      }
      
      const orderItems = validCartItems.map((item) => ({
        product_id: item.product_id,
        product_naam: item.naam,
        aantal: item.aantal,
        prijs: item.prijs,
        opmerking: item.extras?.opmerking || null,
        extras: item.extras || null,
      }))

      console.log('Order items being sent:', orderItems)
      const totaal = validCartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0)
      console.log('Calculated total:', totaal)

      const order = await orderAPI.createPublic({
        klant_id: customer.id,
        items: orderItems,
        opmerking: customerData.opmerking || null,
        totaal: totaal,
        betaalmethode: customerData.betaalmethode || 'cash',
      })

      // Als betaalmethode Stripe/online is, eerst betaling uitvoeren
      if (customerData.betaalmethode === 'online') {
        if (!stripe || !elements) {
          throw new Error(t.language === 'nl' ? 'Betaalsysteem (Stripe) is niet beschikbaar. Probeer later opnieuw.' : t.language === 'fr' ? 'Le système de paiement (Stripe) n\'est pas disponible. Veuillez réessayer plus tard.' : 'Payment system (Stripe) is not available. Please try again later.')
        }

        setPaymentProcessing(true)

        // Maak PaymentIntent via backend
        const payment = await paymentsAPI.create(order.id, totaal)

        const card = elements.getElement(CardElement)
        if (!card) {
          throw new Error('Geen kaartveld gevonden. Vernieuw de pagina en probeer opnieuw.')
        }

        const result = await stripe.confirmCardPayment(payment.client_secret, {
          payment_method: {
            card,
            billing_details: {
              name: customerData.naam,
              email: customerData.email,
              phone: customerData.telefoon,
            },
          },
        })

        if (result.error) {
          console.error('Stripe payment error:', result.error)
          setPaymentError(result.error.message || 'Betaling mislukt. Probeer een andere kaart of betaalmethode.')
          setPaymentProcessing(false)
          // We laten de order bestaan maar tonen geen success scherm
          return
        }
      }

      // Save customer data to localStorage for autofill (only if not logged in)
      if (!isLoggedIn) {
        try {
          const dataToSave = {
            naam: customerData.naam,
            telefoon: customerData.telefoon,
            email: customerData.email,
            straat: customerData.straat,
            huisnummer: customerData.huisnummer,
            postcode_gemeente: customerData.postcode_gemeente,
            // Don't save betaalmethode and opmerking as these may change
          }
          localStorage.setItem('checkout_autofill', JSON.stringify(dataToSave))
          setHasAutofillData(true)
        } catch (e) {
          console.error('Error saving autofill data:', e)
        }
      }

      // Clear cart
      localStorage.removeItem('cart')
      setCartItems([])

      // Redirect to confirmation page with bonnummer
      navigate(`/order-confirmation?bonnummer=${order.bonnummer}`)
    } catch (err: any) {
      console.error('Error placing order:', err)
      console.error('Error details:', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        url: err.config?.url,
        method: err.config?.method,
      })
      const errorMsg = getErrorMessage(err)
      const validationErrors = formatValidationErrors(err)
      
      // Special handling for Method Not Allowed (405)
      if (err.response?.status === 405) {
        setError('De server accepteert deze actie niet. Probeer de pagina te verversen en opnieuw te proberen.')
        console.error('Method Not Allowed - Check if POST request is being sent correctly')
      } else {
        setError(errorMsg)
      }
      
      if (validationErrors) {
        setErrors(validationErrors as Partial<CustomerData>)
      }
    } finally {
      setSubmitting(false)
      setPaymentProcessing(false)
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
            {t.checkout}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
              {error}
            </Alert>
          )}

          {paymentError && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>
              {paymentError}
            </Alert>
          )}

          {minAmountWarning && (
            <Alert severity="warning" sx={{ mb: 3, borderRadius: '10px' }}>
              {minAmountWarning}
            </Alert>
          )}

          <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 600, mb: 2 }}>
            {t.orderSummary}
          </Typography>

          <TableContainer sx={{ mb: 4 }}>
            <Table sx={{ width: '100%', borderCollapse: 'collapse' }}>
              <TableHead>
                <TableRow sx={{ bgcolor: '#fff7f6' }}>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    {t.items}
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    {t.language === 'nl' ? 'Details' : t.language === 'fr' ? 'Détails' : 'Details'}
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    {t.quantity}
                  </TableCell>
                  <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                    {t.price}
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
                          {translateProduct(item.naam) || (t.language === 'nl' ? 'Onbekend product' : t.language === 'fr' ? 'Produit inconnu' : 'Unknown product')}
                        </Typography>
                        <Typography variant="caption" sx={{ 
                          fontSize: { xs: '0.75rem', sm: '0.85rem' }, 
                          display: 'block', 
                          fontWeight: 600,
                          color: brandColors.primary,
                          mb: 0.5,
                        }}>
                          {t.language === 'nl' ? 'Categorie' : t.language === 'fr' ? 'Catégorie' : 'Category'}: {translateCategory(item.categorie)}
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
                            {t.language === 'nl' ? 'Geen extra\'s' : t.language === 'fr' ? 'Aucun extra' : 'No extras'}
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
                    {t.total}:
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
                <strong>{t.tip}</strong> {t.loginRegisterTip}
                {hasAutofillData && (
                  <span style={{ display: 'block', marginTop: '8px', fontSize: '0.9em', color: '#4caf50' }}>
                    ✓ {t.dataSaved}
                  </span>
                )}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
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
                  {t.login} / {t.register}
                </Button>
                {hasAutofillData && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      localStorage.removeItem('checkout_autofill')
                      setHasAutofillData(false)
                      setCustomerData(prev => ({
                        ...prev,
                        naam: '',
                        telefoon: '',
                        email: '',
                        straat: '',
                        huisnummer: '',
                        postcode_gemeente: '',
                      }))
                    }}
                    sx={{
                      textTransform: 'none',
                      borderColor: '#999',
                      color: '#666',
                      '&:hover': {
                        borderColor: '#666',
                        bgcolor: '#f5f5f5',
                      },
                    }}
                  >
                    {t.clearSavedData}
                  </Button>
                )}
              </Box>
            </Box>
          )}

          {isLoggedIn && (
            <Box sx={{ mb: 3, p: 2, bgcolor: '#e8f5e9', borderRadius: '10px', border: '1px solid #4caf50', mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body1" sx={{ color: '#2e7d32', fontWeight: 500 }}>
                  ✓ {t.loggedInAs} {customerData.naam || customerData.email}
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
                  {t.logout}
                </Button>
              </Box>
            </Box>
          )}

          <form onSubmit={handleSubmit}>
            <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 600, mb: 2, mt: 4 }}>
              {t.deliveryAddress}
            </Typography>

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={`${t.name} *`}
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
                  label={`${t.phone} *`}
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
                  label={`${t.email} *`}
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
                  label={`${t.street} *`}
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
                  label={`${t.houseNumber} *`}
                  value={customerData.huisnummer}
                  onChange={handleChange('huisnummer')}
                  error={!!errors.huisnummer}
                  helperText={errors.huisnummer}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth required error={!!errors.postcode_gemeente}>
                  <InputLabel>{t.postcode} {t.city} *</InputLabel>
                  <Select
                    value={customerData.postcode_gemeente}
                    onChange={(e) => handleChange('postcode_gemeente')({ target: { value: e.target.value } })}
                    label={`${t.postcode} ${t.city} *`}
                  >
                    <MenuItem value="">{t.language === 'nl' ? 'Selecteer postcode en gemeente' : t.language === 'fr' ? 'Sélectionnez code postal et ville' : 'Select postcode and city'}</MenuItem>
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
                  <InputLabel>{t.paymentMethod} *</InputLabel>
                  <Select
                    value={customerData.betaalmethode}
                    onChange={(e) => handleChange('betaalmethode')({ target: { value: e.target.value } })}
                    label={`${t.paymentMethod} *`}
                  >
                    <MenuItem value="">{t.language === 'nl' ? 'Selecteer een betaalmethode' : t.language === 'fr' ? 'Sélectionnez un mode de paiement' : 'Select a payment method'}</MenuItem>
                    <MenuItem value="cash">💰 {t.language === 'nl' ? 'Contant bij bezorging' : t.language === 'fr' ? 'Espèces à la livraison' : 'Cash on delivery'}</MenuItem>
                    <MenuItem value="bancontact">💳 {t.language === 'nl' ? 'Bancontact bij bezorging' : t.language === 'fr' ? 'Bancontact à la livraison' : 'Bancontact on delivery'}</MenuItem>
                    <MenuItem value="online">🌐 {t.language === 'nl' ? 'Online betalen (kaart / Bancontact / iDEAL via Stripe)' : t.language === 'fr' ? 'Paiement en ligne (carte / Bancontact / iDEAL via Stripe)' : 'Online payment (card / Bancontact / iDEAL via Stripe)'}</MenuItem>
                  </Select>
                  {errors.betaalmethode && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.75 }}>
                      {errors.betaalmethode}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              {customerData.betaalmethode === 'online' && (
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                    {t.cardDetails}
                  </Typography>
                  <Box
                    sx={{
                      border: '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '12px',
                      bgcolor: '#fafafa',
                    }}
                  >
                    <CardElement
                      options={{
                        style: {
                          base: {
                            fontSize: '16px',
                            color: '#424770',
                            '::placeholder': {
                              color: '#aab7c4',
                            },
                          },
                          invalid: {
                            color: '#9e2146',
                          },
                        },
                      }}
                    />
                  </Box>
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#666' }}>
                    {t.paymentSecure}
                  </Typography>
                </Grid>
              )}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={`${t.notes} (${t.optional})`}
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
                {t.back} {t.cart}
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
                {submitting ? t.submitting : t.placeOrder}
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
        onSuccess={(customer) => {
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

