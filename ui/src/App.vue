<template>
  <div id="app">
    <div class="spacer"></div>
    <notifications position="top right" />
    <NavSidebar @navigate="navigate" @loadPlaylist="loadPlaylist" :playlists="playlists" @update:playlists="updatePlaylists"/>
    <div class="container" style="margin-left: 270px;">
      <nav aria-label="breadcrumb" v-if="navigationHistory.length" class="d-flex align-items-center">
        <button v-if="navigationHistory.length > 1" @click="goBack" class="btn btn-link mr-2 back-button">
          <i class="fas fa-arrow-left"></i>
        </button>
        <ol class="breadcrumb mb-0">
          <li class="breadcrumb-item" v-for="(item, index) in navigationHistory" :key="index">
            <a href="#" @click.prevent="navigateToBreadcrumb(index)">{{ item.view }}{{ item.name ? ': ' + item.name : '' }}</a>
          </li>
        </ol>
      </nav>
      <div class="spacer"></div>
      <ul id="nav-list" class="list-group">
        <li v-for="(item) in displayItems" :key="item.name"
          class="list-group-item border-0 d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <a href="#" @click.prevent="handleNavigation(item)" class="nav-link d-inline-flex align-items-center">
              <i :class="getIconClass(currentView, item.isDirectory)" class="mr-2"></i>
              <span class="truncate" :title="item.name" :data-tooltip="item.name">{{ item.name }}</span>
            </a>
            <br>
            <small v-if="isSongView" class="ml-2">{{ item.path }}</small>
          </div>
          <button v-if="isSongView" @click="addToPlaylist(item)" class="btn btn-add">
            <i class="fas fa-plus"></i>
          </button>
          <button v-if="isAlbumView" @click="addAlbumToPlaylist(item.name)" class="btn btn-add">
            <i class="fas fa-plus"></i>
          </button>
        </li>
      </ul>
    </div>
    <AudioPlayer ref="audioPlayer" :audioSrc="audioSrc" :metadata="metadata" @ended="handleSongEnded"
      @next="handleNextTrack" @previous="handlePreviousTrack" />
    <PlaylistUI ref="playlistUI" :playSong="playSong" :nextSong="nextSong" :previousSong="previousSong" @playlist-action="handlePlaylistAction"/>
  </div>
</template>

<script>
import NavSidebar from "./components/NavSidebar.vue";
import AudioPlayer from "./components/AudioPlayer.vue";
import PlaylistUI, { addSongToPlaylist } from './components/PlaylistUI.vue';
import io from "socket.io-client";

export default {
  components: {
    NavSidebar,
    AudioPlayer,
    PlaylistUI,
  },
  data() {
    return {
      songs: [],
      currentView: 'songs', // albums, songs, all, artists, directory
      displayItems: [],
      playlists: [],
      navigationHistory: [],
      socket: null,
      audioSrc: "",
      metadata: {
        title: "Unknown Title",
        artist: "Unknown Artist",
        album: "Unknown Album",
        year: "Unknown Year"
      },
      currentPlaylist: [],
      currentIndex: -1 // Index to keep track of current playing song in the playlist
    };
  },
  computed: {
    isSongView() {
      return this.currentView === 'songs' || this.currentView === 'all';
    },
    isAlbumView() {
      return this.currentView === 'albums';
    }
  },
  methods: {
    async fetchSongs() {
      try {
        const response = await fetch("http://localhost:5000/songs");
        const data = await response.json();
        this.songs = data.songs.map((song, index) => {
          const pathParts = song.path.split('/');
          const name = song.name.replace(/(\.m4a|\.mp3|\.flac)+$/i, ''); // Remove .m4a, .mp3, .flac extensions, including combinations like .flac.mp3
          return {
            ...song,
            name,
            artist: pathParts[pathParts.length - 2] || "Unknown Artist",
            album: pathParts[pathParts.length - 1] || "Unknown Album",
            path: song.path,
            index: index
          };
        });
        this.displayAllSongs();
      } catch (error) {
        console.error("Error fetching songs:", error);
      }
    },
    handlePlaylistAction(event) {
      if (event.action === 'save') {
        console.log("Saving playlist", event)
        this.playlists.push({name: event.name, playlist: event.playlist});
      }
    },
    buildDirectoryStructure() {
      const root = {};
      this.songs.forEach(song => {
        const parts = song.path.split('/');
        let current = root;
        parts.forEach((part, index) => {
          if (!current[part]) {
            current[part] = {
              name: part,
              path: parts.slice(0, index + 1).join('/'),
              isDirectory: true,
              children: {}
            };
          }
          current = current[part].children;
        });
      });
      return root;
    },
    traverseDirectory(directory, path = '') {
      if (!directory) return [];
      const items = Object.values(directory);
      if (path) {
        this.updateNavigationHistory({ view: 'Directory', name: path });
      }
      return items;
    },
    displayDirectory(path = '') {
      this.currentView = 'directory';
      const directoryStructure = this.buildDirectoryStructure();
      let current = directoryStructure;
      if (path) {
        const parts = path.split('/');
        parts.forEach(part => {
          if (current[part]) {
            current = current[part].children;
          }
        });
      }
      this.displayItems = this.traverseDirectory(current, path);
    },
    playSong(index) {
      const songTitle = this.songs[index].name
      this.$notify("Attempting to play song: " + songTitle);
      this.socket.emit("play_song", { index: index });
    },
    handlePlaySong(data) {
      this.audioSrc = `http://localhost:5000/stream?url=${encodeURIComponent(data.url)}`;
      this.fetchMetadata(this.audioSrc);
    },
    async fetchMetadata(url) {
      try {
        const response = await fetch(url, { method: "HEAD" });
        this.metadata.title = response.headers.get("X-Metadata-Title") || "Unknown Title";
        this.metadata.artist = response.headers.get("X-Metadata-Artist") || "Unknown Artist";
        this.metadata.album = response.headers.get("X-Metadata-Album") || "Unknown Album";
        this.metadata.year = response.headers.get("X-Metadata-Year") || "Unknown Year";
      } catch (error) {
        console.error("Error fetching metadata:", error);
      }
    },
    displayAlbums() {
      this.currentView = 'albums';
      const albums = [...new Set(this.songs.map(song => song.album))];
      this.displayItems = albums.map(album => ({ name: album }));
      this.updateNavigationHistory({ view: 'Albums' });
    },
    displaySongs(album) {
      this.currentView = 'songs';
      this.displayItems = this.songs.filter(song => song.album === album);
      this.updateNavigationHistory({ view: 'Songs', name: album });
    },
    displayAllSongs() {
      this.currentView = 'all';
      this.displayItems = this.songs.map((song, index) => ({ ...song, index }));
      this.updateNavigationHistory({ view: 'All Songs' });
    },
    displayArtists() {
      this.currentView = 'artists';
      const artists = [...new Set(this.songs.map(song => song.artist))];
      this.displayItems = artists.map(artist => ({ name: artist }));
      this.updateNavigationHistory({ view: 'Artists' });
    },
    displayArtistAlbums(artist) {
      this.currentView = 'albums';
      const albums = [...new Set(this.songs.filter(song => song.artist === artist).map(song => song.album))];
      this.displayItems = albums.map(album => ({ name: album }));
      this.updateNavigationHistory({ view: 'Albums', name: artist });
    },
    handleNavigation(item) {
      if (item.isDirectory) {
        const directoryStructure = this.buildDirectoryStructure();
            const parts = item.path.split('/');
            let current = directoryStructure;

            parts.forEach(part => {
                if (current[part]) {
                    current = current[part].children;
                }
            });

            if (Object.keys(current).length === 0) {
                // If no children, it's the deepest directory
                this.displaySongs(item.name);
            } else {
                // If there are children, continue displaying directories
                this.displayDirectory(item.path);
            }
      } else if (this.currentView === 'albums') {
        this.displaySongs(item.name);
      } else if (this.currentView === 'songs' || this.currentView === 'all') {
        this.playSong(item.index);
      } else if (this.currentView === 'artists') {
        this.displayArtistAlbums(item.name);
      }
    },
    goBack() {
      if (this.navigationHistory.length > 1) {
        this.navigationHistory.pop();
        const previousState = this.navigationHistory[this.navigationHistory.length - 1];
        this.restoreView(previousState.view, previousState.name);
      }
    },
    updatePlaylists(newPlaylists) {
      this.playlists = newPlaylists;
    },
    restoreView(view, name) {
      switch (view) {
        case 'All Songs':
          this.displayAllSongs();
          break;
        case 'Artists':
          this.displayArtists();
          break;
        case 'Albums':
          name ? this.displayArtistAlbums(name) : this.displayAlbums();
          break;
        case 'Songs':
          if (name) {
            this.currentView = 'songs';
            this.displayItems = this.songs.filter(song => song.album === name);
          }
          break;
        case 'Directory':
          this.displayDirectory(name);
          break;
      }
    },
    navigate(view) {
      this.navigationHistory = [];
      if (view === 'All') {
        this.displayAllSongs();
      } else if (view === 'Artists') {
        this.displayArtists();
      } else if (view === 'Albums') {
        this.displayAlbums();
      } else if (view === 'Directory') {
        this.displayDirectory();
      }
    },
    navigateToBreadcrumb(index) {
      this.navigationHistory = this.navigationHistory.slice(0, index + 1);
      const previousState = this.navigationHistory[index];
      this.restoreView(previousState.view, previousState.name);
    },
    updateNavigationHistory(state) {
      if (this.navigationHistory.length === 0 || this.navigationHistory[this.navigationHistory.length - 1].view !== state.view || this.navigationHistory[this.navigationHistory.length - 1].name !== state.name) {
        this.navigationHistory.push(state);
      }
    },
    getIconClass(view, isDirectory) {
      if (isDirectory) {
        return 'fas fa-folder';
      }
      switch (view) {
        case 'albums':
          return 'fas fa-folder';
        case 'artists':
          return 'fas fa-microphone';
        case 'songs':
        case 'all':
          return 'fas fa-music';
        default:
          return 'fas fa-music';
      }
    },
    addToPlaylist(item) {
      addSongToPlaylist({ name: item.name, index: item.index });
    },
    addAlbumToPlaylist(albumName) {
      const songs = this.songs.filter(song => song.album === albumName);
      songs.forEach(song => addSongToPlaylist({ name: song.name, index: song.index }));
    },
    songEnded() {
      this.$refs.playlistUI.playNextSong();
    },
    handleSongEnded() {
      console.log("Song is over...")
      this.songEnded();
    },
    loadPlaylist(event){
      this.$refs.playlistUI.playlist = event.playlist;
      this.$refs.playlistUI.isOpen = true;
    },
    handleNextTrack() {
      console.log("Trying to play next...")
      this.$refs.playlistUI.playNextSong();
    },
    handlePreviousTrack() {
      console.log("Trying to play previous...")
      this.$refs.playlistUI.playPreviousSong();
    },
    nextSong() {
      this.handleNextTrack();
    },
    previousSong() {
      this.handlePreviousTrack();
    }
  },
  mounted() {
    this.socket = io.connect('http://localhost:5000');
    this.socket.on('connect', () => {
      console.log('Connected to server');
    });
    this.socket.on('play_song', this.handlePlaySong);
    this.fetchSongs();
  }
};
</script>

<style>
@import url('https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #121212;
  color: #B3B3B3;
}

.container {
  margin: initial;
  width: initial;
  max-width: initial;
}

@media (min-width: 1200px) {
  .container {
    margin: initial;
    width: initial;
    max-width: initial;
  }
}

@media (min-width: 992px) {
  .container {
    margin: initial;
    width: initial;
    max-width: initial;
  }
}

@media (min-width: 768px) {
  .container {
    margin: initial;
    width: initial;
    max-width: initial;
  }
}

@media (min-width: 576px) {
  .container {
    margin: initial;
    width: initial;
    max-width: initial;
  }
}

.spacer {
  margin: 10px;
}

h1 {
  color: #fff;
}

small {
  color: #fff;
}

a:hover {
  color:#000 !important;
}

#nav-list {
  overflow-y: auto;
  margin-bottom: 150px;
}

.list-group-item {
  background-color: #282828;
  color: #B3B3B3;
  border: none;
}

.list-group-item:hover {
  background-color: #1DB954;
  color: #fff;
}

.border-top {
  border-top: 1px solid #444;
}

.breadcrumb {
  background-color: #282828;
  color: #B3B3B3;
}

.breadcrumb-item a {
  color: #1DB954;
}

.breadcrumb-item a:hover {
  color: #fff;
}

.truncate {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 400px;
  display: inline-block;
  vertical-align: middle;
}

/* TOOLTIP */
/* [data-tooltip]{position:absolute;} */
[data-tooltip]:before,
[data-tooltip]:after {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  white-space: nowrap;
  transition: all .2s ease;
  font-size: 11px;
  font-family: dotum;
  letter-spacing: -1px;
}

.btn {
  color:#55ad74 !important;
}

[data-tooltip]:before {
  content: attr(data-tooltip);
  height: 13px;
  position: absolute;
  padding: 5px 1 1 5px;
  border-radius: 2px;
  color: #fff;
  background: #025272;
  box-shadow: 0 3px 8px rgba(165, 165, 165, 0.5);
}

[data-tooltip]:not([data-tooltip=""]):hover:before {
  visibility: visible;
  opacity: 1;
}

[data-tooltip]:not([data-tooltip=""]):hover:after {
  visibility: visible;
  opacity: 1;
  top: -8px;
}

.btn-link {
  color: #1DB954;
}

.btn-link:hover {
  color: #fff;
}
</style>
