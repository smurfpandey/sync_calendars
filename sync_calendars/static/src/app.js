'use strict';

import './app.css';

function App() {
    const setSVGIcon = (svgElement, iconName) => {
        var useSVG = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        useSVG.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${iconName}`);
        svgElement.innerHTML = '';
        svgElement.appendChild(useSVG);
    };

    const fnCheckEmailConnectStatus = async (event) => {
        const elem_this = event.target;
        const dvAuthorize = elem_this.parentElement.nextElementSibling;
        const svgIcon = elem_this.nextElementSibling.children[0].children[0]
        const email = elem_this.value.toLowerCase();
        if (!email) {
            return;
        }

        const calType = elem_this.dataset.calType;
        const status = elem_this.dataset.status;
        if (status == 'Y' || status === 'N') {
            // Status has already been checked
            return;
        }

        // set loader animation
        setSVGIcon(svgIcon, 'icon-loading');
        svgIcon.classList.add('animate-spin');
        elem_this.dataset.status = 'N';

        // Check email access from api
        const apiResp = await fetch(`/api/emails/${email}?type=check`);

        // reset loader animation
        svgIcon.classList.remove('animate-spin');
        svgIcon.innerHTML = '';

        if (apiResp.status === 204) {
            // email exists
            elem_this.dataset.status = 'Y';

            elem_this.classList.remove('border-orange-700');
            elem_this.classList.add('border-green-700');

            setSVGIcon(svgIcon, 'icon-calendar-check-o');

            dvAuthorize.classList.add('hidden');
            return;
        }

        elem_this.classList.remove('border-green-700');
        elem_this.classList.add('border-orange-700');
        setSVGIcon(svgIcon, 'icon-calendar-times-o');

        dvAuthorize.classList.remove('hidden');

        dvAuthorize.children[0].href = `/o365/connect?email=${email}&type=${calType}`;
    };

    const fnResetEmailStatus = (event) => {
        event.target.dataset.status = 'NA';
    }

    const fnSaveSyncFlow = async (event) => {
        const elem_this = event.target;
        const elem_loader = elem_this.children[0];
        const elem_txtSourceSyncEmail = document.getElementById('txtSourceSyncEmail');
        const elem_txtDestSyncEmail = document.getElementById('txtDestSyncEmail');
        const elem_spFormError = document.getElementById('spFormError');

        // read form
        elem_spFormError.innerText = '';
        elem_spFormError.classList.remove('text-green-500');
        elem_spFormError.classList.add('text-red-500');
        let hasError = false;
        const sourceCalEmail = elem_txtSourceSyncEmail.value.toLowerCase();
        const sourceCalEmailStatus = elem_txtSourceSyncEmail.dataset.status;
        const destCalEmail = elem_txtDestSyncEmail.value.toLowerCase();
        const destCalEmailStatus = elem_txtDestSyncEmail.dataset.status;

        if (sourceCalEmailStatus != 'Y') {
            elem_txtSourceSyncEmail.classList.add('border-red-500');

            elem_txtSourceSyncEmail.parentElement.classList.add('animate-shake');
            // remove the class after the animation completes
            setTimeout(function () {
                elem_txtSourceSyncEmail.parentElement.classList.remove('animate-shake');
            }, 300);

            hasError = true;
        }

        if (destCalEmailStatus != 'Y') {
            elem_txtDestSyncEmail.classList.add('border-red-500');

            elem_txtDestSyncEmail.parentElement.classList.add('animate-shake');
            // remove the class after the animation completes
            setTimeout(function () {
                elem_txtDestSyncEmail.parentElement.classList.remove('animate-shake');
            }, 300);

            hasError = true;
        }

        if (sourceCalEmail === destCalEmail) {
            hasError = true;
            elem_spFormError.innerText = 'Source and destination can not be same.';
        }

        if (hasError) {
            return;
        }

        // enable WIP state
        elem_loader.classList.remove('hidden');
        elem_this.classList.add('cursor-not-allowed');
        elem_this.disabled = true;

        // make API request
        const reqData = {
            source_cal: sourceCalEmail,
            dest_cal: destCalEmail
        };

        const response = await fetch('/api/syncs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(reqData)
        });

        elem_loader.classList.add('hidden');
        elem_this.classList.remove('cursor-not-allowed');
        elem_this.disabled = false;

        if (response.status === 400) {
            let errResult = await response.json();
            hasError = true;
            elem_spFormError.innerText = errResult.message;
        }

        if (response.status === 201) {
            elem_spFormError.classList.add('text-green-500');
            elem_spFormError.classList.remove('text-red-500');
            elem_spFormError.innerText = 'Sync created successfully';
        }
    }

    const fnToggleModal = (event) => {
        const body = document.querySelector('body');
        const modal = document.querySelector('.modal');
        modal.classList.toggle('hidden');
        modal.classList.toggle('pointer-events-none');
        body.classList.toggle('modal-active');
    }

    const fnAttachEventListener = (pageName) => {
        if (pageName === 'home') {
            const elem_txtSourceSyncEmail = document.getElementById('txtSourceSyncEmail');
            const elem_txtDestSyncEmail = document.getElementById('txtDestSyncEmail');
            const elem_btnSaveSyncFlow = document.getElementById('btnSaveSyncFlow');
            const elem_btnShowModal = document.getElementById('btnShowModal');
            const elem_divOverlay = document.querySelector('.modal-overlay');
            const elem_btnCloseModal = document.querySelector('.modal-close');

            elem_txtSourceSyncEmail.addEventListener('blur', fnCheckEmailConnectStatus);
            elem_txtDestSyncEmail.addEventListener('blur', fnCheckEmailConnectStatus);
            elem_txtSourceSyncEmail.addEventListener('change', fnResetEmailStatus);
            elem_txtDestSyncEmail.addEventListener('change', fnResetEmailStatus);
            elem_btnSaveSyncFlow.addEventListener('click', fnSaveSyncFlow);
            elem_btnShowModal.addEventListener('click', fnToggleModal);
            elem_divOverlay.addEventListener('click', fnToggleModal);
            elem_btnCloseModal.addEventListener('click', fnToggleModal);
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
