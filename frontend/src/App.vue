<template>
  <div id="app">
    <Navbar />
    <main class="main-content" :class="{ 'with-sidebar': loggedIn }">
      <router-view/>
    </main>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
export default {
  name: 'App',
  components: {
    Navbar
  },
  data () {
    return {
      loggedIn: !!localStorage.getItem('jwt')
    }
  },
  created () {
    window.addEventListener('login', this.handleLogin)
    window.addEventListener('logout', this.handleLogout)
  },
  beforeUnmount () {
    window.removeEventListener('login', this.handleLogin)
    window.removeEventListener('logout', this.handleLogout)
  },
  methods: {
    handleLogin () {
      this.loggedIn = true
    },
    handleLogout () {
      this.loggedIn = false
    }
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  margin-top: 5rem;
  margin-left: 0;
  padding: 0;
  min-height: calc(100vh - 5rem);
  box-sizing: border-box;
}

.main-content.with-sidebar {
  margin-left: 190px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
