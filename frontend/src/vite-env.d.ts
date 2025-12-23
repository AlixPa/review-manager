/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FLAG_DEVELOPMENT_LOGIN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
