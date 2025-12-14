/** @type {import('vite').UserConfig} */
import { defineConfig, loadEnv } from 'vite'
// import { default as vue } from '@vitejs/plugin-vue'
import { default as vuePlugin } from '@vitejs/plugin-vue'

import path from 'path'

// import type { UserConfig as ViteUserConfig } from 'vite'
const viteConfig = { //: ViteUserConfig
  // vite config
  plugins: [vuePlugin()],
  root: ".",
  resolve: {
    alias: [
      // aliases in the form of: { find, replacement, customResolver }
      // this allows an tailwind-import like so:
      // import tailwindConfig from './tailwind.config';
      { find: 'tailwind.config', replacement: path.resolve(__dirname, 'tailwind.config.ts') },
    ],
  },
  optimizeDeps: {
    include: ["tailwind.config.ts"]
  },
  server: {
    host: '0.0.0.0',
    base: "/assets/",
    // port: 3033,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
}

export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  // modes are: development, production, test, depending on how vite is invoked
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  // load envs from .env file
  const env = {...process.env, ...loadEnv(mode, process.cwd(), 'VITE_')}
  if (env.VITE_APP_MODE === 'django') { console.log('VITE_APP_MODE is django')}

  // to differentiate between dev and prod, you can use `command`:
  if (command === 'serve' || command === 'build') {
    const define = {
      define: {
        __APP_ENV__: env.APP_ENV
      }
    }
    const config = Object.assign({}, viteConfig, define)
    return config
  }
  else { return {} }
})
