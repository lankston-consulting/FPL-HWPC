const headers = ["H1", "H2", "H3", "H4", "H5", "H6"]; //We only use h1 and h2

function toggleAccordion(e, edit_mode = false) {
  let target;
  let name;
  if (e.type != undefined) {
    target = e.target;
     name = target.nodeName.toUpperCase();
  } else {
     target = e;
     name = target.nodeName.toUpperCase();
  }

  //only select target if target does not have acc-disabled class
  if (!target.classList.contains("acc-disabled")) {
    if ($.inArray(name, headers) > -1) {
      let subItem = $(target).next();

      //slideUp all elements (except target) at current depth or greater
      if (!edit_mode) {
        let depth = $(subItem).parents().length;
        let allAtDepth = $(".accordion div").filter(function () {
          if ($(this).parents().length >= depth && this !== subItem.get(0)) {
            return true;
          }
        });
        $(allAtDepth).slideUp("fast");
      }
      //slideToggle target content and adjust bottom border if necessary
      subItem.slideToggle("fast", function () {
        $(".accordion :visible:last");
      });
    }
  }
}

// when mc-disclaimer is clicked remove acc-disabled class from all elements

$("#mc-disclaimer").click(function () {
  $(".accordion").find(".disabled").removeClass("disabled");
  $("#monte-carlo-sim").attr({
    "max" : 2000})
  $("#monte-carlo-sim").val(1000);
});

$(".acc-h1, .acc-h2").click(function (e) {
  $("#default-mode").prop("checked", true);
  toggleAccordion(e);
});

$(".acc-h1, .acc-h2").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    toggleAccordion(event);
  }
});

$(".nextbtn").click(function (e) {
  let class_list = $(e.target).attr("class").split(/\s+/);
  let id_split = class_list[1].split("-");
  toggleAccordion($("#" + class_list[1])[0]);
  toggleAccordion(
    $("#" + id_split[0] + "-0" + (parseInt(id_split[1]) + 1))[0],
    true
  );
});

$(".backbtn").click(function (e) {
  let class_list = $(e.target).attr("class").split(/\s+/);
  let id_split = class_list[1].split("-");
  toggleAccordion($("#" + class_list[1])[0]);
  toggleAccordion(
    $("#" + id_split[0] + "-0" + (parseInt(id_split[1]) - 1))[0],
    true
  );
});

$("#edit-mode").change(function (e) {
  for (const element of $(".acc-h1")) {
    if (element.nextSibling.nextSibling.style.display != "block") {
      toggleAccordion(element, true);
    }
  }
});

$("#default-mode").change(function (e) {
  for (const element of $(".acc-h1")) {
    if (element.nextSibling.nextSibling.style.display == "block") {
      toggleAccordion(element, true);
    }
  }
});

$(".edit-mode").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    $("#edit-mode").prop("checked", true);
    for (const element of $(".acc-h1")) {
      if (element.nextSibling.nextSibling.style.display != "block") {
        toggleAccordion(element, true);
      }
    }
  }
});
$(".default-mode").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    $("#default-mode").prop("checked", true);
    for (const element of $(".acc-h1")) {
      if (element.nextSibling.nextSibling.style.display == "block") {
        toggleAccordion(element, true);
      }
    }
  }
});
//mbf to ccf toggle
$(document).ready(function () {
  $('input[type="radio"]').click(function () {
    if ($(this).attr("id") == "mbf") {
      $("#mbftoccf-custom-fu").show();
    } else {
      $("#mbftoccf-custom-fu").hide();
    }
  });
});

$(document).ready(function () {
  $('input[type="radio"]').click(function () {
    if ($(this).attr("id") == "customRatio") {
      $("#custom-file-upload").show();
    } else {
      $("#custom-file-upload").hide();
    }
  });
});

$("#ccf-label").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    $("#ccf").prop("checked", true);
    $("#mbftoccf-custom-fu").hide();
  }
});

$("#mbf-label").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    $("#mbf").prop("checked", true);
    $("#mbftoccf-custom-fu").show();
  }
});

// trigger upload on space & enter
// = standard button functionality
$("#buttonlabel span[role=button]").bind("keypress keyup", function (e) {
  if (e.which === 32 || e.which === 13) {
    e.preventDefault();
    $(".fileupload").click();
  }
});

// return chosen filename to additional input
$(".fileupload").change(function (e) {
  let class_list = $(e.target).attr("class").split(/\s+/);
  let id = class_list[1];
  let filename = $("." + id)
    .val()
    .split("\\")
    .pop();
  $("#" + id).val(filename);
  $("#" + id).attr("placeholder", filename);
  $("#" + id).focus();
  if (class_list[1] == "filename4") {
    $("#regionselection").val("Custom").change();
  }
});

// Set upload file input to null if user clicks on the delete btn
$(".cancel-upload-btn").click(function (e) {
  $(
    e.target
  )[0].previousElementSibling.previousElementSibling.previousElementSibling.value =
    null;
  $(e.target)[0].previousElementSibling.value = null;
  if($(e.target)[0].previousElementSibling.previousElementSibling.previousElementSibling.id == "fu-yearly-harvest" 
  || $(e.target)[0].previousElementSibling.previousElementSibling.previousElementSibling.id == "yearlytimberproductratios"){
    $(e.target)[0].previousElementSibling.placeholder = "No file uploaded";
  }
  else if($(e.target)[0].previousElementSibling.previousElementSibling.previousElementSibling.id == "customregion" ){
    $("#regionselection").val("North Central").change();
    $(e.target)[0].previousElementSibling.placeholder = "Using default";
  }
  else{
    $(e.target)[0].previousElementSibling.placeholder = "Using default";
  }
});

$("#email-address").on("input", function () {
  let input = $(this);
  let re =
    /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
  let is_email = re.test(input.val());
  if (is_email) {
    input.removeClass("invalid").addClass("valid");
  } else {
    input.removeClass("valid").addClass("invalid");
  }
});

$(".info-circle").click(function (e) {
  $("#modal").css("display", "block");
  $(".close").focus();
  $("#modal-content").html(modal_dict[e.target.id]);
});

$(".info-circle").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    $("#modal").css("display", "block");
    $(".close").focus();
    $("#modal-content").html(modal_dict[event.target.lastChild.id]);
  }
});

$(".info-link").click(function (e) {
  $("#modal").css("display", "block");
  $(".close").focus();
  $("#modal-content").html(modal_dict[e.target.id]);
});

$(".info-link").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    $("#modal").css("display", "block");
    $(".close").focus();
    $("#modal-content").html(modal_dict[event.target.lastChild.id]);
  }
});

$(".close").click(function (e) {
  $(".modal").css("display", "none");
});

$(".close").keydown(function (event) {
  if (event.which === 32 || event.which === 13) {
    //32 is Space and 13 is Enter
    $(".modal").css("display", "none");
    $(".info-circle").focus();
  }
});
// Preview Modal
$("#previewbtn").click(function (e) {
  let input_harvest = $("[name='yearlyharvestinput']").val();
  let harvest;
  if (input_harvest != "") {
    input_harvest = input_harvest.split("\\");
    input_harvest = input_harvest[input_harvest.length - 1];
    harvest =
      '<p class="modal-input-data acc-01">Annual Harvest Data: ' +
      input_harvest +
      "</p><br>";
  } else {
    harvest =
      '<p class="modal-input-data acc-01">Annual Harvest Data: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  let input_mbf_to_ccf = $("[name='MbfToCcfFilename']").val();
  let mbf_to_ccf;
  if (input_mbf_to_ccf != "") {
    input_mbf_to_ccf = input_mbf_to_ccf.split("\\");
    input_mbf_to_ccf = input_mbf_to_ccf[input_mbf_to_ccf.length - 1];
    mbf_to_ccf =
      '<p class="modal-input-data acc-01">MBF to CCF Ratios: ' +
      input_mbf_to_ccf +
      "</p><br>";
  } else {
    mbf_to_ccf =
      '<p class="modal-input-data acc-01">MBF to CCF Ratios: Using Default</p><br>';
  }

  let input_timber_product_ratios = $("[name='yearlytimberproductratios']").val();
  let timber_product_ratios;
  if (input_timber_product_ratios != "") {
    input_timber_product_ratios = input_timber_product_ratios.split("\\");
    input_timber_product_ratios =
      input_timber_product_ratios[input_timber_product_ratios.length - 1];
    timber_product_ratios =
      '<p class="modal-input-data acc-02">Timber Product Ratios: ' +
      input_timber_product_ratios +
      "</p><br>";
  } else {
    timber_product_ratios =
      '<p class="modal-input-data acc-02">Timber Product Ratios: Using Default</p><br>';
  }

  let region_input = $("[name='regionselection']").val();
  let region;
  if (region_input != "") {
    region =
      '<p class="modal-input-data acc-03">Region Selected: ' +
      region_input +
      "</p><br>";
  } else {
    region =
      '<p class="modal-input-data acc-03">Region Selected: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  let primary_product_ratios = $("[name='PrimaryProductRatiosFilename']").val();
  let primary_product;
  if (primary_product_ratios != "") {
    primary_product_ratios = primary_product_ratios.split("\\");
    primary_product_ratios =
      primary_product_ratios[primary_product_ratios.length - 1];
    primary_product =
      '<p class="modal-input-data acc-03b">Primary Product Ratios: ' +
    primary_product_ratios +
      "</p><br>";
  } else {
    primary_product =
      '<p class="modal-input-data acc-03b">Primary Product Ratios: Using Default</p><br>';
  }


  let input_end_use_rates = $("[id='chi']");
  let end_use_rates;
  if (input_end_use_rates[0].checked) {
    end_use_rates =
      '<p class="modal-input-data acc-04">End Use In Use Function: Chi squared' +
      "</p><br>";
  } else {
    end_use_rates =
      '<p class="modal-input-data acc-04">End Use In Use Function: Exponential</p><br>';
  }
  // if (input_end_use_rates != "") {
  //   input_end_use_rates = input_end_use_rates.split("\\");
  //   input_end_use_rates = input_end_use_rates[input_end_use_rates.length - 1];
  //   end_use_rates =
  //     '<p class="modal-input-data acc-04b">End Use In Use Function: ' +
  //     input_end_use_rates +
  //     "</p><br>";
  // } else {
  //   end_use_rates =
  //     '<p class="modal-input-data acc-04b">End Use In Use Function: Using Default</p><br>';
  // }

  let input_end_use_ratios = $("[name='EndUseRatiosFilename']").val();
  let end_use_ratios;
  if (input_end_use_ratios != "") {
    input_end_use_ratios = input_end_use_ratios.split("\\");
    input_end_use_ratios =
      input_end_use_ratios[input_end_use_ratios.length - 1];
    end_use_ratios =
      '<p class="modal-input-data acc-04c">End Use Ratios: ' +
      input_end_use_ratios +
      "</p><br>";
  } else {
    end_use_ratios =
      '<p class="modal-input-data acc-04c">End Use Ratios: Using Default</p><br>';
  }

  let input_discard_dispostions = $("[name='DispositionsFilename']").val();
  let discard_dispostions;
  if (input_discard_dispostions != "") {
    input_discard_dispostions = input_discard_dispostions.split("\\");
    input_discard_dispostions =
      input_discard_dispostions[input_discard_dispostions.length - 1];
    discard_dispostions =
      '<p class="modal-input-data acc-04d">Discard Product Dispositions Ratios: ' +
      input_discard_dispostions +
      "</p><br>";
  } else {
    discard_dispostions =
      '<p class="modal-input-data acc-04d">Discard Product Dispositions Ratios: Using Default</p><br>';
  }

  let input_discard_dispostions_half_lives = $("[name='DispositionHalfLivesFilename']").val();
  let discard_dispostions_half_lives;
  if (input_discard_dispostions_half_lives != "") {
    input_discard_dispostions_half_lives =
      input_discard_dispostions_half_lives.split("\\");
    input_discard_dispostions_half_lives =
      input_discard_dispostions_half_lives[
        input_discard_dispostions_half_lives.length - 1
      ];
    discard_dispostions_half_lives =
      '<p class="modal-input-data acc-04e">Discard Dispositions Decay Ratios: ' +
      input_discard_dispostions_half_lives +
      "</p><br>";
  } else {
    discard_dispostions_half_lives =
      '<p class="modal-input-data acc-04e">Discard Dispositions Decay Ratios: Using Default</p><br>';
  }

  let input_burned = $("[name='BurnedRatiosFilename']").val();
  let burned;
  if (input_burned != "") {
    input_burned = input_burned.split("\\");
    input_burned = input_burned[input_burned.length - 1];
    burned =
      '<p class="modal-input-data acc-04f">Discarded Burned with energy capture Ratios: ' +
      input_burned +
      "</p><br>";
  } else {
    burned =
      '<p class="modal-input-data acc-04f">Discarded Burned with energy capture Ratios: Using Default</p><br>';
  }

  let input_loss_factor = $("[name='lossfactor']").val();
  let loss_factor;
  if (input_loss_factor != "") {
    input_loss_factor = input_loss_factor.split("\\");
    input_loss_factor = input_loss_factor[input_loss_factor.length - 1];
    loss_factor =
      '<p class="modal-input-data acc-05">Loss Factor: ' +
      input_loss_factor +
      "</p><br>";
  } else {
    loss_factor =
      '<p class="modal-input-data acc-05">Loss Factor: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  let input_iterations = $("[name='iterations']").val();
  let iterations;
  if (input_iterations != "") {
    input_iterations = input_iterations.split("\\");
    input_iterations = input_iterations[input_iterations.length - 1];
    iterations =
      '<p class="modal-input-data acc-06">Number of Monte Carlo Iterations: ' +
      input_iterations +
      "</p><br>";
  } else {
    iterations =
      '<p class="modal-input-data acc-06">Number of Monte Carlo Iterations: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  let input_distribution = $("[name='DistributionDataFilename']").val();
  let distribution;
  if (input_distribution != "") {
    input_distribution = input_distribution.split("\\");
    input_distribution = input_distribution[input_distribution.length - 1];
    distribution =
      '<p class="modal-input-data acc-06">Distribution Parameters: ' +
      input_distribution +
      "</p><br>";
  } else {
    distribution =
      '<p class="modal-input-data acc-06">Distribution Parameters: Using Default</p><br>';
  }

  let input_email = $("[name='email']").val();
  let email;
  if (input_email != "") {
    input_email = input_email.split("\\");
    input_email = input_email[input_email.length - 1];
    email =
      '<p class="modal-input-data acc-07">Email: ' + input_email + "</p><br>";
  } else {
    email =
      '<p class="modal-input-data acc-07">Email: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  let input_runname = $("[name='runname']").val();
  let runname;
  if (input_runname != "") {
    input_runname = input_runname.split("\\");
    input_runname = input_runname[input_runname.length - 1];
    runname =
      '<p class="modal-input-data acc-08">Run Name: ' +
      input_runname +
      "</p><br>";
  } else {
    runname =
      '<p class="modal-input-data acc-08">Run Name: <span style="color:red;">MISSING REQUIRED DATA</span></p><br>';
  }

  $("#preview-modal").css("display", "block");
  $("#preview-modal-content").html(
    harvest +
      mbf_to_ccf +
      timber_product_ratios +
      region +
      primary_product +
      end_use_rates +
      end_use_ratios +
      discard_dispostions +
      discard_dispostions_half_lives +
      burned +
      loss_factor +
      iterations +
      distribution +
      email +
      runname
  );
  $(".modal-input-data").click(function (e) {
    let class_list = $(e.target).attr("class").split(/\s+/);
    $("#preview-modal").css("display", "none");
    $("#" + class_list[1])
      .get(0)
      .scrollIntoView({ behavior: "smooth", block: "center" });
  
    if (
      class_list[1] == "acc-04a" ||
      class_list[1] == "acc-04b" ||
      class_list[1] == "acc-04c" ||
      class_list[1] == "acc-04d" ||
      class_list[1] == "acc-04e" ||
      class_list[1] == "acc-04f"
    ) {
      toggleAccordion($("#" + class_list[1].slice(0, -1))[0]);
      toggleAccordion($("#" + class_list[1])[0]);
    }
    else {
      toggleAccordion($("#" + class_list[1])[0]);
    }
  });
});

const modal_dict = {
  modal1:
    "A .csv file containing the yearly harvest amount per year in units of CCF (hundred cubic feet). Also see <i>Harvest Data</i> section from the workbook. <br />Should be formatted as follows:<br /><table><tr><th>Year, </th><th>Total</th></tr><tr><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th></tr></table>",
  modal2:
    "A .csv file containing the ratios which harvested wood is converted into timber products. Also see <i>Timber Product Ratios</i> section from the workbook.<br />Should be formatted as follows:<br /><table><tr><th>Timber Product ID,</th><th>TPO Code,</th><th>Timber Description, </th><th>Year 1, </th><th>Year N</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr></table>",
  modal3:
    "A .csv file containing the ratios which a region converts timber products into primary products. Either select a defined region in the drop down, or define a custom region by selecting Custom and inputting a .csv file. Also see <i>Primary Product Ratios</i> section from the workbook. <br />Should be formatted as follows:<br /><table><tr><th>Primary Product ID,</th><th>Timber Product,</th><th>Primary Product, </th><th>Year 1, </th><th>Year N</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr></table>",
  modal4:
    "A .csv file for each end use, this gives the rate at which material is discarded. Default rate is in half-life but can also use the Chi parameter.",
  modal5:
    "A .csv file containing the ratios which primary products are converted to end use products. Also see <i>End Use Product Ratios</i> section from the workbook. <br />Should be formatted as follows:<br /><table><tr><th>End Use Id, </th><th>Primary Product,</th><th> End Use Product, </th><th>Year 1, </th><th>Year N</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr></table>",
  modal6:
    "A .csv file containing the ratios in which products are discarded into their destination dispositions. All years for modeling need ratios, where the “wood” ratios must sum to 1, and the ratios for “paper” must also sum to 1. <br> Also see <i>End Use Product Ratios</i> section from the workbook.<br />Should be formatted as follows:<br /><table><tr><th>Disposition ID, </th><th>Discard Type, </th><th>Discard Destination, </th><th>Year 1, </th><th>Year N</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th><th>X</th><th>X</th><th>X</th></tr></table>",
  modal7:
    "A .csv file containing the half-life decay ratios of the discarded disposition destinations. Also see <i>Discard Half Lives</i> section from the workbook. <br/> Should be formatted as follows: <br/><table><tr><th>Type Id, </th><th>Discard Type, </th><th>Landfill Fixed Ratio, </th><th>Landfill Half Life, </th><th>Dump Half Life, </th><th>Recycled Half Life</th></tr><tr><th>0</th><th>paper</th><th>X</th><th>X</th><th>X</th><th>X</th></tr><th>1</th><th>wood</th><th>X</th><th>X</th><th>X</th><th>X</th><tr></tr></table> ",
  modal8:
    "A .csv file containing the proportions for burned with energy capture. Also see <i>Discard Burned w Energy Capture</i> section from the workbook. <br/> Should be formatted as follows: <br/><table><tr><th>Year, </th><th>Percent</th></tr><tr><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th></tr></table>",
  modal9:
    "Enter a percentage between 0 and 100 of how much wood product is end-use loss.",
  modal10:
    "Enter a number of Monte Carlo Simulations between 1000 and 5000 runs.<br /> A .csv file containing the distribution parameters.",
  modal11:
    "Email is required to send you link of the completed simulation outputs.",
  modal12: "Name of Run to label zip file.",
  modal13: "If harvest data is in MBF and you would like to upload a custom MBF to CCF ratio here to the modal, otherwise the Calculator will use the default MBF to CCF ratios. Also see <i>MBF to CCF</i> section from the workbook.<br /> Should be formatted as follows:<br /> <table><tr><th>Start Year, </th><th>Conversion Factor</th></tr><tr><th>X</th><th>X</th></tr><tr><th>X</th><th>X</th></tr></table>",
  modal14: "<b>Temporary Image</b> <br> <img src='static/images/image007.png' width='100%'>"
};

$("#getdata").click(function (e) {
    toggleAccordion($("#acc-01")[0], true);
    toggleAccordion($("#acc-02")[0], true);
    toggleAccordion($("#acc-05")[0], true);
    toggleAccordion($("#acc-06")[0], true);
    toggleAccordion($("#acc-07")[0], true);
  $(".required-alert").each(function () {
    let temp_alert = $(this);
    $(this)
      .siblings()
      .each(function () {
        if ($(this).is("input")) {
          if (
            !$(this)[0].validity.valid &&
            $(this)[0].required
          ) {
            temp_alert.show();
            e.preventDefault();
          }
          else if ($(this)[0].id == "run-name") {
            if (validate_runname($(this)[0].value) == false) {
              temp_alert.show();
              e.preventDefault();
            } else {
              temp_alert.hide();
            }
          }
          else if (
            $(this)[0].validity.valid &&
            $(this)[0].required
          ) {
            temp_alert.hide();
          }
          
        }
      });
  });
});


function validate_runname(name) {
  let valid;
  // Regex alpha, numeric, underscore, dash, no special characters
  let nameRGEX = new RegExp(/^([a-zA-Z0-9 _-]+)$/);
  let nameResult = nameRGEX.test(name);
  if (!nameResult) {
    window.alert("Please enter a valid name for the run. No special characters allowed.");
    valid = false;
  }
  else {
    valid = true;
  }
  return valid
}

//Jquery function for drag and drop on file inputs
$(function () {
  let fileInputs = $(".file-input");
  fileInputs.each(function () {
    ondragover = function (e) {
      e.preventDefault();
      $(this).addClass("dragover");
    };
    ondrop = function (e) {
      fileInput.files = evt.dataTransfer.files;
    }
  });
})

