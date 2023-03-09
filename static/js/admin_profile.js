var user_id;
var view_user_id;

//Scheduale
document.getElementById("scheduale-cover").addEventListener("click", function(event){
            document.getElementById("scheduale-cover").style.display = "none";
            document.getElementById("scheduale-grid").style.display = "none";
            document.getElementById("scheduale-time").style.display='none';
            document.getElementById("schedule-drivers-add").style.display='none';
        });

function newScheduale(){
    document.getElementById("scheduale-time").style.display='block';
}

function exitNewScheduale(){
    document.getElementById("scheduale-time").style.display='none';
}
function updateScheduale(){
    document.getElementById("scheduale-grid").style.display='block';
    document.getElementById("scheduale-cover").style.display='block';
    getDriversScheduleAjax();
}


function remove_tool(id, id_nr, object){
    document.getElementById("car_name-" + id_nr).innerText = "";
    console.log(id);
    updateModelRelationship(id);
}

function updateModelRelationship(id){
    var result;
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      async: false,
      data: JSON.stringify({id: id}),
      headers: {
        "X-Requested-For": "EmployeeMachineryControl",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
      result = data['payload'];
      },
      error: (error) => {
        console.log(error);
      }
    });
    return result;
}

function add_tool(id, id_nr, object){
    user_id = id
    view_user_id = id_nr
    const element = document.getElementById("vehicle-form");
    if(element != null){
        newBody = document.getElementById("body-form");
        newBody.style.display = "block";
        newDiv = document.getElementById("vehicle-form");
        newDiv.style.display = "block";
        newDiv.replaceChildren();
        createChildren(newBody,newDiv);
    }else{
        var newBody = document.createElement("div");
        newBody.setAttribute("id","body-form");
        newBody.setAttribute("style","position: fixed; width:100%; height:100%; top: 0; background-color: rgb(139, 139, 158); opacity: 0.4;");
        var newDiv = document.createElement("div");
        newDiv.setAttribute("id","vehicle-form");
        newDiv.setAttribute("style"," overflow-y:scroll; scrollbar-color: rebeccapurple green;  scrollbar-width: thin; position: fixed; width:350px; height:400px; background-color: #D8BFD8; top:0; bottom:0; left:0; right:0; margin:auto; border-radius: 10px; border-color:#ADD8E6; cursor:pointer; box-shadow: 0 0 18px rgb(255 182 193 / 100%);  border-style: outset;");
        document.body.appendChild(newBody);
        document.body.appendChild(newDiv);
        document.getElementById("body-form").addEventListener("click", function(event){
            document.getElementById("body-form").style.display = "none";
            document.getElementById("vehicle-form").style.display = "none";
        });

        createChildren(newBody, newDiv);

    }
}

function createChildren(newBody, newDiv){
    data = get_data();
    var message = document.createElement("p");
    message.innerText = "Select Vehicle";
    message.setAttribute("style", "position:sticky; top:10px; padding-left: 0px; text-align: center; font-size:25px; color:#2F4F4F; background-color:#ADD8E6;  border-style: outset;")
    newDiv.appendChild(message);

    var el = 0;
    for( ; el < data.length; el++){
        var btn = document.createElement("button");
        const id = "btn" + el.toString();
        btn.setAttribute("id", id);
        btn.setAttribute("style", "display:flex; flex-direction:column; justify-content: space-evenly; width: 100%; height:100px; background-color: #008B8B; margin-top:15px; border-width:5px; border-color: #ADD8E6; padding-left:20px; cursor: pointer;");
        var span1 = document.createElement("span");
        span1.style.color = "#F0F8FF";
        span1.style.fontSize = "15";
        span1.innerText = "Brand: " +data[el][1];
        var span2 = document.createElement("span");
        span2.style.color = "#F0F8FF";
        span2.style.fontSize = "15";
        span2.innerText = "VIN: " + data[el][0];
        btn.appendChild(span1);
        btn.appendChild(span2);
        newDiv.appendChild(btn);
        btn.addEventListener('click', update_employee_vehicle, false);
    }
}

function update_employee_vehicle(object){
    var value = this.lastChild.innerText.split(' ')[1];
    data = updateModel(value, user_id);
    if (data != 'exists'){
        element_id = "car_name-" + view_user_id;
        document.getElementById(element_id).innerText = data[2];
        document.getElementById("body-form").style.display = "none";
        document.getElementById("vehicle-form").style.display = "none";
    }else{
        alert("Already has a car!");
    }
}

function updateModel(vin, id){
    var result;
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      async: false,
      data: JSON.stringify({vin: vin, id: id}),
      headers: {
        "X-Requested-For": "EmployeeControl",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
      result = data['driver-name'];
      },
      error: (error) => {
        console.log(error);
      }
    });
    return result;
}

function get_data(){
    var result;
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "GET",
      dataType: "json",
      async: false,
      headers: {
        "X-Requested-For": "GetVehiclesWithoutDriver",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
        result = data["data"];
      },
      error: (error) => {
        console.log(error);
      }
    });
    return result;
}


function update_vehicle_status(vin, lst_digit, object){
    vin = vin.toString();
    vin = vin.replace(/.$/,lst_digit);
    const id = object.id[object.id.length-1];
    const obj_id = "vehicle-status-" + id;

    if (object.style.backgroundColor == "aquamarine"){
       object.style.backgroundColor ="lightpink";
       document.getElementById(obj_id).innerHTML = "Not Ready:";
       updateStatus(vin, false);
    }
    else{
        object.style.backgroundColor ="aquamarine";
        document.getElementById(obj_id).innerHTML = "Ready:";
        updateStatus(vin, true);
   }
}

function updateStatus(value, status) {

    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      data: JSON.stringify({vin: value, value: status }),
      headers: {
        "X-Requested-For": "MachineryControl",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
        console.log(data);
      },
      error: (error) => {
        console.log(error);
      }
    });

}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

