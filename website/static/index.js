function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/Home";
    });
  }

function deleteExpense(expenseId, expenseType) {
    console.log('Deleting expense:', expenseId, 'Type:', expenseType);
  
    fetch('/delete-expense', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        expenseId: expenseId,
        expenseType: expenseType,
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Server response:', data);
  
        // Remove the expense from the UI
        var expenseElement = document.getElementById(expenseType + 'ExpenseAmount' + expenseId);
        if (expenseElement) {
          expenseElement.parentNode.parentNode.removeChild(expenseElement.parentNode);
        }
  
        // Refresh the window
        location.reload();
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }