document.addEventListener(
  "DOMContentLoaded",
  // once the page is loaded
  () => {
    console.log("DOMContentLoaded")
    console.log("connecting to the SocketIO backend")
    const socket = io()

    // Réception d'une mise à jour
    socket.on("note-updated", (note) => {
    const { id, done } = note
    const checkbox = document.querySelector(`input[type="checkbox"][data-id="${id}"]`)
    if (checkbox) checkbox.checked = done
    })

    // Pour chaque checkbox, on envoie une requête au serveur quand on la change
    document.querySelectorAll('input[type="checkbox"].done-checkbox').forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        const id = checkbox.dataset.id
        const done = checkbox.checked
        fetch(`/api/notes/${id}/done`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ done }),
        })
      })
    })
  
    document
      .querySelectorAll(".note>form>input")
      // on every input element inside the form inside the note class
      .forEach((element) => {
        // how to react on its change event
        element.addEventListener("change", (event) => {
          const done = element.checked
          const id = element.dataset.id
          // ask the API to update the note
          fetch(`/api/notes/${id}/done`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ done }),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.ok) {
                console.log("ok")
              } else {
                console.log(data.status, data)
              }
            })
        })
      })
  })
