/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string
    readonly VITE_RAZORPAY_KEY_ID: string
    readonly VITE_TRANSLATE_URL: string
    readonly MODE: string
    readonly DEV: boolean
    // more env variables...
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
