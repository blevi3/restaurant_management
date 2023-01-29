
  
  function updateCategory(){
    var Type = document.getElementById("Type").value;
    var category = document.getElementById("category");
    if(Type == "Option 1"){
        category.innerHTML = "<option>Option 1.1</option><option>Option 1.2</option>";
    }
    else if(Type == "Option 2"){
        category.innerHTML = "<option>Option 2.1</option><option>Option 2.2</option>";
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


$(document).on('click', '.modify-button', function() {

    var tdPriceValue = $(this).closest("td").siblings("td#tdPrice").text();
    var tdNameValue = $(this).closest("td").siblings("td#tdName").text();
    var inputValue = $(this).closest("tr").find("input#editdata").val();
    console.log(inputValue);
    document.getElementById("editItemID").value = inputValue
    document.getElementById("name").value = tdNameValue
    document.getElementById("price").value = tdPriceValue
    document.getElementById("myModal").style.display = "block";
});
