<script setup>
import { onMounted, ref} from 'vue'
import axios from "axios";
import io from 'socket.io-client'
let question = ref('')
let answer = ref('')
let user_id = Math.random().toString(36).slice(-8)
//每次进入的时候随机加载user_id
let socket = io(axios.defaults.baseURL, {
  transports: ['websocket', 'polling'],
  timeout: 5000
})
function clsQue() {
  question.value = ''
}
socket.on('recAns',(resp)=>{
  answer.value += resp['msg']
})
socket.on('connect', () => {
  console.log('连接上了')
  user_id = socket.id
})
console.log(socket)
socket.on('disconnect', () => {
  console.log('断开了连接上')
  socket.close()
})

onMounted(() => {
  socket.emit('message', {
    data: '请求连接'
  })
})
window.onbeforeunload = ()=>{
  axios.get('/disconnect/' + user_id)
  socket.close()
}
function getAns() {
  if(question.value === '') {return}
  if (!socket.connected){
    alert('与服务器断开连接, 刷新页面就好')
    return
  }
  answer.value = ''
  axios.post('/getAns/'+ user_id, {"prompt": question.value}).then(async resp => {
    if (resp.data['msg'] === 'failure'){
      alert('单次请求上限为10次, 刷新浏览器即可重置')
    }else{
      console.log(resp.data['msg'])
    }
  }).catch(err => {
    console.log(err)
  })
}
</script>

<template>
  <div class="common-layout">
    <el-container style="height: 100vh">
      <el-header class="header">
        <div style="display: flex; flex-wrap: wrap; height: 100%">
          <el-input :rows="9" v-model="question" style="margin-top: 2px; flex: 1; height: 100%; font-size: 16px; max-height: 220px; overflow: auto" type="textarea" placeholder="您有什么问题"></el-input>
          <div style="display: flex; flex-direction: column; flex-wrap: wrap; align-self: center">
            <el-button @click="getAns" style="width: 80px; height: 40px; margin: 5px;">提问</el-button>
            <el-button @click="clsQue" style="width: 80px; height: 40px; margin: 5px;">清空</el-button>
          </div>

        </div>

      </el-header>
      <el-main class="main">
        <p style="font-size: 18px">回答:</p>
        <div class="pre-text">{{ answer }}</div>
      </el-main>
    </el-container>
  </div>
</template>


<style scoped>
.header {
  background-color: #337ecc;
  flex: 2;

}

.main {
  background-color: cadetblue;
  flex: 5;
}
.pre-text {
  white-space: pre-wrap;
  font-size: 19px;
}
</style>
