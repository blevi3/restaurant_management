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
  var tdNameValue = $(this).closest("td").siblings("td#tdTpye").text();
  var tdNameValue = $(this).closest("td").siblings("td#tdCategory").text();
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