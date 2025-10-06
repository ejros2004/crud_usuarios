from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import secrets
import string
import logging

_logger = logging.getLogger(__name__)

class CRUDUsuario(models.Model):
    _name = 'crud.usuario'
    _description = 'Usuario del Sistema CRUD'
    _order = 'fecha_registro desc'
    
    nombre = fields.Char(string='Nombre Completo', required=True)
    email = fields.Char(string='Email', required=True)
    telefono = fields.Char(string='Teléfono', required=True, size=15)
    direccion = fields.Text(string='Dirección', required=True)
    fecha_registro = fields.Datetime(string='Fecha de Registro', default=fields.Datetime.now)
    activo = fields.Boolean(string='Activo', default=True)
    foto = fields.Binary(string='Foto del Usuario', attachment=True)
    
    # Campos para sincronización con usuario de Odoo
    odoo_user_id = fields.Many2one('res.users', string='Usuario Odoo Asociado', readonly=True)
    password_cifrada = fields.Char(string='Contraseña Cifrada', readonly=True)
    password_temporal = fields.Char(string='Contraseña Temporal', readonly=True, 
                                   help='Contraseña temporal en texto plano (solo visible una vez)')

    def _generar_password_temporal(self):
        """Generar una contraseña temporal segura"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        return password

    def _cifrar_password(self, password):
        """Cifrar contraseña usando el método de Odoo"""
        try:
            if password:
                return self.env['res.users']._crypt_context().encrypt(password)
        except Exception as e:
            _logger.error("Error cifrando contraseña: %s", str(e))
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribir create para manejar múltiples registros"""
        records = super(CRUDUsuario, self).create(vals_list)
        for record in records:
            # Generar contraseña temporal para cada registro
            password_temporal = record._generar_password_temporal()
            password_cifrada = record._cifrar_password(password_temporal)
            
            if password_cifrada:
                record.write({
                    'password_cifrada': password_cifrada,
                    'password_temporal': password_temporal
                })
            
            # Crear usuario de Odoo automáticamente
            record._crear_usuario_odoo(password_temporal)
            
            # Limpiar contraseña temporal después de crear el usuario Odoo
            record.write({'password_temporal': False})
        
        return records

    def write(self, vals):
        result = super(CRUDUsuario, self).write(vals)
        
        # Sincronizar con usuario de Odoo si existe
        for record in self:
            if record.odoo_user_id:
                record._sincronizar_con_odoo_user()
        
        return result

    def _crear_usuario_odoo(self, password):
        """Crear usuario de Odoo asociado automáticamente"""
        for record in self:
            if record.email:
                # Verificar si ya existe un usuario con este email
                existing_user = self.env['res.users'].search([('login', '=', record.email)], limit=1)
                
                if existing_user:
                    record.odoo_user_id = existing_user.id
                    record._sincronizar_con_odoo_user()
                else:
                    # Crear nuevo usuario de Odoo
                    user_vals = {
                        'name': record.nombre,
                        'login': record.email,
                        'email': record.email,
                        'phone': record.telefono,
                        'active': record.activo,
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                    }
                    
                    if record.foto:
                        user_vals['image_1920'] = record.foto
                    
                    try:
                        new_user = self.env['res.users'].with_context(no_reset_password=True).create(user_vals)
                        new_user.password = password
                        record.odoo_user_id = new_user.id
                    except Exception as e:
                        _logger.error("Error al crear usuario Odoo: %s", str(e))

    def _sincronizar_con_odoo_user(self):
        """Sincronizar datos con el usuario de Odoo asociado"""
        for record in self:
            if record.odoo_user_id:
                update_vals = {
                    'name': record.nombre,
                    'login': record.email,
                    'email': record.email,
                    'phone': record.telefono,
                    'active': record.activo,
                }
                
                if record.foto:
                    update_vals['image_1920'] = record.foto
                
                try:
                    record.odoo_user_id.write(update_vals)
                except Exception as e:
                    _logger.error("Error al actualizar usuario Odoo: %s", str(e))

    def action_obtener_password_temporal(self):
        """Generar y obtener una contraseña temporal"""
        self.ensure_one()
        
        # Generar nueva contraseña temporal
        nueva_password = self._generar_password_temporal()
        
        # Cifrar la nueva contraseña
        password_cifrada = self._cifrar_password(nueva_password)
        
        # Actualizar contraseña en usuario de Odoo
        if self.odoo_user_id:
            self.odoo_user_id.password = nueva_password
        
        # Guardar contraseñas (cifrada y temporal)
        self.write({
            'password_cifrada': password_cifrada,
            'password_temporal': nueva_password
        })
        
        # Mostrar notificación con la contraseña temporal
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contraseña Temporal Generada',
                'message': f'Contraseña temporal para {self.nombre}: {nueva_password}',
                'type': 'success',
                'sticky': True,
            }
        }

    def action_restablecer_password(self):
        """Restablecer contraseña del usuario y mostrar temporal"""
        self.ensure_one()
        
        # Generar nueva contraseña temporal
        nueva_password = self._generar_password_temporal()
        
        # Cifrar la nueva contraseña
        password_cifrada = self._cifrar_password(nueva_password)
        
        # Actualizar contraseña en usuario de Odoo
        if self.odoo_user_id:
            self.odoo_user_id.password = nueva_password
        
        # Guardar contraseñas (cifrada y temporal)
        self.write({
            'password_cifrada': password_cifrada,
            'password_temporal': nueva_password
        })
        
        # Mostrar notificación con la contraseña temporal
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contraseña Restablecida',
                'message': f'Se ha generado una nueva contraseña para {self.nombre}: {nueva_password}',
                'type': 'success',
                'sticky': True,
            }
        }

    def action_cambiar_password_wizard(self):
        """Abrir wizard para cambiar contraseña"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cambiar Contraseña',
            'res_model': 'cambiar.password.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_usuario_id': self.id,
            }
        }

    def name_get(self):
        """Mostrar nombre y email en la vista"""
        result = []
        for record in self:
            name = f"{record.nombre} ({record.email})"
            result.append((record.id, name))
        return result

    # Constraints de validación
    @api.constrains('nombre')
    def _check_nombre(self):
        for record in self:
            if record.nombre:
                if len(record.nombre.strip()) < 2:
                    raise ValidationError('El nombre debe tener al menos 2 caracteres')
                if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', record.nombre):
                    raise ValidationError('El nombre solo puede contener letras, espacios, apostrofes y guiones')

    @api.constrains('email')
    def _check_email_unique_and_format(self):
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.email):
                    raise ValidationError('Por favor ingrese un email válido (formato: usuario@dominio.com)')
                
                existing = self.search([
                    ('email', '=ilike', record.email),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError('El email ya está registrado en el sistema')

    @api.constrains('telefono')
    def _check_telefono(self):
        for record in self:
            if record.telefono:
                telefono_limpio = record.telefono.strip()
                if not re.match(r'^[\d+\-\s]+$', telefono_limpio):
                    raise ValidationError('El teléfono solo puede contener números, +, - y espacios')
                digitos = re.findall(r'\d', telefono_limpio)
                if len(digitos) < 8:
                    raise ValidationError('El teléfono debe tener al menos 8 dígitos numéricos')
                if len(telefono_limpio) > 15:
                    raise ValidationError('El teléfono no puede tener más de 15 caracteres')

    @api.constrains('direccion')
    def _check_direccion(self):
        for record in self:
            if record.direccion and len(record.direccion) > 255:
                raise ValidationError('La dirección no puede tener más de 255 caracteres')

    def unlink(self):
        """Eliminar también el usuario de Odoo asociado"""
        for record in self:
            if record.odoo_user_id:
                record.odoo_user_id.unlink()
        return super(CRUDUsuario, self).unlink()