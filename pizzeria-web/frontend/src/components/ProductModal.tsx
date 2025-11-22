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
  IconButton,
  Grid,
  Chip,
  Paper,
  Alert,
  Card,
  CardContent,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import LocalPizzaIcon from '@mui/icons-material/LocalPizza'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked'

interface ProductModalProps {
  open: boolean
  product: any
  category: string
  extrasConfig: any
  menuItems?: any[] // All menu items for pizza selection
  onClose: () => void
  onAdd: (productData: any) => void
}

const ProductModal = ({ open, product, category, extrasConfig, menuItems = [], onClose, onAdd }: ProductModalProps) => {
  const [aantal, setAantal] = useState(1)
  const [vlees, setVlees] = useState('')
  const [bijgerechtCounts, setBijgerechtCounts] = useState<Record<string, number>>({})
  const [sausCounts, setSausCounts] = useState<Record<string, number>>({})
  const [garnering, setGarnering] = useState<Set<string>>(new Set())
  const [opmerking, setOpmerking] = useState('')
  const [totalPrice, setTotalPrice] = useState(product?.prijs || 0)
  const [half1, setHalf1] = useState('')
  const [half2, setHalf2] = useState('')

  const catLower = category.toLowerCase()
  const isPizza = catLower.includes("pizza")
  const isPasta = catLower.includes("pasta")
  const isMixSchotel = catLower.includes("mix")
  const isHalfHalf = isPizza && product?.naam?.toLowerCase().includes("half")
  
  // Get pizza items for half-half selection
  const getPizzaItems = () => {
    if (!menuItems || !isPizza) return []
    // Filter items from the same pizza category (small, medium, or large)
    return menuItems.filter((item: any) => {
      const itemCat = item.categorie?.toLowerCase() || ''
      return itemCat === catLower && item.id !== product?.id
    })
  }
  
  const pizzaItems = getPizzaItems()

  // Get product-specific extras (like "Napoli speciaal 2 personen")
  const getProductExtras = () => {
    if (!extrasConfig || typeof extrasConfig !== 'object') return {}
    
    const categoryConfig = extrasConfig[category] || extrasConfig[catLower] || {}
    
    // Check for product-specific config (e.g., "Napoli speciaal 2 personen")
    if (product?.naam && categoryConfig[product.naam]) {
      return categoryConfig[product.naam]
    }
    
    // Check for default config in mix schotels
    if (isMixSchotel && categoryConfig.default) {
      return categoryConfig.default
    }
    
    return categoryConfig
  }

  const productExtras = getProductExtras()
  const categoryExtras = extrasConfig?.[category] || extrasConfig?.[catLower] || {}

  // Get bijgerecht options
  const getBijgerechtOptions = () => {
    return productExtras.bijgerecht || categoryExtras.bijgerecht || []
  }

  // Get bijgerecht_aantal
  const getBijgerechtAantal = () => {
    return productExtras.bijgerecht_aantal || categoryExtras.bijgerecht_aantal || 1
  }

  // Get sauzen options
  const getSauzenOptions = () => {
    return productExtras.sauzen || productExtras.saus || categoryExtras.sauzen || categoryExtras.saus || []
  }

  // Get sauzen_aantal
  const getSauzenAantal = () => {
    return productExtras.sauzen_aantal || categoryExtras.sauzen_aantal || 1
  }

  // Get vlees options
  const getVleesOptions = () => {
    return productExtras.vlees || categoryExtras.vlees || []
  }

  // Get garnering options
  const getGarneringOptions = () => {
    return productExtras.garnering || categoryExtras.garnering || {}
  }

  const bijgerechtOptions = getBijgerechtOptions()
  const bijgerechtAantal = getBijgerechtAantal()
  const sauzenOptions = getSauzenOptions()
  const sauzenAantal = getSauzenAantal()
  const vleesOptions = getVleesOptions()
  const garneringOptions = getGarneringOptions()

  // Initialize bijgerecht counts
  useEffect(() => {
    if (bijgerechtOptions.length > 0) {
      const initialCounts: Record<string, number> = {}
      bijgerechtOptions.forEach((opt: string) => {
        initialCounts[opt] = 0
      })
      setBijgerechtCounts(initialCounts)
    }
  }, [product, category])

  // Initialize sauzen counts
  useEffect(() => {
    if (sauzenOptions.length > 0) {
      const initialCounts: Record<string, number> = {}
      sauzenOptions.forEach((opt: string) => {
        initialCounts[opt] = 0
      })
      setSausCounts(initialCounts)
    }
  }, [product, category])

  // Set default vlees if available
  useEffect(() => {
    if (vleesOptions.length > 0 && !vlees) {
      setVlees(vleesOptions[0])
    }
  }, [vleesOptions, vlees])

  // Calculate total price
  useEffect(() => {
    if (product) {
      setTotalPrice(calculateTotal())
    }
  }, [aantal, vlees, bijgerechtCounts, sausCounts, garnering, half1, half2, product])

  const calculateTotal = () => {
    let basePrice = product?.prijs || 0

    // Calculate garnering price
    let garnPrice = 0
    if (garneringOptions && typeof garneringOptions === 'object') {
      garnering.forEach((garn) => {
        const price = parseFloat(garneringOptions[garn] || 0)
        garnPrice += price
      })
    }

    // Calculate extra sauzen price (€1.50 per extra sauzen)
    const totalSauzen = Object.values(sausCounts).reduce((sum, count) => sum + count, 0)
    const extraSauzen = Math.max(0, totalSauzen - sauzenAantal)
    const extraSauzenPrice = extraSauzen * 1.50

    return (basePrice + garnPrice + extraSauzenPrice) * aantal
  }

  const handleBijgerechtIncrement = (naam: string) => {
    const total = Object.values(bijgerechtCounts).reduce((sum, count) => sum + count, 0)
    if (total >= bijgerechtAantal) {
      return // Maximum reached
    }
    setBijgerechtCounts(prev => ({
      ...prev,
      [naam]: (prev[naam] || 0) + 1
    }))
  }

  const handleBijgerechtDecrement = (naam: string) => {
    setBijgerechtCounts(prev => ({
      ...prev,
      [naam]: Math.max(0, (prev[naam] || 0) - 1)
    }))
  }

  const handleSausIncrement = (naam: string) => {
    setSausCounts(prev => ({
      ...prev,
      [naam]: (prev[naam] || 0) + 1
    }))
  }

  const handleSausDecrement = (naam: string) => {
    setSausCounts(prev => ({
      ...prev,
      [naam]: Math.max(0, (prev[naam] || 0) - 1)
    }))
  }

  const handleGarneringToggle = (naam: string) => {
    setGarnering(prev => {
      const newSet = new Set(prev)
      if (newSet.has(naam)) {
        newSet.delete(naam)
      } else {
        newSet.add(naam)
      }
      return newSet
    })
  }

  const handleAdd = () => {
    // Build bijgerecht list
    const bijgerechtList: string[] = []
    Object.entries(bijgerechtCounts).forEach(([naam, count]) => {
      for (let i = 0; i < count; i++) {
        bijgerechtList.push(naam)
      }
    })

    // Build sauzen list
    const sauzenList: string[] = []
    Object.entries(sausCounts).forEach(([naam, count]) => {
      for (let i = 0; i < count; i++) {
        sauzenList.push(naam)
      }
    })

    // Calculate extra sauzen price
    const totalSauzen = sauzenList.length
    const extraSauzen = Math.max(0, totalSauzen - sauzenAantal)
    const extraSauzenPrice = extraSauzen > 0 ? extraSauzen * 1.50 : 0

    const productData = {
      product_id: product.id,
      naam: product.naam,
      prijs: product.prijs,
      aantal,
      categorie: category,
      opmerking: opmerking || null,
      extras: {
        ...(vlees && { vlees }),
        ...(bijgerechtList.length > 0 && { bijgerecht: bijgerechtList.length === 1 ? bijgerechtList[0] : bijgerechtList }),
        ...(sauzenList.length > 0 && { sauzen: sauzenList }),
        ...(extraSauzenPrice > 0 && { sauzen_toeslag: extraSauzenPrice }),
        ...(garnering.size > 0 && { garnering: Array.from(garnering) }),
        ...(isHalfHalf && half1 && half2 && { half_half: [half1, half2] }),
        ...(opmerking && { opmerking }),
      },
    }

    onAdd(productData)
    handleClose()
  }

  const handleClose = () => {
    setAantal(1)
    setVlees('')
    setBijgerechtCounts({})
    setSausCounts({})
    setGarnering(new Set())
    setOpmerking('')
    setHalf1('')
    setHalf2('')
    onClose()
  }

  if (!product) return null

  const totalBijgerecht = Object.values(bijgerechtCounts).reduce((sum, count) => sum + count, 0)
  const totalSauzen = Object.values(sausCounts).reduce((sum, count) => sum + count, 0)
  const extraSauzen = Math.max(0, totalSauzen - sauzenAantal)
  const extraSauzenPrice = extraSauzen * 1.50

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '20px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
        }
      }}
    >
      <DialogTitle
        sx={{
          bgcolor: '#e52525',
          color: '#fff',
          py: 2.5,
          px: 3,
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
              {product.naam}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              {category}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#fff' }}>
              €{totalPrice.toFixed(2)}
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              Basisprijs: €{product.prijs.toFixed(2)}
            </Typography>
          </Box>
          <IconButton 
            onClick={handleClose}
            sx={{ 
              color: '#fff',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, bgcolor: '#f9f9f9' }}>
        <Box sx={{ p: 3 }}>
          {/* Half-Half Pizza Section */}
          {isHalfHalf && pizzaItems.length > 0 && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px', border: '2px solid #e52525' }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocalPizzaIcon /> Half-Half Pizza
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Kies 2 verschillende pizza's:
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>Pizza 1:</Typography>
                  <Box sx={{ maxHeight: '200px', overflowY: 'auto', p: 1, bgcolor: '#f5f5f5', borderRadius: '8px' }}>
                    {pizzaItems.map((pizza: any) => {
                      const isSelected = half1 === pizza.naam
                      return (
                        <Card
                          key={pizza.id}
                          elevation={0}
                          onClick={() => setHalf1(pizza.naam)}
                          sx={{
                            mb: 1,
                            border: '2px solid',
                            borderColor: isSelected ? '#e52525' : '#e0e0e0',
                            borderRadius: '8px',
                            bgcolor: isSelected ? '#fff5f5' : '#fff',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            '&:hover': {
                              borderColor: '#e52525',
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Typography variant="body2" sx={{ fontWeight: isSelected ? 700 : 600, color: isSelected ? '#e52525' : '#333' }}>
                              {pizza.naam}
                            </Typography>
                            {pizza.beschrijving && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                {pizza.beschrijving}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      )
                    })}
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>Pizza 2:</Typography>
                  <Box sx={{ maxHeight: '200px', overflowY: 'auto', p: 1, bgcolor: '#f5f5f5', borderRadius: '8px' }}>
                    {pizzaItems.map((pizza: any) => {
                      const isSelected = half2 === pizza.naam
                      return (
                        <Card
                          key={pizza.id}
                          elevation={0}
                          onClick={() => setHalf2(pizza.naam)}
                          sx={{
                            mb: 1,
                            border: '2px solid',
                            borderColor: isSelected ? '#e52525' : '#e0e0e0',
                            borderRadius: '8px',
                            bgcolor: isSelected ? '#fff5f5' : '#fff',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            '&:hover': {
                              borderColor: '#e52525',
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Typography variant="body2" sx={{ fontWeight: isSelected ? 700 : 600, color: isSelected ? '#e52525' : '#333' }}>
                              {pizza.naam}
                            </Typography>
                            {pizza.beschrijving && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                {pizza.beschrijving}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      )
                    })}
                  </Box>
                </Grid>
              </Grid>
              {half1 && half2 && half1 === half2 && (
                <Alert severity="warning" sx={{ mt: 2, borderRadius: '8px' }}>
                  Kies 2 verschillende pizza's voor een half-half pizza.
                </Alert>
              )}
            </Paper>
          )}

          {/* Vlees Section */}
          {vleesOptions.length > 0 && !isPizza && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700 }}>
                🥩 Keuze Vlees
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
                {vleesOptions.map((opt: string) => (
                  <Chip
                    key={opt}
                    label={opt}
                    onClick={() => setVlees(opt)}
                    icon={vlees === opt ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                    sx={{
                      bgcolor: vlees === opt ? '#e52525' : '#f5f5f5',
                      color: vlees === opt ? '#fff' : '#333',
                      fontWeight: vlees === opt ? 700 : 500,
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: vlees === opt ? '#c41e1e' : '#fff5f5',
                      },
                    }}
                  />
                ))}
              </Box>
            </Paper>
          )}

          {/* Bijgerecht Section */}
          {bijgerechtOptions.length > 0 && !isPasta && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e52525', fontWeight: 700 }}>
                  🍟 Bijgerecht{bijgerechtAantal > 1 ? 'en' : ''} ({bijgerechtAantal})
                </Typography>
                <Chip
                  label={`Gekozen: ${totalBijgerecht} / ${bijgerechtAantal}`}
                  color={totalBijgerecht >= bijgerechtAantal ? 'success' : 'default'}
                  sx={{ fontWeight: 600 }}
                />
              </Box>
              <Grid container spacing={2}>
                {bijgerechtOptions.map((opt: string) => {
                  const count = bijgerechtCounts[opt] || 0
                  return (
                    <Grid item xs={12} sm={6} key={opt}>
                      <Card
                        elevation={0}
                        sx={{
                          border: '2px solid',
                          borderColor: count > 0 ? '#e52525' : '#e0e0e0',
                          borderRadius: '10px',
                          bgcolor: count > 0 ? '#fff5f5' : '#fff',
                          transition: 'all 0.2s',
                          '&:hover': {
                            borderColor: '#e52525',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(229, 37, 37, 0.15)',
                          },
                        }}
                      >
                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ fontWeight: 600, flex: 1 }}>
                              {opt}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleBijgerechtDecrement(opt)}
                                disabled={count === 0}
                                sx={{
                                  bgcolor: '#f5f5f5',
                                  color: '#e52525',
                                  '&:hover': { bgcolor: '#ffe6e6' },
                                  '&:disabled': { opacity: 0.3 },
                                }}
                              >
                                <RemoveIcon fontSize="small" />
                              </IconButton>
                              <Typography
                                variant="h6"
                                sx={{
                                  minWidth: '30px',
                                  textAlign: 'center',
                                  fontWeight: 700,
                                  color: count > 0 ? '#e52525' : '#999',
                                }}
                              >
                                {count}
                              </Typography>
                              <IconButton
                                size="small"
                                onClick={() => handleBijgerechtIncrement(opt)}
                                disabled={totalBijgerecht >= bijgerechtAantal}
                                sx={{
                                  bgcolor: '#e52525',
                                  color: '#fff',
                                  '&:hover': { bgcolor: '#c41e1e' },
                                  '&:disabled': { bgcolor: '#ccc' },
                                }}
                              >
                                <AddIcon fontSize="small" />
                              </IconButton>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                })}
              </Grid>
            </Paper>
          )}

          {/* Sauzen Section */}
          {sauzenOptions.length > 0 && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e52525', fontWeight: 700 }}>
                  🍯 Sauzen
                </Typography>
                <Box sx={{ textAlign: 'right' }}>
                  <Chip
                    label={`Gekozen: ${totalSauzen} (${sauzenAantal} gratis)`}
                    color="info"
                    sx={{ fontWeight: 600, mb: 0.5 }}
                  />
                  {extraSauzen > 0 && (
                    <Typography variant="caption" sx={{ color: '#d32f2f', fontWeight: 600, display: 'block' }}>
                      Extra: {extraSauzen} × €1,50 = €{extraSauzenPrice.toFixed(2)}
                    </Typography>
                  )}
                </Box>
              </Box>
              <Grid container spacing={2}>
                {sauzenOptions.map((opt: string) => {
                  const count = sausCounts[opt] || 0
                  return (
                    <Grid item xs={12} sm={6} key={opt}>
                      <Card
                        elevation={0}
                        sx={{
                          border: '2px solid',
                          borderColor: count > 0 ? '#e52525' : '#e0e0e0',
                          borderRadius: '10px',
                          bgcolor: count > 0 ? '#fff5f5' : '#fff',
                          transition: 'all 0.2s',
                          '&:hover': {
                            borderColor: '#e52525',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(229, 37, 37, 0.15)',
                          },
                        }}
                      >
                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ fontWeight: 600, flex: 1 }}>
                              {opt}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleSausDecrement(opt)}
                                disabled={count === 0}
                                sx={{
                                  bgcolor: '#f5f5f5',
                                  color: '#e52525',
                                  '&:hover': { bgcolor: '#ffe6e6' },
                                  '&:disabled': { opacity: 0.3 },
                                }}
                              >
                                <RemoveIcon fontSize="small" />
                              </IconButton>
                              <Typography
                                variant="h6"
                                sx={{
                                  minWidth: '30px',
                                  textAlign: 'center',
                                  fontWeight: 700,
                                  color: count > 0 ? '#e52525' : '#999',
                                }}
                              >
                                {count}
                              </Typography>
                              <IconButton
                                size="small"
                                onClick={() => handleSausIncrement(opt)}
                                sx={{
                                  bgcolor: '#e52525',
                                  color: '#fff',
                                  '&:hover': { bgcolor: '#c41e1e' },
                                }}
                              >
                                <AddIcon fontSize="small" />
                              </IconButton>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                })}
              </Grid>
              {sauzenAantal > 0 && (
                <Alert severity="info" sx={{ mt: 2, borderRadius: '8px' }}>
                  Eerste {sauzenAantal} sauzen zijn inbegrepen. Extra sauzen kosten €1,50 per stuk.
                </Alert>
              )}
            </Paper>
          )}

          {/* Pasta Type Selection */}
          {isPasta && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700 }}>
                🍝 Keuze Pasta
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
                {['Spaghetti', 'Tagliatelle', 'Macaroni'].map((type) => (
                  <Chip
                    key={type}
                    label={type}
                    onClick={() => setVlees(type)}
                    icon={vlees === type ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                    sx={{
                      bgcolor: vlees === type ? '#e52525' : '#f5f5f5',
                      color: vlees === type ? '#fff' : '#333',
                      fontWeight: vlees === type ? 700 : 500,
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: vlees === type ? '#c41e1e' : '#fff5f5',
                      },
                    }}
                  />
                ))}
              </Box>
            </Paper>
          )}

          {/* Garnering Section */}
          {garneringOptions && Object.keys(garneringOptions).length > 0 && (
            <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700 }}>
                🌿 Extra Garneringen
              </Typography>
              <Grid container spacing={1.5}>
                {Object.entries(garneringOptions).map(([naam, price]: [string, any]) => {
                  const isSelected = garnering.has(naam)
                  const priceNum = parseFloat(price || 0)
                  return (
                    <Grid item xs={6} sm={4} md={3} key={naam}>
                      <Card
                        elevation={0}
                        onClick={() => handleGarneringToggle(naam)}
                        sx={{
                          border: '2px solid',
                          borderColor: isSelected ? '#e52525' : '#e0e0e0',
                          borderRadius: '10px',
                          bgcolor: isSelected ? '#fff5f5' : '#fff',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          '&:hover': {
                            borderColor: '#e52525',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 12px rgba(229, 37, 37, 0.15)',
                          },
                        }}
                      >
                        <CardContent sx={{ p: 1.5, textAlign: 'center', '&:last-child': { pb: 1.5 } }}>
                          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                            {naam}
                          </Typography>
                          {priceNum > 0 && (
                            <Typography variant="caption" sx={{ color: '#e52525', fontWeight: 600 }}>
                              +€{priceNum.toFixed(2)}
                            </Typography>
                          )}
                          {priceNum === 0 && (
                            <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 600 }}>
                              Gratis
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                })}
              </Grid>
            </Paper>
          )}

          {/* Opmerking Section */}
          <Paper elevation={0} sx={{ p: 2.5, mb: 3, bgcolor: '#fff', borderRadius: '12px' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700 }}>
              📝 Opmerking (optioneel)
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={opmerking}
              onChange={(e) => setOpmerking(e.target.value)}
              placeholder="Bijv. zonder ui, extra pittig, etc."
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '10px',
                },
              }}
            />
          </Paper>

          {/* Aantal Section */}
          <Paper elevation={0} sx={{ p: 2.5, bgcolor: '#fff', borderRadius: '12px' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#e52525', fontWeight: 700 }}>
              📊 Aantal
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton
                onClick={() => setAantal(Math.max(1, aantal - 1))}
                disabled={aantal <= 1}
                sx={{
                  bgcolor: '#f5f5f5',
                  color: '#e52525',
                  '&:hover': { bgcolor: '#ffe6e6' },
                  '&:disabled': { opacity: 0.3 },
                }}
              >
                <RemoveIcon />
              </IconButton>
              <TextField
                type="number"
                value={aantal}
                onChange={(e) => setAantal(Math.max(1, parseInt(e.target.value) || 1))}
                inputProps={{ min: 1, style: { textAlign: 'center', fontSize: '1.2em', fontWeight: 700 } }}
                sx={{
                  width: '100px',
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '10px',
                  },
                }}
              />
              <IconButton
                onClick={() => setAantal(aantal + 1)}
                sx={{
                  bgcolor: '#e52525',
                  color: '#fff',
                  '&:hover': { bgcolor: '#c41e1e' },
                }}
              >
                <AddIcon />
              </IconButton>
            </Box>
          </Paper>
        </Box>
      </DialogContent>

      <DialogActions
        sx={{
          p: 3,
          bgcolor: '#f9f9f9',
          borderTop: '1px solid #e0e0e0',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Totaal prijs:
            </Typography>
            <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
              €{totalPrice.toFixed(2)}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              onClick={handleClose}
              variant="outlined"
              sx={{
                borderColor: '#e52525',
                color: '#e52525',
                fontWeight: 600,
                px: 3,
                py: 1.5,
                borderRadius: '25px',
                '&:hover': {
                  borderColor: '#c41e1e',
                  bgcolor: '#fff5f5',
                },
              }}
            >
              Annuleren
            </Button>
            <Button
              variant="contained"
              onClick={handleAdd}
              startIcon={<AddIcon />}
              sx={{
                bgcolor: '#e52525',
                color: '#fff',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                borderRadius: '25px',
                boxShadow: '0 4px 12px rgba(229, 37, 37, 0.3)',
                '&:hover': {
                  bgcolor: '#c41e1e',
                  boxShadow: '0 6px 16px rgba(229, 37, 37, 0.4)',
                },
              }}
            >
              Toevoegen aan winkelwagen
            </Button>
          </Box>
        </Box>
      </DialogActions>
    </Dialog>
  )
}

export default ProductModal
