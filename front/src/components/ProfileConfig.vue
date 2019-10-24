<template>
  <div>
    <p>Properties of profile {{profileName}}</p>
    <div v-if="properties">
      <ConfigProperty v-for="property in properties" :key="property.name" :property="property"/>
    </div>
  </div>
</template>

<script>
  import api from '../services/api.service';
  import ConfigProperty from './ConfigProperty';

  export default {
    name: 'ProfileConfig',
    components: {ConfigProperty},
    props: ['profileName'],
    data() {
      return {
        properties: null
      }
    },
    methods: {
      refreshProfile() {
        this.properties = [];
        api.getProfileProperties(this.profileName).then((properties) => {
          this.properties = properties;
        });
      }
    },
    watch: {
      profileName: function () {
        this.refreshProfile();
      }
    }
  }
</script>

<style scoped>

</style>
