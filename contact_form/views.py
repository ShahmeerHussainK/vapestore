from django.shortcuts import render
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .forms import ContactForm
from django.contrib import messages  # Add this import
from products.models import AllProducts
from django.core.mail import send_mail  # Import the send_mail function



# class ContactUs(SuccessMessageMixin, CreateView):
#     """"
#     Handles the contact form display and submission
#     """
#     form_class = ContactForm
#     template_name = './contact_form/contact_us.html'
#     success_url = reverse_lazy('home')
#     success_message = 'Your Order has been received.\
#          We will get back to you as soon as possible via the provided email.'
#
#     def form_valid(self, form):
#         """
#         Validates form data
#
#         """
#
#         form.save()
#         return super().form_valid(form)


class ContactUs(SuccessMessageMixin, CreateView):
    """
    Handles the contact form display and submission
    """
    form_class = ContactForm
    template_name = './contact_form/contact_us.html'
    success_url = reverse_lazy('contact_us')

    def form_valid(self, form):
        """
        Validates form data
        """
        form.save()
        name = form.cleaned_data.get('name')
        address = form.cleaned_data.get('address')
        phone_number = form.cleaned_data.get('phone_number')
        email = form.cleaned_data.get('email')

        cart_summary = ""
        total_price = 0

        cart = self.request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = AllProducts.objects.get(id=product_id)
                product.stock_level -= quantity  # Decrease the quantity
                if product.stock_level < 0:  # Ensure quantity does not go below zero
                    product.stock_level = 0
                cart_summary += f"Product: {product.name}, Quantity: {quantity}\n"
                total_price +=  product.price*quantity
                product.save()
            except AllProducts.DoesNotExist:
                messages.error(self.request, f"Product with ID {product_id} does not exist.")
        subject = "New Order Received"
        message = f"""
               A new order has been placed:

               Name: {name}
               Address: {address}
               Phone Number: {phone_number}

               Order Summary:
               {cart_summary}
               
               Total Price :  "{total_price}"
               """
        send_mail(
            subject,
            message,
            'shahmeerhussainkhadmi@gmail.com',  # Replace with your email
            ['shahmeerhussainkhadmi@gmail.com'],  # Recipient email
            fail_silently=False,
        )

        # Send confirmation email to the customer
        customer_subject = "Order Confirmation"
        customer_message = f"""
               Dear {name},

               Thank you for your order!

               Your order has been placed successfully and will be delivered to the following address within 7 working days:
               {address}

               If you have any questions, feel free to contact us at 0312-7899318.

               Best regards,
               Smoke's Hub Pakistan
               """
        send_mail(
            customer_subject,
            customer_message,
            'shahmeerhussainkhadmi@gmail.com',  # Replace with your email
            [email],  # Customer email
            fail_silently=False,
        )

        # Clear the session cart
        if 'cart' in self.request.session:
            del self.request.session['cart']
            self.request.session.modified = True  # Ensure session changes are saved
        messages.success(self.request, 'Your Order has been received. We will get back to you as soon as possible via the provided email.')
        return super().form_valid(form)