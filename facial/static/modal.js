const deleteBtn = document.querySelector("#del-btn");
const modalForm = document.querySelector("#deleteModal");
const confirmBtn = modalForm.querySelector("#confirmBtn");
const cancelBtn = modalForm.querySelector("#cancelBtn");

cancelBtn.addEventListener("click", (e) => {
  //prevent cancelBtn submit action
  e.preventDefault();
  modalForm.close();
});

deleteBtn.addEventListener("click", () => {
  modalForm.showModal();
});
