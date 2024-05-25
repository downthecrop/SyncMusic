<template>
  <div id="app">
    <NavSidebar @navigate="navigate" />
    <div class="container" style="margin-left: 270px;">
      <h1>Music Streamer</h1>
      <button v-if="navigationHistory.length" @click="goBack" class="btn btn-secondary mb-3">Back</button>
      <ul v-if="currentView !== 'all'" id="nav-list" class="list-group">
        <li v-for="item in displayItems" :key="item.name" class="list-group-item">
          <a href="#" @click.prevent="handleNavigation(item)" class="nav-link">{{ item.name }}</a>
        </li>
      </ul>
      <ul v-else id="songs-list" class="list-group">
        <li v-for="song in songs" :key="song.index" class="list-group-item">
          <a href="#" @click.prevent="playSong(song.index)" class="play-song">{{ song.name }}</a>
          <br><small>{{ song.path }}</small>
        </li>
      </ul>
    </div>
    <AudioPlayer ref="audioPlayer" :audioSrc="audioSrc" :metadata="metadata" />
  </div>
</template>

<script>
import NavSidebar from "./components/NavSidebar.vue";
import AudioPlayer from "./components/AudioPlayer.vue";
import io from "socket.io-client";

export default {
  components: {
    NavSidebar,
    AudioPlayer,
  },
  data() {
    return {
      songs: [],
      currentView: 'albums', // albums, songs, all, artists
      currentAlbum: null,
      currentArtist: null,
      displayItems: [],
      navigationHistory: [],
      socket: null,
      audioSrc: "",
      metadata: {
        title: "Unknown Title",
        artist: "Unknown Artist",
        album: "Unknown Album",
        year: "Unknown Year"
      }
    };
  },
  methods: {
    async fetchSongs() {
      try {
        const response = await fetch("http://localhost:5000/songs");
        const data = await response.json();
        this.songs = data.songs.map(song => {
          const pathParts = song.path.split('/');
          return {
            ...song,
            artist: pathParts[pathParts.length - 2] || "Unknown Artist",
            album: pathParts[pathParts.length - 1] || "Unknown Album"
          };
        });
        this.displayAlbums();
      } catch (error) {
        console.error("Error fetching songs:", error);
      }
    },
    playSong(index) {
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
    displayAlbums(saveHistory = true) {
      if (saveHistory) {
        this.navigationHistory.push({
          view: this.currentView,
          album: this.currentAlbum,
          artist: this.currentArtist
        });
      }
      this.currentView = 'albums';
      this.currentAlbum = null;
      this.currentArtist = null;
      const albums = [...new Set(this.songs.map(song => song.album))];
      this.displayItems = albums.map(album => ({ name: album }));
    },
    displaySongs(album, saveHistory = true) {
      if (saveHistory) {
        this.navigationHistory.push({
          view: this.currentView,
          album: this.currentAlbum,
          artist: this.currentArtist
        });
      }
      this.currentView = 'songs';
      this.currentAlbum = album;
      this.displayItems = this.songs.filter(song => song.album === album);
    },
    displayAllSongs() {
      this.currentView = 'all';
      this.displayItems = this.songs;
    },
    displayArtists() {
      this.currentView = 'artists';
      this.currentAlbum = null;
      this.currentArtist = null;
      const artists = [...new Set(this.songs.map(song => song.artist))];
      this.displayItems = artists.map(artist => ({ name: artist }));
    },
    displayArtistAlbums(artist, saveHistory = true) {
      if (saveHistory) {
        this.navigationHistory.push({
          view: this.currentView,
          album: this.currentAlbum,
          artist: this.currentArtist
        });
      }
      this.currentView = 'albums';
      this.currentArtist = artist;
      const albums = [...new Set(this.songs.filter(song => song.artist === artist).map(song => song.album))];
      this.displayItems = albums.map(album => ({ name: album }));
    },
    handleNavigation(item) {
      if (this.currentView === 'albums') {
        this.displaySongs(item.name);
      } else if (this.currentView === 'songs') {
        this.playSong(item.index);
      } else if (this.currentView === 'artists') {
        this.displayArtistAlbums(item.name);
      }
    },
    goBack() {
      const previousState = this.navigationHistory.pop();
      if (previousState) {
        this.currentView = previousState.view;
        this.currentAlbum = previousState.album;
        this.currentArtist = previousState.artist;
        if (this.currentView === 'albums') {
          this.displayAlbums(false);
        } else if (this.currentView === 'songs') {
          this.displaySongs(this.currentAlbum, false);
        } else if (this.currentView === 'artists') {
          this.displayArtists();
        }
      }
    },
    navigate(view) {
      if (view === 'All') {
        this.navigationHistory = [];
        this.displayAllSongs();
      } else if (view === 'Artists') {
        this.navigationHistory = [];
        this.displayArtists();
      } else if (view === 'Albums') {
        this.navigationHistory = [];
        this.displayAlbums();
      }
    },
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

h1 {
  color: #fff;
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
