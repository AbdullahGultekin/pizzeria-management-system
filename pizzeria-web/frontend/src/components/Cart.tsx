import { Box, Paper, Typography, Button, IconButton } from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'

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

interface CartProps {
  items: CartItem[]
  onUpdateQuantity: (id: string, delta: number) => void
  onRemoveItem: (id: string) => void
  onPlaceOrder: () => void
  loading?: boolean
}

const Cart = ({ items, onUpdateQuantity, onRemoveItem, onPlaceOrder, loading }: CartProps) => {
  const total = items.reduce((sum, item) => sum + item.prijs * item.aantal, 0)

  return (
    <Paper 
      className="order-summary"
      sx={{ 
        p: 0, 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        borderRadius: '20px',
        boxShadow: '0 4px 25px rgba(229, 37, 37, 0.08)'
      }}
    >
      <Typography variant="h6" className="order-summary h2" sx={{ 
        margin: 0,
        padding: '20px',
        color: '#e52525',
        fontSize: '1.4em',
        textAlign: 'center',
        borderBottom: '2px solid #ffe6e6'
      }}>
        Winkelwagen
      </Typography>
      <Box className="order-content" sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Box className="order-list" sx={{ flex: 1, overflowY: 'auto', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4, fontStyle: 'italic' }}>
            Winkelwagen is leeg
          </Typography>
        ) : (
          items.map((item) => (
            <Box key={item.id} className="order-item" sx={{ 
              background: '#fff',
              borderRadius: '12px',
              padding: '12px',
              border: '1px solid #ffe6e6',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '10px',
              '&:hover': {
                borderColor: '#e52525',
                transform: 'translateX(3px)',
                boxShadow: '0 2px 8px rgba(229, 37, 37, 0.08)'
              }
            }}>
              <Box className="order-item-content" sx={{ flex: 1 }}>
                <Box className="order-item-header" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                  <Typography className="order-item-name" variant="body1" sx={{ fontWeight: 600, color: '#333' }}>
                    {item.product_naam}
                  </Typography>
                  <Typography className="order-item-price" variant="body2" sx={{ color: '#e52525', fontWeight: 600 }}>
                    €{(item.prijs * item.aantal).toFixed(2)}
                  </Typography>
                </Box>
                <Box>
                  {item.extras && (
                    <Box sx={{ mt: 0.5 }}>
                      {item.extras.vlees && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Vlees: {item.extras.vlees}
                        </Typography>
                      )}
                      {item.extras.bijgerecht && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Bijgerecht: {item.extras.bijgerecht}
                        </Typography>
                      )}
                      {item.extras.saus1 && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Saus: {item.extras.saus1}
                          {item.extras.saus2 && `, ${item.extras.saus2}`}
                        </Typography>
                      )}
                      {item.extras.garnering && item.extras.garnering.length > 0 && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Garnering: {item.extras.garnering.join(', ')}
                        </Typography>
                      )}
                    </Box>
                  )}
                  {item.opmerking && (
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5, fontStyle: 'italic' }}>
                      Opmerking: {item.opmerking}
                    </Typography>
                  )}
                </Box>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <IconButton
                  size="small"
                  onClick={() => onUpdateQuantity(item.id, -1)}
                  disabled={item.aantal <= 1}
                >
                  <RemoveIcon fontSize="small" />
                </IconButton>
                <Typography variant="body2" sx={{ minWidth: '20px', textAlign: 'center' }}>
                  {item.aantal}
                </Typography>
                <IconButton
                  size="small"
                  onClick={() => onUpdateQuantity(item.id, 1)}
                >
                  <AddIcon fontSize="small" />
                </IconButton>
                <IconButton
                  size="small"
                  className="remove-btn"
                  onClick={() => onRemoveItem(item.id)}
                  sx={{ 
                    color: '#e52525',
                    background: 'none',
                    border: 'none',
                    padding: '5px',
                    opacity: 0.7,
                    '&:hover': {
                      opacity: 1,
                      transform: 'scale(1.1)'
                    }
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
            </Box>
          ))
        )}
        </Box>

        {items.length > 0 && (
          <Box className="order-footer" sx={{ 
            background: '#fff',
            padding: '15px',
            borderTop: '1px solid #ffe6e6',
            borderRadius: '0 0 20px 20px'
          }}>
            <Box className="order-totals" sx={{ marginBottom: '15px' }}>
              <Box className="order-line total" sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '15px',
                background: 'linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%)',
                borderRadius: '10px',
                border: '2px solid #e52525',
                boxShadow: '0 2px 8px rgba(229, 37, 37, 0.1)'
              }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#333' }}>
                  Totaal
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: '#e52525', fontSize: '1.5em' }}>
                  €{total.toFixed(2)}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                {items.reduce((sum, item) => sum + item.aantal, 0)} {items.reduce((sum, item) => sum + item.aantal, 0) === 1 ? 'item' : 'items'}
              </Typography>
            </Box>
            <Box className="order-actions" sx={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <Button
                variant="contained"
                fullWidth
                onClick={onPlaceOrder}
                disabled={items.length === 0 || loading}
                sx={{
                  background: '#e52525',
                  color: '#fff',
                  padding: '14px',
                  fontSize: '1.1em',
                  fontWeight: 700,
                  borderRadius: '10px',
                  textTransform: 'none',
                  boxShadow: '0 4px 12px rgba(229, 37, 37, 0.3)',
                  '&:hover': {
                    background: '#c41e1e',
                    boxShadow: '0 6px 16px rgba(229, 37, 37, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  '&:disabled': {
                    background: '#ccc',
                    boxShadow: 'none',
                  },
                  transition: 'all 0.2s ease'
                }}
              >
                {loading ? 'Plaatsen...' : 'Bestelling Plaatsen (Ctrl+Enter)'}
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    </Paper>
  )
}

export default Cart

