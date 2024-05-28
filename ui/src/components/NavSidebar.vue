<template>
  <div class="nav-sidebar">
    <div class="sidebar-header">
      <img src="http://localhost:5000/static/logo.png" alt="Sidebar Image" class="sidebar-image">
      <h1 class="sidebar-title">Syncify</h1>
    </div>
    <ul class="nav flex-column">
      <li class="nav-item" v-for="link in links" :key="link.name">
        <a class="nav-link" :class="{ active: link.active }" href="#" @click.prevent="navigate(link.name)">
          <i :class="link.icon"></i> {{ link.name }}
        </a>
      </li>
    </ul>
    <div class="playlist-section">
      <h2 class="playlist-title"></h2>
      <ul class="playlist-list">
        <li class="playlist-item" v-for="(playlist, index) in localPlaylists" :key="playlist.name">
          <div class="playlist-controls">
            <input
              v-if="editingIndex === index"
              :value="playlist.name"
              @input="debouncedUpdatePlaylistName($event.target.value, index)"
              @blur="stopEditing(index)"
              @keyup.enter="stopEditing(index)"
              class="playlist-input"
            />
            <a
              v-else
              class="playlist-link"
              @click="loadPlaylist(playlist)"
              href="#"
            >
              {{ playlist.name }}
            </a>
            <button @click="startEditing(index)" class="edit-button">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="deletePlaylist(index)" class="delete-button">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    playlists: Array
  },
  data() {
    return {
      links: [
        { name: "All", href: "#", icon: "fas fa-list", active: true },
        { name: "Artists", href: "#", icon: "fas fa-user", active: false },
        { name: "Albums", href: "#", icon: "fas fa-record-vinyl", active: false },
        { name: "Directory", href: "#", icon: "fas fa-folder", active: false }
      ],
      editingIndex: null,
      localPlaylists: [...this.playlists],
      updateTimeout: null
    };
  },
  methods: {
    navigate(view) {
      this.links.forEach(link => {
        link.active = (link.name === view);
      });
      this.$emit('navigate', view);
    },
    loadPlaylist(playlist) {
      console.log("Loading playlist", playlist);
      this.$emit('loadPlaylist', playlist);
    },
    startEditing(index) {
      this.editingIndex = index;
    },
    stopEditing() {
      if (this.updateTimeout) {
        clearTimeout(this.updateTimeout);
        this.updateTimeout = null;
      }
      this.editingIndex = null;
      this.updatePlaylists();
    },
    deletePlaylist(index) {
      this.localPlaylists.splice(index, 1);
      this.updatePlaylists();
    },
    updatePlaylists() {
      this.$emit('update:playlists', this.localPlaylists);
      this.savePlaylists();
    },
    savePlaylists() {
      localStorage.setItem('playlists', JSON.stringify(this.localPlaylists));
    },
    debouncedUpdatePlaylistName(newName, index) {
      if (this.updateTimeout) {
        clearTimeout(this.updateTimeout);
      }
      this.updateTimeout = setTimeout(() => {
        this.localPlaylists[index].name = newName;
        this.updatePlaylists();
      }, 1000);
    }
  },
  watch: {
    playlists: {
      handler(newPlaylists) {
        this.localPlaylists = [...newPlaylists];
      },
      deep: true
    }
  },
  mounted() {
    if (localStorage.getItem('playlists')) {
      this.localPlaylists = JSON.parse(localStorage.getItem('playlists'));
      this.$emit('update:playlists', this.localPlaylists);
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
}

a:link {
  text-decoration: none;
}
a:visited {
  text-decoration: none;
}
a:hover {
  text-decoration: none;
}
a:active {
  text-decoration: none;
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

.divider {
  border: 1px solid #B3B3B3;
  width: 80%;
  margin: 20px auto;
}

.playlist-section {
  padding: 0 20px;
}

.playlist-title {
  color: #fff;
  font-size: 1.1em;
  margin-bottom: 10px;
  border-bottom: 1px solid #1DB954;
  padding-bottom: 5px;
}

.playlist-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.playlist-item {
  padding: 8px 0;
}

.playlist-controls {
  display: flex;
  align-items: center;
}

.playlist-input {
  flex-grow: 1;
  padding: 5px;
  margin-right: 5px;
  border: 1px solid #B3B3B3;
  border-radius: 5px;
  background-color: #333;
  color: #B3B3B3;
}

.playlist-link {
  color: #B3B3B3;
  text-decoration: none;
  display: block;
  padding: 8px 10px;
  border-radius: 5px;
  flex-grow: 1;
}

.playlist-link:hover {
  color: #fff;
  background-color: #333;
}

.edit-button, .delete-button {
  background: none;
  border: none;
  color: #B3B3B3;
  cursor: pointer;
  margin-left: 5px;
}

.edit-button:hover, .delete-button:hover {
  color: #fff;
}
</style>
