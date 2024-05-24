$(document).ready(function () {
    $.get('/songs', function (data) {
        var songs = data.songs;
        var songsList = $('#songs-list');
        songs.forEach(function (song) {
            songsList.append(
                '<li class="list-group-item">' +
                '<a href="#" class="play-song" data-index="' + song.index + '">' + song.name + '</a>' +
                '<br><small>' + song.path + '</small>' +
                '</li>'
            );
        });
    });

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Connected to server');
    });

    $(document).on('click', '.play-song', function (e) {
        e.preventDefault();
        var songIndex = $(this).data('index');
        console.log('Emitting play_song event for index ' + songIndex);
        socket.emit('play_song', { index: songIndex });
    });

    socket.on('play_song', function (data) {
        console.log("trying to play", data.url);
        var audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = '/stream?url=' + encodeURIComponent(data.url);
        audioPlayer.play();

        fetch(audioPlayer.src, { method: 'HEAD' }).then(response => {
            document.getElementById('track-title').textContent = response.headers.get('X-Metadata-Title') || 'Unknown Title';
            document.getElementById('track-artist').textContent = response.headers.get('X-Metadata-Artist') || 'Unknown Artist';
            document.getElementById('track-album').textContent = response.headers.get('X-Metadata-Album') || 'Unknown Album';
            document.getElementById('track-year').textContent = response.headers.get('X-Metadata-Year') || 'Unknown Year';
        });
    });
});

const audio = document.getElementById('audio-player');
const playPauseBtn = document.getElementById('play-pause-btn');
const seekBar = document.getElementById('seek-bar');
const volumeBar = document.getElementById('volume-bar');
const currentTimeElem = document.getElementById('current-time');
const durationElem = document.getElementById('duration');

playPauseBtn.addEventListener('click', () => {
    if (audio.paused) {
        audio.play();
        playPauseBtn.textContent = '⏸️';
    } else {
        audio.pause();
        playPauseBtn.textContent = '▶️';
    }
});

audio.addEventListener('timeupdate', () => {
    if (!isNaN(audio.currentTime) && !isNaN(audio.duration)) {
        seekBar.value = (audio.currentTime / audio.duration) * 100;
        currentTimeElem.textContent = formatTime(audio.currentTime);
    }
});

seekBar.addEventListener('input', () => {
    if (!isNaN(audio.duration)) {
        audio.currentTime = (seekBar.value / 100) * audio.duration;
    }
});

volumeBar.addEventListener('input', () => {
    audio.volume = volumeBar.value / 100;
});

audio.addEventListener('loadedmetadata', () => {
    if (!isNaN(audio.duration)) {
        durationElem.textContent = formatTime(audio.duration);
    }
});

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    seconds = Math.floor(seconds % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}