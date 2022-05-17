$(document).ready(function () {
    subscribe_formio_event('loaded', install_event_handlers)
});

const install_event_handlers = type => {
    const badge_input = document.querySelector('[name="data[badge_input]"]');
    badge_input.addEventListener('keypress', event => {
        if (event.key === 'Enter') {
            const res = badge_raw2hex(badge_input.value);
            formio.getComponent('badge_input').setValue('');
            if (res.valid) {
                let prev_visitor = null;
                visitors.forEach(v => {
                    if (v.badge_code === res.code) {
                        if (confirm(`De badge is reeds toegewezen aan ${v.last_name} ${v.first_name}\nWilt u verder gaan met deze badge?`)) {
                            prev_visitor = v;
                            return
                        }
                    }
                });
                if (prev_visitor) {
                    formio.getComponent('badge_code').setValue(prev_visitor.badge_code);
                    formio.getComponent('badge_number').setValue(prev_visitor.badge_number);
                } else {
                    formio.getComponent('badge_code').setValue(res.code);
                    formio.getComponent('badge_number').setValue('');
                }
            } else {
                alert(`${res.code} is geen valide code`);
            }
        }
    })
}

