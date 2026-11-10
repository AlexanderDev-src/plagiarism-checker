// @ts-check
import { defineConfig } from 'astro/config';

import svelte from '@astrojs/svelte';

// https://astro.build/config
export default defineConfig({
  integrations: [svelte()],
  // dev only: forward API calls to Flask (`uv run plagiarism-checker`, port 5000)
  vite: { server: { proxy: { '/api': 'http://127.0.0.1:5000' } } },
});
