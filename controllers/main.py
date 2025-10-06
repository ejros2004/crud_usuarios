from odoo import http
from odoo.http import request
import datetime
import base64

class UsuarioController(http.Controller):
    
    @http.route('/usuarios', type='http', auth='public', website=True)
    def pagina_usuarios(self, **kwargs):
        usuarios = request.env['crud.usuario'].sudo().search([])
        return request.render('crud_usuarios.pagina_principal', {
            'usuarios': usuarios,
            'datetime': datetime
        })
    
    @http.route('/crear_usuario', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def crear_usuario(self, **post):
        try:
            campos_obligatorios = ['nombre', 'email', 'telefono', 'direccion']
            for campo in campos_obligatorios:
                if not post.get(campo):
                    return request.redirect('/usuarios')
            
            vals = {
                'nombre': post.get('nombre'),
                'email': post.get('email'),
                'telefono': post.get('telefono'),
                'direccion': post.get('direccion'),
                'activo': True,
            }
            
            # Manejar la foto
            foto_file = post.get('foto')
            if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
                try:
                    file_data = foto_file.read()
                    if file_data:
                        vals['foto'] = base64.b64encode(file_data)
                except Exception:
                    pass
            
            request.env['crud.usuario'].sudo().create(vals)
            
        except Exception:
            pass
        
        return request.redirect('/usuarios')
    
    @http.route('/editar_usuario/<model("crud.usuario"):usuario>', type='http', auth='public', website=True)
    def editar_usuario_form(self, usuario, **kwargs):
        return request.render('crud_usuarios.formulario_edicion', {
            'usuario': usuario
        })
    
    @http.route('/actualizar_usuario/<model("crud.usuario"):usuario>', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def actualizar_usuario(self, usuario, **post):
        try:
            campos_obligatorios = ['nombre', 'email', 'telefono', 'direccion']
            for campo in campos_obligatorios:
                if not post.get(campo):
                    return request.redirect('/usuarios')
            
            vals = {
                'nombre': post.get('nombre'),
                'email': post.get('email'),
                'telefono': post.get('telefono'),
                'direccion': post.get('direccion'),
                'activo': post.get('activo') == 'on',
            }
            
            # Manejar la foto
            foto_file = post.get('foto')
            if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
                try:
                    file_data = foto_file.read()
                    if file_data:
                        vals['foto'] = base64.b64encode(file_data)
                except Exception:
                    pass
            elif post.get('eliminar_foto'):
                vals['foto'] = False
            
            usuario.sudo().write(vals)
                
        except Exception:
            pass
        
        return request.redirect('/usuarios')
    
    @http.route('/eliminar_usuario/<model("crud.usuario"):usuario>', type='http', auth='public', website=True, csrf=False)
    def eliminar_usuario(self, usuario):
        usuario.sudo().unlink()
        return request.redirect('/usuarios')
    
    @http.route('/reporte_usuarios', type='http', auth='public', website=True)
    def reporte_usuarios(self):
        usuarios = request.env['crud.usuario'].sudo().search([])
        
        total_usuarios = len(usuarios)
        usuarios_activos = len([u for u in usuarios if u.activo])
        usuarios_inactivos = len([u for u in usuarios if not u.activo])
        
        return request.render('crud_usuarios.reporte_usuarios', {
            'usuarios': usuarios,
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': usuarios_inactivos,
            'fecha_reporte': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
            'datetime': datetime
        })