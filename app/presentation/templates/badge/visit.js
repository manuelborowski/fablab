const visit_process_badge = async event => {
    if (badge_process_badge(event)) {
        const badge_code = document.querySelector('#badge-code');
        const ret = await fetch(Flask.url_for('api.visit_add', {api_key}), {
            method: 'POST',
            body: JSON.stringify({code: badge_code.value}),
        });
        badge_code.value = '';
        const status = await ret.json();
        var timeout;
        const modal = document.querySelector(".modal");
        const modal_content = document.querySelector(".modal div");
        const content = document.querySelector(".modal div h1");
        if (status.status) {
            timeout = 2000;
            modal_content.style.backgroundColor = "green";
        } else {
            timeout = 3000;
            modal_content.style.backgroundColor = "red";
        }
        content.innerHTML = status.data;
        modal.style.display = "block";
        setTimeout(function () {
            modal.style.display = "none";
        }, timeout);
    }
}
