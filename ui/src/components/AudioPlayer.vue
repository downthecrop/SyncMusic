<template>
  <div class="audio-player-container">
    <div class="audio-player">
      <div class="audio-info">
        <img :src="albumCover" alt="Album Cover" class="cover">
        <div class="track-info">
          <span class="track-title">{{ metadata.title }}</span>
          <span class="track-artist">{{ metadata.artist }}</span>
        </div>
      </div>
      <div class="audio-controls">
        <div class="control-buttons">
          <button @click="previousTrack" class="control-btn">
            <i class="fas fa-backward"></i>
          </button>
          <button @click="toggleShuffle" class="control-btn">
            <i :class="{'fas fa-random': isShuffle, 'fas fa-backward': !isShuffle}"></i>
          </button>
          <button @click="togglePlay" class="control-btn">
            <i :class="{'fas fa-pause': isPlaying, 'fas fa-play': !isPlaying}"></i>
          </button>
          <button @click="toggleRepeat" class="control-btn">
            <i :class="{'fas fa-redo': isRepeat, 'fas fa-forward': !isRepeat}"></i>
          </button>
          <button @click="nextTrack" class="control-btn">
            <i class="fas fa-forward"></i>
          </button>
        </div>
        <div class="audio-progress">
          <span class="time">{{ currentTime }}</span>
          <input type="range" v-model="seek" @input="seekAudio" class="seek-bar">
          <span class="time">{{ duration }}</span>
        </div>
      </div>
      <div class="volume-control">
        <input type="range" v-model="volume" @input="changeVolume" class="volume-bar">
      </div>
    </div>
    <audio ref="audioPlayer" :src="audioSrc" @timeupdate="updateTime" @loadedmetadata="updateDuration" @loadeddata="onLoadedData" @play="onPlay" @ended="onEnded" @error="handleError">
      Your browser does not support the audio element.
    </audio>
  </div>
</template>

<script>
import '@fortawesome/fontawesome-free/css/all.css';

export default {
  props: ['audioSrc', 'metadata'],
  data() {
    return {
      albumCover: "https://pbs.twimg.com/media/FPx0VtLX0AcOSK3.jpg:large",
      isPlaying: false,
      isShuffle: false,
      isRepeat: false,
      seek: 0,
      currentTime: "0:00",
      duration: "2:07",
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
        audio.load();
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
    toggleShuffle() {
      this.isShuffle = !this.isShuffle;
    },
    toggleRepeat() {
      this.isRepeat = !this.isRepeat;
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
    },
    onEnded() {
      this.$emit('ended');
    },
    nextTrack() {
      this.$emit('next');
    },
    previousTrack() {
      this.$emit('previous');
    }
  }
};
</script>

<style>
.audio-player-container {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #181818;
  color: #fff;
}

.audio-player {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
}

.audio-info {
  display: flex;
  align-items: center;
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

.track-artist {
  color: #b3b3b3;
}

.audio-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.control-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 5px;
}

.control-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  margin: 0 10px;
}

.audio-progress {
  display: flex;
  align-items: center;
  width: 80%;
}

.seek-bar {
  -webkit-appearance: none;
  appearance: none;
  height: 5px;
  background: #535353;
  cursor: pointer;
  flex: 1;
  margin: 0 10px;
}

.seek-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 10px;
  height: 10px;
  background: #1db954;
  border-radius: 50%;
}

.volume-control {
  display: flex;
  align-items: center;
}

.volume-bar {
  -webkit-appearance: none;
  appearance: none;
  height: 5px;
  background: #535353;
  cursor: pointer;
  width: 80px;
}

.volume-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 10px;
  height: 10px;
  background: #1db954;
  border-radius: 50%;
}

.time {
  color: #b3b3b3;
  margin: 0 10px;
}

audio {
  display: none;
}
</style>
