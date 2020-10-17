'use strict';

function App() {
    const fnCheckEmailConnectStatus = (event) => {
        const email = event.target.value;
        alert(email)
    }
    const fnAttachEventListener = (pageName) => {
        if (pageName === 'home') {
            const elem_txtSourceSyncEmail = document.getElementById('txtSourceSyncEmail');
            const elem_txtDestSyncEmail = document.getElementById('txtDestSyncEmail');

            elem_txtSourceSyncEmail.addEventListener('blur', fnCheckEmailConnectStatus);
            elem_txtDestSyncEmail.addEventListener('blur', fnCheckEmailConnectStatus);
        }
    };

    this.init = (pageName) => {
        fnAttachEventListener(pageName);
        return true;
    }

}

(() => {
    const app = new App();
    app.init(PAGE_NAME);
})();
