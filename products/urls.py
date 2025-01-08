from django.urls import path, re_path
from . import views

urlpatterns = [
    path(
        '',
        views.AllProductsView.as_view(),
        name='products'
    ),
    path(
        'updatevape/', views.update_disposable_vape_product,name='update_disposable_vape_product'
        ),
    path(
        'imagenameupdate/', views.update_image_paths,name='update_image_paths'
        ),
    re_path(r'^disposable-vapes/$', views.disposable_vapes_by_brand, name='disposable_vapes_by_brand'),
    re_path(r'^pods-systems/$', views.pods_by_brand, name='pods_by_brand'),
    re_path(r'^e-liquid/$', views.flavors_by_brand, name='flavors_by_brand'),

    path('<int:id>/', views.ProductDetails.as_view(), name='product_detail'),

    path(
        'edit/<slug:slug>/',
        views.EditExistingProduct.as_view(),
        name='edit_product'
    ),
    path(
        'delete/<int:product_id>/',
        views.DeleteProduct.as_view(),
        name='delete_product'
    ),

]
