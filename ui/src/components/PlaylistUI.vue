<template>
  <div class="playlist-popup" v-if="isOpen">
    <div class="playlist-header">
      <h3>Playlist Manager</h3>
      <div class="button-group">
        <button @click="playPlaylist" class="btn btn-sm">Play</button>
        <button @click="savePlaylist" class="btn btn-sm">Save Playlist</button>
        <button @click="shufflePlaylist" class="btn btn-sm">Shuffle</button>
        <button @click="handleAddItem" class="btn btn-sm">Add</button>
        <button @click="isOpen = false" class="btn btn-sm">X</button>
      </div>
    </div>
    <div class="playlist-body">
      <draggable v-model="playlist" @end="onDragEnd" tag="ul">
        <template #item="{ element, index }">
          <li :key="index" class="list-item">
            {{ element.name }}
            <button @click="removeItem(index)">Remove</button>
          </li>
        </template>
      </draggable>
    </div>
  </div>
  <button class="open-popup-button" v-if="!isOpen" @click="isOpen = true">
    Open Playlist Manager
  </button>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import draggable from 'vuedraggable';

const playlist = ref([]);

export const addSongToPlaylist = (song) => {
  playlist.value.push(song);
};

export default {
  props: {
    playSong: Function,
    nextSong: Function,
    previousSong: Function
  },
  components: {
    draggable,
  },
  setup(props) {
    const isOpen = ref(false);
    const newItem = ref('');
    const currentSongIndex = ref(-1);

    const handleAddItem = () => {
      addSongToPlaylist({ name: newItem.value, index: playlist.value.length });
      newItem.value = '';
    };

    const removeItem = (index) => {
      playlist.value.splice(index, 1);
    };

    const onDragEnd = () => {
      // Logic to handle when dragging ends (if needed)
    };

    const playNextSong = () => {
      console.log("Playist sees the new next event!")
      if (currentSongIndex.value < playlist.value.length - 1) {
        currentSongIndex.value++;
        props.playSong(playlist.value[currentSongIndex.value].index);
      }
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
      // Logic to save the playlist
      console.log('Saving playlist:', playlist.value);
    };

    const shufflePlaylist = () => {
      // Logic to shuffle the playlist
      for (let i = playlist.value.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [playlist.value[i], playlist.value[j]] = [playlist.value[j], playlist.value[i]];
      }
    };

    watch(currentSongIndex, (newIndex, oldIndex) => {
      if (newIndex !== oldIndex) {
        if (newIndex < playlist.value.length) {
          props.playSong(playlist.value[newIndex].index);
        }
      }
    });

    watch(playlist, () => {
      if (currentSongIndex.value >= playlist.value.length) {
        currentSongIndex.value = playlist.value.length - 1;
      }
    });

    // eslint-disable-next-line vue/no-deprecated-events-api
    onMounted(() => {
      // eslint-disable-next-line vue/no-deprecated-events-api
      this.$on('next', playNextSong);
      // eslint-disable-next-line vue/no-deprecated-events-api
      this.$on('previous', playPreviousSong);
    });

    // eslint-disable-next-line vue/no-deprecated-events-api
    onUnmounted(() => {
      // eslint-disable-next-line vue/no-deprecated-events-api
      this.$off('next', playNextSong);
      // eslint-disable-next-line vue/no-deprecated-events-api
      this.$off('previous', playPreviousSong);
    });

    return {
      isOpen,
      newItem,
      playlist,
      handleAddItem,
      removeItem,
      onDragEnd,
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
  background-color: #333;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.playlist-header {
  background-color: #444;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 5px;
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
  padding: 5px 0;
  background-color: #555;
  margin-bottom: 5px;
  border-radius: 4px;
}

input {
  padding: 5px;
  margin: 10px 0;
  border: 1px solid #666;
  border-radius: 4px;
  background-color: #444;
  color: white;
}

button {
  padding: 5px 10px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.open-popup-button {
  position: fixed;
  bottom: 100px;
  right: 20px;
  padding: 10px 20px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.open-popup-button:hover {
  background-color: #0056b3;
}

.list-item button {
  background-color: #ff4d4d;
}

.list-item button:hover {
  background-color: #ff1a1a;
}
</style>
