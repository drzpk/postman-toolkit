<!--suppress HtmlFormInputWithoutLabel -->
<template>
  <div class="form-group row">
    <label :for="inputName" class="col-4 col-form-label">{{property.name}}</label>
    <div class="col-8">
      <input type="text" class="form-control" :id="inputName" :value="property.value">
    </div>
  </div>
</template>

<script>
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
    }
  }
</script>

<style scoped>

</style>
