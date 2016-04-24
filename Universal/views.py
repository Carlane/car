from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime

from Universal.models import CarBrands , User , UserCar , User_Type , CarModels , User_Address
from Universal.models import Service_Type , Joint_Service_Mapping , Joint_Driver_Mapping , Driver_Allocation_Status , TimeSlot
# Create your views here.
@api_view(['GET' , 'POST'])
def cardetails(request, pk , format = None):
    #Get the details of Car for the user whose user id is sent as primary_key
    if request.method == 'GET':
        user_car_data  = UserCar.objects.filter(carownerid__userid = pk)
        returndata = []
        for row in user_car_data:
            tempDict = {}
            tempDict['name'] = row.carbrand.car_brand
            returndata.append(tempDict)
        return Response(returndata)
    #Add a new car for this User with primary key provided in request
    if(request.method == 'POST'):
        requestdata = request.data
        existUser = User.objects.get(userid = pk)
        if existUser is None:
            print('User Not Added in system - Cant add car for a Ghost')
            return Response({'name':'NoUser'}, status.HTTP_400_BAD_REQUEST)
        newRegNumber = requestdata['registration_number']
        existCar = UserCar.objects.filter(carownerid__userid=pk).filter(registration_number=newRegNumber)
        #car with same regisrtation number is already added
        if existCar is not None and len(existCar) != 0:
            print('Same Car(registration number ) is Already Added for this User-',existUser.name)
            return Response({'name','CarAlreadyAdded'}, status.HTTP_400_BAD_REQUEST)
        # car brands and models table will be mapped between user app and this back end
        try:
            print('TILL HERE')
            cardbrand_requestdata = requestdata['carbrand']
            carmodel_requestdata = requestdata['carmodel']
            print('TILL car brand' , int(cardbrand_requestdata))
            print('TILL car model' , int(carmodel_requestdata))
            carsbrand = CarBrands.objects.get(carbrandid =   int(cardbrand_requestdata))
            print('First doubt')
            try :
                carsmodel =  CarModels.objects.get(modelid = int(carmodel_requestdata))
            except :
                print("Error in getting Car Modes")
            print('Second doubt')
            print('car brand is ' , carsbrand)
            print('carmode is' , carsmodel.car_model)

            newCarEntry = UserCar(carownerid = existUser,   carbrand = carsbrand , carmodel = carsmodel , registration_number = newRegNumber)
            newCarEntry.save()
        except:
            return Response({'error','Entry can not be added'} , status.HTTP_400_BAD_REQUEST)
        return Response({'registration_number': newCarEntry.registration_number ,'name':existUser.first_name}, status.HTTP_201_CREATED)


@api_view(['GET' ,'POST'])
def usersignup(request , format = None):
    if(request.method == 'POST'):
        userdata = request.data
        print('Alok' , userdata['firstname'])
        fname = userdata['firstname']
        lname = userdata['lastname']
        email = userdata['email']
        mobile = userdata['mobile']
        token = userdata['token']
        #validate if the same email or phone is present in the database
        existUser = User.objects.filter(email=email , joint_mobile=mobile)
        print('existUser' , existUser)
        if existUser is None or len(existUser) == 0:
            print('existUser is None')

        elif existUser is not None:
            return Response({'email or phone':'Already Exists'}, status.HTTP_400_BAD_REQUEST)
        try:
            # if no duplicate data entry then save the data
            usertype = User_Type.objects.filter(name='Customer')
            newUserEntry = User(userTypeId=usertype[0] , first_name = fname , last_name = lname, email = email , joint_mobile=mobile,access_token = token,is_active = True , status = 'Normal')
            newUserEntry.save()
        except User.DoesNotExist:
            return Response([] , status = status.HTTP_400_BAD_REQUEST)
        return Response({'name':newUserEntry.first_name,'id':newUserEntry.userid} ,status = status.HTTP_201_CREATED)
    if(request.method =='GET'):
        dict = {'name':'alok'}
        return Response(dict)

@api_view(['GET','POST'])
def address(request , pk , format = None):
    if request.method == 'GET':
        print('Get is Fine for Address')
        try :
            user = User.objects.get(userid = pk)
            q = User_Address.objects.filter(user_id = user)
        except:
            return Response([],status.HTTP_400_BAD_REQUEST)
        addressList = []
        for row in q:
            tempDict = {}
            tempDict['name'] = user.first_name
            tempDict['Line1'] =  row.line1
            tempDict['Line2'] =  row.line2
            tempDict['city'] =  row.city
            tempDict['state'] =  row.state
            tempDict['country'] =  row.country
            addressList.append(tempDict)

        return Response(addressList , status.HTTP_201_CREATED)
    elif request.method == 'POST':
        print('POSTING for address')
        user_request_data = request.data
        user = User.objects.get(userid = pk)
        address_line1= user_request_data['line1']
        address_line2= user_request_data['line2']
        address_city= user_request_data['city']
        address_state= user_request_data['state']
        address_country= user_request_data['country']
        address_lat= user_request_data['lat']
        address_long= user_request_data['long']
        newaddress = User_Address(user_id = user , line1 =address_line1 , line2 = address_line2 , city = address_city , state = address_state ,country = address_country,latt = address_lat , longg = address_long)
        newaddress.save()
        return Response({'name': str(newaddress.id)} , status.HTTP_201_CREATED)


@api_view(['POST'])
def initiate_request(request , pk , format = None):
    #retrieve the request data required for this request
    requestdata = request.data
    requesting_user = User.objects.get(userid = pk)
    requested_service_id = requestdata['servicetype']
    requested_timeslotfrom =  datetime.datetime.strptime(requestdata['timeSlotfrom'], '%H:%M:%S').time()#09:00:00
    requested_timeslotto = datetime.datetime.strptime(requestdata['timeSlotto'], '%H:%M:%S').time()#requestdata['timeSlotto']#12:000:00
    requested_geo_id = requestdata['geo']
    requested_date = datetime.datetime.strptime(requestdata['date'] ,'%d:%m:%Y').date()
    print('user ' , requesting_user.first_name + 'has requested' + str(requested_service_id) +'at geo code' + str(requested_geo_id) + ' at date' +requestdata['date'] )
    print('Request Timings are  from' + requestdata['timeSlotfrom'] + ' to ' + requestdata['timeSlotto'])
    print(requested_timeslotfrom)
    print(requested_timeslotto)
    #find all the Joint which are catering the requested Service
    try :
        print('Finding Joints from Joint Service Mapping')
        q = Joint_Service_Mapping.objects.filter(service_type_id__id = requested_service_id , service_slot_count__gte =1)
    except :
        return Response({'error:','No such service exists'}, status.HTTP_400_BAD_REQUEST)
    #find out all the drivers of the Joints found in above steps
    print('Finding Drivers of suitable Car Joints')
    drivermapping = []
    for each_mapping in q:
        print(each_mapping.car_joint_id.name , each_mapping.service_type_id.name)
        try :
            dmap = Joint_Driver_Mapping.objects.filter(car_joint_id = each_mapping.car_joint_id)
        except :
            return Response({'error:','There is no driver available for this Joing' + each_mapping.service_type_id.name}, status.HTTP_400_BAD_REQUEST)

        print('number of driver driver map objects', len(dmap),dmap)
        for joint_driver_object in dmap:
            drivermapping.append(joint_driver_object)
            print('maps',joint_driver_object.driver_user_id.first_name)

    #find out all the drivers which are available for the requested service
    print('Joint Driver Mapping List Size is ',len(drivermapping))
    drivers = []
    time_slot_for_user =  TimeSlot.objects.filter(time_from = requested_timeslotfrom , time_to = requested_timeslotto , geo_id = requested_geo_id)
    print('Time Slot for User',len(time_slot_for_user) )
    for each_drivermap in drivermapping:
        print('Available driver' , each_drivermap.driver_user_id.first_name , each_drivermap.driver_user_id.last_name , each_drivermap.driver_user_id.joint_mobile )
        # what if there is no entry for the next date
        rider = Driver_Allocation_Status.objects.filter(driver_user_id = each_drivermap.driver_user_id , current_count__lte = 4, time_slot_id = time_slot_for_user , date = requested_date)
        print('rider',rider)
        for each_rider in rider:
            tempdict = {'name' : each_rider.driver_user_id.first_name,'date':requestdata['date']}
            drivers.append(tempdict)
            print('confirm Available driver user ' , each_drivermap.driver_user_id.first_name , each_drivermap.driver_user_id.last_name , each_drivermap.driver_user_id.joint_mobile )

    print('drivers -',len(drivers))
    if len(drivers) == 0:
        #report no available slot and ask to chose a new slot
        print('No Driver Available for the Requested Slot')
        return Response([], status.HTTP_201_CREATED)
    return Response(drivers,status.HTTP_201_CREATED)
