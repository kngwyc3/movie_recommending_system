"""
用户行为追踪模块
用于记录用户对电影的交互行为，并基于这些行为动态计算用户向量
支持时间衰减机制，使近期行为影响力更大
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from collections import defaultdict
import os

class UserBehaviorTracker:
    """用户行为追踪器"""

    def __init__(self, decay_days: int = 30, behavior_weights: Optional[Dict[str, float]] = None,
                 persist_dir: str = None):
        """
        初始化行为追踪器

        Args:
            decay_days: 行为衰减天数，超过该天数的行为影响力降至0
            behavior_weights: 不同行为类型的权重配置
            persist_dir: 行为数据持久化目录
        """
        self.decay_days = decay_days
        self.persist_dir = persist_dir

        # 默认行为权重配置
        # 前端评分是0-10分制，映射到三个等级
        self.behavior_weights = behavior_weights or {
            'like': 1.0,             # 👍 喜欢 - 最高权重
            'favorite': 0.8,         # ⭐ 收藏
            'rate_high': 0.7,        # 高评分 (8-10分)
            'rate_medium': 0.5,       # 中评分 (5-7分)
            'rate_low': 0.3,         # 低评分 (1-4分)
            'click': 0.3,            # 👆 点击 - 最低权重
            'view': 0.3,             # 观看
            'watch': 0.6,            # 完整观看
            'share': 0.6,            # 📤 分享
            'comment': 0.5,          # 💬 评论
        }

        # 用户行为存储: {user_id: {movie_id: [(timestamp, behavior_type, metadata)]}}
        self.user_behaviors = defaultdict(lambda: defaultdict(list))

        # 电影向量缓存（需要外部注入）
        self.movie_embeddings: Dict[int, np.ndarray] = {}

        # 维度信息（需要外部注入）
        self.embedding_dim = None

        # 自动加载持久化数据
        if persist_dir:
            self.load_behaviors()
    
    def set_movie_embeddings(self, movie_embeddings: Dict[int, np.ndarray]):
        """
        设置电影向量映射
        
        Args:
            movie_embeddings: {movie_id: embedding_vector} 的字典
        """
        self.movie_embeddings = movie_embeddings
        if movie_embeddings:
            self.embedding_dim = next(iter(movie_embeddings.values())).shape[0]
    
    def record_behavior(self, user_id: int, movie_id: int, behavior_type: str,
                       metadata: Optional[Dict] = None) -> bool:
        """
        记录用户行为

        Args:
            user_id: 用户ID
            movie_id: 电影ID
            behavior_type: 行为类型 (click, view, favorite, watch, rate, share等)
            metadata: 额外元数据（如评分值、观看时长等）

        Returns:
            是否记录成功
        """
        if movie_id not in self.movie_embeddings:
            print(f"Warning: Movie {movie_id} not found in embeddings")
            return False

        # 处理评分行为，0-10分制映射到三个等级
        if behavior_type == 'rate' and metadata and 'rating' in metadata:
            rating = int(metadata['rating'])
            if rating >= 8:
                behavior_type = 'rate_high'
            elif rating >= 5:
                behavior_type = 'rate_medium'
            else:
                behavior_type = 'rate_low'

        timestamp = datetime.now()
        self.user_behaviors[user_id][movie_id].append((timestamp, behavior_type, metadata))

        # 自动保存（每次记录后）
        if self.persist_dir:
            self.save_behaviors(user_id)

        return True
    
    def get_behavior_weight(self, behavior_type: str) -> float:
        """
        获取行为权重
        
        Args:
            behavior_type: 行为类型
        
        Returns:
            权重值
        """
        return self.behavior_weights.get(behavior_type, 0.3)
    
    def calculate_time_decay(self, behavior_time: datetime, current_time: Optional[datetime] = None) -> float:
        """
        计算时间衰减系数
        
        Args:
            behavior_time: 行为发生时间
            current_time: 当前时间（默认为现在）
        
        Returns:
            衰减系数 (0~1)
        """
        if current_time is None:
            current_time = datetime.now()
        
        time_diff = (current_time - behavior_time).days
        
        if time_diff >= self.decay_days:
            return 0.0
        
        # 线性衰减
        decay = 1.0 - (time_diff / self.decay_days)
        
        # 或者使用指数衰减
        # decay = np.exp(-time_diff / (self.decay_days / 3))
        
        return max(0.0, decay)
    
    def compute_user_vector(self, user_id: int,
                           current_time: Optional[datetime] = None,
                           min_behaviors: int = 1,
                           pretrained_embedding: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        基于用户行为计算动态用户向量

        Args:
            user_id: 用户ID
            current_time: 当前时间（默认为现在）
            min_behaviors: 最少行为数量，少于则返回None
            pretrained_embedding: 预训练用户嵌入向量（用于加权融合）

        Returns:
            用户向量或None
        """
        if user_id not in self.user_behaviors:
            return None

        # 收集所有行为
        all_behaviors = []
        for movie_id, behavior_list in self.user_behaviors[user_id].items():
            all_behaviors.extend([(movie_id, b[0], b[1], b[2]) for b in behavior_list])

        # 如果没有提供预训练嵌入且行为不足，返回None
        if pretrained_embedding is None and len(all_behaviors) < min_behaviors:
            return None

        if self.embedding_dim is None:
            raise ValueError("Embedding dimension not set. Call set_movie_embeddings first.")

        # 计算基于行为的用户向量
        behavior_vector = np.zeros(self.embedding_dim)
        total_weight = 0.0

        for movie_id, timestamp, behavior_type, metadata in all_behaviors:
            # 获取电影向量
            if movie_id not in self.movie_embeddings:
                continue

            movie_embedding = self.movie_embeddings[movie_id]

            # 获取行为权重
            behavior_weight = self.get_behavior_weight(behavior_type)

            # 获取时间衰减
            time_decay = self.calculate_time_decay(timestamp, current_time)

            # 计算综合权重
            combined_weight = behavior_weight * time_decay

            # 累加
            behavior_vector += combined_weight * movie_embedding
            total_weight += combined_weight

        # 归一化行为向量
        if total_weight > 0:
            behavior_vector = behavior_vector / total_weight

            # L2归一化
            norm = np.linalg.norm(behavior_vector)
            if norm > 0:
                behavior_vector = behavior_vector / norm

        # 如果没有预训练嵌入，直接返回行为向量
        if pretrained_embedding is None:
            return behavior_vector

        # 计算加权融合系数α（根据行为数量动态调整）
        behavior_count = len(all_behaviors)
        if behavior_count <= 10:
            alpha = 0.7  # 行为少时，预训练权重高
        elif behavior_count <= 20:
            alpha = 0.5  # 行为中量，权重平衡
        else:
            alpha = 0.3  # 行为多时，行为权重高

        # 归一化预训练嵌入
        pretrained_norm = np.linalg.norm(pretrained_embedding)
        if pretrained_norm > 0:
            pretrained_embedding = pretrained_embedding / pretrained_norm

        # 加权融合: user_emb = α * pretrained_emb + (1-α) * behavior_emb
        user_vector = alpha * pretrained_embedding + (1 - alpha) * behavior_vector

        # 最终L2归一化
        final_norm = np.linalg.norm(user_vector)
        if final_norm > 0:
            user_vector = user_vector / final_norm

        return user_vector
    
    def get_user_behavior_history(self, user_id: int, 
                                  limit: int = 100,
                                  behavior_type: Optional[str] = None) -> List[Dict]:
        """
        获取用户行为历史
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            behavior_type: 筛选特定行为类型
        
        Returns:
            行为历史列表
        """
        if user_id not in self.user_behaviors:
            return []
        
        history = []
        for movie_id, behavior_list in self.user_behaviors[user_id].items():
            for timestamp, b_type, metadata in behavior_list:
                if behavior_type and b_type != behavior_type:
                    continue
                
                history.append({
                    'movie_id': movie_id,
                    'timestamp': timestamp.isoformat(),
                    'behavior_type': b_type,
                    'metadata': metadata
                })
        
        # 按时间倒序排序
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return history[:limit]

    def save_behaviors(self, user_id: int = None):
        """
        保存用户行为数据到文件

        Args:
            user_id: 用户ID，如果为None则保存所有用户数据
        """
        if self.persist_dir is None:
            return False

        try:
            os.makedirs(self.persist_dir, exist_ok=True)

            if user_id is None:
                # 保存所有用户数据
                file_path = os.path.join(self.persist_dir, 'user_behaviors.json')
                data = {}
                for uid, behaviors in self.user_behaviors.items():
                    data[uid] = {}
                    for mid, behavior_list in behaviors.items():
                        data[uid][mid] = [
                            {
                                'timestamp': ts.isoformat(),
                                'behavior_type': bt,
                                'metadata': meta
                            }
                            for ts, bt, meta in behavior_list
                        ]

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            else:
                # 保存单个用户数据
                if user_id not in self.user_behaviors:
                    return False

                file_path = os.path.join(self.persist_dir, f'user_{user_id}_behaviors.json')
                data = {}
                for mid, behavior_list in self.user_behaviors[user_id].items():
                    data[mid] = [
                        {
                            'timestamp': ts.isoformat(),
                            'behavior_type': bt,
                            'metadata': meta
                        }
                        for ts, bt, meta in behavior_list
                    ]

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True

        except Exception as e:
            print(f"保存行为数据失败: {e}")
            return False

    def load_behaviors(self):
        """
        从文件加载用户行为数据
        """
        if self.persist_dir is None:
            return False

        try:
            file_path = os.path.join(self.persist_dir, 'user_behaviors.json')
            if not os.path.exists(file_path):
                print("未找到行为数据文件")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 解析数据并重建结构
            for uid_str, behaviors in data.items():
                user_id = int(uid_str)
                for mid_str, behavior_list in behaviors.items():
                    movie_id = int(mid_str)
                    for item in behavior_list:
                        timestamp = datetime.fromisoformat(item['timestamp'])
                        behavior_type = item['behavior_type']
                        metadata = item.get('metadata', {})
                        self.user_behaviors[user_id][movie_id].append(
                            (timestamp, behavior_type, metadata)
                        )

            print(f"已加载行为数据: {len(self.user_behaviors)} 个用户")
            return True

        except Exception as e:
            print(f"加载行为数据失败: {e}")
            return False

    def cleanup_old_behaviors(self, days: Optional[int] = None):
        """
        清理过期行为数据
        
        Args:
            days: 清理多少天前的数据，默认使用decay_days
        """
        if days is None:
            days = self.decay_days
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for user_id in list(self.user_behaviors.keys()):
            for movie_id in list(self.user_behaviors[user_id].keys()):
                # 过滤掉过期行为
                self.user_behaviors[user_id][movie_id] = [
                    b for b in self.user_behaviors[user_id][movie_id]
                    if b[0] >= cutoff_time
                ]
                
                # 删除空记录
                if not self.user_behaviors[user_id][movie_id]:
                    del self.user_behaviors[user_id][movie_id]
            
            # 删除无行为的用户
            if not self.user_behaviors[user_id]:
                del self.user_behaviors[user_id]
    
    def export_user_data(self, user_id: int) -> Dict:
        """
        导出用户数据
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户数据字典
        """
        if user_id not in self.user_behaviors:
            return {}
        
        return {
            'user_id': user_id,
            'behaviors': {
                movie_id: [
                    {
                        'timestamp': b[0].isoformat(),
                        'behavior_type': b[1],
                        'metadata': b[2]
                    }
                    for b in behavior_list
                ]
                for movie_id, behavior_list in self.user_behaviors[user_id].items()
            }
        }
    
    def import_user_data(self, user_data: Dict):
        """
        导入用户数据
        
        Args:
            user_data: 用户数据字典
        """
        user_id = user_data['user_id']
        
        for movie_id, behavior_list in user_data['behaviors'].items():
            for behavior in behavior_list:
                timestamp = datetime.fromisoformat(behavior['timestamp'])
                self.user_behaviors[user_id][movie_id].append(
                    (timestamp, behavior['behavior_type'], behavior['metadata'])
                )
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total_behaviors = 0
        behavior_counts = defaultdict(int)
        
        for user_id, user_data in self.user_behaviors.items():
            for movie_id, behavior_list in user_data.items():
                total_behaviors += len(behavior_list)
                for _, b_type, _ in behavior_list:
                    behavior_counts[b_type] += 1
        
        return {
            'total_users': len(self.user_behaviors),
            'total_behaviors': total_behaviors,
            'behavior_distribution': dict(behavior_counts),
            'decay_days': self.decay_days,
            'embedding_dim': self.embedding_dim
        }


# 便捷函数：创建用户行为追踪器实例
def create_tracker(movie_embeddings: Dict[int, np.ndarray], 
                   decay_days: int = 30,
                   behavior_weights: Optional[Dict[str, float]] = None) -> UserBehaviorTracker:
    """
    创建并初始化用户行为追踪器
    
    Args:
        movie_embeddings: 电影向量字典
        decay_days: 衰减天数
        behavior_weights: 行为权重
    
    Returns:
        初始化好的追踪器
    """
    tracker = UserBehaviorTracker(decay_days=decay_days, behavior_weights=behavior_weights)
    tracker.set_movie_embeddings(movie_embeddings)
    return tracker


if __name__ == "__main__":
    # 测试代码
    print("用户行为追踪模块测试")
    print("=" * 50)
    
    # 创建模拟数据
    dim = 128
    num_movies = 100
    
    # 生成随机电影向量
    movie_embeddings = {
        i: np.random.randn(dim) for i in range(num_movies)
    }
    
    # 创建追踪器
    tracker = create_tracker(movie_embeddings, decay_days=30)
    
    # 模拟用户行为
    user_id = 1
    
    # 记录一些行为
    tracker.record_behavior(user_id, 1, 'click')
    tracker.record_behavior(user_id, 2, 'favorite')
    tracker.record_behavior(user_id, 3, 'rate', {'rating': 5})
    tracker.record_behavior(user_id, 4, 'rate', {'rating': 2})
    
    print(f"已记录 {len(tracker.user_behaviors[user_id])} 部电影的行为")
    
    # 计算用户向量
    user_vector = tracker.compute_user_vector(user_id)
    
    if user_vector is not None:
        print(f"用户向量维度: {user_vector.shape}")
        print(f"用户向量范数: {np.linalg.norm(user_vector):.4f}")
    
    # 获取行为历史
    history = tracker.get_user_behavior_history(user_id)
    print(f"\n最近的行为记录:")
    for h in history[:3]:
        print(f"  - {h['behavior_type']} Movie {h['movie_id']} at {h['timestamp'][:19]}")
    
    # 统计信息
    stats = tracker.get_statistics()
    print(f"\n统计信息:")
    print(f"  - 用户数: {stats['total_users']}")
    print(f"  - 总行为数: {stats['total_behaviors']}")
    print(f"  - 行为分布: {stats['behavior_distribution']}")
    
    print("\n✓ 测试完成")
