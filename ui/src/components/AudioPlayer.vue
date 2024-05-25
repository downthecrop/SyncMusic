<template>
  <div class="audio-player-container">
    <div class="audio-player">
      <div class="audio-info">
        <img :src="albumCover" alt="Album Cover" class="cover">
        <div class="track-info">
          <span class="track-title">{{ metadata.title }}</span>
          <span class="track-artist">{{ metadata.artist }}</span>
          <span class="track-album">{{ metadata.album }}</span>
          <span class="track-year">{{ metadata.year }}</span>
        </div>
      </div>
      <div class="audio-controls">
        <button @click="togglePlay" class="control-btn">{{ isPlaying ? '⏸️' : '▶️' }}</button>
        <input type="range" v-model="seek" @input="seekAudio" max="100">
        <span>{{ currentTime }}</span> / <span>{{ duration }}</span>
        <input type="range" v-model="volume" @input="changeVolume" max="100">
      </div>
    </div>
    <audio ref="audioPlayer" :src="audioSrc" @timeupdate="updateTime" @loadedmetadata="updateDuration" @loadeddata="onLoadedData" @play="onPlay" @error="handleError">
      Your browser does not support the audio element.
    </audio>
  </div>
</template>

<script>
export default {
  props: ['audioSrc', 'metadata'],
  data() {
    return {
      albumCover: "https://pbs.twimg.com/media/FPx0VtLX0AcOSK3.jpg:large",
      isPlaying: false,
      seek: 0,
      currentTime: "0:00",
      duration: "4:25",
      volume: 100,
      isLoaded: false,
    };
  },
  watch: {
    audioSrc(newSrc) {
      if (newSrc) {
        const audio = this.$refs.audioPlayer;
        this.isLoaded = false;
        audio.pause();
        audio.load(); // Ensure the new source is loaded
        console.log("Audio loaded!")
      }
    }
  },
  methods: {
    togglePlay() {
      const audio = this.$refs.audioPlayer;
      if (audio.paused && this.isLoaded) {
        audio.play();
        this.isPlaying = true;
      } else {
        audio.pause();
        this.isPlaying = false;
      }
    },
    onPlay() {
      this.isLoaded = true;
      this.isPlaying = true;
    },
    onLoadedData() {
      this.isLoaded = true;
      this.$refs.audioPlayer.play();
      this.isPlaying = true;
    },
    updateTime() {
      const audio = this.$refs.audioPlayer;
      if (audio) {
        this.currentTime = this.formatTime(audio.currentTime);
        this.seek = (audio.currentTime / audio.duration) * 100;
      }
    },
    updateDuration() {
      const audio = this.$refs.audioPlayer;
      if (audio) {
        this.duration = this.formatTime(audio.duration);
      }
    },
    formatTime(seconds) {
      const min = Math.floor(seconds / 60);
      const sec = Math.floor(seconds % 60);
      return `${min}:${sec < 10 ? "0" : ""}${sec}`;
    },
    seekAudio() {
      const audio = this.$refs.audioPlayer;
      if (audio) {
        audio.currentTime = (this.seek / 100) * audio.duration;
      }
    },
    changeVolume() {
      const audio = this.$refs.audioPlayer;
      if (audio) {
        audio.volume = this.volume / 100;
      }
    },
    handleError(event) {
      console.error("Error loading audio:", event);
      alert("Failed to load audio. Please try a different song.");
    }
  }
};
</script>

<style>
 .audio-player-container {
     position: fixed;
     bottom: 0;
     width: 100%;
     background-color: #282828;
     color: #fff;
 }

 .audio-player {
     display: flex;
     align-items: center;
     padding: 10px;
 }

 .audio-info {
     display: flex;
     align-items: center;
     flex: 1;
 }

 .cover {
     width: 50px;
     height: 50px;
     margin-right: 10px;
 }

 .track-info {
     display: flex;
     flex-direction: column;
 }

 .track-title {
     font-weight: bold;
     color: #fff;
 }

 .track-artist,
 .track-album,
 .track-year {
     color: #B3B3B3;
 }

 .audio-controls {
     display: flex;
     align-items: center;
     flex: 2;
 }

 .control-btn {
     background: none;
     border: none;
     color: #fff;
     font-size: 20px;
     cursor: pointer;
     margin-right: 10px;
 }

 #seek-bar,
 #volume-bar {
     -webkit-appearance: none;
     appearance: none;
     height: 5px;
     background: #444;
     margin: 0 10px;
     cursor: pointer;
 }

 #seek-bar::-webkit-slider-thumb,
 #volume-bar::-webkit-slider-thumb {
     -webkit-appearance: none;
     appearance: none;
     width: 10px;
     height: 10px;
     background: #1DB954;
     border-radius: 50%;
 }

 #audio-player {
     display: none;
 }
</style>
