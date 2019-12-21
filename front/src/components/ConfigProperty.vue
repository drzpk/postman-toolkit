<!--suppress HtmlFormInputWithoutLabel -->
<template>
  <div class="form-group row">
    <label :for="inputName" class="col-4 col-form-label">{{property.name}}</label>
    <div class="col-8">
      <div class="row">

        <div class="col-11">
          <input type="text" class="form-control" :id="inputName" v-model="property.value" @blur="updateValue()">
        </div>
        <div class="col-1">
          <b-dropdown size="lg"  variant="link" toggle-class="text-decoration-none" no-caret style="margin-top: -0.3em;">
            <!--suppress HtmlUnknownBooleanAttribute, XmlUnboundNsPrefix -->
            <template v-slot:button-content>
              <i class="fas fa-ellipsis-v"></i>
            </template>
            <b-dropdown-item href="#">Rename</b-dropdown-item>
            <b-dropdown-item href="#">Delete</b-dropdown-item>
          </b-dropdown>
        </div>

      </div>
    </div>
  </div>
</template>

<!--suppress JSPrimitiveTypeWrapperUsage -->
<script>
  import api from '../services/api.service';

  export default {
    name: 'ConfigProperty',
    props: ['property'],
    data() {
      return {
        inputName: ''
      };
    },
    mounted() {
      this.inputName = 'config-property' + Math.floor(Math.random() * 100000).toString();
      this.property.oldValue = this.property.value;
    },
    methods: {
      updateValue() {
        if (this.property.oldValue !== this.property.value) {
          api.setProfileProperty(this.property.profile, this.property.name, this.property.value);
          this.property.oldValue = this.property.value;
        }
      }
    }
  }
</script>

<style scoped>

</style>
