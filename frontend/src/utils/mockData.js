/**
 * 集中 mock 数据 —— 模拟管理员账户近7天真实操作数据
 * 所有日期基于当前日期动态生成，保证演示时永远显示"最近7天"
 */

/* ─── 日期工具 ─── */
function daysAgo(n, time = '00:00:00') {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10) + ' ' + time
}
function dateOnly(n) { return daysAgo(n).slice(0, 10) }

/* ─── 用户 ─── */
export const mockUsers = [
  {
    id: 1,
    username: 'admin',
    password: 'admin123',
    nickname: '系统管理员',
    email: 'admin@example.com',
    role: 'admin',
    createdAt: '2026-01-01'
  },
  {
    id: 2,
    username: 'demo',
    password: 'demo123',
    nickname: '演示用户',
    email: 'demo@example.com',
    role: 'user',
    createdAt: '2026-02-15'
  }
]

/* ─── 文本数据（近7天陆续上传，共18篇） ─── */
export const mockTexts = [
  { id: 1,  title: '新能源汽车市场分析报告',     content: '2025年新能源汽车市场持续高速增长，渗透率突破40%。', category: '科技', wordCount: 1240, status: 'active', createdAt: daysAgo(6, '09:12:33'), updatedAt: daysAgo(6, '09:12:33') },
  { id: 2,  title: '大模型技术发展趋势综述',     content: 'GPT-4o、Claude 3.5等大模型在推理能力上取得重大突破。', category: '科技', wordCount: 980,  status: 'active', createdAt: daysAgo(6, '10:45:20'), updatedAt: daysAgo(6, '10:45:20') },
  { id: 3,  title: '全球通货膨胀与货币政策研究', content: '美联储在2025年完成三次降息，联邦基金利率降至4.25%。', category: '经济', wordCount: 1560, status: 'active', createdAt: daysAgo(5, '08:30:00'), updatedAt: daysAgo(5, '08:30:00') },
  { id: 4,  title: '碳中和目标下的能源转型路径', content: '中国2060碳中和目标推动能源结构深度调整，光伏风电装机量创历史新高。', category: '环境', wordCount: 1380, status: 'active', createdAt: daysAgo(5, '14:22:10'), updatedAt: daysAgo(5, '14:22:10') },
  { id: 5,  title: '人工智能伦理与监管框架探讨', content: 'EU AI Act正式生效，对高风险AI系统提出严格合规要求。', category: '政策', wordCount: 1120, status: 'active', createdAt: daysAgo(5, '16:05:44'), updatedAt: daysAgo(5, '16:05:44') },
  { id: 6,  title: '量子计算商业化应用前景分析', content: 'IBM、Google等量子计算公司发布超过1000量子比特的处理器。', category: '科技', wordCount: 1050, status: 'active', createdAt: daysAgo(4, '09:00:00'), updatedAt: daysAgo(4, '09:00:00') },
  { id: 7,  title: '房地产市场深度调整与政策应对', content: '一线城市房价在政策托底下企稳，二三线城市去库存压力仍大。', category: '经济', wordCount: 1320, status: 'active', createdAt: daysAgo(4, '11:30:15'), updatedAt: daysAgo(4, '11:30:15') },
  { id: 8,  title: '生物医药创新药研发现状',     content: 'ADC药物成为全球医药研发最热赛道，国内药企出海授权交易屡创新高。', category: '医疗', wordCount: 890,  status: 'active', createdAt: daysAgo(4, '15:18:00'), updatedAt: daysAgo(4, '15:18:00') },
  { id: 9,  title: '半导体产业链国产替代进展',   content: '中芯国际7nm工艺良率持续提升，华为麒麟芯片量产验证国产先进制程可行性。', category: '科技', wordCount: 1450, status: 'active', createdAt: daysAgo(3, '08:45:00'), updatedAt: daysAgo(3, '08:45:00') },
  { id: 10, title: '数字人民币推广与金融科技创新', content: '数字人民币试点城市扩展至全国主要城市，累计交易额突破万亿元。', category: '经济', wordCount: 760,  status: 'active', createdAt: daysAgo(3, '10:20:30'), updatedAt: daysAgo(3, '10:20:30') },
  { id: 11, title: '气候变化对农业生产的影响评估', content: '极端天气频发导致全球粮食产量波动加剧，粮食安全问题重回国际议程核心。', category: '环境', wordCount: 1180, status: 'active', createdAt: daysAgo(3, '14:00:00'), updatedAt: daysAgo(3, '14:00:00') },
  { id: 12, title: '元宇宙产业发展现状与反思',   content: 'Meta大幅削减元宇宙投入，但工业元宇宙在制造业的应用价值逐步得到验证。', category: '科技', wordCount: 920,  status: 'active', createdAt: daysAgo(2, '09:30:00'), updatedAt: daysAgo(2, '09:30:00') },
  { id: 13, title: '全球供应链重构与产业转移趋势', content: '中国+1战略推动制造业向东南亚、印度、墨西哥转移。', category: '经济', wordCount: 1340, status: 'active', createdAt: daysAgo(2, '11:15:00'), updatedAt: daysAgo(2, '11:15:00') },
  { id: 14, title: '脑机接口技术伦理与监管挑战', content: 'Neuralink完成首例人体植入手术，BCI技术从实验室走向临床。', category: '医疗', wordCount: 1060, status: 'active', createdAt: daysAgo(2, '15:40:00'), updatedAt: daysAgo(2, '15:40:00') },
  { id: 15, title: '教育数字化转型与AI辅助教学', content: 'AI家教、智能批改、个性化学习路径等应用在K12教育领域快速普及。', category: '教育', wordCount: 840,  status: 'active', createdAt: daysAgo(1, '08:00:00'), updatedAt: daysAgo(1, '08:00:00') },
  { id: 16, title: '城市智能交通系统建设实践',   content: '北京、上海、深圳等城市加速推进车路云一体化建设，自动驾驶商业化运营区域持续扩大。', category: '科技', wordCount: 1100, status: 'active', createdAt: daysAgo(1, '10:30:00'), updatedAt: daysAgo(1, '10:30:00') },
  { id: 17, title: '网络安全威胁态势与防御策略', content: '勒索软件攻击持续高发，AI驱动的网络攻击手段更加隐蔽。', category: '政策', wordCount: 1280, status: 'active', createdAt: daysAgo(0, '09:00:00'), updatedAt: daysAgo(0, '09:00:00') },
  { id: 18, title: '老龄化社会养老服务体系构建', content: '中国60岁以上人口占比突破20%，养老服务供给缺口巨大。', category: '社会', wordCount: 970,  status: 'active', createdAt: daysAgo(0, '11:20:00'), updatedAt: daysAgo(0, '11:20:00') }
]
