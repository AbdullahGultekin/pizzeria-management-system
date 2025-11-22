import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  AppBar,
  Toolbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { menuAPI, orderAPI, extrasAPI, printerAPI } from '../services/api'
import MenuGrid from '../components/MenuGrid'
import Cart from '../components/Cart'
import CustomerSearch from '../components/CustomerSearch'
import ProductModal from '../components/ProductModal'
import ProductSearch from '../components/ProductSearch'

interface CartItem {
  id: string
  product_naam: string
  prijs: number
  aantal: number
  opmerking?: string
  extras?: {
    vlees?: string
    bijgerecht?: string
    saus1?: string
    saus2?: string
    garnering?: string[]
  }
}

interface Customer {
  id: number
  naam: string
  telefoon: string
  straat?: string
  huisnummer?: string
  plaats?: string
}

const KassaPage = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menu, setMenu] = useState<any>(null)
  const [extrasConfig, setExtrasConfig] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [orderDialogOpen, setOrderDialogOpen] = useState(false)
  const [orderNote, setOrderNote] = useState('')
  const [placingOrder, setPlacingOrder] = useState(false)
  const [orderSuccess, setOrderSuccess] = useState(false)
  const [orderNumber, setOrderNumber] = useState('')
  const [error, setError] = useState('')
  const [productModalOpen, setProductModalOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<any>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('')

  useEffect(() => {
    console.log('🚀 KassaPage mounted, loading menu...')
    loadMenu()
    loadExtras()
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Enter: Place order
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (cartItems.length > 0) {
          e.preventDefault()
          handlePlaceOrder()
        }
      }
      // Ctrl/Cmd + K: Focus search (if search is visible)
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        // Focus will be handled by ProductSearch component
      }
      // Escape: Close modals
      if (e.key === 'Escape') {
        if (productModalOpen) {
          setProductModalOpen(false)
          setSelectedProduct(null)
        }
        if (orderDialogOpen) {
          setOrderDialogOpen(false)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [cartItems, productModalOpen, orderDialogOpen])

  const loadMenu = async () => {
    try {
      console.log('📡 Fetching menu from API...')
      const data = await menuAPI.getMenu()
      console.log('✅ Menu loaded successfully:', data)
      console.log('   Categories:', data?.categories?.length || 0)
      console.log('   Items:', data?.items?.length || 0)
      
      if (!data) {
        console.warn('⚠️ Menu data is null/undefined')
        setMenu({ categories: [], items: [] })
      } else {
        setMenu(data)
      }
    } catch (error: any) {
      console.error('❌ Error loading menu:', error)
      console.error('   Message:', error.message)
      console.error('   Response:', error.response?.data)
      console.error('   Status:', error.response?.status)
      setError(error.response?.data?.detail || error.message || 'Kon menu niet laden')
      setMenu({ categories: [], items: [] })
    } finally {
      setLoading(false)
      console.log('✅ Menu loading finished')
    }
  }

  const loadExtras = async () => {
    try {
      console.log('📡 Fetching extras config...')
      const data = await extrasAPI.getExtras()
      console.log('✅ Extras config loaded:', Object.keys(data).length, 'categories')
      setExtrasConfig(data)
    } catch (error: any) {
      console.error('❌ Error loading extras:', error)
      setExtrasConfig({})
    }
  }

  const addToCart = (item: any) => {
    // Check if product needs options (has extras config)
    const catLower = (item.categorie || '').toLowerCase()
    const hasExtras = extrasConfig[item.categorie] || extrasConfig[catLower]
    
    if (hasExtras && (hasExtras.vlees || hasExtras.bijgerecht || hasExtras.sauzen || hasExtras.garnering)) {
      // Open modal for product options
      setSelectedProduct(item)
      setSelectedCategory(item.categorie)
      setProductModalOpen(true)
    } else {
      // Simple product, add directly
      const cartItem: CartItem = {
        id: `${item.id}-${Date.now()}`,
        product_naam: item.naam,
        prijs: item.prijs,
        aantal: 1,
      }
      setCartItems([...cartItems, cartItem])
      console.log('🛒 Added to cart:', cartItem)
    }
  }

  const handleProductModalAdd = (productData: any) => {
    const cartItem: CartItem = {
      id: `${selectedProduct.id}-${Date.now()}`,
      product_naam: productData.product_naam,
      prijs: productData.prijs,
      aantal: productData.aantal,
      opmerking: productData.opmerking,
      extras: productData.extras,
    }
    setCartItems([...cartItems, cartItem])
    console.log('🛒 Added to cart with options:', cartItem)
  }

  const updateQuantity = (id: string, delta: number) => {
    setCartItems((items) =>
      items.map((item) =>
        item.id === id
          ? { ...item, aantal: Math.max(1, item.aantal + delta) }
          : item
      )
    )
  }

  const removeFromCart = (id: string) => {
    setCartItems((items) => items.filter((item) => item.id !== id))
  }

  const handlePlaceOrder = () => {
    if (cartItems.length === 0) {
      setError('Winkelwagen is leeg')
      return
    }
    setOrderDialogOpen(true)
  }

  const confirmPlaceOrder = async () => {
    if (cartItems.length === 0) return

    setPlacingOrder(true)
    setError('')

    try {
      const total = cartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0)

      const orderData = {
        klant_id: selectedCustomer?.id || null,
        totaal: total,
        opmerking: orderNote || null,
        items: cartItems.map((item) => ({
          product_naam: item.product_naam,
          aantal: item.aantal,
          prijs: item.prijs,
          opmerking: item.opmerking || null,
        })),
      }

      console.log('📦 Placing order:', orderData)
      const order = await orderAPI.create(orderData)
      console.log('✅ Order placed:', order)

      setOrderNumber(order.bonnummer || '')
      setOrderSuccess(true)
      setCartItems([])
      setSelectedCustomer(null)
      setOrderNote('')
      setOrderDialogOpen(false)

      // Automatically print order after successful creation
      try {
        await printerAPI.printOrder(order.id)
        console.log('✅ Order printed automatically')
      } catch (printErr: any) {
        console.warn('⚠️ Could not print order automatically:', printErr)
        // Don't show error to user, printing is optional
      }

      setTimeout(() => {
        setOrderSuccess(false)
      }, 3000)
    } catch (err: any) {
      console.error('❌ Error placing order:', err)
      setError(err.response?.data?.detail || 'Kon bestelling niet plaatsen')
    } finally {
      setPlacingOrder(false)
    }
  }

  // Debug: Log state changes
  useEffect(() => {
    console.log('📊 KassaPage state:', {
      hasMenu: !!menu,
      categories: menu?.categories?.length || 0,
      items: menu?.items?.length || 0,
      loading,
      cartItems: cartItems.length,
      hasCustomer: !!selectedCustomer,
      user: user?.username,
    })
  }, [menu, loading, cartItems, selectedCustomer, user])

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9' }}>
      <AppBar position="static" className="navbar-light">
        <Toolbar className="navbar-container">
          <Typography variant="h6" component="div" className="navbar-title" sx={{ flexGrow: 1 }}>
            Kassa - {user?.username || 'Gebruiker'}
          </Typography>
          <Button 
            color="inherit" 
            onClick={() => navigate('/geschiedenis')}
            sx={{ color: '#333', fontWeight: 600, mr: 2 }}
          >
            Geschiedenis
          </Button>
          <Button color="inherit" onClick={logout} sx={{ color: '#333', fontWeight: 600 }}>
            Uitloggen
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" className="main-container" sx={{ mt: 3, mb: 3 }}>
        {orderSuccess && (
          <Alert 
            severity="success" 
            sx={{ mb: 2, borderRadius: '10px' }}
            onClose={() => setOrderSuccess(false)}
          >
            <Typography variant="h6" gutterBottom>
              ✅ Bestelling geplaatst!
            </Typography>
            {orderNumber && (
              <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1, mb: 1, mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Bonnummer:
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: '#e52525' }}>
                  {orderNumber}
                </Typography>
              </Box>
            )}
            <Typography variant="body2" sx={{ mt: 1 }}>
              De bestelling is succesvol geplaatst en verschijnt in het admin dashboard.
            </Typography>
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
            <Box sx={{ textAlign: 'center' }}>
              <CircularProgress sx={{ mb: 2 }} />
              <Typography variant="h6">Menu laden...</Typography>
            </Box>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {/* Left side - Menu and Customer Search */}
            <Grid item xs={12} md={8} className="content">
              <Paper sx={{ p: 3, mb: 3, borderRadius: '20px', boxShadow: '0 4px 25px rgba(229, 37, 37, 0.1)' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h5" sx={{ color: '#d32f2f', fontWeight: 600 }}>
                    Klant Selectie
                  </Typography>
                  {selectedCustomer && (
                    <Chip
                      label={selectedCustomer.naam}
                      onDelete={() => setSelectedCustomer(null)}
                      color="primary"
                      sx={{ bgcolor: '#e52525', color: '#fff' }}
                    />
                  )}
                </Box>
                <CustomerSearch
                  onSelectCustomer={setSelectedCustomer}
                  selectedCustomer={selectedCustomer}
                />
              </Paper>

              <Paper sx={{ p: 3, mb: 3, borderRadius: '20px', boxShadow: '0 4px 25px rgba(229, 37, 37, 0.1)' }}>
                <Typography variant="h5" gutterBottom sx={{ color: '#d32f2f', fontWeight: 600, mb: 2 }}>
                  Product Zoeken
                </Typography>
                <ProductSearch
                  items={menu?.items || []}
                  onSelectItem={(item) => {
                    setSelectedProduct(item)
                    setSelectedCategory(item.categorie)
                    setProductModalOpen(true)
                  }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Tip: Gebruik Ctrl+K (Cmd+K op Mac) om snel te zoeken
                </Typography>
              </Paper>

              <Paper sx={{ p: 3, borderRadius: '20px', boxShadow: '0 4px 25px rgba(229, 37, 37, 0.1)' }}>
                <Typography variant="h5" gutterBottom sx={{ color: '#d32f2f', fontWeight: 600 }}>
                  Menu
                </Typography>
                {menu && menu.categories && menu.items ? (
                  menu.categories.length > 0 || menu.items.length > 0 ? (
                    <MenuGrid
                      categories={menu.categories || []}
                      items={menu.items || []}
                      onAddToCart={addToCart}
                    />
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body1" color="text.secondary" gutterBottom>
                        Geen menu items beschikbaar
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Voeg menu items toe via het admin dashboard
                      </Typography>
                      <Button variant="outlined" onClick={loadMenu}>
                        Opnieuw Laden
                      </Button>
                    </Box>
                  )
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography color="error" gutterBottom>
                      Menu data niet beschikbaar
                    </Typography>
                    <Button variant="outlined" onClick={loadMenu} sx={{ mt: 2 }}>
                      Opnieuw Proberen
                    </Button>
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Right side - Cart */}
            <Grid item xs={12} md={4}>
              <Cart
                items={cartItems}
                onUpdateQuantity={updateQuantity}
                onRemoveItem={removeFromCart}
                onPlaceOrder={handlePlaceOrder}
                loading={placingOrder}
              />
            </Grid>
          </Grid>
        )}
      </Container>

      {/* Order Confirmation Dialog */}
      <Dialog open={orderDialogOpen} onClose={() => setOrderDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Bestelling Bevestigen</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body1" gutterBottom>
              <strong>Klant:</strong> {selectedCustomer?.naam || 'Geen klant geselecteerd'}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Aantal items:</strong> {cartItems.length}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Totaal:</strong> €{cartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0).toFixed(2)}
            </Typography>
          </Box>
          <TextField
            fullWidth
            label="Opmerking (optioneel)"
            multiline
            rows={3}
            value={orderNote}
            onChange={(e) => setOrderNote(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOrderDialogOpen(false)}>Annuleren</Button>
          <Button onClick={confirmPlaceOrder} variant="contained" disabled={placingOrder}>
            {placingOrder ? 'Plaatsen...' : 'Bevestigen'}
          </Button>
        </DialogActions>
          </Dialog>

      {/* Product Options Modal */}
      <ProductModal
        open={productModalOpen}
        product={selectedProduct}
        category={selectedCategory}
        extrasConfig={extrasConfig}
        onClose={() => {
          setProductModalOpen(false)
          setSelectedProduct(null)
          setSelectedCategory('')
        }}
        onAdd={handleProductModalAdd}
      />
    </Box>
  )
}

export default KassaPage
