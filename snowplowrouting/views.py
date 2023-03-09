import json
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.models import User
from users.models import Profile
from .forms import AddEmployeeForm, AddMachineryForm, AddSchedule
from .models import InviteEmployee, Machinery, Driver, VehiclesAddress, Schedule, ConfigMode
import users.tokens.tokengenerator as tk
from django.conf import settings
from django.db.models import Q
import snowplowrouting.MapDataTools.OSMManager as osm
import snowplowrouting.MapDataTools.directions as dir



class AdminHomeView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "admin_profile.html"

    def Merge(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res

    def test_func(self):
        return self.request.user.profile.is_admin

    def get(self, request, *args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            is_ajax_unbind_vehicles = request.headers.get('X-Requested-For') == 'GetVehiclesWithoutDriver'
            is_ajax_unbind_drivers = request.headers.get('X-Requested-For') == 'GetDriversWithoutSchedule'
            is_ajax_bind_drivers = request.headers.get('X-Requested-For') == 'GetDriversWithSchedule'
            if is_ajax_unbind_vehicles:
                data = []
                values = Machinery.objects.filter(Q(ready=True) & Q(Q(driver_id1__isnull=True) | Q(driver_id2__isnull=True))).values()
                for value in list(values):
                    data.append([value['vin'], value['model']])
                print(data);
                return JsonResponse({"data": data})
            if is_ajax_unbind_drivers:
                data = []
                possible_drivers = Profile.objects.filter(Q(is_admin=False) & Q(county = request.user.profile.county)).values()
                for driver_data in possible_drivers:
                    driver = Driver.objects.filter(Q(user_id=driver_data["user_id"]) & Q(schedule__isnull=True) & Q(machinery__isnull=False)).values()
                    if driver:
                        vehicle = Machinery.objects.filter(vin=driver[0]["machinery_id"]).values()
                        if vehicle.exists():
                            if vehicle[0]["ready"] == True:
                                info = User.objects.filter(id=driver_data["user_id"]).values()
                                data.append({
                                    "id":info[0]["id"],
                                    "last_name": info[0]["last_name"],
                                    "first_name": info[0]["first_name"],
                                    "machinery_id": driver[0]["machinery_id"]
                                })
                return JsonResponse({"data": data})
            if is_ajax_bind_drivers:
                context = {}
                for obj in Schedule.objects.all():
                    context[str(obj)] = []
                drivers = Driver.objects.filter(Q(machinery__isnull=False) & Q(schedule__isnull=False)).values()
                for driver in drivers:
                    vehicle = Machinery.objects.filter(vin=driver["machinery_id"]).values()
                    if vehicle.exists():
                        if vehicle[0]["ready"] == True:
                            schedule = Schedule.objects.filter(id=driver["schedule_id"]).values()
                            name_sch = str(schedule[0]["start_time"]) + "-" + str(schedule[0]["end_time"])
                            user = User.objects.filter(id=driver["user_id"]).values()
                            data = user[0]["first_name"] + " " + user[0]["last_name"]
                            context[name_sch].append(data)
                return JsonResponse({"data": context})
        else:
            scheduler = []
            context = {
                "name": request.user.first_name + " " + request.user.last_name,
                "users_info": [],
                "machinerys": [],
                "google_api_key": settings.GOOGLE_MAPS_API_KEY,
                "lat": 0.0,
                "lng": 0.0,
                "form": AddSchedule(),
                "scheduler": scheduler,
            }

            for obj in Schedule.objects.all():
                scheduler.append(str(obj))

            geocoding = VehiclesAddress.objects.filter(county=request.user.profile.county)
            if geocoding.exists():
                context["lat"] = geocoding.values()[0]["latitude"]
                context["lng"] = geocoding.values()[0]["longitude"]

            data = Profile.objects.filter(is_admin=False, county=request.user.profile.county).values()
            for emp_user in data:
                profile_emp = User.objects.filter(id=emp_user['user_id'], is_staff=False).values()
                if profile_emp.exists():
                    data = {"first_name": profile_emp[0]['first_name'],
                            "last_name": profile_emp[0]['last_name'],
                            "email": profile_emp[0]['email'],
                            "user_id": emp_user['user_id']
                            }

                    user = User.objects.get(id=emp_user['user_id'])
                    car = Driver.objects.filter(user=user).values()
                    if car.exists():
                        id_car = car[0]['machinery_id']
                        model = Machinery.objects.get(vin = id_car)
                        data["car_name"] = model
                    context["users_info"].append(self.Merge(emp_user, data))

            tools = Machinery.objects.filter(county = request.user.profile.county).values()
            if tools.exists():
                context["machinerys"] = list(tools)
                for tool in tools:
                    tool['lst_digit_vin'] = tool['vin'][16]
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        is_ajax_for_start_app = request.headers.get('X-Requested-For') == 'StartApp';
        is_ajax_for_schedule = request.headers.get('X-Requested-For') == 'Schedule';
        is_ajax_for_config_app_mode = request.headers.get('X-Requested-For') == 'ConfigMode';
        is_ajax_for_update_diver_schedule = request.headers.get('X-Requested-For') == 'UpdateDriversSchedule';
        is_ajax_for_schedule_remove = request.headers.get('X-Requested-For') == 'ScheduleControlRemove';
        is_ajax_for_employee = request.headers.get('X-Requested-For') == 'EmployeeControl';
        is_ajax_for_machinerys = request.headers.get('X-Requested-For') == 'MachineryControl';
        is_ajax_for_machinerys_delete = request.headers.get('X-Requested-For') == 'EmployeeMachineryControl';
        is_ajax_for_geocoding = request.headers.get('X-Requested-For') == 'GeocodingControl';
        response = json.loads(list(request.POST)[0]);

        if is_ajax_for_schedule:
            new_schedule = Schedule(
                start_time=response["start_time"],
                end_time=response["end_time"],
                city=request.user.profile.county,
            )
            new_schedule.save()
            return JsonResponse({'payload': 'succes'})

        if is_ajax_for_schedule_remove:
            data = response["schedule"].split("-")
            Schedule.objects.filter(Q(start_time=data[0]) & Q(end_time= data[1]) & Q(city=request.user.profile.county)).delete()
            print(data)
            # pt fiecare driver sters
            return JsonResponse({'payload': 'succes'})

        if is_ajax_for_machinerys_delete:
            id = response["id"]
            try:
                user = User.objects.get(id = id)
                Machinery.objects.filter(driver_id1 = id).update(driver_id1 = None)
                Machinery.objects.filter(driver_id2 = id).update(driver_id2 = None)
                Driver.objects.get(user=user).delete()
            except ObjectDoesNotExist:
                print("No track with the id")
            return JsonResponse({'payload': 'succes'})

        if is_ajax_for_machinerys:
            vin = response["vin"]
            status = response["value"]
            try:
                Machinery.objects.filter(vin = vin).update(ready = status)
            except ObjectDoesNotExist:
                print("No track with the id")
            return JsonResponse({'payload': 'succes'})

        if is_ajax_for_employee:
            vin = response["vin"]
            id = response["id"]
            try:
                user = User.objects.get(id = id)
                machinery = Machinery.objects.get(vin = vin)
                if not Driver.objects.filter(user = user).exists():
                    user_driver_relation = Driver(user = user, machinery = machinery)
                    user_driver_relation.save()
                    if not Machinery.objects.filter(vin=vin, driver_id1__isnull=False).exists():
                        Machinery.objects.filter(vin = vin).update(driver_id1 = id)
                        return JsonResponse({'driver-name': [user.first_name, user.last_name, machinery.model]})
                    else:
                        if not Machinery.objects.filter( vin=vin, driver_id2__isnull=False).exists():
                            Machinery.objects.filter(vin = vin).update(driver_id2 = id)
                            return JsonResponse({'driver-name': [user.first_name, user.last_name, machinery.model]})
                else:
                    return JsonResponse({'driver-name': 'exists'})
            except ObjectDoesNotExist:
                print("No track with the id")

        if is_ajax_for_geocoding:
            lat = response["lat"];
            lng = response["lng"];
            geolocation = VehiclesAddress.objects.filter(county = request.user.profile.county)
            if geolocation.exists():
                geolocation.update(latitude = lat, longitude = lng)
                return JsonResponse({'payload': 'done'})
            else:
                new_geolocation = VehiclesAddress(county = request.user.profile.county, latitude = lat, longitude = lng)
                new_geolocation.save()
                return JsonResponse({'payload': 'done'})
            return JsonResponse({'payload': 'error'})

        if is_ajax_for_update_diver_schedule:
            existing_vehicles = []
            start, end = response["schedule"].split("-")
            schedule = Schedule.objects.filter(Q(start_time=start) & Q(end_time=end)).values()
            drivers_with_schedule = list(Driver.objects.filter(schedule=schedule[0]["id"]).values())
            for entry in drivers_with_schedule:
                existing_vehicles.append(entry["machinery_id"])
            if schedule:
                for driver_info in response["data"]:
                    info = json.loads(driver_info)
                    print(info)
                    if not info["machinery_id"] in existing_vehicles:
                        Driver.objects.filter(user_id=info["id"]).update(schedule=schedule[0]["id"])
                    else:
                        return JsonResponse({'payload': 'One of the selected cars already exists in the schedule!'})
            return JsonResponse({'payload': 'done'})

        if is_ajax_for_start_app:
            schedules = list(Schedule.objects.filter(city=request.user.profile.county).values())
            schedules_orderd = sorted(schedules, key=lambda x: x['start_time'])
            configuration = ConfigMode.objects.filter(county = request.user.profile.county).values()
            if configuration:
                if configuration[0]["city"] is not None and configuration[0]["configArea"] is not None:
                    current_time = datetime.now().time()
                    drivers = []
                    for schedule in schedules_orderd:
                        if current_time >= schedule["start_time"] and current_time <= schedule["end_time"]:
                            possible_drivers = Profile.objects.filter(
                                Q(is_admin=False) & Q(county=request.user.profile.county)).values()
                            for driver_data in possible_drivers:
                                driver = Driver.objects.filter(
                                    Q(user_id=driver_data["user_id"]) & Q(schedule_id=schedule["id"]) & Q(
                                        machinery__isnull=False)).values()
                                if driver:
                                    vehicle = Machinery.objects.filter(vin=driver[0]["machinery_id"]).values()
                                    if vehicle.exists():
                                        if vehicle[0]["ready"] == True:
                                            drivers.append(driver[0])
                            break
                    print(len(drivers))
                    address_vehicles = VehiclesAddress.objects.filter(county= request.user.profile.county).values()
                    routes = []
                    if address_vehicles:
                        routes = osm.routing(address_vehicles[0]["latitude"], address_vehicles[0]["longitude"],
                                             len(drivers), request.user.profile.county, configuration[0]["city"], configuration[0]["configArea"])
                        print(routes)
                        index = 0
                        for _driver in drivers:
                            Driver.objects.filter(user_id = _driver["user_id"]).update(route=json.dumps(routes[index]))
                            index += 1
            return JsonResponse({'payload': 'done'})
        if is_ajax_for_config_app_mode:
            current_config = ConfigMode(county = request.user.profile.county, city = response["city"], configArea = response["mode"])
            current_config.save()
            return JsonResponse({'payload': 'done'})

class WorkerHomeView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "worker_profile.html"

    def test_func(self):
        return not self.request.user.profile.is_admin

    def get(self, request, *args, **kwargs):
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                is_ajax_next_lap = request.headers.get('X-Requested-For') == 'MapsNextLap'
                is_ajax_previous_lap = request.headers.get('X-Requested-For') == 'MapsPreviousLap'
                user = User.objects.filter(email=request.user.email).values()
                driver = Driver.objects.filter(user_id=user[0]["id"]).values()
                route = json.loads(driver[0]["route"])
                if is_ajax_next_lap:
                    if request.session['current_lap'] < len(route) - 1:
                        request.session['current_lap'] = request.session['current_lap'] + 1
                    else:
                        request.session['current_lap'] = 0
                    return JsonResponse({'payload': 'done'})
                if is_ajax_previous_lap:
                    if request.session['current_lap'] == 0:
                        print("innnn")
                        request.session['current_lap'] = len(route) - 1
                    else:
                        request.session['current_lap'] = request.session['current_lap'] - 1
                    return JsonResponse({'payload': 'done'})
            address = VehiclesAddress.objects.filter(county= request.user.profile.county).values()
            user = User.objects.filter(email = request.user.email).values()
            driver = Driver.objects.filter(user_id = user[0]["id"]).values()
            vehicle_info = Machinery.objects.filter(vin = driver[0]["machinery_id"]).values()
            schedule_id = driver[0]["schedule_id"]
            temp_data = Schedule.objects.filter(id = schedule_id).values()
            schedule = [temp_data[0]["start_time"], temp_data[0]["end_time"]]
            current_time = datetime.now().time()
            if current_time >= schedule[0] and current_time <= schedule[1]:
                route = json.loads(driver[0]["route"])
                if route:
                    if not 'current_lap' in request.session:
                        request.session['current_lap'] = 0
                    directions, origins, destinations, waypts = dir.Directions(depot_lat=address[0]["latitude"], depot_long=address[0]["longitude"], coords = route)
                    lat_start = address[0]["latitude"]
                    long_start = address[0]["longitude"]
                    context = {
                        "name": request.user.first_name + " " + request.user.last_name,
                        "vehicle_name": vehicle_info[0]["model"],
                        "vehicle_vin": vehicle_info[0]["vin"],
                        "google_api_key": settings.GOOGLE_MAPS_API_KEY,
                        "route":route,
                        "lat_a": address[0]["latitude"],
                        "long_a":address[0]["longitude"],
                        "origin": origins[request.session['current_lap']],
                        "destination": destinations[request.session['current_lap']],
                        "directions": directions[request.session['current_lap']],
                        "waypts":waypts[request.session['current_lap']].split("|"),
                        "current_lap": request.session['current_lap'],
                        "total_lap":len(route)-1,
                        "message": "Time for work"
                    }
                    return render(request, self.template_name, context)
                else:
                    context = {
                        "name": request.user.first_name + " " + request.user.last_name,
                        "vehicle_name": vehicle_info[0]["model"],
                        "vehicle_vin": vehicle_info[0]["vin"],
                        "message": "You dont have any route yet"
                    }
                    return render(request, self.template_name, context)
            context = {
                "name": request.user.first_name + " " + request.user.last_name,
                "vehicle_name": vehicle_info[0]["model"],
                "vehicle_vin": vehicle_info[0]["vin"],
                "message": "Your work schedule has not yet begun"
            }
            return render(request, self.template_name, context)

class AddEmployeeView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "add_resources.html"

    def test_func(self):
        return self.request.user.profile.is_admin

    def get(self, request, *args, **kwargs):
        form_1 = AddEmployeeForm()
        form_2 = AddMachineryForm()
        context = {
            "name": request.user.first_name,
            "form_1": form_1,
            "form_2": form_2
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form_1 = AddEmployeeForm(request.POST)
        form_2 = AddMachineryForm(request.POST)
        if form_1.is_valid():
            new_post = InviteEmployee(
                email = form_1.cleaned_data["email"],
                token = tk.Token().employee_token(),
                county = request.user.profile.county
            )
            new_post.save()
        form_2.instance.county = request.user.profile.county
        if form_2.is_valid():
            form_2.save()

        form_1 = AddEmployeeForm()
        form_2 = AddMachineryForm()

        context = {
            "name": request.user.first_name,
            "form_1": form_1,
            "form_2": form_2
        }
        return render(request, self.template_name, context)


