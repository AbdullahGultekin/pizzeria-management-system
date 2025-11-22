/**
 * Error handling utilities for better user experience
 */

export interface ApiError {
  message: string
  status?: number
  details?: any
}

export const getErrorMessage = (error: any): string => {
  // Network errors
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'De server reageert niet. Probeer het later opnieuw.'
    }
    if (error.message?.includes('Network Error')) {
      return 'Geen verbinding met de server. Controleer uw internetverbinding.'
    }
    return 'Er is een fout opgetreden. Probeer het later opnieuw.'
  }

  // HTTP errors
  const status = error.response?.status
  const data = error.response?.data

  switch (status) {
    case 400:
      return data?.detail || 'Ongeldige gegevens. Controleer uw invoer.'
    case 401:
      return 'U bent niet ingelogd. Log opnieuw in.'
    case 403:
      return 'U heeft geen toegang tot deze functie.'
    case 404:
      return data?.detail || 'Niet gevonden.'
    case 409:
      return data?.detail || 'Conflict. Deze gegevens bestaan al.'
    case 422:
      return data?.detail || 'Validatiefout. Controleer uw gegevens.'
    case 429:
      return 'Te veel verzoeken. Wacht even en probeer het opnieuw.'
    case 500:
      return 'Serverfout. Probeer het later opnieuw.'
    case 503:
      return 'Service tijdelijk niet beschikbaar. Probeer het later opnieuw.'
    default:
      return data?.detail || data?.message || `Fout ${status}: Er is iets misgegaan.`
  }
}

export const formatValidationErrors = (error: any): Record<string, string> => {
  const errors: Record<string, string> = {}
  
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    
    // Handle Pydantic validation errors
    if (Array.isArray(detail)) {
      detail.forEach((err: any) => {
        if (err.loc && err.msg) {
          const field = err.loc[err.loc.length - 1]
          errors[field] = err.msg
        }
      })
    } else if (typeof detail === 'string') {
      errors._general = detail
    }
  }
  
  return errors
}


