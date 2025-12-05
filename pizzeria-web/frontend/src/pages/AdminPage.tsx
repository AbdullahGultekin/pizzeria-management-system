import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  AppBar,
  Toolbar,
  Tabs,
  Tab,
  useMediaQuery,
  useTheme,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import OrdersOverview from '../components/admin/OrdersOverview'
import MenuManagement from '../components/admin/MenuManagement'
import Reports from '../components/admin/Reports'
import PrinterSettings from '../components/admin/PrinterSettings'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && children}
    </div>
  )
}

const AdminPage = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [tabValue, setTabValue] = useState(0)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
    if (isMobile) {
      setMobileDrawerOpen(false)
    }
  }

  const tabs = [
    { label: '📊 Bestellingen', icon: '📊' },
    { label: '🍕 Menu Beheer', icon: '🍕' },
    { label: '📈 Rapportages', icon: '📈' },
    { label: '⚙️ Instellingen', icon: '⚙️' },
  ]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9' }}>
      <AppBar position="static" className="navbar-light">
        <Toolbar className="navbar-container" sx={{ flexWrap: { xs: 'wrap', sm: 'nowrap' } }}>
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={() => setMobileDrawerOpen(true)}
              sx={{ mr: 2, color: '#333' }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography 
            variant="h6" 
            component="div" 
            className="navbar-title" 
            sx={{ 
              flexGrow: 1,
              fontSize: { xs: '0.9rem', sm: '1.25rem' },
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            Admin - {user?.username}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: { xs: 'wrap', sm: 'nowrap' } }}>
            <Button 
              color="inherit" 
              onClick={() => navigate('/kassa')}
              sx={{ 
                color: '#333', 
                fontWeight: 600, 
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                px: { xs: 1, sm: 2 },
              }}
            >
              Kassa
            </Button>
            <Button 
              color="inherit" 
              onClick={logout}
              sx={{ 
                color: '#333', 
                fontWeight: 600,
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                px: { xs: 1, sm: 2 },
              }}
            >
              Uitloggen
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="left"
        open={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
        PaperProps={{
          sx: { width: 250 }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Menu
          </Typography>
          <List>
            {tabs.map((tab, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  selected={tabValue === index}
                  onClick={() => handleTabChange({} as React.SyntheticEvent, index)}
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: '#fff5f5',
                      color: '#e52525',
                      '&:hover': {
                        bgcolor: '#fff5f5',
                      },
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <Typography>{tab.icon}</Typography>
                  </ListItemIcon>
                  <ListItemText 
                    primary={tab.label.replace(/[📊🍕📈⚙️]/g, '').trim()} 
                    primaryTypographyProps={{
                      fontSize: '0.9rem',
                      fontWeight: tabValue === index ? 600 : 400,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Container 
        maxWidth="xl" 
        sx={{ 
          mt: { xs: 1, sm: 3 }, 
          mb: { xs: 1, sm: 3 },
          px: { xs: 1, sm: 3 },
        }}
      >
        <Paper 
          sx={{ 
            borderRadius: { xs: '10px', sm: '20px' }, 
            boxShadow: '0 4px 25px rgba(229, 37, 37, 0.1)',
            overflow: 'hidden',
          }}
        >
          {!isMobile && (
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                aria-label="admin tabs"
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  '& .MuiTab-root': {
                    color: '#666',
                    fontWeight: 600,
                    minHeight: 64,
                    '&.Mui-selected': {
                      color: '#e52525',
                    },
                  },
                  '& .MuiTabs-indicator': {
                    backgroundColor: '#e52525',
                  },
                }}
              >
                {tabs.map((tab, index) => (
                  <Tab key={index} label={tab.label} />
                ))}
              </Tabs>
            </Box>
          )}

          {isMobile && (
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: '#fff5f5' }}>
              <Typography variant="h6" sx={{ color: '#e52525', fontWeight: 600 }}>
                {tabs[tabValue].label}
              </Typography>
            </Box>
          )}

          <TabPanel value={tabValue} index={0}>
            <Box sx={{ p: { xs: 1, sm: 3 } }}>
              <OrdersOverview />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ p: { xs: 1, sm: 3 } }}>
              <MenuManagement />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ p: { xs: 1, sm: 3 } }}>
              <Reports />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Box sx={{ p: { xs: 1, sm: 3 } }}>
              <PrinterSettings />
            </Box>
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  )
}

export default AdminPage
