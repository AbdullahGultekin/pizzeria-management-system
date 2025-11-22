/**
 * Brand colors based on logo
 * Warm, inviting Italian/Pizza restaurant colors
 */
export const brandColors = {
  // Primary colors - Warm orange/amber (pizza colors)
  primary: '#FF6B35',      // Warm orange - main brand color
  primaryDark: '#E65100',   // Dark orange for hover states
  primaryLight: '#FF8C65',  // Light orange for backgrounds
  
  // Secondary colors - Deep blue (from delivery zones)
  secondary: '#1A237E',     // Deep indigo blue
  secondaryDark: '#0D47A1', // Darker blue
  secondaryLight: '#3949AB', // Lighter blue
  
  // Accent colors - Gold/yellow
  accent: '#FFB300',        // Gold/yellow for highlights
  accentDark: '#F57C00',    // Darker gold
  accentLight: '#FFC107',   // Light gold
  
  // Neutral colors
  text: '#212529',          // Dark text
  textSecondary: '#6C757D', // Secondary text
  background: '#FAFAFA',    // Light background
  white: '#FFFFFF',
  border: '#E0E0E0',
  
  // Status colors
  success: '#4CAF50',       // Green
  error: '#F44336',         // Red (keep for errors)
  warning: '#FF9800',        // Orange warning
  info: '#2196F3',          // Blue info
}

// Legacy color mappings for gradual migration
export const legacyColors = {
  red: brandColors.primary,
  redDark: brandColors.primaryDark,
  redLight: brandColors.primaryLight,
}

