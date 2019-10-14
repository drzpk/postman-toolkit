<template>
  <div id="navigation">
    <ul>
      <li><router-link to="/">home</router-link></li>
      <li><router-link to="/profiles">profiles</router-link></li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'Navigation',
    data() {
      return {}
    }
  }
</script>

<style scoped>
  #navigation ul {
    list-style-type: none;
  }

  #navigation ul li {
    display: inline-block;
  }
</style>
