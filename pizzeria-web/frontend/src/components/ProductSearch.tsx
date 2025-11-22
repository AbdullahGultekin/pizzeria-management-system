import { useState, useEffect } from 'react'
import {
  TextField,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
  Chip,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

interface MenuItem {
  id: number
  naam: string
  categorie: string
  prijs: number
  beschrijving?: string
  beschikbaar: number
}

interface ProductSearchProps {
  items: MenuItem[]
  onSelectItem: (item: MenuItem) => void
  onClose?: () => void
}

const ProductSearch = ({ items, onSelectItem, onClose }: ProductSearchProps) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredItems, setFilteredItems] = useState<MenuItem[]>([])
  const [showResults, setShowResults] = useState(false)

  useEffect(() => {
    if (searchTerm.trim().length >= 2) {
      const filtered = items.filter(
        (item) =>
          item.beschikbaar > 0 &&
          (item.naam.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.beschrijving?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.categorie.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      setFilteredItems(filtered.slice(0, 10)) // Limit to 10 results
      setShowResults(true)
    } else {
      setFilteredItems([])
      setShowResults(false)
    }
  }, [searchTerm, items])

  const handleSelect = (item: MenuItem) => {
    onSelectItem(item)
    setSearchTerm('')
    setShowResults(false)
    if (onClose) onClose()
  }

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      <TextField
        fullWidth
        placeholder="Zoek producten... (min. 2 karakters)"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            bgcolor: '#fff',
          },
        }}
        onFocus={() => {
          if (filteredItems.length > 0) setShowResults(true)
        }}
        onBlur={() => {
          // Delay to allow click on result
          setTimeout(() => setShowResults(false), 200)
        }}
      />
      {showResults && filteredItems.length > 0 && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            maxHeight: '400px',
            overflow: 'auto',
            zIndex: 1000,
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
            borderRadius: '10px',
          }}
        >
          <List dense>
            {filteredItems.map((item) => (
              <ListItem key={item.id} disablePadding>
                <ListItemButton onClick={() => handleSelect(item)}>
                  <ListItemText
                    primary={item.naam}
                    secondary={
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {item.categorie}
                        </Typography>
                        {item.beschrijving && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            {item.beschrijving}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  <Chip
                    label={`€${item.prijs.toFixed(2)}`}
                    size="small"
                    sx={{
                      bgcolor: '#e52525',
                      color: '#fff',
                      fontWeight: 600,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
      {showResults && searchTerm.length >= 2 && filteredItems.length === 0 && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            p: 2,
            zIndex: 1000,
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
            borderRadius: '10px',
          }}
        >
          <Typography variant="body2" color="text.secondary" align="center">
            Geen producten gevonden
          </Typography>
        </Paper>
      )}
    </Box>
  )
}

export default ProductSearch


