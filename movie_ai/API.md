# Movie AI API 文档

Movie AI 提供基于 RAG 的电影推荐服务，包括向量检索、BM25检索、混合检索和重排序功能。

## 基础信息

- **服务名称**: Movie AI RAG Service
- **默认地址**: http://localhost:5001
- **API 前缀**: `/ai`

## 接口列表

### 1. 健康检查

**接口**: `GET /ai/health`

**描述**: 检查服务是否正常运行

**响应示例**:
```json
{
  "success": true,
  "message": "Movie AI Service is running!",
  "service": "Movie AI RAG Service",
  "version": "1.0.0"
}
```

---

### 2. 电影推荐（完整响应）

**接口**: `POST /ai/recommend`

**描述**: 根据用户查询推荐电影，返回完整的检索、重排序和LLM生成结果

**请求体**:
```json
{
  "query": "我想看科幻电影",
  "top_k": 5,           // 可选，检索数量，默认5
  "rerank_top_n": 3     // 可选，重排序后返回数量，默认3
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "query": "我想看科幻电影",
    "rerank": {
      "results": [
        {
          "rank": 1,
          "title": "Star Wars (1977)",
          "movie_id": "50",
          "score": 0.95,
          "method": "rerank",
          "document": "...",
          "metadata": {...}
        }
      ],
      "top_n": 3
    },
    "recommended_movie_ids": ["50", "181", "89"],
    "llm_content": "根据您的喜好，我推荐以下科幻电影...",
    "timestamp": "2025-12-28T15:40:37.334555",
    "status": "success"
  }
}
```

---

### 3. 电影推荐（流式响应）

**接口**: `POST /ai/recommend/stream`

**描述**: 流式返回推荐结果，适合实时展示

**请求体**:
```json
{
  "query": "我想看科幻电影",
  "top_k": 5,
  "rerank_top_n": 3
}
```

**响应格式**: Server-Sent Events (SSE)

**事件类型**:

1. **retrieval** - 检索结果
```json
{
  "type": "retrieval",
  "data": {
    "rerank_results": [...],
    "recommended_movie_ids": ["50", "181", "89"]
  }
}
```

2. **llm_chunk** - LLM生成的内容片段
```json
{
  "type": "llm_chunk",
  "data": {
    "content": "根据您的"
  }
}
```

3. **complete** - 生成完成
```json
{
  "type": "complete",
  "data": {
    "query": "我想看科幻电影",
    "llm_content": "完整的推荐内容...",
    "timestamp": "2025-12-28T15:40:37.334555"
  }
}
```

4. **error** - 错误信息
```json
{
  "type": "error",
  "data": {
    "message": "错误描述"
  }
}
```

---

### 4. 向量检索

**接口**: `POST /ai/search/vector`

**描述**: 使用向量相似度检索电影

**请求体**:
```json
{
  "query": "科幻电影",
  "top_k": 5
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "query": "科幻电影",
    "method": "vector",
    "results": [
      {
        "id": "50",
        "document": "《星球大战》是一部...",
        "metadata": {
          "title": "Star Wars (1977)",
          "genres": "Action, Adventure, Sci-Fi",
          "movie_id": "50"
        },
        "score": 0.95,
        "method": "vector"
      }
    ],
    "count": 5
  }
}
```

---

### 5. BM25 检索

**接口**: `POST /ai/search/bm25`

**描述**: 使用 BM25 关键词匹配检索电影

**请求体**:
```json
{
  "query": "科幻电影",
  "top_k": 5
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "query": "科幻电影",
    "method": "bm25",
    "results": [...],
    "count": 5
  }
}
```

---

### 6. 混合检索

**接口**: `POST /ai/search/hybrid`

**描述**: 结合向量检索和 BM25 检索

**请求体**:
```json
{
  "query": "科幻电影",
  "top_k": 5,
  "alpha": 0.5,        // 可选，向量检索权重，默认0.5
  "separate": false    // 可选，是否分别返回向量和BM25结果
}
```

**响应示例（separate=false）**:
```json
{
  "success": true,
  "data": {
    "query": "科幻电影",
    "method": "hybrid",
    "results": [...],
    "count": 5
  }
}
```

**响应示例（separate=true）**:
```json
{
  "success": true,
  "data": {
    "query": "科幻电影",
    "method": "hybrid",
    "vector_results": [...],
    "bm25_results": [...],
    "combined_results": [...],
    "vector_count": 10,
    "bm25_count": 10,
    "combined_count": 5
  }
}
```

---

### 7. 重排序

**接口**: `POST /ai/rerank`

**描述**: 对文档列表进行重排序

**请求体**:
```json
{
  "query": "科幻电影",
  "documents": [
    "《星球大战》是一部经典科幻电影...",
    "《泰坦尼克号》是一部爱情电影..."
  ],
  "top_n": 3
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "query": "科幻电影",
    "results": [
      {
        "id": 0,
        "score": 0.95,
        "document": "《星球大战》是一部经典科幻电影..."
      }
    ],
    "count": 2
  }
}
```

---

## 错误响应

所有接口在出错时返回统一格式：

```json
{
  "success": false,
  "message": "错误描述"
}
```

常见 HTTP 状态码：
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 使用示例

### Python 示例

```python
import requests

# 1. 健康检查
response = requests.get('http://localhost:5001/ai/health')
print(response.json())

# 2. 电影推荐
response = requests.post('http://localhost:5001/ai/recommend', json={
    'query': '我想看科幻电影',
    'top_k': 5,
    'rerank_top_n': 3
})
print(response.json())

# 3. 流式推荐
response = requests.post(
    'http://localhost:5001/ai/recommend/stream',
    json={'query': '我想看科幻电影'},
    stream=True
)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### cURL 示例

```bash
# 健康检查
curl http://localhost:5001/ai/health

# 电影推荐
curl -X POST http://localhost:5001/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "我想看科幻电影", "top_k": 5, "rerank_top_n": 3}'

# 向量检索
curl -X POST http://localhost:5001/ai/search/vector \
  -H "Content-Type: application/json" \
  -d '{"query": "科幻电影", "top_k": 5}'
```

---

## 配置说明

服务配置在 `src/config.py` 中：

```python
# Flask配置
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5001
FLASK_DEBUG = False

# RAG配置
TOP_K = 5              # 检索Top-K相关文档
RERANK_TOP_N = 3       # 重排序后返回Top-N条推荐
```

可以通过环境变量覆盖：

```bash
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5001
export FLASK_DEBUG=False
```

---

## 启动服务

```bash
cd movie_ai
python app.py
```

服务启动后会显示：

```
🚀 Movie AI RAG Service 启动中...
📍 地址: http://0.0.0.0:5001
🏥 健康检查: http://localhost:5001/ai/health
🎬 电影推荐: POST http://localhost:5001/ai/recommend
...
```
