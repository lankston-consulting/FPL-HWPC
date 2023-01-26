// In use -> Emitted with energy capture, products in use
// Discarded Products -> Emitted with energy capture (burned with energy capture)

$(function () {
  $("#inUse").hover(
    function () {
      $("#emittedEnergyCapture, #productsInUse").css(
        "background-color",
        "yellow"
      );
    },
    function () {
      // on mouseout, reset the background colour
      $("#emittedEnergyCapture, #productsInUse").css("background-color", "");
    }
  );
});

$("#inUse").focus(function () {
  $(
    function () {
      $("#emittedEnergyCapture, #productsInUse").css(
        "background-color",
        "yellow"
      );
    },
    function () {
      $("#emittedEnergyCapture, #productsInUse").css("background-color", "");
    }
  );
});
