<template>
  <div class="bg-white p-6 rounded shadow-md max-w-2xl mx-auto">
    <div class="mb-4">
      <label class="block font-bold mb-2">上傳郵件檔案 (.txt / .html)</label>
      <input type="file" @change="handleFileUpload" accept=".txt,.html" />
    </div>

    <div class="mb-4">
      <label class="block font-bold mb-2">郵件內容</label>
      <textarea v-model="content" rows="6" class="w-full border rounded p-2"></textarea>
    </div>

    <div class="mb-4">
      <label class="block font-bold mb-2">選擇魔法類型</label>
      <select v-model="generationType" class="w-full border rounded p-2">
        <option disabled value="">請選擇</option>
        <option v-for="type in magicOptions" :key="type.value" :value="type.value">
          {{ type.label }}
        </option>
      </select>
    </div>

    <div v-if="showNumSuggestions" class="mb-4">
      <label class="block font-bold mb-2">想要幾個點子？(1~3)</label>
      <input type="number" v-model.number="numSuggestions" min="1" max="3" class="w-full border rounded p-2" />
    </div>

    <button
      class="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      :disabled="cooldown || !content || !generationType"
      @click="handleSubmit"
    >
      用魔法打敗魔法
    </button>

    <p v-if="errorMsg" class="text-red-500 mt-2">{{ errorMsg }}</p>
    <p v-if="cooldown" class="text-gray-500 mt-2">冷卻中：{{ countdown }} 秒</p>

    <div v-if="result" class="mt-6">
      <h2 class="font-bold mb-2">✨ 魔法建議結果：</h2>
      <div v-if="result.magic_type === 'title_optimize'">
        <div v-for="(item, idx) in suggestions" :key="idx" class="mb-4">
          <p class="font-bold">
            標題：{{ item.title }}
            <button
              type="button"
              class="ml-2 text-sm text-blue-600 underline"
              @click="copyToClipboard(item.title)"
            >
              複製
            </button>
          </p>
          <p>
            預覽文字：{{ item.preheader }}
            <button
              type="button"
              class="ml-2 text-sm text-blue-600 underline"
              @click="copyToClipboard(item.preheader)"
            >
              複製
            </button>
          </p>
        </div>
      </div>
      <pre
        v-else
        class="bg-gray-100 p-3 rounded whitespace-pre-wrap"
      >{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const API_URL = process.env.API_URL;

const content = ref('');
const generationType = ref('');
const numSuggestions = ref(1);
const lastContent = ref('');
const lastGenerationType = ref('');
const token = ref('');
const result = ref(null);
const errorMsg = ref('');
const cooldown = ref(false);
const countdown = ref(10);
let cooldownTimer = null;

const suggestions = computed(() => {
  if (!result.value || !result.value.result) return [];
  return Array.isArray(result.value.result)
    ? result.value.result
    : [result.value.result];
});

const magicOptions = [
  { value: 'title_optimize', label: '標題和預覽文字（雙劍合璧）' },
  // { value: 'title', label: '郵件標題優化（第一印象很重要）' },
  // { value: 'preview', label: '預覽文字建議（吸引眼球的秘訣）' },
  // { value: 'tag', label: '內容關鍵標籤（抓住重點）' },
  // { value: 'spam', label: '垃圾郵件風險檢測（避開垃圾桶的命運）' },
  // { value: 'tone', label: '語氣與情感分析（懂你說話的感覺）' },
  // { value: 'cta', label: '行動號召強化（讓讀者乖乖點擊）' },
];

const showNumSuggestions = computed(() =>
  ['title_optimize', 'title', 'preview', 'cta'].includes(generationType.value)
);

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  errorMsg.value = '';

  const ext = file.name.substring(file.name.lastIndexOf('.'));
  if (!['.txt', '.html'].includes(ext)) {
    errorMsg.value = '僅支援 .txt 或 .html 檔案';
    content.value = '';
    return;
  }

  if (file.size > 1024 * 1024) {
    errorMsg.value = '檔案過大，限制為 1MB';
    content.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    const text = reader.result.trim();
    if (!text) {
      errorMsg.value = '檔案內容為空';
      content.value = '';
      return;
    }
    content.value = text;
  };
  reader.readAsText(file);
}

function utf8ToBase64(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

function copyToClipboard(text) {
  // Centralize clipboard logic for reuse and keep template clean
  navigator.clipboard.writeText(text).catch(() => {
    // Ignore errors to avoid distracting the user
  });
}

async function handleSubmit() {
  errorMsg.value = '';

  if (!content.value) {
    errorMsg.value = '郵件內容為空';
    return;
  }

  if (showNumSuggestions.value && numSuggestions.value > 3) {
    errorMsg.value = '最多只能選 3 個點子唷！';
    return;
  }

  if (content.value.length < 50) {
    errorMsg.value = '字太少囉！至少給 50 個字才能發揮魔法～';
    return;
  }

  if (
    content.value === lastContent.value &&
    generationType.value === lastGenerationType.value
  ) {
    errorMsg.value = '郵件內容沒有變化，打個哈欠表示無聊～重新編輯再試吧！';
    return;
  }

  if (cooldown.value) {
    errorMsg.value = '冷靜一下，等10秒再來試試吧！';
    return;
  }

  // 記錄本次內容
  lastContent.value = content.value;
  lastGenerationType.value = generationType.value;

  // 冷卻機制
  cooldown.value = true;
  countdown.value = 10;
  cooldownTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(cooldownTimer);
      cooldown.value = false;
    }
  }, 1000);

  // 取得 JWT
  if (!token.value) {
    try {
      const exp = Math.floor(Date.now() / 1000) + 20 * 60;
      const jwtRes = await axios.post(
        API_URL + '/email-analyzer/api/public/v1/jwt',
        {
          userSn: 'dev-fe-' + exp,
          exp: new Date(exp * 1000).toISOString(),
        }
      );
      token.value = jwtRes.data.token;
    } catch (err) {
      errorMsg.value = err.message || '取得 JWT 失敗';
      return;
    }
  }

  const payload = {
    campaignSn: utf8ToBase64(content.value + generationType.value).substring(0, 16),
    content: content.value,
    magic_type: generationType.value,
  };

  if (showNumSuggestions.value) {
    payload.num_suggestions = numSuggestions.value;
  }

  try {
    const res = await axios.post(
      API_URL + '/email-analyzer/api/public/v1/generate',
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + token.value,
        },
      }
    );
    result.value = res.data;
  } catch (err) {
    if (err.response && err.response.status === 429) {
      const data = err.response.data;
      errorMsg.value = data.message + `，請於 ${data.nextAllowedTime} 再試`;
    } else {
      errorMsg.value = err.message || '發生錯誤';
    }
  }
}
</script>
