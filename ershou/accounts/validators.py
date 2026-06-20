from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class AlphaNumericPasswordValidator:
    """验证密码是否包含字母和数字"""
    
    def validate(self, password, user=None):
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError(
                _("密码必须包含至少一个字母。"),
                code='password_no_letters',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("密码必须包含至少一个数字。"),
                code='password_no_digits',
            )
    
    def get_help_text(self):
        return _("密码必须包含至少一个字母和一个数字。")
