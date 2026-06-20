<template>
  <div class="statistics-management">
    <h2>数据统计</h2>
    
    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <div class="card-title">总用户数</div>
        <div class="card-value">{{ statistics.total_users }}</div>
        <div class="card-change" :class="{ positive: statistics.user_growth > 0 }">
          {{ statistics.user_growth > 0 ? '+' : '' }}{{ statistics.user_growth }}% 较上周
        </div>
      </div>
      <div class="card">
        <div class="card-title">总商品数</div>
        <div class="card-value">{{ statistics.total_products }}</div>
        <div class="card-change" :class="{ positive: statistics.product_growth > 0 }">
          {{ statistics.product_growth > 0 ? '+' : '' }}{{ statistics.product_growth }}% 较上周
        </div>
      </div>
      <div class="card">
        <div class="card-title">总订单数</div>
        <div class="card-value">{{ statistics.total_orders }}</div>
        <div class="card-change" :class="{ positive: statistics.order_growth > 0 }">
          {{ statistics.order_growth > 0 ? '+' : '' }}{{ statistics.order_growth }}% 较上周
        </div>
      </div>
      <div class="card">
        <div class="card-title">总销售额</div>
        <div class="card-value">¥{{ statistics.total_sales }}</div>
        <div class="card-change" :class="{ positive: statistics.sales_growth > 0 }">
          {{ statistics.sales_growth > 0 ? '+' : '' }}{{ statistics.sales_growth }}% 较上周
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts">
      <div class="chart-item">
        <h3>销售额趋势</h3>
        <div ref="salesChart" class="chart-container"></div>
      </div>
      <div class="chart-item">
        <h3>商品分类分布</h3>
        <div ref="categoryChart" class="chart-container"></div>
      </div>
    </div>
    
    <!-- 详细统计表格 -->
    <div class="detailed-statistics">
      <h3>每日统计详情</h3>
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>新增用户</th>
            <th>新增商品</th>
            <th>订单数</th>
            <th>销售额</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="day in dailyStatistics" :key="day.date">
            <td>{{ day.date }}</td>
            <td>{{ day.new_users }}</td>
            <td>{{ day.new_products }}</td>
            <td>{{ day.orders }}</td>
            <td>¥{{ day.sales }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../axios';
import * as echarts from 'echarts';

const statistics = ref({
  total_users: 0,
  user_growth: 0,
  total_products: 0,
  product_growth: 0,
  total_orders: 0,
  order_growth: 0,
  total_sales: 0,
  sales_growth: 0
});
const salesTrend = ref([]);
const categoryDistribution = ref([]);
const dailyStatistics = ref([]);
const salesChart = ref(null);
const categoryChart = ref(null);
const salesChartInstance = ref(null);
const categoryChartInstance = ref(null);

// 分类名称映射函数
const getCategoryName = (category) => {
  const categoryMap = {
    'books': '图书教材',
    'electronics': '电子数码',
    'sports': '运动户外',
    'clothing': '服装鞋包',
    'other': '其他',
    'home': '家居日用',
    'cards': '卡包劵包',
    'jewelry': '时尚首饰',
    'beauty': '美妆护肤',
    'food': '零食饮料',
    '时尚首饰': '时尚首饰',
    '零食饮料': '零食饮料',
    '美妆护肤': '美妆护肤',
    '家居日用': '家居日用',
    '卡包劵包': '卡包劵包'
  };
  return categoryMap[category] || category;
};

const fetchStatistics = async () => {
  try {
    const response = await api.get('/admin/statistics/');
    statistics.value = response.data;
    salesTrend.value = response.data.sales_trend;
    categoryDistribution.value = response.data.category_distribution;
    dailyStatistics.value = response.data.daily_statistics;
    renderCharts();
  } catch (error) {
    console.error('获取统计数据失败:', error);
    // 使用真实的0值数据，而不是模拟数据
    statistics.value = {
      total_users: 0,
      user_growth: 0,
      total_products: 0,
      product_growth: 0,
      total_orders: 0,
      order_growth: 0,
      total_sales: 0,
      sales_growth: 0
    };
    salesTrend.value = [];
    categoryDistribution.value = [];
    dailyStatistics.value = [];
    renderCharts();
  }
};

const renderCharts = () => {
  // 渲染销售额趋势折线图
  if (salesChart.value) {
    if (!salesChartInstance.value) {
      salesChartInstance.value = echarts.init(salesChart.value);
    }
    const salesOption = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: salesTrend.value.map(item => item.label)
      },
      yAxis: {
        type: 'value',
        name: '销售额'
      },
      series: [{
        data: salesTrend.value.map(item => item.value),
        type: 'line',
        smooth: true,
        lineStyle: {
          color: '#3498db'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(52, 152, 219, 0.5)'
            },
            {
              offset: 1,
              color: 'rgba(52, 152, 219, 0.1)'
            }
          ])
        }
      }]
    };
    salesChartInstance.value.setOption(salesOption);
  }
  
  // 渲染商品分类分布柱形图
  if (categoryChart.value) {
    if (!categoryChartInstance.value) {
      categoryChartInstance.value = echarts.init(categoryChart.value);
    }
    const categoryOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: categoryDistribution.value.map(item => getCategoryName(item.name)),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '商品数量'
      },
      series: [{
        data: categoryDistribution.value.map(item => item.count),
        type: 'bar',
        itemStyle: {
          color: function(params) {
            const colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e', '#95a5a6', '#f1c40f', '#e67e22'];
            return colors[params.dataIndex % colors.length];
          }
        }
      }]
    };
    categoryChartInstance.value.setOption(categoryOption);
  }
};

const handleResize = () => {
  renderCharts();
};

import { watchEffect, nextTick } from 'vue';

// 监听组件可见性，当切换到统计页面时重新获取数据
watchEffect(() => {
  // 检查组件是否可见
  const element = document.querySelector('.statistics-management');
  if (element) {
    nextTick(() => {
      fetchStatistics();
    });
  }
});

onMounted(() => {
  fetchStatistics();
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
});

// 组件卸载时移除事件监听
import { onUnmounted } from 'vue';
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.statistics-management {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  color: #fff;
}

.statistics-management h2 {
  font-size: 24px;
  margin-bottom: 30px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  border-radius: 12px 12px 0 0;
}

.card:nth-child(1)::before {
  background: linear-gradient(90deg, #3498db, #2980b9);
}

.card:nth-child(2)::before {
  background: linear-gradient(90deg, #2ecc71, #27ae60);
}

.card:nth-child(3)::before {
  background: linear-gradient(90deg, #f39c12, #e67e22);
}

.card:nth-child(4)::before {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 15px;
  font-weight: 600;
}

.card-value {
  font-size: 30px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 10px;
}

.card-change {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.card-change.positive {
  color: #27ae60;
  display: flex;
  align-items: center;
}

.card-change.positive::before {
  content: '↑';
  margin-right: 5px;
  font-size: 12px;
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.chart-item {
  background: rgba(255, 255, 255, 0.95);
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chart-item h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.chart-container {
  background: #fff;
  padding: 25px;
  border-radius: 8px;
  min-height: 320px;
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 响应式图表容器 */
@media (max-width: 768px) {
  .chart-container {
    min-height: 280px;
  }
}

@media (max-width: 480px) {
  .chart-container {
    min-height: 240px;
  }
}

.detailed-statistics {
  background: rgba(255, 255, 255, 0.95);
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  color: #333;
}

.detailed-statistics h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.detailed-statistics table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.detailed-statistics th,
.detailed-statistics td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.detailed-statistics th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
}

.detailed-statistics tr:hover {
  background-color: #f8f9fa;
}

.detailed-statistics tr:last-child td {
  border-bottom: none;
}

@media (max-width: 768px) {
  .statistics-management {
    padding: 20px;
  }
  
  .charts {
    grid-template-columns: 1fr;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .card {
    padding: 20px;
  }
  
  .chart-item {
    padding: 20px;
  }
  
  .chart-container {
    padding: 20px;
  }
  
  .detailed-statistics {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .statistics-management h2 {
    font-size: 20px;
  }
}
</style>