function openTab(evt, tabName) {
  // Get all elements with class="tabcontent" and hide them
  let tabcontent = document.getElementsByClassName("tabcontent");
  for (let i = 0; i < tabcontent.length; i++) {
    tabcontent[i].classList.remove("show");
  }

  // Get all elements with class="tablinks" and remove the class "active"
  let tablinks = document.getElementsByClassName("tablinks");
  for (let i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }

  // Show the current tab and add the "active" class to the button that opened the tab
  document.getElementById(tabName).classList.add("show");
  evt.currentTarget.classList.add("active");
}

// Set the default tab to be the first one
document.getElementById("beer").classList.add("show");
document.getElementsByClassName("tablinks")[0].classList.add("active");











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
  
  
