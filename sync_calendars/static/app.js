'use strict';

function App() {
    const setSVGIcon = (svgElement, iconName) => {
        var useSVG = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        useSVG.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${iconName}`);
        svgElement.innerHTML = '';
        svgElement.appendChild(useSVG);
    };

    const fnCheckEmailConnectStatus = async (event) => {
        const dvAuthorize = event.target.parentElement.nextElementSibling;
        const svgIcon = event.target.nextElementSibling.children[0].children[0]
        const email = event.target.value;
        if (!email) {
            return;
        }
        
        // set loader animation
        setSVGIcon(svgIcon, 'icon-loading');
        svgIcon.classList.add('animate-spin');
        
        // Check email access from api
        const apiResp = await fetch(`/api/emails/${email}?type=check`);

        // reset loader animation
        svgIcon.classList.remove('animate-spin');
        svgIcon.innerHTML = '';

        if (apiResp.status === 204) {
            // email exists
            event.target.classList.remove('border-orange-400');
            event.target.classList.add('border-green');
            
            setSVGIcon(svgIcon, 'icon-calendar-check-o');
            
            dvAuthorize.classList.add('hidden');
            return;
        }

        event.target.classList.remove('border-green-400');
        event.target.classList.add('border-orange-400');
        setSVGIcon(svgIcon, 'icon-calendar-times-o');
        
        dvAuthorize.classList.remove('hidden');
        dvAuthorize.children[0].href = `/o365/connect?email=${email}`;
    };

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
