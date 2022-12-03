socket.on('new_ticket', function (data) {
    const messages = document.getElementById('tickets')
    let block = `<tr>
              <td>${data.id}</td>
              <td>${data.username}</td>
              <td>${data.message}</td>
              <td>Новый</td>
              
              <td>Нет</td>
              <td>${getDate(new Date())}</td>
              <td>
                <a class="btn btn-success" href="/tickets/${data.id}">
                  <svg class="feather feather-file-text" width="16" height="16" fill="currentColor" >
                    <use href="/static/icons/bootstrap-icons.svg#send"/>
                  </svg>
                </a>
               </td>
            </tr>`
    messages.innerHTML = block + messages.innerHTML
})
function getDate(dte) {
    let date = new Date(dte)
    let hour = date.getHours().toString().length === 2 ? date.getHours() : '0'+date.getHours()
    let minutes = date.getMinutes().toString().length === 2 ? date.getMinutes() : '0'+date.getMinutes()
    let seconds = date.getSeconds().toString().length === 2 ? date.getSeconds() : '0'+date.getSeconds()
    let day = date.getDate().toString().length === 2 ? date.getDate() : '0'+date.getDate()
    let month = date.getMonth().toString().length === 2 ? date.getMonth() + 1 : '0'+(date.getMonth()+1)
    return `${hour}:${minutes}:${seconds} ${day}.${month}.${date.getFullYear()}`
};