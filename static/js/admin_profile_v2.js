
$(document).on('submit','#form-scheduale',function(e){
    e.preventDefault();
    $.ajax({
        type:'POST',
        url: "http://127.0.0.1:8000/accounts/profile-admin/",
        dataType: "json",
        async: false,
        data:JSON.stringify(
        {
            start_time:$("#id_start_time").val(),
            end_time:$("#id_end_time").val(),
        }),
        headers: {
            "X-Requested-For": "Schedule",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success:function(){
              alert('Saved');
                }
    });
});

$(document).on('submit','#drivers-listbox',function(e){
    e.preventDefault();
    var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    data_drivers = [];
    for (var i = 0; i < checkboxes.length; i++) {
      console.log(checkboxes[i].value);
      data_drivers.push(checkboxes[i].value);
    }
    $.ajax({
        type:'POST',
        url: "http://127.0.0.1:8000/accounts/profile-admin/",
        dataType: "json",
        async: false,
        data:JSON.stringify(
        {
            data:data_drivers,
            schedule:current_schedule,
        }),
        headers: {
            "X-Requested-For": "UpdateDriversSchedule",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (data) =>{
            if(data['payload'] == 'done'){
                $('#schedule').click();
                $('#schedule-drivers-add').hide();
            }
            else{
                alert(data['payload']);
            }
        },
        error: (error) => {
            console.log(error);
        }
        });
});

function removeSchedule(schedule, id, object){
    $(id).remove();
    console.log(object.id);
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      async: false,
      data: JSON.stringify({schedule: schedule}),
      headers: {
        "X-Requested-For": "ScheduleControlRemove",
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
}

function addScheduleDrivers(schedule, id_widget){
    $('#schedule-drivers-add').show();
    $('#scheduale-grid').hide();

    var result = [];
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "GET",
      dataType: "json",
      async: false,
      headers: {
        "X-Requested-For": "GetDriversWithoutSchedule",
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

    $("input").remove(".input-sch");
    $("label").remove(".label-sch");
    $("br").remove();

    current_schedule = schedule;
    for(let i=0; i < result.length; i++ ){
        console.log(result[i]["first_name"]);
        let id = "id".concat(String(i));
        $('#fildset-schedule').prepend(document.createElement('br')
        ).prepend(
        $(document.createElement('input')).prop({
            type: 'checkbox',
            id: id,
            value: JSON.stringify(result[i]),
            text: JSON.stringify(result[i]),
            className:'input-sch',
        })
        );
        let label = $(document.createElement('label')).prop({
            for: id,
            className:'label-sch',
        }).html(result[i]["first_name"] + " " + result[i]["last_name"]);
        $('#'.concat(id)).after(label);
    }
}

function closeListBox(){
    $('#schedule-drivers-add').hide();
    $('#scheduale-grid').show();
}

function getDriversScheduleAjax(){
    var result = [];
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "GET",
      dataType: "json",
      async: false,
      headers: {
        "X-Requested-For": "GetDriversWithSchedule",
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

     $("p").remove(".scedule-driver-name");
    let nodeList = document.querySelectorAll("div.grid-tools > p");
    console.log(nodeList);
    for (let i = 0; i < nodeList.length; i++) {
        const nodeId = nodeList[i].getAttribute('id');
        const counter = nodeId.split('-')[1];
        const locationId = "grid-schedule-".concat(counter);
        const content = nodeList[i].textContent;
        console.log(result[content]);
        for(const el of result[content]){
            var driver = $("<p class=\"scedule-driver-name\"></p>").text(el);
            $('#'.concat(locationId)).append(driver);
        }
    }
}

function startApp(){
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      async: true,
      data: JSON.stringify({"start": true}),
      headers: {
        "X-Requested-For": "StartApp",
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
}