window.onload = () => {
    socket.on('add-form', function (data) {
        let tbody = document.getElementsByTagName('tbody')[0]
        tbody.innerHTML = `<tr id="${data.id}" data-bs-toggle="modal" data-bs-target="#staticBackdrop">
              <td>${data.id}</td>
              <td>${data.name}</td>
              <td>${data.surname}</td>
              <td>${data.years}</td>
              <td>${data.type}</td>
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
        $('education').innerText = `${data.university}\n${data.education}`
        $('labelForm').innerText = `Анекта №${data.id}`
        $('contacts').innerText = `Email: ${data.email}`
        $('cover_letter').innerText = data.cover_letter
        $('form_id').value = data.id
        $('resume').src = window.location.origin + '/static/img/resume/' + `${data.resume}`
        $('resume_url').href = window.location.origin + '/static/img/resume/' + `${data.resume}`

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
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates_titles,
            datasets: [{
                data: dates_info,
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff'
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false
                    }
                }]
            },
            legend: {
                display: false
            }
        }
    });

}