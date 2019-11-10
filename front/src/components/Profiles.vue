<template>
  <div class="row">

    <div class="col-5">
      <p>Available profiles:</p>

      <i>Most important</i>
      <transition-group class="list-group" tag="ul" name="profile-list">
        <li class="list-group-item" v-for="(profile, index) in profiles.slice().reverse()"
            :key="profile.name" @click="selectedProfile = profile" :class="{'active': selectedProfile === profile}">

          {{profile.name}}
          <span style="float: right">
            <!--suppress JSUnresolvedVariable -->
            <i class="fas fa-caret-square-up size-medium cursor-pointer"
               @click="moveUp(profile, $event)" :class="{'disabled': index === 0}"></i>
            <!--suppress JSUnresolvedVariable -->
            <i class="fas fa-caret-square-down size-medium cursor-pointer"
               @click="moveDown(profile, $event)" :class="{'disabled': index + 1 === profiles.length}"></i>
         </span>

        </li>
      </transition-group>
      <i>Least important</i>
    </div>

    <div class="col-7">
      <ProfileConfig v-if="selectedProfile" :profile-name="selectedProfile.name"></ProfileConfig>
    </div>

  </div>
</template>

<script>
  import Vue from 'vue';
  import api from './../services/api.service';
  import ProfileConfig from './ProfileConfig';

  // noinspection JSUnusedGlobalSymbols
  export default {
    name: 'Profiles',
    components: {ProfileConfig},
    data() {
      return {
        profiles: [],
        selectedProfile: null
      }
    },

    mounted() {
      this.loadProfiles();
    },

    methods: {
      loadProfiles() {
        const that = this;
        api.getProfiles().then(function (profiles) {
          that.profiles = profiles;
        });
      },

      // Make profile more important
      moveUp(profile, event) {
        event.stopPropagation();

        const index = this.profiles.indexOf(profile);
        if (index > -1 && index + 1 < this.profiles.length && this.profiles.length > 1) {
          const tmp = this.profiles[index];
          Vue.set(this.profiles, index, this.profiles[index + 1]);
          Vue.set(this.profiles, index + 1, tmp);
          api.moveProfileUp(tmp.name);
        }
      },

      // Make profile less important
      moveDown(profile, event) {
        event.stopPropagation();

        const index = this.profiles.indexOf(profile);
        if (index > -1 && index > 0 && this.profiles.length > 1) {
          const tmp = this.profiles[index];
          Vue.set(this.profiles, index, this.profiles[index - 1]);
          Vue.set(this.profiles, index - 1, tmp);
          api.moveProfileDown(tmp.name);
        }
      }
    }
  }
</script>

<!--suppress CssUnusedSymbol -->
<style scoped>
  .profile-list-move {
    transition: transform 0.5s;
  }

  .list-group-item {
    /* breaks profile swap animation */
    /*transition: background-color 0.1s linear;*/
  }

  .list-group-item i.disabled {
    cursor: not-allowed;
    color: lightgray;
  }

  .list-group-item:not(.active) {
    cursor: pointer;
  }
</style>
