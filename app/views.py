from django.shortcuts import render , redirect , HttpResponse
from .models import Account
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from django.http import JsonResponse
from django.urls import reverse
# Create your views here.
def index(request):
    return render(request,'index.html')



def acc_creation(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('mail')

        # Save account
        account = Account.objects.create(
            name=name,
            phone=phone,
            address=address,
            email=email
        )

        # Send confirmation email
        send_mail(
            f"Thank you {name} for registering",
            f"Your account number is: {account.acc_num}\n\nWelcome to BOB Bank!",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True
        )

        return JsonResponse({"message": "Account created successfully"})

    return render(request, 'create.html')
def pin_generation(request):
    if request.method == "POST":
        acc = request.POST.get('acc')
        try:
            data = Account.objects.get(acc_num=acc)
        except Account.DoesNotExist:
            return JsonResponse({"message": "Account not found."}, status=404)

        otp = randint(100000, 999999)
        send_mail(
            "The OTP for PIN generation",
            f"One-time password is {otp}\nThank you for choosing our bank\nRegards, BOB Bank",
            settings.EMAIL_HOST_USER,
            [data.email],
            fail_silently=True
        )
        request.session['otp'] = otp
        return JsonResponse({
            "message": "OTP sent successfully!",
            "redirect": reverse('validate')
        })

    return render(request, 'pin.html')

def pin_validate(request):
    if request.method == "POST":
        try:
            acc = int(request.POST.get('acc'))
            phone = int(request.POST.get('mobile'))
            otp = int(request.POST.get('otp'))
            pin = int(request.POST.get('pin'))
            cpin = int(request.POST.get('cpin'))

            data = Account.objects.get(acc_num=acc)

            if data.phone != phone:
                return JsonResponse({"message": "❌ Phone number does not match our records."}, status=400)

            session_otp = request.session.get('otp')
            if session_otp != otp:
                return JsonResponse({"message": "❌ Invalid OTP. Please enter the correct OTP."}, status=400)

            if pin != cpin:
                return JsonResponse({"message": "❌ PIN and Confirm PIN do not match."}, status=400)

            # Convert PIN to char format and save
            s1 = "".join(chr(int(i)) for i in str(pin))
            data.pin = s1
            data.save()

            # Send confirmation email
            send_mail(
                subject="PIN GENERATED SUCCESSFULLY",
                message=f"PIN has been generated for account {data.acc_num}. You can now use our services.\n\nThank you for choosing BOB Bank!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[data.email],
                fail_silently=True
            )

            return JsonResponse({
                "message": "✅ PIN successfully generated!"
            })

        except Account.DoesNotExist:
            return JsonResponse({"message": "❌ Account not found."}, status=404)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"message": "❌ Something went wrong. Please try again."}, status=500)

    # GET request: show the page normally
    return render(request, 'validate.html')

def balance(request):
    msg = ""
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        data = Account.objects.get(acc_num = acc)
        check_pin = data.pin
        print(check_pin)
        s = ''
        for i in check_pin:
            s+=str(ord(i))
        # print(s)
        if s == pin:
            msg = f"balance {data.balance}"
        else:
            msg = "invalid pin"

    context = {
        'msg':msg
    }
    return render(request,'balance.html',context)

def withdrawl(request):
    msg = ""
    
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        amt = int(request.POST.get('amt'))

        try:
            data = Account.objects.get(acc_num=acc)
        except Account.DoesNotExist:
            return JsonResponse({"error": "Account not found."})

        # Validate PIN
        encoded_pin = ''.join(str(ord(char)) for char in data.pin)
        
        if encoded_pin != pin:
            return JsonResponse({"error": "Invalid PIN."})

        # Validate amount ≥ ₹500
        if amt < 500:
            return JsonResponse({"error": "Minimum withdrawal amount is ₹500."})

        # Check balance
        if data.balance < amt:
            return JsonResponse({"error": "Insufficient balance."})

        # All validations passed: perform withdrawal
        data.balance -= amt
        data.save()

        # Send confirmation email
        try:
            send_mail(
                subject="Amount Debited - BOB Bank",
                message=f"""Dear {data.name},

We would like to inform you that ₹{amt} has been successfully debited from your account ({data.acc_num}).

🟢 Available Balance: ₹{data.balance}

Thank you for choosing BOB Bank.  
We appreciate your trust and look forward to serving you with the best of our services and benefits.

Warm regards,  
BOB Bank
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[data.email],
                fail_silently=True
            )
        except Exception as e:
            print("Email sending error:", e)

        return JsonResponse({
            "message": f"₹{amt} has been successfully withdrawn from account {data.acc_num}.",
            "balance": data.balance
        })

    return render(request, 'withdrawl.html', {'msg': msg})

def deposit(request):
    msg = ""

    if request.method == "POST":
        acc = request.POST.get("acc")
        pin = request.POST.get('pin')
        amt = int(request.POST.get('amt'))

        try:
            data = Account.objects.get(acc_num=acc)
        except Account.DoesNotExist:
            return JsonResponse({"error": "Account not found."})

        # ✅ Encrypt stored pin using ord() like you did
        encrypted_pin = ""
        for char in data.pin:
            encrypted_pin += str(ord(char))

        # ✅ Check encrypted pin against submitted pin
        if encrypted_pin != pin:
            return JsonResponse({"error": "Invalid PIN."})

        # ✅ Check deposit limits
        if amt < 500:
            return JsonResponse({"error": "Minimum deposit amount is ₹500."})
        elif amt > 100000:
            return JsonResponse({"error": "Maximum deposit limit is ₹100000."})

        # ✅ All checks passed: deposit amount
        data.balance += amt
        data.save()

        return JsonResponse({
            "message": f"₹{amt} has been credited to your account ({data.acc_num}).",
            "balance": data.balance
        })

    return render(request, 'deposit.html', {'msg': msg})
def acc_transfer(request):
    msg = ""
    otp = randint(100000,999999)
    if request.method == "POST":
        from_acc = request.POST.get('facc')
        to_acc = request.POST.get('tacc')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        # print(from_acc,to_acc,phone,email)
        from_data = Account.objects.get(acc_num = from_acc)
        to_data = Account.objects.get(acc_num = to_acc)

        if from_data.phone == int(phone):
            if from_data.email == email:
                request.session['from_acc'] = from_acc
                request.session['to_acc'] = to_acc
                request.session['otp'] = otp
                send_mail("the otp for account transfer  ",f"one time password is {otp} please dont share to anyone \n Thank you for chossing our bank \n regards BOB bank ",settings.EMAIL_HOST_USER,[from_data.email],fail_silently=True)
                return JsonResponse({
            "message": " OTP sent successfully! Please check your email.",
            "redirect": reverse('transfer_validation')
        })

            
            
            else:
                msg = "invalid email"
        else:
            msg = "invlaid mobile number"
        

        
    context = {
        'msg':msg
    }
    return render(request,'transfer.html',context)


def transfer_validation(request):
    msg = ""
    if request.method == "POST":
        otp = int(request.POST.get('otp'))
        amt = int(request.POST.get('amt'))
        # print(otp,amt)
        f_acc = request.session.get('from_acc')
        t_acc = request.session.get('to_acc')
        c_otp = int(request.session.get('otp'))
        # print(f_acc,t_acc,c_otp)
        if otp == c_otp:
            from_data = Account.objects.get(acc_num = f_acc)
            to_data = Account.objects.get(acc_num = t_acc)
            if amt>=1000 and amt <= int(from_data.balance):
                from_data.balance-=amt
                to_data.balance+=amt
                from_data.save()
                to_data.save()
                send_mail(f"This is to confirm that ₹{amt} has been successfully transferred from your account ({from_data.acc_num}) to {to_data.name}'s account.",settings.EMAIL_HOST_USER,[from_data.email],fail_silently=True)
                send_mail(f"We are pleased to inform you that ₹{amt} has been successfully credited to your account from {from_data.name}.",settings.EMAIL_HOST_USER,[to_data.email],fail_silently=True)
                msg = "TRANSFERED SUCCESSFULLY"
            else:
                msg = "insufficient funds "
        else:
            msg = "invalid otp \n try again "
        return JsonResponse({
    "message": " OTP validated successfully. Amount transferred!",
})
    context = {
        'msg':msg
    }
    return render(request,'transfer_validation.html',context)


def acc_deletion(request):
    msg = ""
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        data = Account.objects.get(acc_num = acc)
        if data.balance == 0:
            s = ""
            for i in data.pin:
                s += str(ord(i))
            if s == pin:
                otp = randint(100000, 999999)
                request.session['otp'] = otp
                request.session['acc'] = acc
                send_mail(
                    "the otp for account deletion",
                    f"one time password is {otp} please don't share it with anyone.\nThank you for choosing our bank.\nRegards,\nBOB Bank",
                    settings.EMAIL_HOST_USER,
                    [data.email],
                    fail_silently=True
                )
                return JsonResponse({
                    "message": "OTP sent successfully! Please check your email.",
                    "redirect": reverse("delete_validate")
                })
            else:
                msg = "invalid pin"
        else:
            msg = "please visit the bank for clearing the balance"

    context = {  # ✅ Now this always exists
        'msg': msg
    }
    return render(request, 'delete.html', context)


def delete_validate(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        session_otp = request.session.get("otp")
        acc = request.session.get("acc")

        if not otp_input or not session_otp or not acc:
            return JsonResponse({
                "error": "❌ OTP expired or session not found."
            }, status=400)

        if otp_input == str(session_otp):
            try:
                Account.objects.get(acc_num=acc).delete()
                request.session.pop("otp", None)
                request.session.pop("acc", None)
                return JsonResponse({
                    "message": "Account deleted successfully!"
                })
            except Account.DoesNotExist:
                return JsonResponse({
                    "error": "❌ Account not found."
                }, status=404)
        else:
            return JsonResponse({
                "error": "❌ Invalid OTP. Please try again."
            }, status=400)

    return render(request, "delete_validate.html")

def about(request):
    return render(request,'Aboutus.html')

def contact(request):
    return render(request,'contact.html')


def help(request):
    return render(request,'help.html')