/**
 * meei Dashboard
 */

// 讀取 usage 資料 (從 ~/.meei/usage.json)
async function loadUsage() {
  // 在瀏覽器環境中，需要透過 API 取得資料
  // 這裡先用假資料示範
  return getMockData();
}

function getMockData() {
  return {
    records: [
      { timestamp: '2024-01-14T10:30:00Z', provider: 'deepseek', model: 'deepseek-chat', input_tokens: 150, output_tokens: 300, cost: 0.0001, latency_ms: 1200, prompt: '你好，請介紹一下你自己' },
      { timestamp: '2024-01-14T10:25:00Z', provider: 'openai', model: 'gpt-4o-mini', input_tokens: 200, output_tokens: 500, cost: 0.0003, latency_ms: 2100, prompt: '寫一個快速排序演算法' },
      { timestamp: '2024-01-14T10:20:00Z', provider: 'gemini', model: 'gemini-1.5-flash', input_tokens: 100, output_tokens: 200, cost: 0.00005, latency_ms: 800, prompt: '什麼是機器學習？' },
      { timestamp: '2024-01-14T10:15:00Z', provider: 'deepseek', model: 'deepseek-coder', input_tokens: 300, output_tokens: 800, cost: 0.0003, latency_ms: 1500, prompt: '用 Python 寫一個網頁爬蟲' },
      { timestamp: '2024-01-14T10:10:00Z', provider: 'qwen', model: 'qwen-turbo', input_tokens: 80, output_tokens: 150, cost: 0.00002, latency_ms: 600, prompt: '翻譯：Hello World' },
    ],
    total_cost: 0.00077
  };
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

function formatCost(cost) {
  if (cost < 0.01) return '$' + cost.toFixed(4);
  return '$' + cost.toFixed(2);
}

function timeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diff = Math.floor((now - then) / 1000);

  if (diff < 60) return '剛剛';
  if (diff < 3600) return Math.floor(diff / 60) + ' 分鐘前';
  if (diff < 86400) return Math.floor(diff / 3600) + ' 小時前';
  return Math.floor(diff / 86400) + ' 天前';
}

function renderDashboard(data) {
  const { records, total_cost } = data;

  // 計算統計
  const totalTokens = records.reduce((sum, r) => sum + (r.input_tokens || 0) + (r.output_tokens || 0), 0);
  const totalRequests = records.length;
  const avgLatency = records.length > 0
    ? Math.round(records.reduce((sum, r) => sum + (r.latency_ms || 0), 0) / records.length)
    : 0;

  // Provider 統計
  const providerStats = {};
  for (const r of records) {
    if (!providerStats[r.provider]) {
      providerStats[r.provider] = { count: 0, cost: 0 };
    }
    providerStats[r.provider].count++;
    providerStats[r.provider].cost += r.cost || 0;
  }

  // 更新統計卡片
  document.getElementById('total-cost').textContent = formatCost(total_cost);
  document.getElementById('total-tokens').textContent = formatNumber(totalTokens);
  document.getElementById('total-requests').textContent = totalRequests;
  document.getElementById('avg-latency').textContent = avgLatency + 'ms';

  // 更新 Provider 分布
  const maxCount = Math.max(...Object.values(providerStats).map(s => s.count), 1);
  const providerBars = document.getElementById('provider-bars');
  providerBars.innerHTML = '';

  const providers = ['deepseek', 'openai', 'gemini', 'qwen', 'grok'];
  for (const pv of providers) {
    const stats = providerStats[pv] || { count: 0, cost: 0 };
    const percentage = (stats.count / maxCount) * 100;

    providerBars.innerHTML += `
      <div class="provider-bar">
        <span class="name">${pv}</span>
        <div class="bar">
          <div class="bar-fill ${pv}" style="width: ${percentage}%"></div>
        </div>
        <span class="count">${stats.count} 次</span>
      </div>
    `;
  }

  // 更新最近請求
  const requestList = document.getElementById('request-list');
  if (records.length === 0) {
    requestList.innerHTML = '<div class="empty-state">尚無請求記錄</div>';
  } else {
    requestList.innerHTML = records.slice(0, 10).map(r => `
      <div class="request-item">
        <span class="provider-tag ${r.provider}">${r.provider}</span>
        <span class="prompt">${r.prompt || '(no prompt)'}</span>
        <div class="meta">
          <span>${formatNumber((r.input_tokens || 0) + (r.output_tokens || 0))} tokens</span>
          <span>${r.latency_ms}ms</span>
          <span>${timeAgo(r.timestamp)}</span>
        </div>
      </div>
    `).join('');
  }

  // 更新時間
  document.getElementById('last-updated').textContent = '更新於 ' + new Date().toLocaleTimeString();
}

// 初始化
async function init() {
  const data = await loadUsage();
  renderDashboard(data);

  // 每 30 秒更新
  setInterval(async () => {
    const data = await loadUsage();
    renderDashboard(data);
  }, 30000);
}

init();
