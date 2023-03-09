
function DirectionsToggle(){
  var el = $('#dir-toggle');
  var dir_table = $('#dir-table')
  if (dir_table.attr("hidden") == "hidden") {
    dir_table.fadeIn()
    dir_table.removeAttr("hidden")
    el.html('hide <a href="javascript:void(0)" onclick="DirectionsToggle()">here')
  } else {
    dir_table.fadeOut()
    dir_table.attr("hidden", "hidden")
    el.html('click <a href="javascript:void(0)" onclick="DirectionsToggle()">here')
  }
}

function previousRoute(){
$.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-worker/",
      type: "GET",
      dataType: "json",
      async: false,
      headers: {
        "X-Requested-For": "MapsPreviousLap",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
        location.reload();
      },
      error: (error) => {
        console.log(error);
      }
    });
}

function nextRoute(){
$.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-worker/",
      type: "GET",
      dataType: "json",
      async: false,
      headers: {
        "X-Requested-For": "MapsNextLap",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
        location.reload();
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

