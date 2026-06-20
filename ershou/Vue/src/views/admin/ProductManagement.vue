<template>
  <div class="product-management">
    <h2>商品管理</h2>
    <div class="search-filter-bar">
      <div class="search">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索商品标题或描述"
          @input="searchProducts"
        />
        <button class="btn-primary">搜索</button>
      </div>
      <div class="filter">
        <select v-model="statusFilter" @change="filterProducts">
          <option value="">所有状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已上架</option>
          <option value="rejected">已拒绝</option>
          <option value="sold_out">已售罄</option>
          <option value="removed">已下架</option>
        </select>
      </div>
    </div>
    <div class="product-list">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>商品标题</th>
            <th>卖家</th>
            <th>分类</th>
            <th>价格</th>
            <th>状态</th>
            <th>浏览量</th>
            <th>点赞数</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>{{ product.id }}</td>
            <td>{{ product.title }}</td>
            <td>{{ product.seller_username }}</td>
            <td>{{ getCategoryName(product.category.name) }}</td>
            <td>¥{{ product.price }}</td>
            <td>
              <span :class="['status-badge', product.status]">
                {{ getStatusText(product.status) }}
              </span>
            </td>
            <td>{{ product.views }}</td>
            <td>{{ product.likes_count }}</td>
            <td>{{ formatDate(product.created_at) }}</td>
            <td>
              <button class="btn-secondary" @click="viewProductDetails(product.id)">查看详情</button>
              <button class="btn-primary" v-if="product.status === 'pending'" @click="approveProduct(product.id)">审核通过</button>
              <button class="btn-danger" v-if="product.status === 'pending'" @click="rejectProduct(product.id)">拒绝</button>
              <button class="btn-danger" v-if="product.status === 'approved'" @click="removeProduct(product.id)">下架</button>
              <button class="btn-danger" @click="deleteProduct(product.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination" v-if="totalProducts > pageSize">
      <button 
        class="btn-secondary" 
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button 
        class="btn-secondary" 
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../axios';

const products = ref([]);
const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalProducts = ref(0);

const totalPages = computed(() => {
  return Math.ceil(totalProducts.value / pageSize.value);
});

const router = useRouter();

const fetchProducts = async () => {
  try {
    const response = await api.get('/admin/products/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value,
        status: statusFilter.value
      }
    });
    products.value = response.data.results;
    totalProducts.value = response.data.count;
  } catch (error) {
    console.error('获取商品列表失败:', error);
    products.value = [];
    totalProducts.value = 0;
    alert('获取商品列表失败，请检查网络连接或权限');
  }
};

const searchProducts = () => {
  currentPage.value = 1;
  fetchProducts();
};

const filterProducts = () => {
  currentPage.value = 1;
  fetchProducts();
};

const changePage = (page) => {
  currentPage.value = page;
  fetchProducts();
};

const viewProductDetails = (productId) => {
  // 跳转到商品详情页
  router.push(`/product/${productId}`);
};

const approveProduct = async (productId) => {
  if (confirm('确定要审核通过该商品吗？')) {
    try {
      await api.patch('/admin/products/', {
        product_id: productId,
        action: 'approve'
      });
      // 重新获取商品列表
      fetchProducts();
      alert('商品审核通过');
    } catch (error) {
      console.error('审核通过商品失败:', error);
      alert('审核通过商品失败，请检查网络连接或权限');
    }
  }
};

const rejectProduct = async (productId) => {
  if (confirm('确定要拒绝该商品吗？')) {
    try {
      await api.patch('/admin/products/', {
        product_id: productId,
        action: 'reject'
      });
      // 重新获取商品列表
      fetchProducts();
      alert('商品已拒绝');
    } catch (error) {
      console.error('拒绝商品失败:', error);
      alert('拒绝商品失败，请检查网络连接或权限');
    }
  }
};

const removeProduct = async (productId) => {
  if (confirm('确定要下架该商品吗？')) {
    try {
      await api.patch('/admin/products/', {
        product_id: productId,
        action: 'remove'
      });
      // 重新获取商品列表
      fetchProducts();
      alert('商品已下架');
    } catch (error) {
      console.error('下架商品失败:', error);
      alert('下架商品失败，请检查网络连接或权限');
    }
  }
};

const deleteProduct = async (productId) => {
  if (confirm('确定要删除该商品记录吗？此操作不可恢复！')) {
    try {
      await api.patch('/admin/products/', {
        product_id: productId,
        action: 'delete'
      });
      // 重新获取商品列表
      fetchProducts();
      alert('商品记录已删除');
    } catch (error) {
      console.error('删除商品失败:', error);
      alert('删除商品失败，请检查网络连接或权限');
    }
  }
};

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审核',
    approved: '已上架',
    rejected: '已拒绝',
    sold_out: '已售罄',
    removed: '已下架'
  };
  return statusMap[status] || status;
};

const getCategoryName = (category) => {
  const categoryMap = {
    'books': '图书教材',
    'electronics': '电子数码',
    'sports': '运动户外',
    'clothing': '服装鞋包',
    'other': '其他',
    '时尚首饰': '时尚首饰',
    '零食饮料': '零食饮料',
    '美妆护肤': '美妆护肤',
    '家居日用': '家居日用',
    '卡包劵包': '卡包劵包'
  };
  return categoryMap[category] || category;
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 定时器，用于自动刷新商品列表
let refreshTimer = null;

onMounted(() => {
  fetchProducts();
  // 设置定时器，每30秒自动刷新一次商品列表
  refreshTimer = setInterval(() => {
    fetchProducts();
  }, 30000);
});

onUnmounted(() => {
  // 清除定时器
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
});
</script>

<style scoped>
.product-management {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: center;
}



.search {
  flex: 1;
  min-width: 300px;
  display: flex;
  gap: 10px;
}

.search input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #7f8c8d 0%, #6c757d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.product-list {
  overflow-x: auto;
}

.product-list table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.product-list th,
.product-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.product-list th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.product-list tr:hover {
  background-color: #f5f5f5;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.sold_out {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-badge.removed {
  background-color: #e2e3e5;
  color: #383d41;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>