<template>
  <div class="playlist-popup" v-if="isOpen">
    <div class="playlist-header">
      <div class="button-group">
        <button type="button" @click="playPlaylist" class="btn btn-sm btn-play">
          <i class="fas fa-play"></i>
        </button>
        <button type="button" @click="savePlaylist" class="btn btn-sm btn-save">
          <i class="fas fa-save"></i>
        </button>
        <button type="button" @click="shufflePlaylist" class="btn btn-sm btn-shuffle">
          <i class="fas fa-random"></i>
        </button>
        <button type="button" @click="playlist = []" class="btn btn-sm btn-close">
          <i class="fas fa-trash-alt"></i>
        </button>
        <button type="button" @click="isOpen = false" class="btn btn-sm btn-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
    <div class="playlist-body">
      <draggable v-model="playlist" @end="onDragEnd" tag="ul">
        <template #item="{ element, index }">
          <li :key="index" :class="['list-item', { 'current-song': index === currentSongIndex }]">
            <span class="truncate" :title="element.name">{{ element.name }}</span>
            <div class="button-group">
              <button @click="playSongAtIndex(index)" :class="['btn-icon', { 'btn-icon-active': index === currentSongIndex }]">
                <i class="fas fa-play"></i>
              </button>
              <button @click="removeItem(index)" :class="['btn-icon', { 'btn-icon-active': index === currentSongIndex }]">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
          </li>
        </template>
      </draggable>
    </div>
  </div>
  <button class="open-popup-button" v-if="!isOpen" @click="isOpen = true">
    <i class="fas fa-music"></i> Open Playlist Manager
  </button>
</template>

<script>
import { ref } from 'vue';
import draggable from 'vuedraggable';

const playlist = ref([]);

export const addSongToPlaylist = (song) => {
  playlist.value.push(song);
};

export default {
  props: {
    playSong: Function,
  },
  components: {
    draggable,
  },
  setup(props, { emit }) {
    const isOpen = ref(false);
    const newItem = ref('');
    const currentSongIndex = ref(-1);

    const removeItem = (index) => {
      playlist.value.splice(index, 1);
    };

    const onDragEnd = () => {
    };

    const playNextSong = () => {
      if (currentSongIndex.value < playlist.value.length - 1) {
        currentSongIndex.value++;
        props.playSong(playlist.value[currentSongIndex.value].index);
      }
    };

    const playSongAtIndex = (index) => {
      currentSongIndex.value = index;
      props.playSong(playlist.value[currentSongIndex.value].index);
    };

    const playPreviousSong = () => {
      if (currentSongIndex.value > 0) {
        currentSongIndex.value--;
        props.playSong(playlist.value[currentSongIndex.value].index);
      }
    };

    const playPlaylist = () => {
      currentSongIndex.value = 0;
      props.playSong(playlist.value[currentSongIndex.value].index);
    };

    const savePlaylist = () => {
      emit('playlist-action', { action: 'save', playlist: playlist.value, name: "New Playlist" });
    };

    const shufflePlaylist = () => {
      for (let i = playlist.value.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [playlist.value[i], playlist.value[j]] = [playlist.value[j], playlist.value[i]];
      }
    };

    return {
      isOpen,
      newItem,
      playlist,
      currentSongIndex,
      removeItem,
      onDragEnd,
      playSongAtIndex,
      playPlaylist,
      savePlaylist,
      shufflePlaylist,
      playNextSong,
      playPreviousSong
    };
  }
};
</script>

<style scoped>
.playlist-popup {
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 300px;
  background-color: #282828;
  color: #B3B3B3;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-size: 14px;
}

.playlist-header {
  background-color: #444;
  padding: 10px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 5px;
}

.btn-sm {
  background-color: #1DB954;
  border: none;
  color: white;
}

.btn-sm:hover {
  background-color: #1DB954;
  opacity: 0.8;
}

.playlist-body {
  padding: 10px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  max-height: 300px;
  overflow-y: auto;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px;
  background-color: #555;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 12px;
}

.truncate {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 180px;
}

.current-song {
  background-color: #1DB954;
  color: white; /* Text color for the active highlighted item */
}

.btn-icon {
  background: none;
  border: none;
  color: #B3B3B3;
  cursor: pointer;
  margin-left: 5px;
}

.btn-icon-active {
  color: white;
}

.btn-icon:hover {
  color: #1DB954;
}

.open-popup-button {
  position: fixed;
  bottom: 100px;
  right: 20px;
  padding: 10px 20px;
  border: none;
  background-color: #1DB954;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.open-popup-button:hover {
  background-color: #1DB954;
}

.playlist-body::-webkit-scrollbar {
  width: 8px;
}

.btn {
  color: white !important;
}

.playlist-body::-webkit-scrollbar-thumb {
  background-color: #1DB954;
  border-radius: 4px;
}

.playlist-body::-webkit-scrollbar-thumb:hover {
  background-color: #1ed760;
}
</style>
