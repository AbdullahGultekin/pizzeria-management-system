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
  IconButton,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CreditCardIcon from '@mui/icons-material/CreditCard'
import PublicHeader from '../components/PublicHeader'
import { brandColors } from '../theme/colors'

interface CartItem {
  id: string
  product_id: number
  naam: string
  prijs: number
  aantal: number
  categorie: string
  extras?: any
}

const CartPage = () => {
  const navigate = useNavigate()
  const [cartItems, setCartItems] = useState<CartItem[]>([])

  useEffect(() => {
    // Load cart from localStorage
    const savedCart = localStorage.getItem('cart')
    if (savedCart) {
      try {
        setCartItems(JSON.parse(savedCart))
      } catch (e) {
        console.error('Error loading cart:', e)
      }
    }
  }, [])

  const updateCart = (items: CartItem[]) => {
    setCartItems(items)
    localStorage.setItem('cart', JSON.stringify(items))
  }

  const removeFromCart = (id: string) => {
    const updated = cartItems.filter(item => item.id !== id)
    updateCart(updated)
  }

  const updateQuantity = (id: string, change: number) => {
    const updated = cartItems.map(item => {
      if (item.id === id) {
        const newAantal = Math.max(1, item.aantal + change)
        return { ...item, aantal: newAantal }
      }
      return item
    })
    updateCart(updated)
  }

  const clearCart = () => {
    if (window.confirm('Weet je zeker dat je de winkelwagen wilt legen?')) {
      updateCart([])
    }
  }

  const getTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.prijs * item.aantal, 0)
  }

  const formatExtras = (extras: any) => {
    if (!extras) return []
    const details: string[] = []
    
    if (extras.vlees) {
      details.push(`Vlees: ${extras.vlees}`)
    }
    if (extras.pasta_keuze) {
      details.push(`Pasta: ${extras.pasta_keuze}`)
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

  // Format category name - capitalize first letter and make it modern
  const formatCategory = (cat: string) => {
    if (!cat) return ''
    return cat
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa' }}>
      {/* Header - Shared Component */}
      <PublicHeader />

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper
          elevation={0}
          sx={{
            bgcolor: '#fff',
            padding: '24px 30px 35px 30px',
            borderRadius: '17px',
            maxWidth: '1000px',
            margin: '30px auto 0 auto',
            boxShadow: '0 3px 20px -6px rgba(180, 68, 68, 0.3)',
            fontSize: '1em',
            color: '#222',
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
            Jouw Winkelwagen
          </Typography>

          {cartItems.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" sx={{ color: '#888', fontSize: '1.15em', mb: 3 }}>
                Je winkelwagen is leeg.
              </Typography>
              <Button
                variant="contained"
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/')}
                sx={{
                  bgcolor: brandColors.primary,
                  color: '#fff',
                  fontWeight: 600,
                  padding: '10px 19px',
                  borderRadius: '19px',
                  fontSize: '1.06em',
                  '&:hover': { bgcolor: brandColors.primaryDark },
                }}
              >
                Terug naar menu
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table className="cart-table" sx={{ width: '100%', borderCollapse: 'collapse', mb: 3 }}>
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#fff7f6' }}>
                      <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                        Product
                      </TableCell>
                      <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                        Categorie
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
                      <TableCell sx={{ color: brandColors.primary, fontWeight: 600, fontSize: '1.09em', py: 2 }}>
                        Actie
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cartItems.map((item) => {
                      const extras = formatExtras(item.extras)
                      return (
                        <TableRow key={item.id} sx={{ '&:last-child td': { borderBottom: 'none' } }}>
                          <TableCell sx={{ py: 2, fontSize: '1em', verticalAlign: 'top' }}>
                            <Typography variant="body1" sx={{ fontWeight: 700, mb: 0.5, fontSize: '1.05em', color: '#333' }}>
                              {item.naam || 'Onbekend product'}
                            </Typography>
                            <Typography variant="caption" sx={{ 
                              fontSize: '0.85rem', 
                              display: 'block', 
                              fontWeight: 600,
                              color: brandColors.primary,
                              mb: 0.5,
                            }}>
                              Categorie: {formatCategory(item.categorie)}
                            </Typography>
                          </TableCell>
                          <TableCell sx={{ py: 2, fontSize: '1em', verticalAlign: 'top' }}>
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
                          <TableCell sx={{ py: 2, fontSize: '1em', verticalAlign: 'top' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <IconButton
                                size="small"
                                onClick={() => updateQuantity(item.id, -1)}
                                disabled={item.aantal <= 1}
                                sx={{
                                  bgcolor: `${brandColors.primaryLight}20`,
                                  color: brandColors.primary,
                                  '&:hover': { bgcolor: `${brandColors.primaryLight}30` },
                                  '&:disabled': { opacity: 0.3 },
                                }}
                              >
                                -
                              </IconButton>
                              <Typography variant="body2" sx={{ minWidth: '30px', textAlign: 'center', fontWeight: 600 }}>
                                {item.aantal}
                              </Typography>
                              <IconButton
                                size="small"
                                onClick={() => updateQuantity(item.id, 1)}
                                sx={{
                                  bgcolor: `${brandColors.primaryLight}20`,
                                  color: brandColors.primary,
                                  '&:hover': { bgcolor: `${brandColors.primaryLight}30` },
                                }}
                              >
                                +
                              </IconButton>
                            </Box>
                          </TableCell>
                          <TableCell sx={{ py: 2, fontSize: '1em', verticalAlign: 'top', fontWeight: 600 }}>
                            €{(item.prijs * item.aantal).toFixed(2)}
                          </TableCell>
                          <TableCell sx={{ py: 2, fontSize: '1em', verticalAlign: 'top' }}>
                            <IconButton
                              onClick={() => removeFromCart(item.id)}
                              sx={{
                                color: brandColors.primary,
                                fontSize: '1.18em',
                                padding: '2px 8px',
                                borderRadius: '50%',
                                '&:hover': { bgcolor: '#fff0ef' },
                              }}
                              title="Verwijderen"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                  <TableFooter>
                    <TableRow>
                      <TableCell colSpan={4} align="right" sx={{ py: 2, fontWeight: 600 }}>
                        <Typography variant="h6">Totaal:</Typography>
                      </TableCell>
                      <TableCell colSpan={2} sx={{ py: 2, fontWeight: 700 }}>
                        <Typography variant="h6" sx={{ color: brandColors.primary }}>
                          €{getTotal().toFixed(2)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableFooter>
                </Table>
              </TableContainer>

              <Box sx={{ display: 'flex', gap: 2, mt: 3, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={() => navigate('/')}
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
                  Verder winkelen
                </Button>
                <Button
                  variant="contained"
                  startIcon={<CreditCardIcon />}
                  onClick={() => navigate('/checkout')}
                  sx={{
                    bgcolor: brandColors.primary,
                    color: '#fff',
                    fontWeight: 600,
                    padding: '10px 19px',
                    borderRadius: '19px',
                    fontSize: '1.06em',
                    '&:hover': { bgcolor: brandColors.primaryDark },
                  }}
                >
                  Afrekenen
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DeleteIcon />}
                  onClick={clearCart}
                  sx={{
                    borderColor: brandColors.primary,
                    color: '#ffeaea',
                    bgcolor: brandColors.primary,
                    fontWeight: 600,
                    padding: '10px 19px',
                    borderRadius: '19px',
                    fontSize: '1.06em',
                    '&:hover': {
                      bgcolor: brandColors.primary,
                      color: '#fff',
                    },
                  }}
                >
                  Alles wissen
                </Button>
              </Box>
            </>
          )}
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
        &copy; 2025 Pita Pizza Napoli
      </Box>
    </Box>
  )
}

export default CartPage

