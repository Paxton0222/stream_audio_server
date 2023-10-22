<template>
    <div class="w-screen h-screen p-4">
        <div class="flex flex-col items-center justify-center">
            <div class="flex justify-center w-4/12">
                <template v-if="data.state.data.thumb_url !== null">
                    <img class="max-w-full max-h-full" :src="data.state.data.thumb_url" />
                </template>
                <template v-else> </template>
            </div>
            <div>
                <p class="mt-2" v-if="playing">
                    {{ data.state.data.title }} - {{ data.state.data.author }}
                </p>
            </div>
        </div>
        <div class="flex justify-center gap-2 mt-4">
            <input
                type="text"
                placeholder="輸入 URL"
                class="w-full max-w-xs input input-bordered"
                v-model="url_input"
                @keyup.enter="add_music"
            />
            <button class="btn btn-square" @click="add_music">
                <vue-feather type="send"></vue-feather>
            </button>
        </div>
        <HlsAudio class="mt-4" :src="hlsSrc" :muted="muted" @play="audio_play" @pause="audio_pause" @mute-state="audio_muted"/>
        <div class="flex justify-center mt-4">
            <div class="btn-group btn-group-vertical lg:btn-group-horizontal">
                <button class="btn" @click="play_music" v-if="!playing">
                    <vue-feather type="play"></vue-feather>
                </button>
                <button class="btn" @click="pause_music" v-if="playing">
                    <vue-feather type="pause"></vue-feather>
                </button>
                <button class="btn" @click="next_music">
                    <vue-feather type="skip-forward"></vue-feather>
                </button>
                <button class="btn" @click="change_mute_state">
                    <vue-feather :type="mute_icon"></vue-feather>
                </button>
            </div>
        </div>
        <div class="overflow-x-auto overflow-y-scroll scrollbar-none">
            <table class="table">
                <!-- head -->
                <thead>
                    <tr>
                        <th></th>
                        <th>title</th>
                        <th>author</th>
                        <th>length (sec)</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- row 1 -->
                    <tr
                        :class="{ 'bg-base-200': index === 0 && playing }"
                        v-bind:key="index"
                        v-for="(music, index) in data.list.data"
                    >
                        <th>{{ index + 1 }}</th>
                        <td>{{ music.title }}</td>
                        <td>{{ music.author }}</td>
                        <td>{{ music.length }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="toast toast-top toast-right">
            <div
                class="flex justify-center duration-300 ease-in-out alert alert-info"
                v-bind:key="index"
                v-for="(toast, index) in toast_notifications"
            >
                <span>{{ toast }}</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import HlsAudio from './HlsAudio.vue'
import api from '../api'

const route = useRoute()
const room = ref(route.params.room)
const channel = ref(route.params.channel)
const page = ref(1)
const limit = ref(10)
const url_input = ref('')
const muted = ref(true)
const toast_notifications = ref([])
const data = reactive({
    state: {
        status: false,
        state: null,
        task_id: null,
        data: {
            url: null,
            audio_url: null,
            title: null,
            author: null,
            thumb_url: null,
            length: 0
        }
    },
    list: {
        data: [],
        total: 1, // total page
        length: 0
    }
})

const mute_icon = computed(() => {
    return muted.value ? "volume-x" : "volume-2" 
})

const websocket_url = computed(() => `${import.meta.env.VITE_WEBSOCKET_URL}/api/radio/${room.value}/${channel.value}`)

const playing = computed(() => {
    return (
        data.state !== null &&
        data.state.status === true &&
        data.state.task_id !== null &&
        data.state.state === 'STARTED'
    )
})
const hlsSrc = computed(() => `${import.meta.env.VITE_HLS_URL}/live/${room.value}-room-${channel.value}.m3u8`)

const load_state = async () => {
    let state_res = await api.stream.state(room.value, channel.value)
    return state_res.status == 200 ? state_res.data : null
}
const load_list = async () => {
    let res = await api.stream.list(room.value, channel.value, page.value, limit.value)
    let temp = []
    res.data.data.forEach((data) => temp.push(JSON.parse(data)))
    res.data.data = temp
    return res.status == 200 ? res.data : null
}
const add_music = async () => {
    if (url_input.value !== '') {
        let temp = url_input.value
        url_input.value = ''
        let res = await api.stream.add(room.value, channel.value,temp)
        if (res.status === 200 && res.data.status) {
            toast_notifications.value.push('加入音樂成功')
            await update()
        } else {
            toast_notifications.value.push(res.data.message)
        }
        return
    } else {
        toast_notifications.value.push('請輸入正確的 Youtube URL')
    }
}
const play_music = async () => {
    toast_notifications.value.push('播放訊息已發送，請稍等...')
    let res = await api.stream.play(room.value, channel.value)
    toast_notifications.value.push(
        res.status === 200
            ? res.data.status
                ? '已開始播放音樂'
                : res.data.message 
            : `播放音樂失敗 (${res.status})`
    )
    await update()
    return res.status == 200 ? res.data : null
}
const pause_music = async () => {
    toast_notifications.value.push('暫停訊息已發送，請稍等...')
    let res = await api.stream.pause(room.value, channel.value)
    toast_notifications.value.push(
        res.status === 200
            ? res.data.status
                ? '已暫停播放音樂'
                : res.data.message
            : `暫停音樂失敗 (${res.status})`
    )
    await update()
    return res.status == 200 ? res.data : null
}
const next_music = async () => {
    toast_notifications.value.push('切換下一首訊息已發送，請稍等...')
    let res = await api.stream.next(room.value, channel.value)
    toast_notifications.value.push(
        res.status === 200
            ? res.data.status
                ? '已切換下一首播放音樂'
                : res.data.message 
            : `切換音樂失敗 (${res.status})`
    )
    await update()
    return res.status == 200 ? res.data : null
}
// eslint-disable-next-line no-unused-vars
const next_page = async () => {
    page.value < data.list.total ? (page.value += limit.value) : null
}
const update = async () => {
    data.list = await load_list()
    data.state = await load_state()
}

const audio_play = async () => {
    await update()
}
const audio_pause = async () => {
    await update()
}
const audio_muted = async (value) => {
    muted.value = value
}
const change_mute_state = () => {
    muted.value = !muted.value
}

let websocket_retry_interval = null

const create_websocket = () => {
    let websocket = new WebSocket(websocket_url.value)

    websocket.addEventListener('message', (event) => {
        let data = JSON.parse(event.data)
        console.log(data)
        if (data.type === "worker") {
            switch (data.message){
                case "play":
                    audio_play()
                    break
                case "pause":
                    audio_pause()
                    break
            }
        } 
    });

    websocket.addEventListener('open', () => {
        if (websocket_retry_interval !== null) {
            clearInterval(websocket_retry_interval)
        }
    });

    websocket.addEventListener('error', (event) => {
        if (websocket_retry_interval === null) {
            websocket_retry_interval = setInterval(() => {
                console.error("websocket retrying...")
                create_websocket()
            },2000)
        } 
    });
}

create_websocket()

watch(toast_notifications.value, () => {
    setTimeout(() => toast_notifications.value.shift(), 3000)
})

onMounted(async () => {
    await update()
})
</script>
