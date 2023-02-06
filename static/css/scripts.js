function updateCategory() {
  var Type = document.getElementById("Type").value;
  var category = document.getElementById("category");
  if (Type == "Option 1") {
    category.innerHTML =
      "<option>Option 1.1</option><option>Option 1.2</option>";
  } else if (Type == "Option 2") {
    category.innerHTML =
      "<option>Option 2.1</option><option>Option 2.2</option>";
  }
}

function updateCategory() {
  var Type = document.getElementById("Type").value;
  var category = document.getElementById("category");

  var option1 = document.createElement("option");
  option1.value = "option1";
  option1.text = "Option 1";

  var option2 = document.createElement("option");
  option2.value = "option2";
  option2.text = "Option 2";

  if (Type == "Option 1") {
    category.appendChild(option1);
  } else if (Type == "Option 2") {
    category.appendChild(option2);
  }
}

$(document).on("click", ".modify-button", function () {
  var tdPriceValue = $(this).closest("td").siblings("td#tdPrice").text();
  var tdNameValue = $(this).closest("td").siblings("td#tdName").text();
  var inputValue = $(this).closest("tr").find("input#editdata").val();
  document.getElementById("editItemID").value = inputValue;
  document.getElementById("name").value = tdNameValue;
  document.getElementById("price").value = tdPriceValue;
  document.getElementById("myModal").style.display = "block";
});

$(document).ready(function () {
  var path = window.location.pathname;
  $(".navbar-nav a").each(function () {
    if ($(this).attr("href") == path) {
      $(this).addClass("active");
    }
  });
});



(function () {
  "use strict";
  var $ = jQuery;
  $.fn.extend({
    filterTable: function () {
      return this.each(function () {
        $(this).on("keyup", function (e) {
          $(".filterTable_no_results").remove();
          var $this = $(this),
            search = $this.val().toLowerCase(),
            target = $this.attr("data-filters"),
            $target = $(target),
            $rows = $target.find("tbody tr");

          if (search == "") {
            $rows.show();
          } else {
            $rows.each(function () {
              var $this = $(this);
              $this.text().toLowerCase().indexOf(search) === -1
                ? $this.hide()
                : $this.show();
            });
            if ($target.find("tbody tr:visible").size() === 0) {
              var col_count = $target.find("tr").first().find("td").size();
              var no_results = $(
                '<tr class="filterTable_no_results"><td colspan="' +
                  col_count +
                  '">No results found</td></tr>'
              );
              $target.find("tbody").append(no_results);
            }
          }
        });
      });
    },
  });
  $('[data-action="filter"]').filterTable();
})(jQuery);

$(function () {
  // attach table filter plugin to inputs
  $('[data-action="filter"]').filterTable();

  $(".container").on("click", ".panel-heading span.filter", function (e) {
    var $this = $(this),
      $panel = $this.parents(".panel");

    $panel.find(".panel-body").slideToggle();
    if ($this.css("display") != "none") {
      $panel.find(".panel-body input").focus();
    }
  });
  $('[data-toggle="tooltip"]').tooltip();
});
