const copyrightYear = document.querySelector("#year");
const errorMessageContainer = document.querySelector("#error-message");
const closeErrorIcon = document.querySelector("#close-icon");
if (copyrightYear) {
  copyrightYear.textContent = (function () {
    return new Date().getFullYear();
  })();
}

closeErrorIcon.addEventListener(
  "click",
  () =>
    (errorMessageContainer.style.cssText =
      "display:none;transition: opacity 200ms, display 200ms;opacity:0")
);

setTimeout(() => (errorMessageContainer.style.cssText = "display:none;"), 4500);
