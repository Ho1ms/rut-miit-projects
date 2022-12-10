window.onload = function() {
const socket = io()

socket.on('notify', function (data) {
    notifyMe(data)
})

function notifyMe(data) {
    console.log(data)
    let notify = new Notification(data.title,{
        tag:'ache-mail',
        body:data.description,
        icon:data.icon
    })
}
function notifySet() {
    if (!("Notification" in window)) {
        alert('Ваш браузер не поддерживает HTML Notifications, его необходимо обновить.');
    }else if (Notification.permission !== "denied") {
      Notification.requestPermission(function (permission){
        if (!('permission' in Notification))
          Notification.permission = permission}
      )
    }
  }


  notifySet();


socket.on('connect', function (data) {
    console.log('Connected!');
});

};