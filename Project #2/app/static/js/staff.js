const modalForm = document.getElementById('staticBackdrop')
modalForm.addEventListener('show.bs.modal', show)
modalForm.addEventListener('hide.bs.modal', hide)
function $(name) {
    return document.getElementById(name)
}
function show(e) {
    body = e.relatedTarget
    let a = document.getElementById(body.id)
    let data = JSON.parse(a.getElementsByTagName('p')[0].innerText)

    $('first_name').value = data.first_name
    $('last_name').value = data.last_name
    $('id').value = body.id
    console.log(body.id)

    let roles = document.getElementById('role')
    Array.from(roles.getElementsByTagName('option')).forEach(e => {
        if (e.value == data.role) e.selected = true
    })


}
function hide(e) {
    $('first_name').value = ''
    $('last_name').value = ''
    $('id').value = ''
}