<script setup lang="ts">
import { RouterView } from 'vue-router'
import Loading from '@/components/common/Loading.vue'
</script>

<template>
  <div id="app">
    <RouterView />
    <Loading />
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  width: 100%;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #333;
  background-color: #f5f7fa;
  overflow-x: hidden;
}

#app {
  height: 100%;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
