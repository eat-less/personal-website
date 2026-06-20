<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您访问的页面不存在或已被移除。</p>
      <a href="/" class="btn-primary">返回首页</a>
    </div>
  </div>
</template>

<script setup>
// 404页面组件
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.not-found-content {
  text-align: center;
  padding: 50px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 80px;
  margin: 0 0 20px 0;
  color: #2196F3;
}

h2 {
  font-size: 32px;
  margin: 0 0 20px 0;
  color: #333;
}

p {
  font-size: 16px;
  margin: 0 0 30px 0;
  color: #666;
}

.btn-primary {
  display: inline-block;
  padding: 12px 24px;
  background-color: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #1976D2;
}
</style>
