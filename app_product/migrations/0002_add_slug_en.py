from django.db import migrations, models
from django.utils.text import slugify


def populate_slug_en(apps, schema_editor):
    """پر کردن slug_en برای رکوردهای موجود با مقادیر یکتا"""
    Product = apps.get_model('app_product', 'Product')
    ProductCategory = apps.get_model('app_product', 'ProductCategory')
    ProductCategory2 = apps.get_model('app_product', 'ProductCategory2')
    ProductTag = apps.get_model('app_product', 'ProductTag')

    for Model in [ProductCategory, ProductCategory2, ProductTag, Product]:
        used = set()
        for obj in Model.objects.all():
            base = obj.title_en or obj.title_fa or f"item-{obj.pk}"
            base_slug = slugify(base, allow_unicode=False) or f"item-{obj.pk}"

            slug = base_slug
            counter = 1
            while slug in used:
                slug = f"{base_slug}-{counter}"
                counter += 1

            used.add(slug)
            Model.objects.filter(pk=obj.pk).update(slug_en=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('app_product', '0001_initial'),
    ]

    operations = [
        # ============================================
        # 1) اضافه کردن slug_en بدون unique + null=True
        # ============================================
        migrations.AddField(
            model_name='product',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, null=True, verbose_name='اسلاگ (انگلیسی)'),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productcategory2',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='producttag',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),

        # ============================================
        # 2) پر کردن مقادیر یکتا
        # ============================================
        migrations.RunPython(populate_slug_en, migrations.RunPython.noop),

        # ============================================
        # 3) حالا unique=True کن
        # ============================================
        migrations.AlterField(
            model_name='product',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, unique=True, verbose_name='اسلاگ (انگلیسی)'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='productcategory2',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='producttag',
            name='slug_en',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),

        # ============================================
        # 4) Alter slug (allow_unicode=True) — برای فیلد slug فارسی
        # ============================================
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=255, unique=True, verbose_name='اسلاگ'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='productcategory2',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='producttag',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, unique=True),
        ),
    ]