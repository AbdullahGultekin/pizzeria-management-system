import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Alert,
  CircularProgress,
  Snackbar,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import DeleteIcon from '@mui/icons-material/Delete'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import LocalDiningIcon from '@mui/icons-material/LocalDining'
import { menuAPI, extrasAPI, settingsAPI } from '../services/api'
import ProductModal from '../components/ProductModal'
import PublicHeader from '../components/PublicHeader'
import { useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../utils/errorHandler'
import { brandColors } from '../theme/colors'

interface MenuItem {
  id: number
  naam: string
  beschrijving?: string
  prijs: number
  beschikbaar: boolean
  categorie: string
}

interface CartItem {
  id: string
  product_id: number
  naam: string
  prijs: number
  aantal: number
  categorie: string
  extras?: any
}


const PublicMenuPage = () => {
  const navigate = useNavigate()
  const [menu, setMenu] = useState<any>(null)
  const [extrasConfig, setExtrasConfig] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [productModalOpen, setProductModalOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<MenuItem | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const categoryProductsRef = useRef<HTMLDivElement>(null)
  const [errorOpen, setErrorOpen] = useState(false)
  const [menuError, setMenuError] = useState('')
  const [customerInfo, setCustomerInfo] = useState<string>('')

  useEffect(() => {
    loadMenu()
    loadExtras()
    loadCustomerInfo()
    // Load cart from localStorage on mount
    const savedCart = localStorage.getItem('cart')
    if (savedCart) {
      try {
        setCartItems(JSON.parse(savedCart))
      } catch (e) {
        console.error('Error loading cart:', e)
      }
    }
  }, [])

  const loadMenu = async () => {
    try {
      setLoading(true)
      setMenuError('')
      const data = await menuAPI.getPublicMenu() // Public endpoint
      setMenu(data)
      // Don't auto-select first category - show all by default
    } catch (err: any) {
      console.error('Error loading menu:', err)
      const errorMsg = getErrorMessage(err)
      setMenuError(errorMsg)
      setErrorMessage(errorMsg)
      setErrorOpen(true)
    } finally {
      setLoading(false)
    }
  }

  const loadExtras = async () => {
    try {
      const data = await extrasAPI.getPublicExtras() // Public endpoint
      setExtrasConfig(data)
    } catch (err: any) {
      console.error('Error loading extras:', err)
      // Extras zijn niet kritiek, dus alleen loggen
    }
  }

  const loadCustomerInfo = async () => {
    try {
      const data = await settingsAPI.getCustomerInfo()
      setCustomerInfo(data.message || '')
    } catch (err: any) {
      console.error('Error loading customer info:', err)
      // Set default message on error
      setCustomerInfo("Beste klanten,\n\nLevertijd in het weekend kan oplopen tot 75 minuten.\n\nMet vriendelijke groeten,\nPita Pizza Napoli")
    }
  }

  const handleProductClick = (product: MenuItem) => {
    if (!product.beschikbaar) return
    setSelectedProduct(product)
    setProductModalOpen(true)
  }

  const handleProductModalAdd = (productData: any) => {
    const cartItem: CartItem = {
      id: `${Date.now()}-${Math.random()}`,
      product_id: productData.product_id,
      naam: productData.naam,
      prijs: productData.prijs,
      aantal: productData.aantal || 1,
      categorie: productData.categorie,
      extras: productData.extras,
    }
    const updated = [...cartItems, cartItem]
    setCartItems(updated)
    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(updated))
    setProductModalOpen(false)
    setSelectedProduct(null)
  }

  const updateQuantity = (id: string, change: number) => {
    const updated = cartItems.map((item) =>
      item.id === id
        ? { ...item, aantal: Math.max(1, item.aantal + change) }
        : item
    )
    setCartItems(updated)
    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(updated))
  }

  const removeFromCart = (id: string) => {
    const updated = cartItems.filter((item) => item.id !== id)
    setCartItems(updated)
    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(updated))
  }

  const getTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0)
  }

  // Format category name - capitalize first letter and make it modern
  const formatCategoryName = (name: string) => {
    if (!name) return ''
    // Replace hyphens with spaces and capitalize each word
    return name
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  // Group items by category for better display
  const getItemsByCategory = (categoryName: string) => {
    return menu?.items?.filter((item: MenuItem) => item.categorie === categoryName) || []
  }

  // Scroll to category products when category is selected
  useEffect(() => {
    if (selectedCategory && categoryProductsRef.current) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        categoryProductsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        })
      }, 100)
    }
  }, [selectedCategory])

  const filteredItems = menu?.items?.filter(
    (item: MenuItem) => !selectedCategory || item.categorie === selectedCategory
  ) || []

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  // Show error if menu failed to load
  if (menuError && !menu) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="sticky" className="navbar-light" sx={{ bgcolor: '#fff', color: '#333', boxShadow: `0 4px 30px ${brandColors.primary}15` }}>
          <Toolbar className="navbar-container" sx={{ maxWidth: '1300px', margin: '0 auto', width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
              <Box
                component="a"
                href="/"
                onClick={(e) => {
                  e.preventDefault()
                  navigate('/')
                }}
                sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
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
                    height: '60px',
                    width: '60px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: `2px solid ${brandColors.primary}`,
                    boxShadow: `0 2px 8px ${brandColors.primary}30`,
                    mr: 1,
                  }}
                />
              </Box>
              <Typography variant="h6" component="div" className="navbar-title" sx={{ color: brandColors.primary, fontWeight: 800, fontSize: '2em' }}>
                Pita Pizza Napoli
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Fout bij laden menu
            </Typography>
            <Typography>{menuError}</Typography>
            <Button
              variant="contained"
              onClick={loadMenu}
              sx={{ mt: 2, bgcolor: brandColors.primary, '&:hover': { bgcolor: brandColors.primaryDark } }}
            >
              Opnieuw proberen
            </Button>
          </Alert>
        </Container>
      </Box>
    )
  }

  // Show message if menu is empty
  if (!menu || !menu.items || menu.items.length === 0) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="sticky" className="navbar-light" sx={{ bgcolor: '#fff', color: '#333', boxShadow: `0 4px 30px ${brandColors.primary}15` }}>
          <Toolbar className="navbar-container" sx={{ maxWidth: '1300px', margin: '0 auto', width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
              <Box
                component="a"
                href="/"
                onClick={(e) => {
                  e.preventDefault()
                  navigate('/')
                }}
                sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
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
                    height: '60px',
                    width: '60px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: `2px solid ${brandColors.primary}`,
                    boxShadow: `0 2px 8px ${brandColors.primary}30`,
                    mr: 1,
                  }}
                />
              </Box>
              <Typography variant="h6" component="div" className="navbar-title" sx={{ color: brandColors.primary, fontWeight: 800, fontSize: '2em' }}>
                Pita Pizza Napoli
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Menu wordt geladen...
            </Typography>
            <Typography>Als dit bericht blijft staan, controleer of de backend draait.</Typography>
            <Button
              variant="contained"
              onClick={loadMenu}
              sx={{ mt: 2, bgcolor: brandColors.primary, '&:hover': { bgcolor: brandColors.primaryDark } }}
            >
              Opnieuw laden
            </Button>
          </Alert>
        </Container>
      </Box>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f0', display: 'flex', flexDirection: 'column' }}>
      {/* Header - Shared Component */}
      <PublicHeader />

      {/* Main Content - Three Column Layout */}
      {(
        <Container maxWidth="lg" sx={{ py: 3, flex: 1 }}>
          <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
            {/* Left Column - Categories */}
            <Box sx={{ 
              width: { xs: '100%', lg: '250px' }, 
              flexShrink: 0,
              position: { xs: 'relative', lg: 'sticky' },
              top: { xs: 0, lg: '20px' },
              alignSelf: 'flex-start',
              zIndex: 10,
              maxHeight: { xs: 'none', lg: 'calc(100vh - 140px)' },
            }}>
              <Paper sx={{ 
                bgcolor: brandColors.primary, 
                borderRadius: '8px', 
                p: 0, 
                boxShadow: `0 2px 8px $${brandColors.primary}30`,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                maxHeight: { xs: 'none', lg: 'calc(100vh - 140px)' },
              }}>
                <Box sx={{ 
                  bgcolor: brandColors.primary, 
                  p: 2, 
                  borderBottom: '1px solid rgba(255,255,255,0.1)' 
                }}>
                  <Typography variant="h6" sx={{ 
                    color: '#fff', 
                    fontWeight: 700, 
                    fontSize: '1.1rem',
                    textAlign: 'center'
                  }}>
                    Kies een categorie
                  </Typography>
                </Box>
                <List sx={{ p: 1.5, bgcolor: '#fff', maxHeight: { xs: '400px', lg: '600px' }, overflowY: 'auto' }}>
                  <ListItem
                    button
                    onClick={() => setSelectedCategory('')}
                    selected={selectedCategory === ''}
                    sx={{
                      borderRadius: '4px',
                      mb: 0.5,
                      bgcolor: selectedCategory === '' ? `${brandColors.primaryLight}20` : 'transparent',
                      '&:hover': {
                        bgcolor: `${brandColors.primaryLight}20`,
                      },
                      '&.Mui-selected': {
                        bgcolor: `${brandColors.primaryLight}20`,
                        '&:hover': { bgcolor: `${brandColors.primaryLight}20` },
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: '32px' }}>
                      <ChevronRightIcon sx={{ color: brandColors.primary, fontSize: '1.2rem' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="Alle categorieën"
                      primaryTypographyProps={{
                        fontSize: '0.95rem',
                        fontWeight: selectedCategory === '' ? 600 : 400,
                        color: '#333',
                      }}
                    />
                  </ListItem>
                  {menu?.categories?.map((cat: any) => {
                    const itemCount = getItemsByCategory(cat.naam).length
                    if (itemCount === 0) return null
                    
                    return (
                      <ListItem
                        key={cat.naam}
                        button
                        onClick={() => setSelectedCategory(cat.naam)}
                        selected={selectedCategory === cat.naam}
                        sx={{
                          borderRadius: '4px',
                          mb: 0.5,
                          bgcolor: selectedCategory === cat.naam ? `${brandColors.primaryLight}20` : 'transparent',
                          '&:hover': {
                            bgcolor: `${brandColors.primaryLight}20`,
                          },
                          '&.Mui-selected': {
                            bgcolor: `${brandColors.primaryLight}20`,
                            '&:hover': { bgcolor: `${brandColors.primaryLight}20` },
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: '32px' }}>
                          <ChevronRightIcon sx={{ color: brandColors.primary, fontSize: '1.2rem' }} />
                        </ListItemIcon>
                    <ListItemText
                      primary={formatCategoryName(cat.naam)}
                      primaryTypographyProps={{
                        fontSize: '0.95rem',
                        fontWeight: selectedCategory === cat.naam ? 700 : 500,
                        color: '#333',
                        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
                        letterSpacing: '0.3px',
                      }}
                    />
                      </ListItem>
                    )
                  })}
                </List>
              </Paper>

            </Box>

          {/* Middle Column - Menu Content */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
          {/* Delivery Zones - Above Products */}
          <Paper sx={{ 
            bgcolor: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
            background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
            borderRadius: '12px', 
            p: 0, 
            boxShadow: '0 4px 20px rgba(26, 35, 126, 0.25)',
            mb: 3,
            overflow: 'hidden',
            border: '2px solid #3949ab',
          }}>
            <Box sx={{ 
              bgcolor: '#1a237e', 
              p: 2, 
              borderBottom: '2px solid #3949ab',
              background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
            }}>
              <Typography variant="h6" sx={{ 
                color: '#fff', 
                fontWeight: 800, 
                mb: 0,
                fontSize: '1.2rem',
                textAlign: 'center',
                textShadow: '0 2px 4px rgba(0,0,0,0.2)',
                letterSpacing: '0.5px',
              }}>
                Leveringszones
              </Typography>
            </Box>
            <Box sx={{ 
              p: 2, 
              bgcolor: '#fff',
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
              gap: 1.5,
            }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  4568 Nieuw-Namen
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 30,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9100 Nieuwkerken-Waas
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 20,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9120 Beveren
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 20,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9120 Vrasene
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 20,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9120 Haasdonk
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 25,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9120 Kallo
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 25,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9120 Melsele
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 25,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9130 Verrebroek
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 20,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9130 Kieldrecht
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 25,00
                </Typography>
              </Box>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: '8px', 
                bgcolor: '#f3f4f6',
                border: '1px solid #e5e7eb',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#3949ab',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(26, 35, 126, 0.15)',
                },
              }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#1a237e', mb: 0.5, fontSize: '0.95rem' }}>
                  9130 Doel
                </Typography>
                <Typography variant="caption" sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '0.85rem' }}>
                  vanaf € 35,00
                </Typography>
              </Box>
            </Box>
            {customerInfo && (
              <Box sx={{ 
                mt: 0, 
                p: 2, 
                bgcolor: '#e8eaf6',
                borderTop: '2px solid #3949ab',
              }}>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontSize: '0.9rem', 
                    color: '#1a237e', 
                    lineHeight: 1.6,
                    fontWeight: 500,
                    textAlign: 'center',
                    whiteSpace: 'pre-line',
                  }}
                  component="div"
                >
                  {customerInfo.split('\n').map((line, index, array) => {
                    const trimmedLine = line.trim()
                    // Check if line contains "Pita Pizza Napoli" to make it bold and red
                    if (trimmedLine.includes('Pita Pizza Napoli')) {
                      return (
                        <span key={index}>
                          <strong style={{ color: brandColors.primary }}>{trimmedLine}</strong>
                          {index < array.length - 1 && <br />}
                        </span>
                      )
                    }
                    // Check if line starts with "Beste" to make it bold
                    if (trimmedLine.startsWith('Beste')) {
                      return (
                        <span key={index}>
                          <strong>{trimmedLine}</strong>
                          {index < array.length - 1 && <br />}
                        </span>
                      )
                    }
                    // Empty line
                    if (trimmedLine === '') {
                      return <br key={index} />
                    }
                    return (
                      <span key={index}>
                        {trimmedLine}
                        {index < array.length - 1 && <br />}
                      </span>
                    )
                  })}
                </Typography>
              </Box>
            )}
          </Paper>

          {menuError && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }} onClose={() => setMenuError('')}>
              <Typography variant="h6" gutterBottom>
                Fout bij laden menu
              </Typography>
              <Typography>{menuError}</Typography>
              <Button
                size="small"
                onClick={loadMenu}
                sx={{ mt: 1 }}
              >
                Opnieuw proberen
              </Button>
            </Alert>
          )}


          {/* Category Sections */}
          {!selectedCategory && menu?.categories ? (
            // Show all categories with their items
            menu.categories.map((category: any) => {
              const categoryItems = filteredItems.filter((item: MenuItem) => item.categorie === category.naam)
              if (categoryItems.length === 0) return null
              
              return (
                <Box key={category.naam} sx={{ mb: { xs: 3, sm: 4 } }}>
                  <Typography
                    variant="h5"
                    sx={{
                      color: brandColors.primary,
                      fontWeight: 800,
                      mb: { xs: 2, sm: 3 },
                      pb: 1,
                      borderBottom: '2px solid ${brandColors.primary}',
                      fontSize: { xs: '1.3rem', sm: '1.5rem' },
                      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
                      letterSpacing: '0.5px',
                      textTransform: 'none',
                    }}
                  >
                    {formatCategoryName(category.naam)}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 1, sm: 1.5 } }}>
                    {categoryItems.map((item: MenuItem, index: number) => (
                      <Paper
                        key={item.id}
                        elevation={0}
                        sx={{
                          display: 'flex',
                          flexDirection: { xs: 'column', sm: 'row' },
                          alignItems: { xs: 'flex-start', sm: 'center' },
                          justifyContent: 'space-between',
                          p: { xs: 1.5, sm: 2 },
                          borderRadius: '8px',
                          border: '1px solid #e0e0e0',
                          cursor: item.beschikbaar ? 'pointer' : 'not-allowed',
                          opacity: item.beschikbaar ? 1 : 0.6,
                          transition: 'all 0.2s ease',
                          bgcolor: '#fff',
                          '&:hover': item.beschikbaar ? {
                            borderColor: '${brandColors.primary}',
                            boxShadow: '0 2px 8px rgba(229, 37, 37, 0.1)',
                            transform: { xs: 'none', sm: 'translateX(2px)' },
                          } : {},
                        }}
                        onClick={() => handleProductClick(item)}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: { xs: 1, sm: 2 }, flex: 1, minWidth: 0, width: '100%' }}>
                          <Typography
                            variant="body2"
                            sx={{
                              color: brandColors.primary,
                              fontWeight: 700,
                              minWidth: { xs: '25px', sm: '35px' },
                              fontSize: { xs: '0.85rem', sm: '0.95rem' },
                              flexShrink: 0,
                            }}
                          >
                            {String(index + 1).padStart(2, '0')}.
                          </Typography>
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Typography
                              variant="body1"
                              component="h3"
                              sx={{
                                fontWeight: 600,
                                color: '#333',
                                fontSize: { xs: '0.9rem', sm: '0.95rem' },
                                mb: 0.5,
                              }}
                            >
                              {item.naam}
                            </Typography>
                            {item.beschrijving && (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{
                                  fontSize: { xs: '0.8em', sm: '0.85em' },
                                  lineHeight: 1.4,
                                  mb: 1,
                                }}
                              >
                                {item.beschrijving}
                              </Typography>
                            )}
                            {!item.beschikbaar && (
                              <Chip label="Niet beschikbaar" size="small" color="error" sx={{ mt: 0.5, fontSize: '0.7rem', height: '20px' }} />
                            )}
                          </Box>
                        </Box>
                        <Box sx={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: { xs: 'space-between', sm: 'flex-end' },
                          gap: { xs: 1, sm: 2 }, 
                          flexShrink: 0, 
                          ml: { xs: 0, sm: 2 },
                          mt: { xs: 1.5, sm: 0 },
                          width: { xs: '100%', sm: 'auto' },
                          pt: { xs: 1, sm: 0 },
                          borderTop: { xs: '1px solid #e0e0e0', sm: 'none' },
                        }}>
                          <Typography
                            variant="h6"
                            sx={{
                              color: brandColors.primary,
                              fontWeight: 700,
                              fontSize: { xs: '1.1rem', sm: '1.2rem' },
                              minWidth: { xs: 'auto', sm: '70px' },
                              textAlign: { xs: 'left', sm: 'right' },
                            }}
                          >
                            €{item.prijs.toFixed(2)}
                          </Typography>
                          {item.beschikbaar && (
                            <Button
                              variant="contained"
                              startIcon={<AddIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                handleProductClick(item)
                              }}
                              sx={{
                                bgcolor: brandColors.primary,
                                color: '#fff',
                                '&:hover': { bgcolor: brandColors.primaryDark },
                                textTransform: 'none',
                                borderRadius: '20px',
                                px: { xs: 2, sm: 2.5 },
                                py: { xs: 0.5, sm: 0.75 },
                                fontWeight: 600,
                                fontSize: { xs: '0.8rem', sm: '0.85rem' },
                                whiteSpace: 'nowrap',
                              }}
                            >
                              <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>Toevoegen</Box>
                              <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>+</Box>
                            </Button>
                          )}
                        </Box>
                      </Paper>
                    ))}
                  </Box>
                </Box>
              )
            })
          ) : (
            // Show filtered items for selected category
            selectedCategory && (
              <Box ref={categoryProductsRef} sx={{ mb: 3, scrollMarginTop: '120px' }}>
                <Typography
                  variant="h4"
                  sx={{
                    color: brandColors.primary,
                    fontWeight: 800,
                    mb: 3,
                    pb: 1,
                    borderBottom: '3px solid ${brandColors.primary}',
                    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
                    letterSpacing: '0.5px',
                    textTransform: 'none',
                  }}
                >
                  {formatCategoryName(selectedCategory)}
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {filteredItems.map((item: MenuItem, index: number) => (
                    <Paper
                      key={item.id}
                      elevation={0}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        p: 2.5,
                        borderRadius: '12px',
                        border: '1px solid #e0e0e0',
                        cursor: item.beschikbaar ? 'pointer' : 'not-allowed',
                        opacity: item.beschikbaar ? 1 : 0.6,
                        transition: 'all 0.2s ease',
                        bgcolor: '#fff',
                        '&:hover': item.beschikbaar ? {
                          borderColor: '${brandColors.primary}',
                          boxShadow: '0 4px 12px $${brandColors.primary}25',
                          transform: 'translateX(4px)',
                        } : {},
                      }}
                      onClick={() => handleProductClick(item)}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="body1"
                          sx={{
                            color: brandColors.primary,
                            fontWeight: 700,
                            minWidth: '40px',
                            fontSize: '1.1em',
                            flexShrink: 0,
                          }}
                        >
                          {String(index + 1).padStart(2, '0')}.
                        </Typography>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography
                            variant="h6"
                            component="h3"
                            sx={{
                              fontWeight: 600,
                              color: '#333',
                              fontSize: { xs: '0.9rem', sm: '0.95rem', md: '1rem' },
                              mb: 0.5,
                            }}
                          >
                            {item.naam}
                          </Typography>
                          {item.beschrijving && (
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                fontSize: '0.95em',
                                lineHeight: 1.5,
                                mb: 1,
                              }}
                            >
                              {item.beschrijving}
                            </Typography>
                          )}
                          {!item.beschikbaar && (
                            <Chip label="Niet beschikbaar" size="small" color="error" sx={{ mt: 0.5 }} />
                          )}
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexShrink: 0, ml: 2 }}>
                        <Typography
                          variant="h5"
                          sx={{
                            color: brandColors.primary,
                            fontWeight: 700,
                            fontSize: '1.5em',
                            minWidth: '80px',
                            textAlign: 'right',
                          }}
                        >
                          €{item.prijs.toFixed(2)}
                        </Typography>
                        {item.beschikbaar && (
                          <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleProductClick(item)
                            }}
                            sx={{
                              bgcolor: brandColors.primary,
                              color: '#fff',
                              '&:hover': { bgcolor: brandColors.primaryDark },
                              textTransform: 'none',
                              borderRadius: '25px',
                              px: 3,
                              py: 1,
                              fontWeight: 600,
                            }}
                          >
                            Toevoegen
                          </Button>
                        )}
                      </Box>
                    </Paper>
                  ))}
                </Box>
              </Box>
            )
          )}

          {filteredItems.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary">
                Geen producten gevonden in deze categorie
              </Typography>
            </Box>
          )}
          </Box>

          {/* Right Column - Shopping Cart */}
          <Box sx={{ 
            width: { xs: '100%', lg: '300px' }, 
            flexShrink: 0,
            position: { xs: 'relative', lg: 'sticky' },
            top: { xs: 0, lg: '20px' },
            alignSelf: 'flex-start',
            zIndex: 10,
            maxHeight: { xs: 'none', lg: 'calc(100vh - 140px)' },
          }}>
            <Paper
              sx={{
                p: 0,
                height: { xs: 'auto', lg: 'calc(100vh - 140px)' },
                maxHeight: { xs: 'none', lg: 'calc(100vh - 140px)' },
                display: 'flex',
                flexDirection: 'column',
                borderRadius: '8px',
                boxShadow: '0 2px 8px $${brandColors.primary}30',
                overflow: 'hidden',
              }}
            >
            <Box sx={{ 
              bgcolor: brandColors.primary, 
              p: 2, 
              textAlign: 'center',
              borderBottom: '1px solid rgba(255,255,255,0.1)'
            }}>
              <Typography
                variant="h6"
                sx={{
                  color: '#fff',
                  fontSize: '1.1rem',
                  fontWeight: 700,
                }}
              >
                Je bestelling
              </Typography>
            </Box>
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', bgcolor: '#fff' }}>
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '15px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                }}
              >
                {cartItems.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <LocalDiningIcon sx={{ 
                      fontSize: '80px', 
                      color: brandColors.primary, 
                      mb: 2,
                      opacity: 0.8
                    }} />
                    <Typography variant="body2" sx={{ color: '#666', fontSize: '0.95rem', mb: 3 }}>
                      Je bestelling is leeg
                    </Typography>
                    <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                      <Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#666', mb: 1 }}>
                        Bezorgkosten: gratis
                      </Typography>
                      <Typography variant="h6" sx={{ fontSize: '1rem', color: brandColors.primary, fontWeight: 700 }}>
                        Totaal: € 0,00
                      </Typography>
                    </Box>
                  </Box>
                ) : (
                  cartItems.map((item) => (
                    <Box
                      key={item.id}
                      sx={{
                        background: '#fff',
                        borderRadius: '12px',
                        padding: '12px',
                        border: '1px solid #ffe6e6',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                        '&:hover': {
                          borderColor: '${brandColors.primary}',
                          transform: 'translateX(3px)',
                          boxShadow: '0 2px 8px $${brandColors.primary}15',
                        },
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <Box sx={{ mb: 0.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="body1" sx={{ fontWeight: 700, color: '#333', fontSize: { xs: '0.9rem', sm: '1rem', md: '1.05rem' }, mb: 0.25 }}>
                              {item.naam || 'Onbekend product'}
                            </Typography>
                            <Typography variant="caption" sx={{ 
                              color: brandColors.primary, 
                              fontSize: { xs: '0.7rem', sm: '0.75rem' }, 
                              display: 'block', 
                              fontWeight: 600,
                              fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
                              letterSpacing: '0.2px',
                            }}>
                              Categorie: {formatCategoryName(item.categorie)}
                            </Typography>
                          </Box>
                          <Typography variant="body2" sx={{ color: brandColors.primary, fontWeight: 700, fontSize: { xs: '0.9rem', sm: '1rem' }, ml: 1 }}>
                            €{(item.prijs * item.aantal).toFixed(2)}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ 
                        pl: 1, 
                        mt: 0.5,
                        pt: 0.5,
                        borderTop: '1px solid #f0f0f0',
                      }}>
                        {item.extras && Object.keys(item.extras).length > 0 ? (
                          <>
                            {item.extras.vlees && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Vlees:</strong> {item.extras.vlees}
                              </Typography>
                            )}
                            {item.extras.pasta_keuze && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Pasta:</strong> {item.extras.pasta_keuze}
                              </Typography>
                            )}
                            {item.extras.bijgerecht && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Bijgerecht:</strong> {Array.isArray(item.extras.bijgerecht) ? item.extras.bijgerecht.join(', ') : item.extras.bijgerecht}
                              </Typography>
                            )}
                            {item.extras.sauzen && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Sauzen:</strong> {Array.isArray(item.extras.sauzen) ? item.extras.sauzen.join(', ') : item.extras.sauzen}
                              </Typography>
                            )}
                            {item.extras.saus1 && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Saus 1:</strong> {item.extras.saus1}
                              </Typography>
                            )}
                            {item.extras.saus2 && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Saus 2:</strong> {item.extras.saus2}
                              </Typography>
                            )}
                            {item.extras.garnering && Array.isArray(item.extras.garnering) && item.extras.garnering.length > 0 && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Extra:</strong> {item.extras.garnering.join(', ')}
                              </Typography>
                            )}
                            {item.extras.half_half && Array.isArray(item.extras.half_half) && item.extras.half_half.length === 2 && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25 }}>
                                <strong>Half-half:</strong> {item.extras.half_half[0]} / {item.extras.half_half[1]}
                              </Typography>
                            )}
                            {item.extras.opmerking && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ fontSize: '0.75rem', mb: 0.25, fontStyle: 'italic', color: '#666' }}>
                                <strong>Opmerking:</strong> {item.extras.opmerking}
                              </Typography>
                            )}
                          </>
                        ) : (
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem', fontStyle: 'italic', color: '#999' }}>
                            Geen extra's
                          </Typography>
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => updateQuantity(item.id, -1)}
                            sx={{
                              bgcolor: '#fff5f5',
                              color: brandColors.primary,
                              '&:hover': { bgcolor: '#ffe6e6' },
                            }}
                          >
                            <RemoveIcon fontSize="small" />
                          </IconButton>
                          <Typography variant="body2" sx={{ minWidth: '30px', textAlign: 'center', fontWeight: 600 }}>
                            {item.aantal}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => updateQuantity(item.id, 1)}
                            sx={{
                              bgcolor: '#fff5f5',
                              color: brandColors.primary,
                              '&:hover': { bgcolor: '#ffe6e6' },
                            }}
                          >
                            <AddIcon fontSize="small" />
                          </IconButton>
                        </Box>
                        <IconButton
                          size="small"
                          onClick={() => removeFromCart(item.id)}
                          sx={{
                            color: '#d32f2f',
                            '&:hover': { bgcolor: '#ffebee' },
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>
                  ))
                )}
              </Box>
              {cartItems.length > 0 && (
                <Box
                  sx={{
                    background: '#fff',
                    padding: '15px',
                    borderTop: '1px solid #e0e0e0',
                  }}
                >
                  <Box sx={{ padding: '10px 0' }}>
                    <Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#666', mb: 1 }}>
                      Bezorgkosten: gratis
                    </Typography>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginTop: '10px',
                        paddingTop: '10px',
                        borderTop: '1px solid #e0e0e0',
                      }}
                    >
                      <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 700, fontSize: '1rem' }}>
                        Totaal:
                      </Typography>
                      <Typography variant="h6" sx={{ color: brandColors.primary, fontWeight: 700, fontSize: '1rem' }}>
                        €{getTotal().toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => {
                      localStorage.setItem('cart', JSON.stringify(cartItems))
                      navigate('/checkout')
                    }}
                    sx={{
                      mt: 2,
                      bgcolor: brandColors.primary,
                      color: '#fff',
                      fontWeight: 600,
                      padding: '12px',
                      borderRadius: '8px',
                      '&:hover': { bgcolor: brandColors.primaryDark },
                    }}
                  >
                    Afrekenen
                  </Button>
                </Box>
              )}
            </Box>
            </Paper>
          </Box>
        </Box>
        </Container>
      )}

      {/* Product Modal */}
      {selectedProduct && (
        <ProductModal
          open={productModalOpen}
          onClose={() => {
            setProductModalOpen(false)
            setSelectedProduct(null)
          }}
          product={selectedProduct}
          category={selectedProduct.categorie || selectedCategory || ''}
          extrasConfig={extrasConfig}
          menuItems={menu?.items || []}
          onAdd={handleProductModalAdd}
        />
      )}

      {/* Error Snackbar */}
      <Snackbar
        open={errorOpen}
        autoHideDuration={6000}
        onClose={() => setErrorOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setErrorOpen(false)}
          severity="error"
          sx={{ width: '100%' }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default PublicMenuPage

