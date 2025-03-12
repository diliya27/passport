from django.shortcuts import render, redirect
from user_app.models import PassportRegistration
from django.contrib.auth.hashers import make_password
from django.contrib import messages  # Import for displaying messages
from django.db import IntegrityError  # Handle unique email constraint

def registrationview(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            date_of_birth = request.POST.get('date_of_birth')
            nationality = request.POST.get('nationality')
            passport_type = request.POST.get('passport_type')
            terms_accepted = request.POST.get('terms_accepted') == 'on'

            # Debugging print statements
            print(f"Received Data: {first_name}, {last_name}, {email}, {password}, {date_of_birth}, {nationality}, {passport_type}, {terms_accepted}")

            if not all([first_name, last_name, email, password, date_of_birth, nationality, passport_type]):
                messages.error(request, "All fields are required.")
                return render(request, 'registration.html')

            register = PassportRegistration.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password),
                date_of_birth=date_of_birth,
                nationality=nationality,
                passport_type=passport_type,
                terms_accepted=terms_accepted
            )
            register.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')

        except IntegrityError:
            messages.error(request, "Email already exists! Try a different email.")
            return render(request, 'registration.html')
        
        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error
            messages.error(request, "Something went wrong. Try again.")
            return render(request, 'registration.html')

    return render(request, 'registration.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import PassportRegistration

def loginview(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, 'login.html')

        try:
            user = PassportRegistration.objects.get(email=email)
            
            # Manually check hashed password
            if check_password(password, user.password):
                request.session['user_id'] = user.id  # Store user session
                request.session['user_name'] = user.first_name  # Store user name for easy access
                messages.success(request, "Login successful!")
                return redirect('dashboard')  # Ensure 'dashboard' exists in urls.py
            else:
                messages.error(request, "Invalid email or password.")
        
        except PassportRegistration.DoesNotExist:
            messages.error(request, "User does not exist. Please register first.")

    return render(request, 'login.html')


def logoutview(request):
    request.session.flush()  # Clears session data
    messages.success(request, "Logged out successfully.")
    return redirect('login') 
def dashboard_view(request):
    return render(request,'dashboard.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import PassportApplication, Document, Payment
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def application_form_view(request):
    try:
        if request.method == 'POST':
            data = request.POST
            files = request.FILES

            application = PassportApplication.objects.create(
                first_name=data.get('first_name'),
                middle_name=data.get('middle_name', ''),
                last_name=data.get('last_name'),
                date_of_birth=data.get('date_of_birth'),
                city_of_birth=data.get('city_of_birth'),
                state_of_birth=data.get('state_of_birth'),
                country_of_birth=data.get('country_of_birth'),
                gender=data.get('gender'),
                marital_status=data.get('marital_status'),
                nationality=data.get('nationality'),
                occupation=data.get('occupation'),
                address_line1=data.get('address_line1'),
                address_line2=data.get('address_line2', ''),
                city=data.get('city'),
                state=data.get('state'),
                postal_code=data.get('postal_code'),
                country=data.get('country'),
                phone_number=data.get('phone_number'),
                email=data.get('email'),
                id_type=data.get('id_type'),
                id_number=data.get('id_number'),
                father_name=data.get('father_name'),
                mother_name=data.get('mother_name'),
                father_nationality=data.get('father_nationality'),
                mother_nationality=data.get('mother_nationality'),
                father_passport_number=data.get('father_passport_number', ''),
                mother_passport_number=data.get('mother_passport_number', ''),
                emergency_contact_name=data.get('emergency_contact_name'),
                emergency_contact_relationship=data.get('emergency_contact_relationship'),
                emergency_contact_phone=data.get('emergency_contact_phone'),
                emergency_contact_address=data.get('emergency_contact_address'),
                passport_type=data.get('passport_type'),
                page_count=data.get('page_count'),
                travel_purpose=data.get('travel_purpose'),
                proof_of_identity=', '.join(data.getlist('proof_of_identity')),
                proof_of_address=', '.join(data.getlist('proof_of_address')),
                additional_documents=data.get('additional_documents', ''),
                payment_method=', '.join(data.getlist('payment_method')),
                expedited_service=data.get('expedited_service') == 'on',
                application_date=timezone.now(),
                parental_consent=data.get('parental_consent') == 'on',
                terms_agreed=data.get('terms_agreed') == 'on',
            )

            if 'signature_file' in files:
                application.signature_file = files['signature_file']
                application.save()

            for file_key, file_value in files.items():
                if file_key.startswith('document_'):
                    Document.objects.create(
                        application=application,
                        document_type=file_key.replace('document_', ''),
                        file=file_value
                    )

            application.total_amount = max(1500.00, 1.00)
            application.save()

            logger.info(f"Application {application.id} successfully created.")
            return redirect('payment_page', application_id=application.id)
        
        return render(request, 'application_form.html')
    
    except Exception as e:
        logger.error(f"Error during form submission: {str(e)}")
        return render(request, 'application_form.html', {'error': str(e)})


def payment_page(request, application_id):
    try:
        application = get_object_or_404(PassportApplication, id=application_id)
        if application.total_amount < 1.00:
            messages.error(request, "The total amount must be at least ₹1.00.")
            return redirect('application_form')

        amount_in_paise = int(application.total_amount * 100)
        
        order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        Payment.objects.create(
            application=application,
            razorpay_order_id=order['id'],
            amount=application.total_amount,
            currency='INR',
            status='initiated',
        )

        return render(request, 'payment_page.html', {
            'application': application,
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': '/user/payment_status/'
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('application_form')


def payment_method(request, application_id):
    try:
        application = get_object_or_404(PassportApplication, id=application_id)
        
        if application.total_amount <= 0:
            messages.error(request, "Invalid total amount. Please try again.")
            return redirect('application_form')
        
        context = {
            'application': application,
            'total_amount': application.total_amount
        }
        
        return render(request, 'payment_method.html', context)
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('application_form')


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()

            application = payment.application
            application.payment_status = 'Completed'
            application.save()

            messages.success(request, "Payment successful!")
            return redirect('application_detail', application_id=application.id)

        except razorpay.errors.SignatureVerificationError:
            payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
            payment.status = 'failed'
            payment.save()

            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('payment_page', application_id=payment.application.id)
    
    return redirect('application_form')


def application_detail(request, application_id):
    try:
        application = get_object_or_404(PassportApplication, id=application_id)
        documents = Document.objects.filter(application=application)
        payment = Payment.objects.filter(application=application).first()

        context = {
            'application': application,
            'documents': documents,
            'payment': payment,
        }
        
        return render(request, 'application_detail.html', context)
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('application_form')
from django.db.models import Q

def track_service_request(request):
    query = request.GET.get('order_id', '').strip()
    payment = None

    if query:
        try:
            payment = Payment.objects.get(razorpay_order_id=query)
        except Payment.DoesNotExist:
            messages.error(request, "No application found for the given Order ID.")

    context = {
        'payment': payment,
        'query': query,
    }
    return render(request, 'track_service_request.html', context)




#     if request.method == 'POST':
#         passport_type = request.POST.get('passport_type')
#         expedited_service = request.POST.get('expedited_service')

#         # Calculate Fee
#         application_fee = 14500  # Regular Passport (36 pages)
#         if passport_type == '60_pages':
#             application_fee = 17500  # Regular Passport (60 pages)

#         if expedited_service == 'yes':
#             application_fee += 6000  # Expedited service fee

#         currency = 'INR'

#         # Create Razorpay Order
#         razorpay_order = razorpay_client.order.create({
#             'amount': application_fee,
#             'currency': currency,
#             'payment_capture': '1'
#         })

#         application.razorpay_order_id = razorpay_order['id']
#         application.save()

#         context = {
#             'application': application,
#             'amount': application_fee,
#             'razorpay_order_id': razorpay_order['id'],
#             'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#             'currency': currency,
#         }
#         return render(request, 'payment_page.html', context)

#     return render(request, 'payment_page.html')



# @csrf_exempt
# def payment_callback(request):
#     if request.method == "POST":
#         data = request.POST
#         razorpay_order_id = data.get('razorpay_order_id')
#         razorpay_payment_id = data.get('razorpay_payment_id')
#         razorpay_signature = data.get('razorpay_signature')

#         try:
#             # Verify payment signature
#             razorpay_client.utility.verify_payment_signature({
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             })
            
#             # Update the application status
#             application = PassportApplication.objects.get(razorpay_order_id=razorpay_order_id)
#             application.payment_status = 'Completed'
#             application.save()

#             messages.success(request, "Payment successful! Your application has been submitted.")
#             return redirect('payment_method', application_id=application.id)
        
#         except razorpay.errors.SignatureVerificationError:
#             messages.error(request, "Payment failed! Please try again.")
#             return redirect('payment_method', application_id=application.id)
    
#     return redirect('payment_method')


























# views.py

# import razorpay
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from .models import PassportApplication

# # Initialize Razorpay client
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def payment_page(request):
#     if request.method == 'POST':
#         # Extract form data
#         payment_method = request.POST.getlist('payment_method')
#         expedited_service = request.POST.get('expedited_service') == 'yes'
#         page_count = request.POST.get('page_count')
        
#         # Set base price based on page count
#         if page_count == '36':
#             base_price = 145.00
#         elif page_count == '60':
#             base_price = 175.00
#         else:
#             base_price = 0.0  # Default case (if no selection is made)
        
#         # Add expedited charge if selected
#         if expedited_service:
#             total_amount = base_price + 60.00
#         else:
#             total_amount = base_price
        
#         # Convert to paisa for Razorpay (₹1 = 100 paisa)
#         total_amount_paisa = int(total_amount * 100)

#         # Create Razorpay Order
#         try:
#             razorpay_order = razorpay_client.order.create({
#                 'amount': total_amount_paisa,
#                 'currency': 'INR',
#                 'payment_capture': '1'
#             })
#         except Exception as e:
#             messages.error(request, "Failed to create payment order. Please try again.")
#             return redirect('payment_page')
        
#         # Save application details to the database
#         application = PassportApplication(
#             payment_method=payment_method,
#             expedited_service=expedited_service,
#             total_amount=total_amount,
#             razorpay_order_id=razorpay_order['id']
#         )
#         application.save()
        
#         # Prepare context data for the payment page
#         context = {
#             'application': application,
#             'razorpay_order_id': razorpay_order['id'],
#             'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#             'total_amount': total_amount_paisa,
#             'currency': 'INR',
#         }
        
#         return render(request, 'payment_page.html', context)
    
#     return render(request, 'payment_page.html')


# @csrf_exempt
# def payment_callback(request):
#     if request.method == "POST":
#         data = request.POST
#         razorpay_order_id = data.get('razorpay_order_id')
#         razorpay_payment_id = data.get('razorpay_payment_id')
#         razorpay_signature = data.get('razorpay_signature')

#         try:
#             # Verify payment signature
#             razorpay_client.utility.verify_payment_signature({
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             })
            
#             # Update the application status
#             application = PassportApplication.objects.get(razorpay_order_id=razorpay_order_id)
#             application.payment_status = 'Completed'
#             application.save()

#             messages.success(request, "Payment successful! Your application has been submitted.")
#             return redirect('payment_success', application.id)
        
#         except razorpay.errors.SignatureVerificationError:
#             messages.error(request, "Payment verification failed. Please try again.")
#             return redirect('payment_page')
    
#     return redirect('payment_page')

