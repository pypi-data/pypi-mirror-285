import App from "./src/App.svelte";

const app = new App({
  target: document.getElementById("app") || document.body,
});

export default app;
