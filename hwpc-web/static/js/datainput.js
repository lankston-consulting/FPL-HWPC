// Run button
let getdata = document.getElementById("getdata");

// Optional inputs button
let options = document.getElementById("options");

let customregion = document.getElementById("customregion");
let regionselection = document.getElementById("regionselection");
let customfileinput = document.getElementById("customfileinput");

customregion.addEventListener("click", (e) => {
  regionselection.value = "";
  customfileinput.setAttribute("required", "true");
});

customfileinput.addEventListener("click", (e) => {
  regionselection.value = "";
  customregion.setAttribute("required", "true");
});

getdata.addEventListener("click", (e) => {
  if ($("#forms")[0].checkValidity()) {
    document.getElementById("overlay").classList.toggle("is-hidden");
  }
});

let temp;
options.addEventListener("click", (e) => {
  temp = document.getElementsByClassName("optional");
  for (const element of temp) {
    element.classList.toggle("is-hidden");
  }
  let body_height = document.getElementById("wrapper").scrollHeight + "px";
  window.parent.postMessage(body_height, "*");
});
