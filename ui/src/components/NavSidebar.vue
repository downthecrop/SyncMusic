<template>
  <div class="nav-sidebar">
    <div class="sidebar-header">
      <img src="https://i.imgur.com/fCgGhAP.png" alt="Sidebar Image" class="sidebar-image">
      <h1 class="sidebar-title">Syncify</h1>
    </div>
    <ul class="nav flex-column">
      <li class="nav-item" v-for="link in links" :key="link.name">
        <a class="nav-link" :class="{ active: link.active }" href="#" @click.prevent="navigate(link.name)">
          <i :class="link.icon"></i> {{ link.name }}
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      links: [
        { name: "All", href: "#", icon: "fas fa-list", active: true },
        { name: "Artists", href: "#", icon: "fas fa-user", active: false },
        { name: "Albums", href: "#", icon: "fas fa-record-vinyl", active: false },
        { name: "Directory", href: "#", icon: "fas fa-folder", active: false }
      ],
    };
  },
  methods: {
    navigate(view) {
      this.links.forEach(link => {
        link.active = (link.name === view);
      });
      this.$emit('navigate', view);
    }
  }
};
</script>

<style>
.nav-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 250px;
  height: 100%;
  background-color: #000;
  padding-top: 20px;
  color: #B3B3B3;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 20px;
}

.sidebar-image {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

.sidebar-title {
  color: #fff;
  font-size: 1.2em;
}

.nav-sidebar .nav-item {
  padding: 10px 20px;
}

.nav-sidebar .nav-item:hover {
  background-color: #1DB954;
  color: #fff;
}

.nav-link {
  color: inherit;
  text-decoration: none;
}

.nav-link .fas {
  margin-right: 8px;
}

.nav-link.active {
  color: #1DB954;
}
</style>
