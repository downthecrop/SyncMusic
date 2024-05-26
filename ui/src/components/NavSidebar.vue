<template>
  <div class="nav-sidebar">
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
        { name: "All", href: "#", icon: "fas fa-list" },
        { name: "Artists", href: "#", icon: "fas fa-user" },
        { name: "Albums", href: "#", icon: "fas fa-record-vinyl" },
        { name: "Directory", href: "#", icon: "fas fa-folder" }
      ],
    };
  },
  methods: {
    navigate(view) {
      console.log("navigate", view)
      this.$emit('navigate', view);
    }
  }
};
</script>

<style>
.nav-link .fas {
  margin-right: 8px;
}
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

.nav-sidebar .nav-item {
  padding: 10px 20px;
}

.nav-sidebar .nav-item:hover {
  background-color: #1DB954;
  color: #fff;
}
</style>
