
    // Add the jQuery code to handle the button click event and show the modal
    $(document).ready(function(){
      // Get the button that opens the modal
      var btn = document.getElementById("modify-button");
      // Get the modal
      console.log('jquery');
      var modal = document.getElementById("modify-modal");
      // Get the <span> element that closes the modal
      var span = document.getElementsByClassName("close")[0];
      // When the user clicks the button, open the modal 
      btn.onclick = function() {
          modal.style.display = "block";
          modal.style.tabindex = 1;
          console.log('jquery');
      }
      // When the user clicks on <span> (x), close the modal
      span.onclick = function() {
          modal.style.display = "none";
      }
      // When the user clicks anywhere outside of the modal, close it
      window.onclick = function(event) {
          if (event.target == modal) {
              modal.style.display = "none";
          }
      }
  });
  
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
