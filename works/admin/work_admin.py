"""
Админка для модели Work
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from works.models import Work, Category


class MultipleFileInput(forms.Widget):
    """
    Кастомный виджет для загрузки нескольких файлов
    """
    input_type = 'file'
    template_name = 'django/forms/widgets/file.html'
    needs_multipart_form = True
    
    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        """
        Возвращаем None, так как файлы не имеют значения по умолчанию
        """
        return None
    
    def value_from_datadict(self, data, files, name):
        """
        Возвращаем список файлов
        """
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return None
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Рендерим HTML для input с атрибутом multiple
        """
        if attrs is None:
            attrs = {}
        final_attrs = {**self.attrs, **attrs}
        final_attrs['multiple'] = True
        final_attrs['name'] = name
        final_attrs['type'] = self.input_type
        
        # Формируем строку атрибутов безопасным способом
        attrs_list = []
        for k, v in final_attrs.items():
            attrs_list.append(format_html('{}="{}"', k, v))
        
        attrs_str = ' '.join(str(attr) for attr in attrs_list)
        
        return format_html('<input {} />', attrs_str)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """
    Админка для управления работами (фотографиями)
    """
    list_display = [
        'image_preview',
        'category',
        'order',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'category',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'category__name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'image_preview',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'image', 'image_preview', 'is_active', 'order')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    
    def changelist_view(self, request, extra_context=None):
        """
        Переопределяем changelist_view для добавления кнопки массовой загрузки
        """
        extra_context = extra_context or {}
        extra_context['bulk_upload_url'] = 'bulk-upload/'
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        """
        Добавляем кастомный URL для страницы массовой загрузки
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'bulk-upload/',
                self.admin_site.admin_view(self.bulk_upload_view),
                name='works_work_bulk_upload',
            ),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        """
        View для страницы массовой загрузки фотографий
        """
        class BulkUploadForm(forms.Form):
            """
            Форма для массовой загрузки фотографий
            """
            category = forms.ModelChoiceField(
                queryset=Category.objects.all().order_by('name'),
                label='Категория',
                help_text='Выберите категорию, к которой будут относиться загружаемые фотографии',
                required=True,
                widget=forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'width: 100%; padding: 8px; font-size: 14px;'
                })
            )
            images = forms.FileField(
                label='Фотографии',
                help_text='Выберите несколько фотографий (можно выбрать несколько файлов, удерживая Ctrl или Cmd). Можно загрузить до 100 файлов за раз.',
                required=False,  # Не валидируем через форму, обрабатываем напрямую из request.FILES
                widget=MultipleFileInput(attrs={
                    'accept': 'image/*',
                    'class': 'form-control',
                    'style': 'padding: 8px; font-size: 14px;'
                })
            )
            is_active = forms.BooleanField(
                label='Активировать работы сразу',
                initial=True,
                required=False,
                help_text='Если отмечено, все загруженные работы будут сразу активны на сайте',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input'
                })
            )
            order = forms.IntegerField(
                label='Порядок сортировки',
                initial=0,
                required=False,
                help_text='Порядок сортировки для всех загруженных работ (чем меньше, тем выше)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'style': 'width: 150px; padding: 8px; font-size: 14px;'
                })
            )
        
        if request.method == 'POST':
            # Получаем файлы напрямую, до валидации формы
            files = request.FILES.getlist('images')
            
            # Создаём форму без файлов для валидации остальных полей
            form = BulkUploadForm(request.POST)
            
            if not files:
                messages.error(request, 'Не выбрано ни одного файла для загрузки!')
            elif form.is_valid():
                category = form.cleaned_data['category']
                is_active = form.cleaned_data.get('is_active', True)
                order = form.cleaned_data.get('order', 0)
                
                if not files:
                    messages.error(request, 'Не выбрано ни одного файла для загрузки!')
                    return redirect('admin:works_work_bulk_upload')
                
                # Валидация файлов
                valid_files = []
                invalid_files = []
                
                for file in files:
                    # Проверяем, что это изображение
                    if not file.content_type.startswith('image/'):
                        invalid_files.append(file.name)
                        continue
                    
                    # Проверяем размер (максимум 10 МБ)
                    if file.size > 10 * 1024 * 1024:
                        invalid_files.append(f'{file.name} (слишком большой файл)')
                        continue
                    
                    valid_files.append(file)
                
                if invalid_files:
                    messages.warning(
                        request,
                        f'Пропущено {len(invalid_files)} невалидных файлов: {", ".join(invalid_files[:5])}'
                        + (f' и ещё {len(invalid_files) - 5}' if len(invalid_files) > 5 else '')
                    )
                
                if not valid_files:
                    messages.error(request, 'Нет валидных файлов для загрузки!')
                    return redirect('admin:works_work_bulk_upload')
                
                # Создаём работы для каждого файла
                created_count = 0
                errors = []
                
                for file in valid_files:
                    try:
                        work = Work.objects.create(
                            category=category,
                            image=file,
                            is_active=is_active,
                            order=order,
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f'{file.name}: {str(e)}')
                
                if errors:
                    messages.warning(
                        request,
                        f'Ошибки при загрузке {len(errors)} файлов: {"; ".join(errors[:3])}'
                        + (f' и ещё {len(errors) - 3}' if len(errors) > 3 else '')
                    )
                
                if created_count > 0:
                    messages.success(
                        request,
                        f'Успешно загружено {created_count} фотографий в категорию "{category.name}"!'
                    )
                    return redirect('admin:works_work_changelist')
                else:
                    messages.error(request, 'Не удалось загрузить ни одной фотографии!')
        else:
            form = BulkUploadForm()
        
        # Контекст для шаблона
        context = {
            **self.admin_site.each_context(request),
            'title': 'Массовая загрузка фотографий работ',
            'form': form,
            'opts': Work._meta,
            'has_view_permission': True,
            'has_add_permission': True,
            'has_change_permission': True,
            'has_delete_permission': True,
        }
        
        return render(request, 'admin/works/bulk_upload.html', context)
    
    def image_preview(self, obj):
        """
        Превью изображения в админке
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'
    
    actions = ['activate_works', 'deactivate_works']
    
    def activate_works(self, request, queryset):
        """
        Действие для массовой активации работ
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} работ(ы) активировано.'
        )
    activate_works.short_description = 'Активировать выбранные работы'
    
    def deactivate_works(self, request, queryset):
        """
        Действие для массовой деактивации работ
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} работ(ы) деактивировано.'
        )
    deactivate_works.short_description = 'Деактивировать выбранные работы'

