import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Alert,
  Divider,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HomeIcon from '@mui/icons-material/Home'
import TrackChangesIcon from '@mui/icons-material/TrackChanges'
import { brandColors } from '../theme/colors'
import PublicHeader from '../components/PublicHeader'
import { useTranslations } from '../hooks/useTranslations'

const OrderConfirmationPage = () => {
  const navigate = useNavigate()
  const { t } = useTranslations()
  const [searchParams] = useSearchParams()
  const [bonnummer, setBonnummer] = useState<string | null>(null)

  useEffect(() => {
    const bonnummerParam = searchParams.get('bonnummer')
    if (bonnummerParam) {
      setBonnummer(bonnummerParam)
    } else {
      // If no bonnummer, redirect to home
      navigate('/')
    }
  }, [searchParams, navigate])

  if (!bonnummer) {
    return null // Will redirect in useEffect
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f0', display: 'flex', flexDirection: 'column' }}>
      <PublicHeader />
      
      <Container maxWidth="md" sx={{ py: 6, flex: 1, display: 'flex', alignItems: 'center' }}>
        <Paper
          elevation={3}
          sx={{
            p: 5,
            textAlign: 'center',
            borderRadius: '17px',
            width: '100%',
            boxShadow: '0 3px 20px -6px rgba(180, 68, 68, 0.3)',
          }}
        >
          <CheckCircleIcon 
            sx={{ 
              fontSize: 80, 
              color: '#4caf50', 
              mb: 3,
              animation: 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': {
                  transform: 'scale(1)',
                },
                '50%': {
                  transform: 'scale(1.05)',
                },
              },
            }} 
          />
          
          <Typography 
            variant="h3" 
            sx={{ 
              color: brandColors.primary, 
              fontWeight: 700, 
              mb: 2,
              fontSize: { xs: '2rem', sm: '2.5rem' },
            }}
          >
            {t.orderPlaced}!
          </Typography>
          
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#666', 
              mb: 4,
              fontSize: { xs: '1rem', sm: '1.25rem' },
            }}
          >
            {t.thankYou}
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Box sx={{ mb: 4 }}>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#666', 
                mb: 2,
                fontSize: '1.1rem',
              }}
            >
              {t.orderNumber}:
            </Typography>
            <Typography 
              variant="h2" 
              sx={{ 
                color: brandColors.primary, 
                fontWeight: 800,
                fontSize: { xs: '2.5rem', sm: '3.5rem' },
                mb: 1,
                letterSpacing: '0.1em',
              }}
            >
              {bonnummer}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#999', 
                fontStyle: 'italic',
              }}
            >
              {t.saveOrderNumber}
            </Typography>
          </Box>

          <Alert 
            severity="info" 
            sx={{ 
              mb: 4, 
              borderRadius: '10px',
              textAlign: 'left',
              '& .MuiAlert-message': {
                width: '100%',
              },
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              {t.whatHappensNext}
            </Typography>
            <Typography variant="body2" component="div">
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>{t.orderReceived}</li>
                <li>{t.confirmationEmail}</li>
                <li>{t.trackWithNumber}</li>
                <li>{t.weWillCall}</li>
              </ul>
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap', mt: 4 }}>
            <Button
              variant="contained"
              startIcon={<TrackChangesIcon />}
              onClick={() => navigate(`/track?bonnummer=${bonnummer}`)}
              sx={{
                bgcolor: brandColors.primary,
                '&:hover': { bgcolor: brandColors.primaryDark },
                textTransform: 'none',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                fontSize: '1rem',
              }}
            >
              {t.trackOrder}
            </Button>
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              onClick={() => navigate('/')}
              sx={{
                borderColor: brandColors.primary,
                color: brandColors.primary,
                textTransform: 'none',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                fontSize: '1rem',
                '&:hover': {
                  borderColor: brandColors.primaryDark,
                  bgcolor: '#fff5f5',
                },
              }}
            >
              {t.back} {t.menu}
            </Button>
          </Box>

          <Typography 
            variant="body2" 
            sx={{ 
              color: '#999', 
              mt: 4,
              fontStyle: 'italic',
            }}
          >
            {t.haveQuestions} {t.callUs} 03 775 72 28 {t.sendEmail} info@pitapizzanapoli.be
          </Typography>
        </Paper>
      </Container>
    </Box>
  )
}

export default OrderConfirmationPage


