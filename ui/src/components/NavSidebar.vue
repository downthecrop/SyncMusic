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
        { name: "Albums", href: "#", icon: "fas fa-record-vinyl" }
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
.nav-sidebar {
  width: 250px;
  position: fixed;
}
.nav-link .fas {
  margin-right: 8px;
}
</style>
