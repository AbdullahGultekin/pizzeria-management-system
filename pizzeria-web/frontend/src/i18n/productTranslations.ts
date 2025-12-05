/**
 * Product and category translations
 * Maps Dutch category/product names to French and English
 */

import { Language } from './translations'

export const categoryTranslations: Record<string, Record<Language, string>> = {
  'Pizza': {
    nl: 'Pizza',
    fr: 'Pizza',
    en: 'Pizza',
  },
  'Pasta': {
    nl: 'Pasta',
    fr: 'Pâtes',
    en: 'Pasta',
  },
  'Dranken': {
    nl: 'Dranken',
    fr: 'Boissons',
    en: 'Drinks',
  },
  'Desserts': {
    nl: 'Desserts',
    fr: 'Desserts',
    en: 'Desserts',
  },
  'Voorgerechten': {
    nl: 'Voorgerechten',
    fr: 'Entrées',
    en: 'Starters',
  },
  'Salades': {
    nl: 'Salades',
    fr: 'Salades',
    en: 'Salads',
  },
  'Kebab': {
    nl: 'Kebab',
    fr: 'Kebab',
    en: 'Kebab',
  },
  'Wraps': {
    nl: 'Wraps',
    fr: 'Wraps',
    en: 'Wraps',
  },
  'Burgers': {
    nl: 'Burgers',
    fr: 'Burgers',
    en: 'Burgers',
  },
  'Bijgerechten': {
    nl: 'Bijgerechten',
    fr: 'Accompagnements',
    en: 'Sides',
  },
}

/**
 * Translate a category name
 */
export const translateCategory = (categoryName: string, language: Language): string => {
  const translation = categoryTranslations[categoryName]
  if (translation) {
    return translation[language]
  }
  // If no translation found, return original
  return categoryName
}

/**
 * Product name translations
 * Common product names that appear frequently
 */
export const productTranslations: Record<string, Record<Language, string>> = {
  // Common words
  'Kleine': {
    nl: 'Kleine',
    fr: 'Petite',
    en: 'Small',
  },
  'Grote': {
    nl: 'Grote',
    fr: 'Grande',
    en: 'Large',
  },
  'Medium': {
    nl: 'Medium',
    fr: 'Moyenne',
    en: 'Medium',
  },
  'Met': {
    nl: 'Met',
    fr: 'Avec',
    en: 'With',
  },
  'Zonder': {
    nl: 'Zonder',
    fr: 'Sans',
    en: 'Without',
  },
  'Extra': {
    nl: 'Extra',
    fr: 'Extra',
    en: 'Extra',
  },
}

/**
 * Translate a product name
 * This is a simple approach - for more complex translations,
 * you might want to use a more sophisticated system
 */
export const translateProduct = (productName: string, language: Language): string => {
  // If already in target language, return as is
  if (language === 'nl') {
    return productName
  }
  
  // Try to find exact match
  const exactMatch = productTranslations[productName]
  if (exactMatch) {
    return exactMatch[language]
  }
  
  // Try partial translations for common words
  let translated = productName
  
  // Replace common Dutch words
  const commonWords: Record<string, Record<Language, string>> = {
    'Kleine': { nl: 'Kleine', fr: 'Petite', en: 'Small' },
    'Grote': { nl: 'Grote', fr: 'Grande', en: 'Large' },
    'Medium': { nl: 'Medium', fr: 'Moyenne', en: 'Medium' },
    'Met': { nl: 'Met', fr: 'Avec', en: 'With' },
    'Zonder': { nl: 'Zonder', fr: 'Sans', en: 'Without' },
  }
  
  for (const [dutch, translations] of Object.entries(commonWords)) {
    const regex = new RegExp(`\\b${dutch}\\b`, 'gi')
    translated = translated.replace(regex, translations[language])
  }
  
  // If no translation found, return original
  // In a real application, you might want to store product translations in the database
  return translated
}


