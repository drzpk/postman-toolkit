<template>
  <div id="app">

    <header>
      <h1>Postman toolkit</h1>
      <div>
        <navigation></navigation>
      </div>
    </header>

    <div class="container-fluid">
      <div class="row">
        <div class="col-10 offset-1">
          <router-view></router-view>
        </div>
      </div>

      <div id="notification-container">
        <Notifications></Notifications>
      </div>
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

  html, body {
    margin: 0;
  }

  header {
    padding: 0.8em 2.2em;
    margin-bottom: 3em;
    background-color: #e8e8e8;
    box-shadow: 0 -3px 12px 0px #585b61;

    h1 {
      display: inline-block;
    }
    div {
      display: inline-block;

      a {
        font-size: 1.2em;
        text-transform: capitalize;
        padding: 0 0.5em;
      }
    }
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
