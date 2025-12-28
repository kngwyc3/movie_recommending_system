"""
简化版 AI 集成测试（Windows 兼容）
"""
import requests
import json

MOVIE_BACK_URL = 'http://localhost:5000'
MOVIE_AI_URL = 'http://localhost:5001'


def test_service(name, url):
    """测试服务是否运行"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name} running")
            return True
        else:
            print(f"[FAIL] {name} status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {name} error: {e}")
        return False


def test_recommend():
    """测试推荐接口"""
    print("\n=== Test 1: Movie Recommend ===")
    try:
        data = {'query': 'sci-fi movies', 'top_k': 5, 'rerank_top_n': 3}
        response = requests.post(f'{MOVIE_BACK_URL}/api/ai/recommend', json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[PASS] Recommended movies: {result['data']['recommended_movie_ids']}")
            print(f"       Rerank count: {len(result['data']['rerank']['results'])}")
            return True
        else:
            print(f"[FAIL] {result.get('message')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_search():
    """测试搜索接口"""
    print("\n=== Test 2: Hybrid Search ===")
    try:
        data = {'query': 'space adventure', 'mode': 'hybrid', 'top_k': 3}
        response = requests.post(f'{MOVIE_BACK_URL}/api/ai/search', json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[PASS] Found {len(result['data'])} results")
            for i, item in enumerate(result['data'][:2], 1):
                print(f"       {i}. {item['title']} (score: {item['score']:.4f})")
            return True
        else:
            print(f"[FAIL] {result.get('message')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_vector_search():
    """测试向量搜索"""
    print("\n=== Test 3: Vector Search ===")
    try:
        data = {'query': 'love story', 'top_k': 3}
        response = requests.post(f'{MOVIE_BACK_URL}/api/ai/vector-search', json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[PASS] Found {len(result['data'])} results")
            return True
        else:
            print(f"[FAIL] {result.get('message')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_chat():
    """测试智能问答"""
    print("\n=== Test 4: AI Chat ===")
    try:
        data = {'query': 'recommend comedy movies', 'top_k': 5}
        response = requests.post(f'{MOVIE_BACK_URL}/api/ai/chat', json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[PASS] Chat response received")
            print(f"       Movies: {result['data'].get('recommended_movie_ids', [])}")
            return True
        else:
            print(f"[FAIL] {result.get('message')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_rerank():
    """测试重排序"""
    print("\n=== Test 5: Rerank ===")
    try:
        data = {
            'query': 'sci-fi',
            'documents': [
                'Star Wars is a classic sci-fi movie',
                'Titanic is a romantic movie',
                'The Matrix is a sci-fi action movie'
            ],
            'top_n': 2
        }
        response = requests.post(f'{MOVIE_BACK_URL}/api/ai/rerank', json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[PASS] Reranked {len(result['data'])} documents")
            return True
        else:
            print(f"[FAIL] {result.get('message')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Movie Back AI Integration Test")
    print("=" * 60)
    
    # Check services
    print("\n--- Service Status ---")
    back_ok = test_service("Movie Back", f"{MOVIE_BACK_URL}/api/health")
    ai_ok = test_service("Movie AI", f"{MOVIE_AI_URL}/ai/health")
    
    if not (back_ok and ai_ok):
        print("\n[ERROR] Services not running!")
        print("Start services:")
        print("  1. cd movie_ai && python app.py")
        print("  2. cd movie_back/src && python app.py")
        return
    
    # Run tests
    print("\n--- Running Tests ---")
    tests = [
        ("Recommend", test_recommend),
        ("Search", test_search),
        ("Vector Search", test_vector_search),
        ("Chat", test_chat),
        ("Rerank", test_rerank)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"[ERROR] Test {name} exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")


if __name__ == '__main__':
    main()
