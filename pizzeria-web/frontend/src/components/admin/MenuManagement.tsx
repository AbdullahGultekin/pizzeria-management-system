import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Chip,
  Tabs,
  Tab,
  CircularProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import { menuAPI } from '../../services/api'

interface MenuItem {
  id: number
  naam: string
  categorie: string
  prijs: number
  beschrijving: string | null
  beschikbaar: number
  volgorde: number
}

interface MenuCategory {
  id: number
  naam: string
  volgorde: number
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const MenuManagement = () => {
  const [menu, setMenu] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [categoryTab, setCategoryTab] = useState(0)
  const [itemDialogOpen, setItemDialogOpen] = useState(false)
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null)
  
  // Form states
  const [itemForm, setItemForm] = useState({
    naam: '',
    categorie: '',
    prijs: 0,
    beschrijving: '',
    beschikbaar: 1,
  })
  const [categoryForm, setCategoryForm] = useState({
    naam: '',
    volgorde: 0,
  })

  useEffect(() => {
    loadMenu()
  }, [])

  const loadMenu = async () => {
    try {
      setLoading(true)
      // Load all items including unavailable ones for admin
      const data = await menuAPI.getMenu(true)
      setMenu(data)
    } catch (err: any) {
      console.error('Error loading menu:', err)
      setError(err.response?.data?.detail || 'Kon menu niet laden')
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCategoryTab(newValue)
  }

  const handleOpenItemDialog = (item?: MenuItem) => {
    if (item) {
      setEditingItem(item)
      setItemForm({
        naam: item.naam,
        categorie: item.categorie,
        prijs: item.prijs,
        beschrijving: item.beschrijving || '',
        beschikbaar: item.beschikbaar,
      })
    } else {
      setEditingItem(null)
      setItemForm({
        naam: '',
        categorie: menu?.categories?.[0]?.naam || '',
        prijs: 0,
        beschrijving: '',
        beschikbaar: 1,
      })
    }
    setItemDialogOpen(true)
  }

  const handleCloseItemDialog = () => {
    setItemDialogOpen(false)
    setEditingItem(null)
    setItemForm({
      naam: '',
      categorie: '',
      prijs: 0,
      beschrijving: '',
      beschikbaar: 1,
    })
  }

  const handleSaveItem = async () => {
    try {
      if (editingItem) {
        await menuAPI.updateItem(editingItem.id, itemForm)
        setSuccess('Menu item bijgewerkt!')
      } else {
        await menuAPI.createItem(itemForm)
        setSuccess('Menu item toegevoegd!')
      }
      handleCloseItemDialog()
      await loadMenu()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kon menu item niet opslaan')
    }
  }

  const handleDeleteItem = async (id: number) => {
    if (!window.confirm('Weet je zeker dat je dit menu item wilt verwijderen?')) {
      return
    }

    try {
      await menuAPI.deleteItem(id)
      setSuccess('Menu item verwijderd!')
      await loadMenu()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kon menu item niet verwijderen')
    }
  }

  const handleOpenCategoryDialog = (category?: MenuCategory) => {
    if (category) {
      setCategoryForm({
        naam: category.naam,
        volgorde: category.volgorde,
      })
    } else {
      setCategoryForm({
        naam: '',
        volgorde: (menu?.categories?.length || 0) + 1,
      })
    }
    setCategoryDialogOpen(true)
  }

  const handleCloseCategoryDialog = () => {
    setCategoryDialogOpen(false)
    setCategoryForm({
      naam: '',
      volgorde: 0,
    })
  }

  const handleSaveCategory = async () => {
    try {
      await menuAPI.createCategory(categoryForm)
      setSuccess('Categorie toegevoegd!')
      handleCloseCategoryDialog()
      await loadMenu()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kon categorie niet opslaan')
    }
  }

  const getItemsByCategory = (categoryName: string) => {
    return menu?.items?.filter((item: MenuItem) => item.categorie === categoryName) || []
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ color: '#d32f2f', fontWeight: 600 }}>
          Menu Beheer
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenCategoryDialog()}
            sx={{ mr: 2, background: '#e52525' }}
          >
            Categorie Toevoegen
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenItemDialog()}
            sx={{ background: '#e52525' }}
          >
            Item Toevoegen
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Paper sx={{ borderRadius: '10px' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={categoryTab}
            onChange={handleCategoryTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                color: '#666',
                fontWeight: 600,
                '&.Mui-selected': {
                  color: '#e52525',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#e52525',
              },
            }}
          >
            {menu?.categories?.map((category: MenuCategory) => (
              <Tab key={category.id} label={category.naam} />
            ))}
          </Tabs>
        </Box>

        {menu?.categories?.map((category: MenuCategory, index: number) => (
          <TabPanel key={category.id} value={categoryTab} index={index}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6" sx={{ color: '#d32f2f' }}>
                {category.naam} ({getItemsByCategory(category.naam).length} items)
              </Typography>
              <Button
                size="small"
                variant="outlined"
                onClick={() => handleOpenItemDialog()}
                sx={{ borderColor: '#e52525', color: '#e52525' }}
              >
                Item Toevoegen
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ background: '#fff5f5' }}>
                    <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Naam</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Beschrijving</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Prijs</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="center">Status</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Acties</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {getItemsByCategory(category.naam).length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">Geen items in deze categorie</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    getItemsByCategory(category.naam).map((item: MenuItem) => (
                      <TableRow key={item.id} hover>
                        <TableCell sx={{ fontWeight: 600 }}>{item.naam}</TableCell>
                        <TableCell>{item.beschrijving || '-'}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                          €{item.prijs.toFixed(2)}
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={item.beschikbaar === 1 ? 'Beschikbaar' : 'Niet beschikbaar'}
                            color={item.beschikbaar === 1 ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenItemDialog(item)}
                            sx={{ color: '#e52525' }}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteItem(item.id)}
                            sx={{ color: '#d32f2f' }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        ))}
      </Paper>

      {/* Item Dialog */}
      <Dialog open={itemDialogOpen} onClose={handleCloseItemDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Menu Item Bewerken' : 'Nieuw Menu Item'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Naam"
            value={itemForm.naam}
            onChange={(e) => setItemForm({ ...itemForm, naam: e.target.value })}
            margin="normal"
            required
          />
          <FormControl fullWidth margin="normal" required>
            <InputLabel>Categorie</InputLabel>
            <Select
              value={itemForm.categorie}
              onChange={(e) => setItemForm({ ...itemForm, categorie: e.target.value })}
              label="Categorie"
            >
              {menu?.categories?.map((cat: MenuCategory) => (
                <MenuItem key={cat.id} value={cat.naam}>
                  {cat.naam}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Prijs"
            type="number"
            value={itemForm.prijs}
            onChange={(e) => setItemForm({ ...itemForm, prijs: parseFloat(e.target.value) || 0 })}
            margin="normal"
            required
            inputProps={{ min: 0, step: 0.01 }}
          />
          <TextField
            fullWidth
            label="Beschrijving"
            value={itemForm.beschrijving}
            onChange={(e) => setItemForm({ ...itemForm, beschrijving: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              value={itemForm.beschikbaar}
              onChange={(e) => setItemForm({ ...itemForm, beschikbaar: e.target.value as number })}
              label="Status"
            >
              <MenuItem value={1}>Beschikbaar</MenuItem>
              <MenuItem value={0}>Niet beschikbaar</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseItemDialog}>Annuleren</Button>
          <Button onClick={handleSaveItem} variant="contained" sx={{ background: '#e52525' }}>
            Opslaan
          </Button>
        </DialogActions>
      </Dialog>

      {/* Category Dialog */}
      <Dialog open={categoryDialogOpen} onClose={handleCloseCategoryDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Nieuwe Categorie</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Naam"
            value={categoryForm.naam}
            onChange={(e) => setCategoryForm({ ...categoryForm, naam: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Volgorde"
            type="number"
            value={categoryForm.volgorde}
            onChange={(e) => setCategoryForm({ ...categoryForm, volgorde: parseInt(e.target.value) || 0 })}
            margin="normal"
            inputProps={{ min: 0 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCategoryDialog}>Annuleren</Button>
          <Button onClick={handleSaveCategory} variant="contained" sx={{ background: '#e52525' }}>
            Opslaan
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default MenuManagement
