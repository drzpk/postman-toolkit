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
