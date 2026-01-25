# 动态推荐系统实现总结

## 📋 实现概述

成功实现了基于用户行为的动态推荐系统，使用"静态电影向量 + 动态用户向量"方案，让首页推荐能随用户交互实时调整。

## ✅ 完成的步骤

### Step 1: 用户行为追踪模块
**文件**: `d:/code/vue/movie_ai/src/recommendation/user_behavior.py`

**核心功能**:
- ✅ 记录用户行为（点击、观看、收藏、评分、分享等）
- ✅ 时间衰减机制（30天，可配置）
- ✅ 动态计算用户向量
- ✅ 行为历史查询

**行为类型及权重**:
```python
ACTION_WEIGHTS = {
    'like': 1.0,             # 👍 喜欢 - 最高权重
    'favorite': 0.8,         # ⭐ 收藏
    'rate_high': 0.7,        # 高评分 (8-10分)
    'rate_medium': 0.5,      # 中评分 (5-7分)
    'rate_low': 0.3,        # 低评分 (1-4分)
    'click': 0.3,           # 👆 点击 - 最低权重
    'view': 0.3,            # 观看
    'watch': 0.6,           # 完整观看
    'share': 0.6,           # 📤 分享
    'comment': 0.5,         # 💬 评论
}
```

### Step 2: 增强 LightGCN 推荐器
**文件**: `d:/code/vue/movie_ai/src/recommendation/lightgcn.py`

**增强内容**:
- ✅ 集成用户行为追踪器
- ✅ 新增 `record_user_behavior()` 方法
- ✅ 新增 `_recommend_dynamic()` 方法
- ✅ 修改 `recommend()` 方法支持动态推荐
- ✅ 支持静态/动态两种推荐模式

### Step 3: 集成到 Flask API
**文件**:
- `d:/code/vue/movie_back/src/routes/recommendation_routes.py` - 路由层
- `d:/code/vue/movie_back/src/viewmodels/recommendation_viewmodel.py` - 业务逻辑层
- `d:/code/vue/movie_back/src/app.py` - 应用注册

**提供的 API 接口**:

#### 1. 获取个性化推荐
```
GET /api/recommendation/personalized
参数: user_id, top_k, use_dynamic
```

#### 2. 记录用户行为
```
POST /api/recommendation/behavior
Body: { user_id, movie_id, behavior_type, metadata }
```

#### 3. 批量记录行为
```
POST /api/recommendation/behavior/batch
Body: { behaviors: [...] }
```

#### 4. 获取用户行为历史
```
GET /api/recommendation/user/history
参数: user_id, limit, behavior_type
```

#### 5. 获取相似电影
```
GET /api/recommendation/similar-movies/<movie_id>
参数: top_k
```

#### 6. 获取统计信息
```
GET /api/recommendation/statistics
```

#### 7. 获取热门电影
```
GET /api/recommendation/hot
参数: top_k
```

## 🎯 技术特点

### 1. 静态电影向量
- 使用预训练的 LightGCN 模型生成
- 包含电影的内容特征和协同过滤信息
- 不随时间变化，计算高效

### 2. 动态用户向量
- 基于用户行为实时计算
- 考虑行为类型权重
- 支持时间衰减（近期行为权重更高）
- 随用户交互持续更新

### 3. 时间衰减机制
- 默认30天衰减期
- 超过30天的行为影响力降为0
- 可自定义衰减天数

### 4. 评分映射
- 前端使用0-10分制
- 自动映射到三个等级:
  - 8-10分 → `rate_high` (权重0.7)
  - 5-7分 → `rate_medium` (权重0.5)
  - 1-4分 → `rate_low` (权重0.3)

## 📊 工作流程

```
用户交互 → 记录行为 → 计算动态用户向量 → 匹配静态电影向量 → 返回个性化推荐
    ↓
时间衰减 → 过期行为自动清理
```

## 🔧 使用示例

### 前端调用示例

```javascript
// 记录用户点击
await fetch('/api/recommendation/behavior', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 1,
    movie_id: 10,
    behavior_type: 'click'
  })
})

// 记录评分
await fetch('/api/recommendation/behavior', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 1,
    movie_id: 10,
    behavior_type: 'rate',
    metadata: { rating: 9 }  // 0-10分
  })
})

// 获取个性化推荐
const response = await fetch('/api/recommendation/personalized?user_id=1&top_k=10&use_dynamic=true')
const { data } = await response.json()
console.log(data.recommendations)
```

### Python 后端调用示例

```python
from src.viewmodels.recommendation_viewmodel import recommendation_viewmodel

# 记录用户行为
recommendation_viewmodel.record_user_behavior(
    user_id=1,
    movie_id=10,
    behavior_type='favorite'
)

# 获取个性化推荐
recommendations = recommendation_viewmodel.get_personalized_recommendations(
    user_id=1,
    top_k=10,
    use_dynamic=True
)

# 查看统计信息
stats = recommendation_viewmodel.get_statistics()
print(f"总用户数: {stats['total_users']}")
print(f"总行为数: {stats['total_behaviors']}")
```

## 📁 文件清单

### 核心文件
- `movie_ai/src/recommendation/user_behavior.py` - 用户行为追踪模块
- `movie_ai/src/recommendation/lightgcn.py` - LightGCN 推荐器（已增强）

### API 文件
- `movie_back/src/routes/recommendation_routes.py` - 推荐路由
- `movie_back/src/viewmodels/recommendation_viewmodel.py` - 推荐业务逻辑
- `movie_back/src/app.py` - 应用入口（已注册推荐路由）

### 测试文件
- `movie_back/scripts/test_dynamic_recommendation.py` - 测试脚本

### 文档
- `movie_ai/docs/dynamic_recommendation_summary.md` - 本文档

## 🧪 测试

运行测试脚本验证功能:

```bash
cd d:/code/vue/movie_back
python scripts/test_dynamic_recommendation.py
```

测试覆盖:
- ✅ 推荐系统状态检查
- ✅ 获取热门电影
- ✅ 记录用户行为
- ✅ 获取行为历史
- ✅ 静态推荐
- ✅ 动态推荐
- ✅ 查找相似电影
- ✅ 统计信息查询

## 🎉 总结

成功实现了完整的动态推荐系统，主要优势：

1. **实时性**: 用户行为立即影响推荐结果
2. **个性化**: 基于个体行为历史，提供精准推荐
3. **灵活性**: 支持静态/动态两种模式切换
4. **可扩展**: 易于添加新的行为类型
5. **高效性**: 静态电影向量 + 动态用户向量，计算高效
6. **智能性**: 时间衰减机制，推荐更贴合用户当前兴趣

系统已完全集成到 Flask API，前端可以直接调用接口实现动态推荐功能！
