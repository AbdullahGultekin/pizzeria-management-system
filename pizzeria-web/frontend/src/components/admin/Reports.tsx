import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  CircularProgress,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import { format, parseISO } from 'date-fns'
import PrintIcon from '@mui/icons-material/Print'
import { reportsAPI } from '../../services/api'

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

const Reports = () => {
  const [tabValue, setTabValue] = useState(0)
  const [dailyDate, setDailyDate] = useState<Date | null>(new Date())
  const [monthlyYear, setMonthlyYear] = useState(new Date().getFullYear())
  const [monthlyMonth, setMonthlyMonth] = useState(new Date().getMonth() + 1)
  const [zReportDate, setZReportDate] = useState<Date | null>(new Date())
  
  const [dailyReport, setDailyReport] = useState<any>(null)
  const [monthlyReport, setMonthlyReport] = useState<any>(null)
  const [zReport, setZReport] = useState<any>(null)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const loadDailyReport = async () => {
    if (!dailyDate) return
    
    try {
      setLoading(true)
      setError('')
      const dateStr = format(dailyDate, 'yyyy-MM-dd')
      const data = await reportsAPI.getDailyReport(dateStr)
      setDailyReport(data)
    } catch (err: any) {
      console.error('Error loading daily report:', err)
      setError(err.response?.data?.detail || 'Kon dagelijkse rapportage niet laden')
    } finally {
      setLoading(false)
    }
  }

  const loadMonthlyReport = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await reportsAPI.getMonthlyReport(monthlyYear, monthlyMonth)
      setMonthlyReport(data)
    } catch (err: any) {
      console.error('Error loading monthly report:', err)
      setError(err.response?.data?.detail || 'Kon maandelijkse rapportage niet laden')
    } finally {
      setLoading(false)
    }
  }

  const loadZReport = async () => {
    if (!zReportDate) return
    
    try {
      setLoading(true)
      setError('')
      const dateStr = format(zReportDate, 'yyyy-MM-dd')
      const data = await reportsAPI.getZReport(dateStr)
      setZReport(data)
    } catch (err: any) {
      console.error('Error loading Z-report:', err)
      setError(err.response?.data?.detail || 'Kon Z-rapport niet laden')
    } finally {
      setLoading(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ color: '#d32f2f', fontWeight: 600 }}>
          Rapportages
        </Typography>
        <Button
          variant="contained"
          startIcon={<PrintIcon />}
          onClick={handlePrint}
          sx={{ background: '#e52525' }}
        >
          Afdrukken
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper sx={{ borderRadius: '10px' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
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
            <Tab label="📊 Dagelijks Rapport" />
            <Tab label="📅 Maandelijks Rapport" />
            <Tab label="🔒 Z-Rapport" />
          </Tabs>
        </Box>

        {/* Daily Report Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Selecteer datum"
              type="date"
              value={dailyDate ? format(dailyDate, 'yyyy-MM-dd') : ''}
              onChange={(e) => setDailyDate(e.target.value ? new Date(e.target.value) : null)}
              InputLabelProps={{ shrink: true }}
              sx={{ mr: 2, width: 200 }}
            />
            <Button
              variant="contained"
              onClick={loadDailyReport}
              disabled={loading || !dailyDate}
              sx={{ background: '#e52525' }}
            >
              Laad Rapportage
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : dailyReport ? (
            <Box>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Totaal Bestellingen
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        {dailyReport.total_orders}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Totale Omzet
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        €{dailyReport.total_revenue.toFixed(2)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Gemiddelde Bestelling
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        €{dailyReport.average_order_value.toFixed(2)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {dailyReport.hourly_stats && dailyReport.hourly_stats.length > 0 && (
                <TableContainer component={Paper} sx={{ mb: 3 }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ background: '#fff5f5' }}>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Uur</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Bestellingen</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Omzet</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dailyReport.hourly_stats.map((stat: any) => (
                        <TableRow key={stat.hour}>
                          <TableCell>{stat.hour}:00</TableCell>
                          <TableCell align="right">{stat.orders}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                            €{stat.revenue.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {dailyReport.product_stats && dailyReport.product_stats.length > 0 && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ background: '#fff5f5' }}>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Product</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Aantal</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Omzet</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dailyReport.product_stats
                        .sort((a: any, b: any) => b.omzet - a.omzet)
                        .slice(0, 20)
                        .map((stat: any) => (
                          <TableRow key={stat.naam}>
                            <TableCell>{stat.naam}</TableCell>
                            <TableCell align="right">{stat.aantal}</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                              €{stat.omzet.toFixed(2)}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          ) : (
            <Alert severity="info">
              Selecteer een datum en klik op "Laad Rapportage" om de dagelijkse rapportage te bekijken.
            </Alert>
          )}
        </TabPanel>

        {/* Monthly Report Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Jaar"
              type="number"
              value={monthlyYear}
              onChange={(e) => setMonthlyYear(parseInt(e.target.value) || new Date().getFullYear())}
              sx={{ mr: 2, width: 120 }}
            />
            <TextField
              label="Maand"
              type="number"
              value={monthlyMonth}
              onChange={(e) => setMonthlyMonth(parseInt(e.target.value) || 1)}
              inputProps={{ min: 1, max: 12 }}
              sx={{ mr: 2, width: 120 }}
            />
            <Button
              variant="contained"
              onClick={loadMonthlyReport}
              disabled={loading}
              sx={{ background: '#e52525' }}
            >
              Laad Rapportage
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : monthlyReport ? (
            <Box>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Totaal Bestellingen
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        {monthlyReport.total_orders}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Totale Omzet
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        €{monthlyReport.total_revenue.toFixed(2)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Gemiddelde Bestelling
                      </Typography>
                      <Typography variant="h4" sx={{ color: '#e52525', fontWeight: 700 }}>
                        €{monthlyReport.average_order_value.toFixed(2)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {monthlyReport.daily_stats && monthlyReport.daily_stats.length > 0 && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ background: '#fff5f5' }}>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Datum</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Bestellingen</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Omzet</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {monthlyReport.daily_stats.map((stat: any) => (
                        <TableRow key={stat.date}>
                          <TableCell>
                            {format(parseISO(stat.date), 'dd MMM yyyy')}
                          </TableCell>
                          <TableCell align="right">{stat.orders}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                            €{stat.revenue.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          ) : (
            <Alert severity="info">
              Selecteer jaar en maand en klik op "Laad Rapportage" om de maandelijkse rapportage te bekijken.
            </Alert>
          )}
        </TabPanel>

        {/* Z-Report Tab */}
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Selecteer datum"
              type="date"
              value={zReportDate ? format(zReportDate, 'yyyy-MM-dd') : ''}
              onChange={(e) => setZReportDate(e.target.value ? new Date(e.target.value) : null)}
              InputLabelProps={{ shrink: true }}
              sx={{ mr: 2, width: 200 }}
            />
            <Button
              variant="contained"
              onClick={loadZReport}
              disabled={loading || !zReportDate}
              sx={{ background: '#e52525' }}
            >
              Genereer Z-Rapport
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : zReport ? (
            <Box>
              <Paper sx={{ p: 3, mb: 3, background: '#fff5f5' }}>
                <Typography variant="h6" gutterBottom sx={{ color: '#d32f2f', fontWeight: 700 }}>
                  Z-RAPPORT - DAGAFSLUITING
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Datum: {format(parseISO(zReport.date), 'dd MMM yyyy')}
                </Typography>
                <Typography variant="h5" sx={{ color: '#e52525', fontWeight: 700, mt: 2 }}>
                  Totaal Omzet: €{zReport.total_revenue.toFixed(2)}
                </Typography>
                <Typography variant="body1" sx={{ mt: 1 }}>
                  Aantal Bestellingen: {zReport.total_orders}
                </Typography>
                <Typography variant="body1">
                  Gemiddelde Bestelling: €{zReport.average_order_value.toFixed(2)}
                </Typography>
              </Paper>

              {zReport.hourly_breakdown && zReport.hourly_breakdown.length > 0 && (
                <TableContainer component={Paper} sx={{ mb: 3 }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ background: '#fff5f5' }}>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Uur</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Bestellingen</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Omzet</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {zReport.hourly_breakdown.map((stat: any) => (
                        <TableRow key={stat.hour}>
                          <TableCell>{stat.hour}:00</TableCell>
                          <TableCell align="right">{stat.orders}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                            €{stat.revenue.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {zReport.courier_breakdown && zReport.courier_breakdown.length > 0 && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ background: '#fff5f5' }}>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }}>Koerier ID</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Bestellingen</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#d32f2f' }} align="right">Omzet</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {zReport.courier_breakdown.map((stat: any) => (
                        <TableRow key={stat.koerier_id}>
                          <TableCell>Koerier {stat.koerier_id}</TableCell>
                          <TableCell align="right">{stat.orders}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 600, color: '#e52525' }}>
                            €{stat.revenue.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          ) : (
            <Alert severity="info">
              Selecteer een datum en klik op "Genereer Z-Rapport" om de dagafsluiting te bekijken.
            </Alert>
          )}
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default Reports
