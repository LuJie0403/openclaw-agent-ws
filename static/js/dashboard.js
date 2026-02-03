// 全局变量
let monthlyChart = null;
let categoryChart = null;
let currentYear = new Date().getFullYear();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadInitialData();
});

// 初始化仪表板
function initializeDashboard() {
    // 设置当前日期
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('zh-CN');
    
    // 设置统计年份
    document.getElementById('stats-year').textContent = currentYear;
    
    // 初始化图表
    initializeCharts();
    
    // 绑定事件监听器
    bindEventListeners();
}

// 初始化图表
function initializeCharts() {
    // 月度趋势图表
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '月度支出',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '¥' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    
    // 分类占比图表
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c',
                    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                    '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// 绑定事件监听器
function bindEventListeners() {
    // 年份选择器变化事件
    document.getElementById('yearSelect').addEventListener('change', function() {
        const year = this.value;
        if (year) {
            loadMonthlyStats(parseInt(year));
        } else {
            loadMonthlyStats();
        }
    });
    
    // 分类选择器变化事件
    document.getElementById('categorySelect').addEventListener('change', function() {
        const category = this.value;
        loadTrendData(category);
    });
    
    // 日期筛选器变化事件
    document.getElementById('startDate').addEventListener('change', applyFilters);
    document.getElementById('endDate').addEventListener('change', applyFilters);
}

// 加载初始数据
async function loadInitialData() {
    try {
        // 并行加载所有数据
        await Promise.all([
            loadMonthlyStats(),
            loadCategoryAnalysis(),
            loadRecentExpenses(),
            loadYearlyStats(),
            loadFilters()
        ]);
        
        console.log('所有数据加载完成');
    } catch (error) {
        console.error('加载数据失败:', error);
        showError('数据加载失败，请稍后重试');
    }
}

// 加载月度统计数据
async function loadMonthlyStats(year = null) {
    try {
        const url = year ? `/api/monthly-stats?year=${year}` : '/api/monthly-stats';
        const response = await fetch(url);
        
        if (!response.ok) throw new Error('获取月度统计数据失败');
        
        const data = await response.json();
        updateMonthlyChart(data);
        updateStatsCards(data);
        
    } catch (error) {
        console.error('加载月度统计数据失败:', error);
        showError('加载月度统计数据失败');
    }
}

// 加载分类分析数据
async function loadCategoryAnalysis() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        let url = '/api/category-analysis';
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('获取分类分析数据失败');
        
        const data = await response.json();
        updateCategoryChart(data);
        updateCategoryTable(data);
        
    } catch (error) {
        console.error('加载分类分析数据失败:', error);
        showError('加载分类分析数据失败');
    }
}

// 加载最近支出记录
async function loadRecentExpenses(limit = 10) {
    try {
        const response = await fetch(`/api/recent-expenses?limit=${limit}`);
        if (!response.ok) throw new Error('获取最近支出记录失败');
        
        const data = await response.json();
        updateRecentTable(data);
        
    } catch (error) {
        console.error('加载最近支出记录失败:', error);
        showError('加载最近支出记录失败');
    }
}

// 加载年度统计数据
async function loadYearlyStats() {
    try {
        const response = await fetch('/api/yearly-stats');
        if (!response.ok) throw new Error('获取年度统计数据失败');
        
        const data = await response.json();
        updateYearSelect(data);
        
    } catch (error) {
        console.error('加载年度统计数据失败:', error);
    }
}

// 加载筛选器数据
async function loadFilters() {
    try {
        // 这里可以加载分类列表等筛选数据
        const categories = await loadCategories();
        updateCategorySelect(categories);
        
    } catch (error) {
        console.error('加载筛选器数据失败:', error);
    }
}

// 加载分类列表
async function loadCategories() {
    try {
        const response = await fetch('/api/category-analysis');
        if (!response.ok) throw new Error('获取分类列表失败');
        
        const data = await response.json();
        return data.map(item => item.category);
        
    } catch (error) {
        console.error('加载分类列表失败:', error);
        return [];
    }
}

// 加载趋势数据
async function loadTrendData(category = null, days = 365) {
    try {
        let url = `/api/trend-data?days=${days}`;
        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('获取趋势数据失败');
        
        const data = await response.json();
        // 这里可以更新趋势图表
        console.log('趋势数据:', data);
        
    } catch (error) {
        console.error('加载趋势数据失败:', error);
    }
}

// 更新月度图表
function updateMonthlyChart(data) {
    if (!monthlyChart || !data || data.length === 0) return;
    
    const labels = data.map(item => item.month);
    const values = data.map(item => parseFloat(item.total_amount));
    
    monthlyChart.data.labels = labels;
    monthlyChart.data.datasets[0].data = values;
    monthlyChart.update('active');
}

// 更新分类图表
function updateCategoryChart(data) {
    if (!categoryChart || !data || data.length === 0) return;
    
    const labels = data.map(item => item.category);
    const values = data.map(item => parseFloat(item.total_amount));
    
    categoryChart.data.labels = labels;
    categoryChart.data.datasets[0].data = values;
    categoryChart.update('active');
}

// 更新分类表格
function updateCategoryTable(data) {
    const tbody = document.querySelector('#categoryTable tbody');
    if (!tbody || !data) return;
    
    tbody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="badge bg-primary">${item.category}</span></td>
            <td>¥${parseFloat(item.total_amount).toLocaleString()}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar" style="width: ${item.percentage}%"></div>
                </div>
                <small class="text-muted">${item.percentage}%</small>
            </td>
            <td>${item.transaction_count}</td>
        `;
        tbody.appendChild(row);
    });
}

// 更新最近支出表格
function updateRecentTable(data) {
    const tbody = document.querySelector('#recentTable tbody');
    if (!tbody || !data) return;
    
    tbody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        const date = new Date(item.expense_date).toLocaleDateString('zh-CN');
        
        row.innerHTML = `
            <td>${date}</td>
            <td><span class="badge bg-info">${item.category}</span></td>
            <td>¥${parseFloat(item.amount).toLocaleString()}</td>
            <td>${item.description || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// 更新统计卡片
function updateStatsCards(data) {
    if (!data || data.length === 0) return;
    
    // 计算当前月份数据
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM格式
    const currentMonthData = data.find(item => item.month === currentMonth);
    
    if (currentMonthData) {
        document.getElementById('current-month-total').textContent = 
            '¥' + parseFloat(currentMonthData.total_amount).toLocaleString();
    }
    
    // 计算平均值
    const totalAmount = data.reduce((sum, item) => sum + parseFloat(item.total_amount), 0);
    const avgAmount = totalAmount / data.length;
    
    document.getElementById('avg-monthly').textContent = '¥' + Math.round(avgAmount).toLocaleString();
    
    // 计算总笔数
    const totalTransactions = data.reduce((sum, item) => sum + parseInt(item.transaction_count), 0);
    document.getElementById('total-transactions').textContent = totalTransactions.toLocaleString();
}

// 更新年份选择器
function updateYearSelect(data) {
    const select = document.getElementById('yearSelect');
    if (!select || !data) return;
    
    const years = [...new Set(data.map(item => item.year))].sort((a, b) => b - a);
    
    select.innerHTML = '<option value="">全部年份</option>';
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        select.appendChild(option);
    });
}

// 更新分类选择器
function updateCategorySelect(categories) {
    const select = document.getElementById('categorySelect');
    if (!select || !categories) return;
    
    select.innerHTML = '<option value="">全部分类</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
    });
}

// 应用筛选器
function applyFilters() {
    loadCategoryAnalysis();
    loadRecentExpenses();
}

// 重置筛选器
function resetFilters() {
    document.getElementById('yearSelect').value = '';
    document.getElementById('categorySelect').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    
    loadInitialData();
}

// 导出数据
async function exportData(dataType, format) {
    try {
        const url = `/export/${format}?type=${dataType}`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error('导出数据失败');
        
        // 创建下载链接
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'export.' + format;
        
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        showSuccess('数据导出成功');
        
    } catch (error) {
        console.error('导出数据失败:', error);
        showError('导出数据失败');
    }
}

// 更新月度图表（刷新按钮）
function updateMonthlyChart() {
    const year = document.getElementById('yearSelect').value;
    loadMonthlyStats(year ? parseInt(year) : null);
}

// 显示错误消息
function showError(message) {
    // 这里可以实现一个更友好的错误提示
    alert('错误: ' + message);
}

// 显示成功消息
function showSuccess(message) {
    // 这里可以实现一个更友好的成功提示
    console.log('成功: ' + message);
}

// 工具函数：格式化货币
function formatCurrency(amount) {
    return '¥' + parseFloat(amount).toLocaleString();
}

// 工具函数：格式化百分比
function formatPercentage(value) {
    return parseFloat(value).toFixed(2) + '%';
}

// 工具函数：防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 添加一些动画效果
document.addEventListener('DOMContentLoaded', function() {
    // 为统计卡片添加渐入动画
    const cards = document.querySelectorAll('.stats-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // 为表格行添加悬停效果
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('tr')) {
            e.target.closest('tr').classList.add('table-active');
        }
    });
    
    document.addEventListener('mouseout', function(e) {
        if (e.target.closest('tr')) {
            e.target.closest('tr').classList.remove('table-active');
        }
    });
});