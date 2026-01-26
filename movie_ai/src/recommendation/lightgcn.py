"""
LightGCN 推荐器实现
使用 PyTorch Geometric 的 LGConv 层实现 LightGCN
集成用户行为追踪，支持动态推荐
"""
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import LGConv
from torch_geometric.data import Data
from sklearn.metrics.pairwise import cosine_similarity
from user_behavior import UserBehaviorTracker


class LightGCN(nn.Module):
    """
    LightGCN 图神经网络模型
    """
    def __init__(self, num_users, num_items, embed_dim=64, num_layers=3):
        super(LightGCN, self).__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        
        # 用户和物品的初始嵌入
        self.user_embedding = nn.Embedding(num_users, embed_dim)
        self.item_embedding = nn.Embedding(num_items, embed_dim)
        
        # 初始化嵌入权重
        nn.init.normal_(self.user_embedding.weight, std=0.1)
        nn.init.normal_(self.item_embedding.weight, std=0.1)
        
        # LightGCN 卷积层
        self.convs = nn.ModuleList([
            LGConv(normalize=True) for _ in range(num_layers)
        ])
    
    def forward(self, edge_index):
        """
        前向传播，计算用户和物品的最终嵌入
        """
        # 获取初始嵌入
        user_emb = self.user_embedding.weight
        item_emb = self.item_embedding.weight
        
        # 合并所有节点嵌入
        all_emb = torch.cat([user_emb, item_emb], dim=0)
        
        # 初始化嵌入列表（用于层聚合）
        embs = [all_emb]
        
        # 通过所有卷积层
        for conv in self.convs:
            all_emb = conv(all_emb, edge_index)
            embs.append(all_emb)
        
        # 简单平均聚合所有层的嵌入
        final_emb = torch.stack(embs, dim=0).mean(dim=0)
        
        # 分离用户和物品嵌入
        user_final_emb = final_emb[:self.num_users]
        item_final_emb = final_emb[self.num_users:]
        
        return user_final_emb, item_final_emb
    
    def predict(self, user_ids, item_ids, edge_index):
        """
        预测用户对物品的评分
        """
        user_emb, item_emb = self.forward(edge_index)
        user_emb = user_emb[user_ids]
        item_emb = item_emb[item_ids]
        
        # 使用内积计算分数
        scores = (user_emb * item_emb).sum(dim=-1)
        return scores


class LightGCNRecommender:
    """
    LightGCN 推荐器包装类
    负责训练、保存模型、提供推荐服务
    集成用户行为追踪，支持动态推荐
    """
    def __init__(self, embed_dim=64, num_layers=3, model_dir='d:/code/vue/movie_ai/data',
                 use_behavior_tracking=True, decay_days=30):
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.model_dir = model_dir
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.item_embeddings = None
        self.user_embeddings = None
        
        # 用户行为追踪
        self.use_behavior_tracking = use_behavior_tracking
        self.behavior_tracker = None
        self.decay_days = decay_days
        
        # 评分数据（用于统计热门电影）
        self.ratings_data = None
        self.num_users = 0
        self.num_items = 0
        
        # 创建模型目录
        os.makedirs(model_dir, exist_ok=True)
    
    def _load_movielens_data(self, ml100k_path):
        """
        加载 MovieLens 100K 数据集
        """
        ratings_file = os.path.join(ml100k_path, 'u.data')
        
        # 读取评分数据
        ratings = []
        users = set()
        items = set()
        
        with open(ratings_file, 'r') as f:
            for line in f:
                user_id, item_id, rating, timestamp = line.strip().split('\t')
                user_id = int(user_id) - 1  # 从 1-based 转为 0-based
                item_id = int(item_id) - 1
                rating = float(rating)
                
                ratings.append((user_id, item_id, rating))
                users.add(user_id)
                items.add(item_id)
        
        num_users = max(users) + 1
        num_items = max(items) + 1
        
        print(f"加载数据集: {len(ratings)} 条评分, {num_users} 用户, {num_items} 物品")
        
        return ratings, num_users, num_items
    
    def _build_graph(self, ratings, num_users, num_items, min_rating=4.0):
        """
        构建用户-物品二部图
        只有评分 >= min_rating 的边才被保留
        """
        # 过滤高评分数据
        filtered_ratings = [(u, i, r) for u, i, r in ratings if r >= min_rating]
        
        # 构建边索引
        edge_index = []
        for user_id, item_id, rating in filtered_ratings:
            # 用户 -> 物品
            edge_index.append([user_id, num_users + item_id])
            # 物品 -> 用户 (双向)
            edge_index.append([num_users + item_id, user_id])
        
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        
        print(f"构建图: {len(filtered_ratings)} 条边 ({2 * len(filtered_ratings)} 条双向边)")
        
        return edge_index, len(filtered_ratings)
    
    def train(self, ml100k_path, epochs=50, lr=0.001, batch_size=1024, min_rating=4.0, 
              validation_split=0.2):
        """
        训练 LightGCN 模型
        
        参数:
            validation_split: 验证集比例 (默认 0.2)
            
        返回:
            train_losses: 训练损失列表
            val_losses: 验证损失列表
        """
        print("开始训练 LightGCN 模型...")
        
        # 加载数据
        ratings, num_users, num_items = self._load_movielens_data(ml100k_path)
        
        # 保存评分数据用于统计
        self.ratings_data = ratings
        self.num_users = num_users
        self.num_items = num_items

        # 保存评分数据到文件（用于持久化）
        self.save_ratings_data()
        
        edge_index, num_edges = self._build_graph(ratings, num_users, num_items, min_rating)
        
        # 创建模型
        self.model = LightGCN(
            num_users=num_users,
            num_items=num_items,
            embed_dim=self.embed_dim,
            num_layers=self.num_layers
        ).to(self.device)
        
        # 移动边到设备
        edge_index = edge_index.to(self.device)
        
        # 优化器
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        # 准备数据
        all_data = [(u, i, r) for u, i, r in ratings if r >= min_rating]
        
        # 划分训练集和验证集
        np.random.seed(42)
        np.random.shuffle(all_data)
        split_idx = int(len(all_data) * (1 - validation_split))
        train_data = all_data[:split_idx]
        val_data = all_data[split_idx:]
        
        train_losses = []
        val_losses = []
        
        print(f"训练参数: epochs={epochs}, lr={lr}, batch_size={batch_size}")
        print(f"数据划分: 训练集={len(train_data)}, 验证集={len(val_data)}")
        print(f"设备: {self.device}")
        print("-" * 50)
        
        # 训练循环
        for epoch in range(epochs):
            # 训练阶段
            self.model.train()
            total_loss = 0
            
            # 小批量训练
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i + batch_size]
                user_ids = torch.tensor([u for u, _, _ in batch], dtype=torch.long).to(self.device)
                item_ids = torch.tensor([i for _, i, _ in batch], dtype=torch.long).to(self.device)
                ratings_tensor = torch.tensor([r for _, _, r in batch], dtype=torch.float).to(self.device)
                
                # 预测评分
                optimizer.zero_grad()
                predictions = self.model.predict(user_ids, item_ids, edge_index)
                
                # 计算损失 (BPR Loss 近似)
                # 这里简化为 MSE Loss
                loss = F.mse_loss(predictions, ratings_tensor)
                
                # 添加 L2 正则化
                l2_reg = (
                    self.model.user_embedding.weight.norm() + 
                    self.model.item_embedding.weight.norm()
                ) * 0.001
                loss += l2_reg
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            # 计算平均训练损失
            avg_train_loss = total_loss / (len(train_data) / batch_size)
            train_losses.append(avg_train_loss)
            
            # 验证阶段
            self.model.eval()
            val_loss = 0
            with torch.no_grad():
                for i in range(0, len(val_data), batch_size):
                    batch = val_data[i:i + batch_size]
                    user_ids = torch.tensor([u for u, _, _ in batch], dtype=torch.long).to(self.device)
                    item_ids = torch.tensor([i for _, i, _ in batch], dtype=torch.long).to(self.device)
                    ratings_tensor = torch.tensor([r for _, _, r in batch], dtype=torch.float).to(self.device)
                    
                    predictions = self.model.predict(user_ids, item_ids, edge_index)
                    loss = F.mse_loss(predictions, ratings_tensor)
                    val_loss += loss.item()
            
            avg_val_loss = val_loss / (len(val_data) / batch_size)
            val_losses.append(avg_val_loss)
            
            # 打印进度
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"Epoch {epoch + 1}/{epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        
        print("-" * 50)
        print("训练完成！")
        
        # 提取并保存嵌入
        self._save_embeddings(edge_index)
        
        return train_losses, val_losses
    
    def _save_embeddings(self, edge_index):
        """
        提取并保存用户和物品的嵌入
        """
        self.model.eval()
        with torch.no_grad():
            user_emb, item_emb = self.model.forward(edge_index)
            
            # 转换为 numpy 并保存
            self.user_embeddings = user_emb.cpu().numpy()
            self.item_embeddings = item_emb.cpu().numpy()
            
            # 保存嵌入文件
            user_emb_path = os.path.join(self.model_dir, 'lightgcn_user_embeddings.npy')
            item_emb_path = os.path.join(self.model_dir, 'lightgcn_item_embeddings.npy')
            
            np.save(user_emb_path, self.user_embeddings)
            np.save(item_emb_path, self.item_embeddings)
            
            print(f"用户嵌入已保存: {user_emb_path}")
            print(f"物品嵌入已保存: {item_emb_path}")
            
            # 初始化行为追踪器
            if self.use_behavior_tracking:
                self._init_behavior_tracker()
    
    def _init_behavior_tracker(self):
        """
        初始化用户行为追踪器
        使用电影嵌入作为基础
        """
        if self.item_embeddings is None:
            print("警告: 物品嵌入未加载，无法初始化行为追踪器")
            return

        # 构建电影ID到向量的映射
        movie_embeddings = {i: self.item_embeddings[i] for i in range(len(self.item_embeddings))}

        # 创建行为追踪器
        # 使用与前端匹配的0-10分制评分权重，映射到三个等级
        self.behavior_tracker = UserBehaviorTracker(
            decay_days=self.decay_days,
            persist_dir=self.model_dir,  # 持久化目录
            behavior_weights={
                'like': 1.0,             # 👍 喜欢 - 最高权重
                'favorite': 0.8,         # ⭐ 收藏
                'rate_high': 0.7,        # 高评分 (8-10分)
                'rate_medium': 0.5,      # 中评分 (5-7分)
                'rate_low': 0.3,         # 低评分 (1-4分)
                'click': 0.3,            # 👆 点击 - 最低权重
                'view': 0.3,             # 观看
                'watch': 0.6,            # 完整观看
                'share': 0.6,            # 📤 分享
                'comment': 0.5,          # 💬 评论
            }
        )
        # 设置电影嵌入
        self.behavior_tracker.set_movie_embeddings(movie_embeddings)
        self.behavior_tracker.set_movie_embeddings(movie_embeddings)
        
        print(f"✓ 行为追踪器已初始化 (衰减天数: {self.decay_days})")
    
    def record_user_behavior(self, user_id, movie_id, behavior_type, metadata=None):
        """
        记录用户行为
        
        参数:
            user_id: 用户ID (int)
            movie_id: 电影ID (int, 0-based)
            behavior_type: 行为类型 (str)
                - click: 点击/浏览
                - view: 观看
                - favorite: 收藏/喜欢
                - watch: 完整观看
                - rate: 评分 (需在 metadata 中提供 rating 值)
                - share: 分享
            metadata: 额外元数据 (dict)
                - rating: 评分值 (1-5)
                - watch_duration: 观看时长
                等
        
        返回:
            bool: 是否记录成功
        """
        if not self.use_behavior_tracking:
            print("警告: 行为追踪未启用")
            return False
        
        if self.behavior_tracker is None:
            print("警告: 行为追踪器未初始化")
            return False
        
        return self.behavior_tracker.record_behavior(user_id, movie_id, behavior_type, metadata)
    
    def load_embeddings(self):
        """
        从文件加载预训练的嵌入
        """
        user_emb_path = os.path.join(self.model_dir, 'lightgcn_user_embeddings.npy')
        item_emb_path = os.path.join(self.model_dir, 'lightgcn_item_embeddings.npy')

        if os.path.exists(user_emb_path) and os.path.exists(item_emb_path):
            self.user_embeddings = np.load(user_emb_path)
            self.item_embeddings = np.load(item_emb_path)
            print(f"已加载预训练嵌入: 用户={self.user_embeddings.shape}, 物品={self.item_embeddings.shape}")

            # 加载评分数据
            self.load_ratings_data()

            # 将电影嵌入设置到行为追踪器
            if self.use_behavior_tracking:
                self._init_behavior_tracker()

            return True
        else:
            print("未找到预训练嵌入文件，需要先训练模型")
            return False
    
    def recommend(self, user_history, top_k=10, exclude_seen=True, user_id=None, use_dynamic=False):
        """
        基于用户历史推荐电影
        
        参数:
            user_history: 用户历史观看的电影 ID 列表（0-based）
            top_k: 返回 top-k 推荐
            exclude_seen: 是否排除已看过的电影
            user_id: 用户ID (用于动态推荐)
            use_dynamic: 是否使用动态用户向量推荐
        
        返回:
            List[Tuple[int, float]]: [(movie_id, score), ...]
        """
        if self.item_embeddings is None:
            raise ValueError("需要先训练模型或加载嵌入")
        
        # 尝试使用动态推荐
        if use_dynamic and user_id is not None and self.use_behavior_tracking:
            if self.behavior_tracker is not None:
                return self._recommend_dynamic(user_id, top_k, exclude_seen, user_history)
        
        # 如果用户没有历史记录，返回热门电影
        if not user_history:
            return self._get_popular_movies(top_k)
        
        # 计算用户历史中所有电影的平均嵌入作为用户画像
        user_emb = np.mean([self.item_embeddings[mid] for mid in user_history if mid < len(self.item_embeddings)], axis=0)
        
        # 计算所有电影的相似度
        similarities = cosine_similarity([user_emb], self.item_embeddings)[0]
        
        # 排除已看过的电影
        if exclude_seen:
            for mid in user_history:
                if mid < len(similarities):
                    similarities[mid] = -1
        
        # 获取 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]
        
        return list(zip(top_indices.tolist(), top_scores.tolist()))
    
    def _recommend_dynamic(self, user_id, top_k=10, exclude_seen=True, user_history=None):
        """
        基于动态用户向量推荐电影（推荐给有行为记录的用户）

        参数:
            user_id: 用户ID
            top_k: 返回 top-k 推荐
            exclude_seen: 是否排除已看过的电影
            user_history: 用户历史（用于排除）

        返回:
            List[Tuple[int, float]]: [(movie_id, score), ...]
        """
        if self.item_embeddings is None:
            raise ValueError("需要先训练模型或加载嵌入")

        if self.behavior_tracker is None:
            raise ValueError("行为追踪器未初始化")

        # 获取预训练用户嵌入
        pretrained_emb = None
        if self.user_embeddings is not None and user_id < len(self.user_embeddings):
            pretrained_emb = self.user_embeddings[user_id]

        # 计算动态用户向量（加权融合预训练嵌入和行为向量）
        user_emb = self.behavior_tracker.compute_user_vector(
            user_id,
            pretrained_embedding=pretrained_emb
        )

        # 如果没有行为数据且没有预训练嵌入，回退到静态推荐
        if user_emb is None:
            print(f"用户 {user_id} 行为数据不足且无预训练嵌入，使用静态推荐")
            if user_history:
                return self.recommend(user_history, top_k, exclude_seen)
            else:
                return self._get_popular_movies(top_k)
        
        # 计算所有电影的相似度
        similarities = cosine_similarity([user_emb], self.item_embeddings)[0]
        
        # 排除已看过的电影
        if exclude_seen:
            # 排除历史记录中的电影
            if user_history:
                for mid in user_history:
                    if mid < len(similarities):
                        similarities[mid] = -1
            
            # 排除行为记录中的电影
            if user_id in self.behavior_tracker.user_behaviors:
                for movie_id in self.behavior_tracker.user_behaviors[user_id].keys():
                    if movie_id < len(similarities):
                        similarities[movie_id] = -1
        
        # 获取 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]

        return list(zip(top_indices.tolist(), top_scores.tolist()))

    def save_ratings_data(self):
        """
        保存评分数据到文件
        """
        if self.ratings_data is None:
            return False

        try:
            ratings_path = os.path.join(self.model_dir, 'lightgcn_ratings_data.npy')
            # 使用 object 类型保存列表数据
            np.save(ratings_path, np.array(self.ratings_data, dtype=object))
            print(f"已保存评分数据: {len(self.ratings_data)} 条记录")
            return True
        except Exception as e:
            print(f"保存评分数据失败: {e}")
            return False

    def load_ratings_data(self):
        """
        从文件加载评分数据
        """
        try:
            ratings_path = os.path.join(self.model_dir, 'lightgcn_ratings_data.npy')
            if os.path.exists(ratings_path):
                self.ratings_data = list(np.load(ratings_path, allow_pickle=True))
                print(f"已加载评分数据: {len(self.ratings_data)} 条记录")
                return True
            else:
                print("未找到评分数据文件")
                return False
        except Exception as e:
            print(f"加载评分数据失败: {e}")
            return False

    def find_similar_movies(self, movie_id, top_k=10):
        """
        查找与指定电影相似的电影
        
        参数:
            movie_id: 电影 ID（0-based）
            top_k: 返回 top-k 相似电影
        """
        if self.item_embeddings is None:
            raise ValueError("需要先训练模型或加载嵌入")
        
        if movie_id >= len(self.item_embeddings):
            return []
        
        # 计算所有电影与目标电影的相似度
        similarities = cosine_similarity(
            [self.item_embeddings[movie_id]], 
            self.item_embeddings
        )[0]
        
        # 排除自己
        similarities[movie_id] = -1
        
        # 获取 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]
        
        return list(zip(top_indices.tolist(), top_scores.tolist()))
    
    def _get_popular_movies(self, top_k=10):
        """
        获取热门电影（基于评分统计）

        计算逻辑：
        1. 统计每部电影的评分次数
        2. 计算每部电影的平均评分
        3. 综合评分次数和平均评分进行排序
           - 综合分数 = 评分次数权重 * log(评分次数) + 平均评分权重 * 平均评分
        """
        if self.ratings_data is None:
            raise ValueError("需要先训练模型以加载评分数据")
        
        # 统计每部电影的评分次数和总分
        movie_stats = {}
        for user_id, item_id, rating in self.ratings_data:
            if item_id not in movie_stats:
                movie_stats[item_id] = {'count': 0, 'total': 0.0}
            movie_stats[item_id]['count'] += 1
            movie_stats[item_id]['total'] += rating
        
        # 计算平均评分和综合分数
        popular_movies = []
        for movie_id, stats in movie_stats.items():
            avg_rating = stats['total'] / stats['count']
            # 综合分数：结合评分次数（热度）和平均评分（质量）
            # 使用 log(count) 避免评分次数的影响过大
            popularity_score = 0.6 * np.log(stats['count']) + 0.4 * avg_rating
            popular_movies.append((movie_id, popularity_score, stats['count'], avg_rating))
        
        # 按综合分数降序排序
        popular_movies.sort(key=lambda x: x[1], reverse=True)
        
        # 返回 top-k
        return [(mid, float(score)) for mid, score, _, _ in popular_movies[:top_k]]
