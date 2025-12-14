<template>
  <h1 class="text-3xl font-bold text-cyan-500">Pytomatom</h1>
  <div class="flex justify-center">
    <img class="logo" src="/src/assets/images/sg_cartouche.png" alt="saint-gobain-cartouche">
  </div>
  <WelcomeComponent />

</template>

<script setup lang="ts">
import WelcomeComponent from './components/WelcomeComponent.vue'

</script>

<style scoped>
.logo {
  height: 8em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

</style>
