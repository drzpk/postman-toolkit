import Vue from 'vue';
import Router from 'vue-router';
import {BootstrapVue, AlertPlugin, PopoverPlugin} from 'bootstrap-vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css'


import Home from '@/components/Home';
import Profiles from '@/components/Profiles';
import Properties from '@/components/Properties';


Vue.use(Router);
Vue.use(BootstrapVue);
Vue.use(AlertPlugin);
Vue.use(PopoverPlugin);

export default new Router({
  base: '/app',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/profiles',
      name: 'Profiles',
      component: Profiles
    },
    {
      path: '/properties',
      name: 'Properties',
      component: Properties
    }
  ]
})
