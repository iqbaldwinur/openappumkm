from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import manage_users, edit_user, create_user, edit_belanja


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),


    path('anggaran_list/', views.anggaran_list, name='anggaran_list'),
    path('anggaran_form', views.anggaran_create, name='anggaran_create'),
    path('anggaran/update/<int:pk>/', views.anggaran_update, name='anggaran_update'),
    path('anggaran/delete/<int:pk>/', views.anggaran_delete, name='anggaran_delete'),
    
    path('belanja_list/', views.belanja_list, name='belanja_list'),
    path('create_belanja/', views.create_belanja, name='create_belanja'),
    path('belanja_delete/<int:user_id>/', views.belanja_delete, name='belanja_delete'),
    path('edit_belanja/<int:belanja_id>/', views.edit_belanja, name='edit_belanja'),
    
    
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('manage_user/', manage_users, name='manage_users'),
    path('create_user/', create_user, name='create_user'),
    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    path('distribusi-modal/', views.distribusi_modal_list, name='distribusi_modal_list'),
    path('distribusi-modal/create/', views.create_distribusi_modal, name='create_distribusi_modal'),
    path('distribusi-modal/edit/<int:distribusi_id>/', views.edit_distribusi_modal, name='edit_distribusi_modal'),
    path('distribusi-modal/delete/<int:distribusi_id>/', views.delete_distribusi_modal, name='delete_distribusi_modal'),
    
    
    path('ssh/', views.ssh_list, name='ssh_list'),
    path('ssh/create/', views.create_ssh, name='create_ssh'),
    path('ssh/edit/<int:ssh_id>/', views.edit_ssh, name='edit_ssh'),
    path('ssh/delete/<int:ssh_id>/', views.delete_ssh, name='delete_ssh'),
    
    path('create-transaksi-anggaran-belanja/', views.create_transaksi_anggaran_belanja, name='create_transaksi_anggaran_belanja'),
    path('transaksi-anggaran-belanja-list/', views.transaksi_anggaran_belanja_list, name='transaksi_anggaran_belanja_list'),
    path('edit-transaksi-anggaran-belanja/<int:id>/', views.edit_transaksi_anggaran_belanja, name='edit_transaksi_anggaran_belanja'),
    path('transaksi-anggaran-belanja/<int:pk>/delete/', views.delete_transaksi_anggaran_belanja, name='delete_transaksi_anggaran_belanja'),
    
    
    path('detail-transaksi-anggaran-belanja/<int:anggaran_id>/detail/', views.detail_anggaran_belanja_list, name='detail_anggaran_belanja_list'),
    path('transaksi-anggaran-belanja/<int:anggaran_id>/barang/create/', views.create_detail_transaksi_belanja, name='create_detail_transaksi_belanja'), 
    path('transaksi-anggaran-belanja/barang/<int:barang_id>/edit/', views.edit_detail_transaksi_belanja, name='edit_detail_transaksi_belanja'),
    path('transaksi-anggaran-belanja/barang/<int:barang_id>/delete/', views.delete_detail_transaksi_belanja, name='delete_detail_transaksi_belanja'),
    
    
    
    path('transaksi/create/', views.create_transaksi, name='create_transaksi'),
    path('transaksi/<int:transaksi_id>/edit/', views.edit_transaksi, name='edit_transaksi'),
    path('edit-transaksi/<int:id>/', views.edit_transaksi, name='edit_transaksi'),
    path('delete-transaksi/<int:id>/', views.delete_transaksi, name='delete_transaksi'),

    path('transaksi/', views.transaksi_list, name='transaksi_list'),

    path('transaksi-belanja/<int:transaksi_id>/', views.transaksi_belanja_list, name='transaksi_belanja_list'),
    path('transaksi-belanja/<int:transaksi_id>/create/', views.create_transaksi_belanja, name='create_transaksi_belanja'),
    path('edit-transaksi-belanja/<int:transaksi_id>/<int:belanja_id>/', views.edit_transaksi_belanja, name='edit_transaksi_belanja'),
    path('transaksi-belanja/<int:transaksi_id>/delete/<int:belanja_id>/', views.delete_transaksi_belanja, name='delete_transaksi_belanja'),
    path('transaksi-belanja/<int:transaksi_id>/pdf/', views.transaksi_belanja_pdf, name='transaksi_belanja_pdf'),

    
    
    

]

