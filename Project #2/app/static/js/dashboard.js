window.onload = () => {
    socket.on('add-form', function (data) {
        let tbody = document.getElementsByTagName('tbody')[0]
        tbody.innerHTML = `<tr id="${data.id}" data-bs-toggle="modal" data-bs-target="#staticBackdrop">
              <td>${data.id}</td>
              <td>${data.surname}</td>
              <td>${data.name}</td>
              <td>${data.father}</td>
              <td>${data.years}</td>
              <td>${data.direction}</td>
              <td>${data.city}</td>
              <td>Новое</td>
            </tr>` + tbody.innerHTML

    });

    function $(id) {
        return document.getElementById(id)
    }

    let forms = {}

    function draw_form(data) {
        $('name').innerText = `${data.name} ${data.surname} ${data.father_name}`
        $('city').innerText = `${data.city} - ${data.direction}`
        $('years').innerText = `${data.date} (${data.years})`
        $('education').innerText = `Место учёбы: ${data.university}\nНаправление образования: ${data.education}`
        $('labelForm').innerText = `Анекта №${data.id}`
        $('contacts').innerText = `Email: ${data.email}\nTelegram: @${data.username}`
        $('cover_letter').innerText = data.cover_letter
        $('form_id').value = data.id
        if (data.resume) {

            $('resume').src = window.location.origin + '/static/img/resume/' + `${data.resume}`
            $('resume_url').href = window.location.origin + '/static/img/resume/' + `${data.resume}`
        } else {
             $('resume_label').innerText = 'Резюме: Без резюме.'
        }


    }

    const modalForm = document.getElementById('staticBackdrop')
    modalForm.addEventListener('show.bs.modal', event => {
        const form = event.relatedTarget
        const xhttp = new XMLHttpRequest();

        if (form.id in forms) return draw_form(forms[form.id]);

        xhttp.open('GET', window.location.origin + `/api/get-form?id=${form.id}`, true)
        xhttp.send()
        xhttp.onreadystatechange = function () {
            if (this.status === 200 && this.readyState === 4) {
                data = JSON.parse(this.responseText)
                forms[form.id] = data
                draw_form(data)

            }
        }
    })
    modalForm.addEventListener('hide.bs.modal', event => {
        $('resume_label').innerText = 'Резюме:'
        $('name').innerText = ''
        $('city').innerText = ''
        $('years').innerText = ''
        $('education').innerText = ''
        $('labelForm').innerText = ''
        $('contacts').innerText = ''
        $('cover_letter').innerText = ''
        $('resume').src = ''
        $('resume_url').href = ''
        $('form_id').value = ''
    })


    function getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    var ctx = document.getElementById('myChart')
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates_titles,
            datasets: [{
                data: bot_uses,
                label:'Новые пользователи',
                lineTension: 0,
                borderJoinStyle:'bevel',
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff'
            }, {
                data: form_uses,
                label:'Анкеты',
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#f50c0c',
                borderWidth: 4,
                pointBackgroundColor: '#f50c0c'
            }, {
                data: ticket_uses,
                label:'Тикеты',
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#11991e',
                borderWidth: 4,
                pointBackgroundColor: '#11991e'
            }

            ]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false
                    }
                }]
            }
        }
    });

}