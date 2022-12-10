window.onload = () => {

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
    let avatar_url = data.avatar.startsWith('https://t.me/i/userpic/320/') ? data.avatar : document.location.origin+'/static/img/avatars/'+data.avatar
    let img = `<img src="${avatar_url}" alt="avatar" class="rounded-circle d-flex align-self-start m-3 shadow-1-strong" width="60">`
    let block = `<li class="d-flex justify-content-between mb-4">
            ${data.is_bot ? img : ''}
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
            ${data.is_bot ? '' : img}
          </li>`
                messages.innerHTML += block
})

socket.on('close_ticket',function (data){
    document.getElementsByTagName('textarea')[0].disabled = true
    let buttons = document.getElementsByTagName('button')
    buttons[1].disabled = true
    buttons[2].disabled = true
})

}
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
            img: avatar,
            user_id:getCook('id')
         })
        })

    text.value = ''

};

function getCook(cookiename)
  {
  var cookiestring=RegExp(cookiename+"=[^;]+").exec(document.cookie);
  return decodeURIComponent(!!cookiestring ? cookiestring.toString().replace(/^[^=]+./,"") : "");
  }
  
  function getDate(dte) {
    let date = new Date(dte)
    let hour = date.getHours().toString().length === 2 ? date.getHours() : '0'+date.getHours()
    let minutes = date.getMinutes().toString().length === 2 ? date.getMinutes() : '0'+date.getMinutes()
    let seconds = date.getSeconds().toString().length === 2 ? date.getSeconds() : '0'+date.getSeconds()
    let day = date.getDate().toString().length === 2 ? date.getDate() : '0'+date.getDate()
    let month = date.getMonth().toString().length === 2 ? date.getMonth() + 1 : '0'+(date.getMonth()+1)
    return `${hour}:${minutes}:${seconds} ${day}.${month}.${date.getFullYear()}`
};

function close_ticket() {
    fetch(
        document.location.href,
        {
        method: "post",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action:'close-ticket'
         })
        })
}