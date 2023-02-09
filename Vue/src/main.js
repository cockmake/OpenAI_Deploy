import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import axios from "axios";
axios.defaults.baseURL = "http://123.60.110.117:80/"
// axios.defaults.baseURL = "http://127.0.0.1:80/"


const app = createApp(App)

app.use(ElementPlus)
app.mount('#app')