"""
ViewModels package
"""
from .movie_viewmodel import movie_viewmodel, MovieViewModel
from .auth_viewmodel import auth_viewmodel, AuthViewModel
from .user_viewmodel import user_viewmodel, UserViewModel
from .ai_viewmodel import ai_viewmodel, AIViewModel

__all__ = [
    'movie_viewmodel', 'MovieViewModel',
    'auth_viewmodel', 'AuthViewModel',
    'user_viewmodel', 'UserViewModel',
    'ai_viewmodel', 'AIViewModel'
]
