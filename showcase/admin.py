from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, StudentProject, StudentBadge  # Rozetler için StudentBadge modelini içe aktar
from .models import Badge # Badge modelini içe aktar

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'badge_color') # Listede görünecek sütunlar

# ==========================================
# 1. ÖĞRENCİ PROFİLİ BİRLEŞTİRME (INLINE)
# ==========================================
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Öğrenci Atölye Bilgileri'

# ==========================================
# 2. GELİŞMİŞ KULLANICI (USER) YÖNETİMİ
# ==========================================
class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)
    # Admin listesinde kullanıcı adı, ad, soyad ve yetki durumunu gösterir
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    # Listede isme göre arama yapabilmeni sağlar
    search_fields = ('username', 'first_name', 'last_name')

# Eski varsayılan User tanımını kaldırıp yeni hazırladığımız yapıyı kaydediyoruz
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ==========================================
# 3. PROJE YÖNETİMİ (Mevcut Kodunun Güncel Hali)
# ==========================================
@admin.register(StudentProject)
class ProjectAdmin(admin.ModelAdmin):
    # 🌟 'like_count' sütununu listeye ekledik, böylece dışarıdan kaç beğeni olduğunu görebilirsin
    list_display = ('get_student_name', 'project_type', 'like_count')
    
    list_filter = ('project_type',)
    search_fields = ('student__first_name', 'student__last_name', 'student__username')
    
    # 🌟 Beğenen öğrencileri kolayca seçip listeden çıkarabilmen için çift kutulu arayüzü açar
    filter_horizontal = ('liked_by',)
    
    # Öğrencinin adını ve soyadını çekmek için özel fonksiyonun (Aynen kaldı)
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    get_student_name.short_description = 'Öğrenci Adı Soyadı'

    # 🌟 KRİTİK OTOMASYON: Admin panelinden birini silip "Kaydet" dediğinde 
    # beğeni sayısını otomatik olarak yeniden hesaplar ve senkronize eder.
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        project = form.instance
        project.like_count = project.liked_by.count()
        project.save()
@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    # Listede öğrenci adını, rozet adını ve ne zaman kazandığını görelim
    list_display = ('get_student_name', 'get_badge_title', 'earned_at')
    
    # Hızlıca filtreleme yapabilmek için filtre kutuları ekleyelim
    list_filter = ('badge', 'earned_at')
    
    # Öğrenci ismine göre arama yapabilmek için arama çubuğu
    search_fields = ('student__first_name', 'student__last_name', 'student__username')

    # Öğrencinin adını pürüzsüz getiren fonksiyonumuz
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    get_student_name.short_description = 'Öğrenci'

    # Rozet adını pürüzsüz getiren fonksiyonumuz
    def get_badge_title(self, obj):
        return obj.badge.title
    get_badge_title.short_description = 'Kazanılan Rozet'