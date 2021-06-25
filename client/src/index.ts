import app from './vue/index.vue';

// extension Vue
import Vue from 'vue';
import Axios from 'axios';
// $api
Vue.prototype.$api = Axios.create({
  baseURL: '/api/v1/',
});

// render
new Vue({
  el: '#app',
  render: h => h(app),
});
