"""
初始化电影数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from config.database import db
from models.movie_model import MovieModel
from repositories.movie_repository import movie_repository


def init_movies():
    """初始化电影数据"""
    
    # 检查数据库是否已有数据
    try:
        existing = db.get_collection().get(limit=1)
        if existing['ids']:
            print("⚠️  数据库已有数据，跳过初始化")
            return
    except:
        pass
    
    # 热门电影数据
    hot_movies = [
        MovieModel(id=1, title='黑客帝国', 
                  image='https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=600&fit=crop',
                  genre='科幻', rating=9.5, badge='强烈推荐',
                  description='在未来世界，黑客尼奥发现人类生活在由机器创造的虚拟现实中，他必须选择是继续活在幻象中，还是面对残酷的现实。',
                  year=1999, director='沃卓斯基姐妹',
                  cast=['基努·里维斯', '劳伦斯·菲什伯恩', '凯瑞-安·莫斯'],
                  is_hot=True),
        
        MovieModel(id=2, title='阿凡达',
                  image='https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&h=600&fit=crop',
                  genre='科幻', rating=9.2, badge='热门',
                  description='前海军陆战队员杰克·萨利来到潘多拉星球，通过阿凡达技术与纳美人接触，在美丽的外星世界展开一段史诗般的冒险。',
                  year=2009, director='詹姆斯·卡梅隆',
                  cast=['萨姆·沃辛顿', '佐伊·索尔达娜', '西格妮·韦弗'],
                  is_hot=True),
        
        MovieModel(id=3, title='沙丘',
                  image='https://images.unsplash.com/photo-1478720568477-152d9b164e63?w=400&h=600&fit=crop',
                  genre='科幻', rating=8.8,
                  description='年轻的保罗·厄崔迪前往宇宙中最危险的星球，为了家族的未来和人民的命运而战。',
                  year=2021, director='丹尼斯·维伦纽瓦',
                  cast=['提莫西·查拉梅', '赞达亚', '奥斯卡·伊萨克'],
                  is_hot=True),
        
        MovieModel(id=4, title='盗梦空间',
                  image='https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=400&h=600&fit=crop',
                  genre='科幻', rating=9.3, badge='新片',
                  description='专业窃贼柯布通过潜入他人梦境窃取机密，这次他要完成一项不可能的任务：植入想法。',
                  year=2010, director='克里斯托弗·诺兰',
                  cast=['莱昂纳多·迪卡普里奥', '玛丽昂·歌迪亚', '渡边谦'],
                  is_hot=True),
        
        MovieModel(id=5, title='银翼杀手2049',
                  image='https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&h=600&fit=crop',
                  genre='科幻', rating=8.9,
                  description='新一代银翼杀手K发现了一个埋藏已久的秘密，这个秘密可能会颠覆整个社会秩序。',
                  year=2017, director='丹尼斯·维伦纽瓦',
                  cast=['瑞恩·高斯林', '哈里森·福特', '安娜·德·阿玛斯'],
                  is_hot=True),
        
        MovieModel(id=6, title='2001太空漫游',
                  image='https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&h=600&fit=crop',
                  genre='科幻', rating=9.0, badge='经典',
                  description='一部开创性的科幻史诗，探索人类进化、人工智能和外星生命的终极奥秘。',
                  year=1968, director='斯坦利·库布里克',
                  cast=['凯尔·杜拉', '加里·洛克伍德'],
                  is_hot=True),
        
        MovieModel(id=7, title='机械姬',
                  image='https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&h=600&fit=crop',
                  genre='科幻', rating=8.5,
                  description='年轻程序员受邀参加一项突破性实验：评估一个拥有完美人类外表的人工智能机器人。',
                  year=2014, director='亚力克斯·嘉兰',
                  cast=['艾丽西亚·维坎德', '多姆纳尔·格里森', '奥斯卡·伊萨克'],
                  is_hot=True),
        
        MovieModel(id=8, title='降临',
                  image='https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=400&h=600&fit=crop',
                  genre='科幻', rating=8.7, badge='精选',
                  description='语言学家路易丝受命与神秘外星访客沟通，在学习他们语言的过程中，她的世界观发生了翻天覆地的变化。',
                  year=2016, director='丹尼斯·维伦纽瓦',
                  cast=['艾米·亚当斯', '杰瑞米·雷纳', '福里斯特·惠特克'],
                  is_hot=True),
    ]
    
    # 最新电影数据
    new_movies = [
        MovieModel(id=9, title='星际穿越2',
                  image='https://images.unsplash.com/photo-1616530940355-351fabd9524b?w=400&h=600&fit=crop',
                  genre='科幻', rating=9.1, badge='新片',
                  description='库珀再次穿越虫洞，探索更深层的宇宙奥秘，寻找人类文明的终极答案。',
                  year=2024, director='克里斯托弗·诺兰',
                  cast=['马修·麦康纳', '安妮·海瑟薇', '杰西卡·查斯坦'],
                  is_new=True),
        
        MovieModel(id=10, title='赛博朋克2077',
                  image='https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?w=400&h=600&fit=crop',
                  genre='动作', rating=8.6,
                  description='在未来的夜之城，雇佣兵V为了生存和自由，在霓虹闪烁的街道上展开激烈战斗。',
                  year=2024, director='约翰·卡梅隆',
                  cast=['基努·里维斯', '艾玛·斯通'],
                  is_new=True),
        
        MovieModel(id=11, title='银河护卫队3',
                  image='https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400&h=600&fit=crop',
                  genre='冒险', rating=8.8, badge='热门',
                  description='银河护卫队面临前所未有的挑战，他们必须团结一致，保护宇宙的和平。',
                  year=2023, director='詹姆斯·古恩',
                  cast=['克里斯·帕拉特', '佐伊·索尔达娜', '戴夫·巴蒂斯塔'],
                  is_new=True),
        
        MovieModel(id=12, title='变形金刚7',
                  image='https://images.unsplash.com/photo-1535016120720-40c646be5580?w=400&h=600&fit=crop',
                  genre='动作', rating=8.4,
                  description='汽车人与霸天虎的战斗延续到新的战场，人类再次卷入这场机器人之间的史诗战争。',
                  year=2024, director='迈克尔·贝',
                  cast=['马克·沃尔伯格', '伊莎贝拉·莫奈'],
                  is_new=True),
    ]
    
    # 特色电影
    featured_movie = MovieModel(
        id=13, title='星际穿越',
        image='https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1920',
        genre='科幻', rating=9.4, badge='强烈推荐',
        description='在不久的将来,地球气候恶化,人类面临生存危机。一组宇航员通过虫洞穿越太空,寻找人类的新家园。一场关于爱、牺牲与时空的史诗之旅。',
        year=2014, director='克里斯托弗·诺兰',
        cast=['马修·麦康纳', '安妮·海瑟薇', '杰西卡·查斯坦', '迈克尔·凯恩'],
        is_featured=True
    )
    
    # 添加所有电影
    all_movies = hot_movies + new_movies + [featured_movie]
    
    for movie in all_movies:
        movie_repository.create(movie)
    
    print(f"✅ 成功初始化 {len(all_movies)} 部电影数据")


if __name__ == '__main__':
    init_movies()
