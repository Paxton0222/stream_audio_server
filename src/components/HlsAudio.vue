<template>
    <div class="flex justify-center hidden">
        <audio ref="audio" controls autoplay muted></audio>
    </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import Hls from 'hls.js';

const audio = ref(null)
const props = defineProps({
    src: {
        type: String,
        default: undefined
    },
    muted: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(["play", "pause", "muteState"])

const hls = new Hls({})

let interval = null
let clicked = ref(false)
let playing = ref(false)
let muted = ref(props.muted)

const loadAudioStream = () => {
    hls.loadSource(props.src)
    hls.attachMedia(audio.value)
    hls.on(Hls.Events.ERROR, async (event, data) => {
        if (data.type === Hls.ErrorTypes.NETWORK_ERROR && data.fatal) {
            playing.value = false
            if (interval === null) {
                interval = setInterval(() => {
                    console.error("retrying...")
                    hls.loadSource(props.src)
                    hls.attachMedia(audio.value)
                    emit("pause")
                }, 5000)
            }
        }
    });
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log("audio stream attached.")
        if (interval !== null) {
            clearInterval(interval)
            interval = null
        }
        if (!clicked.value) {
            audio.value.muted = true;
            muted.value = audio.value.muted
        }
        else{
            audio.value.play()
        }
        playing.value = true
        emit("play")
    })
}
watch(muted, (value) => {
    emit("muteState", value)
})
watch(props, (value) => {
    audio.value.muted = value.muted 
    muted.value = audio.value.muted
})
onMounted(async () => {
    document.addEventListener('click', () => {
        if (audio.value !== null && !clicked.value) {
            audio.value.muted = false
            muted.value = audio.value.muted
            audio.value.play()
        }
        clicked.value = true;
    })
    loadAudioStream()
})
</script>
