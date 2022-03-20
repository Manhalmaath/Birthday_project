import string
from typing import List

import pandas as pd
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from ninja import File
from ninja import Router
from ninja.files import UploadedFile

from account.authorization import GlobalAuth, get_tokens_for_user
from account.models import Customer, User
from account.schemas import MessageOut, AuthOut, AccountCreate, SigninSchema, AccountOut, AccountUpdate, \
    ChangePasswordSchema, CustomerOut, BirthdayMassage

User = get_user_model()

account_controller = Router(tags=['auth'])


@account_controller.post('signup', response={
    400: MessageOut,
    201: AuthOut,
})
def signup(request, account_in: AccountCreate):
    if account_in.password1 != account_in.password2:
        return 400, {'detail': 'Passwords do not match!'}

    try:
        User.objects.get(email=account_in.email)
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            first_name=account_in.first_name,
            last_name=account_in.last_name,
            email=account_in.email,
            password=account_in.password1
        )

        token = get_tokens_for_user(new_user)

        return 201, {
            'token': token,
            'account': new_user,
        }

    return 400, {'detail': 'User already registered!'}


@account_controller.post('signin', response={
    200: AuthOut,
    404: MessageOut,
})
def signin(request, signin_in: SigninSchema):
    user = authenticate(email=signin_in.email, password=signin_in.password)

    if not user:
        return 404, {'detail': 'User does not exist'}

    token = get_tokens_for_user(user)

    return {
        'token': token,
        'account': user
    }


@account_controller.get('', auth=GlobalAuth(), response=AccountOut)
def me(request):
    return get_object_or_404(User, id=request.auth['pk'])


@account_controller.put('', auth=GlobalAuth(), response={
    200: AccountOut,
})
def update_account(request, update_in: AccountUpdate):
    User.objects.filter(id=request.auth['pk']).update(**update_in.dict())
    return get_object_or_404(User, id=request.auth['pk'])


@account_controller.post('change-password', auth=GlobalAuth(), response={
    200: MessageOut,
    400: MessageOut
})
def change_password(request, password_update_in: ChangePasswordSchema):
    user = authenticate(get_object_or_404(User, id=request.auth['pk']).EMAIL_HOST_USER, password_update_in.old_password)
    if password_update_in.new_password1 != password_update_in.new_password2:
        return 400, {'detail': 'passwords do not match'}
    user = get_object_or_404(User, id=request.auth['pk'])
    is_it_him = user.check_password(password_update_in.old_password)

    if not is_it_him:
        return 400, {'detail': 'Dude, make sure you are him!'}

    user.set_password(password_update_in.new_password1)
    user.save()
    return {'detail': 'password updated successfully'}


@account_controller.post("/upload", auth=GlobalAuth(), response={201: MessageOut, 400: MessageOut})
def upload(request, payload: BirthdayMassage, file: UploadedFile = File(...)):
    customers = Customer.objects.all()
    data = pd.read_excel(file, sheet_name='Sheet1')
    user = get_object_or_404(User, id=request.auth['pk'])
    massage = payload.massage
    user.massageText = massage
    english_letters = list(string.ascii_letters)
    first_letter = massage.split(' ')[0][0]
    if not (first_letter in english_letters):
        user.language = False
    user.save()
    customers_name = []
    customers_email = []
    for i in range(len(customers)):
        customers_name.append(customers[i].name)
        customers_email.append(customers[i].email)
    for i in range(0, len(data.index)):
        name = data.loc[i, 'name']
        email = data.loc[i, 'email']
        birthday = data.loc[i, 'birthday (M-D-Y)']
        gender = data.loc[1, 'gender (male-female)']
        phone_num = data.loc[1, 'phone_number']
        if not ((name in customers_name) and (email in customers_email)):
            try:
                Customer.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    birthday=birthday,
                    gender=gender,
                    phone_number=phone_num
                )
            except:
                return 400, {'detail': 'birthday is not valid'}
        print("created")
    return 201, {'detail': 'customers created successfully'}


@account_controller.get("get_all_customers", response=List[CustomerOut], auth=GlobalAuth())
def getCustmers(request):
    user = get_object_or_404(User, id=request.auth['pk'])
    customers = Customer.objects.filter(user=user)
    return customers


@account_controller.get('test', response=MessageOut)
def test(request, payload: MessageOut):
    return payload.detail
