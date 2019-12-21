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

    <div id="notification-container">
      <Notifications></Notifications>
    </div>
  </div>
</template>

<script>
  // TODO: settings page: adding prefix to each property imported to Postman
  // TODO: settings page: updating properties changed in Postman
  import Navigation from '@/components/Navigation';
  import Notifications from '@/components/Notifications';

  export default {
    name: 'App',
    components: {
      Navigation,
      Notifications
    }
  }
</script>

<!--suppress CssUnusedSymbol -->
<style lang="scss">
  @import "../node_modules/@fortawesome/fontawesome-free/css/all.css";
  @import "styles/common.scss";
  #app {

  }

  #notification-container {
    position: absolute;
    width: 24%;
    min-width: 21em;
    right: 0;
    top: 100px;
    margin-right: 2em;
  }

  .size-medium {
    font-size: 1.3em;
  }

  .cursor-pointer {
    cursor: pointer;
  }
</style>
