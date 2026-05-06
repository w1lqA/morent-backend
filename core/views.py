from rest_framework.views import APIView
from rest_framework.response import Response
from .singleton import DatabaseConnection, AuthService

class SingletonDemoView(APIView):
    """демонстрация работы Singleton паттерна"""

    def get(self, request):
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        auth1 = AuthService()
        auth2 = AuthService()

        return Response({
            'message': 'singleton pattern works',
            'database_connection': {
                'db1_id': id(db1),
                'db2_id': id(db2),
                'is_same': id(db1) == id(db2)
            },
            'auth_service': {
                'auth1_id': id(auth1),
                'auth2_id': id(auth2),
                'is_same': id(auth1) == id(auth2)
            }
        })