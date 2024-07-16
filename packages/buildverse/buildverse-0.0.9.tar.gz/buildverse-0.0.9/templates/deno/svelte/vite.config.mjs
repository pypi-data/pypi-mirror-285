import { defineConfig } from "npm:vite@latest";
import { svelte } from "npm:@sveltejs/vite-plugin-svelte@latest";
import viteDeno from "https://deno.land/x/vite_deno_plugin/mod.ts";

//import "npm:materialize-css@latest";
import "npm:svelte@latest";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [viteDeno(), svelte()],
});
