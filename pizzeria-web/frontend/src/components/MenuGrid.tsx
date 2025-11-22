import { useState } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  Chip,
  Tabs,
  Tab,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'

interface MenuItem {
  id: number
  naam: string
  categorie: string
  prijs: number
  beschrijving?: string
  beschikbaar: number
}

interface MenuCategory {
  id: number
  naam: string
  volgorde: number
}

interface MenuGridProps {
  categories: MenuCategory[]
  items: MenuItem[]
  onAddToCart: (item: MenuItem) => void
}

const MenuGrid = ({ categories, items, onAddToCart }: MenuGridProps) => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    categories && categories.length > 0 ? categories[0].naam : null
  )

  const filteredItems = selectedCategory
    ? items.filter((item) => item.categorie === selectedCategory)
    : items || []

  const handleCategoryChange = (_event: React.SyntheticEvent, newValue: string) => {
    setSelectedCategory(newValue)
  }

  return (
    <Box>
      {categories.length > 0 && (
        <Tabs
          value={selectedCategory || false}
          onChange={handleCategoryChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ mb: 2 }}
        >
          {categories.map((category) => (
            <Tab key={category.id} label={category.naam} value={category.naam} />
          ))}
        </Tabs>
      )}

      <Grid container spacing={2}>
        {filteredItems.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                Geen producten beschikbaar in deze categorie
              </Typography>
            </Paper>
          </Grid>
        ) : (
          filteredItems.map((item) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
              <Paper
                className="product-list-item"
                sx={{
                  p: 2,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  background: '#fff',
                  borderRadius: '10px',
                  boxShadow: '0 3px 14px -14px #b44',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 20px rgba(229, 37, 37, 0.15)',
                  },
                }}
              >
                <Typography variant="h6" className="product-list-name" gutterBottom sx={{ fontWeight: 600 }}>
                  {item.naam}
                </Typography>
                {item.beschrijving && (
                  <Typography variant="body2" className="product-list-desc" sx={{ mb: 1, flexGrow: 1, color: '#888', fontSize: '0.96em' }}>
                    {item.beschrijving}
                  </Typography>
                )}
                <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mt: 'auto' }}>
                  <Typography variant="h6" className="product-list-price" sx={{ color: '#d32f2f', fontWeight: 'bold' }}>
                    €{item.prijs.toFixed(2)}
                  </Typography>
                  <Button
                    className="open-modal-btn"
                    variant="contained"
                    size="small"
                    onClick={() => onAddToCart(item)}
                    disabled={item.beschikbaar === 0}
                    sx={{
                      background: '#e52525',
                      color: '#fff',
                      borderRadius: '8px',
                      minWidth: '40px',
                      '&:hover': {
                        background: '#ffcc00',
                        color: '#e52525'
                      }
                    }}
                  >
                    <AddIcon />
                  </Button>
                </Box>
                {item.beschikbaar === 0 && (
                  <Chip label="Niet beschikbaar" color="error" size="small" sx={{ mt: 1 }} />
                )}
              </Paper>
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  )
}

export default MenuGrid

