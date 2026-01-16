"""
Админка для управления контент-блоками
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django import forms
from core.models import ContentBlock


class ContentBlockForm(forms.ModelForm):
    """
    Форма для контент-блока с автогенерацией ключа из описания
    """
    class Meta:
        model = ContentBlock
        fields = '__all__'
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'Например: Заголовок главной страницы',
                'style': 'width: 100%; padding: 8px; font-size: 14px;'
            }),
            'content': forms.Textarea(attrs={
                'rows': 10,
                'style': 'width: 100%; padding: 8px; font-size: 14px; font-family: monospace;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Делаем block_key readonly и скрываем его из основного отображения
        if 'block_key' in self.fields:
            if self.instance and self.instance.pk:
                # Для существующих блоков делаем поле readonly
                self.fields['block_key'].widget.attrs['readonly'] = True
                self.fields['block_key'].widget.attrs['style'] = 'background: #f5f5f5; color: #666;'
                # Добавляем информацию об использовании в help_text
                if hasattr(self.instance, 'page') and hasattr(self.instance, 'block_key'):
                    usage_info = f'Используется в шаблоне: {{% get_content \'{self.instance.page}\' \'{self.instance.block_key}\' \'...\' %}}'
                    self.fields['block_key'].help_text = usage_info
        
        # При создании нового блока делаем описание обязательным
        if 'description' in self.fields:
            if not (self.instance and self.instance.pk):
                self.fields['description'].required = True
    
    def clean(self):
        """Валидация формы"""
        cleaned_data = super().clean()
        description = cleaned_data.get('description', '').strip()
        block_key = cleaned_data.get('block_key', '').strip()
        
        # Если это новый блок и нет описания, требуем его
        if not self.instance.pk and not description:
            raise forms.ValidationError({
                'description': 'Описание обязательно для нового блока. Ключ блока сгенерируется автоматически.'
            })
        
        # Автогенерация ключа из описания, если не указан
        if not block_key and description:
            cleaned_data['block_key'] = slugify(description)
            # Ограничиваем длину
            if len(cleaned_data['block_key']) > 100:
                cleaned_data['block_key'] = cleaned_data['block_key'][:100]
        
        return cleaned_data


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """
    Админка для управления контент-блоками.
    Удобный интерфейс с группировкой по страницам и поиском.
    """
    form = ContentBlockForm
    list_display = ['page', 'get_description_display', 'get_preview', 'get_html_badge', 'updated_at']
    list_filter = ['page', 'is_html', 'created_at', 'updated_at']
    search_fields = ['description', 'content', 'block_key']
    list_editable = []
    readonly_fields = ['id', 'block_key', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'description', 'block_key'),
            'description': 'Выберите страницу и укажите описание блока. Ключ блока сгенерируется автоматически.'
        }),
        ('Содержимое', {
            'fields': ('content', 'is_html'),
            'description': mark_safe('''
                <div style="background: #1f2937; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #dc2626;">
                    <p style="color: #ffffff; margin: 0 0 12px 0; font-size: 16px; line-height: 1.6;">
                        <strong style="color: #ffffff;">Как редактировать текст:</strong>
                    </p>
                    <p style="color: #ffffff; margin: 0 0 15px 0; font-size: 14px; line-height: 1.7;">
                        Просто введите текст в поле ниже. Можно использовать обычный текст - он будет отображаться нормально.
                    </p>
                    <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; line-height: 1.7;">
                        <strong style="color: #ffffff;">Для дополнительного форматирования используйте HTML:</strong>
                    </p>
                    <ul style="color: #ffffff; margin: 0 0 15px 0; padding-left: 20px; line-height: 2;">
                        <li style="color: #ffffff;">Жирный текст: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;strong&gt;текст&lt;/strong&gt;</code></li>
                        <li style="color: #ffffff;">Курсив: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;em&gt;текст&lt;/em&gt;</code></li>
                        <li style="color: #ffffff;">Заголовок: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;h2&gt;Заголовок&lt;/h2&gt;</code></li>
                        <li style="color: #ffffff;">Список: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;ul&gt;&lt;li&gt;Элемент&lt;/li&gt;&lt;/ul&gt;</code></li>
                        <li style="color: #ffffff;">Цветной текст: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;span class="text-red-700"&gt;текст&lt;/span&gt;</code></li>
                        <li style="color: #ffffff;">Ссылка: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;a href="URL"&gt;Текст&lt;/a&gt;</code></li>
                    </ul>
                    <p style="color: #d1d5db; margin: 0; font-size: 13px; font-style: italic; border-top: 1px solid #374151; padding-top: 12px;">
                        💡 Совет: HTML не обязателен - можно просто ввести текст, и он будет отображаться нормально. Включите "Разрешить HTML" только если используете HTML-теги.
                    </p>
                </div>
            ''')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_description_display(self, obj):
        """Отображение описания с ключом блока в скобках"""
        if obj.description:
            desc = format_html(
                '<strong style="color: #333; font-size: 14px;">{}</strong><br>'
                '<span style="color: #999; font-size: 12px;">Ключ: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{}</code></span>',
                obj.description,
                obj.block_key
            )
        else:
            desc = format_html(
                '<span style="color: #999;">(без описания)</span><br>'
                '<span style="color: #999; font-size: 12px;">Ключ: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{}</code></span>',
                obj.block_key
            )
        return desc
    get_description_display.short_description = 'Описание'
    get_description_display.allow_tags = True
    
    def get_preview(self, obj):
        """Превью содержимого в списке"""
        if not obj.content:
            return format_html('<span style="color: #999;">(пусто)</span>')
        
        preview = obj.content[:100].replace('\n', ' ')
        if len(obj.content) > 100:
            preview += '...'
        
        return format_html(
            '<div style="max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{}</div>',
            preview
        )
    get_preview.short_description = 'Содержимое'
    get_preview.allow_tags = True
    
    def get_html_badge(self, obj):
        """Бейдж для HTML"""
        if obj.is_html:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">HTML</span>'
            )
        return format_html('<span style="color: #999;">—</span>')
    get_html_badge.short_description = 'HTML'
    get_html_badge.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        """Автогенерация ключа из описания при сохранении"""
        if not obj.block_key and obj.description:
            obj.block_key = slugify(obj.description)
            # Ограничиваем длину
            if len(obj.block_key) > 100:
                obj.block_key = obj.block_key[:100]
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related()
    
    class Media:
        """Дополнительные стили и скрипты для админки"""
        css = {
            'all': ('admin/css/content_block_admin.css',)
        }
