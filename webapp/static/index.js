// Function for deleting the summaries that are displayed
function deleteSumm(summId) {

  // Fetching the delete-sum function from pages.py using POST method
  fetch("/delete-summ", {
    method: "POST",
    body: JSON.stringify({ summId: summId }),
  }).then((_res) => {

    // Refreshes the Home page
    window.location.href = "/";
  });
}