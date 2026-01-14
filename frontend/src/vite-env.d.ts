/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_ADMIN_LDAP_IDS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
