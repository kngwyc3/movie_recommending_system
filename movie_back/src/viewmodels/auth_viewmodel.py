"""
Auth ViewModel - 认证业务逻辑层
"""
import jwt
import re
from datetime import datetime, timedelta
from repositories.user_repository import user_repository
from models.user_model import UserModel


class AuthViewModel:
    """认证视图模型类"""
    
    # JWT密钥（生产环境应该放在环境变量中）
    SECRET_KEY = "your-secret-key-change-this-in-production"
    
    def register(self, username, email, password):
        """用户注册"""
        # 验证输入
        validation_error = self._validate_registration(username, email, password)
        if validation_error:
            return {'success': False, 'message': validation_error}
        
        # 检查邮箱是否已存在
        if user_repository.email_exists(email):
            return {'success': False, 'message': '该邮箱已被注册'}
        
        # 检查用户名是否已存在
        if user_repository.username_exists(username):
            return {'success': False, 'message': '该用户名已被使用'}
        
        # 生成新用户ID
        user_id = user_repository.get_next_user_id()
        
        # 创建新用户
        new_user = UserModel(
            id=user_id,
            username=username,
            email=email,
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        )
        
        # 设置密码（自动加密）
        new_user.set_password(password)
        
        # 保存到数据库
        created_user = user_repository.create(new_user)
        
        if not created_user:
            return {'success': False, 'message': '注册失败，请稍后重试'}
        
        # 生成token
        token = self._generate_token(created_user.id)
        
        return {
            'success': True,
            'message': '注册成功',
            'data': {
                'user': created_user.to_dict(),
                'token': token
            }
        }
    
    def login(self, email, password):
        """用户登录"""
        # 验证输入
        if not email or not password:
            return {'success': False, 'message': '邮箱和密码不能为空'}
        
        # 查找用户
        user = user_repository.find_by_email(email)
        
        if not user:
            return {'success': False, 'message': '邮箱或密码错误'}
        
        # 验证密码
        if not user.check_password(password):
            return {'success': False, 'message': '邮箱或密码错误'}
        
        # 生成token
        token = self._generate_token(user.id)
        
        return {
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }
    
    def verify_token(self, token):
        """验证token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                return None

            # 检查用户是否存在
            user = user_repository.find_by_id(user_id)
            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def change_password(self, email, old_password, new_password):
        """修改密码"""
        # 验证输入
        if not email or not old_password or not new_password:
            return {'success': False, 'message': '邮箱、旧密码和新密码不能为空'}

        # 查找用户
        user = user_repository.find_by_email(email)

        if not user:
            return {'success': False, 'message': '用户不存在'}

        # 验证旧密码
        if not user.check_password(old_password):
            return {'success': False, 'message': '旧密码错误'}

        # 验证新密码格式
        validation_error = self._validate_password(new_password)
        if validation_error:
            return {'success': False, 'message': validation_error}

        # 检查新密码是否与旧密码相同
        if user.check_password(new_password):
            return {'success': False, 'message': '新密码不能与旧密码相同'}

        # 设置新密码
        user.set_password(new_password)

        # 更新到数据库
        updated_user = user_repository.update(user)

        if not updated_user:
            return {'success': False, 'message': '修改密码失败，请稍后重试'}

        return {
            'success': True,
            'message': '密码修改成功'
        }

    def _validate_password(self, password):
        """验证密码格式"""
        if not password or len(password) == 0:
            return '密码不能为空'

        if len(password) < 6:
            return '密码至少6个字符'

        if len(password) > 30:
            return '密码最多30个字符'

        return None
    
    def _generate_token(self, user_id, expires_in=7):
        """生成JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=expires_in),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')
        return token
    
    def _validate_registration(self, username, email, password):
        """验证注册输入"""
        # 验证用户名
        if not username or len(username.strip()) == 0:
            return '用户名不能为空'
        
        if len(username) < 2:
            return '用户名至少2个字符'
        
        if len(username) > 20:
            return '用户名最多20个字符'
        
        # 验证邮箱
        if not email or len(email.strip()) == 0:
            return '邮箱不能为空'
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return '邮箱格式不正确'
        
        # 验证密码
        if not password or len(password) == 0:
            return '密码不能为空'
        
        if len(password) < 6:
            return '密码至少6个字符'
        
        if len(password) > 30:
            return '密码最多30个字符'
        
        return None


# 创建全局视图模型实例
auth_viewmodel = AuthViewModel()
