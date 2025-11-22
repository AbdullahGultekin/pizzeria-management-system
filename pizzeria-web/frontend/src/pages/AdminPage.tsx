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
} from '@mui/material'
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
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const AdminPage = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9' }}>
      <AppBar position="static" className="navbar-light">
        <Toolbar className="navbar-container">
          <Typography variant="h6" component="div" className="navbar-title" sx={{ flexGrow: 1 }}>
            Admin Dashboard - {user?.username}
          </Typography>
          <Button 
            color="inherit" 
            onClick={() => navigate('/kassa')}
            sx={{ color: '#333', fontWeight: 600, mr: 2 }}
          >
            Kassa
          </Button>
          <Button 
            color="inherit" 
            onClick={logout}
            sx={{ color: '#333', fontWeight: 600 }}
          >
            Uitloggen
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Paper sx={{ borderRadius: '20px', boxShadow: '0 4px 25px rgba(229, 37, 37, 0.1)' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="admin tabs"
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
              <Tab label="📊 Bestellingen" />
              <Tab label="🍕 Menu Beheer" />
              <Tab label="📈 Rapportages" />
              <Tab label="⚙️ Instellingen" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <OrdersOverview />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <MenuManagement />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Reports />
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <PrinterSettings />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  )
}

export default AdminPage
