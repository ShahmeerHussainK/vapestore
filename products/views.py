from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.views import generic, View
from django.contrib import messages
from django.db.models import Q
from .models import AllProducts
from reviews.models import ProductReviews
from reviews.forms import ProductReviewForm
from .forms import ProductForm
from django.http import HttpResponse
from .helpers import *


class AllProductsView(generic.ListView):
    """"
    View to return all products
    """

    model = AllProducts
    template_name = 'products/products.html'
    context_object_name = 'products'
    # paginate_by = 6
    sort = None
    current_ordering = None
    query = None
    categories = None
    subcategories = None
    clearance = None

    def get_ordering(self, *args, **kwargs):
        """
        Returns the ordering of the products
        """

        if self.request.GET.get('ordering'):

            sort_by = self.request.GET['ordering']
            self.sort = sort_by

            if sort_by == 'name':

                sort_by = self.request.GET.get('sort_by', 'name')

            elif sort_by == 'price':

                sort_by = self.request.GET.get('ordering', 'price')

            elif sort_by == 'current_rating':

                sort_by = self.request.GET.get('ordering', 'current_rating')

        else:

            sort_by = 'id'

        return sort_by

    def get_queryset(self, *args, **kwargs):
        """
        Returns all products in specific querysets
        """

        products = super(AllProductsView, self).get_queryset(*args, **kwargs)

        if self.request.GET:

            ordering = self.get_ordering(self)
            self.current_ordering = ordering

            if 'clearance' in self.request.GET:

                products = products.filter(has_sale=True)
                self.clearance = True

            if 'category' in self.request.GET:

                self.categories = self.request.GET['category'].split(',')
                products = products.filter(
                    category__name__in=self.categories).order_by(
                        self.current_ordering)

            if 'subcategory' in self.request.GET:

                self.subcategories = self.request.GET['subcategory'].split(',')
                products = products.filter(
                    sub_category__name__in=self.subcategories).order_by(
                        self.current_ordering)

            if 'q' in self.request.GET:

                self.query = self.request.GET['q']

                if not self.query:

                    messages.error(
                        self.request, "You didn't enter any search criteria!")

                queries = Q(
                    name__icontains=self.query) | Q(
                    description__icontains=self.query)

                products = products.filter(queries).order_by(
                    self.current_ordering)

            return products.order_by(self.current_ordering)

        else:

            return products

    def get_context_data(self, **kwargs):
        """
        extent the generic views context and pass to the template
        """

        context = super().get_context_data(**kwargs)
        context['current_ordering'] = self.current_ordering
        context['search_query'] = self.query
        context['current_categories'] = self.categories
        context['current_subcategories'] = self.subcategories
        context['clearance'] = self.clearance

        return context


class ProductDetails(View):
    """"
    View to return a single product
    """

    def get(self, request, id, *args, **kwargs):
        """"
        Returns a single product and it details
        """

        individual_product = get_object_or_404(AllProducts, id=id)
        slug = individual_product.id
        form = ProductReviewForm()

        reviews = ProductReviews.objects.filter(product=individual_product.id)

        context = {
            'product': individual_product,
            'review_form': form,
            'reviews': reviews,
        }

        return render(
            request,
            'products/product-detail.html', context
        )


class EditExistingProduct(View):
    """"
    View to edit an existing product via a form
    """

    def get(self, request, slug, *args, **kwargs):
        """"
        Returns a single product and it details in a form for editing
        """

        if not request.user.is_superuser:

            messages.error(request, 'Sorry, only store owners can do that.')
            return redirect(reverse('home'))

        individual_product = get_object_or_404(AllProducts, slug=slug)
        slug = individual_product.id
        form = ProductForm(instance=individual_product)

        context = {
            'product': individual_product,
            'form': form,
        }

        return render(
            request,
            'products/edit-product.html', context)

    def post(self, request, slug, *args, **kwargs):
        """"
        Posts the edited details to the database
        """

        individual_product = get_object_or_404(AllProducts, slug=slug)
        slug = individual_product.id
        form = ProductForm(request.POST, request.FILES,
                           instance=individual_product)

        if form.is_valid():

            form.save()
            # messages.success(request, 'Product Updated Successfully!')

            return redirect(reverse('product_detail', args=[slug]))

        else:

            # messages.error(
                # request,
                # 'Failed to update product. Please ensure the form is valid.')

            return render(
                request,
                'products/edit-product.html', {'form': form})


class DeleteProduct(View):
    """"
    View to delete a product
    """
    @staticmethod
    def get(request, *args, **kwargs):
        """"
        Deletes a product from the database
        but restricts this action to superusers
        """

        if not request.user.is_superuser:

            messages.error(request, 'Sorry, only store owners can\
                 delete products.')

            return redirect(reverse('home'))

        individual_product = get_object_or_404(
            AllProducts, id=kwargs['product_id'])

        individual_product.delete()

        messages.success(request, 'Product Deleted Successfully!')

        return redirect(reverse('products'))

def disposable_vapes_by_brand(request):
    """
    View to get all disposable vapes filtered by the brand.
    If no brand is provided, it will return all disposable vapes.
    """
    brand = request.GET.get('brand', None)
    disposable_vapes = DisposableVapes.objects.all()

    if brand:
        disposable_vapes = disposable_vapes.filter(brand__iexact=brand)

    context = {
        'products': disposable_vapes,
    }
    return render(request, 'products/products.html', context)

def pods_by_brand(request):
    """
    View to get all disposable vapes filtered by the brand.
    If no brand is provided, it will return all disposable vapes.
    """
    brand = request.GET.get('brand', None)
    pods = Pods.objects.all()

    if brand:
        pods = pods.filter(brand__iexact=brand)

    context = {
        'products': pods,
    }
    return render(request, 'products/products.html', context)

def flavors_by_brand(request):
    """
    View to get all disposable vapes filtered by the brand.
    If no brand is provided, it will return all disposable vapes.
    """
    brand = request.GET.get('brand', None)
    pods = VapeJuice.objects.all()
    elequid = ""
    if brand:
        elequid = pods.filter(brand__iexact=brand)
    else:
        elequid=pods
    context = {
        'products': elequid,
    }
    return render(request, 'products/products.html', context)

def update_image_paths(request):
    base_path = "C:\\Users\\HASSAN\\PycharmProjects\\kabhi_kusi_kabhi_gam\\Vape-Store-main\\media\\"
    images_updated = 0

    # Iterate through all ImageModel instances
    for image_instance in Image.objects.all():
        full_path = image_instance.image.name
        # Check if the full path contains the base path we want to replace
        if full_path.startswith(base_path):
            relative_path = full_path.replace(base_path, '')
            # Update the image field with the new relative path
            image_instance.image.name = relative_path
            print(image_instance.image.name)
            print('***************************')
            image_instance.save()
            images_updated += 1

    # Return a simple HttpResponse indicating how many images were updated
    return HttpResponse(f"{images_updated} image paths were updated.")
def update_disposable_vape_product(request):
   #fetch_and_update_disposable_pods()..
    #fetch_and_update_e_liquids()..
    #fetch_and_update_mods()..
    #fetch_and_update_coils()..
    #fetch_and_update_accessories()..
    fetch_and_update_tanks()
    #fetch_and_update_pods()..
    return HttpResponse("Disposable Pods have been updated.")
