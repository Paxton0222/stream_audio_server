<template>

</template>

<script setup>
    import { ref, onMounted } from "vue";
    import api from "../api"

    const state = ref(null)

    onMounted(async () => {
        let state_res = await api.stream.state('paxton','2')
        if (state_res.status == 200){
            state.value = state_res.data
        }
    })

</script>