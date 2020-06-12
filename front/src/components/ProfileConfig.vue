<template>
  <div>
    <p>Properties of profile {{profileName}}</p>
    <div v-if="properties">
      <ConfigProperty v-for="property in properties" :key="property.name" :property="property"/>
    </div>
    <div class="add-property">
      <b-button id="popover-target" variant="outline-primary" @click="showNewPropertyDialog = !showNewPropertyDialog">
        <i class="fas fa-plus"></i> Add property
      </b-button>
      <b-popover target="popover-target" triggers="manual" placement="bottom"
                 :show.sync="showNewPropertyDialog">
        <!--suppress XmlUnboundNsPrefix -->
        <template v-slot:title>Add new property</template>
        <!--suppress HtmlFormInputWithoutLabel -->
        <input type="text" class="form-control" placeholder="Property name" v-model="newPropertyName"/>
        <br/>
        <b-button @click="addProperty()">OK</b-button>
      </b-popover>
    </div>
  </div>
</template>

<script>
  import api from '../services/api.service';
  import notificationService from '../services/notification.service';
  import ConfigProperty from './ConfigProperty';

  export default {
    name: 'ProfileConfig',
    components: {ConfigProperty},
    props: ['profileId', 'profileName'],
    data() {
      return {
        properties: null,
        showNewPropertyDialog: false,
        newPropertyName: ''
      }
    },
    methods: {
      refreshProfile() {
        this.properties = [];
        api.getProfileProperties(this.profileId).then((properties) => {
          this.properties = properties;
        });
      },

      addProperty() {
        if (!this.newPropertyName.trim().length) {
          notificationService.emitError('Property name cannot be empty');
          return;
        }

        const that = this;
        api.addProfileProperty(this.profileId, this.newPropertyName, '').then(function () {
          that.refreshProfile();
          that.showNewPropertyDialog = false;
          notificationService.emitInfo(`Property ${that.newPropertyName} has been created`);
        }).catch(function () {
          notificationService.emitError(`Error while creating property ${that.newPropertyName}`);
        });
      }
    },
    watch: {
      profileId: function () {
        this.refreshProfile();
        this.showNewPropertyDialog = false;
        this.newPropertyName = '';
      }
    }
  }
</script>

<style scoped>
  .add-property {
    margin-top: 2.1em;
    float: right;
  }
</style>
