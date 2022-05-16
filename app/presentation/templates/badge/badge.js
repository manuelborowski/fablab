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

const badged = (event) => {
    if (event.key === 'Enter') {
        let badge_input = document.querySelector(("#badge-input"))
        const res = badge_raw2hex(badge_input.value);
        badge_input.value = '';
        if (res.valid) {
            document.querySelector("#badge-code").value = res.code;
        } else {
            alert(`${res.code} is geen valide code`);
        }
    }

}

const badge_raw2hex = code => {
    const decode_caps_lock = code => {
        let out = '';
        const dd = {'&': '1', 'É': '2', '"': '3', '\'': '4', '(': '5', '§': '6', 'È': '7', '!': '8', 'Ç': '9',
                    'À': '0', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F'};
        for(r of code) {
            out += dd[r.toUpperCase()];
        }
        return out
    }

    const process_int_code = code_int => {
        if (code_int < 100000 || code_int > parseInt('FFFFFFFF', 16)) {
            return {is_rfid_code: false, code: code_int}
        }
        //convert the int to a hex number, add leading 0's (if required) to get 8 characters
        //revert the order of the 4 tupples (big to little endian)
        let hex = code_int.toString(16).toUpperCase();
        hex = '0'.repeat(8 - hex.length) + hex;
        hex = hex.split('');
        let out = []
        for(let i = 6; i >= 0; i -= 2) { out = out.concat(hex.slice(i, i + 2)) }
        out = out.join('');
        return {is_rfid_code: true, code: out}
    }

    let is_rfid_code = true
    let is_valid_code = true
    code = code.toUpperCase();

    if (code.length === 8) {
        // Asume a hex code of 8 chars
        if (code.contains('Q')) {
            // the badgereader is a qwerty HID device
            code = code.replace(/Q/g, 'A');
        }
        if (!/^[0-9a-fA-F]+$/.test(code)) {
            // it is not a valid hex code :-(  Check if capslock was on
            code = decode_caps_lock(code);
            if (!/^[0-9a-fA-F]+$/.test(code)) {
                // it is not a valid code :-(
                is_valid_code = is_rfid_code = false;
            }
        }
    } else {
        // Assume it is an integer code, so test it
        if (/^[0-9]+$/.test(code)) {
            const res = process_int_code(parseInt(code));
            is_rfid_code = res.is_rfid_code;
            code = res.code;
        } else
        {
            code = decode_caps_lock(code);
            if (/^[0-9]+$/.test(code)) {
                const res = process_int_code(parseInt(code));
                is_rfid_code = res.is_rfid_code;
                code = res.code;
            } else {
                is_valid_code = is_rfid_code = false;
            }
        }
    }
    return {valid: is_rfid_code, code}
}