/** @type {import('tailwindcss').Config} */

import type { Config as TailwindConfig } from 'tailwindcss';

const tailwindConfig: TailwindConfig = {
  content: [
    "./index.html",
    "./src/**/*.{html,vue,ts}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default tailwindConfig;
