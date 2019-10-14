<template>
  <div id="app" class="container-fluid">
    <h1>Postman toolkit</h1>
    <div class="row">
      <div class="col-10 offset-1">
        <navigation></navigation>
      </div>
    </div>

    <div class="row">
      <div class="col-10 offset-1">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
  import Navigation from '@/components/Navigation';

  export default {
    name: 'App',
    components: {
      Navigation
    }
  }
</script>

<style>
  #app {

  }
</style>
