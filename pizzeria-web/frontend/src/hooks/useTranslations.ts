/**
 * Hook to get translation functions for categories and products
 */
import { useLanguage } from '../contexts/LanguageContext'
import { translateCategory, translateProduct } from '../i18n/productTranslations'
import { Language } from '../i18n/translations'

export const useTranslations = () => {
  const { language, t } = useLanguage()
  
  return {
    t,
    language,
    translateCategory: (category: string) => translateCategory(category, language),
    translateProduct: (product: string) => translateProduct(product, language),
  }
}


