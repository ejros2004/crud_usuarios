from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CambiarPasswordWizard(models.TransientModel):
    _name = 'cambiar.password.wizard'
    _description = 'Wizard para cambiar contraseña de usuario'
    
    # Campos del wizard
    usuario_id = fields.Many2one('crud.usuario', string='Usuario', required=True)
    nueva_password = fields.Char(string='Nueva Contraseña', required=True)
    confirmar_password = fields.Char(string='Confirmar Contraseña', required=True)
    
    @api.model
    def default_get(self, fields_list):
        """Obtener valores por defecto del contexto"""
        result = super().default_get(fields_list)
        if self.env.context.get('default_usuario_id'):
            result['usuario_id'] = self.env.context.get('default_usuario_id')
        return result
    
    def action_cambiar_password(self):
        """Cambiar la contraseña del usuario"""
        self.ensure_one()
        
        # Validar que las contraseñas coincidan
        if self.nueva_password != self.confirmar_password:
            raise ValidationError('Las contraseñas no coinciden.')
        
        # Validar longitud mínima de contraseña
        if len(self.nueva_password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        # Cifrar la nueva contraseña
        password_cifrada = self.usuario_id._cifrar_password(self.nueva_password)
        
        # Actualizar contraseña en usuario de Odoo
        if self.usuario_id.odoo_user_id:
            self.usuario_id.odoo_user_id.password = self.nueva_password
        
        # Guardar contraseña cifrada y temporal
        self.usuario_id.write({
            'password_cifrada': password_cifrada,
            'password_temporal': self.nueva_password  # Guardar temporalmente para mostrar
        })
        
        # Mostrar notificación de éxito
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contraseña Cambiada',
                'message': f'Se ha cambiado la contraseña para {self.usuario_id.nombre}: {self.nueva_password}',
                'type': 'success',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }