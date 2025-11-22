import { useState, useEffect } from 'react'
import {
  TextField,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material'
import { customerAPI } from '../services/api'

interface Customer {
  id: number
  naam: string
  telefoon: string
  straat?: string
  huisnummer?: string
  plaats?: string
}

interface CustomerSearchProps {
  onSelectCustomer: (customer: Customer | null) => void
  selectedCustomer: Customer | null
}

const CustomerSearch = ({ onSelectCustomer, selectedCustomer }: CustomerSearchProps) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)

  useEffect(() => {
    const searchCustomers = async () => {
      if (searchTerm.length < 2) {
        setCustomers([])
        setShowResults(false)
        return
      }

      setLoading(true)
      try {
        const results = await customerAPI.getAll({ search: searchTerm, limit: 10 })
        setCustomers(results)
        setShowResults(true)
      } catch (error) {
        console.error('Error searching customers:', error)
        setCustomers([])
      } finally {
        setLoading(false)
      }
    }

    const debounceTimer = setTimeout(searchCustomers, 300)
    return () => clearTimeout(debounceTimer)
  }, [searchTerm])

  const handleSelectCustomer = (customer: Customer) => {
    onSelectCustomer(customer)
    setSearchTerm(customer.telefoon)
    setShowResults(false)
  }

  const handleClear = () => {
    onSelectCustomer(null)
    setSearchTerm('')
    setShowResults(false)
  }

  return (
    <Box sx={{ position: 'relative' }}>
      <TextField
        fullWidth
        label="Zoek klant (telefoon of naam)"
        variant="outlined"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onFocus={() => searchTerm.length >= 2 && setShowResults(true)}
        InputProps={{
          endAdornment: loading ? <CircularProgress size={20} /> : null,
        }}
      />

      {selectedCustomer && (
        <Paper sx={{ mt: 1, p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="body1" fontWeight="bold">
                {selectedCustomer.naam || 'Geen naam'}
              </Typography>
              <Typography variant="body2">
                {selectedCustomer.telefoon}
              </Typography>
              {selectedCustomer.straat && (
                <Typography variant="body2">
                  {selectedCustomer.straat} {selectedCustomer.huisnummer}, {selectedCustomer.plaats}
                </Typography>
              )}
            </Box>
            <Typography
              variant="body2"
              sx={{ cursor: 'pointer', textDecoration: 'underline' }}
              onClick={handleClear}
            >
              Verwijder
            </Typography>
          </Box>
        </Paper>
      )}

      {showResults && customers.length > 0 && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            maxHeight: '300px',
            overflowY: 'auto',
            mt: 1,
          }}
        >
          <List>
            {customers.map((customer) => (
              <ListItem key={customer.id} disablePadding>
                <ListItemButton onClick={() => handleSelectCustomer(customer)}>
                  <ListItemText
                    primary={customer.naam || 'Geen naam'}
                    secondary={
                      <>
                        {customer.telefoon}
                        {customer.straat && ` • ${customer.straat} ${customer.huisnummer}, ${customer.plaats}`}
                      </>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  )
}

export default CustomerSearch


