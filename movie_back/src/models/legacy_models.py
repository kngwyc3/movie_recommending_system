"""
电影数据模型
包含电影数据和数据库操作方法
使用 ChromaDB 进行数据存储和检索
"""

import chromadb
from chromadb.config import Settings
import os
import json
from datetime import datetime


class MoviesDatabase:
    """电影数据库类"""
    
    def __init__(self):
        # 初始化 ChromaDB 客户端
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建或获取电影集合
        try:
            self.collection = self.chroma_client.get_collection(name="movies")
            print("✅ 已连接到现有的电影数据库集合")
        except:
            self.collection = self.chroma_client.create_collection(
                name="movies",
                metadata={"description": "电影信息数据库，包含基本信息和embedding用于RAG检索"}
            )
            print("✅ 创建了新的电影数据库集合")
            # 初始化数据
            self._init_movie_data()
        
        # 所有分类列表
        self.categories = ['全部', '科幻', '动作', '冒险', '悬疑', '爱情', '动画']
    
    def _init_movie_data(self):
        """初始化电影数据到 ChromaDB"""
        hot_movies = [
            {
                'id': 1,
                'title': '黑客帝国',
                'image': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 9.5,
                'badge': '强烈推荐',
                'description': '在未来世界，黑客尼奥发现人类生活在由机器创造的虚拟现实中，他必须选择是继续活在幻象中，还是面对残酷的现实。',
                'year': 1999,
                'director': '沃卓斯基姐妹',
                'cast': ['基努·里维斯', '劳伦斯·菲什伯恩', '凯瑞-安·莫斯']
            },
            {
                'id': 2,
                'title': '阿凡达',
                'image': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 9.2,
                'badge': '热门',
                'description': '前海军陆战队员杰克·萨利来到潘多拉星球，通过阿凡达技术与纳美人接触，在美丽的外星世界展开一段史诗般的冒险。',
                'year': 2009,
                'director': '詹姆斯·卡梅隆',
                'cast': ['萨姆·沃辛顿', '佐伊·索尔达娜', '西格妮·韦弗']
            },
            {
                'id': 3,
                'title': '沙丘',
                'image': 'https://images.unsplash.com/photo-1478720568477-152d9b164e63?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 8.8,
                'description': '年轻的保罗·厄崔迪前往宇宙中最危险的星球，为了家族的未来和人民的命运而战。',
                'year': 2021,
                'director': '丹尼斯·维伦纽瓦',
                'cast': ['提莫西·查拉梅', '赞达亚', '奥斯卡·伊萨克']
            },
            {
                'id': 4,
                'title': '盗梦空间',
                'image': 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 9.3,
                'badge': '新片',
                'description': '专业窃贼柯布通过潜入他人梦境窃取机密，这次他要完成一项不可能的任务：植入想法。',
                'year': 2010,
                'director': '克里斯托弗·诺兰',
                'cast': ['莱昂纳多·迪卡普里奥', '玛丽昂·歌迪亚', '渡边谦']
            },
            {
                'id': 5,
                'title': '银翼杀手2049',
                'image': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 8.9,
                'description': '新一代银翼杀手K发现了一个埋藏已久的秘密，这个秘密可能会颠覆整个社会秩序。',
                'year': 2017,
                'director': '丹尼斯·维伦纽瓦',
                'cast': ['瑞恩·高斯林', '哈里森·福特', '安娜·德·阿玛斯']
            },
            {
                'id': 6,
                'title': '2001太空漫游',
                'image': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 9.0,
                'badge': '经典',
                'description': '一部开创性的科幻史诗，探索人类进化、人工智能和外星生命的终极奥秘。',
                'year': 1968,
                'director': '斯坦利·库布里克',
                'cast': ['凯尔·杜拉', '加里·洛克伍德']
            },
            {
                'id': 7,
                'title': '机械姬',
                'image': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 8.5,
                'description': '年轻程序员受邀参加一项突破性实验：评估一个拥有完美人类外表的人工智能机器人。',
                'year': 2014,
                'director': '亚力克斯·嘉兰',
                'cast': ['艾丽西亚·维坎德', '多姆纳尔·格里森', '奥斯卡·伊萨克']
            },
            {
                'id': 8,
                'title': '降临',
                'image': 'https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 8.7,
                'badge': '精选',
                'description': '语言学家路易丝受命与神秘外星访客沟通，在学习他们语言的过程中，她的世界观发生了翻天覆地的变化。',
                'year': 2016,
                'director': '丹尼斯·维伦纽瓦',
                'cast': ['艾米·亚当斯', '杰瑞米·雷纳', '福里斯特·惠特克']
            }
        ]
        
        # 最新上映电影数据
        new_movies = [
            {
                'id': 9,
                'title': '星际穿越2',
                'image': 'https://images.unsplash.com/photo-1616530940355-351fabd9524b?w=400&h=600&fit=crop',
                'genre': '科幻',
                'rating': 9.1,
                'badge': '新片',
                'description': '库珀再次穿越虫洞，探索更深层的宇宙奥秘，寻找人类文明的终极答案。',
                'year': 2024,
                'director': '克里斯托弗·诺兰',
                'cast': ['马修·麦康纳', '安妮·海瑟薇', '杰西卡·查斯坦']
            },
            {
                'id': 10,
                'title': '赛博朋克2077',
                'image': 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?w=400&h=600&fit=crop',
                'genre': '动作',
                'rating': 8.6,
                'description': '在未来的夜之城，雇佣兵V为了生存和自由，在霓虹闪烁的街道上展开激烈战斗。',
                'year': 2024,
                'director': '约翰·卡梅隆',
                'cast': ['基努·里维斯', '艾玛·斯通']
            },
            {
                'id': 11,
                'title': '银河护卫队3',
                'image': 'https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400&h=600&fit=crop',
                'genre': '冒险',
                'rating': 8.8,
                'badge': '热门',
                'description': '银河护卫队面临前所未有的挑战，他们必须团结一致，保护宇宙的和平。',
                'year': 2023,
                'director': '詹姆斯·古恩',
                'cast': ['克里斯·帕拉特', '佐伊·索尔达娜', '戴夫·巴蒂斯塔']
            },
            {
                'id': 12,
                'title': '变形金刚7',
                'image': 'https://images.unsplash.com/photo-1535016120720-40c646be5580?w=400&h=600&fit=crop',
                'genre': '动作',
                'rating': 8.4,
                'description': '汽车人与霸天虎的战斗延续到新的战场，人类再次卷入这场机器人之间的史诗战争。',
                'year': 2024,
                'director': '迈克尔·贝',
                'cast': ['马克·沃尔伯格', '伊莎贝拉·莫奈']
            }
        ]
        
        # 特色推荐电影
        featured_movie = {
            'id': 13,
            'title': '星际穿越',
            'image': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1920',
            'genre': '科幻',
            'rating': 9.4,
            'badge': '强烈推荐',
            'description': '在不久的将来,地球气候恶化,人类面临生存危机。一组宇航员通过虫洞穿越太空,寻找人类的新家园。一场关于爱、牺牲与时空的史诗之旅。',
            'year': 2014,
            'director': '克里斯托弗·诺兰',
            'cast': ['马修·麦康纳', '安妮·海瑟薇', '杰西卡·查斯坦', '迈克尔·凯恩']
        }
        
        # 合并所有电影数据
        all_movies = hot_movies + new_movies + [featured_movie]
        
        # 准备数据存储到 ChromaDB
        ids = []
        documents = []  # 用于语义搜索的文本
        metadatas = []  # 存储完整的电影信息
        
        for movie in all_movies:
            movie_id = str(movie['id'])
            ids.append(movie_id)
            
            # 创建文档文本（用于生成 embedding）
            doc_text = f"标题: {movie['title']}\n"
            doc_text += f"类型: {movie['genre']}\n"
            doc_text += f"年份: {movie['year']}\n"
            doc_text += f"导演: {movie['director']}\n"
            if 'cast' in movie:
                doc_text += f"演员: {', '.join(movie['cast'])}\n"
            doc_text += f"简介: {movie['description']}"
            documents.append(doc_text)
            
            # 准备元数据（存储完整的电影信息）
            metadata = {
                'id': movie['id'],
                'title': movie['title'],
                'image': movie['image'],
                'genre': movie['genre'],
                'rating': movie['rating'],
                'description': movie['description'],
                'year': movie['year'],
                'director': movie['director'],
                'is_hot': movie['id'] <= 8,  # ID 1-8 为热门电影
                'is_new': 9 <= movie['id'] <= 12,  # ID 9-12 为最新电影
                'is_featured': movie['id'] == 13,  # ID 13 为特色推荐
            }
            
            # 添加可选字段
            if 'badge' in movie:
                metadata['badge'] = movie['badge']
            if 'cast' in movie:
                metadata['cast'] = json.dumps(movie['cast'], ensure_ascii=False)
            
            metadatas.append(metadata)
        
        # 批量添加到 ChromaDB
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"✅ 成功初始化 {len(all_movies)} 部电影数据到 ChromaDB")
        except Exception as e:
            print(f"❌ 初始化电影数据失败: {str(e)}")
    
    def _format_movie(self, metadata):
        """格式化电影数据"""
        movie = {
            'id': metadata['id'],
            'title': metadata['title'],
            'image': metadata['image'],
            'genre': metadata['genre'],
            'rating': metadata['rating'],
            'description': metadata['description'],
            'year': metadata['year'],
            'director': metadata['director'],
        }
        
        # 添加可选字段
        if 'badge' in metadata:
            movie['badge'] = metadata['badge']
        if 'cast' in metadata:
            movie['cast'] = json.loads(metadata['cast'])
        
        return movie
    
    def get_hot_movies(self, page=1, per_page=8):
        """获取热门电影列表（分页）"""
        try:
            # 查询热门电影 (ID 1-8)
            results = self.collection.get(
                where={"is_hot": True},
                limit=per_page,
                offset=(page - 1) * per_page
            )
            
            movies = [self._format_movie(meta) for meta in results['metadatas']]
            return movies
        except Exception as e:
            print(f"❌ 获取热门电影失败: {str(e)}")
            return []
    
    def get_new_movies(self, page=1, per_page=4):
        """获取最新电影列表（分页）"""
        try:
            # 查询最新电影 (ID 9-12)
            results = self.collection.get(
                where={"is_new": True},
                limit=per_page,
                offset=(page - 1) * per_page
            )
            
            movies = [self._format_movie(meta) for meta in results['metadatas']]
            return movies
        except Exception as e:
            print(f"❌ 获取最新电影失败: {str(e)}")
            return []
    
    def get_featured_movie(self):
        """获取特色推荐电影"""
        try:
            # 查询特色电影 (ID 13)
            results = self.collection.get(
                where={"is_featured": True},
                limit=1
            )
            
            if results['metadatas']:
                return self._format_movie(results['metadatas'][0])
            return None
        except Exception as e:
            print(f"❌ 获取特色电影失败: {str(e)}")
            return None
    
    def get_all_movies(self, page=1, per_page=12):
        """获取所有电影列表（分页）"""
        try:
            # 查询所有电影（除了特色电影）
            results = self.collection.get(
                where={"is_featured": False},
                limit=per_page,
                offset=(page - 1) * per_page
            )
            
            movies = [self._format_movie(meta) for meta in results['metadatas']]
            return movies
        except Exception as e:
            print(f"❌ 获取所有电影失败: {str(e)}")
            return []
    
    def get_movies_by_category(self, category, page=1, per_page=12):
        """根据分类筛选电影"""
        try:
            # 如果是"全部"分类,返回所有电影(除了特色电影)
            if category == '全部':
                where_clause = {"is_featured": False}
            else:
                # 按分类筛选 - 使用 $and 操作符
                where_clause = {
                    "$and": [
                        {"genre": {"$eq": category}},
                        {"is_featured": {"$eq": False}}
                    ]
                }
            
            results = self.collection.get(
                where=where_clause,
                limit=per_page,
                offset=(page - 1) * per_page
            )
            
            movies = [self._format_movie(meta) for meta in results['metadatas']]
            return movies
        except Exception as e:
            print(f"❌ 按分类获取电影失败: {str(e)}")
            return []
    
    def get_category_count(self, category):
        """获取指定分类的电影数量"""
        try:
            if category == '全部':
                where_clause = {"is_featured": False}
            else:
                # 使用 $and 操作符
                where_clause = {
                    "$and": [
                        {"genre": {"$eq": category}},
                        {"is_featured": {"$eq": False}}
                    ]
                }
            
            results = self.collection.get(where=where_clause)
            return len(results['ids'])
        except Exception as e:
            print(f"❌ 获取分类数量失败: {str(e)}")
            return 0
    
    def get_all_categories(self):
        """获取所有分类"""
        return self.categories
    
    def search_movies(self, query, page=1, per_page=12):
        """搜索电影（使用语义搜索和关键词匹配）"""
        try:
            # 使用 ChromaDB 的语义搜索功能
            results = self.collection.query(
                query_texts=[query],
                n_results=per_page * page,  # 获取足够的结果用于分页
                where={"is_featured": False}
            )
            
            if not results['metadatas'] or len(results['metadatas'][0]) == 0:
                return []
            
            # 分页
            start = (page - 1) * per_page
            end = start + per_page
            metadata_list = results['metadatas'][0][start:end]
            
            movies = [self._format_movie(meta) for meta in metadata_list]
            return movies
        except Exception as e:
            print(f"❌ 搜索电影失败: {str(e)}")
            return []
    
    def get_search_count(self, query):
        """获取搜索结果数量"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=100,  # 获取最多100条结果
                where={"is_featured": False}
            )
            
            if not results['metadatas'] or len(results['metadatas'][0]) == 0:
                return 0
            
            return len(results['metadatas'][0])
        except Exception as e:
            print(f"❌ 获取搜索数量失败: {str(e)}")
            return 0
    
    def get_movie_by_id(self, movie_id):
        """根据ID获取电影详情"""
        try:
            results = self.collection.get(
                ids=[str(movie_id)]
            )
            
            if results['metadatas'] and len(results['metadatas']) > 0:
                return self._format_movie(results['metadatas'][0])
            
            return None
        except Exception as e:
            print(f"❌ 获取电影详情失败: {str(e)}")
            return None
    
    def chat_with_assistant(self, question, conversation_history=None):
        """电影智能助手聊天功能（基于RAG）"""
        try:
            # 使用语义搜索找到相关电影
            results = self.collection.query(
                query_texts=[question],
                n_results=3  # 获取最相关的3部电影
            )
            
            # 构造上下文
            context_movies = []
            if results['metadatas'] and len(results['metadatas'][0]) > 0:
                for meta in results['metadatas'][0]:
                    movie = self._format_movie(meta)
                    context_movies.append(movie)
            
            # 这里可以集成大语言模型，目前先返回简单的回复
            response = {
                'answer': f'我找到了 {len(context_movies)} 部与您问题相关的电影。',
                'related_movies': context_movies,
                'question': question
            }
            
            return response
        except Exception as e:
            print(f"❌ 智能助手处理失败: {str(e)}")
            return {
                'answer': '抱歉，我遇到了一些问题，请稍后再试。',
                'related_movies': [],
                'question': question
            }


# 创建全局数据库实例
movies_db = MoviesDatabase()
