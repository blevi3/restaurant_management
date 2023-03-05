function updateCategory(Type, Category) {
  var type = document.getElementById(Type).value;
  console.log(type);
  var category = document.getElementById(Category);
  $(category).empty();
  if (type == "Food") {
     category.innerHTML =
      "<option>Hamburger</option><option>Hot-Dog</option><option>Snacks</option>";
  } else if (type == "Drink") {
    category.innerHTML =
      "<option>Beer</option><option>Wine</option>";
      console.log(category);
  }
}


function openForm(id) {
  document.getElementById(id).style.display = "block";
}
function closeForm(id) {
  document.getElementById(id).style.display = "none";
}


$(document).on("click", ".modify-button", function () {

  var tdPriceValue = $(this).closest("td").siblings("#tdPrice").text();
  var tdNameValue = $(this).closest("td").siblings("#tdName").text();
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


function toggler(){
  const navbar = document.getElementById("navbarNav");
  const nav = document.querySelector(".navbar-collapse");



    if (navbar.style.display === "none") {
      navbar.style.display = "block";
    } else {
      navbar.style.display = "none";
    }

  }

  $(".navbar-collapse").collapse('toggle');



//--------------------------------------------------------------------------------------
 //Reservation timerange Set
  var startTimeSelect = document.getElementById("id_starttime");
  var endTimeSelect = document.getElementById("id_endtime");

  var firstOption = document.createElement("option");
  firstOption.value = "";
  firstOption.selected = true;
  firstOption.text = "Select end time";
  endTimeSelect.insertBefore(firstOption, endTimeSelect.firstChild);
  var defaultOption = endTimeSelect.options[0];

  var originalEndTimeOptions = endTimeSelect.innerHTML;

  startTimeSelect.addEventListener("change", function() {
    var selectedStartTime = this.value;

    endTimeSelect.innerHTML = "";

    endTimeSelect.innerHTML = originalEndTimeOptions;
 
    for (var i = 0; i < endTimeSelect.options.length; i++) {
      var optionValue = endTimeSelect.options[i].value;
      if (optionValue <= selectedStartTime || optionValue > addMinutes(selectedStartTime, 30)) {
        endTimeSelect.options[i].disabled = true;
        
      } else {
        endTimeSelect.options[i].disabled = false;
      }
    }
  });
  
  function addMinutes(time, minutes) {
    var date = new Date("2000-01-01T" + time + ":00Z");
    date.setMinutes(date.getMinutes() + minutes);
    return date.toISOString().slice(11, 16);
  }

  endTimeSelect.addEventListener("change", function() {
    var startTimeValue = startTimeSelect.value;
    var endTimeValue = endTimeSelect.value;
    if (endTimeValue <= startTimeValue) {
      endTimeSelect.selectedIndex = defaultOption.index;
    }
  });
  
