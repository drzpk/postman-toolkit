<template>
  <div>
    <div class="row">

      <div class="col-5">
        <p>Available profiles:</p>

        <i>Most important</i>
        <transition-group class="list-group" tag="ul" name="profile-list">
          <li class="list-group-item" v-for="(profile, index) in profiles.slice()"
              :key="profile.name" @click="selectedProfile = profile" :class="{'active': selectedProfile === profile}">

            {{profile.name}}
            <span style="float: right">
              <i class="fas fa-eye size-medium cursor-pointer" v-b-tooltip.hover title="Toggle active state"
                 :class="{'fa-eye': profile.active, 'fa-eye-slash': !profile.active}" @click="toggleActiveState(profile, $event)"></i>
              &nbsp;&nbsp;
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
        <ProfileConfig v-if="selectedProfile" :profile-id="selectedProfile.id"
                       :profile-name="selectedProfile.name"></ProfileConfig>
      </div>
    </div>

    <div class="row" style="margin-top: 2em">
      <div class="col-4">
        <div id="add-profile">
          <b-button id="add-profile-button" variant="outline-primary"
                    @click="showNewProfileDialog = !showNewProfileDialog">
            <i class="fas fa-plus"></i> Add profile
          </b-button>
          <b-popover target="add-profile-button" triggers="manual" placement="bottom"
                     :show.sync="showNewProfileDialog">
            <!--suppress XmlUnboundNsPrefix -->
            <template v-slot:title>Add new profile</template>
            <!--suppress HtmlFormInputWithoutLabel -->
            <input type="text" class="form-control" placeholder="Property name" v-model="newProfileName"/>
            <br/>
            <b-button @click="addProfile()">OK</b-button>
          </b-popover>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue';
  import api from './../services/api.service';
  import ProfileConfig from './ProfileConfig';
  import notificationService from '../services/notification.service';

  // noinspection JSUnusedGlobalSymbols
  export default {
    name: 'Profiles',
    components: {ProfileConfig},
    data() {
      return {
        profiles: [],
        selectedProfile: null,
        showNewProfileDialog: false,
        newProfileName: null
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
        if (index > -1 && index > 0 && this.profiles.length > 1) {
          const tmp = this.profiles[index];
          Vue.set(this.profiles, index, this.profiles[index - 1]);
          Vue.set(this.profiles, index - 1, tmp);
          api.moveProfileUp(tmp.id);
        }
      },

      // Make profile less important
      moveDown(profile, event) {
        event.stopPropagation();

        const index = this.profiles.indexOf(profile);
        if (index > -1 && index + 1 < this.profiles.length && this.profiles.length > 1) {
          const tmp = this.profiles[index];
          Vue.set(this.profiles, index, this.profiles[index + 1]);
          Vue.set(this.profiles, index + 1, tmp);
          api.moveProfileDown(tmp.id);
        }
      },

      toggleActiveState(profile, event) {
        event.stopPropagation();
        const method = profile.active ? api.deactivateProfile : api.activateProfile;

        method(profile.id).then(function () {
          profile.active = !profile.active;
        });
      },

      addProfile() {
        if (!this.newProfileName.trim().length) {
          notificationService.emitError('Profile name cannot be empty');
          return;
        }

        const that = this;
        api.addProfile(this.newProfileName, false).then(function () {
          that.loadProfiles();
          notificationService.emitInfo(`Profile ${that.newProfileName} has been created`);
        }).catch(function () {
          notificationService.emitError(`Error while creating profile ${that.newProfileName}`);
        }).then(function () {
          that.showNewProfileDialog = false;
          that.newProfileName = null;
        });
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
