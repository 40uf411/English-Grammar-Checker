// mode 0:idl, 1: after checking
mode = 0;

send = document.getElementById("send-button");
text = document.getElementById("text-data");
sucs = document.getElementById("result-success");

fail = document.getElementById("result-fail");
ltfl = document.getElementById("load-test-file");

lrfl = document.getElementById("load-train-file");
tran = document.getElementById("train-model");
flsl = document.getElementById("you-selected-a-file");

erdv = document.getElementById("errors-div");
errr = document.getElementById("errors");

var trainingText = ''
send.onclick = () => {
  if (mode == 0) {
    if (text.value.length >= 10) {
      send.innerHTML = "Loading";
      send.disabled = true;
      console.log();
      var formData = new FormData();
      formData.append("text", text.value);
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
          data = xmlHttp.response;
          response = JSON.parse(data);
          console.log(response);
          if (response.result) {
            sucs.style.display = "block";
          } else {
            fail.style.display = "block";
            erdv.style.display = "block";
            errr.innerHTML = response.errors
          }
          send.innerHTML = "Clear";
          send.disabled = false;
          mode = 1;
        }
      };
      xmlHttp.open("post", "/check");
      xmlHttp.send(formData);
    }
  } else {
    text.value = "";
    sucs.style.display = "none";
    fail.style.display = "none";
    erdv.style.display = "none";
    send.innerHTML = "Check";
    mode = 0;
  }
};

ltfl.onclick = function () {
  openFile(function (txt) {
    text.value = txt;
  }, 0);
};

lrfl.onclick = function () {
  openFile(function (txt) {
      trainingText = txt
    flsl.innerHTML = "<b>You have selected the following text:</b><br> " + txt;
  }, 0);
};

tran.onclick = function () {
    var formData = new FormData();
    formData.append("text", trainingText);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        data = xmlHttp.response;
        response = JSON.parse(data);
        console.log(response);
        flsl.innerHTML = "Awesome! the training is complete!";
      }
    };
    xmlHttp.open("post", "/train");
    xmlHttp.send(formData);
};

function openFile(callBack, id) {
  var element = document.createElement("input");
  element.setAttribute("type", "file");
  element.setAttribute("id", "btnOpenFile" + id);
  element.onchange = function () {
    readText(this, callBack);
    document.body.removeChild(this);
  };

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();
}

function readText(filePath, callBack) {
  var reader;
  if (window.File && window.FileReader && window.FileList && window.Blob) {
    reader = new FileReader();
  } else {
    alert(
      "The File APIs are not fully supported by your browser. Fallback required."
    );
    return false;
  }
  var output = ""; //placeholder for text output
  if (filePath.files && filePath.files[0]) {
    reader.onload = function (e) {
      output = e.target.result;
      callBack(output);
    }; //end onload()
    reader.readAsText(filePath.files[0]);
  } //end if html5 filelist support
  else {
    //this is where you could fallback to Java Applet, Flash or similar
    return false;
  }
  return true;
}
