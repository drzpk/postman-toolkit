<!--suppress HtmlFormInputWithoutLabel -->
<template>
  <div class="form-group row">

    <div id="label-wrapper" class="col-4 col-form-label" v-show="!nameEditor.active">
      <label :for="inputName">{{property.name}}</label>
      <i class="fas fa-pencil-alt" @click="enableEditMode()"></i>
    </div>

    <div id="label-wrapper-edit" class="col-4" v-show="nameEditor.active">
      <input type="text" class="form-control" v-model="nameEditor.value">
      <i class="fas fa-check" @click="disableEditMode(true)"></i>
      <i class="fas fa-times" @click="disableEditMode(false)"></i>
    </div>

    <div class="col-8">
      <div class="row">

        <div class="col-11">
          <input type="text" class="form-control" :id="inputName" v-model="property.value" @blur="updateValue()">
        </div>
        <div class="col-1">
          <b-dropdown size="lg" variant="link" toggle-class="text-decoration-none" no-caret style="margin-top: -0.3em;">
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
        inputName: '',
        nameEditor: {
          active: false,
          value: 'test'
        }
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
      },

      enableEditMode() {
        this.nameEditor.active = true;
        this.nameEditor.value = this.property.name;
      },

      disableEditMode(saveChanges) {
        this.nameEditor.active = false;
        if (saveChanges) {
          api.renameProfileProperty(this.property.profile, this.property.name, this.nameEditor.value);
          this.property.name = this.nameEditor.value;
        }
      }
    }
  }
</script>

<style scoped>
  #label-wrapper {
    position: relative;
    box-sizing: border-box;
  }

  #label-wrapper:hover {
    border: 1px solid gray;
  }

  #label-wrapper > i {
    opacity: 0;
    position: relative;
    top: 0.3em;
    float: right;
    cursor: pointer;
  }

  #label-wrapper:hover > i {
    opacity: 1;
  }

  #label-wrapper > label {
    position: absolute;
  }

  #label-wrapper-edit {
    display: flex;
  }

  #label-wrapper-edit > i {
    font-size: 1.4em;
    position: relative;
    top: 0.3em;
    cursor: pointer;
  }

  #label-wrapper-edit > i:first-of-type {
    margin-left: 0.2em;
    margin-right: 0.3em;
  }

  .fas {
    color: gray;
  }
</style>
