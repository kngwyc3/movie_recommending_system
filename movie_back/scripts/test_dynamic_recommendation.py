"""
测试动态推荐系统
验证用户行为追踪和个性化推荐功能
"""
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from recommendation_viewmodel import recommendation_viewmodel


def test_recommendation_system():
    """测试推荐系统"""
    
    print("=" * 60)
    print("动态推荐系统测试")
    print("=" * 60)
    
    # 测试 1: 检查推荐系统状态
    print("\n[测试 1] 检查推荐系统状态")
    print("-" * 60)
    
    try:
        stats = recommendation_viewmodel.get_statistics()
        print(f"✓ 推荐系统状态: {stats['status']}")
        print(f"  - 行为追踪: {stats.get('behavior_tracking', False)}")
        print(f"  - 总用户数: {stats.get('total_users', 0)}")
        print(f"  - 总行为数: {stats.get('total_behaviors', 0)}")
        print(f"  - 行为分布: {stats.get('behavior_distribution', {})}")
    except Exception as e:
        print(f"✗ 获取统计信息失败: {str(e)}")
        return False
    
    # 测试 2: 获取热门电影（冷启动）
    print("\n[测试 2] 获取热门电影（冷启动推荐）")
    print("-" * 60)
    
    try:
        hot_movies = recommendation_viewmodel.get_hot_movies(top_k=5)
        print(f"✓ 获取到 {len(hot_movies)} 部热门电影:")
        for i, movie in enumerate(hot_movies[:3], 1):
            print(f"  {i}. {movie['title']} (分数: {movie['score']:.4f})")
    except Exception as e:
        print(f"✗ 获取热门电影失败: {str(e)}")
    
    # 测试 3: 记录用户行为
    print("\n[测试 3] 记录用户行为")
    print("-" * 60)
    
    test_user_id = 1
    test_movie_ids = [10, 20, 30]
    
    behaviors = [
        (test_movie_ids[0], 'click'),
        (test_movie_ids[0], 'view'),
        (test_movie_ids[1], 'favorite'),
        (test_movie_ids[2], 'like'),
        (test_movie_ids[0], 'rate', {'rating': 9}),   # 高评分
        (test_movie_ids[1], 'rate', {'rating': 6}),   # 中评分
        (test_movie_ids[2], 'rate', {'rating': 3}),   # 低评分
    ]
    
    for movie_id, behavior_type, *metadata in behaviors:
        try:
            metadata_dict = metadata[0] if metadata else {}
            success = recommendation_viewmodel.record_user_behavior(
                user_id=test_user_id,
                movie_id=movie_id,
                behavior_type=behavior_type,
                metadata=metadata_dict
            )
            if success:
                print(f"✓ 用户 {test_user_id} {behavior_type} Movie {movie_id}")
            else:
                print(f"✗ 记录行为失败: {behavior_type} Movie {movie_id}")
        except Exception as e:
            print(f"✗ 记录行为异常: {str(e)}")
    
    # 测试 4: 获取用户行为历史
    print("\n[测试 4] 获取用户行为历史")
    print("-" * 60)
    
    try:
        history = recommendation_viewmodel.get_user_behavior_history(
            user_id=test_user_id,
            limit=10
        )
        print(f"✓ 用户 {test_user_id} 的行为历史 (最近 {len(history)} 条):")
        for h in history[:5]:
            print(f"  - {h['behavior_type']} Movie {h['movie_id']} at {h['timestamp'][:19]}")
    except Exception as e:
        print(f"✗ 获取行为历史失败: {str(e)}")
    
    # 测试 5: 获取个性化推荐（静态）
    print("\n[测试 5] 获取个性化推荐（静态推荐）")
    print("-" * 60)
    
    try:
        recommendations = recommendation_viewmodel.get_personalized_recommendations(
            user_id=test_user_id,
            top_k=5,
            use_dynamic=False
        )
        print(f"✓ 用户 {test_user_id} 的静态推荐 (Top {len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['title']} (分数: {rec['score']:.4f})")
    except Exception as e:
        print(f"✗ 获取静态推荐失败: {str(e)}")
    
    # 测试 6: 获取个性化推荐（动态）
    print("\n[测试 6] 获取个性化推荐（动态推荐）")
    print("-" * 60)
    
    try:
        recommendations = recommendation_viewmodel.get_personalized_recommendations(
            user_id=test_user_id,
            top_k=5,
            use_dynamic=True
        )
        print(f"✓ 用户 {test_user_id} 的动态推荐 (Top {len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['title']} (分数: {rec['score']:.4f})")
    except Exception as e:
        print(f"✗ 获取动态推荐失败: {str(e)}")
    
    # 测试 7: 查找相似电影
    print("\n[测试 7] 查找相似电影")
    print("-" * 60)
    
    try:
        similar_movies = recommendation_viewmodel.get_similar_movies(
            movie_id=test_movie_ids[0],
            top_k=3
        )
        print(f"✓ 与 Movie {test_movie_ids[0]} 相似的电影:")
        for i, movie in enumerate(similar_movies[:3], 1):
            print(f"  {i}. {movie['title']} (相似度: {movie['score']:.4f})")
    except Exception as e:
        print(f"✗ 获取相似电影失败: {str(e)}")
    
    # 测试 8: 再次查看统计信息
    print("\n[测试 8] 更新后的统计信息")
    print("-" * 60)
    
    try:
        stats = recommendation_viewmodel.get_statistics()
        print(f"✓ 更新后统计:")
        print(f"  - 总用户数: {stats.get('total_users', 0)}")
        print(f"  - 总行为数: {stats.get('total_behaviors', 0)}")
        print(f"  - 行为分布: {stats.get('behavior_distribution', {})}")
    except Exception as e:
        print(f"✗ 获取统计信息失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_recommendation_system()
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
