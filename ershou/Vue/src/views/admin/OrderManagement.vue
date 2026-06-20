<template>
  <div class="order-management">
    <h2>订单管理</h2>
    
    <!-- 搜索和筛选区域 -->
    <div class="search-filter-bar">
      <div class="search">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索订单ID或商品名称"
          @input="fetchOrders"
        />
        <button class="btn-primary">搜索</button>
      </div>
      <div class="filter">
        <select v-model="statusFilter" @change="fetchOrders">
          <option value="">所有状态</option>
          <option value="ongoing">进行中</option>
          <option value="completed">已完成</option>
          <option value="returned">已退货</option>
        </select>
      </div>
    </div>
    
    <!-- 订单列表 -->
    <div class="order-list">
      <table>
        <thead>
          <tr>
            <th>订单ID</th>
            <th>商品名称</th>
            <th>买家</th>
            <th>卖家</th>
            <th>价格</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.product_title }}</td>
            <td>{{ order.buyer_username }}</td>
            <td>{{ order.seller_username }}</td>
            <td>¥{{ order.price }}</td>
            <td>
              <span :class="['status-badge', order.status]">
                {{ getStatusText(order.status) }}
              </span>
            </td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>
              <button class="btn-danger" @click="deleteOrder(order.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 空状态 -->
    <div v-if="orders.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p>暂无订单</p>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../axios';

const orders = ref([]);
const searchQuery = ref('');
const statusFilter = ref('');
const loading = ref(false);

const fetchOrders = async () => {
  loading.value = true;
  try {
    const params = {
      search: searchQuery.value,
      status: statusFilter.value
    };
    
    const response = await api.get('/admin/orders/', { params });
    orders.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取订单列表失败:', error);
    orders.value = [];
  } finally {
    loading.value = false;
  }
};

const deleteOrder = async (orderId) => {
  if (confirm('确定要删除该订单吗？此操作将影响数据统计中的总销售额。')) {
    try {
      await api.delete(`/admin/orders/${orderId}/`);
      // 重新获取订单列表
      fetchOrders();
      alert('订单已删除');
    } catch (error) {
      console.error('删除订单失败:', error);
      alert('删除订单失败，请检查网络连接或权限');
    }
  }
};

const getStatusText = (status) => {
  const statusMap = {
    ongoing: '进行中',
    completed: '已完成',
    returned: '已退货'
  };
  return statusMap[status] || status;
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
.order-management {
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
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
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
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.order-list {
  overflow-x: auto;
}

.order-list table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.order-list th,
.order-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.order-list th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.order-list tr:hover {
  background-color: #f5f5f5;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.ongoing {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.returned {
  background-color: #f8d7da;
  color: #721c24;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 18px;
  color: #666;
  margin: 0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  margin: 0;
}

@media (max-width: 768px) {
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search {
    min-width: auto;
  }
  
  .order-list table {
    font-size: 12px;
  }
  
  .order-list th,
  .order-list td {
    padding: 8px;
  }
}
</style>