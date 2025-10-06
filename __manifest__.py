{
    'name': 'Sistema CRUD de Usuarios',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Sistema completo CRUD para gestión de usuarios con interfaz web',
    'description': """
        Módulo para gestión completa de usuarios con operaciones CRUD
        =============================================================

        Características:
        * Crear, leer, actualizar y eliminar usuarios
        * Subida de fotos de perfil
        * Interfaz web responsive
        * Reportes de usuarios
        * Gestión de estados (activo/inactivo)
    """,
    'author': 'Emilio',
    'website': 'http://localhost:8069/web',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/usuario_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'crud_usuarios/static/src/css/crud_users.css',
            'crud_usuarios/static/src/js/crud_users.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
