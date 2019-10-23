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
  // TODO: settings page: adding prefix to each property imported to Postman
  // TODO: settings page: updating properties changed in Postman
  import Navigation from '@/components/Navigation';

  export default {
    name: 'App',
    components: {
      Navigation
    }
  }
</script>

<!--suppress CssUnusedSymbol -->
<style>
  @import "../node_modules/@fortawesome/fontawesome-free/css/all.css";
  #app {

  }

  .size-medium {
    font-size: 1.3em;
  }

  .cursor-pointer {
    cursor: pointer;
  }
</style>
