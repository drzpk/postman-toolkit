<!--suppress HtmlFormInputWithoutLabel -->
<template>
  <div>
    <div class="form-group row">
      <span class="chevron-container" @click="toggleExpanded()">
        <i class="fas fa-chevron-right" :class="{'expanded': expanded}"></i>
      </span>
      <label v-if="!expanded" :for="inputName" class="col-3 col-form-label">{{property.name}}</label>
      <label v-if="expanded" class="col-8 col-form-label">{{expandedProperties[0].name}} - property hierarchy</label>
      <div v-if="!expanded" class="col-8">
        <input type="text" class="form-control" :id="inputName" :value="property.value">
      </div>
    </div>

    <div v-if="expanded">
      <div class="form-group row" v-for="(property, i) in expandedProperties" :key="i">
        <label :for="inputName" class="col-3 col-form-label">
          {{property.profile}}
          <i v-show="!property.active" class="fas fa-eye-slash" v-b-tooltip.hover="" title="this profile is inactive"></i>
        </label>
        <div class="col-8">
          <input type="text" class="form-control" :id="inputName" :value="property.value">
        </div>
      </div>
    </div>
  </div>

</template>

<script>
  import api from '../services/api.service';

  export default {
    name: 'ExtendedConfigProperty',
    props: ['property'],
    data() {
      return {
        inputName: '',
        expanded: false,
        expandedProperties: null
      };
    },
    mounted() {
      this.inputName = 'config-property' + Math.floor(Math.random() * 100000).toString();
    },
    methods: {
      toggleExpanded() {
        if (this.expanded) {
          this.expanded = false;
          return;
        }

        api.getPropertyDetails(this.property.name).then((property) => {
          this.expanded = true;
          property.ancestors.splice(0, 0, {
            name: property.name,
            value: property.value,
            profile: property.profile,
            active: property.active
          });
          this.expandedProperties = property.ancestors;
        });
      }
    }
  }
</script>

<!--suppress CssUnusedSymbol -->
<style scoped>
  .chevron-container {
    margin-top: 0.4em;
    cursor: pointer;
  }

  .chevron-container i {
    transition: transform 0.5s;
  }

  .chevron-container i.expanded {
    transform: rotate(90deg);
  }

  i.fa-eye-slash {
    font-size: 0.8em;
  }
</style>
