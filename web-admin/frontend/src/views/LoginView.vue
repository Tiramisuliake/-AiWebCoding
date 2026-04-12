<script setup>
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { useI18n } from "../composables/useI18n";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const formRef = ref();
const { t, locale, setLocale } = useI18n();

const form = reactive({
  username: "",
  password: ""
});

const localeOptions = computed(() => [
  { value: "zh-CN", label: t("common.chinese") },
  { value: "en-US", label: t("common.english") }
]);

const rules = computed(() => ({
  username: [{ required: true, message: t("login.usernameRequired"), trigger: "blur" }],
  password: [{ required: true, message: t("login.passwordRequired"), trigger: "blur" }]
}));

async function submit() {
  await formRef.value.validate();
  try {
    await authStore.login(form);
    const redirect = route.query.redirect || "/";
    router.push(redirect);
    ElMessage.success(t("login.loginSuccess"));
  } catch (error) {
    const msg = error.response?.data?.msg || error.message || t("login.loginFailed");
    ElMessage.error(msg);
  }
}

function onLocaleChange(value) {
  setLocale(value);
}
</script>

<template>
  <div class="login-page">
    <div class="orb orb-a"></div>
    <div class="orb orb-b"></div>
    <div class="grid-mask"></div>

    <el-card class="login-card">
      <div class="card-head">
        <div>
          <h1 class="title">{{ t("login.title") }}</h1>
          <p class="subtitle">{{ t("login.subtitle") }}</p>
        </div>
        <el-select
          :model-value="locale"
          size="small"
          style="width: 105px"
          @change="onLocaleChange"
        >
          <el-option
            v-for="option in localeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('login.username')" prop="username">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('login.password')" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            autocomplete="current-password"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button
          type="primary"
          :loading="authStore.loading"
          class="submit-btn"
          @click="submit"
        >
          {{ t("login.signIn") }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(155deg, #0f172a 0%, #1e3a8a 42%, #e2e8f0 100%);
  position: relative;
  overflow: hidden;
  padding: var(--space-2);
}

.orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(20px);
}

.orb-a {
  width: 260px;
  height: 260px;
  background: rgba(56, 189, 248, 0.45);
  top: -80px;
  left: -40px;
}

.orb-b {
  width: 300px;
  height: 300px;
  background: rgba(147, 197, 253, 0.35);
  bottom: -120px;
  right: -80px;
}

.grid-mask {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: linear-gradient(transparent 95%, rgba(255, 255, 255, 0.18) 95%),
    linear-gradient(90deg, transparent 95%, rgba(255, 255, 255, 0.18) 95%);
  background-size: 30px 30px;
  opacity: 0.2;
}

.login-card {
  width: min(92vw, 460px);
  border-radius: 14px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(8px);
  position: relative;
  z-index: 2;
}

.card-head {
  margin-bottom: var(--space-2);
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: var(--space-2);
}

.title {
  margin: 0 0 6px;
  font-size: 28px;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
}

.submit-btn {
  width: 100%;
  margin-top: var(--space-1);
  height: 42px;
}
</style>
