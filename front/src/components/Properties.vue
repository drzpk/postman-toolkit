<template>
  <div>
    <h4>List of all available properties</h4>
    <div class="row">
      <div class="col-4">
        <input type="text" class="form-control" :value="propertyFilter" placeholder="filter properties"/>
      </div>
      <div class="col-2">
        <b-dropdown id="dropdown-1" :text="'Sort: ' + sortOrderLabels[sortOrder]">
          <b-dropdown-item v-for="i in sortOrderLabels.length" :key="i">{{sortOrderLabels[i - 1]}}</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="row" v-if="properties">
      <div class="col-8" v-for="property in properties" :key="property.name">
        <ExtendedConfigProperty :property="property"/>
      </div>
    </div>
  </div>
</template>

<!--suppress JSUnusedGlobalSymbols -->
<script>
  import api from '../services/api.service';
  import ExtendedConfigProperty from './ExtendedConfigProperty';

  export default {
    name: 'Properties',
    components: {ExtendedConfigProperty},
    data() {
      return {
        propertyFilter: '',
        sortOrder: 0,
        sortOrderLabels: [
          'default',
          'name a-z',
          'name z-a'
        ],
        properties: null
      };
    },
    mounted() {
      this.loadProperties();
    },
    methods: {
      loadProperties() {
        api.getAllProperties(true).then((properties) => {
          this.properties = properties;
        });
      }
    }
  }
</script>

<style scoped>

</style>
