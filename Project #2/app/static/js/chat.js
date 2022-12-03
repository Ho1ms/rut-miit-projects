function getCook(cookiename)
  {
  var cookiestring=RegExp(cookiename+"=[^;]+").exec(document.cookie);
  return decodeURIComponent(!!cookiestring ? cookiestring.toString().replace(/^[^=]+./,"") : "");
  }

socket.on('connect', function (data) {
    socket.emit('join',
        {
            'room':location.pathname,
            'token':getCook('token'),
            'id':getCook('id')
        })
    console.log('Connected chat!');
});

socket.on('new_message', function (data) {
    let block = `<li class="d-flex justify-content-between mb-4">
            
            <div class="card w-100">
              <div class="card-header d-flex justify-content-between p-3">
                <p class="fw-bold mb-0">${data.name}</p>
                <p class="text-muted small mb-0"><i class="far fa-clock"></i> ${getDate(new Date())}</p>
              </div>
              <div class="card-body">
                <div class="mb-0">
                  ${data.text.replaceAll('\n','<br>')}
                </div>
              </div>
            </div>
            <img src="${data.avatar}" alt="avatar"
              class="rounded-circle d-flex align-self-start m-3 shadow-1-strong" width="60">
          </li>`
                messages.innerHTML += block
})
function send_message() {

    let text = document.getElementById('text')

    let messages = document.getElementById('messages')
    fetch(
        document.location.href,
        {
        method: "post",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text.value,
            name: name,
            img: avatar
         })
        })

    text.value = ''

};



function getDate(dte) {
    let date = new Date(dte)
    let hour = date.getHours().toString().length === 2 ? date.getHours() : '0'+date.getHours()
    let minutes = date.getMinutes().toString().length === 2 ? date.getMinutes() : '0'+date.getMinutes()
    let seconds = date.getSeconds().toString().length === 2 ? date.getSeconds() : '0'+date.getSeconds()
    let day = date.getDate().toString().length === 2 ? date.getDate() : '0'+date.getDate()
    let month = date.getMonth().toString().length === 2 ? date.getMonth() + 1 : '0'+(date.getMonth()+1)
    return `${hour}:${minutes}:${seconds} ${day}.${month}.${date.getFullYear()}`
};