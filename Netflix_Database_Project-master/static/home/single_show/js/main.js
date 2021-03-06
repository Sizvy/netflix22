const one = document.getElementById('first')
const two = document.getElementById('second')
const three = document.getElementById('third')
const four = document.getElementById('fourth')
const five = document.getElementById('fifth')
console.log(one)

const form = document.querySelector('.rate-form')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

const handleStarSelect = (size) => {
    const children = form.children
    for (let i = 0; i < children.length; i++) {
        if (i <= size) {
            children[i].classList.add('checked')
        }
        else {
            children[i].classList.remove('checked')
        }
    }
}

const handleSelect = (selection) => {
    switch (selection) {
        case 'first': {
            handleStarSelect(1)
            return
        }
        case 'second': {
            handleStarSelect(2)
            return
        }
        case 'third': {
            handleStarSelect(3)
            return
        }
        case 'fourth': {
            handleStarSelect(4)
            return
        }
        case 'fifth': {
            handleStarSelect(5)
            return
        }
    }
}

const getnumericValue = (stringValue) => {
    let numericValue;
    if (stringValue === 'first') {
        numericValue = 1
    }
    else if (stringValue === 'second') {
        numericValue = 2
    }
    else if (stringValue === 'third') {
        numericValue = 3
    }
    else if (stringValue === 'fourth') {
        numericValue = 4
    }
    else if (stringValue === 'fifth') {
        numericValue = 5
    }
    else {
        numericValue = 0
    }
    return numericValue
}

if (one) {
    const arr = [one, two, three, four, five]
    arr.forEach(item => item.addEventListener('mouseover', (event) => {
        handleSelect(event.target.id)
    }))

    arr.forEach(item => item.addEventListener('click', (event) => {
        const val = event.target.id

        let isSubmit = false

        form.addEventListener('submit', e => {
            e.preventDefault()
            const id = e.target.id
            //alert(id)
            const val_num = getnumericValue(val)

            $.ajax({
                type: 'POST',
                path: 'home/rating/',
                data: {
                    'csrfmiddlewaretoken': csrf[0].value,
                    'show_id': id,
                    'rating': val_num
                }
            })
        })
    }))
}

