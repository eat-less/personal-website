<template>
  <div class="publish-container">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        返回
      </button>
      <h1>发布闲置</h1>
    </div>
    
    <div class="publish-form">
      <!-- 图片上传区域 -->
      <div class="form-section">
        <h3>商品图片</h3>
        <div class="image-upload-area">
          <label for="image-upload" class="upload-btn" v-if="images.length < 6">
            <span class="upload-icon">+</span>
            <input 
              type="file" 
              id="image-upload" 
              ref="imageInput"
              accept="image/*" 
              multiple
              @change="handleImageUpload"
              style="display: none"
            >
            <span class="upload-text">点击上传图片</span>
            <span class="upload-hint">最多上传6张</span>
          </label>
          
          <!-- 图片预览列表 -->
          <div class="image-preview-list">
            <div 
              v-for="(image, index) in images" 
              :key="index"
              class="image-preview-item"
              @click="openImagePreview(index)"
            >
              <img :src="image.url" :alt="`商品图片${index+1}`" class="preview-img">
              <button 
                class="remove-image-btn"
                @click.stop="removeImage(index)"
              >×</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 商品信息区域 -->
      <div class="form-section">
        <h3>商品信息</h3>
        
        <!-- 商品标题 -->
        <div class="form-group">
          <label for="title">商品标题</label>
          <input 
            type="text" 
            id="title" 
            v-model="form.title" 
            placeholder="请输入商品标题"
            class="form-input"
          >
        </div>
        
        <!-- 商品描述 -->
        <div class="form-group">
          <label for="description">商品描述</label>
          <textarea 
            id="description" 
            v-model="form.description" 
            placeholder="请详细描述商品的成色、使用情况等信息"
            rows="4"
            class="form-textarea"
          ></textarea>
        </div>
        
        <!-- 商品分类 -->
        <div class="form-group">
          <label for="category">商品分类</label>
          <select 
            id="category" 
            v-model="form.category" 
            class="form-select"
          >
            <option value="">请选择分类</option>
            <option value="electronics">电子数码</option>
            <option value="books">图书教材</option>
            <option value="clothing">服饰鞋包</option>
            <option value="sports">运动户外</option>
            <option value="jewelry">时尚首饰</option>
            <option value="food">零食饮料</option>
            <option value="beauty">美妆护肤</option>
            <option value="home">家居日用</option>
            <option value="cards">卡包劵包</option>
            <option value="other">其他</option>
          </select>
        </div>
        
        <!-- 价格和数量 -->
        <div class="form-row">
          <div class="form-group">
            <label for="price">价格</label>
            <div class="price-input">
              <span class="price-symbol">¥</span>
              <input 
                type="text" 
                id="price" 
                v-model="form.price" 
                placeholder="0.00"
                class="form-input price"
                @input="handlePriceInput"
                @keypress="handlePriceKeypress"
              >
              <p v-if="priceError" class="error-message">{{ priceError }}</p>
            </div>
          </div>
          
          <div class="form-group">
            <label for="quantity">数量</label>
            <input 
              type="number" 
              id="quantity" 
              v-model.number="form.quantity" 
              placeholder="1"
              min="1"
              class="form-input"
            >
          </div>
        </div>
        
        <!-- 配送方式 -->
        <div class="form-group">
          <label>配送方式</label>
          <div class="delivery-options">
            <label class="delivery-option">
              <input 
                type="radio" 
                v-model="form.delivery_method" 
                value="self_pickup"
              >
              <span class="option-text">买家自提</span>
            </label>
            <label class="delivery-option">
              <input 
                type="radio" 
                v-model="form.delivery_method" 
                value="delivery"
              >
              <span class="option-text">支持配送</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- 提交按钮 -->
      <div class="form-actions">
        <button 
          type="button" 
          class="btn-primary"
          @click="submitForm"
          :disabled="loading"
        >
          {{ loading ? '发布中...' : '发布商品' }}
        </button>
      </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div class="image-preview-modal" v-if="showImageModal" @click="closeImagePreview">
      <div class="modal-content" @click.stop>
        <img :src="previewImage" alt="图片预览" class="modal-image">
        <button class="close-btn" @click="closeImagePreview">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const router = useRouter();
const loading = ref(false);
const images = ref([]);
const showImageModal = ref(false);
const previewImage = ref('');
const imageInput = ref(null);

// 表单数据
const form = ref({
  title: '',
  description: '',
  category: '',
  price: '',
  quantity: 1,
  delivery_method: 'self_pickup'
});

// 错误信息
const priceError = ref('');

// 返回上一页
const goBack = () => {
  router.back();
};

// 处理图片上传
const handleImageUpload = (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    Array.from(files).forEach(file => {
      if (images.value.length >= 6) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        images.value.push({
          file: file,
          url: e.target.result
        });
      };
      reader.readAsDataURL(file);
    });
  }
};

// 移除图片
const removeImage = (index) => {
  images.value.splice(index, 1);
};

// 打开图片预览
const openImagePreview = (index) => {
  if (images.value[index]) {
    previewImage.value = images.value[index].url;
    showImageModal.value = true;
  }
};

// 关闭图片预览
const closeImagePreview = () => {
  showImageModal.value = false;
  previewImage.value = '';
};

// 价格输入处理
const handlePriceInput = (event) => {
  const input = event.target;
  let value = input.value;
  
  // 保存原始值和光标位置
  const originalValue = value;
  const cursorPos = input.selectionStart;
  
  // 移除所有非数字和小数点的字符
  value = value.replace(/[^0-9.]/g, '');
  
  // 确保只有一个小数点
  const parts = value.split('.');
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('');
  }
  
  // 限制小数点后最多两位
  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].substring(0, 2);
  }
  
  // 计算新的光标位置
  let newCursorPos = cursorPos;
  if (value.length < originalValue.length) {
    // 如果字符被删除，保持光标位置
    newCursorPos = Math.min(cursorPos, value.length);
  } else if (value.length > originalValue.length) {
    // 如果字符被添加，光标位置向前移动
    newCursorPos = cursorPos;
  }
  
  // 更新值
  form.value.price = value;
  
  // 延迟设置光标位置，确保DOM已更新
  setTimeout(() => {
    input.focus();
    input.setSelectionRange(newCursorPos, newCursorPos);
  }, 0);
};

// 价格按键处理
const handlePriceKeypress = (event) => {
  const charCode = event.charCode;
  // 只允许数字和小数点
  return (charCode >= 48 && charCode <= 57) || charCode === 46;
};

// 提交表单
const submitForm = async () => {
  // 表单验证
  if (!form.value.title) {
    alert('请输入商品标题');
    return;
  }
  
  if (!form.value.description) {
    alert('请输入商品描述');
    return;
  }
  
  if (!form.value.category) {
    alert('请选择商品分类');
    return;
  }
  
  if (!form.value.price || form.value.price <= 0) {
    alert('请输入有效的价格');
    return;
  }
  
  if (images.value.length === 0) {
    alert('请至少上传一张商品图片');
    return;
  }
  
  loading.value = true;
  
  try {
    // 创建FormData对象
    const formData = new FormData();
    
    // 添加商品信息
    formData.append('title', form.value.title);
    formData.append('description', form.value.description);
    formData.append('category', form.value.category);
    formData.append('price', form.value.price);
    formData.append('quantity', form.value.quantity);
    formData.append('delivery_method', form.value.delivery_method);
    
    // 添加图片
    images.value.forEach((image, index) => {
      formData.append('images', image.file);
    });
    
    // 发送请求
            const response = await api.post('/products/', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            
            alert('发布成功，商品待审核中');
            router.push('/');
  } catch (err) {
    console.error('发布失败:', err);
    alert('发布失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.publish-container {
  max-width: 800px;
  margin: 50px auto;
  padding: 0 20px;
  min-height: calc(100vh - 100px);
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

/* 返回按钮 */
.back-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background-color: #e0e0e0;
  border-color: #ccc;
}

.back-icon {
  font-size: 16px;
  font-weight: bold;
}

.page-header h1 {
  color: #333;
  margin: 0;
  font-size: 24px;
}

/* 发布表单 */
.publish-form {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

/* 表单区域 */
.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

/* 图片上传区域 */
.image-upload-area {
  position: relative;
}

.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #f9f9f9;
}

.upload-btn:hover {
  border-color: #2196F3;
  background-color: #f0f8ff;
}

.upload-icon {
  font-size: 32px;
  color: #999;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 12px;
  color: #999;
}

/* 图片预览列表 */
.image-preview-list {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.image-preview-item {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #ddd;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.remove-image-btn:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

/* 表单组 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
  font-size: 14px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.3s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* 表单行 */
.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

/* 价格输入 */
.price-input {
  position: relative;
}

.price-symbol {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 14px;
}

.price {
  padding-left: 24px;
}

/* 配送方式选项 */
.delivery-options {
  display: flex;
  gap: 30px;
}

.delivery-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.delivery-option input[type="radio"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* 表单操作 */
.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.btn-primary {
  padding: 12px 40px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1976D2;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 图片预览模态框 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: -10px;
  width: 30px;
  height: 30px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
  
  .delivery-options {
    flex-direction: column;
    gap: 10px;
  }
  
  .image-preview-list {
    justify-content: center;
  }
}
</style>
