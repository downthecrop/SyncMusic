<template>
  <div class="playlist-popup" v-if="isOpen">
    <div class="playlist-header">
      <h3>Playlist Manager</h3>
      <button @click="isOpen = false">X</button>
    </div>
    <div class="playlist-body">
      <draggable v-model="playlist" @end="onDragEnd" tag="ul">
        <template #item="{ element, index }">
          <li :key="index" class="list-item">
            {{ element }}
            <button @click="removeItem(index)">Remove</button>
          </li>
        </template>
      </draggable>
      <input v-model="newItem" placeholder="Add new item" />
      <button @click="addItem">Add</button>
    </div>
  </div>
  <button class="open-popup-button" v-if="!isOpen" @click="isOpen = true">
    Open Playlist Manager
  </button>
</template>

<script>
import { ref } from 'vue';
import draggable from 'vuedraggable';

export default {
  components: {
    draggable,
  },
  setup() {
    const isOpen = ref(false);
    const newItem = ref('');
    const playlist = ref([]);

    const addItem = () => {
      if (newItem.value.trim()) {
        playlist.value.push(newItem.value.trim());
        newItem.value = '';
      }
    };

    const removeItem = (index) => {
      playlist.value.splice(index, 1);
    };

    const onDragEnd = () => {
      // Logic to handle when dragging ends (if needed)
    };

    return {
      isOpen,
      newItem,
      playlist,
      addItem,
      removeItem,
      onDragEnd,
    };
  },
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

.playlist-body {
  padding: 10px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
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
