import Vue from 'vue';
import Router from 'vue-router';
import BootstrapVue from 'bootstrap-vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css'


import Home from '@/components/Home';
import Profiles from '@/components/Profiles';


Vue.use(Router);
Vue.use(BootstrapVue);

export default new Router({
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
    }
  ]
})
