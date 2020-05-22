(function () {
    const descValue = document.querySelector('#desc-value');
    const descSave = document.querySelector('#desc-save');

    function setDesc(desc) {
        descValue.value = desc;
        descValue.disabled = false;
        descValue.oninput = () => {
            descSave.disabled = descValue.value == desc;
        };
        descSave.disabled = true;
    }

    chrome.storage.sync.get('desc', items => {
        const storedDesc = items.desc || 'Description template';
        setDesc(storedDesc);
        descSave.onclick = () => {
            const desc = descValue.value;
            descValue.disabled = true;
            descSave.disabled = true;
            chrome.storage.sync.set({ 'desc': desc }, () => {
                setDesc(desc);
            });
        };
    });
})()