var isAdding = false;
var modalTitle = "Edit game";
if (isAdding) {
    modalTitle = "Add game";
    isAdding = true;
}
var refreshModal = (isAdding) => {
  var modalTitle = "Edit game";
  if (isAdding) {
    modalTitle = "Add game";
    isAdding = true;
  }
  $('#editModalLabel').text(modalTitle);
}

var openGamesModal = (isAdding) => {
    console.log("Open model L ", isAdding)
   refreshModal(isAdding);
   $('#editModal').modal('show');
}