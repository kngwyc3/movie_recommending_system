"""
测试 Movie AI API 接口
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5001'

def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_health():
    """测试健康检查接口"""
    print_section("1. 测试健康检查")
    
    try:
        response = requests.get(f'{BASE_URL}/ai/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_recommend():
    """测试电影推荐接口"""
    print_section("2. 测试电影推荐（完整响应）")
    
    try:
        data = {
            'query': '我想看科幻冒险电影',
            'top_k': 5,
            'rerank_top_n': 3
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(f'{BASE_URL}/ai/recommend', json=data)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        if result['success']:
            print(f"\n✅ 推荐成功!")
            print(f"\n查询: {result['data']['query']}")
            print(f"\n推荐的电影ID: {result['data']['recommended_movie_ids']}")
            print(f"\nLLM推荐内容:\n{result['data']['llm_content']}")
            print(f"\n重排序结果数量: {len(result['data']['rerank']['results'])}")
        else:
            print(f"❌ 推荐失败: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_recommend_stream():
    """测试流式推荐接口"""
    print_section("3. 测试电影推荐（流式响应）")
    
    try:
        data = {
            'query': '推荐一些动画电影',
            'top_k': 5,
            'rerank_top_n': 3
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(
            f'{BASE_URL}/ai/recommend/stream',
            json=data,
            stream=True
        )
        
        print(f"状态码: {response.status_code}\n")
        print("流式响应:\n")
        
        llm_content = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    event_data = json.loads(line_str[6:])
                    
                    if event_data['type'] == 'retrieval':
                        print(f"📥 检索完成，推荐电影ID: {event_data['data']['recommended_movie_ids']}\n")
                        print("🤖 LLM生成中: ", end='', flush=True)
                    
                    elif event_data['type'] == 'llm_chunk':
                        content = event_data['data']['content']
                        llm_content += content
                        print(content, end='', flush=True)
                    
                    elif event_data['type'] == 'complete':
                        print(f"\n\n✅ 生成完成!")
                        print(f"时间戳: {event_data['data']['timestamp']}")
                    
                    elif event_data['type'] == 'error':
                        print(f"\n❌ 错误: {event_data['data']['message']}")
                        return False
        
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_vector_search():
    """测试向量检索接口"""
    print_section("4. 测试向量检索")
    
    try:
        data = {
            'query': '太空探险',
            'top_k': 3
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(f'{BASE_URL}/ai/search/vector', json=data)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        if result['success']:
            print(f"\n✅ 检索成功! 找到 {result['data']['count']} 个结果\n")
            for i, item in enumerate(result['data']['results'][:3], 1):
                print(f"{i}. {item['metadata']['title']} (评分: {item['score']:.4f})")
        else:
            print(f"❌ 检索失败: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_bm25_search():
    """测试BM25检索接口"""
    print_section("5. 测试BM25检索")
    
    try:
        data = {
            'query': '喜剧',
            'top_k': 3
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(f'{BASE_URL}/ai/search/bm25', json=data)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        if result['success']:
            print(f"\n✅ 检索成功! 找到 {result['data']['count']} 个结果\n")
            for i, item in enumerate(result['data']['results'][:3], 1):
                print(f"{i}. {item['metadata']['title']} (评分: {item['score']:.4f})")
        else:
            print(f"❌ 检索失败: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_hybrid_search():
    """测试混合检索接口"""
    print_section("6. 测试混合检索")
    
    try:
        data = {
            'query': '爱情故事',
            'top_k': 3,
            'separate': True
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(f'{BASE_URL}/ai/search/hybrid', json=data)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        if result['success']:
            print(f"\n✅ 检索成功!")
            print(f"向量检索: {result['data']['vector_count']} 个结果")
            print(f"BM25检索: {result['data']['bm25_count']} 个结果")
            print(f"合并后: {result['data']['combined_count']} 个结果\n")
            
            print("合并结果:")
            for i, item in enumerate(result['data']['combined_results'][:3], 1):
                print(f"{i}. {item['metadata']['title']} (方法: {item['method']})")
        else:
            print(f"❌ 检索失败: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_rerank():
    """测试重排序接口"""
    print_section("7. 测试重排序")
    
    try:
        data = {
            'query': '科幻电影',
            'documents': [
                '《星球大战》是一部经典的科幻冒险电影',
                '《泰坦尼克号》是一部浪漫爱情电影',
                '《黑客帝国》是一部科幻动作电影',
                '《阿甘正传》是一部励志剧情电影'
            ],
            'top_n': 2
        }
        
        print(f"请求: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
        
        response = requests.post(f'{BASE_URL}/ai/rerank', json=data)
        print(f"状态码: {response.status_code}")
        
        result = response.json()
        if result['success']:
            print(f"\n✅ 重排序成功! 返回 {result['data']['count']} 个结果\n")
            for i, item in enumerate(result['data']['results'], 1):
                print(f"{i}. 文档{item['id']+1} (评分: {item['score']:.4f})")
                print(f"   {item['document'][:50]}...")
        else:
            print(f"❌ 重排序失败: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*80)
    print("  Movie AI API 测试")
    print("="*80)
    print(f"\n目标服务: {BASE_URL}")
    print("请确保服务已启动: python app.py\n")
    
    input("按 Enter 键开始测试...")
    
    # 运行所有测试
    tests = [
        ("健康检查", test_health),
        ("电影推荐", test_recommend),
        ("流式推荐", test_recommend_stream),
        ("向量检索", test_vector_search),
        ("BM25检索", test_bm25_search),
        ("混合检索", test_hybrid_search),
        ("重排序", test_rerank)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  测试被用户中断")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 测试 {name} 时发生异常: {e}")
            results.append((name, False))
    
    # 打印测试总结
    print_section("测试总结")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == '__main__':
    main()
