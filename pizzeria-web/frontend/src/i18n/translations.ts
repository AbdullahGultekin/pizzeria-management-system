/**
 * Translation strings for the application
 */

export type Language = 'nl' | 'fr' | 'en'

export interface Translations {
  // Header
  menu: string
  cart: string
  trackOrder: string
  contact: string
  login: string
  register: string
  logout: string
  myAccount: string
  
  // Opening hours
  open: string
  closed: string
  today: string
  tomorrow: string
  openingHours: string
  opensAt: string
  closesAt: string
  
  // Common
  loading: string
  error: string
  success: string
  cancel: string
  save: string
  delete: string
  edit: string
  add: string
  remove: string
  confirm: string
  back: string
  next: string
  submit: string
  
  // Auth
  email: string
  password: string
  forgotPassword: string
  resetPassword: string
  newPassword: string
  confirmPassword: string
  loginTitle: string
  registerTitle: string
  alreadyHaveAccount: string
  noAccount: string
  
  // Password requirements
  passwordRequirements: string
  passwordMinLength: string
  passwordUppercase: string
  passwordLowercase: string
  passwordNumber: string
  passwordSpecial: string
  
  // Checkout
  checkout: string
  deliveryAddress: string
  paymentMethod: string
  orderSummary: string
  total: string
  placeOrder: string
  
  // Order
  orderConfirmation: string
  orderNumber: string
  orderStatus: string
  orderDate: string
  orderTime: string
  
  // Contact
  contactUs: string
  address: string
  phone: string
  emailContact: string
  
  // Language
  language: string
  dutch: string
  french: string
  english: string
  
  // Cart
  cartEmpty: string
  cartTotal: string
  quantity: string
  price: string
  removeFromCart: string
  clearCart: string
    proceedToCheckout: string
    emptyCartMessage: string
    continueShopping: string
  
  // Menu
  allCategories: string
  addToCart: string
  unavailable: string
  description: string
  
  // Checkout
  customerInfo: string
  name: string
  phone: string
  street: string
  houseNumber: string
  postcode: string
  city: string
  deliveryType: string
  delivery: string
  pickup: string
  deliveryTime: string
  pickupTime: string
  notes: string
  cash: string
  card: string
  online: string
  submitting: string
  
  // Order Tracking
  trackYourOrder: string
  enterOrderNumber: string
  enterPhoneNumber: string
  track: string
  orderNotFound: string
  
  // Contact
    sendMessage: string
    message: string
    yourName: string
    yourEmail: string
    yourPhone: string
    messageSent: string
    contactFormTitle: string
    contactFormDescription: string
    nameRequired: string
    emailRequired: string
    invalidEmail: string
    messageRequired: string
    planRoute: string
    allRightsReserved: string
  openingHours: string
  monday: string
  tuesday: string
  wednesday: string
  thursday: string
  friday: string
  saturday: string
  sunday: string
  
  // Order Confirmation
  thankYou: string
  orderPlaced: string
  orderDetails: string
  items: string
  youCanTrack: string
  
  // Common messages
  required: string
  optional: string
    confirmDelete: string
    yes: string
    no: string
    
    // Checkout specific
    tip: string
    loginRegisterTip: string
    dataSaved: string
    clearSavedData: string
    loggedInAs: string
    saveOrderNumber: string
    whatHappensNext: string
    orderReceived: string
    confirmationEmail: string
    trackWithNumber: string
    weWillCall: string
    haveQuestions: string
    callUs: string
    sendEmail: string
    orderPlacedBy: string
    comment: string
    noAccountNeeded: string
    haveAccount: string
    logInToSee: string
    helperTextOrderNumber: string
    helperTextPhoneRequired: string
    searching: string
    searchOrder: string
    orderNotFound: string
    checkOrderNumber: string
    paymentMethodNotSpecified: string
    expectedDeliveryTime: string
    minutes: string
    cardDetails: string
    paymentSecure: string
    stripeInfo: string
    meat: string
    sideDish: string
    sauces: string
    sauce1: string
    sauce2: string
    extra: string
    halfHalf: string
    remark: string
}

export const translations: Record<Language, Translations> = {
  nl: {
    // Header
    menu: 'Menu',
    cart: 'Winkelwagen',
    trackOrder: 'Bestelling Volgen',
    contact: 'Contactpagina',
    login: 'Inloggen',
    register: 'Registreren',
    logout: 'Uitloggen',
    myAccount: 'Mijn Account',
    
    // Opening hours
    open: 'Open',
    closed: 'Gesloten',
    today: 'Vandaag',
    tomorrow: 'Morgen',
    openingHours: 'Openingstijden',
    opensAt: 'Opent om',
    closesAt: 'Sluit om',
    
    // Common
    loading: 'Laden...',
    error: 'Fout',
    success: 'Succes',
    cancel: 'Annuleren',
    save: 'Opslaan',
    delete: 'Verwijderen',
    edit: 'Bewerken',
    add: 'Toevoegen',
    remove: 'Verwijderen',
    confirm: 'Bevestigen',
    back: 'Terug',
    next: 'Volgende',
    submit: 'Verzenden',
    
    // Auth
    email: 'E-mailadres',
    password: 'Wachtwoord',
    forgotPassword: 'Wachtwoord vergeten?',
    resetPassword: 'Wachtwoord resetten',
    newPassword: 'Nieuw wachtwoord',
    confirmPassword: 'Wachtwoord bevestigen',
    loginTitle: 'Inloggen',
    registerTitle: 'Registreren',
    alreadyHaveAccount: 'Heb je al een account?',
    noAccount: 'Nog geen account?',
    
    // Password requirements
    passwordRequirements: 'Wachtwoord vereisten:',
    passwordMinLength: 'Minimaal 8 tekens',
    passwordUppercase: 'Minimaal één hoofdletter',
    passwordLowercase: 'Minimaal één kleine letter',
    passwordNumber: 'Minimaal één cijfer',
    passwordSpecial: 'Minimaal één speciaal teken (!@#$%^&*()_+-=[]{}|;:,.<>?)',
    
    // Checkout
    checkout: 'Afrekenen',
    deliveryAddress: 'Bezorggegevens',
    paymentMethod: 'Betaalmethode',
    orderSummary: 'Bestellingsoverzicht',
    total: 'Totaal',
    placeOrder: 'Bestelling plaatsen',
    
    // Order
    orderConfirmation: 'Bestelling Bevestigd',
    orderNumber: 'Bestelnummer',
    orderStatus: 'Status',
    orderDate: 'Datum',
    orderTime: 'Tijd',
    
    // Contact
    contactUs: 'Contact',
    address: 'Adres',
    phone: 'Telefoon',
    emailContact: 'E-mail',
    
    // Language
    language: 'Taal',
    dutch: 'Nederlands',
    french: 'Français',
    english: 'English',
    
    // Cart
    cartEmpty: 'Je winkelwagen is leeg',
    cartTotal: 'Totaal',
    quantity: 'Aantal',
    price: 'Prijs',
    removeFromCart: 'Verwijderen',
    clearCart: 'Winkelwagen legen',
    proceedToCheckout: 'Naar afrekenen',
    emptyCartMessage: 'Voeg producten toe aan je winkelwagen om verder te gaan',
    continueShopping: 'Verder winkelen',
    
    // Menu
    allCategories: 'Alle categorieën',
    addToCart: 'Toevoegen',
    unavailable: 'Niet beschikbaar',
    description: 'Beschrijving',
    
    // Checkout
    customerInfo: 'Klantgegevens',
    name: 'Naam',
    street: 'Straat',
    houseNumber: 'Huisnummer',
    postcode: 'Postcode',
    city: 'Gemeente',
    deliveryType: 'Type bestelling',
    delivery: 'Bezorgen',
    pickup: 'Afhalen',
    deliveryTime: 'Levertijd',
    pickupTime: 'Afhaaltijd',
    notes: 'Opmerkingen',
    cash: 'Contant',
    card: 'Kaart',
    online: 'Online betalen',
    submitting: 'Plaatsen...',
    
    // Order Tracking
    trackYourOrder: 'Volg je bestelling',
    enterOrderNumber: 'Voer bestelnummer in',
    enterPhoneNumber: 'Voer telefoonnummer in',
    track: 'Volgen',
    orderNotFound: 'Bestelling niet gevonden',
    
    // Contact
    sendMessage: 'Verzenden',
    message: 'Bericht',
    yourName: 'Je naam',
    yourEmail: 'Je e-mail',
    yourPhone: 'Je telefoon',
    messageSent: 'Bericht verzonden!',
    contactFormTitle: 'Stuur ons een bericht',
    contactFormDescription: 'Heb je vragen, opmerkingen of wil je direct bestellen? Neem contact met ons op!',
    nameRequired: 'Naam is verplicht',
    emailRequired: 'E-mail is verplicht',
    invalidEmail: 'Ongeldig e-mailadres',
    messageRequired: 'Bericht is verplicht',
    planRoute: 'Route plannen met Google Maps',
    allRightsReserved: 'Alle rechten voorbehouden',
    monday: 'Maandag',
    tuesday: 'Dinsdag',
    wednesday: 'Woensdag',
    thursday: 'Donderdag',
    friday: 'Vrijdag',
    saturday: 'Zaterdag',
    sunday: 'Zondag',
    
    // Order Confirmation
    thankYou: 'Bedankt voor je bestelling!',
    orderPlaced: 'Je bestelling is geplaatst',
    orderDetails: 'Bestelgegevens',
    items: 'Items',
    youCanTrack: 'Je kunt je bestelling volgen met je bestelnummer en telefoonnummer',
    
    // Common messages
    required: 'Verplicht',
    optional: 'Optioneel',
    confirmDelete: 'Weet je zeker dat je dit wilt verwijderen?',
    yes: 'Ja',
    no: 'Nee',
    
    // Checkout specific
    tip: 'Tip:',
    loginRegisterTip: 'Log in of registreer je om je gegevens automatisch in te vullen bij volgende bestellingen.',
    dataSaved: 'Je gegevens zijn opgeslagen en worden automatisch ingevuld',
    clearSavedData: 'Opgeslagen gegevens wissen',
    loggedInAs: 'Ingelogd als',
    saveOrderNumber: 'Bewaar dit nummer om je bestelling te volgen',
    whatHappensNext: 'Wat gebeurt er nu?',
    orderReceived: 'Je bestelling is ontvangen en wordt verwerkt',
    confirmationEmail: 'Je ontvangt een bevestiging per e-mail (indien opgegeven)',
    trackWithNumber: 'Je kunt je bestelling volgen met je bonnummer en telefoonnummer',
    weWillCall: 'We bellen je als er vragen zijn over je bestelling',
    haveQuestions: 'Heb je vragen?',
    callUs: 'Bel ons op',
    sendEmail: 'of stuur een e-mail naar',
    orderPlacedBy: 'Besteld door:',
    comment: 'Opmerking',
    noAccountNeeded: 'Geen account nodig om je bestelling te volgen',
    haveAccount: 'Heb je een account?',
    logInToSee: 'Log in om al je bestellingen te zien',
    helperTextOrderNumber: 'Het bonnummer dat je hebt ontvangen bij je bestelling',
    helperTextPhoneRequired: 'Verplicht om je bestelling te volgen (beveiliging)',
    searching: 'Zoeken...',
    searchOrder: 'Bestelling Zoeken',
    checkOrderNumber: 'Controleer het bonnummer en telefoonnummer',
    paymentMethodNotSpecified: 'Niet gespecificeerd',
    expectedDeliveryTime: 'Verwachte levertijd',
    minutes: 'minuten',
    cardDetails: 'Kaartgegevens',
    paymentSecure: 'Betalingen worden veilig verwerkt via Stripe. Wij slaan geen kaartgegevens op.',
    stripeInfo: 'Stripe',
    meat: 'Vlees',
    sideDish: 'Bijgerecht',
    sauces: 'Sauzen',
    sauce1: 'Saus 1',
    sauce2: 'Saus 2',
    extra: 'Extra',
    halfHalf: 'Half-half',
    remark: 'Opmerking',
  },
  fr: {
    // Header
    menu: 'Menu',
    cart: 'Panier',
    trackOrder: 'Suivre Commande',
    contact: 'Contact',
    login: 'Connexion',
    register: 'S\'inscrire',
    logout: 'Déconnexion',
    myAccount: 'Mon Compte',
    
    // Opening hours
    open: 'Ouvert',
    closed: 'Fermé',
    today: 'Aujourd\'hui',
    tomorrow: 'Demain',
    openingHours: 'Heures d\'ouverture',
    opensAt: 'Ouvre à',
    closesAt: 'Ferme à',
    
    // Common
    loading: 'Chargement...',
    error: 'Erreur',
    success: 'Succès',
    cancel: 'Annuler',
    save: 'Enregistrer',
    delete: 'Supprimer',
    edit: 'Modifier',
    add: 'Ajouter',
    remove: 'Retirer',
    confirm: 'Confirmer',
    back: 'Retour',
    next: 'Suivant',
    submit: 'Envoyer',
    
    // Auth
    email: 'Adresse e-mail',
    password: 'Mot de passe',
    forgotPassword: 'Mot de passe oublié?',
    resetPassword: 'Réinitialiser le mot de passe',
    newPassword: 'Nouveau mot de passe',
    confirmPassword: 'Confirmer le mot de passe',
    loginTitle: 'Connexion',
    registerTitle: 'S\'inscrire',
    alreadyHaveAccount: 'Vous avez déjà un compte?',
    noAccount: 'Pas encore de compte?',
    
    // Password requirements
    passwordRequirements: 'Exigences du mot de passe:',
    passwordMinLength: 'Minimum 8 caractères',
    passwordUppercase: 'Au moins une majuscule',
    passwordLowercase: 'Au moins une minuscule',
    passwordNumber: 'Au moins un chiffre',
    passwordSpecial: 'Au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)',
    
    // Checkout
    checkout: 'Commander',
    deliveryAddress: 'Adresse de livraison',
    paymentMethod: 'Méthode de paiement',
    orderSummary: 'Résumé de la commande',
    total: 'Total',
    placeOrder: 'Passer la commande',
    
    // Order
    orderConfirmation: 'Commande Confirmée',
    orderNumber: 'Numéro de commande',
    orderStatus: 'Statut',
    orderDate: 'Date',
    orderTime: 'Heure',
    
    // Contact
    contactUs: 'Contact',
    address: 'Adresse',
    phone: 'Téléphone',
    emailContact: 'E-mail',
    
    // Language
    language: 'Langue',
    dutch: 'Néerlandais',
    french: 'Français',
    english: 'Anglais',
    
    // Cart
    cartEmpty: 'Votre panier est vide',
    cartTotal: 'Total',
    quantity: 'Quantité',
    price: 'Prix',
    removeFromCart: 'Retirer',
    clearCart: 'Vider le panier',
    proceedToCheckout: 'Passer à la commande',
    emptyCartMessage: 'Ajoutez des produits à votre panier pour continuer',
    continueShopping: 'Continuer les achats',
    
    // Menu
    allCategories: 'Toutes les catégories',
    addToCart: 'Ajouter',
    unavailable: 'Indisponible',
    description: 'Description',
    
    // Checkout
    customerInfo: 'Informations client',
    name: 'Nom',
    street: 'Rue',
    houseNumber: 'Numéro',
    postcode: 'Code postal',
    city: 'Ville',
    deliveryType: 'Type de commande',
    delivery: 'Livraison',
    pickup: 'À emporter',
    deliveryTime: 'Heure de livraison',
    pickupTime: 'Heure de retrait',
    notes: 'Remarques',
    cash: 'Espèces',
    card: 'Carte',
    online: 'Paiement en ligne',
    submitting: 'Envoi...',
    
    // Order Tracking
    trackYourOrder: 'Suivre votre commande',
    enterOrderNumber: 'Entrez le numéro de commande',
    enterPhoneNumber: 'Entrez le numéro de téléphone',
    track: 'Suivre',
    orderNotFound: 'Commande non trouvée',
    
    // Contact
    sendMessage: 'Envoyer',
    message: 'Message',
    yourName: 'Votre nom',
    yourEmail: 'Votre e-mail',
    yourPhone: 'Votre téléphone',
    messageSent: 'Message envoyé!',
    contactFormTitle: 'Envoyez-nous un message',
    contactFormDescription: 'Avez-vous des questions, des commentaires ou souhaitez-vous commander directement? Contactez-nous!',
    nameRequired: 'Le nom est obligatoire',
    emailRequired: 'L\'e-mail est obligatoire',
    invalidEmail: 'Adresse e-mail invalide',
    messageRequired: 'Le message est obligatoire',
    planRoute: 'Planifier un itinéraire avec Google Maps',
    allRightsReserved: 'Tous droits réservés',
    monday: 'Lundi',
    tuesday: 'Mardi',
    wednesday: 'Mercredi',
    thursday: 'Jeudi',
    friday: 'Vendredi',
    saturday: 'Samedi',
    sunday: 'Dimanche',
    
    // Order Confirmation
    thankYou: 'Merci pour votre commande!',
    orderPlaced: 'Votre commande a été passée',
    orderDetails: 'Détails de la commande',
    items: 'Articles',
    youCanTrack: 'Vous pouvez suivre votre commande avec votre numéro de commande et votre numéro de téléphone',
    
    // Common messages
    required: 'Requis',
    optional: 'Optionnel',
    confirmDelete: 'Êtes-vous sûr de vouloir supprimer cela?',
    yes: 'Oui',
    no: 'Non',
    
    // Checkout specific
    tip: 'Astuce:',
    loginRegisterTip: 'Connectez-vous ou inscrivez-vous pour remplir automatiquement vos données lors des prochaines commandes.',
    dataSaved: 'Vos données sont enregistrées et seront remplies automatiquement',
    clearSavedData: 'Effacer les données enregistrées',
    loggedInAs: 'Connecté en tant que',
    saveOrderNumber: 'Conservez ce numéro pour suivre votre commande',
    whatHappensNext: 'Que se passe-t-il maintenant?',
    orderReceived: 'Votre commande a été reçue et est en cours de traitement',
    confirmationEmail: 'Vous recevrez une confirmation par e-mail (si fourni)',
    trackWithNumber: 'Vous pouvez suivre votre commande avec votre numéro de commande et votre numéro de téléphone',
    weWillCall: 'Nous vous appellerons s\'il y a des questions sur votre commande',
    haveQuestions: 'Avez-vous des questions?',
    callUs: 'Appelez-nous au',
    sendEmail: 'ou envoyez un e-mail à',
    orderPlacedBy: 'Commandé par:',
    comment: 'Remarque',
    noAccountNeeded: 'Aucun compte nécessaire pour suivre votre commande',
    haveAccount: 'Vous avez un compte?',
    logInToSee: 'Connectez-vous pour voir toutes vos commandes',
    helperTextOrderNumber: 'Le numéro de commande que vous avez reçu avec votre commande',
    helperTextPhoneRequired: 'Obligatoire pour suivre votre commande (sécurité)',
    searching: 'Recherche...',
    searchOrder: 'Rechercher la commande',
    checkOrderNumber: 'Vérifiez le numéro de commande et le numéro de téléphone',
    paymentMethodNotSpecified: 'Non spécifié',
    expectedDeliveryTime: 'Temps de livraison estimé',
    minutes: 'minutes',
    cardDetails: 'Détails de la carte',
    paymentSecure: 'Les paiements sont traités en toute sécurité via Stripe. Nous ne stockons pas les détails de la carte.',
    stripeInfo: 'Stripe',
    meat: 'Viande',
    sideDish: 'Accompagnement',
    sauces: 'Sauces',
    sauce1: 'Sauce 1',
    sauce2: 'Sauce 2',
    extra: 'Extra',
    halfHalf: 'Moitié-moitié',
    remark: 'Remarque',
  },
  en: {
    // Header
    menu: 'Menu',
    cart: 'Cart',
    trackOrder: 'Track Order',
    contact: 'Contact',
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    myAccount: 'My Account',
    
    // Opening hours
    open: 'Open',
    closed: 'Closed',
    today: 'Today',
    tomorrow: 'Tomorrow',
    openingHours: 'Opening Hours',
    opensAt: 'Opens at',
    closesAt: 'Closes at',
    
    // Common
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    remove: 'Remove',
    confirm: 'Confirm',
    back: 'Back',
    next: 'Next',
    submit: 'Submit',
    
    // Auth
    email: 'Email Address',
    password: 'Password',
    forgotPassword: 'Forgot Password?',
    resetPassword: 'Reset Password',
    newPassword: 'New Password',
    confirmPassword: 'Confirm Password',
    loginTitle: 'Login',
    registerTitle: 'Register',
    alreadyHaveAccount: 'Already have an account?',
    noAccount: 'Don\'t have an account?',
    
    // Password requirements
    passwordRequirements: 'Password Requirements:',
    passwordMinLength: 'Minimum 8 characters',
    passwordUppercase: 'At least one uppercase letter',
    passwordLowercase: 'At least one lowercase letter',
    passwordNumber: 'At least one digit',
    passwordSpecial: 'At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)',
    
    // Checkout
    checkout: 'Checkout',
    deliveryAddress: 'Delivery Address',
    paymentMethod: 'Payment Method',
    orderSummary: 'Order Summary',
    total: 'Total',
    placeOrder: 'Place Order',
    
    // Order
    orderConfirmation: 'Order Confirmed',
    orderNumber: 'Order Number',
    orderStatus: 'Status',
    orderDate: 'Date',
    orderTime: 'Time',
    
    // Contact
    contactUs: 'Contact',
    address: 'Address',
    phone: 'Phone',
    emailContact: 'Email',
    
    // Language
    language: 'Language',
    dutch: 'Dutch',
    french: 'French',
    english: 'English',
    
    // Cart
    cartEmpty: 'Your cart is empty',
    cartTotal: 'Total',
    quantity: 'Quantity',
    price: 'Price',
    removeFromCart: 'Remove',
    clearCart: 'Clear cart',
    proceedToCheckout: 'Proceed to checkout',
    emptyCartMessage: 'Add products to your cart to continue',
    continueShopping: 'Continue shopping',
    
    // Menu
    allCategories: 'All categories',
    addToCart: 'Add',
    unavailable: 'Unavailable',
    description: 'Description',
    
    // Checkout
    customerInfo: 'Customer Information',
    name: 'Name',
    street: 'Street',
    houseNumber: 'House number',
    postcode: 'Postcode',
    city: 'City',
    deliveryType: 'Order type',
    delivery: 'Delivery',
    pickup: 'Pickup',
    deliveryTime: 'Delivery time',
    pickupTime: 'Pickup time',
    notes: 'Notes',
    cash: 'Cash',
    card: 'Card',
    online: 'Online payment',
    submitting: 'Submitting...',
    
    // Order Tracking
    trackYourOrder: 'Track your order',
    enterOrderNumber: 'Enter order number',
    enterPhoneNumber: 'Enter phone number',
    track: 'Track',
    orderNotFound: 'Order not found',
    
    // Contact
    sendMessage: 'Send',
    message: 'Message',
    yourName: 'Your name',
    yourEmail: 'Your email',
    yourPhone: 'Your phone',
    messageSent: 'Message sent!',
    contactFormTitle: 'Send us a message',
    contactFormDescription: 'Do you have questions, comments or want to order directly? Contact us!',
    nameRequired: 'Name is required',
    emailRequired: 'Email is required',
    invalidEmail: 'Invalid email address',
    messageRequired: 'Message is required',
    planRoute: 'Plan route with Google Maps',
    allRightsReserved: 'All rights reserved',
    monday: 'Monday',
    tuesday: 'Tuesday',
    wednesday: 'Wednesday',
    thursday: 'Thursday',
    friday: 'Friday',
    saturday: 'Saturday',
    sunday: 'Sunday',
    
    // Order Confirmation
    thankYou: 'Thank you for your order!',
    orderPlaced: 'Your order has been placed',
    orderDetails: 'Order details',
    items: 'Items',
    youCanTrack: 'You can track your order with your order number and phone number',
    
    // Common messages
    required: 'Required',
    optional: 'Optional',
    confirmDelete: 'Are you sure you want to delete this?',
    yes: 'Yes',
    no: 'No',
    
    // Checkout specific
    tip: 'Tip:',
    loginRegisterTip: 'Log in or register to automatically fill in your details for future orders.',
    dataSaved: 'Your data is saved and will be automatically filled in',
    clearSavedData: 'Clear saved data',
    loggedInAs: 'Logged in as',
    saveOrderNumber: 'Save this number to track your order',
    whatHappensNext: 'What happens next?',
    orderReceived: 'Your order has been received and is being processed',
    confirmationEmail: 'You will receive a confirmation by email (if provided)',
    trackWithNumber: 'You can track your order with your order number and phone number',
    weWillCall: 'We will call you if there are questions about your order',
    haveQuestions: 'Do you have questions?',
    callUs: 'Call us at',
    sendEmail: 'or send an email to',
    orderPlacedBy: 'Ordered by:',
    comment: 'Comment',
    noAccountNeeded: 'No account needed to track your order',
    haveAccount: 'Do you have an account?',
    logInToSee: 'Log in to see all your orders',
    helperTextOrderNumber: 'The order number you received with your order',
    helperTextPhoneRequired: 'Required to track your order (security)',
    searching: 'Searching...',
    searchOrder: 'Search Order',
    checkOrderNumber: 'Check the order number and phone number',
    paymentMethodNotSpecified: 'Not specified',
    expectedDeliveryTime: 'Expected delivery time',
    minutes: 'minutes',
    cardDetails: 'Card Details',
    paymentSecure: 'Payments are securely processed via Stripe. We do not store card details.',
    stripeInfo: 'Stripe',
    meat: 'Meat',
    sideDish: 'Side Dish',
    sauces: 'Sauces',
    sauce1: 'Sauce 1',
    sauce2: 'Sauce 2',
    extra: 'Extra',
    halfHalf: 'Half-Half',
    remark: 'Remark',
  },
}

