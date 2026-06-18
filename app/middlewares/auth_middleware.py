from flask_jwt_extended import verify_jwt_in_request, get_jwt


def verificar_role(roles_permitidas):

    def decorator(function):

        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            role = get_jwt().get("role")
            if role not in roles_permitidas:
                return {
                    "success": False,
                    "message": "Acesso negado."
                }, 403
            wrapper.__name__ = function.__name__
            return function(*args, **kwargs)
        return wrapper

    return decorator
