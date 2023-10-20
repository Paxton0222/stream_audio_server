<template>
    <div class="flex justify-center hidden">
        <video ref="audio" class="video-js vjs-default-skin" controls autoplay muted></video>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import videojs from 'video.js'

const audio = ref(null)
const props = defineProps({
    src: {
        type: String,
        default: undefined
    }
})

let player = null
let retryInterval = null
const retryDelay = 5000 // 重试间隔，单位毫秒

const initializePlayer = () => {
    if (player) {
        player.dispose() // 销毁现有的Video.js播放器
    }

    // 创建一个新的Video.js播放器
    player = videojs(audio.value, {
        controls: true,
        autoplay: true,
        muted: true,
        sources: [
            {
                src: props.src,
                type: 'application/x-mpegURL' // 指定媒体类型
            }
        ]
    })

    // 在 "ended" 事件发生时执行重新连接
    player.on('ended', () => {
        retry()
    })

    player.on('error', () => {
        retry()
    })

    // 在 "playing" 事件发生时清除重试间隔
    player.on('playing', () => {
        player.play()
        // player.muted(false)
        clearInterval(retryInterval)
    })
}

const retry = () => {
    // 清除现有的重试间隔
    clearInterval(retryInterval)

    // 创建一个新的重试间隔
    retryInterval = setInterval(() => {
        initializePlayer()
    }, retryDelay)
}

onMounted(() => {
    initializePlayer() // 初始化播放器

    document.addEventListener('click', () => {
        // 当用户点击文档的任意地方时，取消静音
        if (player) {
            player.muted(false)
        }
    })
})

onUnmounted(() => {
    if (player) {
        player.dispose() // 在组件卸载时销毁播放器
    }
    clearInterval(retryInterval)
})

retry() // 初始化时执行第一次重连
</script>

<style>
/* 您的CSS样式可以放在这里 */
</style>
