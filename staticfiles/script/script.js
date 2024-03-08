
 // JavaScript function to show and hide the message box
 function showMessage() {
    var messageBox = document.getElementById('messageBox');
    messageBox.style.display = 'block';
    setTimeout(function() {
        messageBox.style.display = 'none';
    }, 5000); // 5000 milliseconds = 5 seconds
  }
  
  // Call showMessage function to display the message box
  showMessage();