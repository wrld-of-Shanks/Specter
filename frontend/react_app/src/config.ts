// Helper to safely get env vars in both Vite and CRA environments
const getEnv = (key: string, viteKey: string): string => {
  // Check if we are in a Vite environment
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return (import.meta.env as any)[viteKey] || '';
  }
  // Fallback to process.env for CRA/Node
  // @ts-ignore
  return process.env[key] || '';
};

// API Configuration
const config = {
  // Use VITE_API_BASE_URL if available, otherwise default to production
  API_BASE_URL: getEnv('REACT_APP_API_URL', 'VITE_API_BASE_URL') || 'https://lawman-9ffr.onrender.com',
  RAZORPAY_KEY_ID: getEnv('REACT_APP_RAZORPAY_KEY_ID', 'VITE_RAZORPAY_KEY_ID') || 'rzp_test_RjAktAstOznCtJ',

  // For translation service (if needed)
  TRANSLATE_API_URL: getEnv('REACT_APP_TRANSLATE_URL', 'VITE_TRANSLATE_URL') || 'http://localhost:8000',

  // Other configs
  APP_NAME: 'SPECTER AI',
  VERSION: '1.0.0',
  ENV: (typeof import.meta !== 'undefined' && import.meta.env) ? import.meta.env.MODE : 'development',
  IS_DEV: (typeof import.meta !== 'undefined' && import.meta.env) ? import.meta.env.DEV : true,
};

// Debug logging
const currentEnv = (typeof import.meta !== 'undefined' && import.meta.env) ? import.meta.env.MODE : 'development';
console.log('Environment:', currentEnv);
console.log('API_BASE_URL:', config.API_BASE_URL);

export default config;
