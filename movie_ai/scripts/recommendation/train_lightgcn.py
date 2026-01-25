"""
LightGCN 训练脚本
用于训练模型并测试推荐功能
"""
import sys
import os
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.recommendation.lightgcn import LightGCNRecommender
import numpy as np


def plot_recommendations(recommendations, title, save_path, filename):
    """
    绘制推荐结果的柱状图
    
    参数:
        recommendations: 推荐结果列表 [(movie_id, score), ...]
        title: 图表标题
        save_path: 保存路径
        filename: 文件名
    """
    movie_ids = [f"电影{mid}" for mid, _ in recommendations]
    scores = [score for _, score in recommendations]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(movie_ids)), scores, color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1.5)
    
    # 设置标题和标签
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('推荐电影', fontsize=12, fontweight='bold')
    plt.ylabel('相似度/评分', fontsize=12, fontweight='bold')
    
    # 设置 x 轴刻度
    plt.xticks(range(len(movie_ids)), movie_ids, rotation=45, ha='right')
    
    # 在柱子上显示数值
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=9)
    
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    # 保存图片
    os.makedirs(save_path, exist_ok=True)
    plot_path = os.path.join(save_path, filename)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✓ 推荐结果图已保存: {plot_path}")
    
    plt.close()


def plot_training_curves(train_losses, val_losses, save_path='d:/code/vue/movie_ai/scripts/recommendation/result'):
    """
    绘制训练和验证损失曲线
    
    参数:
        train_losses: 训练损失列表
        val_losses: 验证损失列表
        save_path: 保存路径
    """
    epochs = range(1, len(train_losses) + 1)
    
    plt.figure(figsize=(12, 5))
    
    # 绘制损失曲线
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, 'b-', label='训练损失', linewidth=2, marker='o', markersize=4)
    plt.plot(epochs, val_losses, 'r-', label='验证损失', linewidth=2, marker='s', markersize=4)
    plt.title('训练和验证损失曲线', fontsize=14, fontweight='bold')
    plt.xlabel('训练轮数 (Epoch)', fontsize=12)
    plt.ylabel('损失 (Loss)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # 绘制损失差异
    plt.subplot(1, 2, 2)
    loss_diff = np.array(val_losses) - np.array(train_losses)
    plt.plot(epochs, loss_diff, 'g-', linewidth=2, marker='^', markersize=4)
    plt.title('验证损失与训练损失差异', fontsize=14, fontweight='bold')
    plt.xlabel('训练轮数 (Epoch)', fontsize=12)
    plt.ylabel('验证损失 - 训练损失', fontsize=12)
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    os.makedirs(save_path, exist_ok=True)
    plot_path = os.path.join(save_path, 'training_curves.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 训练曲线图已保存: {plot_path}")
    
    plt.close()
    
    # 打印统计信息
    print(f"\n训练损失统计:")
    print(f"  初始: {train_losses[0]:.4f}")
    print(f"  最终: {train_losses[-1]:.4f}")
    print(f"  最小: {min(train_losses):.4f}")
    print(f"\n验证损失统计:")
    print(f"  初始: {val_losses[0]:.4f}")
    print(f"  最终: {val_losses[-1]:.4f}")
    print(f"  最小: {min(val_losses):.4f}")


def main():
    """
    训练 LightGCN 模型并测试推荐功能
    """
    print("=" * 60)
    print("LightGCN 训练脚本")
    print("=" * 60)
    
    # 初始化推荐器
    print("\n[1/4] 初始化 LightGCN 推荐器...")
    recommender = LightGCNRecommender(
        embed_dim=64,      # 嵌入维度
        num_layers=3,      # GCN 层数
        model_dir='d:/code/vue/movie_ai/data'  # 模型保存路径
    )
    print(f"✓ 参数: embed_dim={recommender.embed_dim}, num_layers={recommender.num_layers}")
    print(f"✓ 设备: {recommender.device}")
    print(f"✓ 保存路径: {recommender.model_dir}")
    
    # 设置数据路径
    ml100k_path = 'd:/code/vue/movie_ai/datasets/ml-100k'
    
    # 训练模型
    print(f"\n[2/4] 开始训练模型...")
    print(f"数据集路径: {ml100k_path}")
    
    try:
        train_losses, val_losses = recommender.train(
            ml100k_path=ml100k_path,
            epochs=50,          # 训练轮数
            lr=0.001,           # 学习率
            batch_size=1024,    # 批次大小
            min_rating=4.0,    # 最小评分（保留评分 >= 4 的数据）
            validation_split=0.2  # 验证集比例
        )
        print(f"\n✓ 训练完成！训练轮数: {len(train_losses)}")
    except Exception as e:
        print(f"\n✗ 训练失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 绘制训练曲线
    print(f"\n[2.5/4] 绘制训练曲线...")
    plot_training_curves(
        train_losses=train_losses,
        val_losses=val_losses,
        save_path='d:/code/vue/movie_ai/scripts/recommendation/result'
    )
    
    # 测试基于用户历史的推荐
    print(f"\n[3/4] 测试基于用户历史的推荐...")
    
    # 模拟用户历史观看的电影（使用 MovieLens 数据中的几个热门电影 ID）
    # 注意：MovieLens 100K 的电影 ID 是 0-based（共 1682 个电影）
    test_user_history = [0, 1, 2, 10, 20]  # 用户看过的电影 ID
    
    print(f"模拟用户历史: {test_user_history}")
    recommendations = recommender.recommend(
        user_history=test_user_history,
        top_k=10
    )
    
    print(f"\n为用户推荐 Top 10 电影:")
    print("-" * 50)
    for i, (movie_id, score) in enumerate(recommendations, 1):
        print(f"{i:2d}. 电影ID: {movie_id:4d} | 相似度: {score:.4f}")
    
    # 绘制推荐结果柱状图
    plot_recommendations(
        recommendations=recommendations,
        title='用户推荐 Top 10',
        save_path='d:/code/vue/movie_ai/scripts/recommendation/result',
        filename='recommendations.png'
    )
    
    # 测试相似电影查询
    print(f"\n[4/4] 测试相似电影查询...")
    
    # 查找与电影 0 相似的电影
    target_movie_id = 0
    similar_movies = recommender.find_similar_movies(
        movie_id=target_movie_id,
        top_k=10
    )
    
    print(f"\n与电影 ID={target_movie_id} 相似的 Top 10 电影:")
    print("-" * 50)
    for i, (movie_id, score) in enumerate(similar_movies, 1):
        print(f"{i:2d}. 电影ID: {movie_id:4d} | 相似度: {score:.4f}")
    
    # 绘制相似电影柱状图
    plot_recommendations(
        recommendations=similar_movies,
        title=f'与电影 {target_movie_id} 相似的 Top 10',
        save_path='d:/code/vue/movie_ai/scripts/recommendation/result',
        filename='similar_movies.png'
    )
    
    # 测试加载嵌入
    print(f"\n测试加载预训练嵌入...")
    new_recommender = LightGCNRecommender(model_dir='d:/code/vue/movie_ai/data')
    if new_recommender.load_embeddings():
        print(f"✓ 成功加载预训练嵌入")
        print(f"  用户嵌入形状: {new_recommender.user_embeddings.shape}")
        print(f"  物品嵌入形状: {new_recommender.item_embeddings.shape}")
    else:
        print(f"✗ 加载预训练嵌入失败")
    
    print("\n" + "=" * 60)
    print("训练和测试完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 检查嵌入文件是否保存在: d:/code/vue/movie_ai/data/")
    print("2. 继续创建混合推荐器 (hybrid.py)")
    print("3. 创建 API 路由")


if __name__ == '__main__':
    main()
