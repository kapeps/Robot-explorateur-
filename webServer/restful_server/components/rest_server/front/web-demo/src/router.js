import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Chart from './views/Chart.vue'
import Light from './views/Light.vue'
import Led from './views/Led.vue'
import Motor from './views/Motor.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/chart',
      name: 'chart',
      component: Chart
    },
    {
      path: '/light',
      name: 'light',
      component: Light
    },
    {
      path: '/led',
      name: 'led',
      component: Led
    },
    {
      path: '/motor',
      name: 'motor',
      component: Motor
    }
  ]
})
